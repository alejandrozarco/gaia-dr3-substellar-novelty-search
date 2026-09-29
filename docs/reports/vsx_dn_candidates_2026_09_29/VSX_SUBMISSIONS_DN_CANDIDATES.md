# VSX packages — seven outbursting ZTF sources (prepared 2026-09-29, not submitted)

New entries. Values from `dn_lightcurves.py` (dn_census.csv) and `dn_fields.py` (dn_fields.json); light-curve plots
`<ZTF name>_lc.png` go in the File field. ATLAS forced photometry for these positions is queued and not included.

Common to all seven:
- Data: ZTF data-release PSF light curves (IRSA, catflags 0) and ZTF alerts (ALeRCE broker; isdiffpos 1, drb >= 0.8).
- Magnitudes are ZTF g and r (enter as Sloan g / r). "Min" is the median ZTF data-release magnitude (quiescence).
- An outburst = an episode (points grouped with gaps > 15 d) with at least 2 points more than 1.5 mag brighter than
  quiescence; isolated single points are not counted.
- Selected from ALeRCE light-curve-classifier CV/Nova objects; no entry in VSX (API, 60 arcsec, 2026-09-29, control star
  AM Her returned), SIMBAD, 15 CV catalogues (Ritter-Kolb, Szkody ZTF, Inight, DESI DR1, Canbay, LAMOST, eROSITA CVs,
  CRTS, Coppejans and others), Gaia Alerts, TNS (10 arcsec) or ADS full text (checks 2026-09-28; journals
  docs/object_journals/<Gaia id>.md).
- Discoverer: (submitter). References for every entry:
  Bellm, E. C.; et al., 2019, The Zwicky Transient Facility: System Overview — 2019PASP..131a8002B;
  Masci, F. J.; et al., 2019, The Zwicky Transient Facility: Data Processing, Products, and Archive — 2019PASP..131a8003M;
  Förster, F.; et al., 2021, The Automatic Learning for the Rapid Classification of Events (ALeRCE) Alert Broker — 2021AJ....161..242F.

Suggested filing order (strongest evidence first): 1 ZTF20aaxughc, 2 ZTF21abuysmk, 3 ZTF24abfojgu, 4 ZTF20actkemr,
5 ZTF22aaahiva, 6 ZTF18acrmcvc, 7 ZTF18actbmig.

---

## 1. Gaia DR3 6291945806661266560 = ZTF20aaxughc

| field | value |
|---|---|
| Position (J2000) | 13 38 37.35 -20 15 38.88 (Gaia DR3, epoch 2000.0) |
| Primary name | Gaia DR3 6291945806661266560 |
| Other names | ZTF20aaxughc; AllWISE J133837.39-201538.5; 3eRASS J133837.5-201542 |
| Constellation | Virgo |
| Type | UG |
| Magnitude range | 15.60 – 19.66 g |
| Period | none |
| File | `ZTF20aaxughc_lc.png` |

Remarks: Two outbursts in ZTF (2023 January 13, 11 d, peak g 15.60 / r 16.07; 2025 March 19, 7 d), 4.1 mag above quiescence
(median g 19.66, r 19.56; data-release light curve 2018 March to 2025 July). No orbital period in quiescence (ZTF,
flickering-dominated). Gaia DR3 G 19.65, BP-RP 0.46, parallax 1.60 ± 0.43 mas, proper motion 16 mas/yr (37.8 sigma).
X-ray source 3eRASS J133837.5-201542 (4.8 arcsec).

## 2. 2MASS J19140190+0843438 = ZTF21abuysmk

| field | value |
|---|---|
| Position (J2000) | 19 14 01.85 +08 43 42.82 (Gaia DR3, epoch 2000.0) |
| Primary name | 2MASS J19140190+0843438 |
| Other names | Gaia DR3 4308831935765230720; ZTF21abuysmk |
| Constellation | Aquila |
| Type | UG |
| Magnitude range | 16.22 – 18.14 r |
| Period | none |
| File | `ZTF21abuysmk_lc.png` |

