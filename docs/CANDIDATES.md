# Candidates

Authoritative list of objects currently in the discovery queue, with the
evidence that produced each verdict.

## Backing data (machine-readable)

| File | Pool | Rows |
|---|---|---:|
| `data/derived/main_hunt_derived_v2.parquet`         | v2 production: NSS Orbital + AstroSpectroSB1; G ≤ 13, plx ≥ 1.0 mas, 100 ≤ P ≤ 3000 d, significance ≥ 12 | 56,100 |
| `data/derived/main_hunt_derived_v2_relaxed.parquet` | Relaxed producer: G ≤ 15, plx ≥ 0.5 mas (mostly faint AstroSpectroSB1)                                  | 71,346 |
| `data/derived/main_hunt_derived_v2_alt.parquet`     | OrbitalAlternative + OrbitalAlternativeValidated channel                                                |    629 |
| `data/derived/acceleration_v3.parquet`              | NSS Acceleration channel (P-degenerate compact-object candidates)                                       | 16,949 |

Per-target columns include: `source_id`, `nss_solution_type`, `P_d`, `e`,
`significance`, `M2_msun_v2`, `sini_implied_v2`, `tier_v2`, `class_v2`,
all four filter verdicts + reasons.

## Headline

| Bucket | Count |
|---|---:|
| **Confirmed (independent 2-channel)** | **2** |
| Strong candidate (single-method, archival follow-up identified) | ~8 |
| Tier-1 NS pool (v2 + v2_relaxed)         | 291 |
| Tier-1 BH pool (v2 + v2_alt)             | 3 — 2 demoted by 2nd method, 1 dossier STRONG |
| Tier-2 (RV-inconclusive)                  | 87 (v2) + 829 (v2_relaxed) + 42 (v2_alt) |
| v3 Acceleration P-degenerate compact-object | 10,818 |
| Demoted / falsified after 2nd method      | ~30 named |

## Confirmed (independent 2-channel)

### CRTS J051419+0111

| Field | Value |
|---|---|
| Class | CV — SU UMa subclass DN, in the orbital-period gap |
| RA, Dec | 78.583, +1.189 |
| G | 15.40 |
| First channel | ZTF DR23: P = 180.770 ± 0.001 min = 3.013 hr (BLS power 43,842) |
| Second channel | TESS S98 eclipse at the ZTF period — **median quiescent depth = 71%, individual eclipses > 98% flux removed**. Near-total eclipse at i ≈ 84°. Headline "25%" was the phase-bin-averaged dilution; per-eclipse measurement is much deeper. |
| Superoutburst | ZTF caught a 7-day g = 14.41 superoutburst (2023-09-15 → 22) confirming SU UMa subclass |
| Component masses (Knigge 2011 donor sequence at P = 3.013 hr) | M_WD ≈ 0.70–0.90 M_⊙, M_donor ≈ 0.20–0.30 M_⊙, q ≈ 0.31, i ≈ 84° |
| Novelty | 14 CV catalogs queried (RKcat 7.24, Hardy 2017, Pala 2019/2020, Bruch 2024, Inight 2019/2021/2023a/2023b/2024, CuPS-ETV) — no prior orbital period for this source. SIMBAD has 2 ingest bibcodes (Drake+ 2014, Coppejans+ 2016 DN class) — neither measured P_orb. |
| QSO false-positive | Gaia DR3 `in_qso_candidates = True` + DSC quasar prob = 0.994 — known DSC failure mode for blue + variable CVs (Pala 2020, Inight 2023). CV identification overrides. |
| Dossier | `docs/dossiers/CRTS_J051419+0111_DOSSIER_2026_05_28.md` |

### Gaia DR3 3155543945892767232

| Field | Value |
|---|---|
| Class | NS candidate (62% NS, 20% mass-gap BH, 38% WD on the posterior) |
| Primary | K1III RGB giant, Teff = 5100 K, log g = 3.4, M_1 = 1.4 ± 0.3 M_⊙, d ≈ 1050 pc |
| NSS solution_type | AstroSpectroSB1 — significance 40.7, n_obs = 206 |
| Orbit | P = 543.27 ± 4.56 d, e = 0.089 ± 0.045, K_1 ≈ 15.5 km/s |
| First channel | NSS AstroSpectroSB1 astrometric + spectroscopic joint fit |
| Second channel | LAMOST LRS 2 epochs: MJD 56352 (RV 31.78 km/s), MJD 57325 (RV 45.45 km/s). Predicted ΔRV at the NSS-phase pair (0.874 → 0.665) matches observed at **χ² = 0.36**, residuals 0.22σ + 0.32σ. ΔTeff = 13 K, Δlogg = 0.022 between epochs → no SB2 contamination. |
| M_2 posterior at M_1 = 1.4 | 1.08 / 1.57 / 2.34 M_⊙ (16/50/84%) |
| Dossier | `docs/dossiers/3155543945892767232_DOSSIER_2026_05_28.md` |

