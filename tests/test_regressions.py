"""Regression tests for specific cascade bugs we have identified and
fixed. Each test pins down a past failure mode so it cannot silently
recur.

The bug-history this file enforces:

  * v1.0.0–v1.7.0 — Filter #28 (exoplanet.eu coord cross-match) was a
    silent no-op because ra/dec was never propagated into the
    production candidate pool. The else-branch always fired.

  * Pre-v1.9.0 — RUWE verdict labels drifted from the conditional
    RUWE rule introduced post-v2. Sources with ruwe_pass=True under
    the conditional rule still carried the historical REJECTED_ruwe
    label.

  * Pre-v1.9.0 — HD 185501 was CORROBORATED in v8 even though
    Sahlmann 2025 lists it as CONFIRMED_BINARY_FP. No filter
    rejected on the Sahlmann FP tag.

  * Pre-v1.9.0 — Short-period orbits whose 25-yr HGCA arc averages
    out (HD 92320 at P=145d, HGCA chi^2=2.25) were SURVIVOR even
    when Kervella's 10-yr arc retained the wobble (Kervella SNR=6).

  * Pre-v1.9.0 — Resolved visual binaries (HD 222805, SIMBAD obj
    type=`**`) were not filtered.

  * v1.10.0 — The cascade's M_1 default of 0.09 M_sun (for sources
    without SpType, calibrated for M dwarfs) was applied unmodified
    to a SIMBAD WD* source, producing a spurious substellar M_2.
    Now corrected to ~0.6 M_sun for WD hosts (v1.13.0 manual fix).
"""
from __future__ import annotations

import polars as pl
import pytest


def test_filter28_pool_has_ra_dec_or_auto_fetches(test_pool):
    """The v8 pool (and any pool fed to Filter #28) must EITHER
    contain ra/dec columns OR the filter must auto-fetch them.
    The v1.0.0–v1.7.0 silent failure was caused by the filter
    falling through to else-branch when ra/dec were missing,
    silently returning False for every source.

    Regression check: assert that the test pool has ra/dec
    populated. (The auto-fetch path is exercised in integration
    tests requiring network access.)
    """
    assert "ra" in test_pool.columns and "dec" in test_pool.columns
    non_null_ra = test_pool.filter(pl.col("ra").is_not_null()).height
    assert non_null_ra > 0, (
        "Test pool has no populated ra column — Filter #28 would "
        "silently fail as in the v1.0.0–v1.7.0 era."
    )


def test_filter28_auto_fetch_default_is_on():
    """The v8 Filter #28 fix added `auto_fetch_coords=True` as the
    default. If anyone flips this to False to "fix" some perceived
    issue, Filter #28 would silently fail on pools without ra/dec
    columns again — the exact bug we spent v1.0.0–v1.7.0 not
    noticing.

    This test pins the default to True. To intentionally disable
    auto-fetch in a calling script, pass auto_fetch_coords=False
    explicitly.
    """
    import inspect

    import pipeline_v8_filter28_fix_2026_05_17 as v8

    sig = inspect.signature(v8.filter_exoplanet_eu_coord_pm_corrected)
    auto_fetch_default = sig.parameters["auto_fetch_coords"].default
    assert auto_fetch_default is True, (
        "Filter #28 auto_fetch_coords default must be True. "
        "Setting it False reintroduces the v1.0.0–v1.7.0 silent "
        "no-op failure mode."
    )


def test_filter28_caught_hd33636_via_pm_correction(test_pool, known_source_ids):
    """HD 33636 has 9.7" raw offset from exoplanet.eu coords but 6.8"
    PM-corrected offset. The v1.8.0 fix broadened the radius to 10"
    AND added PM correction; both are necessary to catch HD 33636.
    """
    hd33636 = test_pool.filter(
        pl.col("source_id") == known_source_ids["HD_33636"]
    ).to_dicts()[0]
    assert hd33636["v8_verdict"].startswith("REJECTED_published_exoplanet_eu"), (
        f"HD 33636 should be REJECTED by Filter #28 PM-correct, got "
        f"{hd33636['v8_verdict']}"
    )


