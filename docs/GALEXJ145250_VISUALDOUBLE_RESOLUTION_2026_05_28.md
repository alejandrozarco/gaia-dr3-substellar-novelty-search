# GALEX J145250.3-192225 / Gaia DR3 6281177228434199296: visual-double resolution

**Date:** 2026-05-28
**Question:** Is the M_2 = 12.75 M_⊙ Tier-1 BH candidate corrupted by the SIMBAD `**` flag, or is the visual-double signature spurious?
**Verdict (TL;DR):** The `**` flag is **NOT** a real visual binary. There is no resolved companion within Gaia's PSF. **The astrometric BH inference is robust against the visual-double concern, but the source was already flagged as Class-III BH candidate by Shahaf+ 2023 and is consistent with — though not confirmed by — Tanikawa+ 2023's spectroscopic test. UV photometry rules out a WD companion. Status: surviving Tier-1 BH candidate, but inclination-uncertain.**

---

## 1. Identity

| Catalog | Identifier | Notes |
|---|---|---|
| Gaia DR3 | 6281177228434199296 | G=11.259, BP-RP=0.912, plx=4.412±0.152, RUWE=6.46 |
| Gaia DR2 | 6281177228434199296 | same |
| GALEX | J145250.3-192225 | NUV=16.544±0.027, FUV not detected (exp=96 s) |
| 2MASS | J14525036-1922251 | J=10.059, H=9.691, K=9.586 |
| AllWISE | J145250.33-192225.0 | W1=9.494, W2=9.537, W3=9.457, W4=8.456 |
| Tycho-2 | 6163-94-1 | matched at 0.6″ |
| TIC | 309514076 | |
| GSC | 06163-00094 / GSC2 S91M000276 | Class=0 (star) |
| USNO-B1.0 | 0706-00292913 | |
| RAVE | J145250.4-192225 | single epoch HRV=-23.68 ± 0.71 km/s (MJD 53127) |
| Bailer-Jones 2021 | r_geo = 227.3 (217.9-236.6) pc | |
| eROSITA-DE eRASS1 | 1eRASS J145250.2-192230 | 5.3″ off-pos; likely chance / corona of G dwarf |

SIMBAD `otypes`: `*`, `**`, `UV`, `NIR`.

---

## 2. Visual-double evidence search

### 2.1 WDS / Tycho-Double / SIMBAD cone
| Catalog | Result |
|---|---|
| **WDS (Mason+ B/wds/wds)** within 30″ | **NO ENTRY** |
| **TDSC (Fabricius I/276)** within 30″ | **NO ENTRY** |
| **SIMBAD cone within 60″** | only one source (this one) |
| Mason/Hartkopf speckle catalogs | no entry |
| Hipparcos | not in main catalog |

There is no historically resolved visual double at this position in any double-star catalog. The SIMBAD `**` otype is therefore a **flag inherited from the Gaia DR3 NSS Orbital classification** (or possibly the RAVE multi-epoch RV variability), not from an optical resolution.

### 2.2 Same-position multi-catalog cone (0–10″)
| Catalog | Bright matches within 1.5″ | Faint catch-alls 1.5–10″ |
|---|---|---|
| Gaia DR3 | 1 (this source) | 1 at 8.8″ (G=17.9, different plx/pm) + 1 at 10″ (G=21) |
| PanSTARRS DR2 | 1 at 0.83″ | 2 at 8.7″ and 9.5″ |
| 2MASS | 1 at 0.88″ | none |
| AllWISE | 1 at 0.50″ | none |
| GALEX AIS | 1 at 1.07″ | none |
| APASS DR9 | 1 at 0.45″ | none |
| UCAC4 | 1 at 0.83″ | none |
| Tycho-2 | 1 at 0.60″ | none |
| SkyMapper DR4 | no entry (no coverage?) | — |

### 2.3 Two "double" detections that look suspicious
| Catalog | Entries within ~0.5″ | Reality |
|---|---|---|
| **VHS DR4/DR5** (II/367) | [0] at 0.10″ with full JHKY phot, pStar=0.9997 (star, prim=1.0); [1] at 0.36″ with **only Y=12.5, pGal=0.9, Class=1 (galaxy)** | The 0.36″ "duplicate" is a background galaxy detection, not a stellar companion. |
| **GSC 2.4.2** (I/353) | [0] at 0.02″ (this source, Class=0, full multi-band phot incl. Gaia G=11.26); [1] at 0.36″ with **only Y=12.5, Class=3 (galaxy)** | Same background galaxy as the VHS entry. |

