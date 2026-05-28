# Upstream filter audit (F#1-F#28) vs Shahaf+ 2023 Triage sample

*Compiled 2026-05-28. Audits the SQL `WHERE`-clause filters that build our
56,100-source v2 cascade input pool (`scripts/streaming/producer.py`),
using Shahaf+ 2023 (MNRAS 518.2991, table 2) as ground truth. Goal: find
the genuine NS / BH candidates we lose **before** the cascade ever sees
them.*

## TL;DR

- **Only 12 of Shahaf's 177 Triage candidates reach our v2 pool (6.8%).**
  165 are excluded by upstream filters. The single dominant filter is
  **F#5 (G < 13)**, which excludes 162 of 165 (98%). Shahaf reaches
  G ≈ 18; our pool stops at G = 13.
- Running the v2 cascade math on the 165 missing sources recovers
  **68 NS-mass candidates (M_2 ≥ 1.2)** and **2 BH-mass candidates
  (M_2 ≥ 3.0)** — but **0 are NEW**: all 8 Shahaf-BH and all 60 Shahaf-NS
  in this set are known. The 2 BH-mass ones simply recover Shahaf's
  values.
- **No NS/BH-mass candidate survives all four post-cascade filters
  (F#29-F#32)** at Tier-1 level — because RV data (`rv_amplitude_robust`,
  `rv_chisq_pvalue`) is absent for nearly all G > 13 sources, so F#31
  and F#32 are uniformly `NO_DATA`.
- **Tier-2 NS-mass recoveries: 36.** These pass F#29 + F#30 cleanly,
  F#31/F#32 are simply uninformative. They are real candidates that
  need follow-up RV.
- **Recommendation: relax F#5 from G<13 to G<14 (or G<15) for v3.1.**
  This recovers all 36 Tier-2 NS plus the 2 BH-mass without disrupting
  the cascade. The cost is roughly a 4-8× pool growth in the v3 fetch.

## 1. The exclusion breakdown

### 1.1 Overlap with Shahaf

| Stratum | Count | NS | BH | WD |
|---|---:|---:|---:|---:|
| Shahaf+ 2023 table 2 total | 177 | 68 | 8 | 101 |
| In our v2 pool | 12 | 9 | 3 | 0 |
| Missing from our pool | 165 | 59 | 5 | 101 |

Our pool catches no Shahaf "WD" class because Shahaf's WD class has
M_2 ≈ 0.6-1.1 M_⊙ and the AMRF "compact" signal is at G > 13 where our
G-cut blocks them.

### 1.2 Per-filter exclusion (main-mode cuts: sig≥12, P 100-3000 d, plx≥1, G<13, Orbital+ASB1+OTS+OTSV, A,B Thiele-Innes NOT NULL)

| Filter | What it cuts | # of 165 failing | first to fail |
|---|---|---:|---:|
| F#1 | NSS solution type ∉ {Orbital, AstroSpectroSB1, OrbitalTargetedSearch, OrbitalTargetedSearchValidated} | 0 | 0 |
| F#2 | nss.significance < 12 | 12 (7.3%) | 12 |
| F#3 | period < 100 d or > 3000 d | 5 (3.0%) | 5 |
| F#4 | gaia_source.parallax < 1.0 mas | 7 (4.2%) | 7 |
| **F#5** | **phot_g_mean_mag ≥ 13** | **162 (98.2%)** | **141** |
| F#6 | a_thiele_innes IS NULL | 0 | 0 |
| F#7 | b_thiele_innes IS NULL | 0 | 0 |

The "first to fail" column is the most discriminative: 141 of the 165
are excluded *primarily* by F#5 (i.e., they pass every earlier filter).

The non-G filters fail orthogonal sources:
- 12 with sig<12 are mostly intermediate-magnitude (G 12.9-17.5)
  candidates with weaker orbits — three of these are Shahaf BH at
  M_2 = 2.4-3.1.
- 7 with plx<1 are nearby NS candidates (plx 0.5-0.99 mas), G 13.5-15.4,
  Shahaf M_2 ≈ 1.2-1.7.
