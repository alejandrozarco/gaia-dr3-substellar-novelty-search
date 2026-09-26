# WD-binary full-Thiele-Innes-covariance MC mass re-derivation — regeneration of the deleted 2026-05-31 report

**Date:** 2026-06-10 (run 2026-06-09/10)
**Purpose:** The DR4 pre-registration (`docs/dr4_preregistration_2026_06_01.md`) and the 2026-05-31
framing correction (`docs/CANDIDATES.md`, both WD dossiers, both object journals) anchor their
WD-binary companion masses to `/tmp/wd_sed_mass_refinement_2026_05_31.md`, which was deleted.
This report regenerates those numbers from the Gaia archive + the repo's vetted code chain and
adjudicates REPRODUCED / DISCREPANT against the published-in-repo anchors.

**Targets**
| Object | Gaia DR3 source_id | M1 prior (GF21 DA, per pre-registration) | NSS solution |
|---|---|---|---|
| WDJ020915+380425 | `332248057157474176` | 0.718 ± 0.053 M⊙ | Orbital, P≈274.5 d, sig 67.3, **F2=+8.39 (weak fit)** |
| WDJ060042-293041 | `2909342818326298112` | 0.612 ± 0.050 M⊙ | Orbital, P≈935 d, sig 20.6, F2=+0.79 (clean) |

**Expected anchors (published in repo):**
WDJ020915 M2 = 1.32 [1.27–1.38] M⊙, P(M2>1.4) = 8.6%;
WDJ060042 M2 = 1.37 [1.23–1.52] M⊙, P(M2>1.4) = 41%.

---

## 1. Headline result — both anchors REPRODUCED

| Object | Anchor M2 [16/50/84] | Regenerated M2 [16/50/84] | Anchor P(>1.4) | Regenerated P(>1.4) | Verdict |
|---|---|---|---|---|---|
| WDJ020915 | 1.32 [1.27–1.38] | **1.322 [1.267–1.379]** | 8.6% | **8.7%** | **REPRODUCED** |
| WDJ060042 | 1.37 [1.23–1.52] | **1.368 [1.229–1.521]** | 41% | **41.4%** | **REPRODUCED** |

Secondary anchors also reproduced (all within rounding / MC noise):
- WDJ020915: f(M) = 0.556 [0.528–0.584] vs prereg 0.556 [0.53–0.585]; M_tot = 2.041 ± 0.101 vs 2.04 ± 0.10.
- WDJ060042: f(M) = 0.653 [0.553–0.768] vs prereg 0.653 [0.55–0.77]; M_tot = 1.981 ± 0.167 vs 1.98 ± 0.17.
- The pre-registration's **"conservative full-TI MC"** numbers are reproduced by the raw
  full-covariance MC (budget RAW below): WDJ020915 a_phot 95% CI **7.67–22.69 mas** (prereg "7.7–22.6"),
  M2 97.5th pct **15.4** (prereg "up to 15.2"), P(M2>1.4) = **84.6%** (prereg "85%");
  WDJ060042 a_phot 95% CI **19.03–44.14** (prereg "19.0–44.2"), M2 97.5th pct **8.58** (prereg "up to 8.6").

**Method identification (a finding of this regeneration).** The deleted report's "realistic budget"
(the anchor numbers) corresponds to: delta-method σ(a_phot) propagated through the **full
Thiele-Innes 4×4 covariance** (from `corr_vec`), then **independent** Gaussian MC over
(a_phot, π_NSS, P) × Gaussian M1 prior. Its "conservative" variant corresponds to raw MC sampling
of all 12 fitted NSS parameters from the full covariance. Both regenerate exactly (§4).

---

## 2. Data — Gaia archive query

Single ADQL query via `astroquery.gaia` (run 2026-06-09; archive returned both rows):

```sql
SELECT * FROM gaiadr3.nss_two_body_orbit
WHERE source_id IN (332248057157474176, 2909342818326298112)
```

