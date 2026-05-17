# Cascade Test Suite

Regression and unit tests for the filter cascade. Designed to prevent
silent failures of the type that affected Filter #28 from v1.0.0 through
v1.7.0 (the silent no-op caused by missing ra/dec columns in the
production pool).

## What's here

```
tests/
├── conftest.py            # Shared fixtures (test pool loader, known IDs)
├── data/
│   └── test_pool.csv      # Curated 13-row slice of v9b_scan_full_pool.csv
├── test_filters_unit.py   # Per-filter unit tests
├── test_regressions.py    # Bug-history regression tests (one per past flaw)
├── test_cascade_e2e.py    # End-to-end cascade run on the test pool
└── README.md              # This file
```

## How to run

From the repo root:

```bash
pip install pytest polars astropy
pytest tests/ -v
```

No network access required; the suite is fully offline against
`tests/data/test_pool.csv`.

## What the test pool covers

The 13-source pool is hand-picked to exercise every cascade filter
path that has been modified or fixed in v1.8+:

| Source | What it tests |
|---|---|
| HD 185501 | Sahlmann CONFIRMED_BINARY_FP rejection (v1.9.0 Fix A) |
| HD 33636 | Filter #28 PM-corrected at 9.7" raw → 6.8" corrected (v1.8.0) |
| HD 30246, BD+05 5218 | Filter #28 standard catches (v1.8.0) |
| HD 222805 | SIMBAD `**` visual-double rejection (v1.9.0 Fix B) |
| HD 92320 | Kervella-substitute-for-HGCA short-period promotion (v1.9.0 Fix D) |
| HD 5433 | Conditional RUWE verdict-logic re-sync (v1.9.0 Fix C) |
| HD 89707 | FLAG → CORROBORATED via Sahlmann promotion (v1.9.0 Fix A) |
| HD 76078, BD+56 1762 | v1.8.0 headline candidates (negative control) |
| HIP 60865, HIP 20122 | M-dwarf headline candidates (negative control) |
| HD 140895 | High-χ² REJECTED_hgca_stellar (negative control on the inner orbit; outer is in multi-body category) |

## Adding new tests

When you fix a cascade bug or change a filter rule:

1. **Add a regression test** in `test_regressions.py` that pins down the
   specific bug. Reference the version it was fixed in.
2. **If the rule has thresholds** (e.g., chi^2 tier boundaries, RUWE
   cuts), add a unit test in `test_filters_unit.py` that explicitly
   checks the numeric thresholds. Threshold drift in the wrong direction
   silently changes the candidate list.
3. **Update `test_cascade_e2e.py`** if the change alters the verdict
   distribution on the test pool.

## What the suite does NOT cover (yet)

* The Stage 1 substellar selection (parallax, RUWE, significance pre-cuts).
  The test pool starts from v8 outputs, so Stage 1 is implicit.
* The Halbwachs DPAC cross-match — needs the full Halbwachs catalog or
  a slice committed to `tests/data/`.
* The multi-body Kervella PMa pipeline for the 4 multi-body candidates.
* Network-fetching code paths (Vizier TAP, Gaia TAP, SIMBAD). These
  are exercised by the production scripts; the tests use cached data.

Adding any of these is a worthwhile follow-up.
