"""Synthetic DR4-like epoch (per-transit) astrometry generator.

DR4 is not out (expected 2 Dec 2026), so the re-fit engine is exercised on
synthetic along-scan data built from a *known* orbit + a simplified Gaia
scanning model.  The generator is deliberately conservative-realistic:

  * Baseline: 66 months / 5.5 yr (25 Jul 2014 -> 20 Jan 2020), the full nominal
    mission DR4 will publish (DR3 was 34 months).  Reference epoch J2017.5.
  * Cadence: Gaia visits a given sky point in clusters of a few transits
    separated by ~106.5 min (one spacecraft revolution; the two FoV separated
    by the 106.5-deg basic angle) during each ~1-2 day visibility window, with
    windows recurring irregularly across the mission.  We approximate this with
    Poisson-spaced visibility windows, each contributing 1-3 transits ~6 h apart,
    to land a realistic total transit count (typically 30-90 over 5.5 yr).
  * Scan angle psi: drawn from a broad distribution (Gaia's scanning law gives a
    well-spread but not uniform set of scan directions at a given point); we use
    a von Mises-perturbed two-lobe distribution so AL directions are varied
    enough to constrain the 2-D orbit.
  * Parallax factor f_par(t): the AL-projected parallax factor.  We model it as
    the projection of the standard annual parallax ellipse onto the scan
    direction, ~ sin(2π (t - t_peri)/yr) modulated by ecliptic latitude — a
    faithful-enough proxy for fitting tests (DR4 will publish parallax_factor_al).
  * sigma_AL: realistic per-transit along-scan error.  Gaia's single-CCD AL
    centroiding precision is ~0.1-0.5 mas at G<13 rising to a few mas by G~18-20.
    We map G -> sigma_AL with a simple floor+exponential, matching the published
    per-transit precision curve closely enough for model-recovery tests.

This module's ONLY job is to make believable epoch tables; it deliberately does
not encode DR4's exact (unpublished) scanning law.  When real DR4 lands, the
adapter in adapter.py maps the real columns onto EpochData and synth.py is used
only for tests.

stdlib + numpy + astropy(time) only.
"""
from __future__ import annotations

import math
from typing import Optional

import numpy as np

from model import (EpochData, abfg_from_geometry, elliptical_xy, forward_al)

# Nominal mission span DR4 will publish (TCB days, JD-2455197.5-ish offsets are
# irrelevant for fitting; we use a clean day axis with J2017.5 at the centre).
# Use a simple day axis: t=0 at J2017.5 (the Gaia reference epoch), spanning
# -1005 d .. +1005 d  (~5.5 yr nominal mission, 25 Jul 2014 -> 20 Jan 2020).
MISSION_HALF_SPAN_D = 1005.0      # ~2.75 yr each side of J2017.5
YEAR_D = 365.25


def sigma_al_from_G(G: float) -> float:
    """Per-transit along-scan uncertainty (mas) as a function of Gaia G mag.

    Rough fit to the Gaia per-CCD AL precision: ~0.10 mas floor at the bright
    end, rising steeply past G~16.  (Lindegren+2021 fig.; Holl+2023.)
    """
    # Floor + exponential rise; tuned to give ~0.15 mas @ G=13, ~0.5 mas @ G=16,
    # ~2 mas @ G=19, ~4 mas @ G=20.5.
    return 0.10 + 0.04 * math.exp(0.62 * max(0.0, G - 13.0))


def _scanning_times(rng, n_target, half_span=MISSION_HALF_SPAN_D):
    """Generate transit times mimicking Gaia visibility windows.

    Poisson-spaced windows across the mission; each window drops 1-3 transits
    ~6 h apart.  Returns a sorted array of times (days, centred on J2017.5).
    """
    times = []
    # Mean window spacing chosen so the expected transit count ~ n_target.
    mean_per_window = 1.9
    n_windows = max(8, int(round(n_target / mean_per_window)))
    # Window start times, irregular across the span.
    starts = np.sort(rng.uniform(-half_span, half_span, n_windows))
    for s in starts:
        k = rng.integers(1, 4)          # 1-3 transits this window
        for j in range(k):
            times.append(s + j * 0.25 + rng.normal(0, 0.03))   # ~6 h apart
    t = np.sort(np.array(times))
    # Trim/pad to roughly n_target.
    if t.size > n_target:
        idx = np.sort(rng.choice(t.size, n_target, replace=False))
        t = t[idx]
    return t


def _scan_angles(rng, n):
    """Draw varied scan angles (radians).  Two-lobe von Mises mix so the AL
    directions span enough of the circle to constrain a 2-D orbit (Gaia's
    scanning law yields a broad but structured psi distribution)."""
    centers = np.array([0.6, 0.6 + math.pi / 2.0])
    pick = rng.integers(0, 2, n)
    kappa = 1.2
    psi = rng.vonmises(centers[pick], kappa)
    return np.mod(psi, 2.0 * math.pi)


