"""Regression tests for the v3 acceleration-channel RV-consistency cross-check
(added 2026-05-31).

The astrometry-only acceleration inversion assumes the full PM acceleration is
sky-projected (face-on) and marginalizes flat in log-P, which over-states the
headline M2 median.  For sources with a significant RV variation, the joint
RV+astrometric solution pins inclination AND mass at each period and collapses
the over-stated candidates to their true (often WD/low-mass) masses.

Anchor case: Gaia DR3 4698497413538721408 (HD 10711) — astrometry-only
M2_median = 4.758 Msun, but joint short-P solution = ~0.6 Msun (white dwarf).
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..",
                                "scripts", "streaming", "v3_acceleration"))
import acceleration_inversion as ai  # noqa: E402

# HD 10711 measured values (Gaia DR3 4698465... acceleration + gaia_source RV)
HD = dict(accel=16.137, plx=7.123961, K1=7.929, M1=1.5)


def test_bisect_root_basic():
    assert abs(ai._bisect_root(lambda x: x * x - 4.0, 0.0, 10.0) - 2.0) < 1e-6
    assert ai._bisect_root(lambda x: x + 1.0, 0.0, 10.0) is None  # no sign change


def test_joint_m2_hd10711_short_period_is_white_dwarf():
    """At the short period favored by the jerk solution, the joint RV+astrometric
    mass is ~0.6 Msun (a white dwarf) — NOT the 4.76 Msun astrometry-only median."""
    r = ai.joint_m2_from_accel_rv(HD["accel"], HD["plx"], HD["K1"], HD["M1"], 3.0)
    assert r is not None
    m2, i_deg = r
    assert 0.4 < m2 < 1.1, m2
    assert 0.0 < i_deg <= 90.0


def test_joint_m2_monotone_in_period():
    """Longer assumed period -> more mass for the same accel+K1."""
    short = ai.joint_m2_from_accel_rv(HD["accel"], HD["plx"], HD["K1"], HD["M1"], 3.0)[0]
    longp = ai.joint_m2_from_accel_rv(HD["accel"], HD["plx"], HD["K1"], HD["M1"], 30.0)[0]
    assert longp > short


def test_jerk_aware_grid_caps_acceleration9():
    _, pmax9 = ai.jerk_aware_period_grid("Acceleration9")
    _, pmax7 = ai.jerk_aware_period_grid("Acceleration7")
    assert pmax9 == 12.0
    assert pmax7 == 100.0


def test_derive_row_v3_flags_and_demotes_overstated_wd():
    """HD 10711-like Acceleration9 row: astrometry-only median is NS/BH-mass but
    the RV-folded joint short-P mass is WD/low-mass -> flagged + demoted."""
    row = dict(
        accel_ra=14.723, accel_dec=-6.605, accel_ra_error=0.1, accel_dec_error=0.1,
        parallax=7.124, bp_rp=0.6, logg_gspphot=4.3, logg_gspspec_ann=None,
        logg_gspspec=None, teff_gspphot=6100.0, teff_gspspec_ann=None,
        rv_amplitude_robust=15.86, rv_chisq_pvalue=0.0,
        nss_solution_type="Acceleration9",
    )
    out = ai.derive_row_v3(row, M1_prior=1.5)
    assert out["has_rv_var_v3"] is True
    assert out["M2_median_v3"] >= 1.2            # astrometry-only over-states
    assert out["M2_joint_shortP_v3"] < 1.2       # joint short-P is WD/low-mass
    assert out["rv_consistency_flag_v3"] == "OVERSTATED_TO_WD_LOWMASS"
    assert out["tier_v3"].startswith("Demoted (RV-joint")
    assert out["jerk_P_yr_max_grid_v3"] == 12.0  # short grid for the jerk solution


def test_derive_row_v3_no_rv_is_unflagged():
    """No significant RV -> no joint columns, flag NO_RV_VAR, tier unchanged."""
    row = dict(
        accel_ra=14.723, accel_dec=-6.605, accel_ra_error=0.1, accel_dec_error=0.1,
        parallax=7.124, bp_rp=0.6, logg_gspphot=4.3, teff_gspphot=6100.0,
        rv_amplitude_robust=None, rv_chisq_pvalue=None,
        nss_solution_type="Acceleration7",
    )
    out = ai.derive_row_v3(row, M1_prior=1.5)
    assert out["rv_consistency_flag_v3"] == "NO_RV_VAR"
    assert out["M2_joint_shortP_v3"] is None


def test_derive_row_v3_genuine_bh_not_flagged():
    """A genuinely massive accelerator (high accel + large K1) stays CONSISTENT_BH
    and is NOT demoted by the cross-check."""
    # synthetic edge-on-ish high-mass case: large K1 forces a high joint mass
    row = dict(
        accel_ra=40.0, accel_dec=0.0, accel_ra_error=0.1, accel_dec_error=0.1,
        parallax=2.0, bp_rp=0.6, logg_gspphot=4.2, teff_gspphot=6000.0,
        rv_amplitude_robust=120.0, rv_chisq_pvalue=0.0,
        nss_solution_type="Acceleration7",
    )
    out = ai.derive_row_v3(row, M1_prior=1.5)
    assert out["rv_consistency_flag_v3"] != "OVERSTATED_TO_WD_LOWMASS"
    assert not out["tier_v3"].startswith("Demoted (RV-joint")