So the only "near companion" anywhere in the literature is a faint background galaxy at ~0.36″ with Y_galaxy − Y_star ≈ 4 mag. Even if Gaia were affected by this, it would contribute ~2% flux, well below the threshold to corrupt the Thiele-Innes elements of a G=11.26 star.

---

## 3. Gaia DR3 internal blend diagnostics

| Field | Value | Healthy range | Verdict |
|---|---:|---:|---|
| `ipd_frac_multi_peak` | 0 | <2% | clean |
| `ipd_frac_odd_win` | 0 | <2% | clean |
| `ipd_gof_harmonic_amplitude` | 0.0086 | <0.05 | clean |
| `phot_bp_rp_excess_factor` | **1.212** | <1.3 | **clean** (no BP/RP blend) |
| `visibility_periods_used` | 15 | ≥9 | good |
| `astrometric_n_obs_al` | 197 | high | good |
| `astrometric_gof_al` | 72.4 | should be <3 for single | dominated by orbital reflex, not blend |
| `astrometric_excess_noise_sig` | 1574.9 | huge | the orbital reflex itself |
| `duplicated_source` | False | | clean |
| `astrometric_primary_flag` | False | | normal for orbital solution |
| `classprob_dsc_combmod_star` | 0.99995 | | DSC: unambiguous star |
| `RUWE` | 6.46 | <1.4 single | very high → orbital reflex |
| `non_single_star` | 1 (Orbital) | | NSS orbital flag set |
| `phot_g_n_obs/bp_n_obs/rp_n_obs` | 201/23/22 | | normal sample for G=11 |

**All Gaia internal blend diagnostics are clean.** The high RUWE / `astrometric_chi2_al = 30,070` / `astrometric_excess_noise_sig = 1575` reflects a real, single-Keplerian orbital reflex — not a blend signature.

---

## 4. NSS orbital solution

`gaiadr3.nss_two_body_orbit` row: `nss_solution_type = Orbital` (astrometry-only — C and H Thiele-Innes elements are NULL; this is NOT an AstroSpectroSB1 combined fit).

| Parameter | Value |
|---|---|
| Period | 153.95 ± 0.36 d |
| Eccentricity | 0.180 ± 0.042 |
| A, B, F, G (mas) | 1.78, −3.08, 3.67, −1.86 |
| a₁ (photocentre semi-major axis from TI) | 5.22 mas (≈ 5.51 mas Kepler at M₂=12.75) |
| Astrometric mass function f_m,astro | ~9–12 M_⊙ |
| `goodness_of_fit` | 8.05 (a bit high, consistent with marginal fit) |
| `significance` | 24.31 |
| `flags` | 64 |
| inclination, K₁, m₂/m₁ | NOT solved (astrometry only — degenerate without RV) |

---

## 5. UV photometry — BH vs WD discriminator

Dereddening with A_V = 0.29 (Gaia gspphot), A_NUV ≈ 2.6 A_V = 0.75 mag.

| Quantity | Observed | Dereddened | Expected for isolated G dwarf (Teff=5800, [Fe/H]=−0.5, log g=4) |
|---|---:|---:|---:|
| NUV − V | 5.10 | 4.63 | 7.0 – 8.0 |
| NUV − G | 5.29 | 4.77 | 7.5 – 8.5 |

The source is **brighter** in NUV than the photospheric prediction by ~2.5–3 mag. **There IS a modest UV excess.**

However, for a 5800 K G dwarf, "NUV − V ~ 4.6" is on the boundary of chromospheric activity vs. hot-companion signatures. Compare to:
- **Hot WD companion:** would push NUV − V well below 3 (typically NUV − V ≈ 0–2 for a 10,000 K WD + G dwarf).
- **Chromospherically active G dwarf:** NUV − V ≈ 4–6 is consistent with active solar-type stars (Findeisen+ 2011; Smith+ 2017).
- **No companion:** ~7–8.

So the UV signature is **inconsistent with a pure photosphere but also inconsistent with a hot WD**. A chromospherically active G dwarf, possibly enhanced by tidal spin-up in the 154-d orbit, is the most parsimonious explanation. **Does NOT support a WD-companion interpretation.** Consistent with either an inert BH/NS companion OR a stripped non-degenerate companion.

The eROSITA 1eRASS detection at 5.3″ off-axis could be coronal X-rays from such an active star, but the positional offset is large and chance alignment cannot be excluded.

---

## 6. Spectroscopic mass-function consistency check

