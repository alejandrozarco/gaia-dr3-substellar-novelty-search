# Candidates — current state of the discovery queue

*v2.0.0 — 2026-05-28. Post-verification-pass single source of truth.*

This document lists every candidate currently in the queue, with per-target
M_2 / P / e / status and what second-method work has or hasn't been done.

The authoritative machine-readable backings are:

- `data/derived/main_hunt_derived_v2.parquet` — full v2 cascade output (56,100 rows; per-source `tier_v2`, `M2_msun_v2`, `sini_implied_v2`, `class_v2`)
- `data/derived/acceleration_v3.parquet`     — v3 NSS Acceleration channel (16,949 rows; per-source `tier_v3`, `M2_range_min_v3`, `M2_range_max_v3`)
- `data/derived/compact_object_candidates_unified.parquet` — slim union schema (17,760 rows)

The single-source web tool (`scripts/web_tool/app.py`) re-derives all
verdicts at runtime, so it stays in parity with whatever is in the
parquets.

---

## Headline summary

| Bucket | Count | Of which discovery-grade* |
|---|---:|---:|
| Confirmed discovery (independent second-method) | **1** | 1 |
| Strong candidate (single-method, archival follow-up identified) | **~6** | 0 |
| Tier-1 NS pool (v2 parquet, before per-target archival vetting) | 277 | — |
| Tier-1 BH pool (v2 parquet, before per-target archival vetting) | 2 | — |
| Tier-2 (RV-inconclusive, needs follow-up) | 87 | — |
| BD-candidate class | 80 | — |
| Planet-candidate class | 2 | — |
| v3 acceleration P-degenerate compact-object candidates | 10,818 | — |
| Demoted / falsified by second-method verification | ~26 (named) | — |

*Discovery-grade = independent second-method verification from archival data.*

The Tier-1 pools above are filter-cascade outputs, not vetted-claim
candidates. Most Tier-1 NS sources are statistically consistent with
heavy-WD companions at the M_2 ≈ 1.1-1.4 M_⊙ boundary; per-target
verification (HGCA, Kervella H2G2, multi-archive RV) is required before
any single source moves to the strong-candidate column.

---

## Confirmed discoveries

### CRTS J051419+0111  (Gaia DR3 source matched via coord)

| Field | Value |
|---|---|
| Discovery | TESS photometric eclipse at the ZTF-derived 3.013-hr orbital period |
| Depth | 25% (eclipse) |
| Subtype | DN (dwarf nova) in the period gap |
| Why headline | Strongest pure in-gap DN in the refresh batch; eclipse depth + ZTF period agreement is independent second-method confirmation |
| G | 15.40 |
| RA, Dec | 78.583, +1.189 |

This is the only candidate in the entire queue with an independent
second-method confirmation from archival data.

---

## Strong candidates — single-method, archival follow-up identified

### HGCA + Kervella H2G2 — survivor from Pile A

| Source | M_2 | P | Notes |
|---|---:|---:|---|
| **HD 157033** | ~4 M_⊙ | ~10 yr | HGCA + Kervella H2G2 + NSS plx all aligned. GALAH DR4 RV time-series available (no telescope time required for first verification). Other 7 Pile-A targets demoted: Kervella M_2 = 0.4-2.9 M_⊙ → stellar binaries. |

### WD-primary + sub-Chandrasekhar-to-Chandrasekhar companion (Pile E)

| Source | Gaia DR3 | M_1 (WD) | M_2 (M_⊙) | P (d) | G |
|---|---|---:|---:|---:|---:|
| **WDJ060042.75-293041.36** | 2909342818326298112 | 0.612 | **1.368** | 935 | 18.4 |
| **WDJ020915.51+380425.92** | 332248057157474176  | 0.718 | **1.323** | 274 | 16.2 |

Both companions sit just above the Chandrasekhar limit on the NSS
mass function. Companion identity (massive WD vs low-mass NS) needs
UV photometry + IR excess test. Neither primary is in SIMBAD — among
the strongest novelty signals in the queue.

### M-dwarf super-Jupiters (Pile B)

| Source | SpT | d (pc) | M_2 (M_J) | P (d) | G | TESS sectors |
|---|---|---:|---:|---:|---:|---:|
| **APMPM J0710-5704**   | M4V    | 17 | 10-12 | 253 | 12.2 | 37 |
| **SCR J1441-7338**     | M6V    | 26 | 8-10  | 488 | 14.8 | TBD |
| **UCAC4 313-025977**   | M4-M5V | 32 | 10-11 | 592 | TBD  | TBD |

