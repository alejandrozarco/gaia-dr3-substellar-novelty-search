# Looking for Brown Dwarfs Around Nearby Stars

This repository contains a software pipeline that searches public astronomical data for **brown dwarfs** — objects more massive than planets but less massive than stars — orbiting nearby Sun-like stars.

## What is a brown dwarf?

A brown dwarf is an object whose mass is between roughly 13 and 80 times the mass of Jupiter. Brown dwarfs form like stars (collapse of gas clouds) but never reach enough mass to ignite hydrogen fusion and become true stars. They sit "in between" planets and stars in the size and mass hierarchy.

Finding brown dwarfs around other stars is hard because:
- They are very faint compared to the stars they orbit (factor 10⁴–10⁶ dimmer in visible light)
- They reveal themselves mainly through their gravitational pull, which makes the host star wobble back and forth
- The wobble is tiny — typically a few milliarcseconds on the sky, or a few hundred meters per second in line-of-sight velocity

## How the pipeline works

The European Space Agency's **Gaia satellite** measured precise positions of more than 1 billion stars between 2014 and 2017. When a star has a brown dwarf companion, the star wobbles slightly in a circle as both objects orbit their common center of mass. Gaia's third data release (DR3, published 2022) identified about 440,000 stars showing such wobbles in two complementary catalogs:

- **NSS Orbital**: stars where Gaia detected a full orbital cycle in 3 years of data, with measured period, eccentricity, and Thiele-Innes geometric elements
- **NSS Acceleration**: stars where Gaia detected only the curvature of the wobble (because the orbit is longer than 3 years), with measured acceleration components

This pipeline starts from those Gaia detections and applies a long sequence of filters to remove false positives, leaving the genuine new candidates.

### The filters

1. **Stellar parameter assumptions**: Pull the host star's mass from independent catalogs (TIC v8.2, APOGEE, GALAH, LAMOST). Apply the formula relating the measured wobble amplitude and orbital period to the companion mass, marginalizing over all possible orbital inclinations.

2. **Already-published systems**: Cross-reference against:
   - NASA Exoplanet Archive (all confirmed planets/BDs since 1995)
   - exoplanet.eu European catalog
   - 30+ specialized literature catalogs (Sahlmann 2011 BDs, Barbato 2023 CORALIE survey, Unger 2023 Gaia validation, Mills 2018 cold-Jupiter survey, Feng 2022 with 230 companions, etc.)
   - SIMBAD database with child-object cone search

3. **Stellar binary impostors**: Stars with M-dwarf companions can mimic brown-dwarf signatures when the orbit is at moderate inclination (i = 30–60°). Filter via:
   - Hipparcos-Gaia long-baseline proper motion anomaly (Brandt 2024, Kervella 2022)
   - Tokovinin Multiple Star Catalog (known hierarchical triples/quadruples)
   - Washington Double Star catalog (visual binaries within 15 arcseconds)
   - SB9 spectroscopic binary catalog (known orbits with K > 5 km/s)
   - GALAH SB2 cross-correlation flag (detected two sets of spectral lines)
   - Trifonov 2025 HIRES SB_flag (radial-velocity-variable host stars)
   - APOGEE STARFLAGS MULTIPLE_SUSPECT (auto-detected SB2)

4. **Activity impostors**: A rotating star with magnetic spots can produce a small astrometric wobble that mimics a companion (the photocentric position drifts as spots come into and out of view). Filter via:
   - TESS Lomb-Scargle rotation-period search at the candidate orbital period
   - Gaia DR3 vari_classifier_result (variable-star classification)
   - Gaia DR3 vbroad (projected rotational broadening)

5. **Radial-velocity reality check**: For each candidate, compute the expected radial-velocity amplitude (K_pred) assuming the orbit is real and substellar. Cross-check against any archival radial-velocity time-series (HARPS, HIRES, APOGEE, GALAH, NASA Exoplanet Archive, CARMENES, ESO Archive). If the observed velocity span exceeds 2× the prediction, the system is more massive than substellar — likely a stellar M-dwarf at moderate inclination.

6. **Multi-archive joint Bayesian analysis**: For candidates with sparse RV coverage across multiple archives (e.g., 3 HARPS epochs + 5 APOGEE + 1 GALAH), combine all data into a joint Keplerian fit using nested sampling with per-instrument zero-point offsets. This recovers periodic signals invisible to any single survey alone.

