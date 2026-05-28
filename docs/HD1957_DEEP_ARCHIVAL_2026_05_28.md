# HD 1957 / HIP 1886 — comprehensive archival assessment

*Compiled: 2026-05-28. Status: requires RV follow-up before any discovery claim.*

## Identity

| Field | Value |
|---|---|
| Names | HD 1957 = HIP 1886 = BD−00°56 = TYC 3-869-1 = TIC 244166874 |
| Gaia DR3 source_id | 2543788153077017344 |
| RA / Dec (ICRS J2016) | 5.9548° / +0.1219° |
| Distance | 433 pc (parallax 2.31 ± 0.03 mas, NSS solution) |
| Galactic position | thick-disk kinematics (per cascade UVW class) |

## Photometry (multi-catalog)

| Band | Value | Source |
|---|---:|---|
| BT (Tycho-2) | 9.83 ± 0.03 | I/259 |
| VT (Tycho-2) | 8.74 ± 0.02 | I/259 |
| Hp (Hipparcos-2) | 8.83 ± 0.002 | I/311 |
| V (APASS DR9) | 8.67 ± 0.01 | II/336 |
| V (Kervella 2022) | 8.64 | J/A+A/657/A7 |
| B (APASS) | 9.57 ± 0.03 | II/336 |
| g (Gaia DR3) | 8.404 ± 0.003 | I/350 |
| BP (Gaia DR3) | 8.883 ± 0.003 | I/350 |
| RP (Gaia DR3) | 7.758 ± 0.004 | I/350 |
| K_s (2MASS via Kervella) | 6.33 ± 0.02 | J/A+A/657/A7 |
| **BP–RP** | **1.125** | (Gaia) |

`phot_bp_rp_excess_factor = 1.23` — consistent with single-star spectrum (excludes SB2 light contamination).

## Stellar physical parameters

### Pre-Gaia classification

- Michigan Spectral Survey (Houk 1999): **G5/6 IV** — subgiant
- This was the value used by the cascade (because the spectral-type filter looks for `III` not `IV`).

### Gaia DR3 GSP-Phot (photometric stellar params)

- `teff_gspphot`, `logg_gspphot`, `mh_gspphot`, FLAME masses/radii: **all NaN**
- GSP-Phot couldn't fit — likely because of the binary motion confusing the photometric SED.
- **This is why Filter #30's `logg < 2.7` rule didn't trigger** at cascade time.

### Gaia DR3 GSP-Spec (BP/RP-spectrum derived)

| Param | Value | Notes |
|---|---:|---|
| Teff_gspspec | 4860 K | |
| log g_gspspec | **2.36** | below F30 threshold (logg<2.7) |
| [M/H] | −0.18 | mildly metal-poor |
| [Fe/H] | −0.16 | |
| spectraltype_esphs | **K** | not G as Michigan claimed |

### Gaia DR3 GSP-Spec ANN (refined neural-net solution; supplementary AP table)

| Param | Value (90% CI) | Notes |
|---|---:|---|
| Teff_ann | 4771 (4758–4784) K | K1–K2 giant |
| log g_ann | **2.63 (2.60–2.67)** | RGB / red clump giant |
| [M/H]_ann | −0.34 (−0.36, −0.33) | thick-disk metallicity |
| [α/Fe]_ann | +0.10 (+0.09, +0.11) | mildly enhanced |
| **Radius_flame_spec** | **15.53 R_⊙** (14.3–17.2) | unambiguously a giant |
| **Lum_flame_spec** | **121 L_⊙** (103–147) | |
| evolstage_flame_spec | 583 | late RGB / red clump |
| grav_redshift | 0.120 km/s | confirms giant gravity |

**Mass estimate from g·R²/G:** M₁ ≈ 1.0–2.0 M_⊙, most likely M₁ = 1.4–1.8 M_⊙ for a red-clump giant.

## Binarity evidence (5 independent lines, all positive)

### 1. Gaia DR3 NSS Orbital + AstroSpectroSB1 (the cascade input)

| | Value |
|---|---:|
| P | **816.27 ± 2.59 d** |
| e | 0.017 ± 0.010 (nearly circular) |
| Significance flag | 105.7 (very high quality) |
| a_phot (Thiele-Innes) | 3.44 mas = 1.49 AU |
| COM radial velocity | −10.39 ± 0.11 km/s |
| N_obs astrom / good | 465 / 420 |
| N_obs RV / good | 18 / 14, 2 deblended |

