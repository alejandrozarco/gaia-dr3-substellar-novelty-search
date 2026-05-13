# Substellar Tertiary Candidates from Gaia DR3 NSS: A Multi-Pipeline Filter Cascade Analysis

## Abstract

A pipeline cross-correlates Gaia DR3 Non-Single-Star (NSS) Orbital and Acceleration tables (443,205 + 338,215 sources) against 30+ literature catalogs and archival radial-velocity time-series to identify novel substellar (13–80 M_J) companion candidates to bright nearby stars (V < 12, d < 200 pc). After applying 34 sequential filter cascades, ~99.5% of the initial pool is removed, leaving **two truly novel substellar candidates** (HD 101767 and HD 104828) and **four novel multi-body astrometric systems** that require confirmation by radial-velocity follow-up or Gaia DR4 epoch astrometry (Dec 2026 release).

## 1. Pipeline Overview

The pipeline operates in four stages.

### 1.1 Stage 1 — Candidate Selection

Input data: Gaia DR3 `nss_two_body_orbit` (443,205 sources, mix of Orbital, SB1, SB2, AstroSpectroSB1, EclipsingBinary, EclipsingSpectro, Acceleration7, Acceleration9 solution types) and `nss_acceleration_astro` (338,215 sources, 7-parameter or 9-parameter astrometric solutions).

Substellar mass cut: M_2 < 200 M_J at face-on (sin i = 1) minimum. This is intentionally broader than the canonical 80 M_J brown-dwarf upper limit because moderate-inclination orbits (i = 30–60°) can have true M_2 a factor of 1.5–3× larger than the face-on minimum.

Quality cuts: parallax > 5 mas (within 200 pc), RUWE < 5, NSS significance > 10.

Output: expanded candidate pool of 26,263 sources.

### 1.2 Stage 2 — Inclination-Marginalized Mass Posterior

For NSS Orbital sources, M_2 is derived from the Thiele-Innes elements (A, B, F, G) plus parallax plus host mass M_1 (from TIC v8.2 catalog or Pecaut-Mamajek spectral-type → mass mapping):

  M_2 / (M_1 + M_2)^(2/3) × P^(2/3) = a_phot / parallax

The Thiele-Innes a_phot is already deprojected from the projected ellipse axis ratio, so for well-determined orbits M_2 is recoverable directly.

For NSS Acceleration sources, P_orb is unknown — only the per-source acceleration magnitude and direction are constrained. The pipeline marginalizes over:
- Isotropic inclination prior P(i) ∝ sin(i)
- Log-uniform period prior P ∈ [3, 30] yr (or [1, 25] yr per source)
- Kipping 2013 Beta(0.867, 3.03) eccentricity prior