7. **The 34 methodology lessons**: During pipeline development, every individual deep dive on a candidate that turned out to be stellar produced a new filtering insight. Each was captured as a numbered "lesson" and added retroactively to the cascade. Examples:
   - **Lesson #22**: NASA Exoplanet Archive excludes objects above 13 Jupiter masses as "non-planetary," creating systematic gaps. Cross-match must use the Gaia source ID, not host names.
   - **Lesson #29**: Some confirmed planets are registered in SIMBAD as child objects (e.g., "HIP 26196b" instead of under the host name). Must do a 1-arcsecond cone search with planet/BD type filter.
   - **Lesson #33**: Gaia DR3 Acceleration9 sources with jerk-derived periods are mathematically degenerate between face-on short-period planets and edge-on long-period stellar binaries. The face-on assumption systematically biases toward planet-mass artifacts.

### What's left after filtering

Starting from ~26,000 expanded candidates, the cascade removes about 99.5% as either previously known, stellar M-dwarf in disguise, activity-driven, or otherwise refuted. After 11 detailed deep-dive investigations and applying all 34 methodology lessons, **two truly novel substellar candidates** remain:

| Target | Spectral type | Apparent magnitude | Orbital period | Mass estimate | Status |
|---|---|---|---|---|---|
| HD 101767 | F8 dwarf | V = 8.88 | 486 days | ~62 Jupiter masses | passes all filters + Gaia rv_amplitude_robust = 3 km/s confirms wobble at predicted level |
| HD 104828 | K0 dwarf | V = 9.86, d = 33 pc | ~10 years | ~41 Jupiter masses | CARMENES archival RV (3 epochs) consistent with predicted amplitude |

Plus **four novel multi-body astrometric candidates** where Gaia detected an inner orbit and the long-baseline Hipparcos-Gaia proper-motion anomaly shows an additional outer companion:

| Target | Inner period | Inner mass | Outer/Inner mass ratio |
|---|---|---|---|
| HD 140895 | 1460 days | 113 M_J | 1.17 |
| HD 140940 | 924 days | 183 M_J | 0.86 |
| BD+46 2473 | 496 days | 74 M_J | 0.68 |
| BD+35 228 | 560 days | 53 M_J | 0.53 |

And **one novel stellar binary discovery** (a real companion, but stellar rather than substellar — methodologically interesting because five independent signals converged):

| Target | Mass | Orbital period | Status |
|---|---|---|---|
| HD 120954 | 1.56 solar masses (K-dwarf) | 70 years | edge-on; directly imageable at SPHERE / MagAO-X at 0.19 arcsecond separation |

## How to confirm the candidates

The two truly novel substellar candidates need additional observations:

### Option 1: Wait for Gaia DR4 (free, public, no telescope time)

Gaia's next data release in **December 2026** will publish per-transit radial velocities for all stars (currently only released for ~370k pulsator variable stars). The 21 individual radial velocities that produced the summary `rv_amplitude_robust = 3.0 km/s` for HD 101767 will become public, sufficient to fully characterize its orbit. The same applies to HD 104828.

### Option 2: New radial-velocity observations

For HD 101767 at V = 8.88, declination +55°: 6 epochs at HARPS-N (Telescopio Nazionale Galileo, La Palma), SOPHIE (Observatoire de Haute-Provence, France), or NEID (WIYN 3.5m, Arizona). About 2 nights of queue time total. Predicted radial-velocity amplitude is 1–1.6 km/s, easily detected at sub-100 m/s precision.

For HD 104828 at V = 9.86, declination +9°: 2–3 epochs at TRES (Fred L. Whipple Observatory), FIES (Nordic Optical Telescope), or CHIRON (SMARTS) at orbital quadrature spacing. Predicted amplitude similar to above.

The multi-body candidates and HD 120954 each have specific follow-up paths described in `REPORT.md`.

## Repository contents

- `README.md` — this file (layman's explanation)
- `REPORT.md` — technical writeup with full methodology and results
- `novelty_candidates.csv` — final candidate list with parameters
- `scripts/` — reproducible pipeline source code (Python; uses polars dataframe library, dynesty nested sampling, orvara joint astrometric fitter)

## Methodological caveat

This is an archival data-mining study. None of the candidates have been confirmed by new observations. The pipeline applies a deliberately strict filter cascade — false positives have been the dominant failure mode of similar published searches, so the methodology emphasizes rejection over discovery.

The pipeline's most significant empirical finding may be that the high-significance Gaia DR3 acceleration signatures preferred by previous publications (Hipparcos-Gaia signal-to-noise > 100) systematically select **stellar M-dwarf companions** at moderate inclinations rather than substellar companions. Substellar discoveries appear to live in the moderate signal-to-noise regime (5–30) combined with multi-axis independent confirmation.
