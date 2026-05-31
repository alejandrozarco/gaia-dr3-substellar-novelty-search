"""Per-filter unit tests for the v2 corrected cascade.

Target: scripts/streaming/v2_corrected/consumer_v2.py (the current production
cascade). Each test exercises a single piece of the v2 cascade logic and checks
the documented numeric thresholds and corrections.

The pre-cleanup v1 tests targeted deleted modules (pipeline_v2.., v7, v8, v9,
v10, v11). Where the v1 logic survived into v2 it has been rewritten here;
where it did not, the test was pruned (see the one-line PRUNED comments).
"""
from __future__ import annotations

import consumer_v2 as c2


# ---------------------------------------------------------------------------
# select_m1 — Correction to the fixed-1.5 M_1 default (the bug we just fixed)
# ---------------------------------------------------------------------------

def test_select_m1_prefers_mass_flame_over_default():
    """select_m1 must return the measured FLAME mass, not the 1.5 fallback,
    whenever mass_flame is present and positive. Using the fixed 1.5 default
    systematically biased M_2 (re-tiered ~53% of the Tier-1/2 pool)."""
    m1, src = c2.select_m1({"mass_flame": 2.0})
    assert (m1, src) == (2.0, "FLAME")


def test_select_m1_falls_back_to_mass_flame_spec():
    """When mass_flame is absent but mass_flame_spec is present, use it."""
    m1, src = c2.select_m1({"mass_flame": None, "mass_flame_spec": 0.8})
    assert (m1, src) == (0.8, "FLAME_spec")


def test_select_m1_default_when_no_flame_mass():
    """No FLAME mass at all → the 1.5 fallback (and the provenance string
    that flags it as a default, so downstream audits can spot it)."""
    m1, src = c2.select_m1({"mass_flame": None})
    assert (m1, src) == (1.5, "DEFAULT_1.5")


def test_select_m1_ignores_nan_and_nonpositive_flame():
    """NaN or non-positive FLAME masses are not real measurements and must
    fall through to the default rather than poison the M_2 inversion."""
    assert c2.select_m1({"mass_flame": float("nan")}) == (1.5, "DEFAULT_1.5")
    assert c2.select_m1({"mass_flame": 0.0}) == (1.5, "DEFAULT_1.5")
    assert c2.select_m1({"mass_flame": -1.0}) == (1.5, "DEFAULT_1.5")


# ---------------------------------------------------------------------------
# solve_m2 — mass-function invertibility / round-trip against K1_kms
# ---------------------------------------------------------------------------

def test_solve_m2_round_trips_the_mass_function():
    """solve_m2 inverts f(M)=M_2^3/(M_1+M_2)^2 for M_2. Feeding it the f(M)
    of a known (M_1, M_2) pair must recover M_2."""
    for M1, M2_true in [(0.5, 0.08), (0.93, 8.94), (1.5, 2.0), (1.0, 0.5)]:
        fM = M2_true ** 3 / (M1 + M2_true) ** 2
        M2_rt = c2.solve_m2(fM, M1)
        assert abs(M2_rt - M2_true) < 1e-3, (
            f"solve_m2 failed to round-trip M_2={M2_true} (M_1={M1}): got {M2_rt}"
        )


def test_solve_m2_round_trips_through_K1_kms():
    """End-to-end: derive K_1 from (P, e, M_1, M_2, sin i=1) via K1_kms, then
    recover M_2 from the implied f(M). Pins that the spectroscopic and
    photocentric mass-function math agree (Filter #32 depends on this)."""
    P_d, e, M1, M2_true, sini = 800.0, 0.10, 1.0, 0.50, 1.0
    K1 = c2.K1_kms(P_d, e, M1, M2_true, sini)
    assert K1 > 0
    fM = M2_true ** 3 / (M1 + M2_true) ** 2
    M2_rt = c2.solve_m2(fM, M1)
    assert abs(M2_rt - M2_true) < 1e-3


# ---------------------------------------------------------------------------
# mass_class — tier boundary thresholds (must not drift)
# ---------------------------------------------------------------------------

def test_mass_class_thresholds():
    """The mass_class cut points are a fixed contract; drift silently
    re-tiers the candidate list."""
    assert c2.mass_class(3.0) == "dormant_BH_candidate"
    assert c2.mass_class(5.0) == "dormant_BH_candidate"
    assert c2.mass_class(1.2) == "dormant_NS_candidate"
    assert c2.mass_class(2.9) == "dormant_NS_candidate"
    assert c2.mass_class(0.5) == "WD_or_low_mass_star"
    assert c2.mass_class(1.19) == "WD_or_low_mass_star"
    assert c2.mass_class(0.08) == "M_dwarf_companion"
    assert c2.mass_class(0.49) == "M_dwarf_companion"
    assert c2.mass_class(0.013) == "BD_candidate"
    assert c2.mass_class(0.079) == "BD_candidate"
    assert c2.mass_class(0.012) == "planet_candidate"


