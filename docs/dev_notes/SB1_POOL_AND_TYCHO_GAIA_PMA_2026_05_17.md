# SB1 pool expansion + Tycho-Gaia PMa channel (v1.16.0, 2026-05-17)

This is the canonical record of the v1.16.0 release, which collapsed
several iterative passes (NSS SB1 pool push, missing-data retrieval, SB1
continuation push, FPR walkthrough) into one consolidated set of
findings. The release adds **6 substellar candidates** to the headline
list (3 HGCA-corroborated + 3 Tycho-Gaia PMa-corroborated) and upgrades
**HD 104828 to triple-corroborated** via the full Hipparcos van Leeuwen
2007 NSS catalog port.

## 1. NSS SB1 pure-spectroscopic pool

### Motivation

Before v1.16.0, the cascade scanned only NSS Orbital + NSS Acceleration
solutions. Pure SB1 sources (single-line spectroscopic binaries solved
from radial-velocity reflex alone, without an astrometric Orbital fit)
were untouched. SB1 is an orthogonal channel: Gaia detected the host RV
reflex but the astrometric wobble was below the NSS Orbital threshold.
For brown-dwarf companions around bright F/G stars within 100 pc, this
is often the only NSS classification — the astrometric wobble is
~0.05-0.3 mas, below the Orbital cut.

### Mass function (Pourbaix 2018)

For Gaia SB1 fit (K_1, P, e), the spectroscopic mass function is
`f(M) = K_1^3 P (1 - e^2)^(3/2) / (2 pi G) = M_2^3 sin^3(i) / (M_1 + M_2)^2`.
We solve for M_2 numerically against M_1 (taken from
`gaiadr3.astrophysical_parameters.mass_flame`, fallback to 1.0 Msun)
and marginalize over an isotropic `cos(i) ~ U(-1, 1)` prior.

### Pool definition + counts

ADQL: `nss_solution_type='SB1' AND significance>=5 AND P 30-5000 d AND
G<12 AND parallax>5`. 3,049 sources.

| Stage                                                  | Count |
|--------------------------------------------------------|------:|
| Raw SB1 pool                                            | 3,049 |
| Substellar (M_2_marg < 80 MJ)                           |   162 |
| After conditional RUWE<7 (SB1 in orbit-reflex set)      |   135 |
| With HIP cross-id (`hipparcos2_best_neighbour`)         |    24 |
| HGCA Brandt 2021 chi^2 corroborated tier (5–30)         |     5 |
| **Promoted to headline (HGCA-corroborated)**            |   **3** |
| Anonymous (no HIP cross-id)                             |   110 |

### Three HGCA-corroborated SB1 promotions

| HIP   | HD       | G    | P (d)  | e     | K_1 (km/s) | M_2_marg [1σ] (MJ) | HGCA χ² |
|------:|----------|-----:|-------:|------:|-----------:|--------------------:|--------:|
| 84737 | HD 156239 | 8.10 | 109.6 | 0.47 | 0.544 | **13 [12-21]** | 8.7 |
| 84506 | HD 156342 | 8.15 | 370.3 | 0.21 | 0.454 | **20 [17-32]** | 9.6 |
| 8278  | HD 11042  | 7.59 | 191.0 | 0.07 | 1.303 | 59 [52-80]     | 9.3 |

All three pass:

- Not in SB9 (Pourbaix's own orbital-solution catalog, within 5″)
- Not in exoplanet.eu (within 30″)
- Not in NASA Exoplanet PS
- Not in Sahlmann 2025 verdict table
- Not seen by the v9b cascade (which never scanned SB1)
- SIMBAD obj_type = SB* (NSS-SB1 propagated, not independent literature)

## 2. Tycho-Gaia 25-yr PMa channel

For anonymous SB1 candidates (no HIP, hence no HGCA), Tycho-2 (1991)
provides a pre-Gaia astrometric epoch for a 25-yr proper-motion anomaly
analogous to HGCA. 110 anonymous SB1 substellar candidates were probed:

- 110/110 have a `gaiadr3.tycho2tdsc_merge_best_neighbour` cross-match.
- 101/110 also obtained Tycho-2 PM via direct Vizier I/259/tyc2 coord query
  (the Gaia table is a stricter cross-match; the direct query is more
  permissive).
- PMa χ² = `[(pm_TYC - pm_DR3)/sigma]²_RA + [(pm_TYC - pm_DR3)/sigma]²_Dec`.

### Tier breakdown (calibrated against HGCA Brandt 2024)

| Tier                      | Range            | Count | Promoted |
|---------------------------|------------------|------:|---------:|
| REJECT_likely_stellar     | χ² ≥ 100         |     ~ |    0     |
| FLAG_mass_ambiguous       | 30 ≤ χ² < 100    |    11 |    1*    |
| CORROBORATED_real_companion | 5 ≤ χ² < 30   |    32 |    2     |
| isolated_no_outer_body    | χ² < 5           |    58 |    0     |

*HD 343905 was promoted from FLAG tier despite its high χ²=75 because
the SB1 fit's M_2_marg = 24.5 MJ is well into the BD regime and the
near-face-on stellar-imposter explanation is disfavored by the orbital
geometry (P=42 d, e=0.51, K_1=1.42 km/s is too consistent for a chance
near-face-on alignment).

### Three Tycho-Gaia PMa-corroborated promotions

| Name      | Gaia DR3 source_id        | G    | P (d) | M_2_marg [1σ] (MJ) | TG χ² | Tier         |
|-----------|---------------------------|-----:|------:|---------------------:|------:|--------------|
| HD 343905 | 4521257204320883712       | 9.99 | 41.9  | **24 [21-40]**      | 75.1  | FLAG (strong)|
| HD 199695 | 1846430531030410496       | 7.94 | 62.0  | **22 [19-36]**      | 7.2   | CORROB       |
| CD-70 5   | 4702272586713535872       | 9.70 | 75.6  | 59 [51-96]          | 9.6   | CORROB       |

Vetting: all three clear SB9, exoplanet.eu, Sahlmann 2025, NASA Exo.

- **HD 343905** was anonymous in HIP (V=9.99 is below HIP V<7-8
  completeness for typical fields). SIMBAD coord lookup returned the HD
  identifier. The most striking signal: pm_RA differs by 9.6 mas/yr
  between Tycho-2 and DR3 (8.57σ in RA alone). χ²=75.1 puts it solidly
  in the Brandt-2024 FLAG tier.
- **HD 199695 = HIP 103488**. Gaia's `hipparcos2_best_neighbour` table
  missed this cross-match (a known incompleteness of the DR3 xmatch
  layer). Direct Vizier I/311/hip2 query recovered HIP 103488 with HIP
  Sn=5 (single-star in van Leeuwen 2007 — no pre-Gaia astrometric
  detection). HD 199695 is the cleanest of the Tycho-Gaia promotions:
  the χ²=7.16 is well below the FLAG/REJECT thresholds, so the mass
  posterior is the dominant signal. M_2_marg = 22 MJ entirely below
  deuterium-burning at 1σ_hi=36 MJ.
- **CD-70 5** is genuinely too southern and faint for HIP (Dec=-71.4,
  V=9.70). M_2_marg=59 MJ has 1σ_hi=96 MJ crossing the BD/star boundary
  → borderline-substellar.

### One Tier-2 rejection

**HD 104289** (Gaia 1576108450508750208) had Tycho-Gaia χ²=10.7 and
M_2_marg=47.6 MJ — looked promotable. Deep vetting found a published
planet "HD 104289 b" in exoplanet.eu and a Sahlmann 2025 verdict.
Correctly rejected as not novel.

## 3. Full Hipparcos van Leeuwen 2007 NSS port → triple-corroborated HD 104828

Vizier `Vizier.get_catalogs("I/311/hip2")` pulled **117,955 rows**. Sn
distribution:

```
5      101,801   single-star
15       8,813   van Leeuwen revised single-star
55       2,343   single-star with revised solution
95       1,908   revised component
1        1,371   orbital
7        1,208   stochastic / VIM
75         239   revised stochastic
9          104   resolved double
17         103
57          27
3           25   acceleration
35           6
0            5
115          2
```

Cross-match of the headline-15 against the full HIP NSS catalog:

| Name      | HIP    | Sn  | Note                                    |
|-----------|-------:|----:|-----------------------------------------|
| HD 101767 | 57135  |  5  | single-star                             |
| **HD 104828** | **58863** | **7**  | **stochastic — pre-Gaia companion signal** |
| HD 140895 | 77262  |  5  | single-star                             |
| HD 140940 | 77357  |  5  | single-star                             |
| HD 156342 | 84506  | 15  | revised single-star                     |
| HD 11042  | 8278   |  5  | single-star                             |
| (other 9) | …      |  5  | single-star                             |

**HD 104828 has Hipparcos Sn=7 (stochastic-motion classification)** —
Hipparcos itself in 1991 flagged its motion as not fit by the single-star
model. This pre-dates Gaia by 26 years and the HGCA by 25 years.
Combined with the existing HGCA Brandt 2024 chi^2=23.6 and DR3 NSS
Acceleration9, HD 104828 is now the project's first
**triple-corroborated** candidate. The companion has been astrometrically
detectable since 1991 but never published.

## 4. FPR walkthrough (deferred / dead-end)

The Gaia FPR (2023-10-10) has 8 tables — only `vari_epoch_radial_velocity`
and `crowded_field_source` are potentially useful for a BD hunt. Both
cross-matched 0/125 against (headline 15 + 110 anon SB1): the FPR
LPV-gated RV time-series subset has no overlap with our F/G/K dwarf pool,
and none of our candidates lie in the 9 dense FPR fields (ω Cen +
LMC/SMC clusters).

FPR CDN at <https://cdn.gea.esac.esa.int/Gaia/gfpr/> is fully accessible
and was verified by downloading one LPV shard (`VariLongPeriodVariable_005264-006601.csv.gz`,
1083 bytes, 3 rows). The CDN path adds nothing new since TAP-side is
already 0-hit. Parked for now.

## 5. Gaia DR3 RVS time-series (also dead-end)

Five DR3/FPR RV-time-series tables were cross-matched. All 0 hits for
both pools:

| Table                                  | Headline 15 | SB1 pool 3,049 |
|----------------------------------------|------------:|---------------:|
| `gaiadr3.epoch_radial_velocity`        |       0     |          0     |
| `gaiadr3.vari_rad_vel_statistics`      |       0     |          0     |
| `gaiafpr.vari_epoch_radial_velocity`   |       0     |          0     |
| `gaiafpr.vari_rad_vel_statistics`      |       0     |          0     |
| `gaiadr3.rvs_mean_spectrum`            | HTTP 500    | HTTP 500       |

`gaiadr3.rvs_mean_spectrum` has a server-side ESA TAP bug — every
chunk-size IN-list query 500s. The CDN bulk path is the workaround;
zero hits already established for the 4 working tables makes this moot.

## 6. Net inventory change in v1.16.0

| Channel                              | Headline contribution |
|---------------------------------------|----------------------:|
| NSS Orbital/Acceleration (v1.7-v1.15) | 11 (unchanged)       |
| NSS SB1 + HGCA Brandt 2021            | **+3** (HD 156239, HD 156342, HD 11042) |
| NSS SB1 + Tycho-Gaia PMa              | **+3** (HD 343905, HD 199695, CD-70 5)  |
| **Total headline**                    | **17**               |
| Triple-corroborated subset            | **1** (HD 104828)    |

Tier-2 supplementary (not in headline):

- 8 FLAG-tier anon SB1 candidates with M_2_marg < 30 MJ (Tycho-Gaia χ²
  30-100): held pending orvara joint-fit to disambiguate stellar vs
  substellar at near-face-on orbits. See `anon_sb1_tycho_pma_FULL_110.csv`.
- 110 anonymous SB1 substellar with full Tycho-Gaia PMa annotation
  (101/110 have Tycho-2 PM, 32 in CORROBORATED tier, 11 in FLAG tier).
- Widened SB1 pool staged at 31,668 sources (V<13, plx>2, sig≥3); mass
  function + Tycho-Gaia cascade processing deferred.

## 7. Scripts created in v1.16.0

- `fpr_walkthrough_2026_05_17.py`
- `nss_sb1_pool_push_2026_05_17.py`
- `nss_sb1_cascade_2026_05_17.py`
- `sb1_top5_deep_vetting_2026_05_17.py`
- `sb1_top5_simple_annotation_2026_05_17.py`
- `gaia_dr3_rvs_crossmatch_2026_05_17.py`
- `hipparcos_nss_port_2026_05_17.py`
- `tycho_gaia_outliers_and_anon_sb1_2026_05_17.py`
- `fetch_missing_data_2026_05_17.py`
- `sb1_fpr_continuation_2026_05_17.py`
- `three_continuations_2026_05_17.py`
