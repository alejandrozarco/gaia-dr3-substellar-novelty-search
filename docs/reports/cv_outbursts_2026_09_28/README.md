# Galactic outburst lane: new dwarf-nova candidates from ZTF (2026-09-28/29)

## Prior art (method level)
Szkody et al. 2020, 2021 (ZTF CVs, years 1-2); van Roestel et al. 2021 (outbursting AM CVn in ZTF); ALeRCE light-curve classifier (Sanchez-Saez et al. 2021); Rodriguez et al. 2025 (eROSITA+Gaia CVs, not in VizieR: declared hole); Inight et al. 2023/2025 (SDSS CVs); DESI DR1 CVs (2026); Canbay et al. 2025; Coppejans et al. 2016 and Drake et al. 2014 (CRTS). This lane is method validation plus propagation of uncatalogued objects, not a new method.

## Pipeline
1. pull_alerce.py: every ZTF object whose top-ranked ALeRCE class is CV/Nova (probability >= 0.3) in two classifiers: 42,533 rows, 33,860 objects.
2. xmatch_all.py (CDS XMatch): VSX, SIMBAD, Gaia DR3, 15 CV catalogues, AllWISE, eRASS1, eRASS:3. Unknown pool: not in VSX or any CV list, SIMBAD not CV-family or another class, not extragalactic-looking (Gaia parallax and proper motion both < 3 sigma, or W1-W2 >= 0.8): 8,619.
3. fetch_lc.py: ALeRCE alert detections for all 8,619 (no failures).
4. outburst.py: brightening measured against Gaia G (a ZTF reference that underestimates the star makes every visit a false brightening); placeholder magnitudes (100) removed; outburst points >= AMP above Gaia G in positive-difference detections; episodes = gaps > 15 d; fading-alert fraction. Controls (results/controls.csv): at >= 2 episodes, amp >= 2 mag, fading fraction <= 0.5: 40/80 known dwarf novae pass; 0/80 eclipsing binaries, 0/40 RR Lyrae, 0/60 young stars, 1/60 AGN.
5. Candidates: 183 repeated, 19 single outbursts. Gates (vet_cands.py): Gaia Alerts (4 hits), CRTS and Coppejans CV catalogues (0; both return 12/80 control dwarf novae), Gaia DR3 variability class. TNS web search is rate-limited (HTTP 429): tns_slow.py runs one query per 20 s with pauses; Fink's TNS field was found uninformative (1/80 known dwarf novae carry it).
6. Tier A (X-ray within 15 arcsec, or a parallax placing the star in the CV region): 17. All 17 checked in TNS, ADS (ZTF name, J-name, Gaia id), filtered VizieR all-table cones, Gaia proper motion (blazar test), ZTF data-release light curves (dr_lc.py; a second pipeline that includes quiescence).

## Tier-A outcome
- Seven candidates journaled (docs/object_journals): Gaia DR3 6291945806661266560 (ZTF20aaxughc), 3082396190372984832 (ZTF18acrmcvc), 5614298790271682688 (ZTF20actkemr), 5701425912708783488 (ZTF22aaahiva), 3109248424693126400 (ZTF18actbmig), 4308831935765230720 (ZTF21abuysmk), 5182404743053707904 (ZTF24abfojgu). ATLAS forced photometry queued. No archival spectrum in any VizieR-indexed SDSS, LAMOST or DESI table.
- Known transients: AT 2019dgd (ZTF19aapgrmm), AT 2019qbv (ZTF19aalyedp), AT 2018brg / AT 2026jxd (ZTF21aaylpht).
- Rejected: probable AGN (ZTF20aaivxme), probable quasar (ZTF19aapsymv), blend with a star ~4 mag brighter at 1.74 arcsec (ZTF20acurwll), not confirmed by the data-release light curve (ZTF20achvkyl, ZTF21aafavhq). Holes (IRSA header-only replies): ZTF19abageyu, ZTF18aauqjro.

## Gaia-first run
gaia_cvregion.py: Gaia DR3 sources in the CV region of the HR diagram (parallax/error > 3, 4 + 3(BP-RP) < M_G < 11.5 + 2.5(BP-RP)) with G range > 1 mag and negative skewness: 1,581. 1,514 are in VSX (mostly UG/UGSU/CV), 63 uncovered. Only 90 of 399 targets have ZTF alert objects (south of the ZTF sky or no alerts); one passes (a VSX RR Lyrae with 39 short episodes and many fading alerts: not a dwarf nova). Gaia epoch photometry of the 63 shows only single-point spikes; five are M31-field sources and one a known blazar. No candidates.

## Catalogue-mismatch pass
12,479 ALeRCE CV/Nova objects that VSX lists under a non-CV type (mostly E/EA, RRAB, DSCT, VAR). 30 pass the outburst detector; the ZTF data-release light curves confirm repeated outbursts in 11 whose VSX/SIMBAD type does not explain them (VSX types RR:, RR, VAR, EW; SIMBAD EB* for one); two X-ray binaries, two young stars, a Mira and a quasar candidate are explained by their class. TNS pending. These are VSX type-revision candidates, not new objects.

### Mismatch outcome (TNS complete, results/mm_final.csv)
- Journaled as VSX type-revision candidates (no TNS entry, repeated outbursts in both ZTF pipelines): SEKBO 104640.1251 (VSX RR:, X-ray; Gaia DR3 3150635554187154816), Gaia DR3 130827628710149632 (VSX RR), ZTF J203126.24+301752.2 (VSX EW, P 0.3232 d, possibly the orbital period; 1860991874621259520), ASASSN-V J192658.57+035432.7 (VSX VAR, 16-19 outbursts; 4289523583895578112), CSS 101007:001205+383049 (VSX VAR; 379786090922454656), MASTER OT J053123.94+120051.5 (VSX VAR, X-ray; 3340873919313839744).
- Registered: PS1-3PI J203539.20+460510.4 (VSX RRAB, outbursts mainly in g), MLS 171011:030654+333244 (faint), Gaia DR3 1945440861615614336 (VSX E, one outburst), and six Gaia Alerts objects with TNS names but VSX type VAR (Gaia19dme = AT 2019nkm, Gaia23bci = AT 2023dfa, Gaia20dbw = AT 2020nyn, Gaia18cno = AT 2018gcu, Gaia20cbt = AT 2020jaw, Gaia21dxt = AT 2021wuy).

## Quiescent periods of the seven candidates (2026-09-29)
`quiescent_period.py` searches the ZTF DR light curves in quiescence (outbursts ±3 d and nights with more than 6 points removed) with Lomb-Scargle and a box search on flux (quiescent_period.csv, quiescent_folds/).
- Gaia DR3 5182404743053707904 (ZTF24abfojgu) shows a coherent 0.14-mag modulation at 76.343 min or its 1-day alias 80.630 min (equal power). Both are near the CV period minimum.
- The other candidates show no significant period or eclipse. ZTF22aaahiva has only 2 usable quiescent points (hole).
- A 7.38-h "eclipse" in ZTF21abuysmk was produced by two high-cadence nights of minute-scale flickering; it disappears when those nights are dropped.