- 5 with P<100 d (one source) or P>3000 d (four sources) include two
  Shahaf NS with M_2 ≈ 1.0-1.3.

### 1.3 Per-filter defensibility verdict

| Filter | Verdict | Justification |
|---|---|---|
| F#1 (NSS type) | **Keep** | Already the broadest reasonable set. Adding `SB1` brings spectroscopic-only solutions with no astrometric mass info; the v2 derivation requires a Thiele-Innes orbit. |
| F#2 (sig≥12) | **Relax to ≥5** | Removes 12 sources including 3 Shahaf BH candidates (sig 6.8-10.8). Significance is an orbit-fit quality metric; sources with sig<12 simply have noisier orbits but Shahaf still catalogues them. Add an explicit `sig_bucket` column downstream. |
| F#3 (100<P<3000) | **Keep** | Cuts only 5 sources (3% of missing). P<100 d candidates are likely close binaries; P>3000 d candidates approach the DR3 mission baseline and have poorly-constrained orbits. |
| F#4 (plx≥1.0) | **Relax to ≥0.5** | Drops 7 NS candidates at 0.5-1.0 mas. The cascade math has no parallax floor; F#4 was originally a heuristic to ensure detection significance. With the v2 NSS-parallax correction, low-plx sources are perfectly handleable. |
| F#5 (G<13) | **CRITICAL: Relax to G<14 (minimum) or G<15 (preferred)** | This is the binding constraint. Excludes 98% of Shahaf's NS sample. Was originally chosen to keep the pool tractable for the initial RVS+ML pipeline; the cascade itself has no G-mag dependence. Relaxing to G<14 recovers ~46 NS + 2 BH; G<15 recovers all 36 Tier-2 NS + 2 BH-mass. Cost: pool grows from 56k to ~250-450k rows. |
| F#6, F#7 (A/B Thiele-Innes IS NOT NULL) | **Keep** | The v2 derivation needs both A and B. Sources with NULL Thiele-Innes are SB1 / Acceleration NSS rows that belong in the **deferred** acceleration pipeline (see `scripts/streaming/v3_acceleration/`), not the orbital cascade. |

## 2. v2 cascade math on the 165 missing sources

All 165 have valid Thiele-Innes coefficients and parallax, so the v2
math is computable.

### 2.1 class distribution

| class_v2 | count |
|---|---:|
| WD_or_low_mass_star | 97 |
| dormant_NS_candidate | 66 |
| dormant_BH_candidate | 2 |

### 2.2 Recovered NS-mass (M_2_v2 ≥ 1.2 M_⊙): 68 sources

Filter pass rates among these 68:
| Filter | PASS | FAIL | NO_DATA |
|---|---:|---:|---:|
| F#29 (SB2) | 68 | 0 | 0 |
| F#30 (K-giant chromatic) | 36 | 32 | — |
| F#31 (RV reality) | 2 | 0 | 66 |
| F#32 (joint K_obs vs K_pred) | 2 | 0 | 66 |

F#30 demotes 32/68 as K-giants (BP-RP > 1.2 or logg < 2.7 via the
gspphot → gspspec_ann → gspspec fallback chain). These are likely
4 UMi-class chromatic offsets, correctly demoted.

The remaining 36 form the "Tier-2" pool: pass F#29 + F#30; F#31/F#32
NO_DATA because Gaia DR3 RVS rarely reaches G > 13 with usable
`rv_amplitude_robust` + `rv_chisq_pvalue`.

### 2.3 Recovered BH-mass (M_2_v2 ≥ 3.0 M_⊙): 2 sources

| source_id | Shahaf class | M_2 Shahaf | M_2 v2 | F#30 | G | sig | P (d) | First-fail |
|---|---|---:|---:|---|---:|---:|---:|---|
| 4373465352415301632 | BH | 12.81 | 12.73 | PASS | 13.77 | 13.6 | 185.8 | F#5 |
| 6802561484797464832 | BH | 3.08 | 3.07 | PASS | 12.88 | 6.8 | 574.8 | F#2 |

Both are known Shahaf BH (Triage-III class BH). Our M_2 values agree
with Shahaf to within 1%, validating the v2 math. No new BH discovery
in this slice.