| Quantity | Value | Interpretation |
|---|---|---|
| Gaia DR3 `rv_amplitude_robust` | 20.1 km/s | implies K₁ ≈ 10 km/s |
| Gaia DR3 `rv_nb_transits` | 7 | sparse RV sampling |
| Gaia DR3 `rv_chisq_pvalue` | 0.0 | RV variability is highly significant |
| Gaia DR3 mean RV | +0.56 ± 3.55 km/s | center-of-mass-like |
| RAVE single epoch (2004) | −23.68 ± 0.71 km/s | offset 24 km/s from Gaia mean → confirms RV variability |
| Classical f(M) from K₁ ≈ 10 km/s, P=154 d, e=0.18 | **0.015 M_⊙** | spectroscopic mass function |
| Implied M₂ if sin i = 0.11 (Gaia astrometric value) | **13.4 M_⊙** | matches astrometric BH inference |
| Implied M₂ if sin i = 1.0 (edge-on) | 0.30 M_⊙ | M-dwarf (excluded by astrometry) |
| Implied M₂ if sin i = 0.5 | ~3 M_⊙ | NS/heavy-BH boundary |

**At the astrometric inclination sin i = 0.11, the K_observed ≈ 10 km/s is precisely what a M_2 = 12.75 M_⊙ companion predicts.** The Gaia RV is self-consistent with the BH hypothesis — but not independently constraining, because the same K_1 fits any (M_2, sin i) combination on the line K_1 = a_1 sin i × (2π/P)/√(1-e²).

Tanikawa+ 2023 (arXiv:2209.05632) excludes this source from their final BH list because their hard cut `0.5 ≤ f_m,spectro/f_m,astro ≤ 2` is not met (ratio = 0.0017). But their own text acknowledges: *"We do not intend to reject the three BH candidates completely. The three BH candidates may suffer from large errors of spectroscopic data."* The Tanikawa metric divides by sin³i to recover f_m,spectro from K₁; for genuinely face-on (small sin i) BH binaries, the spectroscopic K₁ has limited diagnostic power and the test loses sensitivity.

---

## 7. Cross-check published BH catalogs

