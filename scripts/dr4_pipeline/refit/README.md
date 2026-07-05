# DR4 candidate re-fit engine (`scripts/dr4_pipeline/refit/`)

**Lane #116.** When Gaia **DR4** lands (~2 Dec 2026) it will publish, for the
first time, the **per-transit (epoch) astrometric time series** that DR3
withheld — plus a re-derived, longer-baseline `nss_two_body_orbit`. This engine
**re-fits each standing candidate's photocentric orbit directly from the
along-scan measurements**, decides **single-body vs multi-body** (clean orbit vs
hierarchical triple / 2nd companion), and applies the **pre-registered
confirm/refute thresholds** in `docs/dr4_preregistration_2026_06_01.md`.

DR4 is **not out yet**, so the engine is built and tested entirely on
**synthetic** DR4-like epoch data. A thin **adapter** isolates every assumption
about DR4 column names so that only one file changes once ESA publishes the
datamodel. (A sibling agent owns `scripts/dr4_pipeline/rehunt/`; this directory
writes only under `refit/`.)

---

## How it works

Gaia is a scanning instrument: each transit measures the star's position
essentially along **one** direction (the scan, at angle ψ). The measured
quantity is the **along-scan (AL) abscissa**

```
w = Δα* sinψ + Δδ cosψ + ϖ·f_par(t) + μα*·(t−t₀)sinψ + μδ·(t−t₀)cosψ + w_orbit
```

with the 5 standard astrometric parameters (Δα*, Δδ, ϖ, μα*, μδ) and the
photocentric **orbit** term in Thiele-Innes form
`Δα*_orb = B·X + G·Y`, `Δδ_orb = A·X + F·Y`, where `X=cosE−e`, `Y=√(1−e²)sinE`
and E solves Kepler's equation `E − e sinE = 2π(t−T0)/P`.

The fit is **linear** in the 5 astrometric params + (A,B,F,G) at fixed
(P,e,T0); we solve that 9-column (or 13-/10-column) system in closed form inside
a `scipy.least_squares` (TRF, an LM-class trust-region method) loop over only
the **non-linear** period parameters. A coarse period pre-scan gives a robust
start.

After the fit, `a_phot` and inclination come from the **vetted, repo-canonical**
relations (mirroring `scripts/streaming/v2_corrected/consumer_v2.py`):

```
u = ½(A²+B²+F²+G²),  v = A·G − B·F
a_phot = √( u + √(u²−v²) )
cos i  = |A·G − B·F| / a_phot²        # NO sqrt — see the 2026-05-31 bugfix
```

> **The cos-i relation has no `sqrt`.** A 2026-05-31 audit found a spurious
> `sqrt` wrapping the Campbell relation in three deep-dive scripts (it biased i
> face-on; true 46° → buggy 33.5°). `A·G − B·F = a²cos i`, so
> `cos i = |A·G − B·F| / a²` directly. `test_refit.py::test_cosi_has_no_sqrt`
> guards this by forward construction.

### Multi-body hypothesis (the triple / 2nd-companion test)

Two complementary complex models are fit and compared to the 1-body fit:

| Model | Extra parameters | What it catches |
|---|---|---|
| **1-body + acceleration** (`fit_accel`) | barycentric accel (and optional jerk), AL-projected | a distant outer body whose **P ≫ baseline** → a smooth curvature. Cheap, robust. |
| **double Keplerian** (`fit_two_body`) | a full **outer Keplerian** (A₂,B₂,F₂,G₂,P₂,e₂,T0₂) | an outer period **comparable to the baseline** — the explicit hierarchical-triple model. |

`modelselect.select_model` fits all three and returns a verdict
`{single | multi | inconclusive}` using:

- **ΔBIC** (and ΔAIC): `BIC(1body) − BIC(complex)`; > +10 strongly favours the
  complex model (Kass & Raftery 1995).
- a nested-model **F-test** on the χ² drop (p-value from the F survival function),
- the **acceleration SNR** (linear error propagation through `(AᵀWA)⁻¹`),
- the Gaia-style **F2** goodness-of-fit of the 1-body model
  (Wilson–Hilferty; the pre-registered quantity).

