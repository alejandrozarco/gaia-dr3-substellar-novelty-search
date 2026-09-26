# New ZZ Ceti stars from SDSS-V DR20 spectroscopy x TESS (lane 1 + DBV lane 3; 2026-09-24)

Sample: SDSS-V DR20 SnowWhite DA spectra with Teff 10-13.5 kK, log g 7.3-9.3, S/N > 8 (4,536 rows) and DB-class spectra with
Gentile Fusillo+2021 Teff_He 19-36 kK (219); G < 18: 912 stars; 743 with SPOC time series (`data/tess_coverage.json`).
Light curves: SPOC 120-s PDCSAP from Sectors >= 70 (Cycles 6-8; earlier cycles are covered by Romero+2022/2025, and Huang+2026
searched Cycle 7 20-s data): 1,562 requested, 1,506 analysed (552 DA and 36 DB stars), 56 download holes.
Method (`scripts/run_lane1.py`, `scripts/vet_lane1.py`): QUALITY = 0, 5-sigma clip, Lomb-Scargle amplitude spectrum 20-359 c/d;
detection = highest peak >= 5x mean amplitude and Baluev FAP < 1e-3; frequencies shared by >= 3 targets in a sector would be
flagged as instrumental (none found). Known-pulsator filter: 882-star list (`../magnetic_pulsators_2026_09_24/`), plus SIMBAD,
VSX API, MWDD, ADS full text on all aliases and the source text of Romero+2022, Romero+2025, Bognar+2023, Huang+2026 and
Vincent+2020 (`data/new7_novelty.json`). Pixel test (`scripts/vet_candidate.py`): single-source Gaussian-PSF fits to the
in-phase amplitude map of the target pixel file, WCS re-registered with Gaia; control KX Dra: target chi2 38 vs >= 1,015.

Result: 35 stars with a detection; 29 known pulsators recovered (28 in the 882-star list; PG 1310+583, Bognar+2026, found only by
the ADS name search). Six candidates tested:

| Gaia DR3 | name | G | SnowWhite Teff / log g | TESS | pixel test | status |
|---|---|---|---|---|---|---|
| 6492083311194727168 | [OHD2001] WD J2324-595 | 16.81 | 11,600 K / 7.89 | 1049.3 s (S102 12.1 sigma, S103 8.7); 881.6-884.8 s (S103 10.0, S104 8.3, S105 5.1) | on target (S102 delta chi2 68, S103 73) | new ZZ Ceti; VSX lists VAR (Gaia DR3) |
| 6558472750993181568 | GALEX J214927.5-515827 | 17.08 | 11,817 K / 8.12 | 472.6 s in S95/S102/S104/S105 (4.7, 4.4, 4.3, 6.4 sigma); 947.5 s (S102 6.5 sigma) | on target (S102 delta chi2 58, S105 59) | new ZZ Ceti; VSX lists WD (Gaia DR3) |
| 2908195134345338496 | GALEX J054243.4-261011 | 17.63 | 12,173 K / 7.93 | 692.1 s (S98 5.7 sigma; only sector) | on target (delta chi2 21) | probable; not in VSX |
| 4729763229265811328 | GALEX J033619.1-564435 | 17.49 | 11,626 K / 8.07 | 971.3 s (S96 6.2 sigma; only sector) | target preferred over G 15.26 star at 9.2" (delta chi2 9) | probable; VSX lists VAR (Gaia DR3) |
| 6437146045214398336 | - | 17.19 | - | 4043 s in 4 sectors (CROWDSAP 0.008) | on G 10.26 star 26.6" away (delta chi2 637) | contamination |
| 3642549978347753600 | GALEX J142410.1-042116 | 17.94 | - | 3282 s (S91; CROWDSAP 0.012) | not significant in the pixels (1.5 sigma) | dropped |

DB stars (36 with data): highest peak S/N 4.9; no DBV detection. Figures: `figures/fig_<gaia>.png` (amplitude spectra per sector).

## Lane 1b: TESS Cycles 1-5 (Sectors < 70), 120-s light curves (2026-09-24)
Same 912-star selection and analysis (`scripts/run_lane1b.py`, `scripts/vet_lane1b.py`): 2,339 light curves, 2,294 analysed,
45 download holes. 35 stars with a detection (S/N >= 5, FAP < 1e-3, non-instrumental); 31 in the known-pulsator list, plus PG 1310+583 again
(Bognar+2026). New signals:

| Gaia DR3 | name | G | TESS | pixel test | status |
|---|---|---|---|---|---|
| 6472153670805656832 | L 210-25 = LTT 8002 | 16.40 | 817.3 s, 12.1 ppt, S/N 6.0 (S13 only); peaks at 880-964 s at S/N 4.0-4.4 in S27, S67, S94, S101, S104, S105 | on target (5.6 sigma, delta chi2 11.7) | probable ZZ Ceti; VSX type WD, P 1330 s (Gaia DR3) |
| 5933935199933176576 | - | 16.38 | 2948 s, 96-192 ppt (S39, S66; CROWDSAP 0.007) | - | contamination |
| 6437146045214398336 | - | 17.19 | 3798-4205 s, ~300 ppt (S39, S66; CROWDSAP 0.004) | (see above) | contamination |

`scripts/run_lane20.py` (20-s light curves, 20-2159 c/d) was started on the same selection; results pending.

## Lane 1c: TESS 20-s light curves (2026-09-24)
1,518 20-s light curves of the same selection (1,517 analysed), 20-2159 c/d (`scripts/run_lane20.py`; template test GD 491 and
TIC 24603397, injections at 150 s and 78.5 s recovered). 43 stars with a detection; no new pulsator. CX Boo (120.4 s) is recovered
only in the 20-s data (above the 120-s Nyquist frequency). No hot DAV with P < 240 s among the new objects. GALEX J214927.5-515827:
472.6 s also in S68, S95, S104 and S105. L 210-25: 940.9 s in S105 (S/N 5.0), on target in the pixel test (6.3 sigma, delta chi2 12.2),
plus 820-940 s power at S/N 3.8-4.4 in S67, S101 and S104; with the S13 detection it is a ZZ Ceti with changing modes. Four more
long-period detections (2,948-4,312 s) are in apertures with CROWDSAP < 0.04 (contamination). Vetting: `data/lane20_vet.txt`.