Remarks: Two outbursts in ZTF (2021 August 24, 13 d, peak r 16.22 / g 16.93; 2026 May 26, 8 d), about 2 mag above quiescence
(median r 18.14, g 19.70; data-release light curve 2018 March to 2025 October, 3250 points). The source is bluer in
outburst (g-r 0.7 at peak vs 1.6 in quiescence; the field is at b = -1.0, so the quiescent colour includes reddening).
No orbital period or eclipse in quiescence (an apparent 7.4-h signal came from two high-cadence nights of flickering).
Gaia DR3 G 18.40, BP-RP 2.02, parallax 0.93 ± 0.19 mas, proper motion 4.0 mas/yr (24.6 sigma).

## 3. Gaia DR3 5182404743053707904 = ZTF24abfojgu

| field | value |
|---|---|
| Position (J2000) | 03 17 01.52 -04 21 56.39 (Gaia DR3, epoch 2000.0) |
| Primary name | Gaia DR3 5182404743053707904 |
| Other names | ZTF24abfojgu |
| Constellation | Eridanus |
| Type | CV |
| Magnitude range | 17.84 – 20.25 g |
| Period | none entered (see remarks) |
| File | `ZTF24abfojgu_lc.png` |

Remarks: Quiescent in ZTF from 2018 July to 2024 September (median g 20.25, r 20.38). The ZTF data-release photometry shows a
rise from g 20.04 (2024 September 24) to 18.38 (2024 September 27). Every later ZTF measurement lies 1.0-2.4 mag above
quiescence (g 17.84-19.27, median 18.71; r 18.09-19.36, median 18.55; 211 points), with night-to-night changes of about
0.5 mag: the data-release photometry (unbiased) covers 2024 September to 2025 October and shows no return to quiescence;
alerts (detections only) continue at the same level to 2026 September. Pan-STARRS1 (42 detections, 2010-2014, g 20.37) and
Gaia DR3 (mean G 20.35, 2014-2017) are at the quiescent level. A modulation at 76.34 min (1-day aliases 72.49 and 80.63 min
not excluded) is present in quiescence (semi-amplitude 0.20 mag) and continues in the bright state at the same frequency
and phase (0.26 mag; phase difference -0.007 ± 0.026 cycles), so the modulated flux rose with the system brightness.
GALEX NUV 20.72 (quiescence).
Gaia DR3 G 20.35, BP-RP 0.27, parallax 2.69 ± 0.79 mas, proper motion 15.5 mas/yr (19.3 sigma).

## 4. Gaia DR3 5614298790271682688 = ZTF20actkemr

| field | value |
|---|---|
| Position (J2000) | 07 41 03.36 -24 44 09.05 (Gaia DR3, epoch 2000.0) |
| Primary name | Gaia DR3 5614298790271682688 |
| Other names | ZTF20actkemr; 3eRASS J074103.2-244405; 1eRASS J074102.8-244407 |
| Constellation | Puppis |
| Type | UG: |
| Magnitude range | 16.54 – 20.22 g |
| Period | none |
| File | `ZTF20actkemr_lc.png` |

Remarks: Five outbursts in ZTF (2020 November 23 (5 d), 2021 March 7, 2022 February 19, 2022 October 31, 2025 October 30),
brightest g 16.54 / r 17.56 (different outbursts), 3.7 mag above quiescence (median g 20.22, r 19.80). Gaia DR3 G 20.27, BP-RP 1.24, parallax
0.91 ± 0.48 mas, proper motion 5.5 mas/yr (14.7 sigma). X-ray source 3eRASS J074103.2-244405 (3.8 arcsec). A VSX
DSCT|GDOR|SXPHE star (Gaia DR3 5614298858991162368, G 14.3) lies 34 arcsec away.

## 5. Gaia DR3 5701425912708783488 = ZTF22aaahiva