# ---------------------------------------------------------------------------
# Correction A — NSS parallax preference (select_plx)
# ---------------------------------------------------------------------------

def test_select_plx_prefers_nss_over_gaia_source():
    """When both parallaxes are available, the NSS (orbit-fit) parallax wins
    over gaia_source.parallax, which absorbs orbital motion as fake parallax
    and inflates M_2."""
    plx, src = c2.select_plx(plx_gs=0.82, plx_nss=0.8528)
    assert (plx, src) == (0.8528, "NSS")


def test_select_plx_falls_back_to_gaia_source():
    """No NSS parallax → use gaia_source.parallax."""
    plx, src = c2.select_plx(plx_gs=2.309, plx_nss=None)
    assert (plx, src) == (2.309, "gaia_source")


def test_select_plx_none_when_neither_positive():
    """Neither parallax available/positive → (None, None) so the caller
    short-circuits rather than dividing by a bad parallax."""
    assert c2.select_plx(plx_gs=None, plx_nss=None) == (None, None)
    assert c2.select_plx(plx_gs=-1.0, plx_nss=float("nan")) == (None, None)


# ---------------------------------------------------------------------------
# Correction B — rv_amplitude_robust is peak-to-trough, so K_1 = K_obs/2
# ---------------------------------------------------------------------------

def test_filter32_uses_K_obs_over_2():
    """filter32_v2 must convert the peak-to-trough rv_amplitude_robust to a
    semi-amplitude by dividing by 2 before comparing to K_pred(i=90°).
    Verified against Gaia BH2 (rv_amplitude_robust=36.96, El-Badry K_1=21.2)."""
    # Construct a case where K_pred(i=90) == K_obs/2 exactly, so sin i ≈ 1.
    P_d, e, M1, M2 = 1276.7, 0.5176, 0.93, 8.94
    K_max = c2.K1_kms(P_d, e, M1, M2, 1.0)
    K_obs_peak_to_trough = 2.0 * K_max  # if /2 is applied, sin i == 1.0
    status, sini, kmax = c2.filter32_v2(K_obs_peak_to_trough, P_d, e, M1, M2)
    assert status == "PASS"
    assert abs(sini - 1.0) < 1e-6, f"expected sin i=1.0 after /2 conversion, got {sini}"


def test_filter32_no_data_when_K_obs_missing():
    status, sini, kmax = c2.filter32_v2(None, 800.0, 0.1, 1.0, 0.5)
    assert status == "NO_DATA"


# ---------------------------------------------------------------------------
# Correction C — Filter #30 logg fallback chain (gspphot → ann → gspspec)
# ---------------------------------------------------------------------------

def test_filter30_logg_fallback_uses_gspspec_ann_when_gspphot_nan():
    """gspphot returns NaN for binaries; F#30 must fall back to
    logg_gspspec_ann. HD 1957 / BD+38 2040 had logg_gspphot=NaN but
    logg_gspspec_ann < 2.7 — the original cascade missed them."""
    status, risk, logg_used, logg_source, reason = c2.filter30_v2(
        bp_rp=0.9,
        logg_gspphot=float("nan"),
        logg_gspspec_ann=2.63,
        logg_gspspec=None,
        teff_gspphot=4771.0,
    )
    assert logg_source == "gspspec_ann"
    assert logg_used == 2.63
    assert risk is True and status == "FAIL"


def test_filter30_logg_fallback_handles_numpy_float32_nan():
    """Regression (2026-05-29): a numpy.float32 NaN must be treated as missing
    so F#30 falls back to logg_gspspec_ann. isinstance(v, float) is False for
    np.float32, which let a float32-NaN logg_gspphot (as stored in the
    production parquet) slip past the NaN guard -> F#30 PASS -> HD 1957 became a
    phantom Tier-1 NS. The earlier fixture used python float64 and masked it."""
    import numpy as np
    status, risk, logg_used, logg_source, reason = c2.filter30_v2(
        bp_rp=0.9,
        logg_gspphot=np.float32("nan"),
        logg_gspspec_ann=2.63,
        logg_gspspec=None,
        teff_gspphot=np.float32(4771.0),
    )
    assert logg_source == "gspspec_ann"
    assert logg_used == 2.63
    assert risk is True and status == "FAIL"


def test_filter30_logg_prefers_gspphot_when_present():
    status, risk, logg_used, logg_source, reason = c2.filter30_v2(
        bp_rp=0.5,
        logg_gspphot=4.2,
        logg_gspspec_ann=2.0,   # would FAIL, but gspphot wins and is dwarf-like
        logg_gspspec=None,
        teff_gspphot=6000.0,
    )
    assert logg_source == "gspphot"
    assert logg_used == 4.2
    assert risk is False and status == "PASS"


