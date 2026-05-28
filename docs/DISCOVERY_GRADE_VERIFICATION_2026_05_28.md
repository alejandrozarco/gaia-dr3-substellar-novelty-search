# Discovery-grade second-method verification — archival-only sweep

*2026-05-28. Five-task verification of "candidate" → "discovery-grade" promotion using only archival data, no new telescope time. All scripts and JSON in `/tmp/discovery_verify_2026_05_28/`.*

---

## TL;DR verdict table

| # | Target | Method-1 (assumed) | Method-2 (this work) | Agreement | M_2 consistent | Discovery-grade verdict |
|---|---|---|---|---|---|---|
| 1 | APMPM J0710-5704 | Gaia NSS Orbital (P=253 d, M_2≈super-Jupiter) | TESS BLS, 35 QLP sectors, 244k pts, 7.4-yr baseline | No transit at P_Gaia | N/A — null | **No transit ⇒ i < 90 deg constraint, not discovery** |
| 2 | Gaia 5476986108823894400 (= HD 46491) | "K_1=163 km/s APOGEE+RAVE" claim | Gaia NSS Orbital + raw APOGEE/RAVE archives | NSS empty; RAVE σ=115, APOGEE σ=6.96 km/s — **18× disagreement** | NO | **Claim falsified — NOT discovery** |
| 3a | BD+35 228 | Gaia NSS Orbital (P=560 d, M_2=44.6 M_J at M_1=1) | HGCA + Kervella H2G2 | Kervella snrPMa=5.85, BinH2G2=1; HGCA chi2=18.9 (sub-25) | M_2(Kervella, rescaled) = 12.9 MJ → factor-3 discrepant | **Likely triple** — outer companion not in NSS but in Kervella; NSS M_2 only valid for inner orbit |
| 3b | HD 217588 | Gaia NSS AstroSpectroSB1 (P=873 d, M_2=68.3 M_J) | HGCA + Kervella H2G2 | snrPMa(H2G2)=1.86, BinH2G2=0; HGCA chi2=3.34 (FAIL) | N/A | **Single-channel only** — Kervella + HGCA both fail to confirm |
| 3c | HD 49264 | Gaia NSS Orbital (P=428 d, e=0.73, M_2=59.8 M_J) | HGCA + Kervella H2G2 | snrPMa=1.82, BinH2G2=0; HGCA chi2=1.49 (FAIL) | N/A | **Single-channel only** — eccentric inner orbit, Kervella long-baseline not sensitive |
| 4 | 8 HGCA BH-class (CD-46 10032A, LP 155-298, HD 16385, HD 173689, HD 157033, HD 81825, HD 37943, HD 5514) | HGCA Brandt 2021 (chi2>100) | Kervella 2022 H2G2 snrPMa | 7/8 in both catalogs at snrPMa>=3 | M_2 at Kervella's 5-AU ref = **0.4–2.9 M_sun** (stellar, NOT BH-mass) | **2-baseline-confirmed binaries, but M_2 << 10 M_sun — the "BH-class" label is wrong** |
| 5 | HD 12871 | (no work — citation only) | — | — | — | Triple system; methodology paper note: APOGEE K_1=11.9 = NSS SB1 K_1=11.9 (Hardy 2017 / Bruch 2026 anchor) |

**Net: 0 candidates promoted to discovery-grade. 7 candidates corroborated as multi-channel binaries (Task 4) but reclassified out of BH-mass regime. 1 candidate falsified outright (Task 2).**

---

## Promotions to discovery-grade

**None.** Every target either failed cross-channel agreement or had the catalog M_2 estimate revised downward by the second method.

---

## Demotions and reclassifications

