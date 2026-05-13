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
| 27 | Gaia DR3 NSS known-FP source-ID list (4 IDs) | ESA Gaia DR3 known-issues page (updated 27 May 2024) |
| 28 | exoplanet.eu coord cross-match (5 arcsec) | Schneider+ 2011 exoplanet.eu (catches systems NASA Exo PS misses) |
| 29 | HGCA Brandt 2024 chi² tier filter — REJECT > 100, FLAG 30-100, CORROBORATED 5-30, isolated < 5 | Brandt 2024 HGCA vEDR3, applied as primary gating filter rather than cross-check |
| 30 | Conditional RUWE per `nss_solution_type` — skip < 2 cut for orbit-reflex types (Orbital, AstroSpectroSB1, OrbitalTargetedSearchValidated) where RUWE > 1.4 is expected from astrometric reflex | (this pipeline, methodology lesson) |

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

After ~30 sequential filters (the count grew through pipeline iterations):
- 1,228 sources flagged as previously-published or stellar imposters in the v1 cascade
- 14 sources flagged as previously-published in the v2 scan via Stage-3 exoplanet.eu coord cross-match (Filter #28) that NASA Exo PS via gaia_dr3_id missed
- 150 sources flagged as REJECTED by HGCA Brandt 2024 chi² > 100 in the v2 scan (Filter #29) — independently-confirmed stellar-mass companions
- ~15 sources emerged for individual deep-dive verification under v1; the v2 comprehensive scan surfaced an additional 22 CORROBORATED + 15 FLAG-mass-ambiguous HGCA-quality candidates
- 12 deep-dived sources resolved during examination under v1:
  - 7 sources were determined to be likely stellar M-dwarf companions at moderate inclination
  - 2 sources were determined to be previously published in catalogs that the initial cross-match missed
  - 1 source was determined to be a previously known hierarchical triple
  - 2 sources have astrometric and partial RV evidence consistent with substellar companions but no archival data sufficient for confirmation

After v2 scan additions and cross-check against 10 published catalogs:
- 11 tentative substellar candidates in `novelty_candidates.csv` (this release)
- 8 of 11 have independent HGCA Brandt 2024 corroboration in the CORROBORATED or FLAG range
- Aggregate expected-real-substellar yield: 5.07 (sum of per-candidate P_real_substellar)

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

#### HIP 91479 / LP 335-104 (Gaia DR3 4539057576001089408)
- K5-K7 dwarf, V ≈ 10.8, d = 55.6 pc; Luyten high-PM star
- NSS Orbital AstroSpectroSB1: P = 855.84 ± 25 d, e = 0.815 ± 0.038
- Joint astrometric Kepler M_2 from Thiele-Innes a_phot = 64 M_J (M_1 ± 20% → 55-72 M_J)
- HGCA Brandt 2024 chi² = 50.3 (FLAG mass-ambiguous tier — strong PM anomaly, mass uncertain between substellar and stellar)
- Gaia DR3 RV: rv_amplitude_robust = 3.9 km/s peak-to-peak across 30 transits, rv_chisq_pvalue = 6.7×10⁻⁵ (strongly variable)
- Marcussen & Albrecht 2023 Table 1 entry: verdict "Unknown" (independent reanalysis flagged it as low-mass companion candidate needing further follow-up)
- Originally filtered out by the uniform RUWE < 2 cut; surfaced after conditional-RUWE methodology fix (RUWE 4.1 is expected for AstroSpectroSB1 with real reflex)

#### HIP 60865 / G 123-34 (Gaia DR3 1518957932040718464)
- M dwarf, V = 12.09; high-PM Luyten star
- NSS Orbital: P = 500.7 d, e = 0.25, significance = 34.1
- M_2 marginalized median ≈ 49 M_J (BD-class)
- HGCA Brandt 2024 chi² = 10.5 (CORROBORATED tier — independent 25-yr PM anomaly)
- RUWE = 3.84 (expected for orbital reflex; conditional-RUWE filter)
- Surfaced in v2 comprehensive scan (2026-05-13); not in any of 10 cross-checked published catalogs

#### HIP 20122 (Gaia DR3 3255968634985106816)
- M dwarf, V = 13.49
- NSS Orbital: P = 254.7 d, e = 0.17, significance = 28.6
- M_2 marginalized median ≈ 64 M_J (BD-class)
- HGCA Brandt 2024 chi² = 5.1 (CORROBORATED mild tier)
- RUWE = 5.82
- Surfaced in v2 comprehensive scan; faint M-dwarf host requires precision-RV access for follow-up

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

6. **Multi-archive joint inference does not extend new-planet detection capability for the NSS substellar pool.** A reassessment of the planet-mass (K = 50–300 m/s) unlock regime — where single archives might be insufficient but combined inference might detect — found that 92.8% of NSS substellar candidates have no archive RV coverage at all. Of the 7.2% with any coverage, only 3 candidates have ≥2 useable archives. The multi-archive enhancement factor (joint inverse-variance combined SNR / best single-archive SNR) never exceeds 1.05 across this pool. The bottleneck is archive availability, not joint statistical significance. The empirically genuine "unlock" space for novel planet-mass detection lies in archive-rich blind subsets (e.g., HARPS RVBank Trifonov 2020's 1,822 stars with 50+ HARPS epochs but no announced planets) which do not intersect the NSS substellar pool and would require a separate mining pipeline outside this scope.

7. **Multiple independent astrometric baselines tend to converge on consistent orbital interpretations when a real wide-orbit companion is present.** For sources where the pipeline retained the candidate through all filters (e.g., HD 75426), four independent astrometric baselines (HGCA Hipparcos-Gaia Δμ, Kervella 2022 PMa, Gaia DR3 NSS Acceleration, Tycho-Gaia 25-year ΔPM) yielded mutually consistent v_t excess values within ~30% of each other. Whether or not the inferred mass is in the substellar regime, the convergence of multiple independent baselines is a stronger indicator of a real long-period companion than any single baseline alone, and resolves cases where any one baseline would be inconclusive.

8. **The inverse-direction blind discovery channel (RV-archive-rich, Gaia-NSS-blind) does not intersect the substellar parameter space probed by this pipeline.** Starting from the HARPS RVBank (Trifonov+ 2020, 252,615 RV epochs across 5,239 unique targets) and applying selection cuts of σ_med < 5 m/s, σ_RV < 100 m/s, baseline ≥ 5 yr, and N_epochs ≥ 30 yields 261 HD/HIP candidates with high-quality long-baseline RV monitoring. Cross-match against NASA Exoplanet Archive PS table (via both hostname / hd_name / hip_name strings and gaia_dr3_id) removes 1 known-published system (HD 125612B). Cross-match of the remaining 260 against the full Gaia DR3 NSS Orbital and NSS Acceleration tables yields 2 hits, both of which are independently catalogued as stellar multiples (HD 223238 = WDS J23479+0411A = TOK 684 visual binary in the Tokovinin Multiple Star Catalog; HD 28635 = SB\* in SIMBAD). Zero candidates carry simultaneously an unexplained Gaia NSS astrometric anomaly and a clean HARPS RV-quiet record. This is consistent with the dynamic-range mismatch between the two pipelines: HARPS-rich monitoring programs select for activity-quiet stars with σ_RV < 5 m/s (excluding any companion massive enough to drive Gaia-detectable astrometric reflex at the 20–100 pc distance scale of the sample by construction), while Gaia NSS detections at these distances require either close-in massive companions or long-baseline accelerations whose radial-velocity signature would also exceed the rv_std < 100 m/s cut. The 258 RV-rich Gaia-NSS-quiet targets form a clean negative-control sample for systematics testing but do not contribute new substellar candidates. The implication is that the pipeline's primary candidate discovery channel — Gaia NSS substellar pool + targeted RV at single quadrature epochs — remains the most productive direction. Methodology details and target lists are in the `harps_rich_blind_xmatch_2026_05_13/` dossier in the development repository.

9. **The planet-regime (M_2 < 13 M_J) tail of the Gaia DR3 NSS Orbital pool is partially accessible to first-pass detection but is degraded by Gaia's own documented false-positive software-bug artifacts at exactly this mass range.** Applying the Stage-1 face-on mass cut narrowly (M_2 face-on < 13 M_J) to the NSS Orbital pool yields 39 candidates, of which 10 are already-published Gaia-validated systems (Gaia-4, Gaia-5, HD 81040 b, HD 40503 b, HD 132406 b, etc.) and 29 are not in NASA Exoplanet Archive PS. After applying marginalized-mass confidence cuts (M_2 median < 13 M_J AND 1σ upper bound < 30 M_J), 19 face-on planet-mass candidates remain. After SIMBAD stellar-multiple flags (WDS, Tokovinin MSC, SB\*, EB\*) — 0 caught. Cross-match to exoplanet.eu within 30 arcsec — 0 hits. Cross-match to HARPS RVBank within 10 arcsec — 0 hits. The Gaia DR3 NSS known-issues page (`cosmos.esa.int/web/gaia/dr3-known-issues`, "NSS: False-positive astrometric binary solutions", updated 27 May 2024) lists four `nss_two_body_orbit` source IDs whose orbital solutions are spurious software-bug artifacts: 4698424845771339520 (WD 0141-675), 5765846127180770432 (HIP 64690), 522135261462534528 (\* 54 Cas, HIP 10031), and 1712614124767394816 (HIP 66074). Three of these four were in our Stage-1 NSS Orbital pool (HIP 64690 had been pre-filtered on quality cuts) and the brightest, \* 54 Cas (F8V at 27 pc, G = 6.45, P = 401 d, marg M_2 = 7.3 M_J), would have been the standout candidate in this probe had Gaia's documented FP catalog not been applied. After removing the 3 documented FPs the probe yields **18 candidates**, of which **7 pass the tier-A astrometric quality cut**. All remaining candidates have G ≥ 12.9 and require proposal-grade access to precision RV spectrographs (CARMENES, MAROON-X, NEID at the north; HARPS, FEROS, ESPRESSO at the south). The actionable bright-target case disappeared with the FP filter, leaving no single-night-confirmable planet candidate. **These planet-regime candidates are single-pipeline detections (Gaia DR3 NSS Orbital only) and lack the multi-archive astrometric corroboration (HGCA, Kervella PMa, Tycho-Gaia ΔPM) used for the substellar tentative list in §4.2.** They are documented separately as the result of the planet-regime probe. The empirical lesson is that Gaia DR3 NSS Orbital planet-mass detections at the survey's astrometric sensitivity floor are vulnerable to documented software-bug artifacts at exactly the parameter range of interest; the four official FP sources must be removed from any planet-regime list before further analysis, and any new candidate in this regime should be checked against the cosmos.esa.int known-issues catalog as a prerequisite filter.

10. **The v2 comprehensive scan with HGCA Brandt 2024 chi² as a primary gating filter surfaces two new tentative candidates the v1 pipeline missed, and identifies the right axes for future expansion.** Applying the v2 cascade (Filters #27-30: documented-FP, exoplanet.eu coord, HGCA chi² tier, conditional RUWE) to the full 9,498-source combined NSS Orbital + NSS Acceleration substellar pool yielded:

  - 22 sources in the CORROBORATED tier (HGCA chi² = 5-30 — independent 25-year proper-motion anomaly consistent with substellar mass)
  - 15 sources in the FLAG mass-ambiguous tier (chi² = 30-100 — real companion confirmed but mass uncertain between substellar and stellar)
  - 150 sources REJECTED in the HGCA chi² > 100 tier (likely stellar companions that the v1 cascade did not catch)
  - 14 sources REJECTED by exoplanet.eu coord cross-match (NASA Exoplanet Archive PS missed these via gaia_dr3_id-only matching)
  - 633 sources REJECTED by quality-tier RUWE filter

  Of the 22 CORROBORATED, 4 were already published (HIP 60321 b, HIP 75202 Ab, HIP 117179 b, plus G 15-6 in SB9) — caught by the same exoplanet.eu coord filter. Of the remaining 18 truly novel HGCA-corroborated candidates, 2 with substellar-class mass + clean Orbital solution_type + HIP cross-match were promoted to `novelty_candidates.csv`: **HIP 60865 (G 123-34)** with HGCA chi² = 10.5 + P = 500.7 d and **HIP 20122** with chi² = 5.1 + P = 254.7 d.

  The v1 cascade had missed both because it applied a uniform RUWE < 2 cut. RUWE > 1.4 is *expected* for sources with a real astrometric orbital reflex (the reflex IS the signal RUWE measures), so the v2 cascade applies RUWE cuts conditional on `nss_solution_type`. The same gap surfaced HIP 91479 / LP 335-104 (AstroSpectroSB1 with RUWE = 4.1 — promoted earlier when the AstroSpectroSB1 pool was first deep-dived).

  Methodology summary: the v2 scan validates that **HGCA chi² as a primary filter (not just a cross-check)** materially expands the tentative-candidate base. Of the 11 candidates in this release, 8 carry independent HGCA Brandt 2024 25-year astrometric corroboration in the CORROBORATED or FLAG range.

  Pipeline-vs-published parameter recovery: cross-checking the v2 scan's recovered parameters against published values for the 10 known systems caught (HIP 75202 Ab, HIP 117179 b, HIP 60321 b, TYC 7922-716-1 b, CD-41 1115 b, etc.) shows:
  - Period: 0% deviation (identical, both fit same Gaia data)
  - Eccentricity: identical for 8/10; for 2/10 our value disagrees with published 0.000 because the published paper used a circular fit while Gaia's NSS Orbital recovers the eccentric solution
  - Mass: typically ±25-50% (median +13% over-estimate vs Halbwachs/Pourbaix joint-fit posterior). The discrepancy is dominated by host-mass M_1 assumption uncertainty.

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
