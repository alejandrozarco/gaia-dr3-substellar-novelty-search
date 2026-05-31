"""Acceleration-NSS mass-function inversion (v3 extension of the cascade).

For sources in `gaiadr3.nss_acceleration_astro`, no Thiele-Innes orbit fit
exists (P > Gaia mission baseline), only a 7- or 9-parameter PM-acceleration
model. We cannot recover M_2 directly because the period P is unconstrained.

The inversion strategy (Brandt 2018 ApJS 239 31; Kervella+ 2019 A&A 623 A72;
El-Badry+ 2024 for BH3):

    The proper-motion acceleration amplitude |a| (mas/yr^2) for a primary
    with companion of mass M_2 on a circular orbit of period P (yr) is:

        |a|_mas/yr^2 = 4 pi^2 * (M_2 / (M_1 + M_2)^(2/3)) * P_yr^(-4/3) * plx_mas

    where P_yr is the orbital period in years, M_1 + M_2 the total mass in
    M_sun, and plx_mas the parallax in mas.

    Solving for M_2 (given measured |a|, plx, M_1, assumed P) requires
    numerical inversion of

        M_2 / (M_1 + M_2)^(2/3) = |a| / (4 pi^2 * plx * P^(-4/3))

    which we do by bisection.  For an unknown P, we grid in log-P over the
    physically motivated range:

        P_min = 3 yr   (below this Gaia would have fit an orbit, not
                        an acceleration -- ~equals mission baseline)
        P_max = 100 yr (long-period dormant binary cap)

    and report (M_2_min, M_2_median, M_2_max) across the grid.

Mass-function intuition for circular orbits is preserved: longer assumed P
yields larger inferred M_2 (since |a| ~ 1/P^(4/3) means more mass is needed
to produce the same acceleration for longer periods).

Exponent correction (2026-05-31): the inversion uses M_2/(M_1+M_2)^(2/3) -- the
exact two-body exponent, since a_1 = a_rel * M_2/M_tot and a_rel = (M_tot P^2)^(1/3)
give |a| ~ M_2 / M_tot^(2/3) * P^(-4/3).  The original code/docstring used
^(1/3), which under-stated the face-on M_2 increasingly with P (e.g. P=17 yr:
4.6 vs the correct 18.4 M_sun for HD 10711's acceleration).

The output mass range encodes the P-uncertainty.  Combined with the F#29-32
filters (re-imported from v2_corrected/consumer_v2.py), a source is tagged
Tier-1 BH if even the *pessimistic* (P_min) M_2 estimate already exceeds 3
M_sun -- such sources cannot be ordinary stellar binaries at any P in the
[P_min, P_max] range.

Note: We deliberately keep the math in this file pure-Python (math + numpy)
so it can be smoke-tested on BH3 published values without an ADQL query.
"""
from __future__ import annotations
import math
from typing import Optional, Tuple, Iterable

import numpy as np


FOUR_PI_SQ = 4.0 * math.pi * math.pi


# ---------------------------------------------------------------------------
# Core PM-acceleration mass-function inversion
# ---------------------------------------------------------------------------