| field | value |
|---|---|
| Position (J2000) | 08 16 00.43 -20 30 16.46 (Gaia DR3, epoch 2000.0) |
| Primary name | Gaia DR3 5701425912708783488 |
| Other names | ZTF22aaahiva; 3eRASS J081600.3-203019; 1eRASS J081600.5-203025 |
| Constellation | Puppis |
| Type | UG: |
| Magnitude range | 16.16 – 20.77 r |
| Period | none |
| File | `ZTF22aaahiva_lc.png` |

Remarks: Four outbursts in ZTF alerts (2022 February 12 (4 d), 2023 April 16, 2024 March 19 (5 d), 2025 March 23 (3 d)),
peak r 16.16 / g 16.26, 4.6 mag above quiescence. Quiescence: ZTF data-release median r 20.77 (the data-release light
curve at this position has 79 points, nearly all from 2018); Gaia DR3 G 20.63. Gaia BP-RP 0.41, parallax 0.16 ± 0.80 mas,
proper motion 3.3 mas/yr (5.4 sigma). X-ray source 3eRASS J081600.3-203019 (3.5 arcsec).

## 6. Gaia DR3 3082396190372984832 = ZTF18acrmcvc

| field | value |
|---|---|
| Position (J2000) | 07 53 43.71 -00 59 32.63 (Gaia DR3, epoch 2000.0) |
| Primary name | Gaia DR3 3082396190372984832 |
| Other names | ZTF18acrmcvc; 3eRASS J075343.5-005932 |
| Constellation | Monoceros |
| Type | UG: |
| Magnitude range | 16.28 – 20.40 g |
| Period | none |
| File | `ZTF18acrmcvc_lc.png` |

Remarks: Two outbursts in ZTF, each caught on one night in both g and r (2024 January 30, g 18.02 / r 18.09; 2024 November 26, peak
g 16.28 / r 16.64), 4.1 mag above quiescence (median g 20.40, r 20.10; data-release light curve 2018 April to 2025 October,
593 points). Gaia DR3 G 20.25, BP-RP 0.18, parallax -0.02 ± 0.72 mas, proper motion 3.5 mas/yr (6.9 sigma). X-ray source
3eRASS J075343.5-005932 (2.3 arcsec).

## 7. Gaia DR3 3109248424693126400 = ZTF18actbmig

| field | value |
|---|---|
| Position (J2000) | 07 05 55.47 -01 54 25.89 (Gaia DR3, epoch 2000.0) |
| Primary name | Gaia DR3 3109248424693126400 |
| Other names | ZTF18actbmig; 3eRASS J070555.5-015423 |
| Constellation | Monoceros |
| Type | UG: |
| Magnitude range | 17.95 – 20.41 g |
| Period | none |
| File | `ZTF18actbmig_lc.png` |

Remarks: Three outbursts in ZTF (2020 January 2 (4 d), 2024 November 7, 2025 October 13), brightest g 17.95 / r 17.97 (different outbursts), 2.5 mag
above quiescence in g (median g 20.41, r 19.49). Gaia DR3 G 20.55, BP-RP 1.33, two-parameter astrometric solution (no
parallax). X-ray source 3eRASS J070555.5-015423 (2.2 arcsec). A VSX DSCT|GDOR|SXPHE star (Gaia DR3 3109250662374124416,
G 14.1) lies 37 arcsec away.

---

## Notes for the filer (not for submission)

- ZTF22aaahiva and ZTF18actbmig have the thinnest records (outbursts mostly in alerts, single-night episodes); ATLAS data
  from the queued request would strengthen them before filing.
- ZTF18actbmig: one 2018 high-cadence ZTF night shows two magnitude groups (r ~18.6 and ~19.6), possibly a blend; the Gaia
  two-parameter solution also points to a crowded or faint source.
- ZTF21abuysmk lies outside the eROSITA-DE sky (l = 43.3), so no X-ray statement is made for it.
