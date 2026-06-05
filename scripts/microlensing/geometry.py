"""Astrometric + photometric microlensing geometry.

Pure-physics core for the astrometric-microlensing event predictor (lane #118).
NO network, NO I/O — deterministic functions only, so it can be unit-tested and
re-run unchanged on Gaia DR4 astrometry (the whole point: DR4 overhauls every
input number, not the math).

What it computes, given a foreground LENS (5-parameter astrometry) and a
~static background SOURCE:

  * closest_approach(...)  -> epoch t0 and minimum angular separation u_min*theta_E
        of the lens track past the source over a date window. The lens moves on
        the sky by proper motion + annual parallax; the source is treated as
        fixed (its own PM, if known, is subtracted into a *relative* PM by the
        caller, or neglected — background stars are distant/slow).
  * einstein_radius(M_L, D_L, D_S)  -> theta_E in mas.
  * magnification(u)        -> photometric magnification A(u) (point-source).
  * centroid_shift(u)       -> astrometric centroid shift |dtheta| in units of
        theta_E (the UNRESOLVED, luminous-source-blended-with-images centroid,
        which is what Gaia/Kluter+2018 measure), AND the dark-lens limit.
  * predict_event(...)      -> for an assumed M_L, the peak centroid shift (uas)
        and peak magnification at the geometric u_min.
  * mass_from_shift(...)    -> invert an OBSERVED peak centroid shift to M_L.

Sign / definition conventions (match Kluter+2018 A&A 615 L11, Dominik & Sahu
2000 ApJ 534 213, Paczynski 1996, Bramich 2018 A&A 618 A44):

  theta_E = sqrt( (4 G M_L / c^2) * (1/D_L - 1/D_S) )         [angle]
          = sqrt( kappa * M_L * pi_rel ),   kappa = 8.144 mas/Msun,
          pi_rel = pi_L - pi_S  (relative parallax, mas), M_L in Msun.
  u       = instantaneous lens-source separation / theta_E   (dimensionless).
  A(u)    = (u^2 + 2) / (u sqrt(u^2 + 4)).
  Two images form at theta_+/- = 0.5( u +/- sqrt(u^2+4) ) * theta_E from lens.

  Centroid shift, the observable for astrometric microlensing. Two regimes:
    (1) UNRESOLVED MAJOR+MINOR images, NO luminous lens light (a *dark* lens):
        the light-centroid of the two images, relative to the unlensed source,
        is   dtheta_c = u / (u^2 + 2) * theta_E   (Dominik & Sahu 2000 eq.).
        Peaks at u = sqrt(2) with dtheta_c,max = theta_E / (2 sqrt(2)) ~ 0.354 theta_E.
    (2) LUMINOUS lens with flux ratio g = F_L/F_S(unlensed): the measured
        centroid is a flux-weighted blend of (lensed source images) + (steady
        lens). This is the general Kluter+2018 case; we expose the dark-lens
        limit (g=0) as the headline number and provide the blended form.

This module deliberately keeps the *photocentre of the source images* formula
(regime 1) as the canonical "centroid shift" because the project's targets are
DARK / faint-lens cases where that is the signal; mass_from_shift inverts it.
"""
from __future__ import annotations

import math
import warnings
from dataclasses import dataclass
from typing import Optional, Tuple

import numpy as np

# astropy's ERFA emits "dubious year" warnings for the >2024 prediction epochs;
# they are benign (future leap-second tables), silence them here.
try:  # pragma: no cover
    from erfa import ErfaWarning
    warnings.filterwarnings("ignore", category=ErfaWarning)
except Exception:  # pragma: no cover
    pass

# --------------------------------------------------------------------------- #
# Physical constants (SI + astro)
# --------------------------------------------------------------------------- #
G_SI = 6.67430e-11          # m^3 kg^-1 s^-2
C_SI = 2.99792458e8         # m/s
MSUN = 1.98892e30           # kg
PC_M = 3.0856775814913673e16  # m
AU_M = 1.495978707e11       # m
MAS_PER_RAD = 180.0 / math.pi * 3600.0 * 1000.0   # mas per radian
RAD_PER_MAS = 1.0 / MAS_PER_RAD
YR_D = 365.25               # days per Julian year

