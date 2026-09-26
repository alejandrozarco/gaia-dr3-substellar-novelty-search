## Verdict

**Send a revised coordination email, not the present classification claim.** Photospheric carbon is convincing. A **DQ/DQA-like optical spectrum with probable hydrogen** is defensible; a carbon-dominated atmosphere, an 18–24 kK temperature, and a merger origin remain unproved. A hydrogen-dominated, carbon-bearing atmosphere has **not been quantitatively excluded**.

The most consequential new findings are:

- Several advertised optical carbon features have quality flags.
- COS C III 1247 loses its photospheric centre in one exposure.
- **Lyα’s centre is masked in the combined COS spectrum.**
- Si II 1260 contains a near-zero-velocity component; it is not established as photospheric silicon.
- Sahu’s **August 2026 EuroWD presentation explicitly reports carbon/silicon analysis of 427 COS DA spectra**. That materially changes the courtesy framing.

I inspected the supplied files and recomputed spectral diagnostics without modifying files.

## Blocking issues — must fix before sending

1. **Separate spectral appearance from atmospheric composition.** Replace “we therefore regard it as a hot DQ” with “the optical spectrum appears DQ/DQA-like; atmospheric composition and temperature are unfitted.” Do not imply that “DAQ” necessarily means hydrogen dominates by number.

2. **Remove unsupported precision and universal statements.** “Common velocity” needs qualification; “same colour and absolute magnitude” overstates the control matching; “show no variability” overstates the timing results.

3. **Correct any accompanying figures.** Break the COS trace across missing wavelengths, identify the Lyα gap, distinguish laboratory from observed wavelengths, and remove “sigma” from the CCF legend. The seven earlier corrections were not fully propagated into the draft and figures.

4. **Acknowledge current work explicitly.** The proposed recipients are conducting precisely the relevant UV abundance analyses. Frame the email around potentially useful **optical evidence**, not an assumed overlooked discovery.

A joint atmosphere fit is necessary before claiming carbon dominance or rejecting a hot DA interpretation. It is **not necessary before sending the corrected inquiry below**.

## Alternative interpretations tested — with numbers

My profile fits are descriptive measurements, not atmosphere fits. Their formal errors omit continuum, blending and resampling systematics.

| Test | Reanalysis | Implication |
|---|---|---|
| Optical C II 4267 complex | Vacuum centroid **4269.26 Å**; fitted EW **2.47 Å**, FWHM **8.45 Å** | Strong, resolved carbon absorption in an unflagged region. |
| Carbon near Hα | Simultaneously fitting hydrogen and carbon gives carbon EW **2.7–3.0 Å**, versus **1.30 Å** from the dossier’s isolated fit | The isolated carbon EW is biased by its treatment of neighbouring Hα and continuum. |
| Hα | Two-Gaussian fits give centroid **6566.24–6566.54 Å**, FWHM **15–18 Å**, EW **3.7–4.6 Å** | Supports hydrogen; reproduces the earlier identification. |
| Hβ | Local fits give depth **15–16%**, FWHM **31–33 Å**, EW **5.0–5.5 Å**, centre **4864.3–4864.8 Å** | A substantial additional hydrogen candidate, omitted from the email. |
| Hγ | No convincing absorption centred at the expected wavelength | For an assumed 33 Å Gaussian profile, a conditional formal 3σ EW limit is approximately **1.1 Å**. This is not a general atmosphere-model limit. |
| Hδ | Weak and sensitive to carbon masking and continuum | A fixed 33 Å profile gives EW approximately **0.9 Å**; allowing broad wings makes the result poorly constrained. |
| Hε | Carbon blends compromise the diagnostic | No trustworthy standalone hydrogen EW. |

**Does this exclude a 28–35 kK, log g ≈9 DA?** No quantitative exclusion has been achieved. Hβ’s width alone does not exclude one. The weak higher Balmer series creates tension with an ordinary hydrogen spectrum, but the percentile normalization suppresses broad structure and the blue spectrum is crowded.

**Specific limitation:** no suitable synthetic atmosphere grid was supplied, and attempted external model retrieval failed. I therefore cannot honestly supply predicted DA equivalent widths, a model χ² comparison, or a carbon-abundance threshold. Those are missing tests, not negative results.

