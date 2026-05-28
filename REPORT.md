# Project report — v2.0.0 (2026-05-28)

This report describes the current state of the dormant compact-object & substellar companion search after the v2 cascade corrections. It supersedes `docs/archive/root_v1/REPORT_v1.md`.

For the canonical candidate list see `docs/MASTER_OBJECTS_OF_INTEREST_2026_05_28.md`.
For the full state inventory + lessons learned see `docs/PROJECT_STATE_2026_05_28.md`.

## Status

**This work remains experimental.** The pipeline applies a corrected filter cascade plus a 7-step novelty verification to public Gaia DR3 NSS data, but **only one of the 32 truly-novel candidates has independent second-method confirmation** (CRTS J051419+0111, via TESS-photometric eclipse at the ZTF-derived period). The remaining 31 are strong candidates requiring observational follow-up.

## Abstract

Filter-cascade analysis of the Gaia DR3 NSS Orbital + AstroSpectroSB1 + Acceleration catalogs (~73,000 candidate sources after upstream quality cuts) identifies 32 truly-novel companion candidates after applying:

- **v2-corrected mass-function inversion** (NSS parallax + K_obs = rv_amplitude_robust/2 + Filter #30 logg fallback chain)
- **Four cascade filters** (F#29 SB2, F#30 K-giant chromatic, F#31 RV reality, F#32 joint K_obs/K_pred)
- **7-step novelty verification** (SIMBAD bibcodes + exoplanet.eu + NASA Exoplanet Archive + Google + arXiv + CuPS-ETV + studied PCEB master list)

Cascade validation against 70 published benchmark systems gives 93% recall on confirmed compact/sub-stellar systems and 14% Tier-1 false-positive rate on adversarial cases. Median \|ΔM_2\|/M_2 against Shahaf+ 2024 NS sample: 4.5%.

The 32 truly-novel candidates distribute across 6 papers in preparation:

1. **14 new CV orbital periods** — MNRAS Letter draft ready (`docs/CV_PERIOD_PAPER_DRAFT_2026_05_28.md`)
2. **8 → 1 HGCA + no-NSS BH-class** (HD 157033 survives vetting, others demoted as visual binaries)
3. **2 WD-primary Type Ia progenitor candidates** (both not in SIMBAD)
4. **3 M-dwarf super-Jupiter candidates** (APMPM J0710-5704 has 37 TESS sectors)
5. **3 Stefánsson substellar candidates** (BD+05 5218 dropped per Stevenson 2023 scoop)
6. **2 multi-survey dual-binarity hits** (Gaia 5476986 with APOGEE+RAVE K_1 = 163 km/s)

## Methodology

### Stage 1 — Input pool

Gaia DR3 NSS Orbital + AstroSpectroSB1 (56,100 sources after upstream quality cuts) plus NSS Acceleration (16,949 sources at `significance ≥ 50`). Upstream filters: parallax > 0.5 mas, RUWE < 10, significance > 5, valid Thiele-Innes for Orbital channel.

The upstream G < 13 cut excludes 162 of 177 Shahaf+ 2023 NS candidates from the input pool — this is the **binding completeness constraint**, documented in `docs/UPSTREAM_FILTER_AUDIT_2026_05_28.md`.

### Stage 2 — Mass function inversion

For Orbital + AstroSpectroSB1: derive M_2 from the Thiele-Innes constants (A, B, F, G) at the **NSS-corrected parallax**, with a per-source M_1 prior (FLAME mass when available, else 1.5 M_⊙ default). The mass function

f(M) = M_2³ / (M_1 + M_2)² = a_phot³ / P²

is inverted by 80-iteration bisection.

For Acceleration: PM-acceleration → M_2 over a period grid P ∈ [3, 100] yr. Report M_2_min, M_2_median, M_2_max because the period is degenerate without an orbital fit.

### Stage 3 — Filter cascade

| Filter | What it catches |
|---|---|
| **F#29 SB2** | Double-lined spectroscopic binaries — luminous secondary contaminating the astrometric photocentre |
| **F#30 K-giant chromatic** | K-giant primaries with BP–RP > 1.2 or log g < 2.7 — chromatic photocentric bias inflates a_phot by ~2× (4 UMi and HD 1957 calibration cases). Logg fallback chain: GSP-Phot → GSP-Spec ANN → GSP-Spec. |
| **F#31 RV reality** | rv_amplitude_robust > 0 but rv_chisq_pvalue > 0.5 — phantom RV variability from outlier transits (A-dwarf calibration case) |
| **F#32 joint K_obs/K_pred** | K_obs (= rv_amplitude_robust / 2) compared to K_pred(i = 90°) from the astrometric M_2. sin(i)_implied > 1.05 indicates either non-orbital noise or M_2 inflation |

A proposed **F#33** (AstroSpectroSB1 self-consistency: C,H-implied K_1 vs rv_amplitude_robust/2 disagreement > 2σ → demote) is documented in `docs/FILTER33_PROPOSAL_2026_05_28.md` but not in the current cascade.

### Stage 4 — 7-step novelty verification

Before any candidate is promoted as truly novel, all 7 checks must return null:

1. SIMBAD bibcode count + last 5-10 paper title scan
2. exoplanet.eu CSV cross-reference (cached locally)
3. NASA Exoplanet Archive TAP query
4. Google search "<target>" + ["tertiary" | "circumbinary" | "compact" | "binary" | "NS" | "BH"]
5. arXiv full-text API search
6. CuPS-ETV catalog (for PCEB candidates)
7. Master "studied PCEB" list + project's own INVESTIGATION_JOURNAL

Default classification: NOT NOVEL. The DD CrB lesson (a v1.16 candidate that turned out to be a previously-published planet host) is the precedent.

## Validation

| Group | Result |
|---|---|
| Confirmed Gaia BHs (BH1/BH2/BH3) | 2/3 caught as compact-mass. BH3 absent from DR3 NSS (P = 11.6 yr exceeds mission baseline). |
| **Shahaf 2024 NS subset (21 confirmed via multi-epoch RV)** | **21/21 = 100% caught with M_2 ≥ 1.2 M_⊙. Median \|ΔM\|/M = 4.5%.** |
| Andrews/Shahaf candidates (40) | 40/40 produce M_2 ≥ 1.2. **14% Tier-1 FP rate** on the spectroscopically-ruled-out subset. |
| FP calibrators (4 UMi, A-dwarf phantom, HD 76078) | 2/3 caught by the correct filter. HD 76078 (SB2) rejects at the architectural level (no Thiele-Innes). |
| Sub-stellar recovery (HD 81040, HD 111232 — known planet hosts) | Both classified as `planet_candidate` with ~10% mass error. |

**Class-level recall on confirmed compact + sub-stellar systems: 93% (25/27).**

Full validation table at `docs/CASCADE_VALIDATION_EXTENDED_2026_05_28.md`.

## Honest discovery assessment

A discovery in compact-object astronomy requires:

1. Detection above noise floor ✓ — all 32 candidates qualify
2. Methodologically sound ✓ — v2 cascade + 7-step protocol
3. Novel (not previously published) ✓ — passed 7-step today
4. **Independent verification by a second method** ← gate
5. **Confirmed by independent observation** ← gate

| Pile | Discoveries (Gate 4+5) | Strong candidates (Gates 1–3) |
|---|---:|---:|
| F (CV-period) | **1** (CRTS J051419+0111 via TESS eclipse) | 13 |
| A (HGCA BH-class) | 0 | 1 (HD 157033) |
| E (WD-primary) | 0 | 2 |
| B (M-dwarf super-Jupiters) | 0 | 3 |
| D (Stefánsson) | 0 | 3 |
| C (Multi-survey) | 0 | 2 |
| **Total** | **1** | **24** |

The CV-period paper is publishable as a discovery letter because **photometric period determination IS the discovery mechanism in CV literature**. The other 5 papers need follow-up RV or AO imaging to confirm individual candidates before they can claim discovery status.

## What's next

1. **CV-period MNRAS Letter** — convert `docs/CV_PERIOD_PAPER_DRAFT_2026_05_28.md` to LaTeX, finalize figures (19 phase-fold PNGs already generated), submit.
2. **HD 157033** — request GALAH DR4 RV time series (already in their archive, free).
3. **APMPM J0710-5704** — fold all 37 TESS sectors at P = 253 d to search for transit (agent in progress at the time of v2.0.0 release).
4. **WD-primary X-shooter / HARPS-N campaign** — 5 epochs over one 9-month season for WDJ020915.51+380425.92 yields >20σ M_2.
5. **Stefánsson 3 TRES nights** — 1 quadrature epoch per target.
6. **Multi-survey Gaia 5476986** — 1 night confirmation spectroscopy.
7. **Gaia DR4** (December 2026) — per-transit RV release will automatically confirm or refute candidates we haven't observed.

## Lessons learned

`docs/PROJECT_STATE_2026_05_28.md` §3 documents 20 numbered lessons. The five most consequential are:

1. **DD CrB lesson**: SIMBAD/ADS bibcode alone misses exoplanet catalog entries. The 7-step verification protocol is mandatory.
2. **Two compensating cascade bugs** (NSS-plx + K_obs = 2K_1) cancelled inside Filter #32, making M_2 wrong by 2× without breaking internal consistency.
3. **F#5 (G < 13) is the binding completeness constraint** — 162/165 Shahaf 2023 NS candidates are excluded by this single filter.
4. **Hierarchical triple diagnosis**: SB1 + Acceleration with discordant M_2 inferences = triple, not single compact-object companion (HD 12871 case validated by independent APOGEE K_1 = 11.9 = Gaia SB1 K_1).
5. **Multi-survey was integral from v1** (APOGEE Kounkel 2021 SB2 negative-controls in Task A1) but only became a discovery channel in v3.
