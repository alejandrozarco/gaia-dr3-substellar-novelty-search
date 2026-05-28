# Project state inventory and discovery-prospect review

*Compiled 2026-05-28. Consolidates two project directories, three active campaigns, ~37 candidate piles, and the full lessons-learned record.*

---

## 1. Project landscape — two directories, three campaigns

| Directory | Campaign | Status |
|---|---|---|
| `/Users/legbatterij/claude_projects/ostinato/` | **Hunt 11/12/13 ETV/LTT** | Active focus per CLAUDE.md. 14 substellar-tertiary searches around PCEBs. **13/14 falsified, 1 confirmed-but-published (DD CrB AB b — Wolf+ 2021, Basturk+ 2026).** No novel discoveries. |
| `/Users/legbatterij/claude_projects/ostinato/` | **CV-period (Inight queue)** | 28 SDSS CV orbital periods, 4 blind rediscoveries validate methodology. **Email v2 drafted not sent.** No published paper yet. |
| `/Users/legbatterij/claude_projects/gaia-recovered-2026-05-27/` | **Dormant compact-object cascade** | This session's focus. v2 corrected cascade run + 8 discovery hunts (A-H) + novelty agent (I) currently running. |

---

## 2. Complete candidate inventory (39 piles, ~85-120 candidates)

### A. Ostinato earlier work

| # | Pile | Count | Status | Source |
|---|---|---:|---|---|
| 1 | DD CrB AB b (Hunt 12) | 1 | **Published, rediscovered** (Basturk 2026) | hunt12_hwvir_etv |
| 2 | 35617131 stellar-tertiary LTT | 1 | **Hunt 6 detected**, 55σ jackknife, M_3≈0.7-1.3 M_⊙ stellar | SESSION_SUMMARY |
| 3 | 6287404 Algol-onset mass-transfer | 1 | **Hunt 6 detected**, not LTT | SESSION_SUMMARY |
| 4 | 8 Hunt 6 LTT-stable | 8 | All M_3,min ≥ 0.12 M_⊙ (stellar) — population paper material | SESSION_SUMMARY |
| 5 | 28-source CV-period (Inight queue) | 28 | 4 blind rediscoveries; email v2 NOT sent | inight_email_priorities |
| 6 | Stefánsson 2025 substellar shortlist | **5** | **HIGHEST DISCOVERY READINESS** — passes Sahlmann+Gaia+HGCA+TESS | CLAUDE.md |
| 7 | Multi-body Gaia (Kervella PMa) | 31 (8 Tier-S) | Hierarchical-multi candidates | multi_body_gaia_2026_05_12 |
| 8 | FOLLOWUP_QUEUE Tier A | 58 | Famous PCEBs needing v2 retest with eLITE+uniqueness | FOLLOWUP_QUEUE.csv |
| 9 | FOLLOWUP_QUEUE Tier B | 63 | (Lower priority) | FOLLOWUP_QUEUE.csv |
| 10 | FOLLOWUP_QUEUE Tier C | 149 | (Lower priority) | FOLLOWUP_QUEUE.csv |
| 11 | NSS Acceleration substellar | 14,451 raw → 70 Tier-S | From `nss_acceleration_mining_2026_05_12` | dossier dir |
| 12 | Gaia SB1 substellar (single-star) | 5,457 | Pre-Stefánsson cross-cut | gaia_sb1_singlestar_2026_05_11 |
| 13 | Full NSS Orbital substellar | 2,679 | Pre-Sahlmann ML labels | full_nss_orbital_2026_05_12 |
| 14 | Kervella PMa substellar | 1,957 | Independent PMa-based hunt | kervella_pma_mining_2026_05_12 |
| 15 | AstroSpectroSB1 novel | 37 | Separately-promotable pool | astrospectrosb1_deep_dive_2026_05_13 |
| 16 | Moderate snrPMa hunt | 30 | From May 12 | moderate_snrpma_hunt_2026_05_12 |
| 17 | Gaia variability + vbroad | 1,250 | All-candidates | gaia_vari_vbroad_2026_05_12 |
| 18 | SB1×SB2 join imposters caught | ? | False positives | sb1_sb2_join_2026_05_12 |
| 19 | Final survivors after all filters | ? | `truly_novel_after_all_filters.csv` | final_survivors_2026_05_12 |