APMPM J0710 is the key target: 37 TESS sectors at d=17 pc. Phase-fold
at P=253d gives depth = 0.18% vs predicted 6.6% for R_p = 1 R_J at
i=90° — i.e. non-eclipsing. Non-detection doesn't refute the planet
(inclination geometry) but cannot promote to discovery without RV.

### Stefánsson 2025 substellar shortlist (Pile D)

| Source | Gaia DR3 | V | P (d) | M_2 (M_J) | d (pc) |
|---|---|---:|---:|---:|---:|
| **BD+35 228**  | 321123400368013696  | 9.0 | 560 | 43.6 | 134 |
| **HD 217588**  | 2842069508617361920 | 7.7 | 873 | 66.4 | 277 |
| **HD 49264**   | 5484481960625470336 | 9.4 | 428 | 57.7 | 115 |

All 3 show Kervella H2G2 M_2 a factor of 3 *lower* than the NSS-M_2
— consistent with hierarchical triples, not single-companion BD
verification. Per-target archival RV needed.

### CV-period orbital periods (Pile F siblings to the confirmed discovery)

13 more sources with ZTF DR23-confirmed orbital periods in the CV
regime (5 with TESS coverage). Detailed table at the end of this
document. The headline confirmation is CRTS J051419+0111 above; the
rest await per-target archival cross-check.

---

## Tier-1 BH pool — both candidates demoted by second method

| Source (Gaia DR3) | v2 M_2 | Status |
|---|---:|---|
| 6281177228434199296 (GALEX J145250-192225) | 12.75 | **DISPUTED**. Already in Shahaf+ 2023 Triage I (M_2 = 11.9 M_⊙); Tanikawa+ 2023 self-consistency cut; TESS ellipsoidal 0.138% (4.6× too high for face-on); RAVE-Gaia RV drift inconsistent with face-on geometry. |
| 3263804373319076480 (GALEX J033455+000910) | 3.22  | **FALSIFIED**. Simon, Lam, El-Badry, Reggiani 2026 (arXiv:2603.20371) published as WD with M_2 ≤ 0.9 M_⊙ via 7 MIKE + 4 FEROS + APOGEE + LAMOST RV epochs. |

After second-method verification, **no surviving discovery-grade BH
candidates remain** in the v2 NSS Orbital pool. The HGCA-only hunt
likewise produced no BH-class survivor (7/8 Pile-A candidates demoted
to stellar binaries by Kervella H2G2).

The v3 Acceleration channel (10,818 P-degenerate sources, M_2_max
envelopes only) contains the BH3-regime parameter space but cannot
produce single-target BH claims without an independent period
constraint.

---

## Demoted / falsified by second-method verification

| Source | Previous claim | Why demoted |
|---|---|---|
| GALEX J033455+000910                                  | Tier-1 BH 3.2 M_⊙ | Simon+ 2026 published as WD |
| GALEX J145250-192225                                  | Tier-1 BH 12.8 M_⊙ | Already in Shahaf+ 2023; TESS ellipsoidal + RAVE-Gaia drift inconsistent |
| HD 1957                                               | Tier-1 NS         | K-giant chromatic FP per v2 F#30 logg fallback (GSP-Spec ANN logg = 2.63) |
| HD 207141                                             | Tier-1 NS 7.6 M_⊙ | M_2 = 7.57 → 1.31 with NSS plx correction; now WD/NS boundary |
| TYC 1363-2339-1, TYC 1299-727-1, TYC 2773-348-1, TYC 8785-1657-1 | Tier-1 NS 3.2-3.9 M_⊙ | M_2 → 1.0-1.2 with NSS plx; sub-Chandrasekhar CO-WD companions |
| TYC 4791-2322-1                                       | Tier-1 NS 2.66 M_⊙ | M_2 → 1.34 with NSS plx; F#32 sin_i_implied = 1.51 fails joint check |
| Pile-A HGCA "BH-class" (7 of 8)                       | BH-class headlines | Kervella H2G2 M_2 = 0.4-2.9 M_⊙ at 5-AU reference → stellar binaries |
| BD+05 5218 = HIP 117179 b                             | Stefánsson BD     | Stevenson 2023 already published as 44 M_J BD; in exoplanet.eu |
| Gaia DR3 5476986108823894400                          | Multi-survey K_1=163 km/s | RETRACTED — RAVE σ=115 km/s is pipeline noise, not phase-folded amplitude. Primary is A1IV V=8.82, not in any Gaia NSS table. |
| HD 12871                                              | NS candidate      | Hierarchical triple — APOGEE 3-visit K_1 = 11.9 km/s matches Gaia SB1 K_1 = 11.9; outer companion drives Acceleration |
| HD 37419                                              | HGCA BH-class     | Known visual triple ADS 4267; HGCA signal is inner pair |
| APMPM J0710-5704 (as transit detection)               | Discovery via TESS eclipse | TESS depth 0.18% vs predicted 6.6% for i=90° → non-eclipsing geometry. Planet not refuted; just cannot be promoted to discovery from photometry alone. |

