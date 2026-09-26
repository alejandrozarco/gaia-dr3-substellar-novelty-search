# Zeeman-split Balmer lines in SDSS-V DR20 white-dwarf spectra (2026-09-23)

## Sample
SDSS-V DR20 SnowWhite classifications (`snow_white_boss_star`, CAS DR20): 78 stars with p_dah + p_dahe + p_dbh + p_mwd > 0.3
(`data/sw_magnetic.csv`). SIMBAD spectral types: 17 DAH, 2 DAP, 59 other (DA, DA:, none). Spectra: Astra 0.8.1 `mwmStar` coadds
and `mwmVisit` visits (BOSS, APO and LCO).

## Method
1. `scripts/zeeman_scan_v1.py`: linear-Zeeman triplet vs a single Gaussian. Rejected: every star, including ordinary DA spectra,
   preferred a triplet at 5-8 MG because one Gaussian cannot fit a Balmer line with a narrow core and broad wings.
2. `scripts/zeeman_scan2.py`: null = two concentric Gaussians (core + wing) per line; alternative = the same profile as a
   linear-Zeeman triplet (pi 0.5, sigma 0.25 each) with one field for H-alpha and H-beta, scanned 0.2-30 MG; ranking plus visual
   inspection of all 78 (`figures/zeeman_v2_page*.png`). 32 stars without a magnetic SIMBAD type were selected by eye.
3. `scripts/zfit_free.py`: per line, three free-centre Gaussians plus a broad wing on a linear continuum; field from the sigma
   half-separation, B_split = dlambda / (20.13 A/MG at H-alpha, 11.04 A/MG at H-beta). Values are on the linear-splitting scale.
   Comparison with published fields for four stars in the sample: SDSS J074853.07+302543.5 (Kepler+2013, from Kulebi+2009 model
   fits: 8.0 MG) 5.25/5.70; SDSS J202501.10+131025.6 (11.0) 5.81/5.59; SDSS J100759.80+162349.6 (14.0) 7.08/6.93;
   J0547+1501 (Jewett+2024 offset dipole: 8 MG) 5.29/5.22 (H-alpha/H-beta). No conversion is applied.
4. Selection limits of steps 2-3: the continuum windows (|dlambda| > 190 A at H-alpha) contain the sigma components for
   B_split >~ 9 MG, and non-linear (high-field) patterns are not modelled. A second look at the 27 unselected stars with full-range
   spectra (`scripts/fullspec.py`, `figures/rest27_fullspec_p*.png`) added five stars with B_split 9-11 MG
   (`data/second_look_summary.csv`).
5. Pipeline velocity shifts (`scripts/visits.py`, `data/visits.json`): Astra resamples each visit to a rest frame with the XCSAO
   velocity `xcsao_v_rad`, which for these white dwarfs ranges from -725 to +8176 km/s. Three stars whose coadds showed all Balmer
   lines displaced (Gaia DR3 604881311110788864, 894999926685547520, 600396471902522624) have one visit with xcsao_v_rad
   +5365, +4212 and +8176 km/s; SDSS (2001, 2006) and eBOSS/BOSS (2012, 2017) spectra of the first two show normal DA lines
   (`figures/rv_artefact_sdss_vs_sdssv.png`). After undoing the shift per visit, the triplet fits of the other stars are repeated
   per visit; for most stars H-alpha and H-beta give the same B_split within ~10% (Doppler copies would give
   B_Hbeta/B_Halpha = 1.35), and the pi components are displaced to the blue by more in H-beta than in H-alpha (H-beta shifts often
   reach the 15 A fit bound).

## Prior-classification checks (per object)
SIMBAD (identifiers, types, bibliography; `scripts/simbad_refs.py`); VizieR all-table cone, 5 arcsec around the J2000 position
(`scripts/novelty.py`; 18 of 19 known magnetic stars in the sample return a DAH/DAP/magnetic value, the miss is classified only in
the DESI EDR catalogue); ADS full text on all aliases including Jhhmm+ddmm and Jhhmmss+ddmmss forms (`scripts/ads_aliases.py`);
DESI DR1 spectra (Legacy Survey viewer layer) and the DR1 classifications of Amorim+2026 (arXiv:2607.00430, GitHub
DESI_CLASS_FINAL.txt) and Swan+2026 (arXiv:2609.04314, Warwick catalogue v1.0); LAMOST DR10 v2.0 cone search
(`scripts/desi_lamost_lookup.py`); Montreal White Dwarf Database master table (table.json, 163,279 rows, modified 2026-08-05);
arXiv source text of 18 papers (`scripts/prior_art_sources.py`, `data/paper_source_matches.json`: Kilic+2020, Kilic+2025,
Caron+2023, Jewett+2024, Moss+2025, Amorim+2023, Hardy+2023, Kulebi+2009, Amorim+2026 (two papers), Swan+2026, Yu+2026,
Garcia-Zamora+2026, Kawka+2007, Kawka & Vennes 2012, Koester+2009, Napiwotzki+2020, Vincent+2020; 17 of 19 known magnetic
controls are found). Not searched: observatory archives other than the ESO log, MWDD per-paper references.

