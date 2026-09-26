# Arévalo+2026 `nonvar-star` reservoir — eclipsing-binary pilot, 2026-09-22

## Question

Does the class `nonvar-star` in Arévalo et al. 2026 (A&A 705, A247; VizieR `J/A+A/705/A247`), restricted to
objects that the same catalogue gives a high probability of variability, contain eclipsing binaries that are
absent from variable-star catalogues?

## Samples

Parent selection: `J/A+A/705/A247/catalog`, `predClass = 'nonvar-star'`, `14.5 <= magMean <= 19.5`, `nEpochs >= 80`.

| sample | condition | parent rows | draw | stars analysed |
|---|---|---:|---|---:|
| reservoir | `Pvar >= 0.99 AND Std >= 0.04` | 274,249 | `MOD(recno,220)=13` | 1,281 |
| control | `Pvar < 0.5` | 8,576,864 | `MOD(recno,8000)=13` | 1,127 |

Duplicates within 2″ were merged. Targets were processed in shuffled order.

## Method

EB-hunt pipeline of 2026-09-20 (`scripts/eb_hunt.py`, `scripts/harmonic.py`, exact versions run):
ZTF DR light curves from IRSA (3″ cone, 2″ per-epoch filter; catflags, sharp, chi and limiting-magnitude
cuts), box least squares on flux, harmonic refinement, and a hold-out test in which the period fitted
to the first half of the data must predict the eclipses in the second half. Both templates were recovered
before the run: ZTF18abxnwmb (P = 3.727043 d) and Gaia DR3 2716884161263924224 (P = 3.969311 d).

## Pipeline result

| sample | stars | CANDIDATE | WEAK | NO_ECLIPSE | CONTINUOUS_MODULATION | DAY_ALIAS |
|---|---:|---:|---:|---:|---:|---:|
| reservoir | 1,281 | 8 (0.62%) | 54 | 784 | 348 | 87 |
| control | 1,127 | 0 (0.00%) | 21 | 725 | 317 | 64 |

The WEAK class has not been inspected.

## The eight candidates

| Arévalo OID | Gaia DR3 | G | pipeline P (d) | outcome | catalogue status |
|---|---|---:|---:|---|---|
| 2484_000431_zg_c01_q1 | 4353463277400908160 | 17.83 | 1.243326 | EB; eclipses every 1.243321 d, equal minima at 2.486657 d | VSX and Gaia DR3 EB table, P = 2.545907 d |
| 1861_000407_zg_c15_q1 | 3233615666672318336 | 18.04 | 1.53733 | EB; 1.537339 d, equal minima at 3.074660 d | VSX and Gaia DR3 EB table, P = 2.734521 d |
| 711_000456_zg_c11_q3 | 3283967904744688768 | 17.60 | 2.912971 | EB; 2.912954 d, equal minima at 5.825779 d | VSX and Gaia DR3 EB table, P = 2.784238 d |
| 747_000417_zg_c05_q1 | 3828306424841718656 | 16.72 | 1.741262 | EB; P = 3.482506 d (or 6.965012 d) | no type or period found |
| 1918_000493_zg_c16_q4 | 1738942132557316864 | 17.87 | 1.076991 | EB; P = 1.076989 d | no type or period found |
| 990_000495_zg_c14_q3 | 2709405317531811840 | 18.24 | 6.381704 | EB; P = 6.381715 d | no type or period found |
| 2445_000482_zg_c04_q4 | 4408578251951356160 | 18.70 | 0.933813 | broad continuous modulation, no clean eclipse; not pursued | Mowlavi+2021 large-amplitude list |
| 3471_000536_zg_c13_q2 | 4500887823677796736 | 18.46 | 17.646137 | signal from dense single-night sequences (6 nights); not accepted | — |

Figure: `figures/pilot_candidates_folds.png` (each candidate folded at P and 2P).

### Catalogued EBs: periods

For the three EBs already in VSX (entries named after their Gaia DR3 source, type E, period from the Gaia
DR3 eclipsing-binary table), the ZTF light curves do not phase at the catalogued period and do phase at
the period found here (`figures/known_eb_period_check.png`; BLS signal at the catalogued period is 0.25-0.44
of the value at the ZTF period). For 3283967904744688768 the frequency difference between the two values
is 1/63.0 d⁻¹. At twice the ZTF eclipse spacing the depths at phase 0 and 0.5 agree within 1.7 sigma in r and g for all
three (largest differences: +0.042 ± 0.030 mag, g, for 4353463277400908160; −0.051 ± 0.030 mag, r, for
3283967904744688768). The orbital periods are therefore 2.486657, 3.074660 and 5.825779 d if the components
are similar, or the eclipse spacing if the secondary eclipse is undetected.

### Uncatalogued EBs: parameters

