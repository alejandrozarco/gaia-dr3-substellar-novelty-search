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

The full filter cascade reduces about 26,000 initial candidates to a small set of sources that survive every filter. Of about 12 sources that received individual deep-dive investigation:

- 7 sources turned out to be likely stellar M-dwarf companions in eccentric or moderate-inclination orbits.
- 2 sources turned out to be previously published planets/brown-dwarf candidates that the initial catalog cross-match missed because of naming or catalog-policy gaps. These cases helped identify which catalogs needed deeper cross-matching.
- 1 source turned out to be a known hierarchical triple system already catalogued in the Tokovinin Multiple Star Catalog and the Washington Double Star catalog (the latter since 1876).
- 1 source emerged as an apparent stellar companion discovery (not a brown dwarf), with multiple converging astrometric and radial-velocity signals. This is also tentative and depends on the joint fit.
- A handful of sources have astrometric evidence and partial archival radial-velocity statistics that are consistent with brown-dwarf-mass companions, but lack sufficient observational data for independent verification. These appear in the candidate output table as tentative candidates only.

See `REPORT.md` for the detailed methodology and `novelty_candidates.csv` for the candidate parameters. Many parameters in the candidate table are pipeline estimates (e.g., inclination-marginalized mass posteriors) rather than direct measurements.

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

## Setup notes

The pipeline scripts expect catalog files to be present at a location set via the `GAIA_NOVELTY_DATA_ROOT` environment variable. The required catalogs are listed in `CATALOG_DEPENDENCIES.md` along with their public access URLs. The catalogs themselves are not redistributed in this repository.

## A note on tone

The methodology lessons and filter rules in this repository were accumulated through iterative deep-dive analysis of individual sources, many of which turned out to be stellar in the end. The lessons themselves are heuristic and have not been independently validated. The pipeline is intended as a tool for examining Gaia DR3 NSS data systematically, not as a confirmed discovery system.