def M2_from_acceleration(accel_mas_yr2: float,
                         plx_mas: float,
                         M1: float,
                         P_yr: float) -> Optional[float]:
    """Return the companion mass M_2 (M_sun) implied by a measured PM
    acceleration `|a|` (mas/yr^2), parallax `plx` (mas), primary mass
    `M_1` (M_sun) and an assumed orbital period `P` (yr).

    Solves by bisection:
        f(M_2) = M_2 / (M_1 + M_2)^(2/3) - K = 0,
        K     = |a| / (4 pi^2 * plx * P^(-4/3))
              = |a| * P^(4/3) / (4 pi^2 * plx)

    The LHS is monotone increasing in M_2 (>0), so bisection is guaranteed
    to converge.  Returns None if inputs are invalid.

    The formula assumes circular orbits (e=0).  For eccentric orbits the
    instantaneous acceleration varies along the orbit, but for the orbit-
    averaged PM-acceleration solution this circular form is the canonical
    first-order estimate (Brandt 2018).
    """
    if (accel_mas_yr2 is None or plx_mas is None
            or M1 is None or P_yr is None):
        return None
    try:
        accel_mas_yr2 = float(accel_mas_yr2)
        plx_mas = float(plx_mas)
        M1 = float(M1)
        P_yr = float(P_yr)
    except (TypeError, ValueError):
        return None
    if (math.isnan(accel_mas_yr2) or math.isnan(plx_mas)
            or math.isnan(M1) or math.isnan(P_yr)):
        return None
    if accel_mas_yr2 <= 0 or plx_mas <= 0 or M1 <= 0 or P_yr <= 0:
        return None

    K = (accel_mas_yr2 * P_yr ** (4.0 / 3.0)) / (FOUR_PI_SQ * plx_mas)
    if K <= 0:
        return None

    # Bisection bracket: M_2 in [1e-4, 1e4] M_sun.
    lo, hi = 1e-4, 1e4
    f_lo = lo / (M1 + lo) ** (2.0 / 3.0) - K
    f_hi = hi / (M1 + hi) ** (2.0 / 3.0) - K
    if f_lo > 0:
        # Even the smallest M_2 exceeds the required K -- inversion sets M_2
        # at the lower bound.
        return lo
    if f_hi < 0:
        # Even M_2 = 1e4 cannot reach the observed acceleration -- unphysical.
        return hi
    for _ in range(80):
        mid = 0.5 * (lo + hi)
        fm = mid / (M1 + mid) ** (2.0 / 3.0) - K
        if fm > 0:
            hi = mid
        else:
            lo = mid
    return 0.5 * (lo + hi)


def M2_range(accel_mas_yr2: float,
             plx_mas: float,
             M1: float = 1.5,
             P_yr_min: float = 3.0,
             P_yr_max: float = 100.0,
             n_grid: int = 32) -> Optional[Tuple[float, float, float]]:
    """Return (M_2_min, M_2_median, M_2_max) over a log-P grid.

    For each P_yr in geomspace([P_yr_min, P_yr_max], n_grid), invert the
    acceleration formula to get M_2, then report the min/median/max of
    the resulting array.

    Note that the M_2 vs. P_yr relation is monotone (longer P -> larger M_2
    for the same |a|), so M_2_min = M_2(P_yr_min) and M_2_max = M_2(P_yr_max).
    We compute the full grid to allow `median` reporting and to defensively
    keep the API parallel to a more general (eccentric, inclined) variant.

    Returns None if any input is invalid.
    """
    if accel_mas_yr2 is None or plx_mas is None:
        return None
    try:
        if (math.isnan(float(accel_mas_yr2))
                or math.isnan(float(plx_mas))):
            return None
    except (TypeError, ValueError):
        return None
    if accel_mas_yr2 <= 0 or plx_mas <= 0:
        return None

    Pgrid = np.geomspace(P_yr_min, P_yr_max, n_grid)
    M2s = np.empty_like(Pgrid)
    for i, P in enumerate(Pgrid):
        m2 = M2_from_acceleration(accel_mas_yr2, plx_mas, M1, float(P))
        M2s[i] = m2 if m2 is not None else float('nan')

    if np.all(np.isnan(M2s)):
        return None
    M2_min = float(np.nanmin(M2s))
    M2_med = float(np.nanmedian(M2s))
    M2_max = float(np.nanmax(M2s))
    return (M2_min, M2_med, M2_max)