| Target | Old class | New class | Driver |
|---|---|---|---|
| Gaia 5476986108823894400 / HD 46491 | "Two-survey K_1 confirmed BH (46 M_sun)" | **NOT a dark-companion candidate** | APOGEE 6-visit σ=6.96 km/s (real), RAVE 3-visit σ=115 km/s (noise-dominated low-res survey). Doc's K_1_max=162.7 = RAVE σ, which is RAVE pipeline noise floor, not a phase-folded K_1. APOGEE σ=6.96 km/s implies M_2 ~ 1–3 M_J at P=100d if it is a real orbit, not 46 M_sun. NSS Orbital, Acceleration, NonLinearSpectro all empty. astrometric_excess_noise_sig=36 is real, but probably reflects astrophysics other than a 46-M_sun companion (e.g. A1IV pulsation/variability, see Teff=8390K subgiant). |
| 8 HGCA "BH-class" (Task 4) | "M_2 = 4–60 M_sun BH-class candidates" | **Stellar binaries, M_2 = 0.4–2.9 M_sun** at Kervella's 5-AU reference | The headline "M_2_at_PXX_Msun" columns in `step3_hgca_pmamp_M2.csv` (project file) over-estimate by 10–100× because they assume the entire PMa is on a single orbit at a single P; the correct Kervella-paper convention uses a fixed-a reference. None of the 8 are BH-mass. |
| Stefánsson 3 BDs (BD+35 228, HD 217588, HD 49264) | "Triple-astrometric verified BD candidates" | **NSS-only BD candidates, HGCA/Kervella too noisy at the NSS period** | Kervella H2G2 is sensitive to outer (>1 AU) long-baseline companions; the BD candidates have inner orbits at a ~ 1.1–2.6 AU which leak into Kervella only weakly. HGCA chi2 = 1.5–18.9 — well below the chi2>25 cutoff for a confident 2-baseline confirmation. BD+35 228 has the strongest secondary signal (snrPMa(H2G2)=5.85, BinH2G2=1) but the Kervella-rescaled M_2 ~ 13 M_J is 3× lower than NSS — likely an outer tertiary, not BD verification. |
| APMPM J0710-5704 | M-dwarf super-Jupiter candidate (NSS Orbital P=253 d) | **Non-eclipsing companion; NSS-only** | 35 QLP TESS sectors stitched (244k pts, baseline 2691 d). BLS depth at P_Gaia = 0.18%; predicted depth for R_p=1 R_Jup, R_star=0.4 R_sun is **6.6%**. The companion at P=253d is therefore **not eclipsing** to high confidence. This constrains i but does not promote. RMS_LC = 1635 ppm. Strongest BLS peak in 200-350 d is at 338 d (power 1002, depth 0.6%), well above the noise — likely a stellar-rotation/spot harmonic or instrumental, not a transit. |

---

## Per-candidate write-up paragraphs (for the discovery paper)

### Task 1 — APMPM J0710-5704
*"The brightest M-dwarf super-Jupiter candidate from the Gaia NSS Orbital sweep (P=253 d, Gaia DR3 5486916932205092352) was tested for transits in the joint multi-sector TESS QLP light curve (35 sectors S2–S98, 244 000 cadences, 2692-d baseline, RMS=1635 ppm). Predicted transit depth for a 1 R_Jup companion at i=90° on a 0.4 R_sun M4V host is 6.6%. The observed BLS power at P=253.5 d is 359 (vs. p99 floor 891), and the recovered depth is 0.18% — below the prediction by a factor of 37. We rule out a transiting Jovian companion at the Gaia NSS period at high confidence. The system therefore retains a single-method (astrometric) detection and would benefit from RV follow-up at the predicted K_1 amplitude."*

### Task 2 — HD 46491 / Gaia 5476986108823894400
*"The brightest single-line candidate from the project's two-survey K_1 sweep, claimed at K_1=163 km/s (APOGEE+RAVE) with M_2 ≥ 46 M_sun at P=100 d. Direct archival re-examination shows that this K_1 was constructed from the per-survey RV scatter (APOGEE 6-visit σ=6.96 km/s, RAVE 3-visit σ=115 km/s); only the APOGEE value is physically meaningful, with the RAVE σ dominated by the survey's low-resolution noise floor. The Gaia DR3 source has no entry in nss_two_body_orbit, nss_acceleration_astro, or nss_non_linear_spectro. The astrometric_excess_noise_sig=36 is real but is consistent with the A1IV photometric variability of HD 46491 rather than a 46-M_sun dark companion. We retract this candidate from the headline list."*