## Strong candidates (single-method)

### Gaia DR3 5406907085973524224 — BH candidate

| Field | Value |
|---|---|
| NSS solution_type | OrbitalAlternative (high parameter correlation, not luminous-binary inconsistency) |
| Orbit | P = 25 d, e = 0.28, K_1 sin i predicted ≈ 100 km/s (87-130 km/s 16-84%) |
| Primary | M_1 = 0.85 ± 0.15 M_⊙ (StarHorse + GSP-Phot + TIC convergent), G = 14.53 |
| M_2 posterior at M_1 = 0.85 | 3.1 / 4.5 / 6.6 M_⊙ (16/50/84%) |
| P(M_2 > 1.4) | 99.7% (WD ruled out) |
| P(M_2 > 2.2) | 96.7% (NS upper limit exceeded) |
| P(M_2 > 3.0) | 85.5% (stellar-mass BH) |
| RV-variability corroboration | Gaia `rv_chisq_pvalue = 0` across 27 transits |
| Follow-up | HARPS half-night (3 epochs × 30 min) — predicted K_1 ≈ 100 km/s vs HARPS σ_RV = 5 m/s |
| Prior identification | ResearchGate preprint #403022650 (unreviewed; their a_phot uses √(s/2) not Pourbaix-Halbwachs, giving M_2_min ≈ 1.95 M_⊙) |
| Dossier | `docs/dossiers/5406907085973524224_DOSSIER_2026_05_28.md` |

### Gaia DR3 5858574810404752256 — mass-gap-BH / NS candidate

| Field | Value |
|---|---|
| Primary | G0 IV subgiant, M_1 = 1.5 ± 0.3 M_⊙, R_1 ≈ 3.9 R_⊙, d ≈ 1.69 kpc, G = 11.97 |
| Orbit | P = 506.135 ± 2.8 d, e = 0.542, significance 20σ, a_phot = 0.527 mas |
| f(M) | 0.367 M_⊙ |
| AMRF (Shahaf+ 2019) | 0.63 — dark companion confirmed |
| RV evidence | rv_amplitude_robust = 23.9 km/s peak-to-peak, p_χ² = 1.6×10⁻¹⁴ over 22 RVS transits |
| M_2 interpretation | rv_amplitude as 2K_1 (v2 convention): K_1 ≈ 12 km/s, sin i ≈ 0.53 → **M_2 ≈ 2.82 M_⊙ (mass-gap BH)**; as half-amplitude: K_1 = 24 km/s, sin i = 1.0 → M_2 = 1.48 (NS / heavy WD) |
| Novelty | Truly novel — not in SIMBAD, not in Shahaf+ 2023 / 2024 |
| Follow-up | 3-5 RV epochs (~5 h CHIRON/FEROS) at periastron |
| Dossier | `docs/dossiers/5858574810404752256_DOSSIER_2026_05_28.md` |

### HD 157033 — HGCA Pile A survivor (first archival K_1 detection)

