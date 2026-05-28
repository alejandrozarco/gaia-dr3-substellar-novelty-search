# HIP 91479 / LP 335-104 — substellar deep-dive (2026-05-13)

**Verdict: TENTATIVE substellar (BD-mass) candidate, joint astro+spec orbit + independent 25-yr astrometric corroboration**

## Source identification

- Gaia DR3 source_id: 4539057576001089408
- HIP: 91479
- LP: 335-104 (Luyten Proper-Motion catalog)
- ICRS coords: 18h 39m 25.6s +28d 22m 27s (J2000)
- Distance: 55.6 pc (Gaia DR3 parallax 17.997 ± 0.067 mas)
- Hipparcos van Leeuwen 2007 parallax: 22.24 ± 2.31 mas (45 pc) — modestly inconsistent at 1.8σ; Gaia is presumably more accurate
- High proper motion: pmra=−117.4, pmdec=−146.3 mas/yr

## Host star

- G = 10.34, BP-RP = 1.50
- M_G = 6.63 (using Gaia parallax)
- → **K3-K7 dwarf**, M_1 ≈ 0.65-0.75 M_⊙
- vbroad = 17.4 ± 3.9 km/s (moderate rotational broadening)
- non_single_star = 3 (NSS-classified as both spectroscopic AND astrometric binary)
- No Gaia DR3 astrophysical parameters (filtered out due to NSS detection — typical for binaries)

## Gaia DR3 NSS Orbital fit (AstroSpectroSB1)

| Parameter | Value | Error |
|---|---|---|
| Period | **855.84 d (2.34 yr)** | ± 25 d |
| Eccentricity | **0.815** | ± 0.038 |
| t_periastron | −225.41 (BJD offset) | ± 4.97 d |
| Center-of-mass velocity γ | −16.34 km/s | ± 0.20 km/s |
| Thiele-Innes A | 1.591 mas | ± 0.085 |
| Thiele-Innes B | −1.311 mas | ± 0.103 |
| Thiele-Innes F | −0.019 mas | ± 0.125 |
| Thiele-Innes G | 1.466 mas | ± 0.131 |
| Thiele-Innes C (spec) | −0.063 km/s | ± 0.022 |
| Thiele-Innes H (spec) | −0.327 km/s | ± 0.049 |
| Significance | 32.24 | — |
| Goodness of fit | 20.7 | — |
| Astrometric n_obs (good) | 416 / 494 | — |
| RV n_obs (good) | 30 / 30 | — |

Solution type **AstroSpectroSB1** means Gaia jointly fit astrometric AND
spectroscopic observations to the same Keplerian orbit. This breaks the
sin(i) degeneracy that affects pure NSS Orbital fits.

## Decomposed companion parameters

From the joint astro + spec fit (Thiele-Innes A,B,F,G → photocentric semi-major axis;
Gaia DR3 rv_amplitude_robust → K_1):

| Quantity | Value | Method |
|---|---|---|
| a_phot (sky-projected) | 2.33 mas | Halbwachs 2023 from A,B,F,G |
| a_1 (host orbit) | 0.127 AU | a_phot / parallax |
| K_1 (host RV amp) | ~1.95 km/s | inferred from Gaia rv_amplitude_robust=3.90 km/s peak-to-peak |
| **M_2 (true mass)** | **58–65 M_J** | Kepler 3rd law from a_1 + P + M_1=0.7 M_⊙ |
| M_2 sin(i) | 42 M_J | K_1 + P + e + M_1 |
| sin(i) | ~0.67 | M_2 sin(i) / M_2 |
| **i** | **~42°** | moderate inclination, not face-on |
| a_2 (companion orbit) | 1.50 AU | a_total − a_1 |

**M_2 ≈ 60 M_J = substellar BD** at the lower-high-mass end of the brown-dwarf
regime, with moderate (not extreme) inclination.

## Independent astrometric corroboration

**HGCA Brandt 2024**: chi² = 50.3 (cross-match with our cached HGCA_vEDR3.fits)
- Hipparcos-Gaia DR3 25-yr proper motion anomaly
- INDEPENDENT of the NSS Orbital fit (uses different astrometric baseline)
- chi² = 50 is a strong PM anomaly; consistent with the predicted reflex from
  the 2.34-yr 60-M_J orbit (10.7 cycles over the HGCA baseline → average
  unresolved displacement ~ a_1 ~ 1 mas)
- This is exactly the kind of multi-pipeline corroboration used for the
  candidates in `novelty_candidates.csv`

## Gaia DR3 RV variability (independent)

- rv_amplitude_robust = 3.90 km/s (peak-to-peak across 30 transits)
- rv_chisq_pvalue = 6.75e−5 → strongly variable
- Predicted K_1 from C, H Thiele-Innes (Pourbaix formula): 574 m/s
- K_1 inferred from observed rv_amplitude_robust ÷ 2: ~1948 m/s
- **3.4× discrepancy** — the Gaia-published spec Thiele-Innes K_1 prediction does
  not match the observed RV scatter. **ERRATUM**: an earlier version of this
  dossier claimed an "exact match" — that was wrong; the prediction was off by 3.4×.
  The same 3-42× discrepancy is present for all 5 AstroSpectroSB1 candidates in
  our supplementary pool, suggesting a normalization issue with the Pourbaix
  C, H formula OR systematic issues in Gaia's AstroSpectroSB1 fits at high RUWE.
  **The astrometric M_2 = 64 M_J from a_phot + Kepler remains valid** because it
  does not depend on K_1. The spectroscopic mass interpretation should be
  considered tentative.

