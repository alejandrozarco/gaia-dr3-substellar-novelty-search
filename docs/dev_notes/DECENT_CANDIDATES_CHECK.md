# Decent-candidate cross-check (2026-05-13)

Applied the same joint astro+spec decomposition that promoted HIP 91479 to
all "decent" candidates. The check exposed two important methodology issues
that change the per-candidate verdicts.

## Methodology applied

For each candidate, compute:
1. **a_phot** from Thiele-Innes (A, B, F, G) — Halbwachs 2023 formula
2. **a_1** (host physical orbital semi-major axis) = a_phot / parallax
3. **M_2 (Kepler)** from a_1 + P + M_1 — independent of inclination
4. **K_1 (Thiele-Innes)** from spectroscopic Thiele-Innes (C, H):
   K_1 = √(C² + H²) / √(1 − e²)  [Pourbaix convention]
5. **K_1 (observed)** = rv_amplitude_robust / 2 (peak-to-peak / 2)
6. **Consistency check**: K_1 obs / K_1 TI ratio — should be ~1 for a clean fit
7. HGCA Brandt 2024 chi² independent astrometric corroboration

## Result table

| Candidate | Pool | P (d) | e | M_2 Kepler (M_J) | K_1 TI (m/s) | K_1 obs (m/s) | **obs/TI ratio** | HGCA chi² |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| HIP 91479 | AstroSpectroSB1 | 855.8 | 0.815 | 64.0 | 574 | 1948 | **3.4×** | 50.3 |
| 530277454305601920 | AstroSpectroSB1 | 484.0 | 0.254 | 59.3 | 91 | 2601 | **28.7×** | — |
| 1398115488116027264 | AstroSpectroSB1 | 290.7 | 0.381 | 58.9 | 47 | 1981 | **42.0×** | — |
| **HIP 60321** | AstroSpectroSB1 | 530.2 | 0.340 | 53.9 | 106 | 3272 | **30.8×** | **42.2** |
| 6901280071143747968 | AstroSpectroSB1 | 753.7 | 0.435 | 53.1 | 211 | 6364 | **30.1×** | — |
| HIP 21449 | SB1+Kervella | 37.8 | 0.038 | — (sin(i) limit 55 M_J) | 3110 (table) | 3492 | 1.12× | 2.1 |
| HIP 105567 | SB1+Kervella | 76.4 | 0.237 | — (limit 63) | 2895 | 3348 | 1.16× | 2.9 |
| HIP 17154 | SB1+Kervella | 107.5 | 0.260 | — (limit 23) | 1298 | 1655 | 1.27× | 4.3 |
| HIP 44680 | SB1+Kervella | 66.3 | 0.059 | — (limit 18) | 1317 | 1561 | 1.18× | 5.2 |

## Issue #1: AstroSpectroSB1 K_1 inconsistency

All 5 AstroSpectroSB1 candidates show a **3–42× discrepancy** between the
K_1 predicted by Gaia's C, H Thiele-Innes spectroscopic elements and the
observed RV variability (peak-to-peak Gaia DR3 rv_amplitude_robust ÷ 2).

In contrast, the 4 SB1+Kervella candidates show K_1 obs / K_1 table within
12-28% — internally consistent.

**Three possible explanations** (we cannot distinguish from archival data alone):

(a) The Pourbaix C, H → K_1 formula has a different normalization than the
    one I used. If true, my K_1 (TI) estimate is systematically biased by
    ~3-40×, and the actual K_1 implied by Gaia's fit matches the observed
    RV. In that case all 5 candidates are clean.

(b) The Gaia AstroSpectroSB1 fits have known systematic issues at high RUWE
    (4-6 for our candidates) and the published C, H values do not accurately
    represent the true K_1. The orbit is real but the parameter posterior
    is biased.

(c) The orbits have additional unmodeled bodies or activity-driven RV
    jitter inflating the observed scatter. This would inflate K_1 obs but
    not K_1 TI.