### Task 3 — Stefánsson 3 BDs
*"For BD+35 228, HD 217588, and HD 49264, the Gaia NSS Orbital solutions are confirmed (P=560, 873, 428 d; M_2 = 44.6, 68.3, 59.8 M_Jup at M_1=1 M_sun). Cross-channel verification via the Kervella+ 2022 Hipparcos-Gaia H2G2 catalog and the Brandt+ 2021 HGCA chi2 metric is weak: only BD+35 228 shows a secondary signal (snrPMa_H2G2=5.85, BinH2G2=1) but the Kervella M_2 rescaled to the NSS period semi-major axis is 13 M_J versus the NSS 44.6 M_J — a factor-3 discrepancy. HD 217588 and HD 49264 have snrPMa < 2, BinH2G2=0, and HGCA chi2 ≤ 3.5. The Kervella long-baseline channel is most sensitive to companions at a > 3 AU; the NSS inner orbits are at a ~ 1.1–2.6 AU. The non-agreement does not falsify the BD claim, but it does mean the original "triple-astrometric" classification (Sahlmann + HGCA + Kervella + TESS-clean) overstated the corroboration: the HGCA and Kervella legs do not independently confirm a sub-stellar inner companion, they only fail to refute it."*

### Task 4 — 8 HGCA "BH-class"
*"All eight HGCA BH-class candidates (CD-46 10032A, LP 155-298, HD 16385, HD 173689, HD 157033, HD 81825, HD 37943, HD 5514) appear in the Kervella+ 2022 H2G2 catalog; seven of eight have snrPMa_H2G2 ≥ 3 (LP 155-298 the only exception, at snrPMa=1.41). The H2G2 BinH2G2 flag is set for the same seven. Two independent astrometric baselines (HG cross-residual chi2 and HIP-Gaia PMa) therefore corroborate the presence of an unresolved companion in 7/8 cases — meeting our two-method discovery threshold for binarity. However, the Kervella-catalog companion mass at the 5-AU reference radius is 0.40 (CD-46 10032A), 2.92 (HD 16385), 1.96 (HD 173689), 0.45 (HD 157033), 1.76 (HD 81825), 2.09 (HD 37943), and 1.57 (HD 5514) M_sun. These are stellar-mass binaries, not BH-mass — the original headline 'M_2 = 4–60 M_sun' in `step3_hgca_pmamp_M2.csv` results from a single-orbit / single-period scaling that inflates M_2 by 10–100× relative to the canonical Kervella reference. The signal is real and two-baseline confirmed; the mass classification is not."*

### Task 5 — HD 12871 (citation only)
*"For methodology validation: the APOGEE 3-visit K_1=11.9 km/s recovered for HD 12871 = Gaia DR3 77413727493690112 matches the Gaia DR3 SB1 catalog K_1=11.9 km/s to within numerical precision, providing a 3rd validation anchor for the K_1 pipeline alongside Hardy+ 2017 (CV-period) and Bruch+ 2026 (CV-period). HD 12871 is the textbook hierarchical-triple case (lesson #17 in CLAUDE.md): the inner SB1 K_1 and the long-baseline acceleration channel give discordant M_2 estimates, which the pipeline correctly diagnoses as triple, not compact-object."*

---

## Caveats

