# Master objects of interest — all confirmed-novel candidates

*Consolidated 2026-05-28. Single source of truth for every candidate currently in our discovery queue.*

This document supersedes all prior candidate lists (PAPER_READY_CATALOG, FINAL_VERDICT, TOP_LEADS_SUMMARY). Older catalogs are kept in `data/archive/` for reference but should NOT be used as the current candidate state.

---

## Headline summary

| Category | Truly novel | Discovery-grade* | Notes |
|---|---:|---:|---|
| **CV-period orbital periods** (Pile F) | **14** | **1** (CRTS J151836-0548) | MNRAS Letter drafted |
| **HGCA BH-class** (Pile A) | **8** | TBD | Per-candidate dossiers in progress (agent M) |
| **M-dwarf super-Jupiters** (Pile B) | **3** | TBD pending agent O TESS fold | Highest TESS leverage (APMPM J0710 has 37 sectors) |
| **WD-primary + dark companion** (Pile E) | **2** | TBD | Both NOT in SIMBAD — strongest novelty signal |
| **Stefánsson substellar** (Pile D) | **3** | TBD pending multi-channel verification | BD+05 5218 dropped (Stevenson 2023 scoop) |
| **Multi-survey dual-binarity** (Pile C) | **2** | Possibly Gaia 5476986 | APOGEE+RAVE K_1 cross-check pending |
| **Total truly novel** | **32** | **1 confirmed + 4-5 candidate-discovery-grade** | |

*Discovery-grade = independent second-method verification from archival data.*

---

## Pile A — HGCA + no-NSS BH-class candidates (8 truly novel)

Hunt source: `docs/HGCA_PMA_HUNT_2026_05_28.md`. 8 of 13 passed the 7-step novelty check.

| Source | Gaia DR3 / HIP | G | M_2_median (M_⊙) | Status | Action |
|---|---|---:|---:|---|---|
| **CD-46 10032A** | HIP 75406 | 10.6 | **58** | **Headline; Be-star contamination check pending (agent M)** | Confirm primary not Be |
| **HD 173689** | (TBD) | 7.2 | (BH-mass) | **Brightest novel** — easy follow-up | Single quadrature spec |
| **HD 157033** | (TBD) | <11 | (BH-mass) | Clean A/F primary | Kervella 2022 H2G2 cross-check (agent O) |
| **HD 16385** | (TBD) | <11 | (BH-mass) | A/F primary | Same |
| **HD 81825** | (TBD) | <11 | (BH-mass) | A/F primary | Same |
| **HD 37943** | (TBD) | (TBD) | (BH-mass) | Novel | Vetting needed |
| **HD 5514** | (TBD) | (TBD) | (BH-mass) | Novel | Vetting needed |
| **LP 155-298** | (TBD) | (TBD) | (BH-mass) | Novel | Vetting needed |

**Dropped from this pile:**
- δ Per (G=3.0), J Vel (G=4.5) — both Be* per SIMBAD; circumstellar-disc contamination risk
- HD 37419 — known visual triple ADS 4267, HGCA signal is the known inner pair (novelty agent caught it)

---

## Pile B — Wide-orbit super-Jupiters around M dwarfs (3 truly novel)

Hunt source: `docs/EXOPLANET_HUNT_2026_05_28.md`. All 3 passed 7-step novelty check. None in NASA Exoplanet Archive or Holl+ 2023.

| Source | SpT | d (pc) | M_2 (M_J) | P (d) | G | TESS sectors |
|---|---|---:|---:|---:|---:|---:|
| **APMPM J0710-5704** | M4V | **17** | 10-12 | 253 | 12.2 | **37** |
| **SCR J1441-7338** | M6V | 26 | 8-10 | 488 | 14.8 | (TBD via agent K) |
| **UCAC4 313-025977** | M4-M5V | 32 | 10-11 | 592 | (TBD) | (TBD via agent K) |

**APMPM J0710-5704 is the key target.** 37 TESS sectors at d=17 pc — agent O is folding all sectors at P=253d to search for transit (transit depth ≈ 1-2% if i=90° and R_p ≈ 1.3 R_Jup). Detection → instant discovery.

---

## Pile C — Multi-survey LAMOST + APOGEE + Gaia (2 truly novel of 3 verified)

Hunt source: `docs/MULTISURVEY_CROSSCHECK_2026_05_28.md`. Agent I verified 3 of 18.

