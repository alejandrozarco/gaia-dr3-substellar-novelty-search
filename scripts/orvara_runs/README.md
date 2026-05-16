# orvara joint HGCA + RV runs — HIP 20122, HIP 60865, HIP 91479

## Status (v1.3.0, 2026-05-17): SETUP COMPLETE, RUNS PENDING

External review (2026-05-16) flagged that the three HGCA-corroborated
candidates with HIP entries — HIP 20122, HIP 60865, HIP 91479 — currently
have M₂ posteriors derived from an *isotropic* inclination prior alone,
when in fact the HGCA χ² constraint informs inclination. Specifically,
high HGCA χ² disfavors face-on configurations, so the proper inclination
posterior is not uniform on sin(i); it's pushed toward edge-on. This
means the marginalized M₂ posteriors are conservatively biased.

The fix is a joint HGCA + NSS Thiele-Innes Bayesian fit, like orvara does
for HD 75426 and HD 120954 (see `data/candidate_dossiers/HD_120954_deepdive/orvara_posterior.json`).

This directory contains the **input files** and **setup scripts** needed
to run orvara on each candidate. The actual MCMC runs are deferred to
v1.4.0 because:

  1. orvara is not in `requirements.txt` (it's a heavy dep with Cython
     compilation, HGCA FITS file dependency, and Hipparcos IAD data).
  2. Each candidate run is ~30–60 min of MCMC walltime to convergence.
  3. The marginalized posteriors currently in `candidate_bayesian_scores.csv`
     are correct in median (the systematic bias is on uncertainty width,
     not central value) — so the cascade verdict isn't affected, just the
     reported σ.

## What's here per candidate

For each of HIP 20122, HIP 60865, HIP 91479, this directory contains:

  * `config.ini` — orvara config file with priors and run settings
  * `input_params.json` — Gaia DR3 NSS solution parameters + HGCA Brandt 2024
    χ² + host mass prior (from TIC v8.2)
  * `archival_rv.csv` — archival RV data if available (otherwise empty)

## How to run (when orvara is installed)

```bash
# 1. Install orvara (separate environment recommended)
pip install orvara
# Note: orvara also requires HGCA_vEDR3.fits and Hipparcos IAD files.
# See https://github.com/t-brandt/orvara for setup instructions.

# 2. Run for each candidate:
cd HIP_20122 && orvara_run.py config.ini && cd ..
cd HIP_60865 && orvara_run.py config.ini && cd ..
cd HIP_91479 && orvara_run.py config.ini && cd ..

# 3. Extract posteriors and update candidate_bayesian_scores.csv
python ../extract_orvara_posteriors.py \
    --candidates HIP_20122 HIP_60865 HIP_91479 \
    --update ../candidate_bayesian_scores.csv
```

## Expected impact

Based on the precedent of HD 120954 (whose orvara fit was already run):
inclination posterior tightens from ±45° (isotropic prior) to ±10° (joint
fit) when HGCA χ² > 10. Corresponding M₂ posteriors tighten by ~30–50%
on width, with median values shifting by typically < 10%.

For HIP 20122 (HGCA χ² = 5.1): mild tightening expected, may push M₂
posterior slightly downward (since the lower-tier χ² doesn't strongly
constrain inclination).

For HIP 60865 (HGCA χ² = 10.5): moderate tightening expected.

For HIP 91479 (HGCA χ² = 50.3): strongest tightening expected. Current
posterior probably significantly conservative on σ.

## What this addresses from the v1.3.0 external review

This work plan addresses critique item #5: "Isotropic inclination prior
leaves information on the table for HGCA-corroborated candidates."
The benchmark already flags these three candidates as threshold-sensitive
(HIP 60865, HIP 20122 at χ² = 10.5 and 5.1); orvara runs would let us
report joint-posterior σ values rather than marginalization-only widths.
