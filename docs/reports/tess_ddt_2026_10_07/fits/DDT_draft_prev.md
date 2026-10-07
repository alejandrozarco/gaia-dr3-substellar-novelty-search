# TESS DDT proposal: DRAFT for PI review (not submitted)

Prepared on 2026-10-07 (UTC). The format follows the official template (tess-ddt-template.tex/.pdf/.docx in this folder): at most 2 pages including figures and references. The recommended sections are DDT Justification, Scientific Justification, Target Justification and Feasibility, and References. The target list goes in a separate machine-readable file with the columns tic, priority (0-1) and keywords (separated by `;`). Send both files to tess-ddt at mit dot edu, which the PI does. A DDT ID is assigned by the TESS team.

**Title:** 20-second cadence of the totally eclipsing white dwarf + M dwarf binary WDJ111803.09-544218.04 (TIC 450781262, P = 2.25 h)

**Proposer:** <PI NAME> (independent / <affiliation> | <email>)

**Cadence:** 20 s, **Sectors:** 111, 112, 113, 114 (on silicon in all four, per tess-point)

**Submission deadline:** 2026-10-15 for all four sectors (S111 starts 2026-11-26). Late window for S111: 2026-11-12, only "under certain circumstances", which would have to be stated. If S111 is missed, S112-S114 remain open until 2026-11-10.

---

## 1. DDT Justification

TIC 450781262 (Gaia DR3 5346312514819760896, WDJ111803.09-544218.04, G = 17.38, T = 17.41) was identified on 2026-09-29 as a totally eclipsing post-common-envelope binary with P = 0.093889794(2) d. That date is after the Cycle 9 GI deadline, and the target falls in Sectors 111-114, which are before any Cycle 10 observations. To our knowledge no publication lists a period, eclipse or binary classification for it (searched: VSX, SIMBAD, MWDD, VizieR, ADS full text).

The target has earlier 2-min data in S90 and S99 and 20-s data in S90, through GI white-dwarf survey programmes (G07092; G08002/G08062). It is therefore likely, though not confirmed, that Cycle 9 white-dwarf programmes will include it at 2-min cadence in S111-S114. The S111+ target lists have not been released yet. We request **20-s cadence only**, because that is the cadence that resolves the white dwarf's eclipse ingress and egress (Section 3).

## 2. Scientific Justification

Optical and infrared photometry show that the system is a low-mass DA white dwarf plus an M4-M5 dwarf:
- MWDD spectroscopic fit: 14.9 kK, log g 7.05, 0.25 Msun.
- AllWISE W1 = 15.52 and 2MASS Ks = 16.08 at about 300 pc.

ATLAS forced photometry over 2015-2026 shows a red-dominated reflection modulation (o 8.3%, c 4.6% semi-amplitude). It also shows a flat-bottomed eclipse at reflection phase 0.5 that hides the hot component:
- c-band depth 102 +- 2% of the white dwarf's expected contribution
- first-to-last contact 7.6 +- 0.2 min
- mid-eclipse BJD_TDB 2460684.83515 +- 0.06 min (ATLAS exposure-start times corrected to mid-exposure)

Eclipsing white dwarf + M dwarf binaries with a resolved ingress and egress are the main source of model-independent white-dwarf radii (e.g. Parsons et al. 2017). He-core white dwarfs of about 0.25 Msun are scarce among them, and this would be a southern, 2.25-h example. The ingress duration tau is set by the white-dwarf radius and the orbital speed:
- For M_WD = 0.25 Msun and M2 = 0.15-0.20 Msun, a = 0.64-0.67 Rsun.
- That gives tau = 70-105 s for R_WD = 0.018-0.026 Rsun.

This interval is shorter than one 2-min exposure. The total duration T14 then constrains the companion radius and inclination jointly. Many eclipses with continuous coverage also yield mid-eclipse times for a period-change baseline, extending ATLAS (2015-2026) and TESS FFI coverage (S10, S37, S63, S64) plus S90 and S99.