def test_filter28_caught_hd30246(test_pool, known_source_ids):
    hd30246 = test_pool.filter(
        pl.col("source_id") == known_source_ids["HD_30246"]
    ).to_dicts()[0]
    assert hd30246["v8_verdict"].startswith("REJECTED_published_exoplanet_eu"), (
        f"HD 30246 should be REJECTED by Filter #28, got {hd30246['v8_verdict']}"
    )


def test_filter28_caught_bd05_5218(test_pool, known_source_ids):
    bd = test_pool.filter(
        pl.col("source_id") == known_source_ids["BD05_5218"]
    ).to_dicts()[0]
    assert bd["v8_verdict"].startswith("REJECTED_published_exoplanet_eu"), (
        f"BD+05 5218 should be REJECTED by Filter #28, got {bd['v8_verdict']}"
    )


def test_ruwe_label_v8_to_v9_sync(test_pool, known_source_ids):
    """HD 5433 (HIP 4387) has ruwe_pass=True under the conditional
    rule (OrbitalTargetedSearch + ruwe=4.06 < lax 7.0), but the v8
    verdict label was the stale REJECTED_ruwe_quality. v9 must
    re-derive the verdict so HD 5433 ends up in its correct tier
    (HGCA chi^2 ≈ 9.2 → CORROBORATED_real_companion).
    """
    hd5433 = test_pool.filter(
        pl.col("source_id") == known_source_ids["HD_5433"]
    ).to_dicts()[0]
    assert hd5433["v8_verdict"] == "REJECTED_ruwe_quality", (
        "Test fixture: HD 5433 should carry the stale v8 label"
    )
    assert hd5433["v9b_verdict"] == "CORROBORATED_real_companion", (
        "Regression: v9 RUWE re-sync should recover HD 5433 → "
        f"CORROBORATED, got {hd5433['v9b_verdict']}"
    )


def test_sahlmann_fp_filter_rejects_hd185501(test_pool, known_source_ids):
    """HD 185501 is sahl_verdict=CONFIRMED_BINARY_FP. Without the
    v1.9.0 Fix A, the cascade leaves it as CORROBORATED. With the
    fix, it becomes REJECTED_sahlmann_fp.
    """
    hd185501 = test_pool.filter(
        pl.col("source_id") == known_source_ids["HD_185501"]
    ).to_dicts()[0]
    assert hd185501["sahl_verdict"] == "CONFIRMED_BINARY_FP", (
        "Test fixture: HD 185501 should have sahl_verdict=CONFIRMED_BINARY_FP"
    )
    assert hd185501["v8_verdict"] == "CORROBORATED_real_companion", (
        "Test fixture: HD 185501 should be the stale v8 CORROBORATED label"
    )
    assert hd185501["v9b_verdict"] == "REJECTED_sahlmann_fp", (
        f"Regression: v9 Fix A should reject HD 185501, got "
        f"{hd185501['v9b_verdict']}"
    )


def test_kervella_substitute_caught_hd92320(test_pool, known_source_ids):
    """HD 92320 has HGCA chi^2=2.25 (no signal, P=145d averages out
    over 25-yr arc) but Kervella SNR=6.07 (10-yr arc retains it).
    The v1.9.0 Fix D should promote it to CORROBORATED_kervella_only.
    """
    hd92320 = test_pool.filter(
        pl.col("source_id") == known_source_ids["HD_92320"]
    ).to_dicts()[0]
    assert hd92320["v8_verdict"] == "SURVIVOR_no_hgca_corroboration", (
        "Test fixture: HD 92320 should be v8 SURVIVOR"
    )
    assert hd92320["v9b_verdict"] == "CORROBORATED_kervella_only", (
        f"Regression: v9 Fix D should promote HD 92320 via Kervella, "
        f"got {hd92320['v9b_verdict']}"
    )