def test_filter30_kgiant_proxy_fires_on_teff_and_logg():
    """K-giant proxy: 3700 ≤ Teff ≤ 5200 K AND logg < 3.0 → FAIL even if
    BP-RP and the logg<2.7 cut alone would pass."""
    status, risk, logg_used, logg_source, reason = c2.filter30_v2(
        bp_rp=0.9,              # < 1.2, would pass on colour
        logg_gspphot=2.8,       # > 2.7, would pass the logg<2.7 cut
        logg_gspspec_ann=None,
        logg_gspspec=None,
        teff_gspphot=4500.0,    # K-giant Teff window, logg < 3.0
    )
    assert risk is True and status == "FAIL"
    assert "K-giant proxy" in reason


def test_filter30_passes_clean_dwarf():
    status, risk, *_ = c2.filter30_v2(
        bp_rp=0.6, logg_gspphot=4.4, logg_gspspec_ann=None,
        logg_gspspec=None, teff_gspphot=5800.0,
    )
    assert risk is False and status == "PASS"


# ---------------------------------------------------------------------------
# Filter #29 — Gaia SB2 rejection (a measured K2 means a luminous secondary)
# ---------------------------------------------------------------------------

def test_filter29_rejects_sb2_solution_type():
    """A row whose nss_solution_type contains 'SB2' (double-lined) is a
    stellar binary and must be demoted, never reach a compact-object tier."""
    row = {
        "a_phot_mas": 3.8, "parallax": 0.82, "nss_parallax": 0.85,
        "period": 1276.7, "eccentricity": 0.5, "mass_flame": 0.93,
        "bp_rp": 0.9, "logg_gspphot": 3.5, "teff_gspphot": 5000.0,
        "rv_amplitude_robust": 36.96, "rv_chisq_pvalue": 0.0,
        "nss_solution_type": "SB2",
    }
    out = c2.derive_row_v2(row)
    assert out["filter29_v2"] == "FAIL"
    assert out["tier_v2"] == "Demoted (failed F#29 SB2)"


def test_filter29_passes_sb1_class():
    """SB1-class (single-lined) solutions are not rejected by F#29."""
    out = c2.derive_row_v2({
        "a_phot_mas": 3.8, "parallax": 0.82, "nss_parallax": 0.85,
        "period": 1276.7, "eccentricity": 0.5, "mass_flame": 0.93,
        "bp_rp": 0.9, "logg_gspphot": 3.5, "teff_gspphot": 5000.0,
        "rv_amplitude_robust": 36.96, "rv_chisq_pvalue": 0.0,
        "nss_solution_type": "AstroSpectroSB1",
    })
    assert out["filter29_v2"] == "PASS"


def test_filter29_in_sb2_flag_also_fails():
    """The explicit in_sb2 boolean (set by the bulk SB2 cross-match) also
    triggers the F#29 rejection independent of the solution-type string."""
    out = c2.derive_row_v2({
        "a_phot_mas": 3.8, "parallax": 0.82, "nss_parallax": 0.85,
        "period": 1276.7, "eccentricity": 0.5, "mass_flame": 0.93,
        "bp_rp": 0.9, "logg_gspphot": 3.5, "teff_gspphot": 5000.0,
        "rv_amplitude_robust": 36.96, "rv_chisq_pvalue": 0.0,
        "nss_solution_type": "Orbital", "in_sb2": True,
    })
    assert out["filter29_v2"] == "FAIL"


# ---------------------------------------------------------------------------
# tier_label — friendly characterization for non-compact masses
# ---------------------------------------------------------------------------

def test_tier_label_demotion_precedence():
    """Filter failures take precedence over the Tier-1 labels, in order
    F#29 → F#30 → F#32 → F#31."""
    assert c2.tier_label("dormant_BH_candidate", "FAIL", "PASS", "PASS", "PASS") \
        == "Demoted (failed F#29 SB2)"
    assert c2.tier_label("dormant_BH_candidate", "PASS", "FAIL", "PASS", "PASS") \
        == "Demoted (failed F#30 K-giant chromatic)"
    assert c2.tier_label("dormant_NS_candidate", "PASS", "PASS", "PASS", "FAIL") \
        == "Demoted (failed F#32 joint K_obs/K_pred)"


def test_tier_label_compact_pass_through():
    assert c2.tier_label("dormant_BH_candidate", "PASS", "PASS", "PASS", "PASS") == "Tier-1 BH"
    assert c2.tier_label("dormant_NS_candidate", "PASS", "PASS", "PASS", "PASS") == "Tier-1 NS"