| Field | Value |
|---|---|
| Gaia DR3 source_id | 4111149395881722496 (= HIP 84960 = TYC 6825-498-1) |
| Primary | A9/F0V, G = 9.95, d = 293 pc, M_1 = 1.60 ± 0.20 M_⊙ (consensus of FLAME 1.67 / StarHorse 1.59 / TIC 1.42 / GALAH 1.43 / Kervella 1.82) |
| Channel 1 — HGCA Brandt 2021 | **χ² = 1583** (one of the highest in the catalog — far above the 30 corroborated threshold) |
| Channel 2 — Kervella H2G2 2022 | snrPMa = 14.85, dVt = 3.15 km/s; Kervella M_2_5AU = 0.45 M_⊙ at face value (the often-quoted "4 M_⊙" only comes from accounting for orbit-averaged PMa dilution at P ≈ 10 yr — see dossier §6) |
| Channel 3 — Gaia DR3 RV variability | `rv_amplitude_robust = 16.305 km/s` over 17 transits; `rv_chisq_pvalue = 1.78×10⁻¹⁵` (> 9σ rejection of single-velocity); `rv_renormalised_gof = 7.22` (≫ 4 = binary) |
| Channel 4 — Multi-archive direct RV (task HH) | **4 archival epochs across 4.3 yr**: GALAH DR3 MJD 57479 = −39.94 km/s; APOGEE DR17 MJD 58567 = +26.54, MJD 58570 = −2.41, MJD 59057 = −44.52 km/s. **ΔRV peak-to-peak = 71 km/s → model-free K_1 ≥ 35.5 km/s, central ≈ 47 km/s — 2-3× larger than the Gaia rv_amplitude_robust.** Strengthens the BH classification. |
| NSS solution | None — P ≈ 10 yr exceeds the Gaia mission 1000-d cutoff (no Keplerian fit possible from the 4 epochs without ephemeris) |
| M_2 (at M_1 = 1.60, P = 10 yr, K_1 = 16.3) | sin i = 1: 3.62 M_⊙; ⟨sin i⟩ = 0.785: 5.65 M_⊙ |
| M_2 (at M_1 = 1.60, P ∈ [3, 10] yr, K_1 ≈ 47 km/s from HH) | **6–17 M_⊙ → solid stellar-mass BH** (or potential hierarchical triple if scatter is from a third body) |
| P(M_2 > 3.0) | ~75% from Gaia channel alone; substantially higher when HH archival K_1 included |
| Novelty | **Zero SIMBAD bibcodes** — no peer-reviewed paper has ever discussed HD 157033. Absent from Halbwachs+ 2023, Shahaf+ 2023, Müller-Horn+ 2026 (excluded by RUWE = 0.85 < 1.4, M_1 = 1.6 > MS cutoff 1.51, rv_amp = 16.3 < 20 threshold). First 2-channel-corroborated identification. |
| Follow-up | ~1 hr on FEROS or 4 epochs of new RV to derive 5-epoch Keplerian; would promote to CONFIRMED |
| Dossier | `docs/dossiers/HD157033_DOSSIER_2026_05_28.md` |
| Status of sibling Pile-A candidates | 7/8 demoted to stellar binaries via Kervella H2G2 (M_2 = 0.4–2.9 M_⊙ at 5 AU): CD-46 10032A, HD 173689, HD 16385, HD 81825, HD 37943, HD 5514, LP 155-298. Detailed demotion dossiers for CD-46 10032A and HD 173689 at `docs/dossiers/CD-46_10032A_DOSSIER_2026_05_28.md` and `docs/dossiers/HD_173689_DOSSIER_2026_05_28.md`. |

### WD-primary + Chandrasekhar-mass companion (Pile E)

Hand-curated (WDJ060042, WDJ020915): **CONFIRMED_WD_BINARY_CHANDRASEKHAR (provisional)**. SED two-component fits exclude M-dwarf companions at >10σ via W1/W2; exclude hot WD companions (T_2 ≥ 11 000 / 20 000 K respectively) at >3σ via GALEX NUV / Pan-STARRS optical. Surviving companion classes: cool double-degenerate (T_2 ≤ 9 000 K cool WD) or dormant low-mass NS.

Pipeline-derived (WG 26, WDJ205650 — from task GG GF21 cross-match of the v2 + v2_relaxed + v2_alt "WD or low-mass star" bin):

| Source | M_1 (WD) | M_2 | M_total | P | G | Pool | Notes | Dossier |
|---|---:|---:|---:|---:|---:|---|---|---|
| **WDJ060042.75-293041.36** (Gaia DR3 2909342818326298112) | 0.612 | 1.368 | 1.98 | 935 d | 18.4 | hand-curated | d = 98 pc. NOT in SIMBAD. M_total >> Chandrasekhar → **Type Ia progenitor candidate** if WD+WD. No archival RV; X-shooter follow-up. | `docs/dossiers/WDJ060042-293041_DOSSIER_2026_05_28.md` |
| **WDJ020915.51+380425.92** (Gaia DR3 332248057157474176)  | 0.718 | 1.323 | 2.04 | 274 d | 16.2 | hand-curated | d = 84 pc. NOT in SIMBAD. M_total >> Chandrasekhar → Type Ia progenitor candidate. Highest-tractability: 5 HARPS-N epochs yield >50σ K_1. | `docs/dossiers/WDJ020915+380425_DOSSIER_2026_05_28.md` |
| **WG 26** = WDJ141039.06-474439.48 (Gaia DR3 6092654861665006592) | 0.53 | 1.03 | **1.56** | 176 d | (TBD) | v2_relaxed | **NEW from GG**. SIMBAD-known DA2.2 WD with no prior binary characterization. M_total = 1.56 M_⊙ → **Type Ia progenitor candidate**. RUWE = 5.0 (marginal). |  |
| **WDJ205650.56+062149.68** (Gaia DR3 1736555475066523008) | 0.39 (low-mass He WD) | 0.56 | 0.95 | 81 d | (TBD) | v2_alt | NEW from GG. SIMBAD GALEX J205650.5+062149, DA WD. Below Chandrasekhar. RUWE = 2.16. |  |

