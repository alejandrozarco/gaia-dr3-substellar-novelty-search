# Gaia DR3 5208047381438507520 (GALEX J073504.2-794409): carbon-rich hot white dwarf (2026-09-24)

> **Update 2026-09-25 (adversarial review 2, `review2/SUMMARY.md`):** hot DQ confirmed. Balmer lines are much weaker than in 16 DAs,
> there are no broad Ly-alpha wings, and C I troughs are present. Teff is about 22 kK (empirical), so the DA-model values below do not apply.
> Hydrogen is only *possible*. Si II 1260 is **interstellar**; the 'Si II 1260 is detected' line below is superseded. The velocity error is
> +-20-40 km/s. The 17420 'DA' label is generic. The 17420 team very likely already sees the UV carbon.


G 16.56 at 96.4 pc (parallax 10.376 +- 0.043 mas); BP-RP -0.41; M_G 11.64.
- It is catalogued as DA from photometry and Gaia XP fits:
  - MWDD / Vincent+2024: 35.3 kK, log g 9.08, 1.24 Msun;
  - Gentile Fusillo+2021: 28.6 kK;
  - Bravo+2025: DA.
- It is also target WDJ073504.07-794410.69 of HST SNAP 17420 (PI Gaensicke, COS G130M, 2024-07-13, zero proprietary period). The Phase II target listing labels it DA and records measured FUV 15.95 against a synthetic 14.80.

## Result
Carbon is detected in two independent spectra:
- **Optical (SDSS-V DR20 BOSS, one LCO visit, MJD 60695):** many C II lines at a common velocity (`scripts/spec_lines.py`, `figures/fig_lines_ccf.png`).
- **Far-UV (HST/COS):** C III 1175 and 1247 and C II 1324 (`scripts/cos_look.py`, `figures/fig_cos.png`).

A broad absorption at H-alpha (6566.4 +- 0.7 A, about +82 km/s in the reviewer's two-Gaussian fit) indicates probable hydrogen. Helium lines are not convincingly detected.

Provisional classification: **hot DQ with probable hydrogen (DQA)**. A hot DAQ, a DA+DQ composite and a magnetic carbon-rich white dwarf are not excluded. Composition, temperature and mass need a joint C/H/He atmosphere fit; the DA-based values do not apply.

No publication, catalogue or archive entry found classifies it as carbon-rich (search log below). The COS spectrum has been public since July 2024, and the HST proposers noted its FUV deficit.

## Evidence

**Optical lines**
- The C II template cross-correlation peaks at +100 km/s. The peak stands 17.5 times the off-peak scatter above the median; this is a contrast, not a calibrated false-alarm probability.
- Every other species tested gives at most 3.4.
- Nine individual C II features give a weighted mean of +93 km/s with chi2 48 for 8 degrees of freedom. With error inflation the uncertainty is about +-14 km/s, before systematics from blends and pressure shifts.

**COS equivalent widths**
- C II 1335 lies between about 1.8 and 3.0 A, depending on the continuum sidebands (reviewer 1.78-2.56; our re-check 2.03-2.96).
- The narrow minimum of the ground-state line C II 1334.53 is at +9 km/s, which suggests an interstellar component. The excited line C II 1335.71 is at +96 km/s, matching the optical carbon velocity.
- C III 1175 is 1.7 A.
- Si II 1260 is detected. N V is not established.
- The "no broad Lyman-alpha" statement in the first dossier is not demonstrated: carbon blanketing, interstellar hydrogen and airglow need modelling.

**GALEX** (`scripts/galex_test.py`, `data/galex_gravity_matched.txt`, `figures/fig_galex.png`)
- FUV-NUV is +0.315.
- DA controls:
  - 97 SDSS-V spectroscopic DAs within 0.06 mag in BP-RP span -0.93 to -0.13 (median -0.49);
  - 16 DAs with M_G > 11.3 within 0.10 mag in BP-RP have a median of -0.43 and a maximum of -0.13.
- MWDD DQ-type white dwarfs at the same colour have a median of +0.04.
- Extinction is negligible at E(B-V) = 0.004 (0.005 mag with the Wall+2019 coefficients).
- The object fails the Kilic+2025 FUV-RP selection cut (-0.888 against -0.612), which explains why it is absent from that survey.

**Variability**
- TESS: 120-s data from S27, S34, S37-S39, S61 and S64-S67; 20-s data from S61 and S64-S67. The combined 120-s periodogram's strongest peak is 4.9 ppt (FAP 0.49), with a mean amplitude of 1.1 ppt. Low-frequency power in the 20-s data is not localised.
- SkyMapper DR4 (2015-2021): scatter consistent with the errors.
- Gaia: photometric scatter equals that of DA controls; not classified as variable.

**Other checks**
- Gaia astrometry is clean: RUWE 0.97, no multi-peak images.
- No radio, X-ray or gamma-ray counterpart (`data/mwcheck.json`).
- No Gaia common-proper-motion companion.

## Novelty search
All five aliases were searched in:
- SIMBAD (DA), MWDD (DA) and a VizieR all-table cone (no DQ type);
- ADS full text (0 hits) and the source text of 58 papers;
- HST programs 17420 (DA) and 18060 (not listed);
- ESO raw archive: a sky-map calibration frame only (the first query failed and was briefly recorded as a null; corrected with a positive control);
- MAST (only 17420);
- DESI and LAMOST (no coverage);
- Gemini: login required, so not checked.

The reviewer's independent web search (`data/astra_review.md`) found no contrary classification.

## Bravo+2025 companion candidate (4.5" NE; `data/companion.txt`, `figures/fig_cutouts.png`)
**Photometry**
- Legacy Survey DR10 (point source): g 25.70, r 23.88, i 21.58, z 20.52.
- VHS: J 18.57, J-Ks 1.12.
- DELVE flags it as a likely galaxy in i.
- WISE: W1 17.0, W2 16.9 (Vega). The Legacy Survey values are AB; converted to Vega they agree with CatWISE. The first dossier's claim of a WISE photometry discrepancy was an AB/Vega mix-up.

**Assessment**
- CatWISE proper motion is (38 +- 46, 24 +- 43) mas/yr.
- The colour i-z 1.05 matches M7-M8 templates (0.98/1.18) better than L6 (1.78). A distance of about 400 pc is not established, and a galaxy remains possible.
- Bravo+2025's L6 estimate follows from M_J 13.65 if the source is at 96 pc.

## Review
An independent review (Codex, model gpt-6-astra; prompt in `data/astra_prompt.txt`, report in `data/astra_review.md`) reproduced the optical, COS, GALEX, TESS and SkyMapper numbers and made seven corrections, all adopted above:
1. WISE AB/Vega mix-up.
2. Wording of the cross-correlation significance.
3. Velocity uncertainty.
4. COS continuum systematics and interstellar C II.
5. Extinction statement and gravity matching of the GALEX controls.
6. Variability limits.
7. The failed ESO query.

It recommends coordinating with the HST SNAP team (Gaensicke, Sahu, Bedard) before calling this an unrecognised discovery, and involving an atmosphere-modelling group (Dufour/Bergeron or Kilic).