In all three cases, the **a_phot-derived M_2 from Kepler** (independent of
K_1 and sin(i)) remains valid because the astrometric orbit's a_1 is a
direct geometric measurement.

## Issue #2: HIP 60321 unexpectedly filtered out

**HIP 60321 (Gaia DR3 6071451157905853312)** has:
- AstroSpectroSB1 significance = **92.9** (highest in our pool)
- HGCA Brandt 2024 chi² = **42.2** (strong independent PM anomaly)
- M_2 (Kepler) = **53.9 M_J** (BD-class)
- HIP-named, V≈11, K-dwarf at 50 pc
- e = 0.34 (moderate), P = 530 d

But was filtered out by the RUWE < 5 cut in our supplementary-pool vetting
(RUWE = 5.77). Same lesson as HIP 91479: RUWE > 1.4 is *expected* for
AstroSpectroSB1 sources.

**HIP 60321 is arguably a STRONGER candidate than HIP 91479**:
- Higher NSS significance (92.9 vs 32.2)
- Comparable HGCA corroboration (42.2 vs 50.3)
- Lower eccentricity (0.34 vs 0.81 — less hierarchical-triple-suspect)

## Updated promotion decisions

| Candidate | Pre-check verdict | Post-check verdict | Action |
|---|---|---|---|
| HIP 91479 | TIER 1A, promoted | TIER 1A with K_1 caveat | **keep promoted, update dossier with K_1 inconsistency notice** |
| HIP 60321 | excluded by RUWE filter | **TIER 1A** (highest sig + HGCA + BD-class Kepler) | **PROMOTE as 10th tentative substellar candidate** |
| 530277454305601920 (anon) | TIER 1B | TIER 1B, no independent HGCA verification | leave in supplementary; note K_1 inconsistency |
| 1398115488116027264 (anon) | TIER 1B | TIER 1B, large K_1 inconsistency 42× | leave in supplementary; note model concern |
| 6901280071143747968 (anon) | TIER 1B_anon | TIER 1B, K_1 inconsistency 30× | leave in supplementary |
| HIP 21449 (SB1+K) | TIER 2A | TIER 2A clean fit, mass-class M_2sin(i)=55 M_J | leave in supplementary (sin(i) ambiguity) |
| HIP 105567 (SB1+K) | TIER 2A | TIER 2A clean, M_2sin(i)=63 M_J | leave in supplementary |
| HIP 17154 (SB1+K) | TIER 2A | TIER 2A clean, M_2sin(i)=23 M_J | leave in supplementary (likely BD/planet at moderate i) |
| HIP 44680 (SB1+K) | TIER 2A | TIER 2A clean, M_2sin(i)=18 M_J + mild HGCA chi²=5.2 | leave in supplementary (likely BD/planet at moderate i) |

## HIP 91479 dossier correction

The original dossier claimed "predicted K_1 = 1.95 km/s ... matches observed
Gaia rv_amplitude_robust = 3.90 km/s exactly". This was incorrect — the
1.95 km/s was the INFERRED K_1 from the observed amplitude, not from the
Thiele-Innes fit. The Thiele-Innes K_1 prediction is only 574 m/s, leaving
a 3.4× unexplained excess in observed RV scatter. The astrometric M_2 = 64 M_J
remains the robust measurement; the spectroscopic interpretation is more
uncertain than the original dossier suggested.

## What's left to nail down

To resolve the K_1 inconsistency would require:
- Pulling Gaia DR3 per-transit RV (only published for the variability subset;
  most AstroSpectroSB1 sources are not in the public epoch RV table)
- A new RV epoch from a ground-based spectrograph to phase-fold against
  Gaia ephemeris and measure K_1 directly
- Gaia DR4 (Dec 2026) will publish per-transit RVs for all sources →
  decisive

For now: the astrometric mass measurements are robust; the spectroscopic
mass interpretations should be considered tentative.