# ---------------------------------------------------------------------------
# RV-consistency cross-check: joint RV + astrometric mass (added 2026-05-31)
# ---------------------------------------------------------------------------
# The astrometry-only M2 above assumes the FULL acceleration is sky-projected
# (face-on) and marginalizes flat in log-P, which systematically OVER-states the
# headline median.  Example: Gaia DR3 4698497413538721408 (HD 10711) has
# astrometry-only M2_median = 4.758 Msun ("dark_candidate"), but the source's OWN
# measured RV (rv_amplitude_robust = 15.86 km/s -> K1 = 7.9 km/s) collapses the
# mass to ~0.6-1.4 Msun at the short periods favored by its 9-parameter (jerk)
# solution -- a white dwarf, not a NS/BH.
#
# When a source HAS a significant RV variation, the spectroscopic K1 pins the
# inclination (sin i = K1 / v1, v1 = the primary's 3-D orbital velocity) AND the
# sky-projected acceleration (a_obs = a_faceon * sqrt((1 + cos^2 i)/2)); both must
# be produced by the SAME circular orbit, giving one self-consistent (M2, i) per
# trial period.  Validated against HD 10711 (2026-05-31; /tmp/g4698_joint2.py).
#
# NOTE: both M2_from_acceleration() above and the JOINT solution below now use the
# exact two-body exponent (2/3) (corrected 2026-05-31; the face-on inversion
# previously used (1/3), which under-stated M2 increasingly with P).

_G_SI = 6.6743e-11
_MSUN = 1.98892e30
_AU = 1.495978707e11
_YR = 3.15576e7
_PC = 3.0856775815e16
_MAS_PER_RAD = 206264.806e3


def _bisect_root(f, lo, hi, n_iter: int = 100):
    """Bisection root of monotone f on [lo, hi] (requires a sign change)."""
    flo, fhi = f(lo), f(hi)
    if flo == 0.0:
        return lo
    if fhi == 0.0:
        return hi
    if (flo > 0.0) == (fhi > 0.0):
        return None
    for _ in range(n_iter):
        mid = 0.5 * (lo + hi)
        fm = f(mid)
        if (fm > 0.0) == (flo > 0.0):
            lo, flo = mid, fm
        else:
            hi = mid
    return 0.5 * (lo + hi)


def _primary_v_and_faceon_accel(P_yr: float, M1: float, M2: float, plx_mas: float):
    """(v1 [m/s], face-on angular acceleration [mas/yr^2]) of the primary's reflex
    circular orbit, from the exact two-body relation a1 = a_rel * M2/Mtot."""
    Mtot = M1 + M2
    a_rel_AU = (Mtot * P_yr ** 2) ** (1.0 / 3.0)
    a1_m = a_rel_AU * _AU * M2 / Mtot
    P_s = P_yr * _YR
    v1 = 2.0 * math.pi * a1_m / P_s
    d_pc = 1000.0 / plx_mas
    af = (4.0 * math.pi ** 2 * a1_m / P_s ** 2 / (d_pc * _PC)) * _MAS_PER_RAD * _YR ** 2
    return v1, af


def joint_m2_from_accel_rv(accel_mas_yr2, plx_mas, K1_kms, M1, P_yr):
    """Companion mass from the JOINT (RV K1 + astrometric acceleration) constraint
    at a fixed circular-orbit period.  The same orbit must reproduce both the
    spectroscopic K1 (sin i = K1/v1) and the observed sky-projected acceleration
    (a_obs = a_faceon * sqrt((1+cos^2 i)/2)).  Returns (M2, i_deg) or None.  If even
    the edge-on (sin i=1) spectroscopic mass floor already over-produces the
    acceleration, returns (floor, 90.0)."""
    try:
        accel_mas_yr2 = float(accel_mas_yr2); plx_mas = float(plx_mas)
        K1_ms = float(K1_kms) * 1000.0; M1 = float(M1); P_yr = float(P_yr)
    except (TypeError, ValueError):
        return None
    if not all(map(math.isfinite, (accel_mas_yr2, plx_mas, K1_ms, M1, P_yr))):
        return None
    if min(accel_mas_yr2, plx_mas, K1_ms, M1, P_yr) <= 0:
        return None
    fM = (P_yr * _YR) * K1_ms ** 3 / (2.0 * math.pi * _G_SI) / _MSUN   # spec. mass fn floor
    floor = _bisect_root(lambda m: m ** 3 / (M1 + m) ** 2 - fM, 1e-5, 500.0)
    if floor is None:
        return None

    def resid(M2):
        v1, af = _primary_v_and_faceon_accel(P_yr, M1, M2, plx_mas)
        s = K1_ms / v1
        if s > 1.0:
            return -999.0
        proj = math.sqrt((1.0 + (1.0 - s * s)) / 2.0)
        return af * proj - accel_mas_yr2

    lo = floor * (1.0 + 1e-9)
    if resid(lo) > 0.0:
        return float(floor), 90.0
    M2 = _bisect_root(resid, lo, 500.0)
    if M2 is None:
        M2 = floor
    v1, _ = _primary_v_and_faceon_accel(P_yr, M1, M2, plx_mas)
    i_deg = math.degrees(math.asin(min(K1_ms / v1, 1.0)))
    return float(M2), float(i_deg)