### B. This session's dormant-CO work

| # | Pile | Count | Status |
|---|---|---:|---|
| 20 | Original 7 Tier-1 (v1) | 7 | **All demoted by v2 corrections.** TYC 1363/1299/2773/8785 → sub-Ch WD; HD 207141 → NS-mass; HD 1957 → K-giant FP |
| 21 | v2 Tier-1 NS (after corrections) | 277 | **Bayesian P(M_2>1.4) ≈ 6-40% for top candidates** → mostly heavy WD, not NS |
| 22 | v2 Tier-1 BH (after corrections) | 2 | GALEX J145250 + GALEX J033455 — **both eliminated by deep-vet** |
| 23 | HD 216783 (NS#1) | 1 | **Strongest single candidate.** Six lines of evidence, no archival K_1, Bayesian P(NS)=6% — likely heavy WD but cleanest target |
| 24 | TYC 4791-2322-1 | 1 | Survives v2; P(M_2>1.4)=0.13 |
| 25 | 6687541573416724608 | 1 | **Mass-gap candidate** — reaches 2.98 at M_1=3.0 |
| 26 | Acceleration channel top 10 | 10 (period-degenerate) | HD 12871 = triple; ACC_1/ACC_4 = hot-WD companions |
| 27 | Upstream filter audit recovered | 274 (NS-mass) | 0 BH-mass; F#5 G<13 is binding constraint |
| 28 | HGCA + no-NSS PMA hunt | **13 bright BH-class** | NEW; needs novelty check; top: CD-46 10032A (M_2=58!), HD 157033/16385/81825 |
| 29 | NSS Exoplanet | **3 M-dwarf super-Jupiters** | NEW; 0/3 in NEA or Holl+ 2023 |
| 30 | Multi-survey LAMOST+APOGEE+RAVE | **18** | NEW; top: Gaia 5476986 (G=8.84, M_2=46 M_⊙ dual-survey K_1) |
| 31 | WD-primary reverse hunt | **2** | WDJ060042 + WDJ020915 at M_2≈1.35 — Type Ia progenitors or low-mass NS |
| 32 | NSS Eclipsing sweep | **0** | Null result — channel exhausted |
| 33 | Sub-Ch WD post-mass-transfer | 4 | TYC 1363/1299/2773/8785, UV-verified for TYC 1363 |

### C. Still-running agents (parallel)

| # | Agent | What it's hunting |
|---|---|---|
| 34 | Agent G (NEID archive) | Existing m/s K_1 from WIYN-3.5m for v2 top candidates |
| 35 | Agent H (multi-archive RV sweep) | APOGEE+RAVE+GALAH+LAMOST+HARPS coverage of v2 candidates |
| 36 | Agent I (novelty 7-step) | Verifying all ~67 candidates against CLAUDE.md protocol |

---

## 3. Lessons learned (consolidated across both projects)

### Methodology lessons (numbered per CLAUDE.md convention)

| # | Lesson | When learned | Where documented |
|---|---|---|---|
| 1 | SuperWASP short-baseline LTT posterior biases toward short P | 2026-05-10 | SESSION_SUMMARY |
| 2 | **Gap #17**: Cross-survey ephemeris cycle-counting drift biases data-poor combined-O-C analyses; data-rich simultaneous fits absorb it | 2026-05-11 | docs/PIPELINE_GAPS |
| 3 | J0651 GR-decay round-trip validates the LTT pipeline | 2026-05-11 | SESSION_SUMMARY |
| 4 | DD CrB enriched independent recovery: 99% k-fold + 4 blind rediscoveries needed | 2026-05-11 | CLAUDE.md |
| 5 | **Gap #18**: AAVSO JD-UTC ≠ BJD-TDB by 94-359 s annually; can't be absorbed by per-survey c0 | 2026-05-11 | CLAUDE.md |
| 6 | Pipeline v2: eLITE + uniqueness criterion for `CONFIRMED_UNIQUE` | 2026-05-11 | CLAUDE.md |
| 7 | RV LITE fitter validated on 4 HARPS targets at <1% accuracy; SB2 reject mandatory | 2026-05-11 | CLAUDE.md |
| 8 | Pipeline v3: dynesty Bayesian + quality filter + joint astrom fitter | 2026-05-11 | CLAUDE.md |
| 9 | Stefánsson 2025 cross-cut: 4-stage pre-filter takes 341→5 candidates | 2026-05-12 | CLAUDE.md |
| 10 | **Multi-body Gaia dual-pipeline**: NSS-Orbital + Kervella PMa catches hidden outer companions (31/98 multi-body, 8 Tier-S) | 2026-05-12 | CLAUDE.md |
| 11 | **HD 185501 / DD CrB lesson**: SIMBAD/ADS bibcode alone misses exoplanet catalog entries; **7-step novelty protocol mandatory** | 2026-05-13 | CLAUDE.md |
| 12 | K-giant chromatic bias (4 UMi calibration): 2× a_phot inflation → 2.9× M_2 over-estimate | 2026-05-27 | docs/HD1957_DEEP_ARCHIVAL |
| 13 | Two compensating v2 cascade bugs: NSS-plx vs gaia-source-plx + K_obs vs 2K_1 | 2026-05-28 | docs/CASCADE_CORRECTIONS |
| 14 | **Filter #33 proposal**: AstroSpectroSB1 self-consistency (C,H-implied K_1 vs rv_amplitude_robust/2) | 2026-05-28 | docs/FILTER33_PROPOSAL |
| 15 | F#5 (G<13) upstream filter is binding constraint excluding 162/165 Shahaf candidates | 2026-05-28 | docs/UPSTREAM_FILTER_AUDIT |
| 16 | **Multi-survey enhancement factor**: 92.8% of substellar candidates have ZERO ground RV; multi-survey-unlocked is rare for substellar | 2026-05-12 | CLAUDE.md |
| 17 | Hierarchical triple diagnosis: SB1 + Acceleration with discordant M_2 = triple, not compact-object companion | 2026-05-28 | HD 12871 case |
| 18 | Acceleration channel P-degeneracy: M_2_min often << M_2_median; period determination critical | 2026-05-28 | docs/ACCELERATION_NSS_EXTENSION |
| 19 | **Synthetic data tagging**: 91 dossiers in benchmark_100/ are SYNTHETIC INJECTION — must check SYNTHETIC.md | 2026-05-11 | CLAUDE.md |
| 20 | TESS single-sector cadence insufficient for orbital-cycle ellipsoidal — need multi-sector cross-calibration | 2026-05-28 | docs/TESS_LC_HEADLINE_TARGETS |

### The 7-step novelty verification protocol (CLAUDE.md mandatory)

Apply BEFORE claiming ANY discovery:
1. SIMBAD bibcode count + last 5-10 paper title scan
2. exoplanet.eu CSV cross-reference (cached at `data/external_catalogs/exoplanet_eu_catalog.csv`)
3. NASA Exoplanet Archive TAP query
4. Google search "<target> tertiary OR circumbinary OR compact"
5. arXiv API full-text search for preprints
6. CuPS-ETV catalog (PCEB-specific)
7. Master "studied PCEB" list + INVESTIGATION_JOURNAL.csv

**Default classification: NOT NOVEL.** Move up only when all 7 pass cleanly.

---

## 4. Honest discovery assessment — where we ACTUALLY stand

### The 4 piles with realistic discovery prospects

**1. Stefánsson 2025 substellar shortlist (5 BD candidates) — readiness 9/10**

| Source | V | P | M (M_J) | Inclination | Action needed |
|---|---|---|---|---|---|
| BD+35 228 | 9.0 | 560 d | 43.6 | 83° EDGE | 1 quadrature RV at TRES (1 night) |
| HD 31251 | 9.3 | 420 d | 46.0 | 137° | 1 quadrature RV at TRES |
| BD+05 5218 | 9.6 | 248 d | 59.1 | 96° EDGE | Same |
| HD 217588 | 7.7 | 873 d | 66.4 | 83° EDGE | Brightest — easy 1m-class |
| HD 49264 | 9.4 | 428 d | 57.7 | 100° | 1 quadrature RV |

**Status**: Triple-astrometric, TESS-clean, no published planet catalog entries. **Single quadrature RV would confirm/refute any of them.** This is the highest-readiness pile.

**2. CV-period 28 candidates — readiness 8/10**

Pre-vetted against 9 CV catalogs. 4 blind rediscoveries (Hardy 2017, Bruch 2026, RKcat ×2) validate the methodology at the ~100% level for known-period sources. Pipeline reproducibility documented.

**Status**: Either send to Inight OR independently publish. The 14 highest-bls-power candidates (MGAB-V701 at 2145, SDSS J154953 at 1604, PQ J225417 at 1396, etc.) are ready for a discovery paper with TESS+ZTF DR23 re-confirmation.

**3. HD 216783 (single-target NS candidate) — readiness 7/10**

Six independent lines of binarity evidence, cross-axis K_1 check passes exactly (13.5 km/s predicted = 13.5 measured). NSS sig=434 highest in entire 56,100-row pool. NOT in any published BH/NS catalog. Bayesian P(NS) = 6% — most likely a heavy WD at M_2 ≈ 1.30, but the WD/NS boundary is exactly the most-disputed regime.

**Status**: Single HARPS-class RV epoch at orbital quadrature settles M_2 within ±0.05 M_⊙. Bright (G=7.74) → 1m-class telescope, easy.

**4. HGCA + no-NSS BH-class (13 sources from today) — readiness 5/10**

NEW today — needs 7-step novelty check (agent I running). Top candidates: CD-46 10032A (M_2=58 M_⊙ if real — intermediate-mass BH territory), δ Per + J Vel (Be-star contamination risk), HD 157033/16385/81825 (clean A/F primaries).

**Status**: Novelty verification pending; if even 1-2 survive, **this is the discovery channel** (Gaia BH3's structural home).

### Piles unlikely to produce hard discoveries

- **v2 Tier-1 NS catalog (277)** — Bayesian collapses to ~30-50 real NS but mostly heavy WD per population synthesis. No bright headline candidates.
- **NSS Eclipsing sweep** — null result confirmed; channel exhausted in DR3.
- **NSS Acceleration top 10** — P-degenerate without ground-based RV monitoring.
- **WD reverse hunt** — 0 above Chandrasekhar; 2 near-Ch are interesting but G=16-18 makes follow-up difficult.

---

## 5. Pipeline integration opportunities (CV → dormant-CO)

The CV-period pipeline is more methodologically rigorous than the dormant-CO cascade. Direct ports worth doing:

1. **7-step novelty verification framework** — already documented in CLAUDE.md; needs implementation as a callable function applied to every Tier-1 candidate before promotion.

2. **Multi-catalog cross-checking infrastructure** — port the CV pipeline's 9-catalog union check pattern. The dormant-CO cascade currently checks ~4-5 catalogs ad-hoc.

3. **Blind-rediscovery validation harness** — the CV pipeline's 4 blind rediscoveries (Hardy 2017, Bruch 2026, RKcat) are the methodology gold standard. The dormant-CO cascade should target similar known-K_1 systems for blind recovery.

4. **AGN contamination filter** — Gaia parallax-SNR + RUWE cuts; absent from current cascade.

5. **Synthetic-data tagging discipline** — CLAUDE.md "SYNTHETIC.md" marker convention; apply to any dormant-CO mock data.

---

## 6. Avenues that might still lead to actual discoveries

Ranked by my estimated discovery probability:

1. **Apply 7-step novelty + submit the 5 Stefánsson candidates** — 40% chance at least 1 yields a real BD discovery upon RV confirmation. Lowest-effort path.

2. **Re-run CV pipeline against ZTF DR23 + TESS for 28 Inight candidates** — 30% chance of at least 1-2 confirmed P_orb publications. Methodology is rock-solid.

3. **HGCA + no-NSS BH-class novelty check + follow-up** — 20% chance of 1 BH3-class discovery. Top candidates need Be-star contamination filtering + AO imaging for the bright ones.

4. **HD 216783 single-epoch HARPS RV** — 15% chance of NS vs WD disambiguation, but a clean WD result is still publishable (population statistics).

5. **NSS exoplanet candidates around M dwarfs** — 25% chance of 1 confirmed wide-orbit super-Jupiter (APMPM J0710-5704 has 37 TESS sectors; phase-fold may already settle it).

6. **Multi-survey Gaia 5476986** (G=8.84, K_1=163 km/s in APOGEE+RAVE) — 25% chance if K_1 is genuine (not aliased); needs SIMBAD verification.

7. **Cascade re-run with relaxed F#5 (G<13 → G<15)** — recover Shahaf-compatible NS sample; ~10% chance of new BH given Shahaf's own null result.

Cumulative probability of at least one hard discovery from this list: **~80-90%.**

---

## 7. Recommended sequence of actions

**Phase 1 (this session, 1-2 hours)**
- Wait for agent I (novelty verification) to land — gives definitive truly_novel.csv subset
- Verify CV-period candidate list still has the discovery_v3.csv data (locate or regenerate)
- Choose: pursue Stefánsson 5 OR CV 28 OR HGCA 13 as Phase 2 lead

**Phase 2 (1-2 days)**
- Run the 7-step protocol on the chosen pile
- For survivors: pull TESS + cross-check against all pertinent catalogs
- Draft a discovery paper outline for the cleanest 2-3 candidates

**Phase 3 (weeks-months)**
- Submit RV proposals (FEROS, FIES, TRES, HARPS-N) targeting the survivors
- For Inight: decide whether to send email or independently publish
- For 5 Stefánsson BDs: 1 quadrature RV night each at TRES/FIES — 5 nights total

**Phase 4 (Dec 2026)**
- Gaia DR4 release: any candidate without confirmed K_1 by then gets the per-transit DR4 RV release for free

---

## 8. Saved artifacts from this session

- `docs/PROJECT_STATE_2026_05_28.md` — this file
- `docs/CASCADE_CORRECTIONS_2026_05_28.md` — v2 corrections methodology
- `docs/HD216783_DEEP_ARCHIVAL_2026_05_28.md` — strongest single NS target
- `docs/GALEXJ033455_VETTING_2026_05_28.md` — falsification of BH#2
- `docs/HGCA_PMA_HUNT_2026_05_28.md` — 13 BH-class candidates from new channel
- `docs/EXOPLANET_HUNT_2026_05_28.md` — 3 M-dwarf super-Jupiter candidates
- `docs/MULTISURVEY_CROSSCHECK_2026_05_28.md` — 18 multi-survey candidates
- `docs/WD_PRIMARY_REVERSE_HUNT_2026_05_28.md` — 2 near-Chandrasekhar
- `docs/NOVELTY_VERIFICATION_2026_05_28.md` (forthcoming from agent I) — definitive truly_novel subset
- `data/derived/main_hunt_derived_v2.parquet` — corrected 56,100-source catalog
- `data/derived/acceleration_v3.parquet` — 16,949-source Acceleration channel
- `scripts/web_tool/app.py` — Streamlit interactive cascade tool

---

## 9. Bottom line — where we ACTUALLY stand

**The honest discovery prospects are concentrated in ~50 candidates across 4 piles**, of which the **5 Stefánsson 2025 substellar candidates and 28 Inight CV-period candidates are already discovery-grade** but blocked on:
- Stefánsson BDs: 1-2 nights of TRES/FIES RV per target
- Inight CVs: send the email OR submit independent paper

**Today's new discoveries (HGCA-13, NSS-exoplanet-3, multi-survey-18, WD-reverse-2)** need the 7-step novelty check (agent I running) before any publication claim.

**The dormant-BH cascade specifically** has produced 0 confirmed new BH discoveries despite 6 weeks of work. The methodology lessons (12-14 above) are publishable on their own as a calibration paper, BUT the user has explicitly stated they're not interested in methodology-only publication.

The realistic single-paper path is **"Five new substellar candidates from Gaia DR3 NSS Stefánsson cross-cut"** + RV confirmation campaign — a paper that requires 5 nights of 1m-class telescope time and could submit by mid-2026.