| | 3828306424841718656 | 1738942132557316864 | 2709405317531811840 |
|---|---|---|---|
| RA, Dec (J2000, Arévalo) | 152.587917, −3.530851 | 320.517223, +6.955780 | 337.753877, +6.763791 |
| G, BP−RP | 16.72, 2.73 | 17.87, 1.63 | 18.24, 1.21 |
| parallax (mas) | 3.712 ± 0.116 | 0.729 ± 0.157 | 0.395 ± 0.168 |
| M_G | 9.57 | 7.18 | 6.22 (parallax S/N 2.3) |
| Teff (GSP-Phot) | 3434 K | 4014 K | 4628 K |
| RUWE | 1.41 | 1.26 | 0.96 |
| P (d) | 3.482506 (or 6.965012) | 1.076989 | 6.381715 |
| epoch of primary minimum (HJD) | 2459344.4402 | 2459478.2872 | 2459465.7205 |
| primary depth r / g / i (mag) | 0.19 ± 0.03 / 0.17 ± 0.03 / 0.22 ± 0.20 | 0.221 ± 0.010 / 0.23 ± 0.03 / 0.21 ± 0.02 | 0.52 ± 0.04 / 0.72 ± 0.18 / 0.43 ± 0.09 |
| secondary at phase 0.5 (r) | not detected (windowed median −0.004 ± 0.020 to +0.040 ± 0.037 depending on window) | 0.19 mag (windowed 0.174 ± 0.012) | ~0.2 mag (windowed 0.194 ± 0.046) |
| eclipse duration T14 (r) | 2.3 ± 0.6 % of P (1.9 h) | 7.1 ± 0.6 % of P (1.8 h) | 2.3 ± 0.3 % of P (3.5 h) |
| ZTF baseline | HJD 2458202.8-2460970.0 | 2458247.0-2460969.8 | 2458255.0-2460969.9 |
| other data | Maíz Apellániz+2023 dispersion flag VarF = VVM | Mowlavi+2021 large-amplitude list (AmpG 0.065, all class flags 0); MDW Hα DR1 source at 1.0″ | DESI DR1: STAR, subtype K, z = −0.000594 (−178 km/s); PTF catalogue entry |

Depths are trapezoid fits to per-OID-normalised ZTF photometry (`scripts/eclipse_fit.py`), errors from 150
bootstrap resamples; T14 is the fitted first-to-last-contact width. For 3828306424841718656 the pipeline
period 1.741262 d is half the eclipse spacing: at 1.741262 d, eclipse windows on odd cycles are covered
(11 points) and flat (median +0.005 mag) while even cycles hold the eclipses (19 points, +0.158 mag). At
6.965012 d the eclipses at phase 0 and 0.5 have equal depth within errors (r: 0.111 ± 0.023 vs
0.129 ± 0.048). Figures: `figures/fold_<source_id>.png`.

## Catalogue checks on the three uncatalogued EBs

| check | 3828306424841718656 | 1738942132557316864 | 2709405317531811840 |
|---|---|---|---|
| all-table VizieR cone, 6″ | 50 tables | 48 tables | 45 tables |
| VSX (VizieR mirror) | absent, coverage 9 rows in 20′ | absent, 27 | absent, 4 |
| ZTF periodic variables, Chen+2020 | absent, 1 | absent, 4 | absent, 1 |
| ATLAS variables, Heinze+2018 | absent, 10 | absent, 23 | absent, 5 |
| Gaia DR3 vclassre / veb | absent, 24 / 2 | absent, 39 / 6 | absent, 13 / 1 |
| Gavras+2023 known-variable cross-match | absent, 50 | absent, 50 | absent, 33 |
| ASAS-SN variables (bare `II/366`) | absent, 2 | absent, 6 | no coverage in 20′ |
| Mowlavi+2021 (Gaia DR2 large amplitude) | absent, 21 | **present** (0.04″) | absent, 16 |
| Maíz Apellániz+2023 (Gaia DR3 dispersions) | **present** (0.14″) | absent, 50 | absent, 50 |
| SIMBAD (TAP, 6″) | none | none | none |
| ALeRCE (3″) | ZTF20acifrhn, 4 detections; stamp classifier AGN / VS | ZTF19abbxuzo, 12 detections; light-curve classifiers Periodic / Periodic-Other; ATAT forced-photometry (beta) EA 0.33 | ZTF19abzvwvd, 10 detections; ATAT forced-photometry (beta) EA 0.52 |
| ADS full text (Gaia DR2/DR3, 2MASS, WISEA, ZTF names) | 0 hits (5 names) | 0 hits (5 names) | 0 hits (5 names) |
| Gaia DR3 sources within 10″ | target only | target only | target only |

"Absent, N" means no row within 15″ while the same catalogue returns N rows within 20′ of the position.
Not checked: the live VSX site (VizieR mirror only), TESS.

## Extrapolation to the full reservoir

| quantity | pilot | rate | 274,249 stars (95% Poisson range) |
|---|---:|---:|---:|
| pipeline candidates | 8 / 1,281 | 0.62% | 1,713 (739-3,375) |
| confirmed EBs | 6 / 1,281 | 0.47% | 1,285 (471-2,796) |
| EBs with no type or period in the checked catalogues | 3 / 1,281 | 0.23% | 642 (132-1,877) |

Throughput of the pilot: 0.13-0.14 stars/s with 4 threads against the IRSA light-curve API, i.e. about
23 days for the full reservoir by the same route.

## Files

- `scripts/` — `draw.py` (samples), `pilot.py` (run), `eb_hunt.py` + `harmonic.py` (pipeline as run),
  `vet_cone.py`, `vet_other.py`, `coverage.py` (catalogue checks), `period_check.py`, `eclipse_fit.py`,
  `period_vs_gaia.py` (periods and eclipse fits), `fold_plots.py`, `object_plots.py` (figures).
  Paths inside the scripts point to the scratch directory they ran from.
- `data/` — `results.jsonl` (all 2,408 pipeline records), `targets_*.json`, `vet_cone.json`, `vet_other.json`,
  `coverage.json`, `eclipse_fit.json`.
- `figures/` — as referenced above.