| Source | G | RUWE | K_1 detection | Status |
|---|---:|---:|---|---|
| **Gaia DR3 5476986108823894400** | 8.84 | (high) | **APOGEE + RAVE both: K_1 ≈ 163 km/s** | Cross-survey + Gaia anomaly → spectro-astrom agreement pending (agent O) |
| **Gaia DR3 604914983655019520** | (TBD) | 3.14 | K_1 ≈ 73 km/s | Cleanest dual-method, M_2 ≈ 5.7 M_⊙ |
| ~~HD 46491 / NGC 2257 P AB~~ | — | — | — | **CONTESTED** (cluster-context check needed) |

**13 of 18 multi-survey candidates not yet vetted via 7-step.** Pending novelty check.

---

## Pile D — Stefánsson 2025 substellar shortlist (3 truly novel)

Hunt source: `CLAUDE.md` (ostinato). 4-stage Stefánsson + Sahlmann + HGCA + TESS pre-filter.

| Source | Gaia DR3 | V | P (d) | M (M_J) | i (°) | d (pc) | Status |
|---|---|---:|---:|---:|---:|---:|---|
| **BD+35 228** | 321123400368013696 | 9.0 | 560 | 43.6 | 83° EDGE | 134 | HGCA SNR=5.85 (corroborated) |
| **HD 217588** | 2842069508617361920 | **7.7** | 873 | 66.4 | 83° EDGE | 277 | Brightest |
| **HD 49264** | 5484481960625470336 | 9.4 | 428 | 57.7 | 100° | 115 | Triple-astrometric |

**Dropped from Pile D today:**
- **BD+05 5218** = **HIP 117179 b** — already published by Stevenson et al. 2023 (MNRAS 526, 5155 = arXiv:2310.02695) as a 44 M_J BD-desert candidate. Caught by exoplanet.eu CSV grep in 7-step protocol.
- HD 31251 — CONTESTED (SIMBAD SB* tag may be Gaia-NSS-induced)

---

## Pile E — WD primary + dark companion (2 truly novel)

Hunt source: `docs/WD_PRIMARY_REVERSE_HUNT_2026_05_28.md`. Both NOT IN SIMBAD AT ALL — strongest possible novelty signal.

| Source | Gaia DR3 | M_1 (WD) | M_2 (M_⊙) | P (d) | G | Notes |
|---|---|---:|---:|---:|---:|---|
| **WDJ060042.75-293041.36** | 2909342818326298112 | 0.612 | **1.368** | 935 | 18.4 | GALEX-confirmed WD; potential Type Ia progenitor (if WD+WD) or low-mass NS |
| **WDJ020915.51+380425.92** | 332248057157474176 | 0.718 | **1.323** | 274 | 16.2 | DA WD; short period → tractable RV follow-up |

Both sit just above the Chandrasekhar limit. Companion identity (WD vs NS) needs UV photometry + IR excess test (agent L pending).

---

## Pile F — CV-period orbital periods (14 truly novel)

Hunt source: `docs/CV_PERIOD_REFRESH_2026_05_28.md` (agent J refresh). All 14 confirmed by ZTF DR23. 5 with TESS coverage. **Paper drafted: `docs/CV_PERIOD_PAPER_DRAFT_2026_05_28.md`.**

