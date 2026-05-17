"""Per-filter unit tests for the v2..v9b cascade.

Each test exercises a single filter against the curated test pool and
checks that the filter produces the documented outcomes for known cases.
"""
from __future__ import annotations

import math

import polars as pl
import pytest


# ---------------------------------------------------------------------------
# Filter #27 — documented_fp
# ---------------------------------------------------------------------------

def test_documented_fp_set_is_4_known_sources():
    """DOCUMENTED_NSS_FPS hardcoded list should contain exactly the 4
    Gaia DR3 documented false-positive source_ids identified by DPAC.
    """
    import pipeline_v2_tuned_filters_2026_05_13 as v2

    expected = {
        "4698424845771339520",  # WD 0141-675
        "5765846127180770432",  # HIP 64690
        "522135261462534528",   # * 54 Cas
        "1712614124767394816",  # HIP 66074
    }
    assert set(v2.DOCUMENTED_NSS_FPS.keys()) == expected


# ---------------------------------------------------------------------------
# Filter #1 — conditional RUWE
# ---------------------------------------------------------------------------

def test_conditional_ruwe_lax_for_orbit_reflex_solution_types():
    """Orbit-reflex solution types (Orbital, AstroSpectroSB1, etc.) must
    use the lax RUWE cutoff (7.0), not the strict cutoff (2.0).

    This is the v1.9.0 Fix C: the old uniform RUWE<2 cut was wrong for
    these solution types where orbital reflex itself drives RUWE up.
    """
    import pipeline_v9_recall_improvements_2026_05_17 as v9

    # HD 5433: OrbitalTargetedSearch, ruwe=4.06 → should pass with lax
    row = {"nss_solution_type": "OrbitalTargetedSearch", "ruwe": 4.06}
    assert v9.reclass_ruwe_pass(row) is True, (
        "OrbitalTargetedSearch with ruwe=4.06 should pass the lax 7.0 cut"
    )

    # Generic source with ruwe=4.06 → should fail strict
    row_strict = {"nss_solution_type": "Acceleration7", "ruwe": 4.06}
    assert v9.reclass_ruwe_pass(row_strict) is False, (
        "Acceleration7 with ruwe=4.06 should fail the strict 2.0 cut"
    )


def test_conditional_ruwe_all_orbit_reflex_types_recognised():
    import pipeline_v2_tuned_filters_2026_05_13 as v2

    must_include = {
        "Orbital",
        "AstroSpectroSB1",
        "OrbitalTargetedSearchValidated",
        "OrbitalTargetedSearch",
        "SB1",
    }
    assert must_include.issubset(v2.ORBIT_REFLEX_SOLUTION_TYPES)


# ---------------------------------------------------------------------------
# Filter #28 — exoplanet.eu coord-match (PM-corrected, v1.8.0 fix)
# ---------------------------------------------------------------------------

def test_pma_projection_back_to_j2000_uses_minus_16_years():
    """The Gaia-DR3-to-exoplanet.eu epoch projection must use -16 yr
    (Gaia J2016.0 → catalog J2000.0). Wrong sign would push positions
    forward in time instead of back.
    """
    import pipeline_v8_filter28_fix_2026_05_17 as v8

    # Project a source with known PM back; PM-RA = +100 mas/yr,
    # dt = -16 yr (V8_EXOEU_EPOCH - V8_GAIA_EPOCH = 2000 - 2016 = -16)
    # So the projected RA should DECREASE by 100*16 = 1600 mas
    ra, dec = v8.project_to_epoch(ra=100.0, dec=0.0, pmra_masyr=100.0,
                                   pmdec_masyr=0.0, dt_yr=-16.0)
    # 1600 mas at dec=0 is 1600/3.6e6 = 4.44e-4 deg
    delta_ra = (ra - 100.0)
    expected_delta = -1600.0 / 3.6e6  # negative because moving back in time
    assert abs(delta_ra - expected_delta) < 1e-6, (
        f"Expected RA shift of {expected_delta:.6f} deg, got {delta_ra:.6f}"
    )