A verdict is `multi` only when BIC **and** the F-test **and** (for accel) the 5σ
acceleration-SNR pre-reg bar all agree, and (for the 2nd Keplerian) the outer
amplitude is a real fraction of the inner — so noise alone cannot manufacture a
triple.

---

## The DR4 column-mapping seam (`adapter.py`)

**This is the only place DR4 column names enter.** The fitter, selector, and
decision logic consume a canonical internal `EpochData`
(`t, w, psi, par_factor, sigma`) and never see a DR4 column name.

`adapter.DEFAULT_EPOCH_MAP` holds best-guess DR4 epoch-table column names
(DR3-style conventions extended to the expected DR4 product):

```python
DEFAULT_EPOCH_MAP = {
  't':          ['t_tcb','obs_time','epoch','time','transit_time','t_obs'],
  'w':          ['abscissa_al','w_al','al_obs','centroid_al','abscissa'],
  'psi':        ['scan_angle','psi','theta_scan','position_angle_scan'],
  'par_factor': ['parallax_factor_al','plx_factor_al','parallax_factor','ppfact_al'],
  'sigma':      ['sigma_al','abscissa_error_al','al_error','w_error','centroid_al_error'],
}
```

**When DR4 publishes the real datamodel (Step 0 in the pre-registration plan),
you update only this dict** — or pass the resolved names at call time without
touching code:

```python
ep = epoch_table_to_epochdata(dr4_table,
        column_map={'t':'tcb_time','w':'al_residual','psi':'scan_pa',
                    'par_factor':'parallax_factor_al','sigma':'al_err'},
        psi_unit='deg')   # set to whatever the datamodel says
```

`epoch_table_to_epochdata` accepts a pandas DataFrame, an astropy Table, or a
dict-of-arrays; it raises a clear `KeyError` listing the available columns if a
required field is missing. `normalize_nss_row` does the analogous best-effort
normalisation for a DR4 `nss_two_body_orbit` row (the cascade re-run consumes
that; the cascade itself lives in the sibling `rehunt/`).

