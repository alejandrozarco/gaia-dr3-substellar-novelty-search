# Filter-Cascade Pipeline for Substellar Tertiary Candidates from Gaia DR3 NSS Data

> **This work is experimental and exploratory.** Nothing in this repository has been observationally confirmed. The candidate list is the output of an automated filter cascade applied to public archival data; surviving candidates are tentative and may turn out to be stellar binaries, photometric/activity artifacts, or already-published systems that the literature cross-match missed. No claims of discovery are made.

## What this is

A software pipeline that searches public Gaia DR3 Non-Single-Star (NSS) data for stars showing astrometric wobbles consistent with brown-dwarf-mass companions (roughly 13 to 80 times the mass of Jupiter), then applies a long sequence of filters to remove sources that are likely stellar binaries, already published, or affected by other systematics.

## A short description of brown dwarfs

Brown dwarfs are objects whose mass falls between approximately 13 and 80 times the mass of Jupiter. They form through gas-cloud collapse like stars do, but they never reach the mass threshold required for hydrogen fusion. They sit between planets and stars in the mass hierarchy.

Finding brown dwarfs in orbit around nearby stars is difficult because:
- They are much fainter than the stars they orbit (a factor of 10⁴ to 10⁶ in visible light).
- Their presence is mainly revealed by their gravitational tug, which makes the host star wobble by a tiny amount.
- The wobble is small — typically a few milliarcseconds on the sky, or a few hundred meters per second in line-of-sight velocity.

## How the pipeline operates

The European Space Agency's Gaia satellite measured the precise positions of more than one billion stars between 2014 and 2017. When a star has a brown-dwarf companion, both objects orbit a common center of mass, and the host star traces a small ellipse on the sky. Gaia's third data release (DR3, published in 2022) identified roughly 440,000 stars showing such wobbles, distributed across two complementary tables:

- **NSS Orbital**: stars where Gaia detected a full orbital cycle in the 3-year observing window, with measured period, eccentricity, and orbital geometry.
- **NSS Acceleration**: stars where Gaia detected only the curvature of the wobble (because the orbit is longer than 3 years), with measured acceleration components but not the full orbit.

This pipeline starts from those Gaia detections and applies the following sequence:

### Stage 1 — Candidate selection
Apply a broad substellar mass cut (under 200 Jupiter masses at face-on minimum) plus quality cuts on parallax, astrometric residuals, and detection significance. This yields about 26,000 candidate sources.

### Stage 2 — Inclination-marginalized mass estimates
For NSS Orbital sources, derive a mass posterior from the published orbital geometry plus assumed host mass. For NSS Acceleration sources, marginalize over an isotropic inclination prior and a log-uniform period prior. These posteriors are pipeline-derived ranking signals and depend on prior assumptions, not direct mass measurements.

### Stage 3 — Filter cascade
Cross-reference against 30+ public catalogs and surveys to filter out:
- Already-published companions (NASA Exoplanet Archive, exoplanet.eu, SIMBAD, plus specialized BD literature: Sahlmann 2011, Barbato 2023, Unger 2023, Mills 2018, Feng 2022)
- Known stellar binaries (Hipparcos-Gaia long-baseline proper-motion anomaly via Brandt 2024 and Kervella 2022, Washington Double Star catalog, SB9 spectroscopic binaries, Tokovinin Multiple Star Catalog, GALAH SB2 cross-correlation flag, Trifonov 2025 HIRES RV-variable flag)
- Activity-driven false signals (TESS rotation period matching the NSS period, Gaia variability classifier, Gaia rotational broadening)
- Specific candidates already identified by the pipeline as imposters during earlier deep-dive examination

### Stage 4 — Multi-archive radial-velocity joint Bayesian analysis
For candidates with sparse RV measurements across multiple archives (HARPS, HIRES, APOGEE, GALAH, NASA Exoplanet Archive, CARMENES), combine the data into a joint Keplerian fit with per-instrument zero-point offsets and per-instrument jitter. This can sometimes reveal signals invisible to any single survey alone. The fit is run with the `dynesty` nested sampler.

