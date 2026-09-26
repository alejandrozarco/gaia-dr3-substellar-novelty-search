# TIC 685214650 = Gaia DR3 4771958598593101184: TESS 20-s check of the 109.7-s signal (2026-09-24)

Target: cool DC white dwarf (MWDD DC, Teff 5617 K), G 19.00, parallax 13.31 +- 0.17 mas (75 pc). Huang+2026
(arXiv:2605.03323, "A Search for High Frequency Oscillations in TESS Cycle 7", table 1) list 787.464 c/d, 69.118 ppt in
Sector 87 20-s data. Gaia neighbours: G 15.99 at 28.3" (plx 0.52 mas), G 16.53 at 42.7" (RUWE 10.2), fainter stars.

- Sector 87 (camera 3, CCD 3; 20-s SPOC; CROWDSAP 0.068, 6-pixel aperture): 787.4655 c/d (109.719 s), 65.5 +- 10.4 ppt of the
  PDCSAP flux, 0.247 +- 0.039 e/s in SAP flux (6.3 sigma); Baluev FAP 5.6e-4 over 50-2159 c/d. Orbit 1: 0.297 +- 0.055 e/s,
  orbit 2: 0.194 +- 0.056 e/s, same phase (115 deg). Not in SAP_BKG (0.04 +- 0.37 e/s).
- Sector 94 (camera 4, CCD 4; CROWDSAP 0.063, FLFRCSAP 0.66 vs 0.70): 0.051 +- 0.037 e/s at the same frequency; highest peak
  within 0.5 c/d is 24 +- 9 ppt at 786.99 c/d (FAP 1). The Sector 87 amplitude would give ~0.24 e/s.
- Pixel test (Sector 87; `tess_psf2.py`): WCS re-registered on the median image with 26 Gaia sources (offset < 0.1 px, PSF
  sigma 0.83 px). Single-source Gaussian-PSF fits to the in-phase amplitude map (49 pixels; no-signal chi2 107.5): white dwarf
  position chi2 68.3 (6.3 sigma amplitude), G 15.99 star chi2 79.3, all other sources >= 99.
- Same-CCD controls (12 Sector 87 20-s targets within 1.4 deg): no significant signal at 787.4655 c/d (<= 2.8 sigma); phases of
  the 9 faint controls are random (resultant length 0.14).
- Files: `tess_check.py` (light curves, amplitude maps), `tess_check2.py` (per orbit, background), `tess_psf2.py` (pixel test),
  `tess_ctrl2.py` (controls), `pixel_S87.png`, `pixel_S94.png`, JSON outputs.