> **DR4 assumptions (shared with rehunt / lane #117 — keep consistent):**
> (a) an epoch-astrometry table keyed by `source_id` with, per transit,
> `(t_obs, abscissa_AL, scan_angle, parallax_factor_AL, sigma_AL)`; (b) an
> expanded `nss_two_body_orbit`. The AL abscissa is treated as the modelled AL
> coordinate; if DR4 instead publishes AL **residuals** w.r.t. a reference
> solution, add the reference back in the adapter (one line) — the fitter is
> agnostic.

---

## How to run

```bash
PY=/Users/legbatterij/claude_projects/ostinato/.venv/bin/python

# Tests (end-to-end, synthetic) — proves the pipeline works today:
cd scripts/dr4_pipeline/refit
$PY -m pytest test_refit.py -q          # or:  $PY test_refit.py

# Day-one driver, synthetic "headline-true" world, all 4 candidates:
$PY run.py --demo --json-out /tmp/dr4_refit_demo.json

# On DR4 day — a real epoch table for one candidate (pulled to /tmp by the
# Step-1 TAP query in the pre-registration doc):
$PY run.py --source-id 332248057157474176 \
           --epoch-table /tmp/dr4_wdj020915_epochs_2026_12_02.parquet \
           --parallax 11.94 --m1 0.718 --psi-unit rad \
           --json-out /tmp/dr4_reanalysis_wdj020915.json
```

`run.py` prints, per candidate, the DR3 anchor → DR4 1-body/accel/2-body fit →
the pre-registered verdict, and emits a machine-readable dict for the main
thread to integrate into `CANDIDATES.md` / dossiers. **This engine writes only
to `/tmp` / stdout and does not edit `docs/`** (per the repo single-writer
guardrail).

---

## Per-candidate pre-registered decision table

Thresholds are transcribed verbatim into `prereg.PREREG` from
`docs/dr4_preregistration_2026_06_01.md` (frozen 2026-06-01) and
**cross-checked at test time** against the doc's anchor line
(`prereg.audit_against_doc`, asserted by `test_prereg_matches_doc`) so the
constants cannot silently drift.

| Candidate (DR3 source_id) | M₁ used | DR3 anchor | **CONFIRM** | **REFUTE / DOWNGRADE / PARK** |
|---|---|---|---|---|
| **WG 26** `6092654861665006592` | 0.62 | a_phot 5.40, i 77.1°, F2 −1.11 | single-Kepler F2 ≤ +2 **AND** a_phot within 3σ of 5.40 **AND** no accel/2nd-period > 5σ → clean sub-Ch DWD (M₂≈0.65) | accel/2nd-period > 5σ **OR** F2 > +5 → **REFUTE → triple** |
| **WDJ020915** `332248057157474176` *(the headline)* | 0.718 | a_phot 7.73, F2 **+8.39**, RUWE 8.79 | F2 collapses ≤ +2 **AND** a_phot within 3σ of 7.73 (**M₂ ≥ 1.2**) **AND** no 2nd-period/accel > 5σ → real M_tot>M_Ch single companion | 2nd-period/accel > 5σ → **REFUTE (triple)**; refined **M₂ < 1.2** → **DOWNGRADE** (sub-Ch DWD); F2 still > +5 → **PARK** |
| **WDJ060042** `2909342818326298112` | 0.612 | a_phot 19.62, i 66.4°, F2 +0.79; π 10.24 vs 12.08 | F2 ≤ +2 **AND** a_phot within 3σ of 19.62 **AND** no 2nd-period/accel > 5σ → M_tot>M_Ch single companion; **super-Chandra companion if refined M₂ > 1.40** | refined **M₂ < 1.33** → **DOWNGRADE** (sub-Ch DWD); 2nd-period/accel > 5σ → **REFUTE (triple)** |
| **UCAC4 313** `5612039087715504640` | 0.23 | a_phot 1.32, e 0.214, **i undetermined** | DR4-measured **sin i ≥ 0.85 (i ≥ 58°)** → M₂ ≤ ~15 M_J → **substellar** (planetary if i ≳ 80° → < 13 M_J) | **i ≤ 45°** → M₂ ≥ ~18–20 M_J (high-mass BD; headline refuted); **M₂ ≥ 0.075 M⊙** → it is a **star** (fully refuted) |

**What DR4 cannot settle** (flagged automatically in the `followup` field):
for **WDJ020915** and **WDJ060042** the **companion class** (cool WD vs dormant
NS) stays open after DR4 — K₁ is identical and the SED is degenerate — so a
CONFIRM verdict's action item is **HST/COS FUV**, not more astrometry. For
**UCAC4 313** a CONFIRM at the BD/star boundary may want a ground spectrum
(CARMENES/NIRPS) to *type* a luminous secondary.

Mass chain: M₂ comes from the **photocentric mass function**
`f(M)=a_phot_AU³/P_yr²` inverted at the candidate's real M₁ — using the
**DR4-fit** `a_phot` and `i`, *not* the DR3 Thiele-Innes. (Bisection +
`mass_class` mirror the vetted `consumer_v2` cascade.)

> **Knife-edge note (WDJ020915).** At the bare anchors (a_phot 7.73, M₁ 0.718,
> P 274.52) the photocentric inversion gives M₂ = 1.223 — sitting *on* the 1.2
> M⊙ NS floor (the doc's realistic 1.322 uses the full-TI-covariance MC,
> marginally higher). So the CONFIRM/DOWNGRADE boundary is genuinely sharp;
> the synthetic CONFIRM test injects a_phot = 8.0 (M₂ ≈ 1.30, within 3σ of 7.73)
> to exercise the wiring in the "headline-true" world.

---

## Day-one self-validation against the labeled false-positive registry

Before the engine's *new* DR4 verdicts are trusted, it must first reproduce the
correct **skeptical** verdict on every false positive the project already
documented. `fp_registry.py` is that corpus — a **source_id-keyed, ledger-sourced
list of the campaign's own retractions** (harvested from `RESEARCH_LOG.md`,
`CANDIDATES.md`, the per-object journals and `CITATION.cff`, **not** from
memory), classified by `fp_class` and by the `owning_subsystem` responsible for
catching each. This engine owns the `dr4-refit-astrometric` slice; photometric
(CV-period, ellipsoidal), SB2/luminous-binary and pure crossmatch FPs are
recorded for completeness but guarded elsewhere.