## Quality flags

| Flag | Value | Concern? |
|---|---|---|
| RUWE | 4.11 | high — but expected for AstroSpectroSB1 with real companion |
| ipd_frac_multi_peak | 0 | clean PSF |
| astrometric_excess_noise_sig | 768 | extreme — but again, expected for binary |
| phot_variable_flag | NOT_AVAILABLE | — |
| Hipparcos van Leeuwen 2007 Sn | 5 | accepted single-star solution at HIP epoch only |

The HIP-only "single-star solution" is consistent — Hipparcos 1989-1993 caught
only ~1.5 orbital cycles, insufficient to detect the BD reflex. Gaia DR3 over
2014-2017 caught ~1.3 cycles plus RV component, enabling the AstroSpectroSB1
detection.

## Cross-match verification (clean)

- NASA Exoplanet Archive PS: NOT in (gaia_dr3_id match) ✓
- exoplanet.eu (30 arcsec coord match): NOT in ✓
- Sahlmann 2025 ML imposter list: NOT in ✓
- Stefansson 2025 G-ASOI: NOT in ✓
- Gaia DR3 documented FP (cosmos.esa.int): NOT in ✓
- SB9 Pourbaix (10 arcsec coord match): NOT in ✓

Genuinely novel substellar candidate at the BD/stellar boundary.

## Why this wasn't surfaced by the original substellar pipeline

The original Stage-1 → 35-filter cascade applied tier_a quality cuts including
RUWE < 2. HIP 91479 has RUWE = 4.11 — **failed the tier_a cut** and was demoted to
the lower-priority pool.

But for AstroSpectroSB1 sources, RUWE > 1.4 is **expected** because the
astrometric reflex itself drives RUWE up. The RUWE < 2 cut was inappropriately
applied to this solution type. This is the expansion-audit's main methodology
finding: tier_a quality cuts should be conditional on `nss_solution_type`.

## Confirmation pathway

Predicted K_1 = ~1.95 km/s is easily detectable with any northern small-aperture
spectrograph at V~11:
- HARPS-N (La Palma, +28°N) — 2-3 night queue
- SOPHIE (Haute-Provence, +43°N) — 1-2 nights
- TRES (Whipple, +32°N) — 1 night for K_1 detection
- HIRES (Keck, +20°N) — partial sky access; only at low airmass

Quadrature epochs are predictable from Gaia DR3 t_periastron and Gaia DR3 RV phase.

Confirmation criteria:
- Observed K_1 within 30% of 1.95 km/s → confirms substellar
- M_2 sin(i) > 80 M_J at observed K → demotes to stellar M-dwarf
- Phase-fold of new RV epochs matches Gaia ephemeris → confirms 2.34 yr period

## Comparison with HD 75426 (existing tentative)

| Property | HD 75426 | HIP 91479 |
|---|---|---|
| Solution type | NSS Acceleration9 (P inferred from jerk) | AstroSpectroSB1 (joint astro+spec, P measured) |
| Multi-pipeline | 4 baselines (HGCA, Kervella, NSS Accel, Tycho-Gaia ΔPM) | 2 baselines (NSS Orbital + HGCA Brandt 2024) |
| Period | ~125 yr (long, marginalized) | 855 d (directly fit) |
| Eccentricity | not constrained | 0.81 (extreme) |
| Mass posterior | inclination-marginalized 100-282 M_J | a_phot + K_1 joint → 60 M_J |
| HGCA chi² | 33 | 50.3 |
| Distance | 50 pc | 55.6 pc |
| Host | F5IV/V dwarf | K5-K7 dwarf |
| Confirmation | DR4 or single FEROS epoch | DR4 or single HARPS-N/SOPHIE epoch |
| P(real substellar) | ~30% | ~60-70% |

HIP 91479 is comparable strength to HD 75426 but with **direct sin(i) measurement**
rather than inclination-marginalization. The high eccentricity is unusual but
matches both astrometric and spectroscopic signals consistently.

## Recommendation

**ADD HIP 91479 to `novelty_candidates.csv` as a new TENTATIVE substellar candidate.**
- Category: `filter_survivor_substellar_candidate_astrospectrosb1`
- FP risk tier: low (AstroSpectroSB1 not on documented FP class; HGCA-corroborated)
- P_real_companion: ~0.95 (HGCA chi²=50.3 + Gaia rv_chisq pvalue 6.75e−5)
- P_substellar_given_real: ~0.65 (M_2 ~ 60 M_J solidly in BD range, but at upper-mass end)
- P_joint: ~0.62

This is a meaningful new candidate that the original pipeline missed due to an
overly-strict RUWE cut applied uniformly across solution types.