# Einstein-radius constant kappa such that theta_E[mas] = sqrt(kappa * M[Msun] * pi_rel[mas]).
# kappa = 4G/c^2 * (1 AU) / (1 mas in rad) * MSUN, all reduced to mas^2 / (Msun * mas).
# Numerically kappa = 8.144 mas / Msun (Gould 2000; Kluter+2018). We compute it
# from constants so DR4 / constant updates flow through.
KAPPA_MAS_PER_MSUN = (
    4.0 * G_SI * MSUN / C_SI**2          # = Schwarzschild-like length scale [m] per Msun
    / AU_M                                # divide by 1 AU  -> dimensionless * (1/D in 1/AU)
    * MAS_PER_RAD                         # pi_rel enters in mas; theta_E^2 in mas^2 -> one factor
)
# The clean closed form: theta_E^2 = (4GM/c^2)(1/D_L - 1/D_S). With pi = 1AU/D,
# (1/D_L - 1/D_S) = pi_rel[rad] / 1AU = pi_rel[mas]*RAD_PER_MAS / 1AU. Then
# theta_E[rad]^2 = 4GM/c^2 * pi_rel[mas]*RAD_PER_MAS/AU_M, convert to mas^2:
#   theta_E[mas]^2 = (4GM/c^2/AU_M) * MAS_PER_RAD * pi_rel[mas]  -> kappa above. M in kg.
# Per-Msun:
KAPPA = KAPPA_MAS_PER_MSUN
# sanity: KAPPA should be ~8.144


# --------------------------------------------------------------------------- #
# Einstein radius
# --------------------------------------------------------------------------- #
def einstein_radius_from_parallax(mass_msun: float, pi_rel_mas: float) -> float:
    """theta_E [mas] = sqrt(kappa * M[Msun] * pi_rel[mas]).

    pi_rel = pi_lens - pi_source (relative parallax, mas). Must be > 0 (lens in
    front). Returns mas. This is the form used in practice (Gaia gives parallaxes).
    """
    if mass_msun <= 0 or pi_rel_mas <= 0:
        return float("nan")
    return math.sqrt(KAPPA * mass_msun * pi_rel_mas)


def einstein_radius(mass_msun: float, d_lens_pc: float,
                    d_source_pc: float) -> float:
    """theta_E [mas] from the textbook form sqrt((4GM/c^2)(1/D_L - 1/D_S)).

    Distances in parsec. If d_source is None/inf the source-term vanishes
    (lens-only limit). Equivalent to the parallax form with
    pi_rel = 1000/D_L - 1000/D_S [mas].
    """
    if mass_msun <= 0 or d_lens_pc is None or d_lens_pc <= 0:
        return float("nan")
    inv_ds = 0.0 if (d_source_pc is None or not np.isfinite(d_source_pc)
                     or d_source_pc <= 0) else 1.0 / (d_source_pc * PC_M)
    inv_dl = 1.0 / (d_lens_pc * PC_M)
    diff = inv_dl - inv_ds
    if diff <= 0:
        return float("nan")
    theta_rad = math.sqrt(4.0 * G_SI * mass_msun * MSUN / C_SI**2 * diff)
    return theta_rad * MAS_PER_RAD


def einstein_radius_phys_au(theta_e_mas: float, d_lens_pc: float) -> float:
    """Physical Einstein radius r_E = theta_E * D_L, in AU (for context)."""
    return theta_e_mas * RAD_PER_MAS * d_lens_pc * PC_M / AU_M


# --------------------------------------------------------------------------- #
# Magnification & centroid shift  (functions of u = sep/theta_E)
# --------------------------------------------------------------------------- #
def magnification(u):
    """Point-source point-lens photometric magnification A(u)."""
    u = np.asarray(u, dtype=float)
    return (u**2 + 2.0) / (u * np.sqrt(u**2 + 4.0))


def magnitude_change(u):
    """Brightening in magnitudes, dm = -2.5 log10 A(u) (negative = brighter)."""
    return -2.5 * np.log10(magnification(u))