`test_fp_selfvalidation.py` turns each astrometric FP into a synthetic-DR4
assertion — e.g. the cos-i sqrt bug must not inflate M₂ across Chandra; the
rv/2→sin-i deprojection must not turn an NS-mass into a fake mass-gap BH (the
5858574 signature: direct M₂≈1.55 vs the retracted 2.82); a hierarchical triple
must be flagged `multi` (5858574 / HD 75567 / 2127900); a weak-fit WDJ020915
must PARK not CONFIRM, and a low-mass one DOWNGRADE; WDJ060042 must not claim
super-Chandra at M₂≈1.37; a near-face-on orbit must REFUTE (stellar, TYC 4562 /
UCAC4 class); and the WDJ205650 mass-join bug (default M₁=1.5 → the retracted
super-Chandra M_tot≈2.06 artifact vs the real sub-Chandra 0.64) must not recur.

Run the gate standalone, or it runs **automatically before the real day-one
analysis** (abort on failure, `--skip-self-validate` to override):

```bash
$PY run.py --self-validate               # explicit gate, exits 0/1
$PY -m pytest test_fp_selfvalidation.py -q
```

## Files

| File | Role |
|---|---|
| `model.py` | Forward AL model; Kepler solver; 1-body / `+accel` / 2-body fitters; vetted a_phot & cos-i (no-sqrt) helpers; `abfg_from_geometry` (Campbell→TI, for synth/tests). |
| `modelselect.py` | 1-body vs multi-body: ΔBIC/ΔAIC, F-test, accel-SNR, F2 → `{single,multi,inconclusive}`. |
| `prereg.py` | Per-candidate frozen thresholds (`PREREG`); `decide()` wiring; mass-function chain; doc cross-check (`audit_against_doc`). |
| `synth.py` | Synthetic DR4-like epoch data: 5.5-yr baseline, visibility-window cadence, varied scan angles, AL parallax factor, G→σ_AL; `CANDIDATE_TRUTH` anchors. |
| `adapter.py` | **The DR4 column-mapping seam.** `epoch_table_to_epochdata`, `normalize_nss_row`. |
| `fp_registry.py` | **Labeled false-positive corpus** — the campaign's own ledger-sourced retractions (source_id-keyed), classified by `fp_class` / `owning_subsystem`; `astrometric_cases()`, `validate_registry()`. |
| `run.py` | Day-one driver: epoch table → fit → model-select → pre-registered verdict (`--demo` for today; `--self-validate` runs the FP gate; the gate runs automatically before a real analysis). |
| `test_refit.py` | End-to-end synthetic tests (8). |
| `test_fp_selfvalidation.py` | **FP self-validation** (11): registry integrity + completeness + every astrometric FP reproduced with its correct skeptical verdict; `run_self_validation()` is the day-one gate entry point. |

Stdlib + numpy + scipy only (pandas/astropy used only by `run.py` for reading
parquet/fits epoch tables; the engine core does not require them).

## References

- Halbwachs+ 2023 (Gaia DR3 NSS, Thiele-Innes / Campbell, A·G−B·F = a²cos i).
- Lindegren+ 2021 (Gaia EDR3 astrometric model; AL observation equation, σ_AL).
- Kass & Raftery 1995 (BIC / ΔBIC interpretation).
- `docs/dr4_preregistration_2026_06_01.md` — the frozen thresholds this engine
  encodes; [ESA Gaia DR4](https://www.cosmos.esa.int/web/gaia/dr4).