Mass function (astrometric) gives M₂ = 2.40 ± 0.09 M_⊙ assuming M₁ = 1.5 M_⊙ **and no chromatic bias**.

### 2. Gaia DR3 main-source quality flags

| Field | Value | Interpretation |
|---|---:|---|
| **RUWE** | **8.75** | Single-star model utterly fails. Threshold is 1.4. |
| astrometric_chi2_al | 54625 (over 465 obs) | χ²/ν ≈ 117 |
| **astrometric_excess_noise_sig** | **1490σ** | single-star solution rejected at 1490 σ |
| non_single_star | 3 | bit 1 (astrometric) + bit 2 (spectro) — both flagged |
| has_mcmc_msc | True | MSC multi-star solution exists |

### 3. Gaia DR3 RVS amplitude

| | |
|---|---:|
| rv_amplitude_robust | **22.6 km/s** |
| rv_chisq_pvalue | 0.0 (machine zero) |
| rv_renormalised_gof | 83.4 |
| time baseline | 881 d |

### 4. Hipparcos-Gaia Catalog of Accelerations (HGCA Brandt+ 2021)

| | Value |
|---|---:|
| HIP | 1886 |
| recno | 1833 |
| pmRA_hip (1991.25) | −1.76 ± 1.18 mas/yr |
| pmDE_hip | +3.10 ± 0.76 mas/yr |
| pmRA_hg (1991–2016 long baseline) | −3.14 ± 0.04 mas/yr |
| pmDE_hg | +2.02 ± 0.025 mas/yr |
| **chi² (PM acceleration)** | **103.5** |

Implied snrPMa ≈ √103.5 = **10.2 σ** independent astrometric acceleration. This is over a 25-year baseline, completely independent of the Gaia DR3 NSS within-mission solution.

### 5. Kervella+ 2022 H2G2 (PMa catalog)

HD 1957 in catalog. Confirms HGCA finding.

## Negative results (worth noting)

| Catalog | Verdict | Implication |
|---|---|---|
| SB9 (Pourbaix+ 2014 SB orbits) | not present | no prior published spectroscopic orbit |
| El-Badry+ 2023 BH1/BH2/binary catalogs | not present | their pipeline filtered HD 1957 out (likely K-giant cut) |
| El-Badry+ 2022 dormant-BH search | not present | same |
| WDS | not in catalog | no resolved visual companion |
| PASTEL stellar params | no row within 5″ | no high-res literature spectroscopy |
| LAMOST DR5–DR9 | no match | not in LAMOST footprint coverage |
| APOGEE DR17 | no match | not in APOGEE footprint |
| GCVS variability | not in catalog | no published photometric variability |
| Pourbaix 1997 (J/A+A/323/L49) | no Vizier table row | bibcode citation is sample-paper, not individual orbit |
| Pourbaix 2015 (J/A+A/580/A23) | no row within 5″ | same |

The SIMBAD bibliography of 13 papers is mostly sample-statistical citations; **no paper has previously solved HD 1957's orbit individually**.

## Follow-up data available without new observations

- **TESS sectors 42 (Aug 2021), 43 (Sep 2021), 70 (Oct 2023)** — FFI cutouts available via TESScut. ~600 days coverage at 30-min cadence. Can constrain or detect ellipsoidal variation at P/2 = 408 d.
- Hipparcos epoch photometry (Hpmag scatter pattern over 1990–1993)

### TESS Sector 42 single-sector check (preliminary)

I pulled a 5×5 pixel FFI cutout via lightkurve. 2970 good points in ~28 days.

| Metric | Value | Interpretation |
|---|---:|---|
| Flux std/median | 2.91% | Significant intra-sector variability |
| Flux range | 14.5% | Large — consistent with K-giant pulsations |
| Lomb–Scargle peak | P = 17.3 d (power 0.49) | Likely rotation or pulsation — *not* the 816-d orbit |
| Half-period fold (within sector) | 0.61% | Upper limit on intra-sector ellipsoidal |

Caveat: a single sector spans only 28 d, which is 3.4% of the orbital period and 6.9% of P/2. **A proper ellipsoidal-variation search needs cross-sector calibration of all three TESS sectors** (Sept 2021 → Oct 2023 = ~770 d, ≈1.0 P). With matched zero-points across sectors, ellipsoidal amplitude at P/2 = 408 d could be measured to ~0.1% sensitivity.