## Results
- 32 stars selected in step 2: 10 already classified as magnetic (DESI DR1: 8; LAMOST DR5/DR7 pipeline, Yu+2026 and
  Jewett+2024: Gaia DR3 3347953532952671360; Garcia-Zamora+2026: 3306772527522597632).
- 22 with no magnetic classification found outside SnowWhite (`data/novelty_summary.csv`, `figures/no_label_22_grid.png`).
  SnowWhite DR20 classes of 18 of them contain DAH; the four without are 1980205739970324224, 3115382600062991872,
  6465559379883395328 and 5665371272869153152. Independent visual grades: secure 6499095244738784128, 2883030508640778752,
  5660016586818424832, 4307667617377160704, 6430762242043644032, 1980205739970324224, 5680077137810906624,
  6412133010376770560; probable 2069622487994113408, 428300220431345536, 4236646794083461120, 3115382600062991872,
  5848754492268362624, 1199447137276626048, 4680104332056706304, 4800536829945050752, 657989024107287168; possible
  6465559379883395328, 375892788968158848, 5665371272869153152, 4833309388918586624, 4187365308538865792.
- Second look: five more with no magnetic classification found (4198738558061020928 and 5807585134758743040 secure;
  50526755482496000, 2833867392391927936, 4241409569220727424 probable); three velocity-shift artefacts; five uncertain.

## J2159+5102 = Gaia DR3 1980205739970324224 (WDJ215917.13+510257.23)
- G 17.06, parallax 12.64 +- 0.06 mas (79 pc), (l, b) = (97.5, -3.1) deg, RUWE 1.03. Gentile Fusillo+2021: Teff_H 10,690 +- 330 K,
  log g 8.35, M 0.82. Vincent+2024 (Gaia XP): "DA:", P(DA) 0.11, Teff 10,959 K, M 0.86. MWDD: "DA:".
- SDSS-V APO BOSS, one visit (MJD 60625, 730 s). SnowWhite DR20: DA (p_dah 0.46; fitted log g at the grid limit 9.49).
  B_split 5.64 +- 0.03 (H-alpha) and 5.57 +- 0.03 MG (H-beta); errors are formal fit errors (`figures/j2159_spectrum.png`).
- Vincent, Bergeron & Lafreniere 2020 (AJ 160, 252), Table 2 (new ZZ Ceti stars): P 1286 s, amplitude 1.2%, 5-sigma level 0.27%,
  one 1.7-h unfiltered run on 2020-08-07 (408 x 15 s).
- ZTF DR light curves 2018-2025 (773 g, 1046 r epochs; `scripts/ztf_ls*.py`, `data/j2159_ztf_ls*.{json,txt}`): no significant
  periodicity 5-300 c/d; per-season maxima in 50-85 c/d all have Baluev FAP >= 0.06 (2020 g: 1278 s, FAP 0.16). Injected coherent
  sinusoids at 60-75 c/d are recovered in 40/40 (g) and 37/40 (r) trials at 1.2% and 37/40 (g) and 15/40 (r) at 0.8%. The r-band
  48.00 c/d peak coincides with a spectral-window peak (47/48/49 c/d). Non-coherent signals are not tested by ZTF.
- Gaia DR3 neighbours at 1.60" (G 18.77), 2.33" (G 18.66), 3.34" (G 20.47), 3.81" (G 20.85), 5.36" (G 19.64).

## J2316-5529 = Gaia DR3 6499095244738784128 (GALEX J231613.4-552927)
G 16.70, 62 pc, B_split 8.01/7.83 MG in the coadd and 8.02/7.86 and 7.99/7.81 MG in the two visits (MJD 60581, 60582). Listed as a
common-proper-motion pair with HD 219458 (F3/5IV, G 6.8) at 164" (~10,200 au projected) in El-Badry & Rix 2018, J/ApJS/247/66,
J/ApJS/253/58 and J/A+A/658/A22. ESO archive: X-shooter 2020-11-22 (programme 106.213V.001, public since 2021-11-22) and UVES
2025-10-27 (programme 116.2964.001, release date 2026-10-27). No publication naming the star was found.

## Files
`scripts/` analysis scripts (run from a working directory holding `sw_magnetic.csv`, `spec/`, `mwdd/`, `desi/`, `arx/`);
`data/` inputs and per-object results; `figures/` plots named above.

## Correction (2026-09-24)
The Amorim+2026 classification file (DESI_CLASS_FINAL.txt) stores Gaia DR3 ids as rounded floating-point numbers (all
44,306 ids above 2^53 are multiples of 64), so the exact-id matches used above are invalid for that file. Matching by
position instead: 1350726601382165632 and 3666514280951973504 are DAH in Amorim+2026 as well as in Swan+2026 (their verdicts
are unchanged); none of the 27 stars without a magnetic classification lies within 917" of any Amorim+2026 entry.