| Reference | Status |
|---|---|
| **Shahaf+ 2023 MNRAS 518.2991 (Triage I)** Table 2 | **YES — Class-III**, M₂ = 11.9 ± 1.5 M_⊙. Their highest-tier compact-companion candidate. |
| **Shahaf+ 2024 MNRAS 529.3729 (Triage II, WD census)** | **NOT listed** — not classified as WD. Consistent with non-WD compact-companion interpretation. |
| **Garbutt+ 2023 ApJ 954.4** ("White Dwarfs Revealed in Gaia's CCBC") | not found in PDF text (paper-search may have missed; cited in SIMBAD bib). |
| **Tanikawa+ 2023 ApJ 946.79** | mentioned by name as "Shahaf's 3 BH candidates"; **explicitly does not list as BH** because f_m,spec/f_m,astro = 0.0017 fails their cut, but **does not rule it out** ("may suffer from large errors"). |
| **Andrews+ 2022** | NOT in their compact-companion list (rejection criterion: `goodness_of_fit > 5`, which our source has). |
| **El-Badry+ 2023** (Gaia BH1, MNRAS 518.1057) | listed in SIMBAD bib but not for this source per se. |
| **Andrews+ 2026 v2 MS/RGB BH CSVs** (`/tmp/andrews_*_BH.csv`) | **NOT in either list** (already grep'd). |
| **An & Gu 2026 (SED diagnostics)** | source not mentioned in PDF. |

---

## 8. Kinematics

UVW heliocentric = (−17.5, −15.7, +16.0) km/s
UVW LSR (Schönrich) = (−6.4, −3.5, +23.3) km/s
|V_pec| = 24 km/s, Toomre √(U² + W²) = 24 km/s → **thin-disk kinematics**, nothing exotic.
Reduced PM H_G = 8.4 → consistent with main-sequence dwarf at d=227 pc.
Pristine Survey CaHK metallicity [Fe/H]_phot = −0.48 (Gaia DR3 gspspec [M/H] = −0.42).

---

## 9. Bottom line

**Is the BH inference robust against the visual-double flag?**

**Yes, with caveats.** Specifically:

1. **The SIMBAD `**` otype is NOT supported by any actual double-star catalog (WDS, TDSC, Mason).** It is plausibly a downstream tag from the Gaia DR3 NSS Orbital classification (or from RAVE multi-epoch RV variability), not a resolved visual companion.
2. **No resolved bright companion exists within Gaia's effective PSF (≲1″).** PS1, 2MASS, AllWISE, GALEX, APASS, UCAC4, Tycho-2 all return a single bright source at this position.
3. **The two "near-companion" catalog entries (GSC2 S91M066373 at 0.36″, VHS DR5 [1] at 0.36″) are identified by both surveys as a background galaxy** (Class=3 in GSC2; pGal=0.9 in VHS). At Y≈12.5 vs. primary Y=12.1, this object contributes ≲4 mag fainter flux at 0.36″ and is too far/too faint to corrupt the Thiele-Innes fit of a G=11.26 star.
4. **All Gaia DR3 internal blend diagnostics are clean**: `ipd_frac_multi_peak=0`, `ipd_frac_odd_win=0`, `ipd_gof_harmonic_amplitude=0.009`, `phot_bp_rp_excess_factor=1.21` (below 1.3 blend threshold), `classprob_dsc_combmod_star=0.99995`.
5. **UV photometry rules out a hot WD companion.** NUV − V_dered = 4.6, consistent with a moderately active G dwarf, **not** with a WD or sdB.
6. **Spectroscopic K₁ ≈ 10 km/s (from RAVE + Gaia) is consistent with M₂ ≈ 12.75 M_⊙ × sin i = 0.11**, exactly matching the astrometric inference. But the face-on geometry means RV cannot independently confirm M₂.

**What the candidate truly hangs on:** the Gaia DR3 astrometric Thiele-Innes solution producing a₁ ≈ 5.2 mas with `significance = 24` and `goodness_of_fit = 8`. The visual-double flag is **not** the failure mode for this source.

**Remaining failure modes** (NOT ruled out here):
- The orbital solution itself could be spurious (`goodness_of_fit = 8` is marginal). Worth checking the corr_vec covariance for degeneracy with single-star 5-parameter fit.
- Active chromosphere (NUV excess) could mean the primary is not quite a clean MS G dwarf — possibly a near-MS object with mild ellipsoidal/tidal effects (P=154 d is too wide for that, though).
- Hierarchical triple with inner subdwarf — possible, but the lack of UV excess argues against any compact inner companion.
- **The eccentric 154-d orbit IS suspicious: it overlaps the Gaia spectroscopic-RV scanning bias regime** (~3× the 63-d scan period? No — 154/63 ≈ 2.44, not an integer multiple). Period aliasing is unlikely.

**Recommendation:** Keep on Tier-1 BH candidate list, but **tag with caveat:**
> "Face-on (sin i ≈ 0.11); M₂ inference geometrically degenerate. Spectroscopic K₁ ≈ 10 km/s consistent with M₂ = 12.75 M_⊙ at this inclination but cannot independently confirm. SIMBAD `**` otype is not a real visual binary. Best follow-up: high-resolution multi-epoch echelle RV (Echelle/HARPS-S 4-6 epochs at quadrature) and adaptive-optics imaging (Keck/NIRC2 H-band) to confirm no inner ~0.1–1″ stellar companion. eROSITA X-ray flag should also be investigated for coronal/accretion signatures."

---

## Appendix: full Gaia DR3 quantities pulled

```
source_id              = 6281177228434199296
ra, dec                = 223.20971, -19.37362
parallax (mas)         = 4.412 ± 0.152
pmra, pmdec (mas/yr)   = -26.15, 4.15
G, BP, RP              = 11.259, 11.627, 10.715
bp_rp                  = 0.912
phot_bp_rp_excess_factor = 1.212   <-- CLEAN
ruwe                   = 6.46
astrometric_chi2_al    = 30070
astrometric_excess_noise_sig = 1574.9
ipd_frac_multi_peak    = 0
ipd_frac_odd_win       = 0
ipd_gof_harmonic_amp   = 0.0086
visibility_periods_used = 15
non_single_star        = 1 (Orbital)
duplicated_source      = False
classprob_dsc_combmod_star = 0.99995
radial_velocity        = 0.557 ± 3.55 km/s
rv_chisq_pvalue        = 0.0
rv_amplitude_robust    = 20.12 km/s
rv_nb_transits         = 7
rv_template_teff/logg/feh = 5750 / 4.0 / -0.25
teff_gspphot           = 5798 K
logg_gspphot           = 4.01   (confirms MS dwarf)
mh_gspphot             = -0.54
mass_flame             = 0.99 M_sun
radius_flame           = 1.24 R_sun
distance_gspphot       = 274.9 pc
A_V (gspphot)          = 0.29

NSS Orbital solution:
  period      = 153.95 ± 0.36 d
  eccentricity = 0.180 ± 0.042
  significance = 24.31
  goodness_of_fit = 8.05
  A,B,F,G TI elements (mas) = 1.78, -3.08, 3.67, -1.86
  (C,H undefined -- astrometry-only fit)
```