Expected ellipsoidal amplitude for HD 1957:
- Primary R₁ = 15.5 R_⊙, semimajor axis a ≈ 2.0 AU
- R₁ / a = 0.036
- For e = 0.017 (nearly circular), ellipsoidal amplitude ≈ 1.5 × (R₁/a)³ × q × sin²i
- q = M₂/M₁ ≈ 1.5 (NS scenario) → ~0.0008 mag ≈ 0.08% (detectable with multi-sector TESS)
- q = 0.5 (stellar scenario) → ~0.03% (below TESS multi-sector floor)

**This is a discriminating test if we can do the multi-sector reduction.**

## The chromatic-bias problem (Filter #30 territory)

**4 UMi calibration object characteristics:**
- K4 III, BP−RP = 1.49, logg ≈ 1.70 (very evolved giant)
- Cascade a_phot inflated 2.0× → M₂ overestimate 2.9×
- RUWE ≈ 1.5

**HD 1957 in comparison:**
- K1–K2 III, BP−RP = 1.12, logg = 2.63 (mildly evolved giant, less extreme)
- Should produce SMALLER chromatic effect than 4 UMi
- But RUWE = 8.75 — much larger than 4 UMi's

**Three scenarios**

| Scenario | M₁ | M₂ | a_phot correction | Astrophysics |
|---|---:|---:|---|---|
| A — cascade is right | 1.5–1.8 | 2.3–2.5 | none | low-mass NS, dormant |
| B — partial chromatic | 1.5–1.8 | 1.2–1.8 | ~1.4× | massive WD or stellar |
| C — full 4-UMi-like correction | 1.5–1.8 | 0.7–0.9 | 2.0× | K/M dwarf companion |

The fact that **HD 1957's RUWE (8.75) is ~6× larger than 4 UMi's (1.5)** suggests scenario A or B is more likely than C — the photocentric motion is dominated by real orbital reflex, not just chromatic offset.

## Where the three independent measurement axes converge or diverge

For HD 1957, we have three completely separate measurements:

### Axis 1: Gaia NSS within-mission astrometric+spectro (2014.5–2017.4)
- Full orbital solution: P = 816.27 d, e = 0.017
- Photocentric a_phot = 3.44 mas
- ⇒ M₂ = 2.40 ± 0.09 M_⊙ (subject to chromatic correction)

### Axis 2: Gaia RVS radial-velocity amplitude
- rv_amplitude_robust = 22.6 km/s (peak-to-trough robust estimator over 18 transits)
- Uses the same P, e
- ⇒ K₁ ≈ 11 km/s (half of 22.6) gives M₂ sin³i / (M₁+M₂)² = 0.27 M_⊙
- For M₁ = 1.5 and i = 70° (sin³i = 0.83): M₂ ≈ 3.0 M_⊙ (low NS-mass)
- For i = 90°: M₂ ≈ 2.8 M_⊙
- **This is INDEPENDENTLY higher than M_₂ = 2.4 from astrometry** — but Filter #31's calibration showed `rv_amplitude_robust` is not a clean K₁ proxy; it can be inflated by transit outliers.

### Axis 3: Hipparcos-Gaia 25-year proper-motion acceleration (1991–2016)
- pmRA_hip vs pmRA_hg differ by 1.37 mas/yr
- pmDE_hip vs pmDE_hg differ by 1.08 mas/yr
- dV_tan ≈ 3.6 km/s
- chi² = 103.5 over 2 d.o.f. → 10.2σ acceleration
- HGCA doesn't directly give a mass — but it sets a lower limit: for P = 816 d circular, M₂ × sin(i) must produce ~3.6 km/s tangential acceleration.
- For M₁ = 1.5, P = 816 d, at the orbital phase where Hipparcos sampled vs the long-baseline mean: M₂ ≥ ~1.5 M_⊙ to produce the observed acceleration. Confirms **substantial companion**, but doesn't distinguish 2.0 from 3.0 M_⊙.

### Alignment

| Axis | Implied M₂ (M_⊙) | 1σ range |
|---|---:|---|
| Gaia NSS astrom (no correction) | 2.40 | 2.31–2.49 |
| Gaia NSS astrom (chromatic ×2) | 0.83 | 0.80–0.86 |
| Gaia rv_amplitude_robust (uncorrected) | ~3.0 | 2.5–3.5 |
| HGCA acceleration (lower bound) | ≥ 1.5 | — |

The three axes do NOT cleanly agree. Two scenarios fit all data:

1. **NS scenario:** M₂ = 2.2–3.0 M_⊙, chromatic bias is small, the K-giant primary may be on the low side (M₁ ≈ 1.2–1.4 M_⊙) to keep mass function consistent with both astrom and RV.
2. **Stellar companion (massive WD or normal star) scenario:** M₂ = 1.0–1.5 M_⊙. Chromatic bias is intermediate (~30%). rv_amplitude_robust is inflated by outlier transits (the F31 calibration failure mode).

**Both scenarios produce ≥10σ HGCA acceleration.** HGCA alone cannot distinguish them.

## What would settle this

| Cost | Action | Outcome | Time |
|---|---|---|---|
| Free | TESS LC analysis sectors 42/43/70 | If ellipsoidal variation < 0.5% at P/2, M_2 likely stellar (massive companion would tidally distort). If detected, locks i + M_2. | ~2 days |
| Free | Hipparcos epoch photometry analysis | Constrain photometric variability over 3 years of HIP mission | ~1 day |
| ~$0 (own data) | Already-archived FEROS/HARPS-N spectra of bright field stars | Check if HD 1957 has any single-epoch survey RV | ~1 day |
| ~10 hr | New HARPS-N or FEROS RV (4 epochs over 6 mo) | Independent K₁ ⇒ unambiguous M₂ via mass function | ~3 mo |
| ~3 hr | VLT/SPHERE or Gemini-N/GPI 50-mas AO imaging | Rule out luminous companion brighter than M_K ≈ 7.5 | ~1 mo |

## Verdict

**HD 1957 is a real binary at 10σ+ (HGCA) and 1490σ (Gaia excess noise).** That's not in question.

**The companion's nature is genuinely undetermined.** The cascade M₂ = 2.40 M_⊙ classification *could* be right — but the K-giant chromatic bias risk (Filter #30 territory based on the NEW GSP-Spec ANN data) means we cannot publish a discovery claim from the cascade output alone.

**Recommended path:**
1. Add Filter #30b: if `logg_gspphot` is NaN, fall back to `logg_gspspec_ann` for the F30 cut. Re-run the cascade — HD 1957 will be flagged as "K-giant ambiguous" rather than Tier-1 NS.
2. Pursue 4–6 RV epochs with FEROS over 2026–2027 (HD 1957 is observable Aug–Dec; P = 816 d means we sample 1 orbital cycle in 2.2 years).
3. Pull TESS LC for sectors 42/43/70 (no telescope time needed).
4. Refresh the paper-ready catalog without HD 1957 as headline — methodology paper still valid, but the NS-mass demotion of HD 1957 *itself* becomes another calibration object alongside 4 UMi.

This is exactly the kind of certainty check the user asked for. **The good news**: the cascade caught a real binary. **The cautionary news**: the mass cannot be claimed as NS-grade without external follow-up.

## ADS bibcode list for HD 1957 (for paper bibliography)

| Bibcode | Year | Likely topic |
|---|---|---|
| 1993yCat.3135....0C | 1993 | Hoffleit-Jaschek BSC IV |
| 1997A&A...323L..49P | 1997 | Pourbaix Letter — Hipparcos+ground RV improved orbits (sample paper) |
| 1999MSS...C05....0H | 1999 | Houk Michigan Spectral Survey (G5/6 IV class) |
| 2007A&A...474..653V | 2007 | van Leeuwen Hipparcos re-reduction (Hpmag) |
| 2011MNRAS.411..435B | 2011 | likely Bensby thick-disk chemistry sample |
| 2012A&A...546A..61D | 2012 | possibly da Silva (mass-loss?) — review by abstract |
| 2012MNRAS.427..343M | 2012 | possibly McDonald spectroscopic sample |
| 2014ASPC..485..223B | 2014 | conference proc. |
| 2015A&A...580A..23P | 2015 | Pourbaix Tycho-2 photometry (HD 1957 in sample, not individual orbit) |
| 2019A&A...623A..72K | 2019 | Kervella+ 2019 PMa first version |
| 2019MNRAS.490.3158C | 2019 | possibly Cantat-Gaudin |
| **2021ApJS..254...42B** | **2021** | **Brandt+ 2021 HGCA — HIP 1886 is recno 1833, χ²=103.5** |
| 2023A&A...674A..34G | 2023 | Gaia Coll DR3 NSS overview paper |

All can be added to BibTeX via NASA ADS. The two highlighted bibcodes (1997 and 2015) suggested at first that HD 1957 had a prior orbital solution — but **Vizier tables confirm it does NOT**; the citations are sample-paper references.