def centroid_shift_dark_lens(u):
    """Astrometric centroid shift in units of theta_E for a DARK (non-luminous)
    lens — the photocentre of the unresolved major+minor images relative to the
    unlensed source position.

        dtheta_c / theta_E = u / (u^2 + 2)              (Dominik & Sahu 2000)

    Peaks at u = sqrt(2): max = 1/(2 sqrt(2)) = 0.35355 theta_E.
    This is the project-relevant signal (an isolated dark remnant has no lens
    light to blend in). Returns dimensionless (multiply by theta_E for an angle).
    """
    u = np.asarray(u, dtype=float)
    return u / (u**2 + 2.0)


def centroid_shift_blended(u, g):
    """Centroid shift in units of theta_E for a LUMINOUS lens of flux ratio
    g = F_lens / F_source(unlensed), the general Gaia/Kluter+2018 observable.

    The unresolved system = (two magnified source images) + (steady lens light).
    Measuring positions relative to the unlensed source+lens blend baseline, the
    shift along the lens-source axis is (Kluter+2018 eq. 4; Bramich 2018):

        delta(u, g) = [ u (u^2 + 3) / (u^2 + 2) - g*u ] / [ (u^2+2)/(u sqrt(u^2+4)) ... ]

    That full algebra is fiddly; we use the compact Kluter form for the shift of
    the *source* light-centroid (images only), then blend with the lens:

        theta_images_centroid (rel. to lens) = u (u^2+3)/(u^2+2) * theta_E
        With lens at 0 and source-unlensed at u*theta_E, and total flux
        F_tot = A(u) F_S + F_L, the measured centroid relative to the
        source-unlensed-plus-lens baseline is returned (units of theta_E).

    For g = 0 this reduces to centroid_shift_dark_lens(u). For g -> inf the lens
    light dominates and the shift -> 0. Sign convention: magnitude only.
    """
    u = np.asarray(u, dtype=float)
    A = magnification(u)
    # Centroid of the two images, measured from the lens, along the axis:
    theta_img = u * (u**2 + 3.0) / (u**2 + 2.0)        # in theta_E, from lens
    # Total flux-weighted centroid (lens at 0, images at theta_img, source-unlensed
    # at u). Baseline (no lensing) centroid = (A->1): (1*u + g*0)/(1+g) = u/(1+g).
    cen_lensed = (A * theta_img + g * 0.0) / (A + g)   # in theta_E, from lens
    cen_base = (1.0 * u + g * 0.0) / (1.0 + g)         # unlensed blend, from lens
    return np.abs(cen_lensed - cen_base)


# convenience: the canonical (dark-lens) curve and its peak
U_PEAK_CENTROID = math.sqrt(2.0)
CENTROID_PEAK_FRAC = 1.0 / (2.0 * math.sqrt(2.0))      # 0.35355 theta_E


# --------------------------------------------------------------------------- #
# Lens sky-track: closest approach to a static source over a date window
# --------------------------------------------------------------------------- #
@dataclass
class Astrometry:
    """Minimal 5-parameter astrometry for a star (ICRS)."""
    ra_deg: float
    dec_deg: float
    pmra_mas_yr: float        # pmRA* = mu_alpha cos(dec)
    pmdec_mas_yr: float
    parallax_mas: float
    ref_epoch_jyear: float = 2016.0   # Gaia DR3 reference epoch


def _earth_barycentric_au(jyear):
    """Earth barycentric position (X, Y, Z) in AU, equatorial ICRS, at epoch
    jyear (Julian year). Prefers astropy's ephemeris (accurate to << 1 mas);
    falls back to a circular-orbit analytic model if astropy is unavailable.
    """
    try:
        from astropy.coordinates import get_body_barycentric
        from astropy.time import Time
        import astropy.units as u
        e = get_body_barycentric("earth", Time(jyear, format="jyear"))
        return (e.x.to(u.AU).value, e.y.to(u.AU).value, e.z.to(u.AU).value)
    except Exception:
        # analytic fallback: circular Earth orbit, obliquity-tilted to equatorial.
        eps = math.radians(23.43928)
        t = jyear - 2000.0
        # Sun mean longitude -> Earth is at L+180 in heliocentric ecliptic.
        L = math.radians((280.460 + 0.9856474 * (t * YR_D)) % 360.0)
        # Earth heliocentric ecliptic (AU), opposite the Sun:
        xe, ye = -math.cos(L), -math.sin(L)
        # ecliptic -> equatorial:
        X = xe
        Y = ye * math.cos(eps)
        Z = ye * math.sin(eps)
        return (X, Y, Z)