Both rows: `nss_solution_type='Orbital'`, `bit_index=8191`, `corr_vec` length 66 → 12 fitted
parameters. **The corr_vec correlation vector was retrieved and used — no diagonal fallback;
the result is NOT degraded.** Raw rows archived at `/tmp/wd_ti_mc/nss_rows.json`.

Key retrieved values (match the dossiers):

| Param | WDJ020915 | WDJ060042 |
|---|---|---|
| parallax (π_NSS, mas) | 11.3761 ± 0.0905 | 12.0830 ± 0.1637 |
| A_TI (mas) | −0.418 ± **5.323** | 18.912 ± 2.026 |
| B_TI (mas) | −6.042 ± 4.668 | −5.102 ± 6.682 |
| F_TI (mas) | 4.312 ± 0.541 | 2.965 ± **17.071** |
| G_TI (mas) | 3.810 ± **7.426** | 7.361 ± 4.460 |
| period (d) | 274.518 ± 0.671 | 935.136 ± 31.473 |
| eccentricity | 0.0242 ± 0.0314 | 0.0380 ± 0.0232 |
| significance / F2 | 67.33 / +8.39 | 20.59 / +0.79 |

(Bold: the "unconstrained" TI components flagged in the pre-registration — error ≫ value.)

## 3. Method & code path (vetted chain, reused by import)

1. **Covariance build:** `nsstools 0.1.12` (CDS / Halbwachs; installed to `/tmp/nsstools_lib`,
   no repo/ostinato pollution) — `NssSource(...).covmat()` decodes `corr_vec` with the official
   Orbital parameter order `[ra, dec, parallax, pmra, pmdec, A, B, F, G, ecc, period, t_periastron]`
   (upper-triangle, column-wise) into the full 12×12 covariance Σ. Correlation-matrix eigenvalue
   checks: min eig = +5.4e-05 (WDJ020915), +2.8e-05 (WDJ060042) → already PSD, **no eigen-clipping
   needed**.
2. **Geometry:** `scripts/dr4_pipeline/refit/model.py` → `photocentric_a` (Halbwachs+2023
   a = √(u+√(u²−v²))) and `inclination_from_ABFG` (**cos i = |AG−BF|/a², the 2026-05-31 no-sqrt
   bugfix**), imported directly from the repo.