def joint_m2_range(accel_mas_yr2, plx_mas, K1_kms, M1, Pgrid):
    """(M2_min, M2_median, M2_max, M2_at_shortest_P, i_at_shortest_P) of the joint
    RV+astrometric solution over `Pgrid` (yr).  None if no period yields a soln."""
    out = []
    for P in Pgrid:
        r = joint_m2_from_accel_rv(accel_mas_yr2, plx_mas, K1_kms, M1, float(P))
        if r is not None:
            out.append((float(P), r[0], r[1]))
    if not out:
        return None
    out.sort(key=lambda t: t[0])
    masses = [m for _, m, _ in out]
    return (float(min(masses)), float(np.median(masses)), float(max(masses)),
            float(out[0][1]), float(out[0][2]))


def jerk_aware_period_grid(nss_solution_type, P_yr_min: float = 3.0,
                           P_yr_max: float = 100.0, jerk_P_yr_max: float = 12.0,
                           n_grid: int = 32):
    """Period grid for the inversion, weighted toward short P for jerk solutions.
    An Acceleration9 (9-parameter) fit includes a measured JERK, which is only
    well-constrained when the orbital curvature changes appreciably over the
    ~2.83-yr DR3 baseline -> P not >> baseline.  So Acceleration9 is capped near a
    few x baseline (jerk_P_yr_max, default 12 yr); Acceleration7 (constant accel)
    keeps the long P_yr_max.  Returns (grid, pmax_used)."""
    st = str(nss_solution_type or '')
    pmax = jerk_P_yr_max if st == 'Acceleration9' else P_yr_max
    return np.geomspace(P_yr_min, pmax, n_grid), pmax


def acceleration_magnitude(accel_ra: float, accel_dec: float) -> Optional[float]:
    """Quadrature sum of accel components (mas/yr^2).  None if either NaN."""
    if accel_ra is None or accel_dec is None:
        return None
    try:
        ar = float(accel_ra)
        ad = float(accel_dec)
    except (TypeError, ValueError):
        return None
    if math.isnan(ar) or math.isnan(ad):
        return None
    return math.sqrt(ar * ar + ad * ad)


def acceleration_magnitude_error(accel_ra: float, accel_dec: float,
                                 accel_ra_err: float, accel_dec_err: float) -> Optional[float]:
    """Error on |a| via standard error propagation."""
    am = acceleration_magnitude(accel_ra, accel_dec)
    if am is None or am <= 0:
        return None
    try:
        ar = float(accel_ra)
        ad = float(accel_dec)
        ar_e = float(accel_ra_err)
        ad_e = float(accel_dec_err)
    except (TypeError, ValueError):
        return None
    if math.isnan(ar_e) or math.isnan(ad_e):
        return None
    var = (ar * ar_e) ** 2 + (ad * ad_e) ** 2
    return math.sqrt(var) / am