def _earth_parallax_factors(jyear, ra_rad, dec_rad):
    """Annual-parallax displacement factors (F_alpha*, F_delta) per unit parallax,
    so the apparent position offset = parallax * (F_alpha*, F_delta), in the same
    units as the parallax (mas). Uses the standard equatorial parallax factors
    (e.g. ESA 1997 / Green 1985):

        F_alpha* =  X sin(a) - Y cos(a)
        F_delta  =  X cos(a) sin(d) + Y sin(a) sin(d) - Z cos(d)

    with (X, Y, Z) the Earth barycentric position in AU. Validated against
    astropy's Earth ephemeris (round-trips a known event TCA + impact parameter
    to < 0.1 mas / < 1 day; see validate.py).
    """
    X, Y, Z = _earth_barycentric_au(jyear)
    sa, ca = math.sin(ra_rad), math.cos(ra_rad)
    sd, cd = math.sin(dec_rad), math.cos(dec_rad)
    Fa = (X * sa - Y * ca)
    Fd = (X * ca * sd + Y * sa * sd - Z * cd)
    return Fa, Fd


def lens_position(astro: Astrometry, jyear):
    """Sky position of the lens at epoch(s) jyear (Julian year), returned as
    offsets (dRA*, dDec) in mas relative to the ref-epoch ICRS position, INCLUDING
    proper motion and annual parallax. dRA* = dRA*cos(dec).

    jyear may be a scalar or array.
    """
    jyear = np.asarray(jyear, dtype=float)
    dt = jyear - astro.ref_epoch_jyear            # years
    dra = astro.pmra_mas_yr * dt                  # mas (already *cos dec)
    ddec = astro.pmdec_mas_yr * dt
    ra_rad = math.radians(astro.ra_deg)
    dec_rad = math.radians(astro.dec_deg)
    if astro.parallax_mas and np.isfinite(astro.parallax_mas) and astro.parallax_mas != 0:
        fa, fd = _parallax_factors_vec(np.atleast_1d(jyear), ra_rad, dec_rad)
        dra = dra + astro.parallax_mas * fa.reshape(jyear.shape)
        ddec = ddec + astro.parallax_mas * fd.reshape(jyear.shape)
    return dra, ddec


def _parallax_factors_vec(jyears, ra_rad, dec_rad):
    """Vectorised parallax factors over an array of epochs (one astropy call)."""
    jyears = np.atleast_1d(np.asarray(jyears, dtype=float))
    try:
        from astropy.coordinates import get_body_barycentric
        from astropy.time import Time
        import astropy.units as u
        e = get_body_barycentric("earth", Time(jyears, format="jyear"))
        X = e.x.to(u.AU).value
        Y = e.y.to(u.AU).value
        Z = e.z.to(u.AU).value
    except Exception:
        X = np.empty_like(jyears); Y = np.empty_like(jyears); Z = np.empty_like(jyears)
        for i, y in enumerate(jyears):
            X[i], Y[i], Z[i] = _earth_barycentric_au(float(y))
    sa, ca = math.sin(ra_rad), math.cos(ra_rad)
    sd, cd = math.sin(dec_rad), math.cos(dec_rad)
    Fa = X * sa - Y * ca
    Fd = X * ca * sd + Y * sa * sd - Z * cd
    return Fa, Fd


@dataclass
class ClosestApproach:
    t0_jyear: float           # epoch of minimum separation
    sep_min_mas: float        # minimum angular separation (mas)
    sep_at_window_edges_mas: Tuple[float, float]
    rel_pm_mas_yr: float      # relative proper motion magnitude used


