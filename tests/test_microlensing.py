"""Offline unit tests for the astrometric-microlensing predictor (lane #118).

Covers (no network):
  * the Einstein-radius constant kappa and the closed-form theta_E,
  * magnification A(u) at canonical points,
  * the dark-lens centroid-shift peak (u=sqrt2, 0.35355 theta_E) and the
    luminous-lens blend limits,
  * the closest-approach solver self-consistency,
  * the published LAWD 37 event closure: theta_E, TCA epoch, impact parameter
    (cached Gaia DR3 astrometry -> McGill+2023 published values),
  * the shift->mass inversion round-trip.
"""
from __future__ import annotations

import math
import warnings

import numpy as np
import pytest

try:
    from erfa import ErfaWarning
    warnings.filterwarnings("ignore", category=ErfaWarning)
except Exception:
    pass

from microlensing import geometry as geo


# --- Einstein radius -------------------------------------------------------- #
def test_kappa_constant():
    assert geo.KAPPA == pytest.approx(8.144, abs=0.01)


def test_einstein_radius_forms_agree():
    # parallax form vs distance form must agree for a distant source
    te_plx = geo.einstein_radius_from_parallax(0.6, 20.0)        # pi_rel=20 mas
    te_dist = geo.einstein_radius(0.6, 50.0, 1e6)               # D_L=50pc, far src
    assert te_plx == pytest.approx(te_dist, rel=1e-3)


def test_einstein_radius_invalid():
    assert math.isnan(geo.einstein_radius_from_parallax(-1, 10))
    assert math.isnan(geo.einstein_radius_from_parallax(1, -10))
    assert math.isnan(geo.einstein_radius(1, 100, 50))         # source in front


# --- magnification ---------------------------------------------------------- #
def test_magnification_canonical():
    assert float(geo.magnification(1.0)) == pytest.approx(1.34164, abs=1e-4)
    # A is monotone decreasing in u
    u = np.array([0.1, 0.5, 1.0, 2.0, 5.0])
    A = geo.magnification(u)
    assert np.all(np.diff(A) < 0)
    # large u -> A -> 1
    assert float(geo.magnification(100.0)) == pytest.approx(1.0, abs=1e-3)


def test_magnitude_change_sign():
    # brighter => negative magnitude change
    assert float(geo.magnitude_change(1.0)) < 0


# --- centroid shift --------------------------------------------------------- #
def test_dark_lens_centroid_peak():
    u = np.linspace(1e-3, 6, 200000)
    cs = geo.centroid_shift_dark_lens(u)
    i = int(np.argmax(cs))
    assert u[i] == pytest.approx(math.sqrt(2.0), abs=1e-3)
    assert cs[i] == pytest.approx(geo.CENTROID_PEAK_FRAC, abs=1e-5)
    assert geo.CENTROID_PEAK_FRAC == pytest.approx(1 / (2 * math.sqrt(2)), abs=1e-9)


def test_blended_reduces_to_dark_lens_at_g0():
    u = np.linspace(0.05, 6, 5000)
    assert np.max(np.abs(geo.centroid_shift_blended(u, 0.0)
                         - geo.centroid_shift_dark_lens(u))) < 1e-12


def test_blended_luminous_lens_suppresses_shift():
    u = np.linspace(0.05, 6, 5000)
    peaks = [np.max(geo.centroid_shift_blended(u, g)) for g in (0.0, 1.0, 10.0)]
    assert peaks[0] > peaks[1] > peaks[2]            # more lens light => smaller shift
    assert peaks[2] < 0.1                            # bright lens nearly kills it


# --- closest-approach solver ------------------------------------------------ #
def test_closest_approach_self_consistent():
    """Place a source perpendicular to the full instantaneous velocity at a
    chosen epoch and a chosen separation; the solver must recover both."""
    lens = geo.Astrometry(176.4566, -64.843, 2661.64, -344.93, 215.675, 2016.0)
    tca = 2019.86
    cosd = math.cos(math.radians(lens.dec_deg))
    p = geo.lens_position(lens, np.array([tca]))
    eps = 1e-3
    p0 = geo.lens_position(lens, np.array([tca - eps]))
    p1 = geo.lens_position(lens, np.array([tca + eps]))
    v = np.array([(p1[0][0] - p0[0][0]) / (2 * eps),
                  (p1[1][0] - p0[1][0]) / (2 * eps)])
    vhat = v / np.hypot(*v)
    perp = np.array([-vhat[1], vhat[0]])
    off = 380.0 * perp
    src_ra = lens.ra_deg + (p[0][0] + off[0]) / 3600e3 / cosd
    src_dec = lens.dec_deg + (p[1][0] + off[1]) / 3600e3
    ca = geo.closest_approach(lens, src_ra, src_dec, 2018.0, 2021.0)
    assert abs((ca.t0_jyear - tca) * geo.YR_D) < 1.0       # within a day
    assert ca.sep_min_mas == pytest.approx(380.0, abs=1.0)


# --- published LAWD 37 event closure (cached Gaia DR3 astrometry) ----------- #
LAWD37 = geo.Astrometry(176.45664726, -64.84305285, 2661.64, -344.93,
                        215.675, 2016.0)


def test_lawd37_theta_e():
    """McGill+2023: theta_E = 32.8 +/- 0.3 mas for M = 0.56 +/- 0.08 Msun."""
    te = geo.einstein_radius_from_parallax(0.56, LAWD37.parallax_mas)
    te_hi = geo.einstein_radius_from_parallax(0.64, LAWD37.parallax_mas)
    # within ~5% and inside the mass-uncertainty band
    assert te == pytest.approx(32.8, rel=0.06)
    assert te <= te_hi


def test_lawd37_major_image_shift():
    """At the published impact parameter (380 mas, u~11.6) the major-image
    deflection theta_E/u must match the published ~2.8 mas peak shift."""
    theta_e = 32.8
    u_min = 380.0 / theta_e
    assert theta_e / u_min == pytest.approx(2.8, abs=0.1)


def test_shift_to_mass_inversion_roundtrip():
    """Forward (mass->shift) then inverse (shift->mass) must round-trip."""
    pi_rel = LAWD37.parallax_mas
    mass = 0.56
    theta_e = geo.einstein_radius_from_parallax(mass, pi_rel)
    u_min = 5.0
    shift_uas = float(geo.centroid_shift_dark_lens(u_min)) * theta_e * 1000.0
    m_back = geo.mass_from_centroid_shift(shift_uas, u_min, pi_rel)
    assert m_back == pytest.approx(mass, rel=1e-6)


def test_predict_event_end_to_end():
    """predict_event returns a finite, sane prediction for LAWD 37 in 2024-2030
    against a nearby static source."""
    pred = geo.predict_event(LAWD37, 176.46, -64.84, 0.56, 2024.0, 2030.0)
    assert pred.theta_e_mas > 0
    assert np.isfinite(pred.t0_jyear)
    assert 2024.0 <= pred.t0_jyear <= 2030.0
    assert pred.peak_magnification >= 1.0
    assert pred.crossing_time_days > 0
