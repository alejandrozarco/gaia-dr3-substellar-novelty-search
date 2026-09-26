# Dossier: Gaia DR3 5208047381438507520 (GALEX J073504.2-794409, WD J073504.07-794410.69, TIC 764468822)

Claim under review: this white dwarf is a hot DQ (carbon-dominated atmosphere), not the DA it is catalogued as, and no
publication classifies it as a DQ. Please try to refute this. Compiled 2026-09-24 from archival data only.

## Basic data (Gaia DR3; files gaia_flags.txt)
- RA 113.76710, Dec -79.73634 (2016.0); l = 291.8, b = -24.8.
- Parallax 10.376 +- 0.043 mas (96.4 pc); PM (+5.64, -7.91) mas/yr; v_tan 4.4 km/s.
- G 16.564, BP 16.432, RP 16.840 (BP-RP -0.408); M_G 11.64.
- RUWE 0.97, ipd_frac_multi_peak 0, astrometric_excess_noise 0.24 mas; not flagged variable; XP continuous spectrum available.
- The Gaia per-observation G scatter proxy (0.0157) equals the median of 308 SDSS-V DA white dwarfs of similar G (0.0155).
- No Gaia source within 11" (next: G 20.8 at 11.1").
- Published parameters, all assuming a DA atmosphere (photometry/XP):
  - Gentile Fusillo+2021: 28.6 kK.
  - Jimenez-Esteban+2023: 28.1 kK, log g 8.86.
  - Vincent+2024 (XP) and the MWDD: 35.3 kK, log g 9.08, 1.24 Msun, type DA.
  - Cheng+2019 list it in their high-mass WD catalogue.

## Optical spectrum: SDSS-V DR20 BOSS (Astra 0.8.1)
- One LCO visit, MJD 60695, S/N 23; sdss_id 95077848. The XCSAO rest-frame shift (+178 km/s) was undone.
- SnowWhite classification: "DA:". Files: spec_lines.py, spec_lines.json, fig_lines_ccf.png, fig_zoom_H_He.png.
- **Cross-correlation with NIST vacuum line lists** (15 strongest lines per species, 3850-9200 A):

  | species | significance | velocity |
  |---|---|---|
  | C II | 17.5 sigma | +100 km/s |
  | C I | 3.4 sigma | |
  | He I, H I, O I, O II, C III, He II, Mg II, Si II | 2.0-3.0 sigma each | |

- **Individual C II features** (Gaussian fits, 9 with depth > 5 sigma): 3921 (v +162 +- 16), 4077 (+81 +- 19), 4268 (+60 +- 12), 4375 (+63 +- 18), 4621 (+79 +- 18), 5892 (+73 +- 13), 6582 (+172 +- 26), 6783 (+137 +- 28) and 7237 (+152 +- 31) km/s.
  - Weighted mean +93 +- 6 km/s; chi2 48 for 8 degrees of freedom (scatter 43 km/s; blends and Stark shifts are not modelled).
  - For about 1.1-1.2 Msun the gravitational redshift is about 100-130 km/s, so the mean is consistent.
- **Hydrogen/helium check at +93 km/s:**
  - There is a broad (FWHM ~30 A) depression centred at H-alpha: flux ~0.72 of the local pseudo-continuum. This is significant against a 99th-percentile baseline of 0.17 in C II-free windows.
  - H-beta shows only a shallow broad depression (~0.84), and H-gamma is weak.
  - He I 5877 shows a weak feature (~7% below its surroundings). He I 4472 and 6680 are not detected; He II 4687 is not detected.
  - Possible interpretation: a trace of hydrogen (hot DQA-like) or a carbon feature. This is not resolved without model atmospheres.
- Visual comparison with SDSS-V/SDSS spectra of MWDD hot DQs is in fig: hotDQ_known_controls_sdssv.png (from the lane). The comparison objects' identities as hot DQs come from the MWDD spectype, not verified in the literature here.

## Far-UV: HST/COS G130M, public
- HST SNAP 17420 ("A legacy survey for evolved planetary systems within 100 pc", PI Gaensicke, Cycle 31, 0-month proprietary period).
- Observed 2024-07-13, 1800 s, target name WDJ073504.07-794410.69. Files: /tmp/hotdq/cos/cos_look.py, fig_cos.png.
- Equivalent widths:

  | feature | EW (A) | significance |
  |---|---|---|
  | C II 1335 | 2.43 | 41 sigma |
  | C III 1175 multiplet | 1.71 | 28 sigma |
  | C III 1247 | 0.31 | 9 sigma |
  | C II 1324 | 0.53 | 13 sigma |
  | Si II 1260 | 0.56 | 18 sigma |
  | Si IV 1394 | 0.12 | 4 sigma |
  | N V 1239 | 0.12 | 4 sigma |