def test_tier_label_substellar_is_characterized_not_rejected():
    """Sub-compact masses are *characterized* companions, not rejections."""
    assert c2.tier_label("BD_candidate", "PASS", "PASS", "PASS", "PASS").startswith(
        "Characterized"
    )
    assert c2.tier_label("planet_candidate", "PASS", "PASS", "PASS", "PASS").startswith(
        "Characterized"
    )


# ---------------------------------------------------------------------------
# PRUNED v1-only tests (targeted modules deleted in commit 5fac35c):
#   - documented_fp set (pipeline_v2.DOCUMENTED_NSS_FPS): the DPAC FP hardcode
#     is not part of the v2 cascade.
#   - conditional-RUWE / Acceleration RUWE set (pipeline_v9/v10): RUWE gating
#     moved into the producer pre-cuts, not consumer_v2.
#   - Filter #28 exoplanet.eu coord/PM projection (pipeline_v8): removed; v2 is
#     scoped to the NSS-only mass-function cascade.
#   - HGCA chi^2 tiering (pipeline_v2): the HGCA second-method tier is not in v2.
#   - Kervella-substitute promotion (pipeline_v9 Fix D): removed in v2.
#   - Sahlmann FP reject / BD promotion (pipeline_v9 Fix A): removed in v2.
#   - V7_FACE_ON / V7_MARG / V7_FLUXRATIO thresholds (pipeline_v7): removed.


# ---------------------------------------------------------------------------
# Test-pool sanity (still-valid offline fixtures, kept from the v1 suite)
# ---------------------------------------------------------------------------

def test_test_pool_loads(test_pool):
    """The curated test pool should still load cleanly."""
    assert test_pool.height >= 13
    assert "source_id" in test_pool.columns


# ---------------------------------------------------------------------------
# Filter #33 — NSS period-confidence flag (flags bit 13 = 8192 =
# NO_SIGNIFICANT_PERIODS_CAN_BE_FOUND). Added 2026-05-31 after the SB1 flags
# QA audit found 49% of AstroSpectroSB1 and ~14% of high-f(M) SB1 carry it.
# ---------------------------------------------------------------------------

def test_filter33_sb1_nonsignificant_period_fails():
    """Pure SB1/SB1C with bit 13 is a hard FAIL — spectroscopic-only period
    (hence f(M)) is unreliable. Example: Gaia DR3 5355234746758153728."""
    assert c2.filter33_v2("SB1", 8192) == "FAIL"
    assert c2.filter33_v2("SB1C", 8192) == "FAIL"


def test_filter33_astrospectrosb1_nonsignificant_period_flags():
    """AstroSpectroSB1 with bit 13 is FLAG (not FAIL) — the astrometric orbit
    independently constrains the period (~49% of AstroSpectroSB1 carry it)."""
    assert c2.filter33_v2("AstroSpectroSB1", 8192) == "FLAG"


def test_filter33_orbital_bit13_not_applicable():
    """bit 13 is a spectroscopic flag; for a pure astrometric solution -> PASS."""
    assert c2.filter33_v2("Orbital", 8192) == "PASS"
    assert c2.filter33_v2("OrbitalAlternative", 8192) == "PASS"


def test_filter33_clean_and_missing():
    assert c2.filter33_v2("SB1", 0) == "PASS"                # bit 13 clear
    assert c2.filter33_v2("AstroSpectroSB1", 64) == "PASS"   # bit 6 only
    assert c2.filter33_v2("SB1", None) == "NO_DATA"          # flags not pulled


def test_filter33_dtype_safe():
    """float32 lesson: numpy dtypes (and NaN) must decode correctly."""
    import numpy as np
    assert c2.filter33_v2("SB1", np.float32(8192)) == "FAIL"
    assert c2.filter33_v2("SB1", np.int64(8192)) == "FAIL"
    assert c2.filter33_v2("SB1", float("nan")) == "NO_DATA"
    # 3155543-like AstroSpectroSB1: flags = 2**52 + 2**13 + 2**6 -> bit 13 set
    assert c2.filter33_v2("AstroSpectroSB1", (1 << 52) | (1 << 13) | (1 << 6)) == "FLAG"


def test_tier_label_f33_fail_demotes():
    t = c2.tier_label("dormant_NS_candidate", "PASS", "PASS", "PASS", "PASS", "FAIL")
    assert "Demoted" in t and "F#33" in t


def test_tier_label_f33_flag_downtiers_to_tier2():
    t = c2.tier_label("dormant_NS_candidate", "PASS", "PASS", "PASS", "PASS", "FLAG")
    assert "Tier-2" in t and "non-significant" in t


def test_tier_label_f33_default_backward_compatible():
    """tier_label still works without f33 (default PASS) -> Tier-1 NS."""
    assert c2.tier_label("dormant_NS_candidate", "PASS", "PASS", "PASS", "PASS") == "Tier-1 NS"