def _parallax_factor_al(t, psi, ecl_lat_deg=45.0):
    """AL-projected parallax factor.

    Approximate the annual parallax ellipse projected onto the scan direction.
    The full factor depends on (alpha, delta, solar longitude); for fitting
    tests we use a faithful proxy: an annual sinusoid in each of (RA*,Dec)
    modulated by ecliptic latitude, projected onto (sin psi, cos psi).
    """
    beta = math.radians(ecl_lat_deg)
    lam = 2.0 * math.pi * t / YEAR_D               # solar longitude proxy
    # Parallax displacement components (in units of parallax): standard ellipse.
    p_ra = np.sin(lam)
    p_dec = -math.sin(beta) * np.cos(lam)
    return p_ra * np.sin(psi) + p_dec * np.cos(psi)


def make_epoch_data(
    *,
    G: float,
    parallax_mas: float,
    pmra: float = 0.0,
    pmdec: float = 0.0,
    dra0: float = 0.0,
    ddec0: float = 0.0,
    # Inner orbit (the candidate's published NSS orbit).
    a_phot_mas: float,
    P_days: float,
    e: float,
    incl_deg: float,
    omega_deg: float = 40.0,
    Omega_deg: float = 110.0,
    T0_days: float = 0.0,
    # Optional outer companion (hierarchical triple) — give a_phot2/P2 to enable.
    a_phot2_mas: Optional[float] = None,
    P2_days: Optional[float] = None,
    e2: float = 0.1,
    incl2_deg: float = 60.0,
    omega2_deg: float = 200.0,
    Omega2_deg: float = 300.0,
    T02_days: float = 0.0,
    # Optional pure acceleration (alternative outer-body parameterisation).
    accel_mas_yr2: Optional[tuple] = None,
    n_transits: int = 60,
    ecl_lat_deg: float = 45.0,
    seed: int = 0,
    sigma_override: Optional[float] = None,
    sigma_inflate: float = 1.0,
) -> EpochData:
    """Build a synthetic EpochData from a known (possibly 2-body) orbit.

    Returns an EpochData whose `w` already includes Gaussian per-transit noise
    at sigma_AL(G) (optionally inflated by `sigma_inflate` to mimic the
    under-estimated-error / F2-inflation scenario of WDJ020915).
    """
    rng = np.random.default_rng(seed)
    t = _scanning_times(rng, n_transits)
    psi = _scan_angles(rng, t.size)
    par_factor = _parallax_factor_al(t, psi, ecl_lat_deg=ecl_lat_deg)
    t_ref = 0.0    # J2017.5

    A, B, Fc, Gc = abfg_from_geometry(a_phot_mas, incl_deg, omega_deg, Omega_deg)
    orbit = (A, B, Fc, Gc, P_days, e, T0_days)

    orbit2 = None
    if a_phot2_mas is not None and P2_days is not None:
        A2, B2, F2c, G2c = abfg_from_geometry(a_phot2_mas, incl2_deg, omega2_deg, Omega2_deg)
        orbit2 = (A2, B2, F2c, G2c, P2_days, e2, T02_days)

    accel = None
    if accel_mas_yr2 is not None:
        accel = (accel_mas_yr2[0], accel_mas_yr2[1])

    w_true = forward_al(t, psi, par_factor, t_ref,
                        (dra0, ddec0, parallax_mas, pmra, pmdec),
                        orbit=orbit, orbit2=orbit2, accel=accel)

    sigma_base = sigma_override if sigma_override is not None else sigma_al_from_G(G)
    sigma = np.full(t.size, sigma_base * sigma_inflate)
    # Noise drawn at the TRUE per-transit error; if sigma_inflate>1 we draw at
    # the true (smaller) error but REPORT the inflated one -> reproduces a
    # high-F2-but-unbiased-a_phot situation (WDJ020915 alternative C).
    noise_sigma = sigma_base if sigma_inflate > 1.0 else sigma
    if np.isscalar(noise_sigma):
        noise = rng.normal(0.0, noise_sigma, t.size)
    else:
        noise = rng.normal(0.0, noise_sigma)
    w = w_true + noise

    return EpochData(t=t, w=w, psi=psi, par_factor=par_factor, sigma=sigma, t_ref=t_ref)


# Convenience: the four pre-registered candidates' DR3 anchor orbits, so synth
# can generate "DR4-like data IF the headline is true" for each.  (DR3 values
# from docs/dr4_preregistration_2026_06_01.md.)
CANDIDATE_TRUTH = {
    # source_id : dict(G, parallax_mas, a_phot_mas, P_days, e, incl_deg)
    '6092654861665006592': dict(  # WG 26
        G=12.6, parallax_mas=17.7, a_phot_mas=5.40, P_days=175.94, e=0.064, incl_deg=77.1),
    '332248057157474176': dict(   # WDJ020915 (the headline)
        G=16.2, parallax_mas=11.9, a_phot_mas=7.73, P_days=274.52, e=0.024, incl_deg=65.8),
    '2909342818326298112': dict(  # WDJ060042
        G=18.4, parallax_mas=12.08, a_phot_mas=19.62, P_days=935.14, e=0.038, incl_deg=66.4),
    '5612039087715504640': dict(  # UCAC4 313
        G=13.9, parallax_mas=30.9, a_phot_mas=1.32, P_days=592.32, e=0.214, incl_deg=75.0),
}