---

## Pile F CV-period table

| # | Name | RA | Dec | G | P (min) | Subtype | TESS confirmation |
|---:|---|---:|---:|---:|---:|---|---|
| 1  | MGAB-V701                       | 204.066 | +38.159 | 19.39 | 29.41  | DN       | — (faint) |
| 2  | SDSS J154953.41+173939.0        | 237.473 | +17.661 | 19.44 | 116.68 | NL:      | — |
| 3  | PQ J225417.5+074227             | 343.573 | +7.708  | 18.78 | 232.15 | CV       | — |
| 4  | (unnamed)                       | 128.518 | +18.905 | 19.23 | 172.00 | Polar    | — |
| 5  | CRTS J212654.5-012053           | 321.727 | -1.348  | TBD   | 213.03 | Polar    | — |
| 6  | CRTS J164017.8+080822           | 250.074 | +8.140  | 16.10 | 105.43 | U Gem    | — |
| 7  | SDSS J091935.66+502825.1        | 139.899 | +50.474 | 19.86 | 93.51  | DN       | TESS S21 (2020-Feb superoutburst found) |
| 8  | SDSS J110706.76+340526.8        | 166.778 | +34.091 | 19.48 | 95.84  | DN:      | — |
| 9  | SDSS J115419.06+575750.9        | 178.579 | +57.964 | 20.62 | 21.58  | ER UMa:  | — |
| 10 | CRTS J151836.0-054803           | 229.650 | -5.801  | 16.50 | 24.64  | DN       | TESS 24.9% eclipse at BLS P |
| 11 | SDSS J160419.02+161548.5        | 241.079 | +16.263 | 19.09 | 128.80 | SU UMa   | TESS 23% eclipse |
| 12 | SDSS J080142.37+210345.8        | 120.426 | +21.063 | 18.86 | 115.11 | Polar:   | — |
| 13 | **CRTS J051419.8+011120**       | 78.583  | +1.189  | 15.40 | 180.05 | DN       | **TESS 25% eclipse at 3.013 hr — confirmed discovery** |
| 14 | SDSS J115639.48+630907.7        | 179.164 | +63.152 | 20.72 | 29.13  | Polar    | — |

Plus 4 blind methodology rediscoveries (validation lower bound, not
claimed as new):

- CRTS J041133.6-090729 → 93.7 min ✓ RKcat 7.24 (93.6 min)
- CRTS J163120.8+103133 → 91.9 min ✓ RKcat (90.3 min)
- CRTS J233003.0+303300 → 224.6 min ✓ Hardy 2017 (224.6 exact)
- CRTS J005152.8+204017 → 295.7 min ✓ Dağ 2026 / Bruch 2026 (290.6, 2% off)

---

## How candidates flow through the cascade

1. The producer (`scripts/streaming/producer.py`) chunked-fetches Gaia DR3 NSS Orbital + AstroSpectroSB1 + Acceleration via ADQL.
2. The v2 consumer (`scripts/streaming/v2_corrected/run_v2.py`) applies the three corrections (NSS plx, K_obs/2, F#30 logg fallback) and writes `data/derived/main_hunt_derived_v2.parquet`.
3. The v3 acceleration consumer (`scripts/streaming/v3_acceleration/run_acceleration.py`) does the PM-acceleration → M_2_range mass-function inversion and writes `data/derived/acceleration_v3.parquet`.
4. Per-target verification (HGCA, Kervella H2G2, multi-archive RV, TESS, novelty cross-check) is done case-by-case against the catalog rows. Only after a single-source archival second-method check should a row move from a Tier-1 pool entry to a "strong candidate" or "confirmed discovery" line in this document.

Every published candidate claim requires the 7-step novelty protocol
(SIMBAD bibcodes + exoplanet.eu CSV grep + NEA + Google + arXiv +
CuPS-ETV + master PCEB list) before submission; see `docs/METHODOLOGY.md`.