| # | Name | RA | Dec | G | P (min) | Subtype | TESS confirmation |
|---:|---|---:|---:|---:|---:|---|---|
| 1 | MGAB-V701 | 204.066 | +38.159 | 19.39 | 29.41 | DN | — (faint) |
| 2 | SDSS J154953.41+173939.0 | 237.473 | +17.661 | 19.44 | 116.68 | NL: | — |
| 3 | PQ J225417.5+074227 | 343.573 | +7.708 | 18.78 | 232.15 | CV | — |
| 4 | (unnamed) | 128.518 | +18.905 | 19.23 | 172.00 | Polar | — |
| 5 | CRTS J212654.5-012053 | 321.727 | -1.348 | (TBD) | 213.03 | Polar | — |
| 6 | CRTS J164017.8+080822 | 250.074 | +8.140 | 16.10 | 105.43 | U Gem | — |
| 7 | SDSS J091935.66+502825.1 (J0919) | 139.899 | +50.474 | 19.86 | 93.51 | DN | TESS S21 (2020-Feb superoutburst found) |
| 8 | SDSS J110706.76+340526.8 | 166.778 | +34.091 | 19.48 | 95.84 | DN: | — |
| 9 | SDSS J115419.06+575750.9 | 178.579 | +57.964 | 20.62 | 21.58 | ER UMa: | — |
| 10 | CRTS J151836.0-054803 | 229.650 | -5.801 | 16.50 | 24.64 | DN | **TESS 24.9% eclipse at BLS P (paper headline #2)** |
| 11 | SDSS J160419.02+161548.5 | 241.079 | +16.263 | 19.09 | 128.80 | SU UMa | TESS 23% eclipse |
| 12 | SDSS J080142.37+210345.8 | 120.426 | +21.063 | 18.86 | 115.11 | Polar: | — |
| 13 | **CRTS J051419.8+011120** | 78.583 | +1.189 | **15.40** | 180.05 | DN | **TESS 25% eclipse at 3.013 hr — STRONGEST PURE IN-GAP DN (paper headline #1)** |
| 14 | SDSS J115639.48+630907.7 | 179.164 | +63.152 | 20.72 | 29.13 | Polar | — |

**4 blind methodology rediscoveries** (validation lower bound):
- CRTS J041133.6-090729 → 93.7 min ✓ RKcat 7.24 (93.6 min)
- CRTS J163120.8+103133 → 91.9 min ✓ RKcat (90.3 min)
- CRTS J233003.0+303300 → 224.6 min ✓ Hardy 2017 (224.6 exact)
- CRTS J005152.8+204017 → 295.7 min ✓ Dağ 2026 / Bruch 2026 (290.6, 2% off)

---

## Confirmed FALSIFIED / NOT-NOVEL (do not pursue)

| Source | Status | Why |
|---|---|---|
| ~~GALEX J033455+000910~~ | NOT_NOVEL | Simon+ 2026 (arXiv:2603.20371) published as WD (M_2 ≤ 0.9 M_⊙) via 7 MIKE + 4 FEROS + APOGEE + LAMOST RV epochs |
| ~~GALEX J145250-192225~~ | DISPUTED | Already in Shahaf+ 2023 Triage I (M_2=11.9 M_⊙); Tanikawa+ 2023 self-consistency cut; TESS ellipsoidal 0.138% (4.6× too high for face-on); RAVE-Gaia RV drift inconsistent with face-on |
| ~~HD 1957~~ | DEMOTED | K-giant chromatic FP per F#30 v2 logg fallback (GSP-Spec ANN logg=2.63) |
| ~~HD 207141~~ | DEMOTED | M_2 = 7.57 → 1.31 with NSS plx correction; now NS-mass at WD/NS boundary |
| ~~TYC 1363-2339-1, TYC 1299-727-1, TYC 2773-348-1, TYC 8785-1657-1~~ | DEMOTED | M_2 = 3.2-3.9 → 1.0-1.2 with NSS plx correction; sub-Ch CO-WD companions verified by GALEX UV (1 of 4) |
| ~~TYC 4791-2322-1~~ | DEMOTED | M_2 = 2.66 → 1.34 with NSS plx; F#32 sin_i_implied = 1.51 fails joint check |
| ~~BD+05 5218~~ = HIP 117179 b | NOT_NOVEL | Stevenson 2023 already published as 44 M_J BD; in exoplanet.eu |
| ~~HD 37419~~ | NOT_NOVEL | Known visual triple ADS 4267; HGCA signal is inner pair |
| ~~HD 12871~~ | NOT_NOVEL | Hierarchical triple — APOGEE 3-visit K_1=11.9 matches Gaia SB1 K_1=11.9; outer companion drives Acceleration |

---

## Pending verification (agents currently running)

| Agent | Hunting | Key result |
|---|---|---|
| K | M-dwarf super-Jupiter dossiers | Per-target HD-1957-style workups for 3 Pile B candidates |
| L | WD-primary dossiers | Type Ia progenitor verification for 2 Pile E candidates |
| M | HGCA BH-class dossiers | Be-star check + Kervella corroboration for CD-46 10032A + HD 173689 + HD 157033 |
| O | Discovery-grade verification | APMPM J0710 37-sector TESS fold; Gaia 5476986 spectro-astrom; Stefánsson 3 cross-channel; HGCA-8 Kervella |

---

## Paper roadmap (ordered by readiness)

| # | Paper | Status | Targets | Telescope time needed |
|---|---|---|---|---|
| **1** | **CV-period orbital periods** | **DRAFT READY** (4,800 words) | 14 candidates + 1 TESS-confirmed (CRTS J051419+0111 or CRTS J151836-0548) + 4 blind rediscoveries | None — archival only |
| 2 | M-dwarf super-Jupiters | Awaiting agent K + O | 3 candidates (APMPM J0710 is leverage) | 0-1 night CHIRON/NEID/FEROS per target |
| 3 | WD-primary Type Ia progenitor candidates | Awaiting agent L | 2 candidates | 6 mo HARPS/CHIRON campaign |
| 4 | HGCA-only BH-class candidates | Awaiting agent M | 8 candidates (3 priority) | 5-10 nights various |
| 5 | Stefánsson substellar | Awaiting agent O verification | 3 candidates | 4 nights TRES |
| 6 | Multi-survey Gaia 5476986 | Awaiting agent O verification | 1-2 candidates | 1 night confirmation |

---

## Methodology infrastructure that supports the discoveries

| Artifact | Purpose | Status |
|---|---|---|
| `scripts/streaming/consumer.py` | v1 cascade pipeline | Deprecated for verdicts, keep for fast first-pass |
| `scripts/streaming/v2_corrected/consumer_v2.py` | v2 cascade with NSS plx + K_obs/2 + F#30 logg fallback | Production |
| `scripts/streaming/v3_acceleration/` | NSS Acceleration channel (16,949 sources) | Production |
| `scripts/web_tool/app.py` | Streamlit interactive cascade UI | Production |
| `data/derived/main_hunt_derived_v2.parquet` | v2 56,100-source catalog | Authoritative for NSS Orbital pool |
| `data/derived/acceleration_v3.parquet` | Acceleration channel 16,949 candidates | Production |
| `data/derived/compact_object_candidates_unified.parquet` | v2 + v3 unified slim schema | 17,760 rows |
| `data/candidate_dossiers/novelty_verification_2026_05_28/` | 7-step novelty results | 23 truly_novel + 6 contested + 2 not_novel |
| `data/candidate_dossiers/hgca_pma_hunt_2026_05_28/` | HGCA + no-NSS hunt outputs | 13 candidates |
| `data/upstream_audit/` | F#5 binding-constraint audit | 165-source Shahaf-miss analysis |
| `docs/CASCADE_CORRECTIONS_2026_05_28.md` | v2 correction methodology | Reference for paper §2 |
| `docs/CASCADE_VALIDATION_EXTENDED_2026_05_28.md` | 70-source benchmark self-test | 93% recall, 14% FP, 4.5% mass error |

---

## Files retired to `data/archive/`

The following v1-cascade files are superseded by v2 and have been moved to `data/archive/v1_2026_05_27/`:

- `main_BH_all_filters_pass.csv/parquet` — v1 BH list (16 sources, mostly invalidated by v2 corrections)
- `main_NS_all_filters_pass.csv/parquet` — v1 NS list (104 sources, ~80% are heavy-WD per Bayesian)
- `main_NS_tiered_2026_05_27.csv` — v1 tiering (superseded by truly_novel.csv)
- `main_defensible_bh.parquet`, `main_defensible_ns.parquet` — pre-v2 defensible lists
- `main_hunt_derived.parquet` — v1 cascade output (use v2)
- `demoted_by_filter32_NS.csv` — v1 demotion list
- `BD_filter32_applied.csv` — v1 BD pool
- `live_stats_main.json` — ephemeral streaming stats
- `PAPER_READY_CATALOG_2026_05_28.md` (in docs/) — superseded by this document
- `TOP_LEADS_SUMMARY_2026_05_27.md`, `FINAL_VERDICT_2026_05_27.md` — superseded

The river ML model (`main_river_model.pkl`, 65 MB) is excluded from git via `.gitignore`.

---

## How to use this document

1. **For paper drafting**: use the per-pile sections to identify which paper each candidate belongs to.
2. **For follow-up planning**: use the "Telescope time needed" column in the paper roadmap.
3. **For novelty re-verification before submission**: the truly_novel.csv at `data/candidate_dossiers/novelty_verification_2026_05_28/` is the authoritative input; this document is human-readable summary.
4. **For lessons learned**: see `docs/PROJECT_STATE_2026_05_28.md` §3 (20 numbered lessons).
5. **For pipeline reproducibility**: see `docs/CASCADE_CORRECTIONS_2026_05_28.md` for the v2 corrections + `docs/CASCADE_VALIDATION_EXTENDED_2026_05_28.md` for the validation suite.
