# Cascade test suite (v2)

Unit + regression tests for the v2 cascade (`scripts/streaming/v2_corrected/consumer_v2.py`).

## Run

```bash
pip install -r requirements.txt   # pytest, pandas, astropy, numpy
pytest tests/ -q
```

Fully offline — uses `scripts/web_tool/sample_data/hd1957_demo.parquet` and
in-test synthetic rows, no network access. ~0.2 s, 32 tests.

## Layout

```
tests/
├── conftest.py            # fixtures + adds scripts/streaming/v2_corrected to sys.path
├── data/test_pool.csv     # legacy v1 fixture (kept for the load-sanity test only)
├── test_filters_unit.py   # per-filter + per-correction unit tests
├── test_regressions.py    # pinned-source regressions
└── test_cascade_e2e.py    # end-to-end derive_row_v2 on the HD 1957 fixture
```

## Coverage

The suite targets the v2 cascade directly (the v1 pipeline modules it used
to import were removed in the repo decluttering):

- **`select_m1()`** — prefers Gaia FLAME mass over the 1.5 fallback (the
  systematic M_1 bias fixed 2026-05-28), with FLAME_spec + NaN fallbacks.
- **`solve_m2()`** — round-trips against the mass function and `K1_kms()`.
- **`mass_class()`** — the M_2 → class thresholds.
- **The three v2 corrections**, each unit-tested:
  - A: `select_plx()` prefers the NSS parallax over `gaia_source.parallax`
  - B: `filter32_v2()` uses K_obs = rv_amplitude_robust / 2
  - C: `filter30_v2()` logg fallback chain (gspphot → gspspec_ann → gspspec)
- **`tier_label()`** — demotion precedence.
- **Regressions**:
  - Gaia BH2 (5870569352746779008) → `dormant_BH_candidate` / Tier-1 BH (El-Badry+ 2023 params, offline)
  - HD 1957 (2543788153077017344) → F#30 K-giant chromatic demotion (bundled parquet)
  - Filter #29 SB2 rejection via `derive_row_v2`

## Adding tests

When you change a filter rule or fix a cascade bug, add a unit test in
`test_filters_unit.py` (thresholds) and a pinned-source regression in
`test_regressions.py`. Keep everything offline against the bundled fixtures.