**Could trace carbon produce the optical spectrum?** Routine UV metal detections are an inadequate explanation by themselves. Hot hydrogen-atmosphere stars can contain photospheric carbon through accretion and radiative support, and observed abundances need not follow simple levitation predictions. [Barstow et al. 2014](https://arxiv.org/abs/1402.2164)

The relevant counterexample is WD 0525+526: **20,820 K, log g 9.05, log(C/H)=−4.62**, with carbon detected in the UV but absent optically. Your several-Å optical features are substantially different. This makes an ordinary trace-pollution interpretation less persuasive, but **does not establish a numerical C/H lower bound at 28–35 kK**. Also, Sahu’s rejection of levitation for that cooler star cannot simply be transferred here. [Sahu et al. 2025](https://arxiv.org/html/2508.03811v1)

Classification letters do not settle this: published DAQs can have carbon-dominated compositions. Kilic’s J2057−3425 has strong optical C II and a fitted temperature **22,916±1,117 K**. [Kilic et al.](https://arxiv.org/html/2507.12655v1)

**Temperature consistency.** C II plus C III is compatible with a hot-DQ interpretation, but the EW ratio is not an ionic abundance ratio: excitation, saturation, density and atmospheric depth matter. Photospheric Si II has not been established, so it cannot currently serve as a low-temperature constraint.

The measured pseudo-continuum ratio is approximately

\[
F_\lambda(1165)/F_\lambda(1410)=0.255.
\]

Blackbodies give approximately **0.79, 0.97, 1.21 and 1.37** at 18, 22, 28.6 and 35 kK. Interpreting the observed ratio as a blackbody would yield an implausible **9.2 kK colour temperature**. This demonstrates that these windows are not an unobscured continuum thermometer; it does not measure \(T_{\rm eff}\). Even DA COS spectra can lack undisturbed continuum because of Lyman opacity. [Koester et al. 2014](https://discovery.ucl.ac.uk/id/eprint/1477440/1/Farihi_aa23691-14.pdf)

**Preferred interpretation:** carbon-bearing white dwarf, DQ/DQA-like optical morphology, probable hydrogen. Hydrogen-dominated mixed/stratified atmospheres, a composite spectrum, and magnetism remain alternatives requiring modelling or further observations.

## Data-quality findings

**BOSS**

- The file contains **one 900 s exposure**, not merely one visit potentially assembled from several exposures. Stored S/N is **16.65**, airmass **1.59**, and `in_stack=True`.
- Multiplying the grid by \(1+178.4339/c\) correctly reverses the stored XCSAO shift and restores **vacuum barycentric wavelengths**. It does not produce topocentric wavelengths. Do not apply another barycentric correction. [Astra conventions](https://sdss-astra.readthedocs.io/en/latest/user/datamodels/products.html)
- The five blue carbon regions through 4622 Å are unflagged. Restricting the CCF to unflagged pixels retains a peak at **+100 km/s**, with contrast **13.9**; blue-only gives **13.2**. These remain contrasts, not calibrated significances.
- Their individual centroids give approximately **+86.5 km/s**, with scatter-inflated uncertainty **19 km/s** before additional systematics. Thus “roughly +90 km/s apparent photospheric velocity” survives.

| Region | Actual concern |
|---|---|
| 5892 Å carbon complex | `BADSKYCHI`, rejection and flat-field flags occur nearby. The Na D sky line lies within the broad feature’s neighbourhood. Do not use this as a clean velocity anchor. |
| 6783 and 7237 Å complexes | Throughout the inspected windows, mask **83886080** includes `BADFLUXFACTOR` and deprecated `NODATA`. Positive inverse variance does not erase the calibration warning. |
| Blue carbon lines and Hα/Hβ | Inspected windows have zero pixel flags. |

These are **BOSS SPPIXMASK** meanings; the similarly named MaNGA mask has different bit assignments. [SDSS mask definitions](https://www.sdss.org/dr19/data_access/bitmasks/)

The supplied Astra product lacks the original sky spectrum and detector-level exposures. It cannot establish the absence of sky residuals or validate absolute spectrophotometry. Nevertheless, the clean blue features make a purely instrumental carbon explanation untenable.

**COS**

There are two **900.192 s** exposures, FP-POS **3 and 4**, G130M/1291, **lifetime position 5**.

| Feature | FP-POS 3 EW | FP-POS 4 EW |
|---|---:|---:|
| C III 1175 | **1.59±0.10 Å** | **1.63±0.10 Å** |
| C II 1324 | **0.55±0.06 Å** | **0.60±0.05 Å** |
| C II 1335 blend | **2.43±0.10 Å** | **2.56±0.09 Å** |

Errors here exclude continuum uncertainty. These detections repeat at different detector positions.

- **C III 1247:** FP-POS 4 masks **1247.630–1247.989 Å**, including the expected stellar centre. DQ=1040 denotes low/very-low response. Its apparent coadded core is therefore supported principally by FP-POS 3, not two independent exposures.
- **Lyα:** the coadd has zero weight from **1214.776–1216.181 Å**, flagged as a gain-sag hole. Both rest Lyα and Lyα at +90 km/s fall inside. The plotting script joins valid samples across this gap, creating an unmeasured connecting trace. [COS DQ documentation](https://hst-docs.stsci.edu/cosdhb/chapter-2-cos-data-files/2-7-error-and-data-quality-arrays)
- Illustrative coadded fits give **C III 1247 ≈+75 km/s**, **C II 1324 ≈+81 km/s**, but narrow **C II 1334 ≈+1 km/s** and **Si II 1260 ≈+7 km/s**. The latter two support an interstellar component. Si II 1265 is not convincingly detected.
- The exact **+96 km/s C II 1335.7 minimum** is a fragile velocity anchor: the depression is structured and the second exposure poorly constrains its centroid. Prefer the excited 1324 and 1247 features.
- N V fails a convincing doublet test; Si IV remains tentative.
- The conspicuous emission near **1200 Å** is consistent with N I airglow and needs labelling alongside O I 1302–1306. Day/night separation cannot be performed from these extracted spectra alone. [COS background handbook](https://hst-docs.stsci.edu/display/COSIHB/7.4%2BDetector%2Band%2BSky%2BBackgrounds)
- COS has a non-Gaussian LSF. Use the **LP5** kernel for component/abundance fitting; the Gaussian centroids above are diagnostic only. [COS LSF documentation](https://hst-docs.stsci.edu/cosihb/chapter-3-description-and-performance-of-the-cos-optics/3-3-the-cos-line-spread-function)

## Scoop/prior-work search log

Search date: **25 September 2026**.

| Search | Finding |
|---|---|
| HST 17420 proposal | **“A legacy survey for evolved planetary systems within 100pc.”** Its aim is atmospheric pollution from planetary debris, targeting roughly 15–30 kK stars. It is not specifically a massive-merger carbon survey. The target is labelled DA, with FUV **15.95** versus synthetic **14.80**. [Proposal, pp. 8–9 and 154](https://www.stsci.edu/hst/phase2-public/17420.pdf) |
| **EuroWD, August 2026** | Sahu’s abstract describes **427 COS DA spectra**, including C/Si analysis across the sample and treatment of radiative levitation. No “0735” or Gaia-ID match found. This is strong evidence of relevant ongoing work, not proof that this object was identified. [Abstract booklet, p. 48](https://eurowd-2026.pages.ist.ac.at/wp-content/uploads/sites/351/2026/08/EuroWD-2026-_-Abstract-Booklet-compressed.pdf) |
| Sahu 2025 and follow-ups | The merger paper concerns **WD 0525+526, program 15073**, not this target. The other 2025 result concerns volatile-rich accretion. [Research page](https://warwick.ac.uk/fac/sci/physics/research/astro/people/snehalatasahu/) |
| Program-associated publication | Ould Rouis et al. acknowledge **17420 funding**, but their listed observations belong to earlier programs. A funding acknowledgement is not publication of this target. [Paper](https://wrap.warwick.ac.uk/id/eprint/188178/7/Ould_Rouis_2024_ApJ_976_156.pdf) |
| 2026 literature | Examined García-Zamora’s hot-DQ survey and Warwick’s UV white paper; neither identifies this star. [Survey](https://arxiv.org/html/2605.16493v1), [white paper](https://arxiv.org/html/2605.26152v1) |
| Aliases, ADS/arXiv, AAS-indexed material | No object-specific carbon classification surfaced. **Direct ADS search access failed**; web-indexed searches are not an exhaustive ADS full-text audit. Local paper-source searches recovered the Bravo companion discussion. [Bravo et al.](https://arxiv.org/html/2412.04597v1) |

**Courtesy conclusion:** assume the team may already be analysing it. Do not assert either that they missed it or that they certainly recognised it.

## Email audit — claim by claim

| Draft claim | Assessment / correction |
|---|---|
| Identity, Gaia ID, 96 pc | Correct: parallax implies **96.38 pc**. |
| “Listed as DA” in 17420 | Correct. This is a target-list classification, not evidence of a satisfactory resolved DA spectrum. |
| “Strong C II absorption” | Supported by multiple clean blue features. |
| Single LCO visit, MJD 60695, ID | Correct; specify one **900 s exposure** if useful. |
| Nine wavelengths “near…” | Ambiguous mixture of nominal laboratory designations and observed centres. For example, 4268.40 vacuum is fitted at **4269.26**, and 7236.73 at **7240.40 Å**. Use a few named complexes instead. |
| “At a common velocity” | Too tidy. Use **“approximately +90 km/s, with substantial line-to-line scatter.”** This includes gravitational redshift. |
| Broad Hα; no obvious He I | Reasonable. Add **Hβ**, while retaining “probable hydrogen.” |
| COS identity/date | Correct. |
| All UV lines “at a similar velocity” | Qualify: 1247/1324 support the stellar velocity; 1175/1335 are blends, and 1247 has incomplete exposure redundancy. |
| Narrow C II core “looks interstellar” | Reasonable, strengthened by near-zero-velocity Si II 1260. |
| FUV−NUV +0.32 | Correct: **+0.315±0.020**, statistical error. |
| “Same colour and absolute magnitude” | Overstated. The 16 controls span **\(M_G=11.34–12.81\)** and BP−RP **−0.486 to −0.311**. Say “16 broadly matched DA controls,” or omit. |
| “Redder than every…” | True only for the selected comparison sample; its maximum is **−0.132**. GALEX artifact/blending checks remain incomplete. |
| FUV deficit “noted” in target list | The two magnitudes are recorded; there is no explicit physical interpretation attached. |
| “TESS … and SkyMapper show no variability” | Incorrectly categorical. Say **“no secure variability detected in the analyses performed.”** TESS crowding fractions are only **0.12–0.39**. Prefer omission. |
| “Therefore … hot DQ” | Replace with morphology-based candidate language. |
| Composition, temperature, mass open | Correct; retained. |
| No publication in catalogues/ADS/~60 papers | Mixes classifications, publications and unequal search coverage. Use **“I have not located a published carbon-rich classification.”** |
| “Since the COS data are yours” | Replace with “given its inclusion in your programme and your ongoing COS analyses.” |
| Offer measurements/collaboration | Appropriate. The scripts currently contain external hard-coded paths, so prepare a portable package before offering them as reproducible. |
| Promise not to publish independently | Unnecessary for courtesy. Include only if it reflects a deliberate commitment. |

**Corrected draft**

> **Subject:** WDJ073504.07−794410.69: optical carbon absorption in a SNAP 17420 target
>
> Dear Professor Gänsicke, Dr Sahu and Dr Bédard,
>
> I am an independent amateur researcher analysing public survey spectra with AI-assisted tools. In SDSS-V DR20 I noticed strong optical carbon absorption in WDJ073504.07−794410.69 (Gaia DR3 5208047381438507520; approximately 96 pc), listed as DA in SNAP 17420.
>
> Its single 900 s BOSS/LCO exposure on MJD 60695, sdss_id 95077848, contains several convincing C II features, including the 4267 Å complex. The clean blue features suggest an apparent photospheric velocity around +90 km/s, with substantial line-to-line scatter. Absorption near Hα and Hβ suggests hydrogen.
>
> The public COS dataset lfac0z010 supports photospheric carbon through C III 1175 and excited carbon features. C III 1175 and C II 1324 repeat in both FP-POS exposures; C III 1247 has incomplete coverage in one exposure. The narrow C II 1334 core appears to include interstellar absorption.
>
> The optical spectrum looks DQ/DQA-like, but I have not fitted atmosphere models or excluded a hydrogen-dominated carbon-bearing atmosphere. Its composition, temperature and mass therefore remain undetermined.
>
> I saw your recent EuroWD presentation on the COS abundance survey and realise this object may already be under investigation. I have not located a published carbon-rich classification. Would the optical measurements be useful to your ongoing analysis? I would be happy to share the measurements and checks and contribute to coordinated work if helpful.
>
> Best regards,  
> [sender]

## Remaining risks

- **No atmosphere-model comparison yet:** neither carbon dominance nor a levitation/accretion explanation has been demonstrated.
- **No robust photospheric C/Si ratio:** the key test distinguishing carbon enrichment from ordinary pollution remains missing.
- **No merger diagnosis:** the measured proper motion implies only approximately **4.4 km/s transverse speed**, providing no high-velocity argument; systemic radial velocity is unknown.
- One optical exposure cannot establish stability, exclude an unresolved composite, or constrain magnetism adequately.
- Catalogue classifications and unpublished team work remain incompletely accessible. The revised email appropriately asks about this uncertainty.