Plus 4 additional candidates from the v3 Acceleration channel (separate pipeline), notably **WDJ173708.52+242024.77** with M_WD = 1.22 M_⊙ — massive ONe WD with significant acceleration.

**Methodological note from GG**: cross-matching the 83 k v2 "WD or low-mass star" rows against Gentile Fusillo 2021 yields only **2 GF21-confirmed WD primaries**. The bin is dominated by M-dwarf primaries, not WD primaries — GF21's Gaia HRD position cut systematically excludes WD+M-dwarf systems where the M-dwarf dominates the visible flux. Pile E expansion is limited; the 50× expansion hoped for via systematic GF21 cross-match is not achievable from this catalog alone.

### M-dwarf super-Jupiter candidates (Pile B)

| Source | SpT | d (pc) | M_2 (M_J) face-on | P (d) | G | TESS sectors | Dossier |
|---|---|---:|---:|---:|---:|---:|---|
| **APMPM J0710-5704** (Gaia DR3 5486916932205092352) | M4V    | 17.07 | 9.5 ± 1.5 | 253.48 | 12.2 | 37 | `docs/dossiers/APMPM_J0710-5704_DOSSIER_2026_05_28.md` |
| **SCR J1441-7338**   (Gaia DR3 5796338299045711232) | M5.5-M6V | 25.55 | 11-12 | 488.05 | 14.8 |  9 | `docs/dossiers/SCR_J1441-7338_DOSSIER_2026_05_28.md`. eROSITA-DE DR1 counterpart at 3.45″, L_X ≈ 1.4×10²⁸ erg/s — consistent with M-dwarf coronal emission, not a compact-companion signature; doesn't affect the SJ companion claim. |
| **UCAC4 313-025977** (Gaia DR3 5612039087715504640) | M4-M5V | 32.39 | 13 | 592.32 | (TBD) |  4 | `docs/dossiers/UCAC4_313-025977_DOSSIER_2026_05_28.md` |

APMPM J0710 archival positive constraint: 37 TESS sectors stitched, **no
phase modulation at P or P/2 below 200 ppm** → companion is dark/substellar
across all inclinations.

## Weak archival corroboration (1 candidate — task BB2)

| Source | NSS class | Sig | P (d) | e | Archival evidence |
|---|---|---:|---:|---:|---|
| **Gaia DR3 1593152388271709824** | Orbital | 104.5 | 597.4 | 0.404 | 3 multi-archive RV epochs (1 APOGEE DR17 + 2 LAMOST DR11) fit a Keplerian at the NSS-locked phases at χ²/dof = 0.00, K_fit = 4.09 km/s. Only 2 distinct phase bins so K–ω degeneracy not yet broken. **One additional RV epoch at near-periastron upgrades to CONFIRMED.** |

## Tier-1 BH pool — verdicts

| Source | M_2 (cascade) | Verdict |
|---|---:|---|
| Gaia DR3 5406907085973524224 (v2_alt) | 4.79 | **STRONG_CANDIDATE** — see above |
| Gaia DR3 3263804373319076480 (GALEX J033455+000910, v2) | 3.22 | DEMOTED — Simon, Lam, El-Badry, Reggiani 2026 (arXiv:2603.20371) published as WD with M_2 ≤ 0.9 via 7 MIKE + 4 FEROS + APOGEE + LAMOST RV epochs |
| Gaia DR3 6281177228434199296 (GALEX J145250-192225, v2) | 12.75 | DISPUTED — Shahaf+ 2023 (Triage I) M_2 = 11.9; TESS ellipsoidal 0.138% (4.6× too high for face-on); RAVE-Gaia RV drift inconsistent |