# ---------------------------------------------------------------------------
# Filter #29-31 helpers (vendored from v2_corrected/consumer_v2.py)
# ---------------------------------------------------------------------------

def _nan_safe(v):
    if v is None:
        return None
    try:
        if isinstance(v, float) and math.isnan(v):
            return None
    except TypeError:
        return None
    return float(v)


def filter29_v3(in_sb2: bool, nss_solution_type: Optional[str]) -> str:
    """F#29 -- SB2 reject.  Acceleration-channel sources are astrometric-only
    so SB2 must come from the gaia_source RV pipeline (rv_amplitude flagged
    SB2) or from external SB2 lookup.  Returns 'PASS' or 'FAIL'.
    """
    nss = str(nss_solution_type or '')
    if 'SB2' in nss:
        return 'FAIL'
    if bool(in_sb2):
        return 'FAIL'
    return 'PASS'


def filter30_v3(bp_rp, logg_gspphot, logg_gspspec_ann, logg_gspspec,
                teff_gspphot=None, teff_gspspec_ann=None):
    """Same as v2 -- chromatic-bias / K-giant rejection."""
    logg_gs = _nan_safe(logg_gspphot)
    logg_ann = _nan_safe(logg_gspspec_ann)
    logg_sp = _nan_safe(logg_gspspec)
    if logg_gs is not None:
        logg_used, logg_source = logg_gs, 'gspphot'
    elif logg_ann is not None:
        logg_used, logg_source = logg_ann, 'gspspec_ann'
    elif logg_sp is not None:
        logg_used, logg_source = logg_sp, 'gspspec'
    else:
        logg_used, logg_source = None, 'NONE'

    teff_used = _nan_safe(teff_gspspec_ann)
    if teff_used is None:
        teff_used = _nan_safe(teff_gspphot)

    bp_rp_v = _nan_safe(bp_rp)
    cbias_color = bp_rp_v is not None and bp_rp_v > 1.2
    cbias_logg = logg_used is not None and logg_used < 2.7
    cbias_kgiant = (teff_used is not None and 3700.0 <= teff_used <= 5200.0
                    and (logg_used is None or logg_used < 3.0))
    cbias_risk = bool(cbias_color or cbias_logg or cbias_kgiant)
    status = 'FAIL' if cbias_risk else 'PASS'

    bits = []
    if cbias_color:
        bits.append(f'BP-RP={bp_rp_v:.2f} > 1.2')
    if cbias_logg:
        bits.append(f'log g={logg_used:.2f} ({logg_source}) < 2.7')
    if cbias_kgiant:
        bits.append(f'K-giant proxy (Teff={teff_used:.0f} K, logg<3)')
    reason = ', '.join(bits) if bits else 'no chromatic-bias signatures'
    return status, cbias_risk, logg_used, logg_source, reason


def filter31_v3(rv_amplitude_robust, rv_chisq_pvalue):
    """F#31 -- RV reality check.  Many acceleration-channel sources have NO
    RV at all (faint or hot), in which case we return NO_DATA.
    """
    if (rv_amplitude_robust is None or rv_chisq_pvalue is None):
        return 'NO_DATA'
    try:
        K = float(rv_amplitude_robust)
        p = float(rv_chisq_pvalue)
    except (TypeError, ValueError):
        return 'NO_DATA'
    if math.isnan(K) or math.isnan(p):
        return 'NO_DATA'
    if K > 5 and p < 0.05:
        return 'PASS'
    if K > 5 and p > 0.5:
        return 'FAIL'
    return 'AMBIGUOUS'


# ---------------------------------------------------------------------------
# Tier classification for the acceleration channel
# ---------------------------------------------------------------------------