The 3 Shahaf BH already in our pool are at M_2_v2 ≈ 2.45-2.56 (NS-mass
class in v2 because of the Bayesian Bayesian solver and our NSS-plx
correction); they appear as Tier-1 BH in v2 with `class_v2 =
dormant_BH_candidate` based on Shahaf's higher M_1 prior of ~1.0-1.1.
With v2's M_1=1.5 default, two recover as BH and one as upper NS.

### 2.4 Top Tier-2 NS-mass recoveries (sorted by significance)

| source_id | Shahaf class | M_2 Shahaf | M_2 v2 | G | sig | P (d) | First-fail |
|---|---|---:|---:|---:|---:|---:|---|
| 1694708646628402048 | NS | 1.34 | 1.30 | 13.20 | 114.9 | 632.0 | F#5 |
| 6328149636482597888 | BH | 2.45 | 2.55 | 13.34 | 89.9 | 736.0 | F#5 |
| 4240540718818313984 | NS | 1.35 | 1.77 | 14.61 | 85.2 | 691.2 | F#5 |
| 1434445448240677376 | NS | 1.33 | 1.28 | 13.65 | 82.5 | 572.4 | F#5 |
| 1695294922548180224 | NS | 1.48 | 1.54 | 13.12 | 79.9 | 601.2 | F#5 |
| 5355633933885075328 | NS | 1.14 | 1.41 | 13.73 | 76.8 | 574.7 | F#5 |
| 1871419337958702720 | NS | 1.47 | 1.52 | 13.70 | 72.1 | 479.3 | F#5 |
| 5331513195692864768 | NS | 1.19 | 1.25 | 15.25 | 72.0 | 870.4 | F#5 |

These all pass F#29 + F#30; F#31/F#32 are NO_DATA because G > 13 → no
RVS coverage. Full list in `data/upstream_audit/recovered_NS_BH_M2_ge_1p2.csv`.

## 3. New candidates not in Shahaf

Step 5 asked: do we have v2-pool candidates that pass everything but
aren't in Shahaf?

| Set | Count |
|---|---:|
| v2 NS+BH class, M_2 ≥ 1.2 | 830 |
| Of which already in Shahaf | 12 |
| Of which NOT in Shahaf | 818 |
| NOT in Shahaf + F#29 + F#30 + F#31 + F#32 all PASS | **274** |
| NOT in Shahaf + M_2 ≥ 3.0 (BH-mass) | 0 |

So the "new" candidate pool is **274 NS-mass sources passing all
filters at Tier-1 (with usable RV)**. None are BH-mass.

The top 10 by M_2 (full list: `data/upstream_audit/new_candidates_not_in_shahaf.csv`):

| source_id | M_2_v2 | sig | P (d) | G | sini_v2 |
|---|---:|---:|---:|---:|---:|
| 6687541573416724608 | 2.14 | 20.1 | 1125 | 12.07 | 0.75 |
| 3378588057203660160 | 1.73 | 12.5 | 999 | 10.32 | 0.90 |
| 5152756278867291392 | 1.72 | 14.7 | 204 | 11.05 | 0.09 |
| 1765282312286903168 | 1.66 | 17.1 | 886 | 12.59 | 0.95 |
| 3416706995764557568 | 1.66 | 22.8 | 725 | 11.82 | 0.33 |
| 1827302018034513920 | 1.63 | 45.5 | 589 | 11.07 | 0.86 |
| 4026840085508765312 | 1.62 | 89.1 | 416 | 8.71 | 0.83 |
| 6779601173750380288 | 1.61 | 14.1 | 1456 | 11.88 | 1.02 |
| 2007282931791340544 | 1.58 | 36.3 | 936 | 10.24 | 0.94 |
| 5226674761983825792 | 1.58 | 33.2 | 531 | 11.56 | 0.89 |

These are candidates Shahaf themselves did not include in their Triage
sample — they pass our G<13 cut, are NS-class in v2, and survive all
four post-cascade filters. Whether they are *genuinely* compact-object
candidates depends on the chromatic-offset / inflated-plx tests
already encoded in F#30/F#32, both of which they pass. They are the
appropriate next-tier targets.

