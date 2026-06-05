"""DR4 candidate re-fit engine — astrometric orbit forward model + fitters.

Lane #116.  When Gaia DR4 publishes the per-transit astrometric time series
(which DR3 withheld), we can fit the photocentric orbit *directly* from the
along-scan (AL) abscissa measurements, instead of consuming the pre-fitted
Thiele-Innes coefficients.  This module provides:

  * the forward model that turns (5 astrometric params + a Keplerian orbit)
    into a predicted along-scan abscissa at each Gaia transit;
  * a 1-body fitter (5 astrometric + single Keplerian);
  * a multi-body fitter (1-body + an *acceleration* term, and 1-body + an
    *outer Keplerian*) for the hierarchical-triple / 2nd-companion hypothesis.

WHAT GAIA ACTUALLY MEASURES (and why we fit AL abscissae, not (ra,dec)).
Gaia is a scanning instrument: at each transit it measures a star's position
essentially in ONE direction — along the scan, at scan-angle psi.  The
measured quantity is the along-scan abscissa

    w = (Δα*) sin(psi) + (Δδ) cos(psi) + ϖ * f_par(t) + (μα*) (t-t0) sin(psi)
        + (μδ) (t-t0) cos(psi)  +  [orbit AL projection]                       (1)

where Δα* = Δα cos δ.  The 5 standard astrometric parameters are
(Δα*, Δδ, ϖ, μα*, μδ).  f_par(t) is the parallax factor projected onto the
scan direction (we accept it precomputed per transit, as DR4 is expected to
publish `parallax_factor_al`).  This is the standard AGIS / NSS observation
equation (Lindegren+2021, Halbwachs+2023 Gaia DR3 NSS documentation).

THE ORBIT TERM.  For an astrometric (photocentric) orbit the displacement of
the photocentre from the system barycentre, projected onto RA* and Dec, is the
classic Thiele-Innes form:

    Δα*_orb = B X + G Y
    Δδ_orb  = A X + F Y                                                         (2)

with the elliptical rectangular coordinates

    X = cos E - e,    Y = sqrt(1-e^2) sin E,                                    (3)

E the eccentric anomaly solved from Kepler's equation
    E - e sin E = M = 2π (t - T0) / P.                                          (4)

The along-scan projection of the orbit is then
    w_orb = Δα*_orb sin(psi) + Δδ_orb cos(psi).                                 (5)

(A,B,F,G) carry the semi-major axis a_phot, inclination i, and the node /
periastron angles; we fit them as free linear coefficients (so the fit is
linear in A,B,F,G and in the 5 astrometric params, and non-linear only in
P,e,T0).  a_phot and i are recovered from (A,B,F,G) post-fit with the SAME
vetted relations used across this repo:

    u = 0.5 (A^2+B^2+F^2+G^2),  v = A G - B F
    a_phot = sqrt(u + sqrt(u^2 - v^2))                 (Halbwachs+2023)
    cos i  = |A G - B F| / a_phot^2                    (NO sqrt — see below)

CRITICAL — the inclination relation has NO sqrt.  A 2026-05-31 bug audit found
a spurious sqrt wrapping the Campbell relation in three deep-dive scripts;
A*G-B*F = a^2 cos i, so cos i = |A*G-B*F| / a^2 directly.  We reproduce the
corrected form here (and a forward-construction test in test_refit.py guards
it).

MULTI-BODY VARIANTS (the triple / 2nd-companion hypothesis).
  (a) ACCELERATION model: add a barycentric acceleration (and optional jerk)
      to the 5-parameter part —
          + 0.5 g_α* (t-t0)^2 ... projected AL, optionally + (1/6) jerk (t)^3.
      A distant outer body whose period >> baseline shows up as a smooth
      acceleration; this is the cheap, robust triple probe.
  (b) DOUBLE-KEPLERIAN model: inner Keplerian (A,B,F,G,P1,e1,T01) + an outer
      Keplerian (A2,B2,F2,G2,P2,e2,T02).  Heavier; used when the acceleration
      model leaves structured residuals or when the outer period may be
      comparable to the baseline.

All fitting is least-squares on the AL abscissae weighted by 1/sigma_AL^2,
linear part solved in closed form at each (P,e,T0) and the non-linear period
parameters optimised by scipy least_squares (Levenberg–Marquardt-class TRF).

stdlib + numpy + scipy only.
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Optional, Sequence

import numpy as np
from scipy.optimize import least_squares

# Days per Julian year (the orbit P is carried in days, consistent with Gaia NSS).
DAYS_PER_YEAR = 365.25


# ---------------------------------------------------------------------------
# Vetted geometry: a_phot and inclination from Thiele-Innes (A,B,F,G).
# Mirrors scripts/streaming/v2_corrected/consumer_v2.photocentric_a_mas and the
# corrected (no-sqrt) cos i relation.  Kept local so the refit engine has no
# import dependency on the streaming package.
# ---------------------------------------------------------------------------

def photocentric_a(A: float, B: float, F: float, G: float) -> float:
    """Photocentric semi-major axis (same units as A,B,F,G; mas if they are mas).

    a = sqrt(u + sqrt(u^2 - v^2)),  u = 0.5(A^2+B^2+F^2+G^2),  v = A G - B F.
    """
    u = 0.5 * (A * A + B * B + F * F + G * G)
    v = A * G - B * F
    disc = max(0.0, u * u - v * v)
    return math.sqrt(u + math.sqrt(disc))


def inclination_from_ABFG(A: float, B: float, F: float, G: float) -> dict:
    """Return {'a': a_phot, 'cos_i', 'incl_deg'} from Thiele-Innes.

    cos i = |A G - B F| / a^2  (NO sqrt — Halbwachs+2023; 2026-05-31 bugfix).
    The node/periastron orientation (Ω, ω) is sign/branch ambiguous from
    (A,B,F,G) alone; only i, a_phot (and e,P,T0 from the fit) are needed for the
    mass-function chain, so we return i and a_phot.
    """
    u = 0.5 * (A * A + B * B + F * F + G * G)
    v = A * G - B * F
    disc = max(0.0, u * u - v * v)
    a2 = u + math.sqrt(disc)
    if a2 <= 0:
        return {'a': 0.0, 'cos_i': 1.0, 'incl_deg': 0.0}
    cosi = min(1.0, max(0.0, abs(v) / a2))
    return {'a': math.sqrt(a2), 'cos_i': cosi, 'incl_deg': math.degrees(math.acos(cosi))}


# ---------------------------------------------------------------------------
# Kepler solver — elliptical rectangular coordinates X, Y.
# ---------------------------------------------------------------------------

def solve_kepler(M: np.ndarray, e: float, tol: float = 1e-11, maxiter: int = 60) -> np.ndarray:
    """Solve Kepler's equation E - e sin E = M (vectorised Newton + bisection guard).

    M is the mean anomaly (radians, any range); returns eccentric anomaly E.
    Robust for 0 <= e < 1.  Starts from the Danby cubic seed for fast convergence.
    """
    M = np.atleast_1d(np.asarray(M, dtype=float))
    Mw = np.mod(M, 2.0 * math.pi)
    # Danby (1988) starting guess.
    E = Mw + 0.85 * e * np.sign(np.sin(Mw))
    for _ in range(maxiter):
        f = E - e * np.sin(E) - Mw
        fp = 1.0 - e * np.cos(E)
        dE = -f / fp
        # Damp huge steps (helps near e->1).
        dE = np.clip(dE, -1.0, 1.0)
        E = E + dE
        if np.max(np.abs(f)) < tol:
            break
    return E


def elliptical_xy(t: np.ndarray, P: float, e: float, T0: float):
    """Return (X, Y) = (cos E - e, sqrt(1-e^2) sin E) at times t (days)."""
    M = 2.0 * math.pi * (t - T0) / P
    E = solve_kepler(M, e)
    X = np.cos(E) - e
    Y = math.sqrt(max(0.0, 1.0 - e * e)) * np.sin(E)
    return X, Y


# ---------------------------------------------------------------------------
# Observation-equation design columns.
# ---------------------------------------------------------------------------

def _astrometric_columns(t, sin_psi, cos_psi, par_factor, t_ref):
    """The 5 standard astrometric AL design columns: [Δα*, Δδ, ϖ, μα*, μδ].

    Returns an (N,5) matrix; column j is ∂w/∂(param_j).
    """
    dt = (t - t_ref) / DAYS_PER_YEAR          # years -> μ in mas/yr
    return np.column_stack([
        sin_psi,                # Δα*  (mas)
        cos_psi,                # Δδ   (mas)
        par_factor,             # ϖ    (mas)  (par_factor is the AL parallax factor)
        dt * sin_psi,           # μα*  (mas/yr)
        dt * cos_psi,           # μδ   (mas/yr)
    ])


def _orbit_columns(t, sin_psi, cos_psi, P, e, T0):
    """AL design columns for the 4 Thiele-Innes coefficients [B, G, A, F].

    w_orb = (B X + G Y) sin psi + (A X + F Y) cos psi   [eqs (2),(5)]
    Column order is chosen so the returned coefficients map cleanly to A,B,F,G.
    Returns (N,4) in the order [A, B, F, G] to match how we unpack them.
    """
    X, Y = elliptical_xy(t, P, e, T0)
    col_A = X * cos_psi      # A multiplies X in Δδ
    col_B = X * sin_psi      # B multiplies X in Δα*
    col_F = Y * cos_psi      # F multiplies Y in Δδ
    col_G = Y * sin_psi      # G multiplies Y in Δα*
    return np.column_stack([col_A, col_B, col_F, col_G])


def _accel_columns(t, sin_psi, cos_psi, t_ref, order=1):
    """AL design columns for a barycentric acceleration (and optional jerk).

    order=1 -> [a_α*, a_δ]  (4 cols counting the (t^2/2) AL projection in α*,δ)
    order=2 -> additionally [j_α*, j_δ] cubic terms.
    Each physical acceleration component projects AL as 0.5 (t)^2 * (sin/cos psi).
    Returns (N, 2*order_terms) and the list of parameter names.
    """
    dt = (t - t_ref) / DAYS_PER_YEAR
    cols = [
        0.5 * dt ** 2 * sin_psi,    # accel in α*  (mas/yr^2)
        0.5 * dt ** 2 * cos_psi,    # accel in δ
    ]
    names = ['accel_ra', 'accel_dec']
    if order >= 2:
        cols += [
            (1.0 / 6.0) * dt ** 3 * sin_psi,   # jerk in α*  (mas/yr^3)
            (1.0 / 6.0) * dt ** 3 * cos_psi,   # jerk in δ
        ]
        names += ['jerk_ra', 'jerk_dec']
    return np.column_stack(cols), names


# ---------------------------------------------------------------------------
# Epoch-data container (the synthetic / DR4 per-transit table, post-adapter).
# ---------------------------------------------------------------------------

@dataclass
class EpochData:
    """Per-transit along-scan astrometry for one source (canonical internal form).

    t          : observation times (days; any zero-point, we use t_ref internally)
    w          : along-scan abscissa measurement (mas)
    psi        : scan angle (radians); AL direction
    par_factor : parallax factor projected onto AL (dimensionless)
    sigma      : per-transit AL uncertainty (mas)
    t_ref      : reference epoch (days) for proper motion / acceleration (defaults
                 to the mean of t).
    """
    t: np.ndarray
    w: np.ndarray
    psi: np.ndarray
    par_factor: np.ndarray
    sigma: np.ndarray
    t_ref: Optional[float] = None

    def __post_init__(self):
        self.t = np.asarray(self.t, float)
        self.w = np.asarray(self.w, float)
        self.psi = np.asarray(self.psi, float)
        self.par_factor = np.asarray(self.par_factor, float)
        self.sigma = np.asarray(self.sigma, float)
        if self.t_ref is None:
            self.t_ref = float(np.mean(self.t))

    @property
    def n(self) -> int:
        return self.t.size

    @property
    def sin_psi(self) -> np.ndarray:
        return np.sin(self.psi)

    @property
    def cos_psi(self) -> np.ndarray:
        return np.cos(self.psi)


# ---------------------------------------------------------------------------
# Fit result container.
# ---------------------------------------------------------------------------

@dataclass
class FitResult:
    model: str                       # '1body' | 'accel' | '2body'
    params: dict                     # named best-fit parameters
    a_phot: Optional[float]          # mas (inner orbit)
    incl_deg: Optional[float]
    P: Optional[float]
    e: Optional[float]
    T0: Optional[float]
    chi2: float
    ndata: int
    nparam: int
    dof: int
    chi2_red: float
    rms_mas: float                   # weighted residual RMS (mas)
    bic: float
    aic: float
    f2: float                        # Wilson-Hilferty "gaussianised" goodness-of-fit
    success: bool
    extra: dict = field(default_factory=dict)


def _gof_f2(chi2: float, dof: int) -> float:
    """Wilson–Hilferty F2 goodness-of-fit statistic (the Gaia 'F2'/GOF).

    F2 = sqrt(9 dof/2) * [ (chi2/dof)^(1/3) - 1 + 2/(9 dof) ].
    ~N(0,1) for a good fit; large positive => poor fit (the WDJ020915 F2=+8.39
    that the whole pre-registration hinges on is exactly this statistic).
    """
    if dof <= 0:
        return float('nan')
    x = chi2 / dof
    return math.sqrt(9.0 * dof / 2.0) * (x ** (1.0 / 3.0) - 1.0 + 2.0 / (9.0 * dof))


# ---------------------------------------------------------------------------
# Linear solve of the (astrometric [+ orbit] [+ accel]) part at fixed (P,e,T0).
# ---------------------------------------------------------------------------

def _build_design(ep: EpochData, period_blocks, accel_order=0):
    """Assemble the full AL design matrix for the linear coefficients.

    period_blocks : list of (P,e,T0) tuples; one orbit block (4 TI cols) each.
    accel_order   : 0 (none), 1 (accel), 2 (accel+jerk).
    Returns (design (N,K), column_names).
    """
    sinp, cosp = ep.sin_psi, ep.cos_psi
    blocks = [_astrometric_columns(ep.t, sinp, cosp, ep.par_factor, ep.t_ref)]
    names = ['dra', 'ddec', 'plx', 'pmra', 'pmdec']
    for k, (P, e, T0) in enumerate(period_blocks):
        blocks.append(_orbit_columns(ep.t, sinp, cosp, P, e, T0))
        # First orbit block is always A,B,F,G (no suffix) so _finalize can read
        # the inner orbit uniformly; outer blocks get 2,3,...
        suffix = '' if k == 0 else f'{k+1}'
        names += [f'A{suffix}', f'B{suffix}', f'F{suffix}', f'G{suffix}']
    if accel_order >= 1:
        acc, anames = _accel_columns(ep.t, sinp, cosp, ep.t_ref, order=accel_order)
        blocks.append(acc)
        names += anames
    return np.hstack(blocks), names


def _wls(design: np.ndarray, w: np.ndarray, sigma: np.ndarray):
    """Weighted linear least squares.  Returns (coef, resid, chi2)."""
    Wsqrt = 1.0 / sigma
    Aw = design * Wsqrt[:, None]
    bw = w * Wsqrt
    coef, *_ = np.linalg.lstsq(Aw, bw, rcond=None)
    model = design @ coef
    resid = w - model
    chi2 = float(np.sum((resid / sigma) ** 2))
    return coef, resid, chi2


def _finalize(ep, coef, names, chi2, model_label, period_params, accel_order):
    nparam = coef.size + len(period_params)   # linear coefs + nonlinear (P,e,T0) per block
    dof = ep.n - nparam
    chi2_red = chi2 / dof if dof > 0 else float('nan')
    # Weighted residual RMS.
    resid = ep.w - _design_from_params(ep, coef, names, period_params, accel_order)
    rms = float(np.sqrt(np.mean(resid ** 2)))
    # BIC / AIC with a Gaussian likelihood (chi2 = -2 ln L up to a constant).
    bic = chi2 + nparam * math.log(ep.n)
    aic = chi2 + 2.0 * nparam
    f2 = _gof_f2(chi2, dof)
    pdict = dict(zip(names, coef.tolist()))
    # Recover a_phot / i for the (first) inner orbit block if present.
    a_phot = incl = P = e = T0 = None
    if period_params:
        P, e, T0 = period_params[0]
        A, B, Fc, Gc = pdict['A'], pdict['B'], pdict['F'], pdict['G']
        geo = inclination_from_ABFG(A, B, Fc, Gc)
        a_phot, incl = geo['a'], geo['incl_deg']
        pdict.update({'P': P, 'e': e, 'T0': T0})
    if len(period_params) >= 2:
        P2, e2, T02 = period_params[1]
        A2, B2, F2c, G2c = pdict['A2'], pdict['B2'], pdict['F2'], pdict['G2']
        geo2 = inclination_from_ABFG(A2, B2, F2c, G2c)
        pdict.update({'P2': P2, 'e2': e2, 'T02': T02,
                      'a_phot2': geo2['a'], 'incl2_deg': geo2['incl_deg']})
    return FitResult(
        model=model_label, params=pdict, a_phot=a_phot, incl_deg=incl,
        P=P, e=e, T0=T0, chi2=chi2, ndata=ep.n, nparam=nparam, dof=dof,
        chi2_red=chi2_red, rms_mas=rms, bic=bic, aic=aic, f2=f2, success=True,
    )


def _design_from_params(ep, coef, names, period_params, accel_order):
    design, _ = _build_design(ep, period_params, accel_order=accel_order)
    return design @ coef


# ---------------------------------------------------------------------------
# Single-Keplerian (1-body) fit.
# ---------------------------------------------------------------------------

def fit_one_body(ep: EpochData, P0: float, e0: float = 0.1, T00: Optional[float] = None,
                 P_bounds=None, refine_grid=True) -> FitResult:
    """Fit 5 astrometric params + a single Keplerian to the AL abscissae.

    Strategy: the model is linear in (Δα*,Δδ,ϖ,μα*,μδ,A,B,F,G) at fixed
    (P,e,T0); we therefore optimise only the 3 non-linear orbit params with
    scipy.least_squares (TRF, an LM-class trust-region method), solving the
    13-column linear system in closed form inside the residual callback.  A
    coarse period pre-scan (refine_grid) gives a robust start.

    P0   : initial period guess (days; e.g. the DR3 NSS period).
    """
    if T00 is None:
        T00 = ep.t_ref
    if P_bounds is None:
        P_bounds = (0.5 * P0, 2.0 * P0)

    def chi2_at(theta):
        P, e, T0 = theta
        e = min(max(e, 0.0), 0.95)
        P = max(P, 1e-3)
        design, names = _build_design(ep, [(P, e, T0)], accel_order=0)
        _, resid, _ = _wls(design, ep.w, ep.sigma)
        return resid / ep.sigma

    # Optional coarse period scan to avoid local minima (cheap: linear solve).
    if refine_grid:
        Pgrid = np.linspace(P_bounds[0], P_bounds[1], 60)
        best = (np.inf, P0)
        for Pg in Pgrid:
            design, _ = _build_design(ep, [(Pg, e0, T00)], accel_order=0)
            _, _, c2 = _wls(design, ep.w, ep.sigma)
            if c2 < best[0]:
                best = (c2, Pg)
        P0 = best[1]

    theta0 = [P0, e0, T00]
    lb = [P_bounds[0], 0.0, T00 - P0]
    ub = [P_bounds[1], 0.95, T00 + P0]
    res = least_squares(chi2_at, theta0, bounds=(lb, ub), method='trf',
                        xtol=1e-12, ftol=1e-12, max_nfev=4000)
    P, e, T0 = res.x
    e = min(max(e, 0.0), 0.95)
    design, names = _build_design(ep, [(P, e, T0)], accel_order=0)
    coef, _, chi2 = _wls(design, ep.w, ep.sigma)
    out = _finalize(ep, coef, names, chi2, '1body', [(P, e, T0)], 0)
    out.success = bool(res.success)
    return out


# ---------------------------------------------------------------------------
# 1-body + acceleration (cheap multi-body / outer-body probe).
# ---------------------------------------------------------------------------

def fit_accel(ep: EpochData, P0: float, e0: float = 0.1, T00: Optional[float] = None,
              order: int = 1, P_bounds=None) -> FitResult:
    """Fit 5 astrometric + single Keplerian + acceleration (order=1) or
    acceleration+jerk (order=2).  A significant acceleration over the 1-body
    fit is the signature of a distant 2nd body (P_outer >> baseline)."""
    if T00 is None:
        T00 = ep.t_ref
    if P_bounds is None:
        P_bounds = (0.5 * P0, 2.0 * P0)

    def chi2_at(theta):
        P, e, T0 = theta
        e = min(max(e, 0.0), 0.95)
        P = max(P, 1e-3)
        design, _ = _build_design(ep, [(P, e, T0)], accel_order=order)
        _, resid, _ = _wls(design, ep.w, ep.sigma)
        return resid / ep.sigma

    theta0 = [P0, e0, T00]
    lb = [P_bounds[0], 0.0, T00 - P0]
    ub = [P_bounds[1], 0.95, T00 + P0]
    res = least_squares(chi2_at, theta0, bounds=(lb, ub), method='trf',
                        xtol=1e-12, ftol=1e-12, max_nfev=4000)
    P, e, T0 = res.x
    e = min(max(e, 0.0), 0.95)
    design, names = _build_design(ep, [(P, e, T0)], accel_order=order)
    coef, _, chi2 = _wls(design, ep.w, ep.sigma)
    label = 'accel' if order == 1 else 'accel2'
    out = _finalize(ep, coef, names, chi2, label, [(P, e, T0)], order)
    out.success = bool(res.success)
    # Report the acceleration magnitude + an SNR estimate (needed by modelselect).
    out.extra['accel_mag_mas_yr2'] = math.hypot(out.params.get('accel_ra', 0.0),
                                                 out.params.get('accel_dec', 0.0))
    return out


# ---------------------------------------------------------------------------
# Double-Keplerian (inner + outer) fit — the explicit hierarchical-triple model.
# ---------------------------------------------------------------------------

def fit_two_body(ep: EpochData, P1_0: float, P2_0: float, e1_0=0.1, e2_0=0.1,
                 T01_0: Optional[float] = None, T02_0: Optional[float] = None,
                 P1_bounds=None, P2_bounds=None) -> FitResult:
    """Fit 5 astrometric + inner Keplerian + outer Keplerian to the AL abscissae.

    6 non-linear params (P1,e1,T01,P2,e2,T02) optimised by least_squares; the
    10 linear coefficients (5 astrometric + A,B,F,G inner + A2,B2,F2,G2 outer)
    solved in closed form per evaluation.
    """
    if T01_0 is None:
        T01_0 = ep.t_ref
    if T02_0 is None:
        T02_0 = ep.t_ref
    if P1_bounds is None:
        P1_bounds = (0.5 * P1_0, 2.0 * P1_0)
    if P2_bounds is None:
        P2_bounds = (0.5 * P2_0, 3.0 * P2_0)

    def chi2_at(theta):
        P1, e1, T01, P2, e2, T02 = theta
        e1 = min(max(e1, 0.0), 0.95); e2 = min(max(e2, 0.0), 0.95)
        design, _ = _build_design(ep, [(P1, e1, T01), (P2, e2, T02)], accel_order=0)
        _, resid, _ = _wls(design, ep.w, ep.sigma)
        return resid / ep.sigma

    theta0 = [P1_0, e1_0, T01_0, P2_0, e2_0, T02_0]
    lb = [P1_bounds[0], 0.0, T01_0 - P1_0, P2_bounds[0], 0.0, T02_0 - P2_0]
    ub = [P1_bounds[1], 0.95, T01_0 + P1_0, P2_bounds[1], 0.95, T02_0 + P2_0]
    res = least_squares(chi2_at, theta0, bounds=(lb, ub), method='trf',
                        xtol=1e-12, ftol=1e-12, max_nfev=8000)
    P1, e1, T01, P2, e2, T02 = res.x
    e1 = min(max(e1, 0.0), 0.95); e2 = min(max(e2, 0.0), 0.95)
    design, names = _build_design(ep, [(P1, e1, T01), (P2, e2, T02)], accel_order=0)
    coef, _, chi2 = _wls(design, ep.w, ep.sigma)
    out = _finalize(ep, coef, names, chi2, '2body',
                    [(P1, e1, T01), (P2, e2, T02)], 0)
    out.success = bool(res.success)
    return out


# ---------------------------------------------------------------------------
# Forward model (used by synth.py and for residual diagnostics).
# ---------------------------------------------------------------------------

def forward_al(t, psi, par_factor, t_ref, astro5, orbit=None, orbit2=None,
               accel=None):
    """Predict along-scan abscissae from explicit parameters.

    astro5 : (dra, ddec, plx, pmra, pmdec)  [mas, mas, mas, mas/yr, mas/yr]
    orbit  : (A,B,F,G,P,e,T0) inner Keplerian (TI coefs in mas) or None
    orbit2 : (A,B,F,G,P,e,T0) outer Keplerian or None
    accel  : (accel_ra, accel_dec[, jerk_ra, jerk_dec]) in mas/yr^2(,^3) or None
    """
    t = np.asarray(t, float)
    sinp, cosp = np.sin(psi), np.cos(psi)
    dt = (t - t_ref) / DAYS_PER_YEAR
    dra, ddec, plx, pmra, pmdec = astro5
    w = (dra * sinp + ddec * cosp + plx * par_factor
         + pmra * dt * sinp + pmdec * dt * cosp)
    for orb in (orbit, orbit2):
        if orb is not None:
            A, B, Fc, Gc, P, e, T0 = orb
            X, Y = elliptical_xy(t, P, e, T0)
            dra_o = B * X + Gc * Y
            ddec_o = A * X + Fc * Y
            w = w + dra_o * sinp + ddec_o * cosp
    if accel is not None:
        ar, ad = accel[0], accel[1]
        w = w + 0.5 * dt ** 2 * (ar * sinp + ad * cosp)
        if len(accel) >= 4:
            jr, jd = accel[2], accel[3]
            w = w + (1.0 / 6.0) * dt ** 3 * (jr * sinp + jd * cosp)
    return w


def abfg_from_geometry(a_phot, incl_deg, omega_deg, Omega_deg):
    """Construct Thiele-Innes (A,B,F,G) from Campbell elements (for synth/tests).

    Standard Halbwachs+2023 definitions (a in mas):
      A = a (cos ω cos Ω - sin ω sin Ω cos i)
      B = a (cos ω sin Ω + sin ω cos Ω cos i)
      F = a (-sin ω cos Ω - cos ω sin Ω cos i)
      G = a (-sin ω sin Ω + cos ω cos Ω cos i)
    """
    i = math.radians(incl_deg)
    w = math.radians(omega_deg)
    O = math.radians(Omega_deg)
    ci = math.cos(i)
    A = a_phot * (math.cos(w) * math.cos(O) - math.sin(w) * math.sin(O) * ci)
    B = a_phot * (math.cos(w) * math.sin(O) + math.sin(w) * math.cos(O) * ci)
    F = a_phot * (-math.sin(w) * math.cos(O) - math.cos(w) * math.sin(O) * ci)
    G = a_phot * (-math.sin(w) * math.sin(O) + math.cos(w) * math.cos(O) * ci)
    return A, B, F, G