def tier_label_v3(M2_min: Optional[float],
                  M2_max: Optional[float],
                  f29: str,
                  f30: str,
                  f31: str,
                  rv_flag: str = 'NO_RV_VAR') -> str:
    """Acceleration-channel tier rule (no F#32 because no orbit fit):

      Tier-1 BH: M2_min >= 3 (BH-mass even at most pessimistic period)
      Tier-1 NS: M2_min >= 1.2 (NS-mass even at P_min) and M2_min < 3
      Tier-2:    M2_max >= 1.2 but M2_min < 1.2 (compact-object possible
                 but P-dependent)
      Rejected:  M2_max < 1.2 (stellar at all assumed periods)

    F#29 and F#30 are demoting filters: a Tier-1 candidate that fails F#29
    or F#30 is demoted to "Demoted (failed F#XX)".  F#31 -- if it fails
    that's a Demoted; AMBIGUOUS or NO_DATA leaves the tier as-is (note that
    acceleration sources don't have F#32).
    """
    if M2_min is None or M2_max is None:
        return 'Rejected (inversion failed)'

    # Mass-based tier
    if M2_min >= 3.0:
        base = 'Tier-1 BH'
    elif M2_min >= 1.2:
        base = 'Tier-1 NS'
    elif M2_max >= 1.2:
        base = 'Tier-2 (P-degenerate compact-object candidate)'
    else:
        base = f'Rejected (stellar at all P; M2_max={M2_max:.2f})'

    # Only the Tier-1 categories are subject to demoting filters
    if base.startswith('Tier-1') or base.startswith('Tier-2'):
        if f29 == 'FAIL':
            return f'Demoted (failed F#29 SB2) -- was {base}'
        if f30 == 'FAIL':
            return f'Demoted (failed F#30 K-giant chromatic) -- was {base}'
        if f31 == 'FAIL':
            return f'Demoted (failed F#31 phantom RV) -- was {base}'
        if rv_flag == 'OVERSTATED_TO_WD_LOWMASS':
            return (f'Demoted (RV-joint short-P mass is WD/low-mass; '
                    f'astrometry-only over-stated) -- was {base}')

    return base


# ---------------------------------------------------------------------------
# One-row v3 acceleration derivation
# ---------------------------------------------------------------------------