These data alone do not give masses: radial velocities are needed. The proposal's product is a photometric radius constraint and an eclipse ephemeris. Ground-based high-speed photometry on a 2-4 m telescope would measure a single eclipse with higher precision. TESS contributes ~1,100 consecutive eclipses over four sectors at no additional cost per eclipse.

## 3. Target Justification and Feasibility

**Pointing.** We checked the pointing with tess-point 0.9.5.post1; the Year 9 pointings match the tess.mit.edu sector pages.

| sector | dates | camera/CCD | col, row |
|---|---|---|---|
| 111 | 2026-11-26 – 12-22 | 4/3 | 923, 1308 |
| 112 | 2026-12-22 – 2027-01-17 | 4/2 | 432, 225 |
| 113 | 2027-01-17 – 02-13 | 3/2 | 617, 1519 |
| 114 | 2027-02-13 – 03-14 | 2/1 | 263, 1240 |

**Feasibility from existing TESS data.** We tested this on the archival SPOC light curves, folded on the ATLAS ephemeris. We used SAP flux, quality = 0 and 0.25-d median detrending, then fitted a trapezoid with exposure smearing. The errors are from the covariance matrix and assume white noise.

| data | eclipse depth (aperture) | mid-eclipse offset | T14 | ingress tau |
|---|---|---|---|---|
| S90 20 s | 0.93 +- 0.04% | +14 +- 4 s | 394 +- 19 s | **79 +- 17 s** |
| S90 2 min | 0.91 +- 0.04% | +12 +- 5 s | 422 +- 42 s | 91 +- 44 s |
| S99 2 min | 1.83 +- 0.08% | +4 +- 4 s | 442 +- 32 s | 126 +- 34 s |

- The eclipse is detected in every TESS sector stack. The mid-eclipse time is measured to about 4-5 s per sector at either cadence. Ingress is constrained only at 20 s, where the error is a factor of ~2.6 smaller than at 2 min for the same sector.
- Four more 20-s sectors would reduce the ingress error to about +-8 s, by sqrt(5) scaling from S90. That is roughly a 10% constraint on R_WD at fixed orbital geometry, compared with about 20% now.
- Individual eclipses are not detected: per-eclipse S/N is about 1. The result relies on stacking.

**Crowding.** The field is crowded (b = +5.7 deg). SPOC CROWDSAP is 0.008 (S90) and 0.021 (S99), so most aperture flux is from neighbours; the nearest Gaia sources are G 19.6 at 2.6 arcsec and G 18.7 at 5.7 arcsec. Dilution scales the eclipse depth only. Timing, T14 and ingress duration come from the shape of the stacked eclipse and do not depend on the crowding correction. However, contaminating flux sets the noise. The PDCSAP point-to-point scatter is about 2x the target flux per 20-s point.

There are no sources brighter than T = 7 in the request. Number of targets: 1 (20 s).

## 4. References

- Parsons S. G. et al. 2017, MNRAS 470, 4473 (eclipsing WD+dM radii)
- Gentile Fusillo N. P. et al. 2021, MNRAS 508, 3877 (Gaia EDR3 WD catalogue)
- Tonry J. L. et al. 2018, PASP 130, 064505 (ATLAS)
- Burke C. J. et al. 2020, tess-point, ASCL 2003.001
- Gaia Collaboration 2023, A&A 674, A1 (DR3)

---

### Notes for the PI (not part of the proposal)

1. **Before sending,** re-check the S90 20-s fit with a red-noise treatment, such as a residual-permutation or bootstrap test. The ingress errors above assume white noise. The two 2-min sectors differ in T14 and tau at roughly the 1-sigma level. Also, the S99 aperture depth is twice the S90 depth: that is a different aperture and crowding, as expected.
2. Verify the MWDD log g and mass that you cite. The journal gives 0.25 Msun from MWDD, and the GF21 values may differ.
3. Check the four references against ADS before citing them; they were written from memory and are not verified.
4. A VSX entry for this object is drafted but not filed. A DDT approval makes the target list public, with no proprietary period. Filing VSX first sets the timestamp.
5. If the template's "why not the GI call" wording needs it: Cycle 10 proposals do not cover S111-S114.