def closest_approach(lens: Astrometry, src_ra_deg: float, src_dec_deg: float,
                     t_start_jyear: float, t_end_jyear: float,
                     src_pmra_mas_yr: float = 0.0,
                     src_pmdec_mas_yr: float = 0.0,
                     n_grid: int = 4000) -> ClosestApproach:
    """Find the time of closest approach and minimum separation between the
    moving lens and a (nearly static) background source over [t_start, t_end].

    The source position at the lens ref-epoch is computed from its ICRS coords;
    its (usually small) proper motion can be supplied and is subtracted as a
    relative motion. Separation is on the local tangent plane through the source,
    with dRA* = (ra_lens - ra_src)*cos(dec_src). Dense-grid scan then parabolic
    refinement — robust against the parallactic wiggle (no closed form).
    """
    cosd = math.cos(math.radians(src_dec_deg))
    # offset of source from lens ref position, in mas (tangent plane at source)
    dra0 = (src_ra_deg - lens.ra_deg) * 3600e3 * cosd     # deg->mas, *cos dec
    ddec0 = (src_dec_deg - lens.dec_deg) * 3600e3

    grid = np.linspace(t_start_jyear, t_end_jyear, n_grid)
    lra, ldec = lens_position(lens, grid)                 # lens offset from its ref
    # source offset from lens ref, including source PM
    dt = grid - lens.ref_epoch_jyear
    sra = dra0 + src_pmra_mas_yr * dt
    sdec = ddec0 + src_pmdec_mas_yr * dt
    sep = np.hypot(lra - sra, ldec - sdec)                # mas

    i = int(np.argmin(sep))
    t0 = grid[i]
    sep_min = sep[i]
    # parabolic refinement if interior
    if 0 < i < n_grid - 1:
        x0, x1, x2 = grid[i-1], grid[i], grid[i+1]
        y0, y1, y2 = sep[i-1], sep[i], sep[i+1]
        denom = (y0 - 2*y1 + y2)
        if denom != 0:
            tv = x1 + 0.5 * (y0 - y2) / denom * (x1 - x0)
            if x0 <= tv <= x2:
                t0 = tv
                lra_v, ldec_v = lens_position(lens, np.array([tv]))
                dtv = tv - lens.ref_epoch_jyear
                sep_min = float(np.hypot(lra_v[0] - (dra0 + src_pmra_mas_yr*dtv),
                                         ldec_v[0] - (ddec0 + src_pmdec_mas_yr*dtv)))
    rel_pm = math.hypot(lens.pmra_mas_yr - src_pmra_mas_yr,
                        lens.pmdec_mas_yr - src_pmdec_mas_yr)
    return ClosestApproach(t0_jyear=float(t0), sep_min_mas=float(sep_min),
                           sep_at_window_edges_mas=(float(sep[0]), float(sep[-1])),
                           rel_pm_mas_yr=rel_pm)


# --------------------------------------------------------------------------- #
# End-to-end event prediction & inversion
# --------------------------------------------------------------------------- #
@dataclass
class EventPrediction:
    theta_e_mas: float
    u_min: float
    sep_min_mas: float
    t0_jyear: float
    peak_centroid_shift_uas: float       # dark-lens centroid shift at u_min, microarcsec
    peak_centroid_shift_uas_max: float   # the GLOBAL peak (at u=sqrt2) if track reaches it
    peak_magnification: float
    peak_delta_mag_mmag: float
    rel_pm_mas_yr: float
    crossing_time_days: float            # ~ theta_E / mu, the event timescale t_E