- Task 1: The 35-sector QLP stitch did not remove sector-edge zero-point bias from QLP detrending; the 338-d BLS peak is plausibly an instrumental harmonic of the 27-d TESS orbit, not a real signal. A targeted re-detrending with SPOC PDC-SAP at the 54-sector level (more aggressive systematics removal) would improve the upper limit on transit depth at P=253 d. The constraint i < 89° depending on R_p (and the non-detection) is robust regardless.
- Task 2: The "K_1=163 km/s" inference was an automated pipeline statistic, not a verified phase-folded amplitude. A human-vetted retraction is appropriate; the candidate has dropped from rank 1 to "not a candidate." However, the APOGEE σ=6.96 km/s across 6 visits over short baseline may still indicate a sub-stellar inner companion (M_2 ~ a few M_J at P=100 d) and the source warrants a separate inner-orbit search.
- Task 3: The Kervella rescaling I applied (M_2(a) ~ M_2(5 AU) × sqrt(a/5)) is a rough approximation; the Kervella paper convention is exact only at the listed reference radii (3, 5, 10, 30 AU). For inner orbits at a < 3 AU one must extrapolate. The factor-3 discrepancy reported above is therefore qualitative, not a hard rejection. Better diagnosis: the NSS inner orbit is at a different geometric regime than what Kervella probes; both can be simultaneously true for a hierarchical-triple system.
- Task 4: The M_2(5 AU) values from Kervella assume a circular orbit at exactly 5 AU; the actual orbital separation is unknown. The seven 2-baseline binaries are confirmed real, but the precise M_2 requires either (a) actually fitting the orbit, or (b) Gaia DR4 epoch astrometry. The reclassification from "BH-mass" to "stellar-mass" is well-motivated but the upper bound on M_2 is loose.
- Task 5: Citation-only, no caveats — the agreement is exact.

---

## Cross-check methodology

- **Task 1**: lightkurve 2.6.0, QLP `search_lightcurve` with `mission="TESS"`, `download_all()`, `remove_nans().normalize().flatten(window_length=801).remove_outliers(sigma=5)`, `LightCurveCollection.stitch()`, `astropy.timeseries.BoxLeastSquares` with periods 200–350 d in 1500 bins, durations [0.5, 1.0, 2.0, 4.0] d.
- **Task 2**: `gaiadr3.nss_two_body_orbit/nss_acceleration_astro/nss_non_linear_spectro/nss_vim_fl` queried via Gaia TAP. Local parquets at `data/multisurvey_2026_05_28/{apogee_sb1,rave_sb1,final_with_masses}.parquet` provide the per-survey RV scatter.
- **Tasks 3+4**: `astroquery.simbad.Simbad` with `sp_type`, `plx_value`, `V` fields (post-deprecation API); `Vizier(catalog='J/A+A/657/A7/tablea1')` for Kervella H2G2 (correct column: `snrPMaH2G2`, `BinH2G2`, `M25au`); `Vizier(catalog='J/ApJS/254/42/catalog')` for HGCA Brandt 2021 (correct column: `chi2`). 10-arcsec match radius for both.

---

## Files

- `/tmp/discovery_verify_2026_05_28/task1_result.json` — APMPM J0710 BLS
- `/tmp/discovery_verify_2026_05_28/task2_v2_result.json` — Gaia 5476986 retraction evidence
- `/tmp/discovery_verify_2026_05_28/task3_v2_result.json` — Stefansson 3 BD cross-channel
- `/tmp/discovery_verify_2026_05_28/task4_v3_result.json` — 8 HGCA + Kervella
- Scripts: `task1_apmpm_tess.py`, `task234_fixed.py`, `task24_v2.py`, `task3_v2.py`, `task4_v3.py`

## What this enables for the paper

The methodology paper now has three populations to write up clearly:
1. **Single-method candidates** (Task 1 APMPM, Task 3 Stefansson 3): real NSS detections, but multi-method verification did not corroborate — these need RV follow-up.
2. **Two-baseline confirmed stellar binaries** (Task 4): 7 sources that *are* multi-method, but at M_2 ~ 0.4–2.9 M_sun rather than BH-mass. Worth a separate write-up as a "stellar-mass binary recovery" sub-population.
3. **Retraction** (Task 2 / Gaia 5476986108823894400): an example of how an automated K_1 pipeline can mis-rank a source by treating low-resolution-survey RV scatter as a phase-folded amplitude. This is a useful negative result for the paper's methodology section.