def test_simbad_visual_double_filter_rejected_hd222805(test_pool, known_source_ids):
    """HD 222805 has SIMBAD obj_type=`**` (resolved visual double,
    WDS J23444-7029AB). The v1.9.0 Fix B should demote it from
    CORROBORATED to REJECTED_simbad_visual_double.
    """
    hd222805 = test_pool.filter(
        pl.col("source_id") == known_source_ids["HD_222805"]
    ).to_dicts()[0]
    assert hd222805["v9b_verdict"] == "REJECTED_simbad_visual_double", (
        f"Regression: v9 Fix B should reject HD 222805 as visual double, "
        f"got {hd222805['v9b_verdict']}"
    )


def test_sahlmann_promotion_recovered_hd89707(test_pool, known_source_ids):
    """HD 89707 was FLAG_hgca_mass_ambiguous (HGCA chi^2=53.5) but
    Sahlmann 2025 lists it as CONFIRMED_BROWN_DWARF. v1.9.0 Fix A
    promotes FLAG → CORROBORATED when Sahlmann confirms.
    """
    hd89707 = test_pool.filter(
        pl.col("source_id") == known_source_ids["HD_89707"]
    ).to_dicts()[0]
    assert hd89707["v8_verdict"] == "FLAG_hgca_mass_ambiguous"
    assert hd89707["v9b_verdict"] == "CORROBORATED_real_companion", (
        f"Regression: v9 Fix A should promote HD 89707 → CORROBORATED, "
        f"got {hd89707['v9b_verdict']}"
    )


def test_v8_filter28_already_existing_corroborated_unaffected(test_pool, known_source_ids):
    """Negative regression: HD 76078 and BD+56 1762 (v1.8.0
    additions) and the original 4 single-orbit headlines must
    remain CORROBORATED through v9b. Any future cascade change
    that demotes them needs to be deliberate, not a side effect.
    """
    must_stay_corroborated = [
        "HD_76078", "BD56_1762", "HIP_60865", "HIP_20122",
    ]
    for k in must_stay_corroborated:
        row = test_pool.filter(
            pl.col("source_id") == known_source_ids[k]
        ).to_dicts()[0]
        assert row["v9b_verdict"].startswith("CORROBORATED"), (
            f"{k} should remain CORROBORATED in v9b, "
            f"got {row['v9b_verdict']}"
        )


def test_wd_mhost_gap_documented_as_pending():
    """v1.13.0 manually demoted a SIMBAD WD* candidate (Gaia
    6422387644229686272) by re-deriving M_2 with M_1=0.6 M_sun.
    This was a MANUAL patch, not a cascade-integrated filter. Until
    the WD-host filter is integrated (planned v1.14+), the cascade
    will still mis-classify any other WD* host the same way.

    This test documents the pending fix and will need updating when
    the filter is integrated.
    """
    # Check that no_hip_frontier_clean.csv does NOT contain the
    # demoted WD candidate (it should be in
    # wd_low_mass_companion_candidates.csv instead).
    from pathlib import Path

    frontier = Path(
        "/tmp/gaia-novelty-publication/data/supplementary/no_hip_frontier_clean.csv"
    )
    wd_demoted = Path(
        "/tmp/gaia-novelty-publication/data/supplementary/wd_low_mass_companion_candidates.csv"
    )
    assert frontier.exists() and wd_demoted.exists()

    f = pl.read_csv(frontier, schema_overrides={"source_id": pl.Int64})
    w = pl.read_csv(wd_demoted, schema_overrides={"source_id": pl.Int64})

    wd_id = 6422387644229686272
    assert wd_id not in f["source_id"].to_list(), (
        "WD candidate should NOT be in the frontier list (demoted v1.13.0)"
    )
    assert wd_id in w["source_id"].to_list(), (
        "WD candidate should be in wd_low_mass_companion_candidates.csv"
    )