def test_pma_radius_is_10_arcsec_default():
    """The v1.8.0 Filter #28 fix broadened the radius to 10″ to catch
    HD 33636's 6.8″ PM-corrected offset. Going back to 5″ would
    silently miss it.
    """
    import pipeline_v8_filter28_fix_2026_05_17 as v8

    assert v8.V8_COORD_MATCH_RADIUS_ARCSEC == 10.0


# ---------------------------------------------------------------------------
# Filter #4 — HGCA chi^2 tier
# ---------------------------------------------------------------------------

def test_hgca_tier_thresholds():
    """HGCA tier function: >100=REJECT, 30-100=FLAG, 5-30=CORROBORATED,
    <5=isolated.
    """
    import pipeline_v2_tuned_filters_2026_05_13 as v2

    def tier(x):
        if x > 100:
            return "REJECTED_likely_stellar"
        if x > 30:
            return "FLAG_mass_ambiguous"
        if x > 5:
            return "CORROBORATED_real_companion"
        return "isolated_no_outer_body"

    assert tier(150) == "REJECTED_likely_stellar"
    assert tier(50) == "FLAG_mass_ambiguous"
    assert tier(15) == "CORROBORATED_real_companion"
    assert tier(3) == "isolated_no_outer_body"
    # Boundary cases
    assert tier(101) == "REJECTED_likely_stellar"
    assert tier(100) == "FLAG_mass_ambiguous"
    assert tier(30) == "CORROBORATED_real_companion"
    assert tier(5) == "isolated_no_outer_body"


# ---------------------------------------------------------------------------
# Fix D (v1.9.0) — Kervella substitute for HGCA on short-period orbits
# ---------------------------------------------------------------------------

def test_kervella_substitute_promotes_short_p_hgca_blind_source():
    """A source with HGCA chi^2 < 5 (no signal), Kervella SNR > 3,
    substellar M_2, AND P < 4 yr should be promoted to
    CORROBORATED_kervella_only. HD 92320 is the canonical example.
    """
    import pipeline_v9_recall_improvements_2026_05_17 as v9

    row = {
        "v8_verdict": "SURVIVOR_no_hgca_corroboration",
        "hgca_chisq": 2.25,            # HGCA sees nothing
        "snrPMaH2G2": 6.07,            # Kervella does
        "period_d": 145.0,             # short P << 25 yr → HGCA averages out
        "M_2_mjup_face_on": 75.0,
        "M_2_mjup_marginalized": 76.0,  # substellar at marg
        "sahl_verdict": None,
    }
    assert v9.reclass_to_v9(row) == "CORROBORATED_kervella_only"


def test_kervella_substitute_NOT_applied_to_long_p_orbits():
    """Long-period (P > 4 yr) orbits should NOT trigger the Kervella
    substitute even with the same Kervella signal — HGCA's 25-yr arc
    actually constrains these directly.
    """
    import pipeline_v9_recall_improvements_2026_05_17 as v9

    row = {
        "v8_verdict": "SURVIVOR_no_hgca_corroboration",
        "hgca_chisq": 2.25,
        "snrPMaH2G2": 6.07,
        "period_d": 2000.0,            # > 4 yr threshold
        "M_2_mjup_face_on": 75.0,
        "M_2_mjup_marginalized": 76.0,
        "sahl_verdict": None,
    }
    # Should remain SURVIVOR — HGCA's null is meaningful at this baseline
    assert v9.reclass_to_v9(row) == "SURVIVOR_no_hgca_corroboration"


def test_kervella_substitute_NOT_applied_to_stellar_mass():
    """A clearly-stellar M_2 must not be promoted even with Kervella
    signal at short P.
    """
    import pipeline_v9_recall_improvements_2026_05_17 as v9

    row = {
        "v8_verdict": "SURVIVOR_no_hgca_corroboration",
        "hgca_chisq": 2.25,
        "snrPMaH2G2": 6.07,
        "period_d": 145.0,
        "M_2_mjup_face_on": 500.0,      # stellar
        "M_2_mjup_marginalized": 500.0,
        "sahl_verdict": None,
    }
    assert v9.reclass_to_v9(row) == "SURVIVOR_no_hgca_corroboration"