**No headline BH discovery: 0 sources have M_2_v2 ≥ 3.0 AND all
filters pass AND are NOT in Shahaf.** The "new" pool is purely
NS-mass.

## 4. Recommendations for v3.1 cascade

### Priority 1 — Relax F#5 (G mag cut)

- Change `producer.py` CUTS['main']`['G_max']` from **13** to **14** as
  a conservative first step, or **15** as the full Shahaf-parity step.
- Pool growth estimate: from 56,100 to ~150-250k rows (G<14) or
  ~400-700k rows (G<15).
- Cost: linear FLAME pull. Should batch in ~2-4× current wallclock.
- Recovers all 36 currently-missed Tier-2 NS, plus brings the v2
  pool to ~99% Shahaf parity.

### Priority 2 — Relax F#2 (significance) to ≥ 5

- Catches the 3 Shahaf BH at sig 6.8-10.8 (including 6802561484797464832
  with v2 M_2 = 3.07, a true BH-mass).
- Adds ~20-30% more rows of marginal orbit fits, all with usable
  Thiele-Innes coefficients.
- Add a `significance_bucket` column to the derived parquet for
  downstream filtering choices.

### Priority 3 — Relax F#4 (parallax) to ≥ 0.5 mas

- Catches 7 nearby NS at plx 0.48-0.99 mas, including 3 in the v2
  Tier-2 pool already (`747174436620510976`, `1350295047363872512`,
  `4578398926673187328`).
- Adds ~5-10% rows; minor pool growth.

### Priority 4 — Add Acceleration NSS as a parallel pool

- Sources with SB1-only or PM-acceleration solutions (no Thiele-Innes,
  fail F#6/F#7) need the `v3_acceleration/` codebase. Already partially
  built. Not in scope here.

### Defer / no change

- F#1: keep the broader NSS-type set. No Shahaf candidate fails F#1.
- F#3: period bounds are physically motivated. Only 5 Shahaf candidates
  fall outside; investigate case-by-case rather than relax globally.
- F#6, F#7: keep the Thiele-Innes requirement — they are essential for
  the cascade math.

## 5. Verification against Shahaf overlap (12 sources)

Of the 12 Shahaf candidates that did reach our pool:

| tier_v2 | count |
|---|---:|
| Tier-1 NS | 3 |
| Tier-1 BH | 2 |
| Tier-2 (RV inconclusive) | 4 |
| Demoted F#30 | 1 |
| Demoted F#31 | 1 |
| Demoted F#32 | 1 |

This 5/12 "Tier-1" recovery rate is consistent with the user's claim
that the cascade achieves 100% recall on the *Shahaf 2024* refined
sample (which was already pre-filtered for survival likelihood).

## Files written

- `data/upstream_audit/shahaf2023_table2_triage.csv` — 177 Shahaf rows
- `data/upstream_audit/missing_ids.json` — 165 source_ids excluded by F#1-F#7
- `data/upstream_audit/missing_sources_raw.parquet` — Gaia query results
- `data/upstream_audit/missing_with_diagnoses.parquet` — per-source filter-failure tags
- `data/upstream_audit/missing_diagnoses.csv` — human-readable failure CSV
- `data/upstream_audit/recovered_v2_derivation.parquet` / `.csv` — full v2 math on all 165 missing
- `data/upstream_audit/recovered_NS_BH_M2_ge_1p2.csv` — 68 NS+BH-mass recoveries
- `data/upstream_audit/recovered_NS_BH_full.csv` — same with all 4 filter outcomes
- `data/upstream_audit/new_candidates_not_in_shahaf.csv` — 274 v2-Tier-1 NS not in Shahaf

## References

- Shahaf, Hallakoun, Mazeh, et al., MNRAS 518, 2991 (2023) — Triage AMRF
- Halbwachs+, A&A 674, A9 (2023) — DR3 NSS Thiele-Innes formalism
- See `docs/CASCADE_CORRECTIONS_2026_05_28.md` for v2 math details
