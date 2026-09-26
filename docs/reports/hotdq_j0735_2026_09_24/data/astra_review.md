## Verdict with confidence

**The carbon detection survives scrutiny; the full claim is too strong.** I have very high confidence that this is a white dwarf with photospheric carbon and that an ordinary DA classification is inadequate. **A provisional hot DQ/DQA classification is justified; a demonstrably carbon-dominated atmosphere is not yet established.**

I found no prior DQ/carbon-rich classification in the material searched. That supports “apparently previously unreported,” not an absolute claim that none exists.

I reproduced the optical measurements, COS equivalent widths, GALEX comparison, combined 120-second TESS result, and SkyMapper statistics. No files were modified.

## Errors found

1. **The WISE comparison mixes AB and Vega magnitudes.** Legacy’s W1=19.6727 and W2=20.2083 become **16.9737 and 16.8693 Vega**, close to CatWISE’s 17.083 and 16.985. The apparent multi-magnitude discrepancy therefore disappears. Blending remains possible, but these numbers do not demonstrate it. [Legacy DR10 photometric conventions](https://www.legacysurvey.org/dr10/description/).

2. **“17.5 sigma” is not a calibrated detection significance.** In [spec_lines.py](/tmp/hotdq/dd/spec_lines.py), it is peak contrast relative to off-peak CCF scatter. Correlated velocity trials, template selection and spectral structure are not included in a false-alarm calculation. Moreover, NIST laboratory intensities are not predicted white-dwarf absorption strengths. The hydrogen template includes numerous Paschen lines and assumes 4 Å profiles: its weak CCF **cannot exclude broad Balmer absorption**. Nevertheless, the many individual C II matches are convincing.

3. **The ±6 km/s velocity precision is misleading.** I reproduce +92.6 km/s and χ²=47.6 for eight degrees of freedom; the common-velocity model has \(p\simeq1.2\times10^{-7}\) under the adopted errors. Simple error inflation already gives approximately ±14 km/s, before systematic centroid errors from multiplet weights, pressure shifts and blends. Agreement with a gravitational redshift inferred from a **DA-model mass** is not independent mass evidence; systemic radial velocity is also unknown. I found no gross optical air/vacuum or correction-sign error: the adopted reversal agrees with the documented vacuum, rest-frame Astra products. [Astra conventions](https://sdss-astra.readthedocs.io/en/latest/user/datamodels/products.html).

4. **COS uncertainties omit the dominant continuum ambiguity.** The quoted EWs reproduce exactly, but [cos_look.py](/tmp/hotdq/cos/cos_look.py) treats a constant, locally estimated continuum as exact. Changing reasonable sidebands moves C II 1335 from **1.78 to 2.56 Å**, versus its quoted ±0.059 Å. The nominal N V EW changes from **+0.122 to −0.019 Å**. Thus N V is not established by this calculation; Si IV also needs a consistent doublet/profile fit. Carbon remains securely detected.

5. **The extinction assertion is incorrect as a universal statement.** White-dwarf-based empirical coefficients give \(R_{\rm FUV}=8.01\), \(R_{\rm NUV}=6.72\), so extinction can redden FUV−NUV. At the quoted \(E(B-V)=0.004\), however, this changes the colour by only **0.005 mag**, nowhere near the observed 0.81-mag offset from the DA median. [Wall et al. 2019](https://arxiv.org/abs/1909.02617). The GALEX anomaly survives, but the controls are not gravity-matched: their median \(M_G=10.17\), versus 11.64 for the target. The DQ controls also mix DQ, DQA and other subtypes.

6. **Variability limits are overstated if interpreted as non-variability.** The 120-second result reproduces: strongest amplitude 4.88 ppt, FAP≈0.49; **1.12 ppt is the mean periodogram amplitude, not an upper limit**. The 20-second low-frequency power is plausibly instrumental/contaminating, but this has not been demonstrated through pixel localisation or injection/recovery. SkyMapper’s null result reproduces. Gaia’s `NOT_AVAILABLE` flag is not a non-variable classification.

7. **The ESO exclusion is unsupported.** [archives.txt](/tmp/hotdq/dd/archives.txt) records an HTTP 400 coordinate error for the raw archive query. Only the Phase-3 query returned an empty result. Minor bookkeeping: the COS header confirms **2024-07-13**, correcting the script’s July-16 comment; the optical visit’s stored S/N is **16.65**, so the quoted 23 needs its alternative definition documented.

## Classification

**My preferred provisional label is “hot DQ with probable hydrogen,” or DQA pending modelling.**

A fresh, simple two-Gaussian fit separating the H-alpha-region depression from adjacent carbon absorption places the former at **6566.42±0.65 Å**, corresponding to approximately **+82 km/s**. Its fitted FWHM is about **16 Å**, rather than the dossier’s approximate 30 Å. These are illustrative profile measurements, not atmosphere-model results. Its location agrees with the carbon velocity, and the supplied C II list offers no strong transition at its centre. **Hydrogen is the leading interpretation and should not be dismissed as an unspecified carbon feature.**

| Interpretation | Assessment |
|---|---|
| Hot DQ/DQA | Best description of the carbon-dominated **optical appearance**; DQA favoured if H-alpha is confirmed. |
| Hot DAQ | A viable atmospheric alternative. Spectral-letter order does not directly measure C/H number abundance. |
| DBQ/DQB | Disfavoured by the absence of a convincing He I series; helium abundance still needs modelling. |
| DA+DQ composite | Possible, but not required. One epoch, normal RUWE and approximately matching velocities do not exclude it. |
| Magnetic carbon-rich WD | Not excluded; the present work provides no quantitative magnetic-field constraint. |

COS independently supports **photospheric carbon**: an illustrative Gaussian fit gives C III 1247 approximately **+75 km/s**, while the narrow C II 1334 core is near **0 km/s**, suggesting an interstellar contribution. The integrated 1335 feature should not all be attributed to the photosphere.

The statement “no broad Ly-alpha” is insufficiently demonstrated. Similar flux on opposite sides of a line does not establish absent absorption; both sides can be depressed. Carbon blanketing, interstellar H and airglow require simultaneous modelling. UV carbon alone does not establish carbon dominance: WD 0525+526 provides a published hydrogen-dominated counterexample. Its optical carbon is much weaker than here, so it is a caution about inference, not an identification of this object. [Sahu et al. 2025](https://arxiv.org/html/2508.03811v1).

The DA-derived temperature, mass and cooling age must consequently be refitted.

## Novelty search log

Searches covered all five supplied aliases, shortened/LaTeX variants, Gaia DR2/EDR3 identifiers, and the additional cached alias `WDJ07354.07-794410.68`.

| Search | Finding |
|---|---|
| Local literature collection | Independently searched **159 text/table files across 58 paper directories**. The only genuine object match was **Bravo et al.**, which lists DA and an explicitly unreliable companion candidate. [Paper](https://arxiv.org/html/2412.04597v1). |
| DQ/DAQ and merger literature | No match in the examined [DAQ study](https://arxiv.org/abs/2403.08878), [Kilic FUV survey](https://arxiv.org/html/2507.12655v1), Sahu paper above, or [García-Zamora et al.](https://arxiv.org/abs/2605.16493), among the local corpus. |
| SDSS-V/DESI/4MOST | No object-specific prior classification found. Checked relevant literature including the [SDSS-V DA+DQ discovery](https://arxiv.org/abs/2507.11618) and [DESI EDR catalogue](https://academic.oup.com/mnras/article/535/1/254/7774399). No matching 4MOST publication surfaced. |
| HST | **17420 explicitly labels the target DA.** Its proposal already records measured FUV=15.95 versus synthetic FUV=14.80: the UV discrepancy was documented, although no carbon classification is stated. The supplied 18060 target list contains no match. [17420 target listing, p.154](https://www.stsci.edu/hst/phase2-public/17420.pdf). |
| Catalogues, ADS, abstracts | Cached SIMBAD/VizieR results support DA; the MWDD material supplies no prior DQ classification. Live object-level catalogue refresh was unavailable. Alias searches of web-indexed ADS/arXiv, AAS/conference, Warwick and Montreal material found no contrary classification. Direct ADS full-text access failed, so I cannot independently certify its reported zero-hit result. |

An informative detail: the object **fails Kilic et al.’s published selection cut**—FUV−RP=−0.888, versus a threshold of −0.612—so its absence from that survey is understandable.

The PHL 657 and J2200−0741 comparison spectra do correspond to published carbon-rich objects; they are useful controls, though both are magnetic and unsuitable as unqualified profile standards. [Published comparison table](https://academic.oup.com/view-large/397137119).

## Missing checks

- **Joint C/H/He atmosphere fitting** of flux-calibrated optical data, COS and parallax-constrained photometry; compare homogeneous, stratified and composite solutions.
- Recover original BOSS `specFull`/individual exposures; inspect masks, resolution and wavelength calibration. Fit COS photospheric and interstellar components with its line-spread function.
- Check GALEX artifact flags, detector position, repeat measurements and source blending; quantify hydrogen/helium limits with synthetic spectra.
- Obtain repeat spectroscopy and magnetic constraints; use timing injection/recovery if variability limits matter.
- Reassess the companion through matched-system SED fitting and astrometry. Its \(i-z=1.05\) supports a late-M hypothesis: published DECam templates give approximately 0.98/1.18 for M7/M8, versus 1.78 for L6. But **M7–M8 at 350–450 pc is not established**, and a galaxy remains possible. At 96 pc, \(M_J=13.65\) explains Bravo’s conditional L6 estimate. [Colour templates](https://academic.oup.com/mnras/article/522/2/1951/7095873).

## Recommendation

Contact **Boris Gänsicke**, with **Snehalata Sahu and Antoine Bédard**, before presenting this as an unrecognised discovery. Their programme has zero proprietary time, so this is scientific coordination, not a request for permission to analyse public data. [Programme details](https://www.stsci.edu/hst-program-info/program/?program=17420). Subsequently involve Patrick Dufour/Pierre Bergeron or Mukremin Kilic for mixed-atmosphere modelling.

Suggested wording:

> We find strong photospheric C II in the public SDSS-V spectrum of Gaia DR3 5208047381438507520, supported by C III in COS dataset lfac0z010 from SNAP 17420. H-alpha suggests hydrogen, so we currently regard it as a hot DQ/DQA candidate; composition and temperature remain unfitted. We found no published carbon-rich classification. Has your team already identified or begun analysing it, and would a coordinated optical–UV atmosphere analysis be useful?