# Rotation search: new SDSS-V magnetic white dwarfs (2026-09-24)

Targets: the 22 magnetic DA white dwarfs without a magnetic label from `mwd_zeeman_sdssv_2026_09_23` plus 5 second-look
objects (27 total; `data/targets.json`, Gaia DR3 astrometry and neighbours within 10").
Controls: 4 magnetic white dwarfs with published rotation periods and 3 non-magnetic DAs (`data/controls.json`).

## Data and method
- ZTF DR24 light curves (IRSA), target object IDs matched by position (`scripts/ztf_download.py`); detrended per field/band;
  Lomb-Scargle 0.05-300 c/d on a uniform grid (df = 0.2/baseline); window function and sidereal/solar-day aliases flagged
  (`scripts/analyze.py`, `scripts/rotlib.py`).
- Significance: Baluev FAP and a 40-permutation null on the real timestamps, with Gumbel tail fit; injection-recovery gives the
  amplitude detected 90% of the time (A90) in three period ranges (`scripts/permnull_inject.py`, `perm/`).
- TESS SPOC 120-s/200-s light curves, all available sectors (`scripts/tess_download.py`, `scripts/tess_analyze.py`); K2 where present.
- Candidates: band split (zg/zr), time split, deep/shallow-epoch split, alias ladder, harmonics, injection-alias test
  (`scripts/cand_check.py`, `cand/`); TESS pixel localisation with single-source PSF fits at Gaia positions (`scripts/tpf_localize.py`, `cand/tpfloc_*`).
- Scripts use absolute working paths under `/tmp/fanout/rotation`; raw light curves and pixel files are not kept.

## Controls
| Gaia DR3 | name | published P | recovered |
|---|---|---|---|
| 2712240064671438720 | EGGR 156 | 22.4 min | 64.15 c/d = 22.45 min (after masking the 2.00 c/d window peak) |
| 1878189370339859328 | SDSS J2223+2319 | 1.42 h | 16.893 c/d = 1.421 h (candidate; global maximum at 2 x the 1-c/d alias) |
| 1304733106575117056 | SDSS J1630+2724 | 14.86 h | 14.855 h (ZTF) |
| 1273088783971336576 | SDSS J1543+3021 | 1.31 h | 1.3054 h (ZTF; TESS S24/S51/S78; pixel fit on target) |

The 3 non-magnetic DA controls show no significant period.

## Results for the 27 targets (`data/rotation_summary.csv`, column `verdict`)
- 16 NULL: no significant period; A90 limits per target in the table (0.5-5% for ZTF, 2-20% for TESS).
- 5 NO_DATA: no usable ZTF or TESS light curve.
- Gaia DR3 6499095244738784128 (GALEX J231613.4-552927): the TESS 14.6 h signal (S95, S102-S105) is on Gaia DR3
  6499095141659569280 (G 14.27, 22" away; pixel fit delta chi2 4491 in S103), listed in VSX as ROT with P 0.60621 d (OID 8203637).
- Gaia DR3 5660016586818424832 (GALEX J095130.1-245723): 10.17 h in TESS S62 only (FAP 1.7e-7); absent in S35, S89 and S99,
  whose pixel fits prefer other stars; ZTF (298 points) shows nothing at that frequency. Unconfirmed.
- Gaia DR3 4307667617377160704: ZTF 7.87 min peak, Baluev FAP 0.010, permutation FAP 0.098. Not significant.
- Gaia DR3 4241409569220727424: ZTF 24.55 min peak, Baluev FAP 0.043, permutation FAP 0.098. Not significant.
- Gaia DR3 5680077137810906624 and 1980205739970324224 (J2159+5102): TESS long-period signals with CROWDSAP 0.01-0.03;
  not attributable to the white dwarf.

No rotation period is established for any of the 27 targets.