## X-ray non-detection note (task Q2)

5-catalog cone search (eROSITA-DE DR1, CSC2.1, 4XMM-DR13, 2RXS, 2SXPS at 10″) on the 4 strong dormant compact-object candidates — 5406907, 5858574, HD 157033, 3155543 — returns **zero counterparts**. Expected: at d = 296 pc – 1.33 kpc, quiescent NS/BH XRB flux would be F_X ~ 10⁻¹⁵ – 10⁻¹⁶ erg/s/cm², below all-sky-survey sensitivity. The null rules out *persistent* L_X > 10³¹ erg/s for 3155543 (only candidate inside the eROSITA-DE footprint); HD 157033, 5406907, 5858574 are in the Russian eROSITA half and not yet probed by any public all-sky X-ray catalog at the required depth. Targeted Chandra/XMM at quiescent-XRB sensitivity is the next confirmation channel.

## Demoted / falsified

| Object | Why demoted |
|---|---|
| HD 207141                                | v2 NSS plx correction: M_2 = 7.57 → 1.31 M_⊙ |
| HD 1957                                  | F#30 K-giant chromatic FP (logg_gspspec_ann = 2.63) |
| TYC 1363-2339-1                          | NSS plx correction: M_2 = 3.88 → 1.12 M_⊙ |
| TYC 1299-727-1                           | NSS plx correction: M_2 = 3.50 → 1.18 M_⊙ |
| TYC 2773-348-1                           | NSS plx correction: M_2 = 3.21 → 1.03 M_⊙ |
| TYC 8785-1657-1                          | NSS plx correction: M_2 = 3.63 → 1.06 M_⊙ |
| TYC 4791-2322-1                          | NSS plx correction: M_2 = 2.66 → 1.34; F#32 sin_i_implied = 1.51 fails joint check |
| Pile-A HGCA "BH-class" (7 of 8)          | Kervella H2G2 M_2 = 0.4-2.9 M_⊙ at 5-AU reference → stellar binaries |
| BD+05 5218                                | = HIP 117179 b; Stevenson 2023 (MNRAS 526, 5155 = arXiv:2310.02695) published as 44 M_J BD |
| HD 37419                                  | Known visual triple ADS 4267; HGCA signal is the inner pair |
| HD 12871                                  | Hierarchical triple — APOGEE 3-visit K_1 = 11.9 matches Gaia SB1 K_1; outer companion drives Acceleration |
| Gaia DR3 5476986108823894400              | Multi-survey "K_1=163 km/s" retracted: APOGEE σ = 6.96 (real) vs RAVE σ = 115 km/s (RAVE pipeline noise floor) |
| Gaia DR3 6802634430521968000              | Gaia MSC pipeline converged on luminous G2V+K3V binary at d = 553 pc (logposterior_msc = 589); 17σ NSS-plx vs gaia_source-plx tension; e = 0.871 in known FP class |
| Gaia DR3 411532290151732992               | Already in Shahaf+ 2023 Triage I (M_2_min = 1.75) |
| Gaia DR3 2899685738980957568              | Already in Shahaf+ 2023 Triage I (M_2_min = 1.58) |
| Gaia DR3 504135672000072064               | Already in Shahaf+ 2023 Triage I (M_2_min = 1.30) |
| Gaia DR3 1985832181476519936 (HD 216783)  | Gaia MSC luminous-binary fit (`logposterior_msc > 50`) AND DSC `binary_prob > 0.5` — near-certain stellar-binary contaminant |

## Pile F — CV-period orbital periods (full table)

14 truly novel + 4 blind methodology rediscoveries. All 14 confirmed by ZTF DR23 period detection. 1 confirmed via independent TESS eclipse; 2 with additional TESS signatures.