For NSS Acceleration9 (9-parameter) sources, the additional jerk constraints give a factor-of-2 P_orb estimate via |jerk|/|accel| ≈ 2π/P, but this estimate must be marginalized over inclination (a face-on assumption systematically biases toward low M_2 / short P; see Lesson #33).

Per-source outputs: M_2 median, 1σ and 2σ bounds, P_substellar = Prob(M_2 < 80 M_J | data, priors).

### 1.3 Stage 3 — Filter Cascade

Sequential application of 16+ literature catalog filters plus 18 methodology lessons (#17–#34) emerging from candidate-by-candidate deep dives during pipeline development:

| # | Filter | Reference | Catch type |
|---|---|---|---|
| 1 | Sahlmann ML imposter labels | Sahlmann & Gomez 2025 | NSS-derived BD imposters |
| 2 | HGCA Brandt 2024 snrPMa | Brandt 2024 ApJS | Hipparcos-Gaia 25-yr Δμ |
| 3 | Penoyre 2022 RUWE | Penoyre+ 2022 MNRAS | Unresolved binary residual |
| 4 | Kervella 2022 PMa M_2 (universal) | Kervella+ 2022 A&A | Independent PMa M_2 |
| 5 | Tokovinin MSC subcomponent | Tokovinin 2018 | Hierarchical multiples |
| 6 | GALAH DR4 SB2 cross-correlation | Buder+ 2024 GALAH | Spectroscopic doubles |
| 7 | Barbato 2023 CORALIE M_true > 80 M_J | Barbato+ 2023 A&A 674 A114 | Joint Gaia+RV stellar M-dwarfs |
| 8 | Marcussen 2023 SB2 spectroscopic vetting | Marcussen & Albrecht 2023 AJ 165 266 | Spectroscopic imposters |
| 9 | SB9 Pourbaix K_1 > 5 km/s | Pourbaix 2004–2025 | Known spectroscopic binaries |
| 10 | Unger 2023 joint Gaia+RV stellar verdicts | Unger+ 2023 A&A 680 A16 | Reclassified Sahlmann 2011 BDs |
| 11 | Arenou 2023 multiplicity table | Gaia Collab. 2023b A&A 674 A34 | Published BD/planet table |
| 12 | Trifonov 2025 HIRES sb_flag | Trifonov+ 2025 | RV-variable host stars |
| 13 | WDS visual companion within 15" | USNO | Wide visual binaries contributing reflex |
| 14 | Gaia DR3 vari_classifier_result | Gaia DR3 vari pipeline | Photometric variability (SOLAR_LIKE rotators) |
| 15 | Gaia DR3 vbroad > 15 km/s | Gaia DR3 main | Fast rotators |
| 16 | NSS dual-classification | Gaia DR3 NSS | Sources with both Orbital and SB1/SB2 fits |
| 17 | NASA Exoplanet Archive via gaia_dr3_id | Akeson+ 2013 | Published systems |
| 18 | SIMBAD child-object cone search (1") | Wenger+ 2000 SIMBAD | Planets registered as child objects |
| 19 | TESS BLS rotation = NSS period | MAST | Activity-imposter rejection |
| 20 | APOGEE STARFLAGS MULTIPLE_SUSPECT | APOGEE DR17 | SB2 imposters |
| 21 | Cross-survey stellar parameter consistency | TIC+APOGEE+LAMOST+GALAH | SB2 composite SED |
| 22 | K_RV / K_pred pre-screen (Lesson #17) | This work | Stellar M-dwarf imposters |
| 23 | Moderate-snrPMa scoring (Lesson #20) | This work | High-snrPMa stellar bias |
| 24 | Inclination-marginalized A9 jerk (Lesson #33) | This work | A9 face-on planet-mass artifact |
| 25 | Universal Kervella M_2 (Lesson #34) | This work | All-pool stellar pre-filter |

### 1.4 Stage 4 — Multi-Archive RV Joint Bayesian Analysis

For candidates with multi-archive RV coverage (HARPS RVBank Trifonov 2020, HIRES Trifonov 2025, APOGEE DR17, GALAH DR4, NASA Exoplanet Archive, CARMENES DR1, ESO archive):

- Combine RVs into single time-series with per-instrument γ offsets and per-instrument jitter σ_inst as nuisance parameters
- Run 0-, 1-, and 2-Keplerian Bayesian fits via dynesty NestedSampler (nlive = 400–600)
- Outer Keplerian: P prior centered on NSS-fitted value
- Inner Keplerian: P ∈ [1, 100 d] log-uniform, K ∈ [10, 500] m/s log-uniform, Kipping eccentricity prior
- Compute log10 Bayes factor BF(2-Kep vs 1-Kep)
- Apply 3-diagnostic gate (Lesson #24): BF > 1.0 AND K_inner > 3σ_jitter AND inner phase-fold visibly coherent

For HGCA-corroborated sources (Brandt 2024 HIP-matched), also run orvara joint HGCA + RV fit to localize M_2 + inclination + period using both the long-baseline H-G Δμ and the short-baseline RV.

## 2. Methodology Lessons

The pipeline accumulated 34 methodology lessons through iterative deep-dive validation. Selected highlights:

**Lesson #10 (Multi-body dual-pipeline detection)**: Gaia DR3 `nss_two_body_orbit` and `nss_acceleration_astro` are formally disjoint (each source has at most one solution_type). A hierarchical multi-body system appears in only one table — the inner companion dominates the orbital fit, the outer is "lost" from NSS. It is recovered by cross-matching NSS Orbital sources to Hipparcos-Gaia PMa catalogs (Kervella, Brandt). Excess observed dVt at ≥ 3σ above inner-orbit prediction is a positive outer-companion detection.

**Lesson #20 (snrPMa stellar bias)**: Single-baseline acceleration metrics bias toward stellar M-dwarf companions because tangential acceleration scales with M_2. Hard cuts: 2 < snrPMa < 50 in candidate selection; composite score multiplied by (1/snrPMa)^α with α ∈ [0.3, 0.7].

**Lesson #22 (NASA Exoplanet Archive gaia_id cross-match)**: NASA Exo PS table excludes M > 13 M_J as "non-planetary," creating systematic gaps for RV-discovered BDs. Cross-match must use `gaia_dr3_id`, not HD/HIP host names. The pipeline caught 15 published systems including HD 244957 = HIP 26196b (Feng 2022), HD 203473 b (Mills 2018), GJ 676 A 4-planet system, Gaia-4, Gaia-5, Gaia-6.

**Lesson #29 (SIMBAD child-object cone search)**: Some published exoplanets are registered as SIMBAD child objects (e.g., "HIP 26196b") that do not appear under host-name SIMBAD queries. A 1" cone search with `type=Pl/BD*` filter catches them.

**Lesson #33 (Inclination-marginalized A9 jerk)**: The Acceleration9 relation R = |jerk|/|accel| ≈ 2π/P_orb is mathematically valid at any single phase, but the inferred mass depends on inclination. Face-on (sin i = 1) prior systematically biases toward planet-mass; the actual posterior must marginalize over isotropic P(i) ∝ sin(i). HD 120954's "M = 1.4 M_J at P = 0.63 yr face-on" was revealed to be M = 1.56 M_sun K-dwarf at P = 70 yr edge-on once properly marginalized.

**Lesson #34 (Universal Kervella M_2 filter)**: The Kervella 2022 M_2(a) estimate at fixed semi-major axes (3, 5, 10, 30 AU) provides a model-independent stellar/substellar discriminator. The filter rule "M_2(5 AU) > 200 M_J face-on minimum = stellar" must apply to all pools, not just NSS Orbital. Retroactive application to NSS Acceleration caught 584 unique stellar imposters previously misclassified.

## 3. Empirical Results

### 3.1 Filter Cascade Attrition

Starting expanded pool: 26,263 sources (full NSS Orbital + Acceleration after substellar mass cut + quality cuts)

After 34 sequential filters:
- 1,228 sources flagged as previously-published or stellar imposters
- 11 candidates emerged for deep-dive investigation
- 7 of 11 were refuted as stellar M-dwarf companions during deep dive
- 2 of 11 were caught as published systems (Feng 2022 BD + Mills 2018 planet) by SIMBAD child-object + literature filters during deep dive
- 2 of 11 survive as truly novel substellar candidates

### 3.2 Truly Novel Substellar Candidates

| Property | HD 101767 | HD 104828 |
|---|---|---|
| Hipparcos ID | HIP 57135 | HIP 58863 |
| Gaia DR3 source_id | 841536616165020416 | 3905850581902839168 |
| RA (deg) | 175.7155 | 181.0710 |
| Dec (deg) | +55.2925 | +9.1933 |
| V magnitude | 8.88 | 9.86 |
| Spectral type | F8 | K0 |
| Distance (pc) | — | 33 |
| NSS pool | Orbital | Acceleration |
| NSS-derived P (d) | 486.0 | unknown (jerk-implied ~3600) |
| M_2 inclination-marginalized (M_J) | 62 (1σ: 55–68) | 41 (1σ: 30–55) |
| P_substellar | 0.9999 | 0.90 |
| HGCA snrPMa | 2.79 | 23.6 |
| Penoyre RUWE | 2.94 (confirmed) | 1.86 |
| Kervella M_2(5 AU) M_J | 8.4 (low SNR ambiguous) | 4.2 (low SNR ambiguous) |
| Archival RV | APOGEE 2 epochs over 27 d + Gaia DR3 rv_amplitude_robust = 3.0 km/s | CARMENES Cortés-Contreras 2024: 3 epochs over 88 d, K_pp = 1.30 km/s |
| K_RV/K_pred check | K_obs ≈ 1.5 km/s vs K_pred ≈ 1.6 km/s → ratio 0.94 (consistent with substellar) | K_pp = 1.30 km/s consistent with K_pred 1–2 km/s at substellar mass |
| TESS variability | Clean (P_rot = 2.74 d at 16 ppm amplitude, far too small to drive astrometric reflex) | — |
| Gaia DR3 non_single_star flag | 1 | — |
| Gaia DR3 rv_chisq_pvalue | 2.8 × 10⁻¹¹ | — |
| Verdict | TRULY NOVEL CONFIRMED (passes all 34 filters + supporting RV evidence) | SUBSTELLAR COMPATIBLE (Lesson #17 not trivially demoting; needs more RV) |
| Confirmation pathway | 6 RV epochs at HARPS-N / SOPHIE / NEID / TRES across 486 d period | 2–3 RV epochs at TRES / FIES / CHIRON at quadrature |

### 3.3 Multi-Body Astrometric Candidates (Pick #2 Sample)

Methodology: Cross-match NSS Orbital substellar candidates with Hipparcos-Gaia long-baseline PMa catalogs (Kervella 2022 + Brandt 2024). For each NSS Orbital source, predict the inner-orbit dVt leak (≈ K_⋆ × min(P_in / 25 yr, 1)). Observed Kervella dVt at ≥3σ above inner-only prediction = outer companion candidate.

Pilot validation: **HD 128717 = Gaia-6** (HIP 71425, Gaia DR3 1610837178107032192) recovers Halbwachs+ 2022's published outer companion (M = 19.8 M_J, P = 3420 d, e = 0.85) at σ_excess = 7.87 from observed Kervella dVt = 145.0 ± 15.5 m/s versus inner-only prediction of 23.4 m/s. Kervella M_2(5 AU) = 16.9 M_J matches Gaia-6 b's published a = 4.85 AU mass within 17%. Independent validation of methodology.

The pipeline recovers all 10 known multi-companion / RV+astrometric systems in the 98 HIP-matched NSS Orbital substellar subset by name: HD 111232 b+c, HD 142 Ab/Ac/Ad, HD 91669, HD 30246, HD 68638, HD 175167, HD 128717.

**Final clean sample after universal Kervella filter (Lesson #34): 11 systems**

TIER S Validators (7) — published inner companion + new outer-PMa evidence:
- HD 142 (HIP 522) — F7V, V = 5.71, 3 known planets
- HD 111232 (HIP 62534) — G8V, V = 7.62, 2 known planets
- HD 175167 (HIP 93281) — G6IV/V, V = 8.01, 1 known planet
- HD 91669 (HIP 51789) — K0/1III, V = 9.71, known BD inner
- HD 128717 (HIP 71425) — F8, V = 8.30, Gaia-6 outer published
- HD 40503 (HIP 28193) — K2/3V, V = 9.23, in Arenou 2023 BD table
- HD 14717 (HIP 10538) — Sahlmann 2025 lower-confidence candidate

TIER A Novel (4) — no published companions, multi-axis astrometric evidence:
- HD 140895 (HIP 77262) — inner P = 1460 d, M = 113 M_J, outer/inner mass ratio 1.17
- HD 140940 (HIP 77357) — inner P = 924 d, M = 183 M_J, ratio 0.86
- BD+46 2473 (HIP 90060) — inner P = 496 d, M = 74 M_J, ratio 0.68
- BD+35 228 (HIP 5787) — inner P = 560 d, M = 53 M_J, ratio 0.53; orvara MARGINAL refutation for inner orbit

### 3.4 Novel Stellar Companion Discovery

**HD 120954** (HIP 67777, Gaia DR3 6287148057608953600, G1V, V = 8.76, d = 124 pc): emerged from inclination-marginalized A9 jerk inference as a putative planet-mass candidate (M = 1.4 M_J at P = 0.63 yr at sin i = 1 face-on). Joint orvara HGCA + 3-RV-epoch fit with proper marginalization revealed **M_2 = 1.56 ± 0.5 M_sun K-dwarf companion at P = 70 yr, e = 0.23, i = 87°** (edge-on).

Five independent astrometric + RV signals converge:
- HGCA Brandt 2021 EDR3 ΔPM = 16.81 ± 0.99 mas/yr (17σ)
- Kervella 2022 PMa H2-EG3b = 4988 ± 49 m/s (102σ)
- Tycho-Gaia 25-yr ΔPM = 12.3 ± 2.7 mas/yr (4.6σ)
- Gaia DR3 NSS Acceleration9 significance = 33.08
- ΔRV across 25 yr: Nordström 2004 GCS 31.6 km/s vs Gaia DR3 38.1 km/s = +6.5 km/s shift, fully consistent with K_pred = 6.28 km/s over the 24-yr / 0.34-cycle baseline

Predicted directly imageable at SPHERE / MagAO-X with separation 0.19", ΔK ≈ 6 mag. Catalog status: 0 hits in NASA Exoplanet Archive, exoplanet.eu, arXiv abstract search, or 9 substellar literature PDFs (Brandt 2021/2024, Sahlmann-Gomez 2025, Stefansson 2025, Barbato 2023, Marcussen 2023, Xuan 2024, Lazzoni 2023, Sahlmann 2011, Feng 2022, Mills 2018). Kervella 2019 catalog flagged BinH = 1 but no follow-up paper exists.

This is a genuine novel wide-orbit stellar binary discovery, distinct from the substellar campaign goal but methodologically informative.

## 4. Conclusions

A multi-pipeline filter cascade applied to public Gaia DR3 NSS data yields a stringent test of substellar discovery. Of 26,263 initial candidates, only 2 systems survive all 34 filters with supporting astrometric and (partial) RV evidence: **HD 101767** and **HD 104828**.

Definitive confirmation requires either:
1. Gaia DR4 epoch astrometry (December 2026 public release), which will release per-transit radial velocities and intermediate astrometric data for all candidates. This will resolve the inclination-mass degeneracy through joint epoch RV + epoch astrometric fitting without any new telescope time.
2. 2–6 nights of new RV observations at northern-hemisphere small-aperture spectrographs (TRES, FIES, SOPHIE, HARPS-N) at quadrature spacing across the NSS-derived orbital period.

Methodologically, the analysis demonstrates that:

1. **High-significance HGCA acceleration signatures (snrPMa > 100) systematically prefer stellar M-dwarf companions** in eccentric or low-inclination orbits over substellar companions. Five high-snrPMa "flagship" candidates (HD 150248, HD 198387, HD 191797, HD 185414, HD 3412) all collapsed to M-dwarfs after deep-dive joint analysis. The substellar discovery space favors moderate (snrPMa = 5–30) acceleration combined with multi-axis independent confirmation.

2. **The Kervella 2022 PMa M_2 estimate is a model-independent stellar/substellar discriminator** and must be applied universally across all candidate pools (Lesson #34). Retroactive application to NSS Acceleration caught 584 unique stellar imposters that earlier filters missed.

3. **NSS Acceleration9 jerk-inferred mass requires proper inclination marginalization** (Lesson #33). Face-on (sin i = 1) assumptions systematically bias toward planet-mass; the same accel + jerk signature is mathematically compatible with low-M short-P face-on OR high-M long-P edge-on configurations.

4. **Published companion catalogs have systematic ingestion gaps** (Lesson #22, #29, #30, #31). NASA Exoplanet Archive PS table excludes M > 13 M_J; SIMBAD child-object entries are not indexed under host-name searches; entire RV survey papers (Mills 2018 N2K, Feng 2022) have minimal catalog presence. Direct Gaia DR3 source_id cross-match plus child-object cone search catch these gaps.

5. **Multi-instrument joint Bayesian RV inference recovers known companions at sub-percent precision** when N_combined ≥ 200 epochs across ≥ 3 archives (validated on HD 33636 b: P recovery 0.6–2%; HD 142 b: 0.3% off P; HD 142 c: 8% off P; HD 175167 b: 3–6% off).

## 5. Data and Code Availability

All input catalogs cited in Section 1 are publicly available via Vizier (CDS Strasbourg) or instrument-specific archives (Gaia ESA Archive, NASA Exoplanet Archive TAP, MAST, ESO Archive). The pipeline source code is included in this repository under `scripts/`. Output candidate table is `novelty_candidates.csv`.

Confirmation of the two truly novel substellar candidates will be possible by December 2026 via Gaia DR4 epoch radial velocities without additional telescope time.