def predict_event(lens: Astrometry, src_ra_deg: float, src_dec_deg: float,
                  mass_msun: float, t_start_jyear: float, t_end_jyear: float,
                  src_parallax_mas: float = 0.0,
                  src_pmra_mas_yr: float = 0.0, src_pmdec_mas_yr: float = 0.0,
                  ) -> EventPrediction:
    """Predict the astrometric + photometric microlensing signal of `lens`
    passing `source` over the window, for an assumed lens mass.

    pi_rel = lens.parallax - src_parallax (mas). Background sources are usually
    much more distant, so src_parallax ~ 0 is the default and conservative for
    theta_E (slightly under-estimates if the source is nearby).
    """
    pi_rel = lens.parallax_mas - (src_parallax_mas or 0.0)
    theta_e = einstein_radius_from_parallax(mass_msun, pi_rel)
    ca = closest_approach(lens, src_ra_deg, src_dec_deg, t_start_jyear, t_end_jyear,
                          src_pmra_mas_yr, src_pmdec_mas_yr)
    u_min = ca.sep_min_mas / theta_e if (theta_e and theta_e > 0) else float("inf")
    # dark-lens centroid shift at the realised u_min:
    shift_frac = float(centroid_shift_dark_lens(u_min))
    peak_shift_uas = shift_frac * theta_e * 1000.0       # mas->uas
    # the global maximum the source could show if the track swept through u=sqrt2:
    peak_shift_uas_max = CENTROID_PEAK_FRAC * theta_e * 1000.0
    A = float(magnification(u_min))
    dmag_mmag = float(magnitude_change(u_min)) * 1000.0
    # event timescale t_E = theta_E / mu_rel
    t_E_days = (theta_e / ca.rel_pm_mas_yr * YR_D) if ca.rel_pm_mas_yr > 0 else float("nan")
    return EventPrediction(
        theta_e_mas=theta_e, u_min=u_min, sep_min_mas=ca.sep_min_mas,
        t0_jyear=ca.t0_jyear, peak_centroid_shift_uas=peak_shift_uas,
        peak_centroid_shift_uas_max=peak_shift_uas_max, peak_magnification=A,
        peak_delta_mag_mmag=dmag_mmag, rel_pm_mas_yr=ca.rel_pm_mas_yr,
        crossing_time_days=t_E_days)


def mass_from_centroid_shift(observed_shift_uas: float, u_min: float,
                             pi_rel_mas: float) -> float:
    """Invert an OBSERVED peak centroid shift (uas) at known u_min and pi_rel to
    the lens mass (Msun). This is the science return: a measured astrometric
    deflection -> a model-independent dark-lens mass.

        dtheta_c[mas] = [u/(u^2+2)] * theta_E,  theta_E = sqrt(kappa M pi_rel)
        => M = ( dtheta_c / ([u/(u^2+2)] ) )^2 / (kappa * pi_rel)
    """
    if u_min <= 0 or pi_rel_mas <= 0:
        return float("nan")
    frac = u_min / (u_min**2 + 2.0)
    theta_e_mas = (observed_shift_uas / 1000.0) / frac
    return theta_e_mas**2 / (KAPPA * pi_rel_mas)


def mass_from_peak_shift_unknown_umin(observed_peak_shift_uas: float,
                                      pi_rel_mas: float) -> float:
    """If only the GLOBAL peak shift is measured (the event swept through the
    maximum at u=sqrt2), invert assuming u_min<=sqrt2:
        dtheta_max = theta_E/(2 sqrt2)  =>  theta_E = 2 sqrt2 * dtheta_max.
    Returns an UPPER bound on theta_E -> a mass estimate (lower bound on M if the
    true u_min>sqrt2). Practical for first-pass mass scoping.
    """
    if pi_rel_mas <= 0:
        return float("nan")
    theta_e_mas = (observed_peak_shift_uas / 1000.0) * 2.0 * math.sqrt(2.0)
    return theta_e_mas**2 / (KAPPA * pi_rel_mas)


if __name__ == "__main__":  # quick self-check
    print(f"kappa = {KAPPA:.4f} mas/Msun  (expect ~8.144)")
    # 1 Msun lens at 50 pc, distant source:
    te = einstein_radius_from_parallax(1.0, 1000.0/50.0)
    print(f"theta_E(1 Msun, D_L=50pc, pi_rel=20 mas) = {te:.3f} mas")
    print(f"  centroid peak = {CENTROID_PEAK_FRAC*te*1000:.1f} uas at u=sqrt2")
    print(f"  A(u=1) = {float(magnification(1.0)):.4f}, "
          f"dm = {float(magnitude_change(1.0))*1000:.2f} mmag")