def derive_row_v3(row: dict,
                  M1_prior: float = 1.5,
                  P_yr_min: float = 3.0,
                  P_yr_max: float = 100.0) -> dict:
    """Single-source v3 (acceleration channel) derivation.

    `row` is a dict-like with the following keys:
        accel_ra, accel_dec        (mas/yr^2; from nss_acceleration_astro)
        accel_ra_error, accel_dec_error
        parallax                   (mas; prefer NSS-internal parallax if present)
        bp_rp                      (gaia_source.bp_rp)
        logg_gspphot, logg_gspspec_ann, logg_gspspec
        teff_gspphot, teff_gspspec_ann
        rv_amplitude_robust, rv_chisq_pvalue
        in_sb2 (bool, default False)
        nss_solution_type (str, e.g. 'Acceleration7' or 'Acceleration9')
        significance               (passed through for reporting)

    Returns dict with all v3-cascade columns (M2_min_v3, M2_max_v3, tier_v3,
    filter30_v3, etc.) or {'error': '...'} if derivation impossible.
    """
    accel_ra = row.get('accel_ra')
    accel_dec = row.get('accel_dec')
    accel_ra_err = row.get('accel_ra_error')
    accel_dec_err = row.get('accel_dec_error')
    plx = row.get('parallax')

    accel_mag = acceleration_magnitude(accel_ra, accel_dec)
    accel_err = acceleration_magnitude_error(accel_ra, accel_dec,
                                             accel_ra_err, accel_dec_err)

    if accel_mag is None or accel_mag <= 0:
        return {'error': 'invalid acceleration magnitude'}
    plx_used = _nan_safe(plx)
    if plx_used is None or plx_used <= 0:
        return {'error': 'invalid parallax'}

    rng = M2_range(accel_mag, plx_used, M1=M1_prior,
                   P_yr_min=P_yr_min, P_yr_max=P_yr_max)
    if rng is None:
        return {'error': 'inversion failed'}
    M2_min, M2_med, M2_max = rng

    # F#29 (SB2)
    in_sb2 = bool(row.get('in_sb2', False))
    nss_type = row.get('nss_solution_type')
    f29 = filter29_v3(in_sb2, nss_type)

    # F#30 (chromatic / K-giant)
    f30, cbias, logg_used, logg_source, f30_reason = filter30_v3(
        bp_rp=row.get('bp_rp'),
        logg_gspphot=row.get('logg_gspphot'),
        logg_gspspec_ann=row.get('logg_gspspec_ann'),
        logg_gspspec=row.get('logg_gspspec'),
        teff_gspphot=row.get('teff_gspphot'),
        teff_gspspec_ann=row.get('teff_gspspec_ann'),
    )

    # F#31 (RV reality)
    f31 = filter31_v3(row.get('rv_amplitude_robust'),
                      row.get('rv_chisq_pvalue'))

    # --- RV-consistency cross-check (joint RV + astrometric mass) ---
    K_obs = _nan_safe(row.get('rv_amplitude_robust'))
    pval = _nan_safe(row.get('rv_chisq_pvalue'))
    has_rv_var = (K_obs is not None and pval is not None
                  and K_obs > 0 and pval < 0.05)
    Pgrid_joint, jerk_pmax = jerk_aware_period_grid(nss_type, P_yr_min, P_yr_max)
    (M2_joint_min, M2_joint_med, M2_joint_max,
     M2_joint_shortP, i_joint_shortP, K1_used) = (None, None, None, None, None, None)
    rv_flag = 'NO_RV_VAR'
    if has_rv_var:
        K1_used = K_obs / 2.0   # rv_amplitude_robust is peak-to-peak; K1 = half (v2 Corr. B)
        jr = joint_m2_range(accel_mag, plx_used, K1_used, M1_prior, Pgrid_joint)
        if jr is None:
            rv_flag = 'JOINT_NO_SOLUTION'
        else:
            (M2_joint_min, M2_joint_med, M2_joint_max,
             M2_joint_shortP, i_joint_shortP) = jr
            if M2_med is not None and M2_med >= 1.2 and M2_joint_shortP < 1.2:
                rv_flag = 'OVERSTATED_TO_WD_LOWMASS'
            elif M2_joint_shortP >= 3.0:
                rv_flag = 'CONSISTENT_BH'
            elif M2_joint_shortP >= 1.2:
                rv_flag = 'CONSISTENT_NS'
            else:
                rv_flag = 'CONSISTENT_LOWMASS'

    tier = tier_label_v3(M2_min, M2_max, f29, f30, f31, rv_flag)

    return {
        'accel_mag_mas_yr2': accel_mag,
        'accel_mag_err': accel_err,
        'plx_used': plx_used,
        'M1_msun_v3': float(M1_prior),
        'P_yr_min_grid': float(P_yr_min),
        'P_yr_max_grid': float(P_yr_max),
        'M2_min_v3': M2_min,
        'M2_median_v3': M2_med,
        'M2_max_v3': M2_max,
        'logg_used_v3': logg_used,
        'logg_source_v3': logg_source,
        'cbias_risk_v3': cbias,
        'filter29_v3': f29,
        'filter30_v3': f30,
        'filter30_reason_v3': f30_reason,
        'filter31_v3': f31,
        'has_rv_var_v3': bool(has_rv_var),
        'K1_used_kms_v3': K1_used,
        'M2_joint_min_v3': M2_joint_min,
        'M2_joint_median_v3': M2_joint_med,
        'M2_joint_max_v3': M2_joint_max,
        'M2_joint_shortP_v3': M2_joint_shortP,
        'i_joint_shortP_deg_v3': i_joint_shortP,
        'jerk_P_yr_max_grid_v3': float(jerk_pmax),
        'rv_consistency_flag_v3': rv_flag,
        'tier_v3': tier,
    }
