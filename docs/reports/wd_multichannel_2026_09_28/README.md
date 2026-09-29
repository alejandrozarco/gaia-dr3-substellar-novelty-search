# Multi-channel anomaly score for the SDSS-V DR20 white dwarfs (2026-09-28)

Sample: the 50,886 SDSS-V DR20 white-dwarf targets (targets.csv of the spectrum store); 50,850 with Gaia DR3 rows.

## Channels
Each channel records whether it was measured and whether the object is anomalous (build_score.py):
- HR: M_G residual from the median at the same BP-RP (bins 0.05 mag), robust |z| > 4, parallax/error > 5.
- RUWE > 1.4.
- GVAR: Gaia G-flux scatter metric sqrt(n_obs) x flux_error / flux against its median at the same G, robust z > 5, or phot_variable_flag = VARIABLE.
- IR: G - W1 residual at the same BP-RP (AllWISE, clean photometry), robust z > 5.
- UV: NUV - G residual at the same BP-RP (GALEX GR5 AIS), robust |z| > 5.
- XRAY: eRASS1 or eRASS:3 source within 15 arcsec; measured only at l >= 180 deg.
- HALPHA: H-alpha emission screen T1/T2, not nebular. HELINES: coadd line screen DAB or DAO channel in a non-helium class. MAG: magnetic class.
- TESS: on-star-plausible TESS 2-min period (CROWDSAP >= 0.7); measured for stars in the sweep.
- Blend veto: corrected BP/RP excess > 5 sigma or ipd_frac_multi_peak > 10 removes the HR, GVAR, IR and UV channels.

Channels are grouped into six families that are physically independent measurements: GAIA (HR, RUWE, GVAR), IR, UV, XRAY, SPEC (HALPHA, HELINES, MAG), TESS. Counting channels instead of families overcounts one Gaia systematic: faint red sources disturbed by neighbours are simultaneously off the HR sequence, high in RUWE and high in G scatter (39 of the first 109 three-channel objects).

## Results
- Anomalous in three or more families: 14 objects (results/top_fam3.csv). Six are catalogued cataclysmic variables (CP Tuc, SDSS J0748+3125, 2QZ J1125-0016, SDSS J0926+0105, and two VSX UG/CV entries); four are white dwarf + M dwarf composites already labelled DA_MS/DB_MS by SnowWhite; three (sdss_id 76230369, 55863470, 100600012) are quasars at z ~ 0.85, 1.07 and 2.2 (broad Mg II, C III], H-beta; results/wdscore_five.png) that entered the white-dwarf sample on spurious 4-5 sigma parallaxes and carry SnowWhite labels CV:, DC: and DZ:; one (3376918831051328640) is a normal DA whose eROSITA match lies 10 arcsec away, where its wide main-sequence companion is the likely X-ray source.
- Rare two-family pairs (expected < 5 under independence): 9 objects (results/rare_pairs.csv), all catalogued (WD 0137-349, PG 1601+581, WDJ172406.13+562003.08, BPS CS 22888-0045 and others) except Gaia DR3 315403470297682304, a very blue, nearly featureless spectrum with weak narrow Balmer lines at S/N 2-3 per visit (a very hot white dwarf or hot subdwarf; not significant enough to claim).
- The one magnetic DA flagged by both spectral screens (898699813376826880) is a Zeeman artefact: its H-alpha "emission" sits at the -600 km/s window edge and its He II "absorption" is impossible at 8.7 kK.
- No new candidate. The score recovers the known accretors, the white dwarf + brown dwarf WD 0137-349 and the known DAe, which validates it as a ranking layer.