## Results

The full filter cascade reduces about 26,000 initial candidates to **11 tentative candidates** documented in `novelty_candidates.csv` (release v1.0.0, 2026-05-13).

### Candidate table

Pipeline-derived parameters for the 11 survivors. M₂ is the inclination-marginalized posterior median (1σ range in the next column). HGCA χ² is from Brandt 2024; values in the 5–30 range are independent corroboration of a real companion at 25-yr astrometric baseline. Where no HGCA entry was available (faint M-dwarfs, mostly), the strongest independent astrometric witness is cited instead.

| Name | HIP | V | SpT | d (pc) | NSS solution | P (d) | e | M₂ median (M_J) | M₂ 1σ (M_J) | Indep. witness | Category |
|---|---|---|---|---|---|---|---|---|---|---|---|
| HD 101767 | 57135 | 8.88 | F8 | 82 | Orbital | 486 | 0.45 | 62 | 55–68 | HGCA χ² = 14.2 | substellar |
| HD 75426 | 43197 | 6.72 | F5IV/V | 43 | Acceleration7 | — | — | 282 | 100–1343 | Kervella 27σ + HGCA 33σ | mass-ambiguous |
| HD 104828 | 58863 | 9.86 | K0 | 33 | Acceleration | ~3600 | — | 41 | 30–55 | HGCA χ² = 23.6 | substellar |
| HD 140895 | 77262 | 9.39 | — | — | Orbital (inner) | 1460 | — | 113 | — | Kervella 17.6σ excess | multi-body (outer) |
| HD 140940 | 77357 | 8.72 | — | — | Orbital (inner) | 924 | — | 183 | — | Kervella 18.4σ excess | multi-body (outer) |
| BD+46 2473 | 90060 | 8.97 | F5 | 286 | Orbital (inner) | 496 | 0.33 | 74 | — | HGCA χ² = 17.8 | multi-body (outer) |
| BD+35 228 | 5787 | 9.08 | G0 | 134 | Orbital (inner) | 560 | 0.40 | 53 | — | HGCA χ² = 18.9 | multi-body (outer) |
| HD 120954 | 67777 | 8.76 | G1V | 124 | Acceleration | 25,500 | — | 1637 | 1018–3621 | Kervella 591σ + ΔRV +6.5 km/s | **stellar** |
| HIP 91479 | 91479 | 11.0 | K5-K7V | 56 | AstroSpectroSB1 | 856 | 0.82 | 60 | 50–75 | HGCA χ² = 50.3 | substellar |
| HIP 60865 | 60865 | 12.09 | M dwarf | 41 | Orbital | 501 | 0.25 | 49 | 40–65 | HGCA χ² = 10.5 | substellar |
| HIP 20122 | 20122 | 13.49 | M2.0Ve | 41 | Orbital | 255 | 0.17 | 64 | 50–85 | HGCA χ² = 5.1 | substellar |

Of the 11, **HD 120954 is the one apparent stellar-mass companion** (~1.56 M_⊙ ≈ 1637 M_J at edge-on, with 5 independent astrometric + multi-decade ΔRV witnesses converging on a ~70-yr companion); the other 10 sit in or near the substellar mass range. **HD 75426 is mass-ambiguous** — the orvara joint posterior median lands in the early M-dwarf regime, but the 2σ lower tail still grazes the substellar boundary. The 4 BD+ / HD multi-body rows have the inner orbit from NSS but the outer companion mass is inferred from Kervella PMa excess and is not directly observed.

### How the candidates were arrived at

Of about 12 sources that received individual deep-dive investigation in v1:

- 7 sources turned out to be likely stellar M-dwarf companions in eccentric or moderate-inclination orbits.
- 2 sources turned out to be previously published planets/brown-dwarf candidates that the initial catalog cross-match missed because of naming or catalog-policy gaps. These cases helped identify which catalogs needed deeper cross-matching.
- 1 source turned out to be a known hierarchical triple system already catalogued in the Tokovinin Multiple Star Catalog and the Washington Double Star catalog (the latter since 1876).
- 1 source emerged as an apparent stellar companion discovery (HD 120954 in the table above), with multiple converging astrometric and radial-velocity signals. This is also tentative and depends on the joint fit.
- A handful of sources have astrometric evidence and partial archival radial-velocity statistics that are consistent with brown-dwarf-mass companions, but lack sufficient observational data for independent verification.

