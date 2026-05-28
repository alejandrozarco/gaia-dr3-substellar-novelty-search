# Final verdict after parallel deep dive on 7+1 top BH candidates

*Result of 2026-05-27 deep dive that applied Filter #31 (paired
K_obs + rv_chisq_pvalue check), IR-excess check (K-W3, K-W4), close Gaia
neighbors (5" contamination zone), and galactic latitude (crowded-field
risk) to all 7 surviving top BH candidates plus the A-dwarf reference.*

## Summary table (data from parallel_deep_dive_2026_05_27.csv)

| Source | G | b | Filter#31 | K-W1 | K-W2 | K-W3 | K-W4 | Nbrs<5" | Verdict |
|---|---:|---:|---|---:|---:|---:|---:|---:|---|
| **HD 207141** | 8.72 | -49° | PASS | 0.13 | 0.04 | 0.03 | -0.11 | 0 | **SURVIVES** |
| **TYC 1363-2339-1** | 9.90 | +21° | PASS | 0.04 | 0.01 | 0.06 | 0.29 | 0 | **SURVIVES** |
| TYC 8785-1657-1 | 10.81 | -34° | PASS | 0.07 | 0.07 | 0.02 | 1.31 | 0 | W4 only — ambiguous |
| Gaia 2801267044426382336 | 12.59 | -43° | PASS | 0.05 | 0.05 | -0.04 | 1.89 | 0 | W4 only — ambiguous |
| Gaia 6784701430232308352 | 11.75 | -47° | PASS | 0.19 | 0.17 | 0.06 | 1.58 | 0 | W4 only — ambiguous |
| Gaia 5889532732877344128 | 12.67 | +5° | PASS | 0.06 | 0.02 | **-0.41** | 2.44 | +1 | DEMOTED (anomalous K-W3 + neighbor) |
| Gaia 5942873714068259584 | 12.96 | +1° | PASS | **1.24** | **1.23** | **1.93** | **3.97** | +3 | DEMOTED (galactic plane + 3 nbrs + all-band IR excess) |
| Gaia 245948793944575360 (A-dwarf) | 11.80 | -4° | **FAIL** | 0.07 | 0.06 | 0.21 | 1.31 | 0 | DEMOTED (Filter #31 fail) |

## Survivor analysis

**HD 207141**: K-W1 through K-W4 all within photospheric expectations
(-0.1 to +0.15 mag range). Single F-subgiant photosphere fit explains
every band. Galactic latitude b = -49° is high above the plane — clean
field. No close Gaia neighbors. rv_chisq_pvalue = 0.0 with
rv_renormalised_gof = 57.4 confirms strong real RV variability. Cascade
M_2 = 7.57 M☉ but RV-derived M_2 = 4.74 at i=60° → joint 4.5-6 M☉ in
the mass-gap.

**TYC 1363-2339-1**: K-W1 through K-W3 all within photospheric range;
K-W4 = +0.29 is marginal (threshold was 0.30) but consistent with
photospheric value at noisy 22-micron band. b = +21° clean. No close
neighbors. rv_chisq_pvalue = 0.0 with rgof = 19.3 — real RV variability.
Both M_2 estimates converge at ~3.9 M☉ at i=60° — TOV / mass-gap boundary.

## Demoted candidates (5 of 7)

### W4-only excess pattern (3 candidates)
TYC 8785, Gaia 2801267, Gaia 6784701 all show **K-W3 clean (<0.10)
but K-W4 strong excess (1.3-1.9)**. Three possible explanations:

1. **Cold debris disk** (Vega-like). Plausible for F-subgiants but doesn't
   invalidate the binary M_2 derivation if the disk is in the same plane.
2. **Background source in the 12" W4 PSF**. The WISE W4 beam is huge;
   even a faint background star not detected in Gaia (< G 21) could
   contribute. K-W3 is clean because W3 PSF (~6.5") doesn't overlap.
3. **Faint cool stellar companion** (M-dwarf at separation < 12"). Would
   need to show up in K-W3 too — not detected, so unlikely.

Verdict: **ambiguous, not eliminated.** Needs higher-resolution mid-IR
(Spitzer / JWST) or a deep optical AO image to localize the W4 source.

### Confirmed contamination (2 candidates)
Gaia 5889532 (b = +5°, 1 neighbor within 5", anomalous K-W3 = -0.41) and
especially Gaia 5942873 (b = +1°, **3 close neighbors**, K-W1 through W4
all show massive excess from 1.24 to 3.97 mag). These are galactic-plane
sources with photometric contamination from blended neighbors. The
Filter #31 pvalue check passes but only because the cascade fit *some*
periodic signal in the contaminated time series. **Not real BH
candidates.**

### A-dwarf (1 candidate)
Already discussed: rv_chisq_pvalue = 0.999, the RV "amplitude" is from
single-epoch outliers in a galactic-plane crowded field, not real binary
motion.

## Updated lead ranking

| Rank | Source | V | M_2 joint | Status | Action |
|---:|---|---:|---|---|---|
| **1** | **TYC 1363-2339-1** | 9.90 | 3-4 M☉ | SURVIVES all filters | INAUGURAL RV target |
| **2** | **HD 207141** | 8.72 | 4.5-6 M☉ | SURVIVES all filters | Secondary RV target |
| 3 | TYC 8785-1657-1 | 10.81 | 3-4 M☉ | W4 excess ambiguous | Mid-IR follow-up first |
| 4 | Gaia 2801267044426382336 | 12.59 | 6.6-9 M☉ | W4 excess ambiguous | Mid-IR follow-up first |
| 5 | Gaia 6784701430232308352 | 11.75 | 3.5 M☉ | W4 excess ambiguous | Mid-IR follow-up first |
| — | Gaia 5889532732877344128 | 12.67 | (was 13) | photometric contamination | dropped |
| — | Gaia 5942873714068259584 | 12.96 | (was 4) | confirmed contamination | dropped |
| — | A-dwarf 245948793944575360 | 11.80 | (was 6) | Filter #31 FAIL | dropped |

## How this changes the v1.22 list

v1.22 had **10 dormant_BH_candidate rows**. After parallel deep dive:
- 2 SURVIVE all filters: TYC 1363, HD 207141
- 3 are W4-ambiguous (need mid-IR follow-up): TYC 8785, Gaia 2801267,
  Gaia 6784701
- 5 are demoted: Gaia 5889532, Gaia 5942873, A-dwarf, plus the v1.20
  removals (HD 147132 K_1 fail, TYC 436-126-1 false positive)

**Robust headline v1.23**: 2 BH + 3 BH-pending + 3 NS + 32 BD = 40 candidates
with much more conservative tier 1 claims.

## The science the deep dive enables

1. **Filter #30 + #31 paper**: Mature methodology contribution. 4 UMi
   calibration + K-giant filter + A-dwarf Filter #31 case + Andrews+ 2026
   alignment. Self-contained, no telescope time required.

2. **Dual RV campaign on TYC 1363 + HD 207141**: Builds a sample of 2
   mass-gap detections from a single methodology. Either both confirm
   (publishable as discovery pair) or one fails (publishable as
   continued calibration).

3. **W4 excess investigation as a sub-paper**: The fact that 3 of 7 BH
   leads show clean K-W3 but excess K-W4 is itself an interesting
   sub-question for the methodology. If the W4 excess is debris disks,
   that's a "BH-host stars with disks" connection. If it's background
   blending, that's a known WISE caveat to document.

## Files

- `parallel_deep_dive_2026_05_27.csv` — raw triage data (8 sources)
- `docs/FINAL_VERDICT_2026_05_27.md` — (this file)
- `docs/TOP_LEADS_SUMMARY_2026_05_27.md` — full leads summary
- `docs/Filter31_proposal_2026_05_27.md` — Filter #31 methodology paper
- `docs/TYC_1363-2339-1_mini_dossier_2026_05_27.md` — inaugural target
- `docs/HD207141_deep_dive_2026_05_27.md` — secondary target
- `docs/observing_proposal_sketch_TYC_1363-2339-1.md` — proposal ready
- `docs/AFK_HANDOFF_2026_05_27.md` — single entry point
- `docs/dev_notes/COMPANIONS_OF_ALL_KINDS_PIVOT_2026_05_18.md` — full pivot
- `scripts/parallel_deep_dive_2026_05_27.py` — re-runnable script