3. **Mass inversion:** `scripts/streaming/v2_corrected/consumer_v2.py` → `solve_m2` (80-iteration
   bisection of M2³/(M1+M2)² = f(M) on [1e-4, 1e3] — exact to machine precision; "resolve the
   cubic exactly" satisfied). Photocentric f(M) = (a_phot/π)³ / P_yr² used **directly** —
   dark companion ⇒ no flux correction, no sin-i inflation (project guardrail).
4. **Vectorised shims** (for 200k-draw speed) were verified against the vetted scalar functions
   on 500 random points before use: max|Δa_phot| = 0, max|Δcos i| = 2.8e-16, max|ΔM2| = 0.
5. **MC:** N = 200,000 draws per budget per object (≥ the required 50,000), seed 20260531
   (`numpy.random.default_rng`). M1 ~ N(M1₀, σ_M1) truncated at 0.1 M⊙ (0 draws hit the
   truncation). Non-physical draws (π≤0, P≤0, a≤0) rejected: **0 in every budget**.
6. **Parallax convention:** NSS-internal parallax (the parameter co-fitted with the orbit, with
   its corr_vec correlations), per dossier §4.1 — not the gaia_source single-star parallax.

Error budgets run:
- **RAW** — all 12 params sampled from N(mean, Σ_full); a_phot, cos i per draw from (A,B,F,G).
- **LIN** — delta-method: Jacobian of [a_phot, π, P] w.r.t. the 12 params (central differences
  through the vetted `photocentric_a`), 3×3 covariance = JΣJᵀ **including cross-correlations**;
  Gaussian MC on the 3-vector.
- **LIN-IND** — same delta-method σ(a_phot), but (a_phot, π, P) sampled **independently**
  (this is the anchor method).
- **DIAG** — RAW with all correlations zeroed (control; shows what corr_vec buys).

Delta-method σ(a_phot) from the full TI covariance: **0.115 mas** (WDJ020915; prereg quotes
a_phot = 7.73 ± 0.12) and **0.953 mas** (WDJ060042; prereg quotes 19.62 ± 0.95) — both reproduce
the published a_phot errors.

## 4. Results

Point estimates through the vetted chain (validation vs dossiers):

| | a_phot (mas) | i (deg) | f(M) (M⊙) | M2 at M1₀ |
|---|---|---|---|---|
| WDJ020915 | 7.7319 (dossier 7.732) | 65.85 (dossier 65.85) | 0.5558 (dossier 0.5558) | 1.323 (dossier 1.323) |
| WDJ060042 | 19.6156 (dossier 19.616) | 66.35 (dossier 66.35) | 0.6527 (dossier 0.6527) | 1.368 (dossier 1.368) |

### WDJ020915+380425 (332248057157474176) — M1 = 0.718 ± 0.053

| Budget | M2 [16/50/84] | M2 95% | P(>1.2) | P(>1.33) | P(>1.4) | M_tot [16/50/84] | i [16/50/84] deg |
|---|---|---|---|---|---|---|---|
| **LIN-IND (anchor)** | **1.267 / 1.322 / 1.379** | 1.214–1.434 | 0.987 | 0.446 | **0.087** | 1.940 / 2.041 / 2.141 | (65.85 point) |
| LIN (corr.) | 1.267 / 1.322 / 1.378 | 1.214–1.434 | 0.987 | 0.446 | 0.085 | 1.940 / 2.041 / 2.141 | (65.85 point) |
| RAW (conservative) | 1.405 / 2.169 / 5.604 | 1.286–15.42 | 0.999 | 0.934 | 0.846 | 2.131 / 2.891 / 6.325 | 65.2 / 65.8 / 66.5 |
| DIAG (control) | 1.255 / 2.787 / 6.299 | 0.680–13.30 | 0.854 | 0.821 | 0.803 | 1.972 / 3.506 / 7.018 | 57.8 / 73.6 / 84.9 |

### WDJ060042-293041 (2909342818326298112) — M1 = 0.612 ± 0.050

| Budget | M2 [16/50/84] | M2 95% | P(>1.2) | P(>1.33) | P(>1.4) | M_tot [16/50/84] | i [16/50/84] deg |
|---|---|---|---|---|---|---|---|
| **LIN-IND (anchor)** | **1.229 / 1.368 / 1.521** | 1.105–1.683 | 0.887 | 0.602 | **0.414** | 1.819 / 1.981 / 2.154 | (66.35 point) |
| LIN (corr.) | 1.286 / 1.367 / 1.448 | 1.209–1.529 | 0.981 | 0.675 | 0.342 | 1.864 / 1.979 / 2.095 | (66.35 point) |
| RAW (conservative) | 1.420 / 1.853 / 3.714 | 1.312–8.585 | 1.000 | 0.961 | 0.871 | 2.031 / 2.470 / 4.331 | 65.9 / 66.5 / 67.1 |
| DIAG (control) | 1.460 / 2.139 / 3.962 | 1.102–8.685 | 0.951 | 0.903 | 0.871 | 2.068 / 2.755 / 4.575 | 61.2 / 75.3 / 85.4 |

### Anchor comparison

| Object | Quantity | Anchor | Regenerated (LIN-IND) | Δ | Verdict |
|---|---|---|---|---|---|
| WDJ020915 | M2 median | 1.32 | 1.322 | +0.002 | REPRODUCED |
| WDJ020915 | M2 16/84 | 1.27 / 1.38 | 1.267 / 1.379 | ≤0.003 | REPRODUCED |
| WDJ020915 | P(M2>1.4) | 8.6% | 8.7% | +0.1 pt | REPRODUCED |
| WDJ060042 | M2 median | 1.37 | 1.368 | −0.002 | REPRODUCED |
| WDJ060042 | M2 16/84 | 1.23 / 1.52 | 1.229 / 1.521 | ≤0.001 | REPRODUCED |
| WDJ060042 | P(M2>1.4) | 41% | 41.4% | +0.4 pt | REPRODUCED |

All deviations are far inside MC noise (σ_MC of a 200k-draw median ≈ 0.0002 M⊙; the quoted
anchors are rounded to 2 decimals / whole percent). **No DISCREPANT entries.**

### Implied inclination

The full-covariance (RAW) draws give remarkably tight i posteriors despite the individually
unconstrained TI components — the correlations constrain the combination AG−BF:
i = 65.8 [65.2–66.5]° (WDJ020915), 66.5 [65.9–67.1]° (WDJ060042); both match the catalog point
values (65.85°, 66.35°) and keep both systems firmly non-eclipsing. The DIAG control destroys
this (i smeared 58–85°), confirming the corr_vec is doing real work.

## 5. Interpretation & caveats (unchanged science, now with provenance)

1. **Why two budgets, and which to trust.** The raw full-covariance MC (RAW) is biased high in
   a_phot because a_phot is a positive-folded statistic of nearly-unconstrained components
   (A = −0.42 ± 5.32, G = +3.81 ± 7.43 for WDJ020915; F = +2.96 ± 17.07 for WDJ060042): noise can
   only inflate it. The pre-registration already adjudicated this as the "conservative" reading;
   the anchor/realistic budget linearises around the catalog point estimate (the NSS fit itself
   is the maximum-likelihood point). DR4 epoch astrometry is the pre-registered arbiter.
2. **A genuine nuance found while regenerating:** the anchor budget sampled (a_phot, π, P) as
   *independent* Gaussians. Keeping their cross-correlations (LIN budget) leaves WDJ020915
   unchanged but **tightens WDJ060042 to M2 = 1.367 [1.286–1.448], P(M2>1.4) = 34%** — the
   published 41% straddle probability is therefore mildly conservative (correlation-neglect
   widens the interval ~1.9×σ→…, 16–84 half-width 0.146 vs 0.081). Direction of the published
   number is safe (it overstates, not understates, the uncertainty).
3. WDJ020915's mass remains **provisional** regardless of budget: F2 = +8.39 / RUWE 8.79 mean the
   per-epoch errors are likely underestimated or a non-Keplerian term exists; no error inflation
   was applied here (matching the original). The pre-registered DR4 confirm/refute thresholds
   are unaffected.
4. WDJ060042 carries the 2.8σ GS-vs-NSS parallax tension (10.24 vs 12.08 mas); this analysis
   uses π_NSS = 12.083 throughout (as the original did). Using the GS parallax would *raise* M2
   (f ∝ π⁻³) — another reason the anchor is not an overclaim.
5. M1 priors are GF21 DA-fit values with the pre-registration's σ (0.053 / 0.050); the framing
   correction conventions of `docs/CANDIDATES.md` (lines 100–103) apply: these are long-period
   M_tot > M_Ch DD / WD+NS binaries, **not** super-Chandrasekhar WDs and **not** Type-Ia
   progenitors (no Hubble-time merger at P = 275 / 935 d).

## 6. Reproducibility

- Scripts: `/tmp/wd_ti_mc/fetch_nss.py` (query), `/tmp/wd_ti_mc/mc_masses.py` (RAW/DIAG/LIN),
  `/tmp/wd_ti_mc/mc_linind.py` (anchor budget), `/tmp/wd_ti_mc/make_outputs.py` (CSV).
- Inputs: `/tmp/wd_ti_mc/nss_rows.json` (raw archive rows incl. corr_vec);
  full numeric results `/tmp/wd_ti_mc/mc_results.json`.
- Outputs: this file + `/tmp/wd_ti_mc_regen_2026_06_10.csv` (per-object × per-budget summary).
- Python: `~/claude_projects/ostinato/.venv/bin/python`; nsstools 0.1.12 in
  `/tmp/nsstools_lib` (pip `--target`, `--no-deps`); seed 20260531; N = 200,000/budget.
- Vetted repo code consumed read-only by import:
  `scripts/dr4_pipeline/refit/model.py` (`photocentric_a`, `inclination_from_ABFG`),
  `scripts/streaming/v2_corrected/consumer_v2.py` (`solve_m2`).