- The continuum is strongly sculpted by broad troughs (about 1140, 1160, 1175, 1190, 1230, 1310-1345, 1360 and 1415 A).
- The flux falls from 2.7e-14 (1420 A) to 5e-15 (1150 A) erg/s/cm2/A.
- There is no broad Lyman-alpha trough of a DA at 20-30 kK: the flux at 1195-1210 A is similar to that at 1230-1240 A.

## GALEX (files galex_test.py, galex_test.csv, fig_galex.png)
- GUVcat AIS: FUV 15.952 +- 0.018, NUV 15.637 +- 0.010; FUV-NUV +0.315.
- 97 SDSS-V spectroscopic DAs within 0.06 mag of the target's BP-RP have FUV-NUV between -0.93 and -0.13 (median -0.49). None reaches the target's value.
- 10 MWDD DQ-type white dwarfs (Teff >= 15 kK) at the same colour have a median of +0.04 (range -0.38..+0.50).
- Interstellar extinction makes FUV-NUV bluer, not redder. At 96 pc E(B-V) is about 0.004 (Kervella+2022).

## Photometric variability
- **TESS** (TIC 764468822): SPOC 120-s in S27, 34, 37-39, 61 and 64-67; 20-s in S61 and 64-67; CROWDSAP 0.12-0.39.
  - The combined 120-s periodogram (0.05-359 c/d) has a highest peak of S/N 4.4 (FAP 0.49), mean amplitude 1.1 ppt.
  - The 20-s light curves show low-frequency power (0.06-0.5 c/d) typical of systematics in crowded apertures.
- **SkyMapper DR4** (2015-2021, 4-10 epochs per filter): chi2/dof 0.5-2.0; rms 2-7% consistent with the errors.

## Other checks
- Radio/X-ray/gamma (mwcheck): absent in RACS, SUMSS, GLEAM, ROSAT 2RXS, eRASS1, eRASS:3, Swift 2SXPS and 4FGL. XMM, Chandra, FIRST and VLASS do not cover the position.
- No common-proper-motion Gaia companion (Kervella+2022).
- Novelty gate:
  - SIMBAD type DA; MWDD DA; VizieR all-table cone (no DQ type anywhere); DESI and LAMOST do not cover it.
  - ADS full text: 0 hits for all aliases.
  - arXiv source grep of 58 papers (55 by script, 3 by hand) on DQ, hot-DQ, DAQ, massive-WD and merger-remnant spectroscopy, including Kilic+2024 (DAQ subclass), Kilic+2025 (all-sky FUV merger remnants), Sahu+2025 Nat. Astron. (WD 0525+526, same HST SNAP team), Ould Rouis+2024, Jewett+2024, Vincent+2024, Garcia-Zamora+2026 and Bravo+2025. Only Bravo+2025 lists it: as DA from photometry, with an "unreliable" candidate L6 companion.
  - HST program 18060 (Bedard, He-rich carbon dredge-up) does not list it.
  - ESO archive: the first dbo.raw query failed (geometry error) and was wrongly summarised as 'no observations' in the version sent for review;
    redone with a coordinate box and a positive control (J2316-5529 X-shooter/UVES recovered): only a GRIPS sky-map calibration frame
    within 1', no science data (eso_raw.txt). Gemini archive: login required (not checked).

## The Bravo+2025 companion candidate (companion.txt, fig_cutouts.png)
- A source 4.5" NE of the white dwarf.
- Photometry:
  - Legacy Survey DR10 (Tractor type PSF): g 25.70, r 23.88, i 21.58, z 20.52.
  - VHS: J 18.57, J-Ks 1.12; star/galaxy probabilities 0.49/0.49.
  - DELVE DR2: i only, extended_class_i = 2 ("likely galaxy").
  - CatWISE2020: W1 17.08, W2 16.99, but blended with the white dwarf at 4.5". Legacy Survey forced WISE photometry gives W1 19.67 and W2 20.21 instead.
- Proper motion: CatWISE (38 +- 46, 24 +- 43) mas/yr; no NSC DR2 detection.
- Our reading: r-i 2.3, i-z 1.05 and J-K 1.1 look like an M7-M8 dwarf at roughly 350-450 pc rather than an L6 at 96 pc. These colour-type relations are from memory and should be verified.

## Questions for the reviewer
1. Is the evidence sufficient to call this a hot DQ (carbon-dominated atmosphere)? Or could it be a hydrogen-rich carbon-polluted white dwarf (a hot "DAQ"), a DQA, a DBQ, a composite (DA + DQ double degenerate), or something else? What does the H-alpha depression imply?
2. Are the C II line identifications and the velocity consistency convincing? What else should be measured from these data?
3. Is it plausible that this object is already known or published as a DQ (e.g., by the HST SNAP 17420 team, the Montreal group, or in DESI, 4MOST or SDSS-V papers)? Please search the literature if you can, including conference abstracts and the MWDD.
4. Is the GALEX FUV-NUV argument valid as independent evidence?
5. Is the companion re-assessment sound?
6. What would you recommend as the next step (who to contact, what to write), given that the HST/COS data have been public since July 2024?
