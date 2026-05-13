# Filter-Cascade Pipeline for Substellar Tertiary Candidates in Gaia DR3 NSS Data

## Status

**This work is experimental and exploratory.** All results in this report are preliminary and based on archival analysis only. No new observations have been carried out. None of the candidates have been observationally confirmed. The pipeline applies a sequence of filters to public archival data and identifies a small number of sources that survive all filters; surviving sources are described here as "tentative candidates," not as discoveries.

The methodology lessons accumulated through this pipeline are themselves experimental and have not been independently validated.

## Abstract

A software pipeline cross-correlates Gaia DR3 Non-Single-Star (NSS) Orbital and Acceleration tables (443,205 + 338,215 sources) against 30+ public literature catalogs and archival radial-velocity time-series. The goal is to identify candidate substellar (13–80 M_J) companions to bright nearby stars (V < 12, d < 200 pc) that have not been claimed in published companion catalogs. After applying 35 sequential filter cascades, ~99.5% of an initial expanded candidate pool is removed. A small number of sources survive all filters and are presented here as tentative candidates for future follow-up; these have not been verified by new observations and may turn out to be either stellar binaries at moderate inclination, photometric/activity false positives not caught by the current filters, or already-published systems that the pipeline's literature cross-match missed.

## 1. Pipeline Overview

The pipeline operates in four stages.

### 1.1 Stage 1 — Candidate Selection

Input data: Gaia DR3 `nss_two_body_orbit` (443,205 sources, mix of Orbital, SB1, SB2, AstroSpectroSB1, EclipsingBinary, EclipsingSpectro, Acceleration7, Acceleration9 solution types) and `nss_acceleration_astro` (338,215 sources, 7-parameter or 9-parameter astrometric solutions).

Substellar mass cut applied: M_2 < 200 M_J at face-on (sin i = 1) minimum. This is broader than the canonical 80 M_J brown-dwarf upper limit because moderate-inclination orbits (i = 30–60°) can have true M_2 a factor of 1.5–3× larger than the face-on minimum.

Quality cuts: parallax > 5 mas (within 200 pc), RUWE < 5, NSS significance > 10.

Output: expanded candidate pool of ~26,000 sources.

### 1.2 Stage 2 — Inclination-Marginalized Mass Posterior

For NSS Orbital sources, M_2 is derived from the Thiele-Innes elements (A, B, F, G) plus parallax plus assumed host mass M_1 (from TIC v8.2 catalog or Pecaut-Mamajek spectral-type → mass mapping):

  M_2 / (M_1 + M_2)^(2/3) × P^(2/3) = a_phot / parallax

For NSS Acceleration sources, P_orb is unknown — only the per-source acceleration magnitude and direction are constrained. The pipeline marginalizes over:
- Isotropic inclination prior P(i) ∝ sin(i)
- Log-uniform period prior P ∈ [3, 30] yr
- Kipping 2013 Beta(0.867, 3.03) eccentricity prior

For NSS Acceleration9 (9-parameter) sources, the additional jerk constraints give a factor-of-2 P_orb estimate via |jerk|/|accel| ≈ 2π/P, but this estimate is degenerate with inclination and must also be marginalized.

Per-source outputs: M_2 median, 1σ and 2σ bounds, P_substellar = fraction of marginalized samples with M_2 < 80 M_J.

These mass posteriors are pipeline-derived and depend on prior choices (inclination distribution, period distribution). They are intended as relative ranking signals, not as definitive mass measurements.

### 1.3 Stage 3 — Filter Cascade

Sequential application of 16+ literature catalog filters plus methodology rules accumulated during pipeline development:

| # | Filter | Reference |
|---|---|---|
| 1 | Sahlmann ML imposter labels | Sahlmann & Gomez 2025 |
| 2 | HGCA Brandt 2024 snrPMa | Brandt 2024 ApJS |
| 3 | Penoyre 2022 RUWE | Penoyre+ 2022 MNRAS |
| 4 | Kervella 2022 PMa M_2 (applied to all pools) | Kervella+ 2022 A&A |
| 5 | Tokovinin MSC subcomponent | Tokovinin 2018 |
| 6 | GALAH DR4 SB2 cross-correlation | Buder+ 2024 GALAH |
| 7 | Barbato 2023 CORALIE M_true > 80 M_J | Barbato+ 2023 A&A 674 A114 |
| 8 | Marcussen 2023 SB2 spectroscopic vetting | Marcussen & Albrecht 2023 AJ 165 266 |
| 9 | SB9 Pourbaix K_1 > 5 km/s | Pourbaix 2004–2025 |
| 10 | Unger 2023 joint Gaia+RV stellar verdicts | Unger+ 2023 A&A 680 A16 |
| 11 | Arenou 2023 multiplicity table | Gaia Collab. 2023b A&A 674 A34 |
| 12 | Trifonov 2025 HIRES sb_flag | Trifonov+ 2025 |
| 13 | WDS visual companion within 15" | USNO |
| 14 | Gaia DR3 vari_classifier_result | Gaia DR3 vari pipeline |
| 15 | Gaia DR3 vbroad > 15 km/s | Gaia DR3 main |
| 16 | NSS dual-classification | Gaia DR3 NSS |
| 17 | NASA Exoplanet Archive via gaia_dr3_id | Akeson+ 2013 |
| 18 | SIMBAD child-object cone search (1") | Wenger+ 2000 SIMBAD |
| 19 | TESS BLS rotation matches NSS period | MAST |
| 20 | APOGEE STARFLAGS MULTIPLE_SUSPECT | APOGEE DR17 |
| 21 | Cross-survey stellar parameter consistency | TIC+APOGEE+LAMOST+GALAH |
| 22 | K_RV / K_pred archival pre-screen | (this pipeline) |
| 23 | Moderate-snrPMa composite scoring | (this pipeline) |
| 24 | Inclination-marginalized A9 jerk re-evaluation | (this pipeline) |
| 25 | Universal Kervella M_2 stellar pre-filter | (this pipeline) |
| 26 | Tokovinin MSC + WDS speckle binary pre-check | (this pipeline) |

The filter cascade is conservative: each source must pass all applicable filters to remain. Sources failing any filter are tagged with the filter reason and removed.

### 1.4 Stage 4 — Multi-Archive RV Joint Bayesian Analysis

For candidates with multi-archive RV coverage (HARPS RVBank Trifonov 2020, HIRES Trifonov 2025, APOGEE DR17, GALAH DR4, NASA Exoplanet Archive, CARMENES DR1, ESO archive):

- Combine RVs into single time-series with per-instrument γ offsets and per-instrument jitter σ_inst as nuisance parameters
- Run 0-, 1-, and 2-Keplerian Bayesian fits via dynesty NestedSampler
- Compute log10 Bayes factor BF(2-Kep vs 1-Kep)
- Apply a 3-diagnostic gate: BF > 1.0 AND K_inner > 3σ_jitter AND inner phase-fold visibly coherent

For HGCA-corroborated sources, also run orvara joint HGCA + RV fit using the orvara package (Brandt 2021).

## 2. Pipeline Caveats

This pipeline has several known limitations:

1. **Posterior priors are assumptions, not measurements.** The isotropic inclination prior and log-uniform period prior in Stage 2 are standard choices, but actual distributions of orbital parameters in the substellar regime are unknown and may differ.

2. **Filter cascade is conservative but not complete.** The 35 filters do not exhaust possible imposter mechanisms. Sources surviving the cascade may still be stellar binaries at unusual inclinations, contaminated by background sources, or affected by photometric/activity systematics not captured by current filters.

3. **Literature catalog cross-match has gaps.** NASA Exoplanet Archive PS table excludes companions with M > 13 M_J as "non-planetary." Some published exoplanets are registered in SIMBAD as child objects (e.g., "HIP 26196b") that do not appear under host-name searches. Entire RV survey papers (Mills 2018 N2K, Feng 2022) have minimal catalog presence. The pipeline applies SIMBAD child-object cone searches and direct Gaia source_id cross-match to mitigate these gaps, but additional missed publications remain possible.

4. **The orbital mass posteriors depend on the assumed host mass.** Host mass is taken from TIC v8.2 or Pecaut-Mamajek spectral-type mapping; both have uncertainties at the 10–20% level that propagate to companion mass.

5. **The substellar mass cut at M_2 < 200 M_J face-on is permissive.** Sources with intrinsic M_2 > 200 M_J at edge-on (i = 90°) can still pass face-on selection if the orbit happens to be face-on. Stage 2 inclination marginalization addresses this, but the marginalized posterior depends on the prior.

6. **No new observations are performed.** All radial-velocity data come from public archives. For candidates with insufficient archival coverage, no statement about orbital character is possible.

## 3. Observational Caveats on Sample

The Gaia DR3 NSS Orbital and Acceleration tables themselves have known systematic effects:

- **An et al. 2025**: NSS Orbital periods exceeding the ~1095-day Gaia DR3 mission baseline are systematically biased toward longer (potentially spurious) periods.
- **Sahlmann & Gomez 2025**: ~91% of Gaia astrometric exoplanet candidates with M < 30 M_J in their machine-learning classifier are likely imposters; the true brown-dwarf candidate yield is ~9%.

These priors are reflected in the empirical results below.

## 4. Empirical Results

### 4.1 Filter Cascade Attrition

Starting expanded pool: ~26,000 sources (full NSS Orbital + Acceleration after substellar mass cut + quality cuts).

After 35 sequential filters:
- 1,228 sources flagged as previously-published or stellar imposters
- ~15 sources emerged for individual deep-dive verification (sources scoring highest under composite ranking)
- 12 deep-dived sources resolved during examination:
  - 7 sources were determined to be likely stellar M-dwarf companions at moderate inclination (mass posteriors after joint HGCA+RV fits with proper inclination marginalization indicate M_2 = 0.13–0.78 M_sun)
  - 2 sources were determined to be previously published in catalogs that the initial cross-match missed (Feng 2022 brown-dwarf catalog entry registered as SIMBAD child object; Mills 2018 RV planet announcement not ingested into NASA Exoplanet Archive)
  - 1 source was determined to be a previously known hierarchical triple (Tokovinin MSC entry since 1876)
  - 2 sources have astrometric and partial RV evidence consistent with substellar companions but no archival data sufficient for confirmation

The remaining ~3 sources have not been individually verified at deep-dive depth and may be subject to similar reclassifications.

### 4.2 Sources Surviving All Filters with Supporting Archival Evidence

The following sources survive all 35 filters and have some archival radial-velocity statistic consistent with substellar mass at the NSS-derived orbital period. These are **tentative candidates only**. None have been observationally confirmed and any of them may turn out to be stellar binaries, activity false positives, or pre-published systems missed by the literature cross-match.

#### HD 101767 (HIP 57135, Gaia DR3 841536616165020416)
- F8 dwarf, V = 8.88
- NSS Orbital period 486 ± 2 d
- Inclination-marginalized M_2 = 62 M_J at P_substellar = 0.9999 under the pipeline priors
- HGCA snrPMa = 2.79; Penoyre RUWE = 2.94
- Gaia DR3 rv_amplitude_robust = 3.0 km/s across 21 transits; rv_chisq_pvalue = 2.8 × 10⁻¹¹
- APOGEE DR17: 2 epochs over 27 d, ΔV = 145 m/s (5.6% of orbital phase)
- The ratio of Gaia-reported rv_amplitude/2 to predicted K at the NSS-marginalized mass and inclination is ≈ 0.94, which is consistent with but does not confirm the substellar interpretation
- No published companion in any of 30+ checked catalogs
- This source has no archival RV time-series sufficient to verify the orbit independently

#### HD 75426 (HIP 43197, Gaia DR3 5328000290404075264)
- F5IV/V (modern parameters indicate dwarf, not subgiant: Gaia logg = 4.12, TIC lumclass = DWARF)
- V = 6.72, d = 43 pc
- NSS Acceleration with significance = 60.3
- HGCA χ² = 1115 (~33σ formal significance)
- Kervella PMa M_2(5 AU) face-on minimum = 66 M_J; M_2(10 AU) = 76 M_J (both substellar)
- orvara HGCA-only joint fit median M_2 = 164 M_J at 1σ range [78, 688] M_J (mass-ambiguous between brown dwarf and early M-dwarf)
- Gaia DR3 rv_amplitude_robust = 1.92 km/s across 27 transits; rv_chisq_pvalue = 0.014 (statistically variable)
- No archival RV time-series available
- This source is mass-ambiguous: the orvara posterior allows both substellar and early-M-dwarf solutions

#### HD 104828 (HIP 58863, Gaia DR3 3905850581902839168)
- K0 dwarf, V = 9.86, d = 33 pc
- NSS Acceleration significance = 37.0; HGCA snrPMa = 23.6
- Inclination-marginalized M_2 median = 41 M_J at P ≈ 10 yr (substellar range under marginalization priors)
- CARMENES Cortés-Contreras 2024: 3 epochs over 88 d with K_pp = 1.30 km/s
- The K observed is roughly consistent with K predicted at substellar mass (the K_RV/K_pred archival pre-screen does not trivially rule out substellar, unlike for the 5 sources where this test ruled stellar)
- orvara posterior straddles the BD/M-dwarf boundary

### 4.3 Multi-Body Astrometric Candidates (Inner Orbital + Outer PMa)

Methodology: Cross-match NSS Orbital sources with Hipparcos-Gaia long-baseline PMa catalogs (Kervella 2022, Brandt 2024). For each NSS Orbital source, predict the inner-orbit dVt leak. Observed Kervella dVt at ≥3σ above inner-only prediction is treated as a possible outer companion signal.

Pilot test: HD 128717 (= Gaia-6, Halbwachs+ 2022 published outer companion M = 19.8 M_J at P = 3420 d) is recovered at σ_excess = 7.87. Kervella M_2(5 AU) = 16.9 M_J matches the published mass at a = 4.85 AU within ~17%.

Sources flagged as tentative multi-body candidates (no published outer companion in checked catalogs, inner orbital + outer PMa excess ≥3σ, surviving the universal Kervella M_2 filter):
- HD 140895 (HIP 77262)
- HD 140940 (HIP 77357)
- BD+46 2473 (HIP 90060)
- BD+35 228 (HIP 5787, with caveats — the inner orbit's period is uncertain)

These are pipeline outputs only and require RV characterization of the inner orbit plus direct imaging or astrometric epoch data for the outer to verify.

### 4.4 Apparent Stellar Binary Detection (Methodology Side-Effect)

HD 120954 (HIP 67777, G1V, V = 8.76) emerged from the inclination-marginalized A9 jerk inference as an initial planet-mass candidate. Joint orvara HGCA + 3 archival RV epochs analysis with proper inclination marginalization indicates a more massive companion: M_2 = 1637 M_J ≈ 1.56 M_sun K-dwarf at P ≈ 70 yr, e ≈ 0.23, i ≈ 87° (edge-on), per the pipeline's combined fit. Five astrometric and RV signals are mutually consistent with this single solution: HGCA Brandt 2021 EDR3 ΔPM = 16.81 ± 0.99 mas/yr; Kervella 2022 PMa H2-EG3b = 4988 ± 49 m/s; Tycho-Gaia 25-yr ΔPM = 12.3 ± 2.7 mas/yr; Gaia DR3 NSS Acceleration9 significance = 33.08; ΔRV across 25 yr (Nordström 2004 GCS vs Gaia DR3) = +6.5 km/s, broadly consistent with the K_pred = 6.28 km/s over the 24-yr / 0.34-cycle baseline.

The pipeline's classification of this source as "tentative stellar binary candidate" is based on the joint fit's posterior mass; this fit uses only 3 archival RV epochs and depends on the orvara HGCA prior. The conclusion should be regarded as preliminary until more RV epochs are obtained.

If the pipeline interpretation is correct, the system would be directly imageable at separation ≈ 0.19 arcsec with current high-contrast instruments.

## 5. Observations on Pipeline Behavior

The deep-dive investigations reveal patterns that may be informative for similar future searches:

1. **High HGCA snrPMa values tend to select stellar companions.** Sources with snrPMa > 100 in the deep-dive sample (HD 150248, HD 198387, HD 191797, HD 185414, HD 3412, HD 120954) all resolved to stellar companions in joint HGCA + RV analysis. This is consistent with the proportionality of astrometric acceleration with companion mass: stronger acceleration signatures preferentially come from more massive companions. The pipeline now down-weights this range via a composite score with `(1/snrPMa)^α` term.

2. **The Kervella 2022 M_2(a) curve is a useful pre-filter when applied to all NSS pools.** Initial pipeline versions applied Kervella M_2 > 200 M_J as a stellar disqualifier only to NSS Orbital candidates. Retroactively applying it universally to NSS Acceleration candidates flagged hundreds of additional likely-stellar imposters.

3. **NSS Acceleration9 jerk inference is degenerate with inclination.** The relation R = |jerk|/|accel| ≈ 2π/P_orb is mathematically valid at any single orbital phase, but the inferred mass depends on the inclination assumption. Face-on (sin i = 1) priors systematically bias toward planet-mass interpretations; proper inclination marginalization is required. HD 120954's initial planet-mass classification was an artifact of the face-on assumption.

4. **Published companion catalogs have systematic ingestion gaps.** NASA Exoplanet Archive PS table excludes M > 13 M_J as policy. SIMBAD child-object entries are not indexed under host-name searches. Some RV survey announcement papers (Mills 2018 N2K, Feng 2022) are missing from major catalogs. Direct Gaia source_id cross-match plus child-object cone search mitigate these gaps but do not fully close them.

5. **Multi-instrument joint Bayesian RV inference performs well on validators.** Pipeline test runs on systems with multiple published companions (HD 33636 b, HD 142 b/c, HD 175167 b, HD 111232 b) recover orbital parameters within 0.3–19% of literature values when the combined epoch count exceeds ~100 across ≥2 archives. The methodology may be useful for sparse-archive characterization independent of the substellar candidate search.

## 6. Confirmation Pathways

For the tentative candidates listed in §4.2, definitive characterization would require either:

1. **Gaia DR4** (Dec 2026 / public early 2027): per-transit radial velocities and intermediate astrometric data, which would resolve the inclination–mass degeneracy through joint epoch-level inference. The 21 individual radial-velocity epochs that produced the Gaia DR3 `rv_amplitude_robust = 3.0 km/s` for HD 101767 will become public; the same applies to other candidates.

2. **New radial-velocity observations** at northern small-aperture spectrographs (TRES, FIES, SOPHIE, HARPS-N), or southern equivalents (CHIRON, FEROS): typically 2–6 epochs at quadrature spacing.

This pipeline is archival-only and does not propose to carry out new observations. Confirmation of any of these candidates requires independent analysis by groups with telescope access.

## 7. Data and Code Availability

All input catalogs cited in §1.3 are publicly available via Vizier (CDS Strasbourg) or instrument-specific archives (Gaia ESA Archive, NASA Exoplanet Archive TAP, MAST, ESO Archive). The pipeline source code is in `scripts/`. The candidate output table is `novelty_candidates.csv`.

External catalog dependencies are documented in `CATALOG_DEPENDENCIES.md`. The scripts use an environment variable `GAIA_NOVELTY_DATA_ROOT` to locate locally cached catalog files; the catalogs themselves are not redistributed in this repository.

## 8. Acknowledgments and Statement on Status

This work is exploratory and experimental. It does not constitute a peer-reviewed scientific publication. The candidate list and methodology lessons may contain errors. The pipeline implementation is provided for reproducibility; results should not be treated as established findings.