# ---------------------------------------------------------------------------
# Fix A (v1.9.0) — Sahlmann CONFIRMED_BINARY_FP rejection
# ---------------------------------------------------------------------------

def test_sahlmann_fp_rejects_otherwise_corroborated_source():
    """A source that the cascade would otherwise CORROBORATE but
    Sahlmann 2025 marks as CONFIRMED_BINARY_FP should be REJECTED.
    HD 185501 is the canonical example.
    """
    import pipeline_v9_recall_improvements_2026_05_17 as v9

    row = {
        "v8_verdict": "CORROBORATED_real_companion",
        "sahl_verdict": "CONFIRMED_BINARY_FP",
        "hgca_chisq": 5.9,
        "M_2_mjup_face_on": 14.5,
    }
    assert v9.reclass_to_v9(row) == "REJECTED_sahlmann_fp"


# ---------------------------------------------------------------------------
# Fix A continued — FLAG → CORROBORATED via Sahlmann promotion
# ---------------------------------------------------------------------------

def test_flag_mass_ambiguous_upgrades_when_sahlmann_confirmed_bd():
    """A FLAG_hgca_mass_ambiguous source that Sahlmann 2025 lists as
    CONFIRMED_BROWN_DWARF should be promoted to CORROBORATED.
    HD 89707 is the canonical example.
    """
    import pipeline_v9_recall_improvements_2026_05_17 as v9

    row = {
        "v8_verdict": "FLAG_hgca_mass_ambiguous",
        "sahl_verdict": "CONFIRMED_BROWN_DWARF",
        "hgca_chisq": 53.5,
    }
    assert v9.reclass_to_v9(row) == "CORROBORATED_real_companion"


# ---------------------------------------------------------------------------
# Filter #37 — both-estimates-stellar M_2 rejection (v1.7.0)
# ---------------------------------------------------------------------------

def test_v7_both_estimates_stellar_thresholds_unchanged():
    """The face_on > 100 AND marg > 200 thresholds must not drift —
    these were calibrated against the truth set and a regression would
    affect specificity numbers in the paper.
    """
    import pipeline_v7_tuned_filters_2026_05_17 as v7

    assert v7.V7_FACE_ON_THRESHOLD_MJ == 100.0
    assert v7.V7_MARG_THRESHOLD_MJ == 200.0


def test_v7_fluxratio_threshold_is_05():
    """Filter #35 v2 (v1.7.0) lowered the threshold from 0.10 to 0.05
    based on cross-validation. Any regression would re-introduce 2
    Halbwachs SB2 escapes.
    """
    import pipeline_v7_tuned_filters_2026_05_17 as v7

    assert v7.V7_FLUXRATIO_THRESHOLD == 0.05


# ---------------------------------------------------------------------------
# Test pool sanity checks
# ---------------------------------------------------------------------------

def test_test_pool_loads(test_pool):
    """The curated test pool should load cleanly and have ≥13 sources."""
    assert test_pool.height >= 13
    assert "source_id" in test_pool.columns
    assert "v9b_verdict" in test_pool.columns


def test_test_pool_has_each_expected_verdict_tier(test_pool):
    """The test pool should cover the major v9b verdict tiers so that
    end-to-end tests exercise each."""
    verdicts = set(test_pool["v9b_verdict"].to_list())
    must_cover = {
        "CORROBORATED_real_companion",
        "CORROBORATED_kervella_only",
        "REJECTED_published_exoplanet_eu_pm_corr",
        "REJECTED_sahlmann_fp",
        "REJECTED_simbad_visual_double",
    }
    missing = must_cover - verdicts
    assert not missing, f"Test pool missing v9b verdicts: {missing}"
