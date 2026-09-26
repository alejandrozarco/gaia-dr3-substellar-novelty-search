# VSX packages — four ZZ Ceti stars from SDSS-V DR20 x TESS (prepared 2026-09-24, not submitted)

Evidence: `docs/reports/zzceti_sdssv_tess_2026_09_24/` and the object journals. Periods from single-sector sinusoid fits to
TESS SPOC 120-s PDCSAP light curves (formal errors ~0.05 s; ZZ Ceti modes change between sectors, so periods are given to 0.1 s).
Amplitudes are PDCSAP semi-amplitudes (crowding-corrected by SPOC) converted to peak-to-peak magnitudes of the dominant mode.
Temperatures and gravities: SDSS-V DR20 SnowWhite fits to the BOSS spectra.

## 1. Revision of VSX OID 8216645 "Gaia DR3 6492083311194727168" (VAR, P 0.482612 d) = [OHD2001] WD J2324-595

| field | value |
|---|---|
| Type | ZZA (currently VAR) |
| Period | 0.0121448 d (1049.3 s), dominant in Sector 102 |
| Magnitude | max 16.70 G (VSX value kept); amplitude 0.046 TESS (dominant mode, peak-to-peak) |
| Spectral type | DA (SDSS-V DR20: Teff 11,600 K, log g 7.89) |
| Remarks | TESS 120-s photometry (Sectors 95, 102-105, 2025-26) shows pulsations at 1049.3 s (Sector 102) and 881.6-884.8 s (Sectors 103-105), semi-amplitudes 15-21 ppt. Pixel-level analysis places the signal on the white dwarf. The 0.482612-d Gaia DR3 period is not seen in TESS. The SDSS-V spectrum is a DA with Teff 11,600 K and log g 7.89, inside the ZZ Ceti instability strip. |

## 2. Revision of VSX OID 8022190 "Gaia DR3 6558472750993181568" (WD, P 0.0358047 d) = GALEX J214927.5-515827

| field | value |
|---|---|
| Type | ZZA (currently WD) |
| Period | 0.0054698 d (472.6 s) |
| Magnitude | max 16.90 G (VSX value kept); amplitude 0.036 TESS (472.6-s mode, peak-to-peak) |
| Spectral type | DA (SDSS-V DR20: Teff 11,817 K, log g 8.12) |
| Remarks | TESS 120-s photometry (Sectors 95, 102, 104, 105) shows a 472.6-s pulsation in all four sectors (semi-amplitude 16.5 ppt in Sector 105) and a 947.5-s mode in Sector 102 (19 ppt). Pixel-level analysis places both signals on the white dwarf. The 0.0358-d Gaia DR3 period is not seen in TESS. The SDSS-V spectrum is a DA with Teff 11,817 K and log g 8.12. |

## 3. New entry (probable; one sector): GALEX J054243.4-261011 = Gaia DR3 2908195134345338496

| field | value |
|---|---|
| Position (J2000) | 05 42 43.47 -26 10 11.3 (Gaia DR3, epoch 2000.0) |
| Other names | Gaia DR3 2908195134345338496; USNO-A2.0 0600-02558132 |
| Type | ZZA: |
| Period | 0.0080099 d (692.1 s) |
| Magnitude | 17.63 G; amplitude 0.045 TESS |
| Remarks | Single TESS sector (98, 120-s): 692.1-s signal, semi-amplitude 20.7 ppt, 5.7 sigma; localised on the white dwarf in the target pixel file. SDSS-V DR20: DA, Teff 12,173 K, log g 7.93. Needs a second sector before submission. |

## 4. Revision of VSX OID 2904767 "Gaia DR3 4729763229265811328" (VAR, P 0.0160481 d) = GALEX J033619.1-564435 (probable)

| field | value |
|---|---|
| Type | ZZA: |
| Period | 0.0112429 d (971.4 s) |
| Remarks | Single TESS sector (96): 971.4-s signal, 25 ppt, 6.2 sigma; CROWDSAP 0.045 and a G 15.26 star 9.2" away, which the pixel fit disfavours only moderately (delta chi2 9). SDSS-V DR20: DA, Teff 11,626 K, log g 8.07. Needs a second sector or ground photometry before submission. |

Submission order suggested: 1 and 2 now; 3 and 4 after another sector.
