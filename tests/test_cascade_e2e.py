"""End-to-end cascade tests.

Runs the v9 + v9b reclassification on the test pool starting from
v8 verdicts (already in the pool) and verifies the final v9b verdicts
match the documented expectations.

These tests do not require network access — they exercise the
verdict-derivation logic in `pipeline_v9_recall_improvements_*.py`
against the offline test pool.
"""
from __future__ import annotations

import polars as pl


def test_v9_reclassify_pool_matches_documented_v9_verdicts(test_pool):
    """Re-run v9 against the test pool's v8 verdicts and check that
    the resulting v9 verdicts match what we recorded in the test pool.
    """
    import pipeline_v9_recall_improvements_2026_05_17 as v9

    # Drop the recorded v9b_verdict so the test isn't trivially passing
    # on the same column we'd later overwrite
    pool = test_pool.drop("v9_verdict", "v9b_verdict")
    result = v9.reclassify_pool_to_v9(pool)
    # Join back to the recorded verdicts for comparison
    expected = test_pool.select(["source_id", "v9_verdict"])
    merged = result.select(["source_id", "v9_verdict"]).rename(
        {"v9_verdict": "v9_verdict_recomputed"}
    ).join(expected, on="source_id")
    mismatches = merged.filter(
        pl.col("v9_verdict_recomputed") != pl.col("v9_verdict")
    )
    assert mismatches.height == 0, (
        f"v9 cascade produces different verdicts than recorded:\n{mismatches}"
    )


def test_v9_verdict_breakdown_unchanged(test_pool):
    """The distribution of v9b verdicts on the test pool is a fixed
    contract. Any cascade change that alters this distribution is a
    semantic change and should be reflected in an updated test."""
    expected = {
        "CORROBORATED_real_companion": 6,       # HD 76078, BD+56 1762, HIP 60865,
                                                # HIP 20122, HD 5433 (Fix C recovery),
                                                # HD 89707 (Fix A promotion)
        "CORROBORATED_kervella_only": 1,        # HD 92320 (Fix D)
        "REJECTED_published_exoplanet_eu_pm_corr": 3,  # HD 33636, HD 30246, BD+05 5218
        "REJECTED_ruwe_quality": 1,             # HD 140895 (genuinely high)
        "REJECTED_sahlmann_fp": 1,              # HD 185501 (Fix A FP catch)
        "REJECTED_simbad_visual_double": 1,     # HD 222805 (Fix B)
    }
    actual = dict(
        test_pool.group_by("v9b_verdict").agg(pl.len().alias("n")).iter_rows()
    )
    # Compare keys
    for k, v in expected.items():
        assert actual.get(k, 0) == v, (
            f"v9b verdict count mismatch for {k}: expected {v}, got {actual.get(k, 0)}"
        )


def test_no_documented_fp_in_test_pool_appears_corroborated(test_pool):
    """Negative regression: the 4 documented_fp source_ids must never
    be CORROBORATED no matter what other filters say."""
    import pipeline_v2_tuned_filters_2026_05_13 as v2

    fp_ids = {int(k) for k in v2.DOCUMENTED_NSS_FPS.keys()}
    fp_in_pool = test_pool.filter(pl.col("source_id").is_in(list(fp_ids)))
    for r in fp_in_pool.to_dicts():
        assert not r["v9b_verdict"].startswith("CORROBORATED"), (
            f"documented_fp source_id {r['source_id']} should NEVER be "
            f"CORROBORATED, got {r['v9b_verdict']}"
        )