The v2 pipeline (Filters #27-30: documented-FP, exoplanet.eu coord, HGCA chi² tier, conditional RUWE) applied to the full 9,498-source pool surfaced 22 HGCA-corroborated candidates + 15 mass-ambiguous flagged candidates. From this 37, 2 truly novel substellar candidates with HIP cross-match were promoted (HIP 60865 and HIP 20122) — both originally filtered out of v1 because the uniform RUWE < 2 cut is inappropriate for solution types where orbital reflex is the signal.

Cross-checked against 10 recent published catalogs (Gaia DPAC 1843 BD, Halbwachs 2023 binary_masses, Marcussen+Albrecht 2023, Stevenson 2023 BD-desert, Brandt+Sosa 2025, Kiefer 2025, Wallace 2026, Stefansson 2025 G-ASOI, Halbwachs+Holl 2024 ML, Cooper 2024 UCD Companion): **zero of our 11 are in any of these catalogs**. The novelty is real — none have a published orbital characterization — but is the result of a specific filter combination (conditional RUWE × multi-pool NSS × HGCA chi² tier × M-dwarf hosts permitted) that no published catalog applies identically. See `CATALOG_COMPLETENESS_ANALYSIS.md` for the per-catalog selection-criterion breakdown.

See `REPORT.md` for the detailed methodology and `novelty_candidates.csv` for the full column set (including per-candidate Bayesian posterior scores and filter-cascade trace). Many parameters in the candidate table are pipeline estimates (e.g., inclination-marginalized mass posteriors) rather than direct measurements.

## What this pipeline does not do

- It does not propose or carry out new observations. All data come from public archives.
- It does not make discovery claims. Surviving candidates may be stellar at moderate inclinations, may be affected by systematics not captured by current filters, or may be pre-published in sources not in the cross-match.
- It does not provide definitive mass measurements. The reported masses are pipeline-derived from astrometric geometry plus prior assumptions on inclination and period.
- It has not been peer-reviewed.

## Paths forward for the tentative candidates

Confirmation of the tentative candidates listed in `novelty_candidates.csv` would require either:

1. **Gaia DR4** (currently scheduled for December 2026 with public release expected in early 2027). DR4 will publish per-transit radial velocities and intermediate astrometric data for all sources, which can resolve the inclination–mass degeneracy through joint epoch-level inference. This costs nothing and requires no new telescope time. For HD 101767, for instance, the 21 individual radial-velocity epochs that produced the summary `rv_amplitude_robust = 3.0 km/s` will become public.

2. **Targeted radial-velocity observations** with northern small-aperture spectrographs (TRES at Whipple, FIES at Nordic Optical Telescope, SOPHIE at Observatoire de Haute-Provence, HARPS-N at Telescopio Nazionale Galileo) or southern equivalents (CHIRON at SMARTS, FEROS at MPG 2.2m). Typically 2–6 epochs at orbital quadrature spacing per target. This requires telescope-allocation proposals that this archival-only pipeline does not address.

## Repository contents

- `README.md` — this file (non-technical introduction)
- `REPORT.md` — technical methodology and results in more detail
- `novelty_candidates.csv` — tentative candidate list with pipeline-derived parameters
- `scripts/` — pipeline source code (Python; uses `polars`, `numpy`, `astropy`, `dynesty`, `orvara`)
- `CATALOG_DEPENDENCIES.md` — list of external catalogs the scripts assume are locally cached, with URLs for download
- `CANDIDATE_FP_AUDIT.md` — per-candidate audit against Gaia DR3 documented false-positive sources (cosmos.esa.int/web/gaia/dr3-known-issues) and independent vetting catalogs (Sahlmann 2025, Stefansson 2025, Tokovinin MSC). Adds an `fp_risk_tier` column to `novelty_candidates.csv`.
- `candidate_bayesian_scores.csv` — per-candidate Bayesian confidence score consolidating all diagnostics. Columns include `P_real_companion`, `P_substellar_given_real`, `P_real_substellar`, and the log-odds contributions from each evidence factor (significance, solution_type, baselines, RV, RUWE, etc.). The same probabilities are mirrored into `novelty_candidates.csv`.
- `EXPANSION_AUDIT.md` — exploration of additional archival directions: AstroSpectroSB1 deep-dive (37 BD candidates with joint astro+spec orbit detection), CPM wide-companion check (0 contamination for our 8), cluster-member cross-match (none in Hunt+Reffert 2023), TESS long-period transit search for HD 101767 / HD 104828 (no transit signal), SB1+Kervella PMa hierarchical-triple expansion (61 candidates).
- `astrospectrosb1_candidates_supplementary.csv` — 37 AstroSpectroSB1 candidates surfaced by the expansion audit. NOT promoted to `novelty_candidates.csv` because they need further per-candidate vetting; documented as a separate supplementary pool.
- `sb1_kervella_hierarchical_triple_candidates_supplementary.csv` — 61 NSS SB1 sources with substellar K1 and Kervella PMa cross-match (potential hierarchical triples). NOT promoted to `novelty_candidates.csv`; documented as a supplementary expansion of the multi-body candidate category.

## Setup notes

The pipeline scripts expect catalog files to be present at a location set via the `GAIA_NOVELTY_DATA_ROOT` environment variable. The required catalogs are listed in `CATALOG_DEPENDENCIES.md` along with their public access URLs. The catalogs themselves are not redistributed in this repository.

Python package dependencies are listed in `requirements.txt`. Install with `pip install -r requirements.txt`.

## Reproducibility status

This repository is **not a turn-key reproduction package.** The pipeline source code is included, but the input data (Gaia DR3 NSS tables, HGCA, Kervella, Penoyre, Tokovinin MSC, NASA Exoplanet Archive, WDS, HARPS RVBank, HIRES, APOGEE, GALAH, LAMOST, etc.) totals roughly 100–200 GB of public catalog downloads that are not bundled here. Each catalog is listed in `CATALOG_DEPENDENCIES.md` with its public download URL.

The final candidate output (`novelty_candidates.csv`) is the result of multiple iterative passes, manual deep-dive verifications, and methodology refinements rather than a single automated pipeline run. Running the scripts blindly on a fresh catalog cache may produce a candidate list that differs from this CSV. See `REPRODUCIBILITY.md` for the full scope statement, script ordering notes, and known reproducibility caveats.

## A note on tone

The methodology lessons and filter rules in this repository were accumulated through iterative deep-dive analysis of individual sources, many of which turned out to be stellar in the end. The lessons themselves are heuristic and have not been independently validated. The pipeline is intended as a tool for examining Gaia DR3 NSS data systematically, not as a confirmed discovery system.

## Contact

For questions about specific candidates, the filter cascade, the v2 scan methodology, or anything else in this repository:

- **GitHub Issues** — [open an issue](https://github.com/alejandrozarco/gaia-dr3-substellar-novelty-search/issues) for technical bugs, candidate-parameter clarifications, or specific cross-reference requests.
- **GitHub Discussions** — [start a discussion](https://github.com/alejandrozarco/gaia-dr3-substellar-novelty-search/discussions) for open-ended threads: "anyone planning RV follow-up on candidate X?", methodology-question threads, etc.
- **Email** — `alejandro.zarcos@gmail.com` for things that don't fit a public thread (e.g., in-prep papers that overlap with a candidate, private Gaia DPAC follow-up status, coordinated submissions).

If you publish a confirmation, falsification, or independent re-analysis of any candidate in `novelty_candidates.csv`, please cite this repository's Zenodo DOI (see `CITATION.cff` for the concept DOI and version-specific DOIs).