| # | Name | RA | Dec | G | P (min) | Subtype | TESS confirmation |
|---:|---|---:|---:|---:|---:|---|---|
|  1 | MGAB-V701                       | 204.066 | +38.159 | 19.39 | 29.41  | DN       | — |
|  2 | SDSS J154953.41+173939.0        | 237.473 | +17.661 | 19.44 | 116.68 | NL:      | — |
|  3 | PQ J225417.5+074227             | 343.573 |  +7.708 | 18.78 | 232.15 | CV       | — |
|  4 | (unnamed) J0834+1854            | 128.518 | +18.905 | 19.23 | 172.00 | Polar    | — |
|  5 | CRTS J212654.5-012053           | 321.727 |  -1.348 |   —   | 213.03 | Polar    | — |
|  6 | CRTS J164017.8+080822           | 250.074 |  +8.140 | 16.10 | 105.43 | U Gem    | — |
|  7 | SDSS J091935.66+502825.1        | 139.899 | +50.474 | 19.86 |  93.51 | DN       | S21 superoutburst recovered |
|  8 | SDSS J110706.76+340526.8        | 166.778 | +34.091 | 19.48 |  95.84 | DN:      | — |
|  9 | SDSS J115419.06+575750.9        | 178.579 | +57.964 | 20.62 |  21.58 | ER UMa:  | — |
| 10 | CRTS J151836.0-054803           | 229.650 |  -5.801 | 16.50 |  24.64 | DN       | 16.6% per-eclipse depth at ZTF P (3.8σ MARGINAL); BLS best at 172 min ≈ 7× ZTF P → ZTF 24.64-min period may be a 1/7 sub-harmonic alias |
| 11 | SDSS J160419.02+161548.5        | 241.079 | +16.263 | 19.09 | 128.80 | SU UMa   | 23% eclipse |
| 12 | SDSS J080142.37+210345.8        | 120.426 | +21.063 | 18.86 | 115.11 | Polar:   | — |
| 13 | **CRTS J051419.8+011120**       |  78.583 |  +1.189 | 15.40 | 180.05 | DN       | **25% eclipse at 3.013 hr — confirmed (Pile F headline)** |
| 14 | SDSS J115639.48+630907.7        | 179.164 | +63.152 | 20.72 |  29.13 | Polar    | — |

Blind methodology rediscoveries: CRTS J041133.6-090729 → 93.7 min (RKcat 93.6), CRTS J163120.8+103133 → 91.9 min (RKcat 90.3), CRTS J233003.0+303300 → 224.6 min (Hardy 2017 224.6), CRTS J005152.8+204017 → 295.7 min (Dağ 2026 / Bruch 2026 290.6).

## Method

Three corrections vs the v1 cascade:

1. **NSS parallax** preferred over `gaia_source.parallax` (the latter is orbital-motion-biased low for binaries by 1.2–2.5×).
2. **K_obs = rv_amplitude_robust / 2** — Gaia DR3 publishes peak-to-trough, not the semi-amplitude K_1. Verified against Gaia BH2: published K_1 = 21.2 km/s vs rv_amplitude_robust = 36.96 (ratio 1.74 ≈ 2 × (1 - 0.13·e) for e = 0.52).
3. **Filter #30 logg fallback** chain: `logg_gspphot → logg_gspspec_ann → logg_gspspec`. Catches K-giant chromatic-bias false positives that GSP-Phot NaN missed.

Full details + per-source verification in `docs/METHODOLOGY.md`.

Cascade validation: 93% class-level recall on 27 confirmed compact + sub-stellar systems, 14% adversarial-FP rate, 4.5% median |ΔM_2|/M_2 on the Shahaf+ 2024 NS sample.

## Reproducibility

Required external catalogs listed in `CATALOG_DEPENDENCIES.md`.

```bash
# Setup
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

# Production v2 (NSS Orbital + AstroSpectroSB1, G ≤ 13, plx ≥ 1.0)
python scripts/streaming/producer.py
python scripts/streaming/v2_corrected/run_v2.py
# → data/derived/main_hunt_derived_v2.parquet

# Relaxed-producer expansion (G ≤ 15, plx ≥ 0.5)
python scripts/streaming/v2_corrected/producer_relaxed.py
python scripts/streaming/v2_corrected/run_v2_relaxed.py
# → data/derived/main_hunt_derived_v2_relaxed.parquet

# OrbitalAlternative + Validated channel
python scripts/streaming/v2_corrected/run_orbital_alt.py
# → data/derived/main_hunt_derived_v2_alt.parquet

# v3 NSS Acceleration channel
python scripts/streaming/v3_acceleration/run_acceleration.py
# → data/derived/acceleration_v3.parquet

# Interactive single-source web tool
streamlit run scripts/web_tool/app.py
```

Tests: `pytest tests/` (cascade end-to-end + filter unit tests + regression assertions on Gaia BH1, Gaia BH2, HD 1957, HD 81040, HD 111232).
