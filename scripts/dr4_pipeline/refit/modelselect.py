"""Model selection: 1-body vs multi-body (acceleration / 2nd Keplerian).

Given the fits from model.py, decide whether the DR4 epoch astrometry of a
candidate is consistent with a SINGLE Keplerian photocentric orbit, or whether
a second body (a hierarchical triple / 2nd companion) is required.  This is the
'is there a 2nd period or acceleration?' test that the pre-registration hangs
the confirm/refute verdicts on (esp. WDJ020915 and WG 26).

Statistics computed (all standard):
  * ΔBIC = BIC(simple) - BIC(complex).  ΔBIC > +10 strongly favours the COMPLEX
    model (Kass & Raftery 1995); < -10 strongly favours simple; |ΔBIC|<2 weak.
  * ΔAIC, analogous (lighter penalty).
  * F-test on the chi2 drop for nested models (1body -> accel, 1body -> 2body):
    F = ((chi2_s - chi2_c)/(p_c - p_s)) / (chi2_c / dof_c); p-value from the
    F-distribution survival function.
  * The Gaia-style F2 goodness-of-fit of the SIMPLE (1-body) model — the
    pre-registered quantity (F2<=+2 clean / >+5 unreliable).
  * The acceleration SNR (its magnitude / a bootstrap-free linear-error proxy).

The verdict is one of {single, multi, inconclusive} with a short reason; the
caller (prereg.py) maps it onto each candidate's pre-registered thresholds.

stdlib + numpy + scipy only.
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Optional

import numpy as np
from scipy import stats

from model import EpochData, FitResult, fit_one_body, fit_accel, fit_two_body


# Decision constants (generic statistical thresholds; the *candidate-specific*
# thresholds live in prereg.py).
DBIC_STRONG = 10.0      # |ΔBIC| above this = strong preference
DBIC_WEAK = 2.0         # below this = inconclusive
FTEST_ALPHA = 1e-3      # p-value below this = significant added structure
ACCEL_SNR_SIGNIF = 5.0  # accel SNR above this = significant (pre-reg uses 5σ)


@dataclass
class SelectionResult:
    verdict: str                       # 'single' | 'multi' | 'inconclusive'
    reason: str
    one_body: FitResult
    accel: Optional[FitResult]
    two_body: Optional[FitResult]
    dbic_accel: Optional[float]        # BIC(1body) - BIC(accel)  (>0 favours accel)
    dbic_two: Optional[float]          # BIC(1body) - BIC(2body)
    ftest_accel_p: Optional[float]
    ftest_two_p: Optional[float]
    accel_snr: Optional[float]
    f2_single: float                   # F2 of the 1-body fit (the pre-reg quantity)
    stats: dict = field(default_factory=dict)


def _ftest(chi2_s, dof_s, chi2_c, dof_c):
    """Nested-model F-test.  s=simple (more dof), c=complex (fewer dof).

    Returns (F, p_value).  p small => the complex model's chi2 drop is
    significant (extra parameters justified).
    """
    dp = dof_s - dof_c            # number of extra parameters
    if dp <= 0 or dof_c <= 0 or chi2_c <= 0:
        return float('nan'), float('nan')
    F = ((chi2_s - chi2_c) / dp) / (chi2_c / dof_c)
    if F <= 0:
        return F, 1.0
    p = stats.f.sf(F, dp, dof_c)
    return F, p


def _accel_snr(accel_fit: FitResult, ep: EpochData) -> float:
    """Estimate the SNR of the acceleration vector via a linear error propagation.

    Re-build the design at the best-fit (P,e,T0) including the accel columns,
    compute the linear covariance (A^T W A)^-1, and form
    SNR = |accel| / sigma(|accel|) using the 2x2 sub-covariance of (a_ra,a_dec).
    """
    from model import _build_design, DAYS_PER_YEAR  # local import to avoid cycle
    order = 2 if accel_fit.model == 'accel2' else 1
    P = accel_fit.params['P']; e = accel_fit.params['e']; T0 = accel_fit.params['T0']
    design, names = _build_design(ep, [(P, e, T0)], accel_order=order)
    Wsqrt = 1.0 / ep.sigma
    Aw = design * Wsqrt[:, None]
    cov = np.linalg.pinv(Aw.T @ Aw)
    ira = names.index('accel_ra'); ide = names.index('accel_dec')
    ar = accel_fit.params['accel_ra']; ad = accel_fit.params['accel_dec']
    mag = math.hypot(ar, ad)
    if mag == 0:
        return 0.0
    # Variance of the magnitude by the delta method.
    grad = np.array([ar / mag, ad / mag])
    sub = np.array([[cov[ira, ira], cov[ira, ide]],
                    [cov[ide, ira], cov[ide, ide]]])
    var_mag = float(grad @ sub @ grad)
    if var_mag <= 0:
        return float('inf')
    return mag / math.sqrt(var_mag)


def select_model(
    ep: EpochData,
    P0: float,
    e0: float = 0.1,
    T00: Optional[float] = None,
    P2_guess: Optional[float] = None,
    try_two_body: bool = True,
) -> SelectionResult:
    """Fit 1-body, 1-body+accel, and (optionally) 2-body; return a verdict.

    P0       : period guess for the inner orbit (e.g. the DR3 NSS period).
    P2_guess : outer-period guess for the 2-body fit; defaults to ~3.5x the
               baseline-limited estimate (a long outer period).
    """
    one = fit_one_body(ep, P0=P0, e0=e0, T00=T00)
    acc = fit_accel(ep, P0=P0, e0=e0, T00=T00, order=1)

    two = None
    if try_two_body:
        if P2_guess is None:
            # Default outer guess: a few x the inner period or ~the baseline,
            # whichever is larger (a genuinely *outer* orbit).
            span = float(ep.t.max() - ep.t.min())
            P2_guess = max(3.0 * P0, 0.8 * span)
        try:
            two = fit_two_body(ep, P1_0=one.P or P0, P2_0=P2_guess, e1_0=one.e or e0)
        except Exception as exc:           # numerically fragile; degrade gracefully
            two = None

    dbic_accel = one.bic - acc.bic if acc else None
    dbic_two = one.bic - two.bic if two else None
    fA, pA = _ftest(one.chi2, one.dof, acc.chi2, acc.dof) if acc else (None, None)
    fT, pT = _ftest(one.chi2, one.dof, two.chi2, two.dof) if two else (None, None)
    snr = _accel_snr(acc, ep) if acc else None

    f2_single = one.f2

    # ---- Verdict logic -----------------------------------------------------
    # MULTI if either complex model is strongly preferred by BIC AND the nested
    # F-test is significant AND (for accel) the accel SNR clears the pre-reg 5σ.
    multi_evidence = []
    if dbic_accel is not None and dbic_accel > DBIC_STRONG and pA is not None and pA < FTEST_ALPHA:
        if snr is not None and snr >= ACCEL_SNR_SIGNIF:
            multi_evidence.append(f'acceleration (ΔBIC={dbic_accel:.1f}, F-test p={pA:.1e}, SNR={snr:.1f}σ)')
    if dbic_two is not None and dbic_two > DBIC_STRONG and pT is not None and pT < FTEST_ALPHA:
        # Guard against the outer Keplerian merely re-fitting noise: require the
        # outer a_phot to be a real fraction of the inner (not microscopic).
        a2 = two.params.get('a_phot2', 0.0) if two else 0.0
        a1 = two.params.get('a_phot', 0.0) if two else 0.0
        if a1 > 0 and a2 / a1 > 0.05:
            multi_evidence.append(f'2nd Keplerian P2={two.params.get("P2"):.0f}d, '
                                  f'a_phot2/a_phot1={a2/a1:.2f} (ΔBIC={dbic_two:.1f}, F-test p={pT:.1e})')

    if multi_evidence:
        verdict = 'multi'
        reason = 'multi-body required: ' + '; '.join(multi_evidence)
    else:
        # SINGLE if the 1-body fit is statistically adequate (BIC does not favour
        # complex models AND the 1-body chi2_red / F2 are acceptable).
        complex_pref = ((dbic_accel is not None and dbic_accel > DBIC_WEAK) or
                        (dbic_two is not None and dbic_two > DBIC_WEAK))
        if not complex_pref:
            verdict = 'single'
            reason = (f'single Keplerian adequate (F2={f2_single:+.2f}, '
                      f'chi2_red={one.chi2_red:.2f}; no complex model preferred by BIC)')
        else:
            verdict = 'inconclusive'
            reason = (f'weak preference for added structure but below decision '
                      f'thresholds (ΔBIC_accel={dbic_accel}, ΔBIC_2body={dbic_two}, '
                      f'accel SNR={snr})')

    return SelectionResult(
        verdict=verdict, reason=reason, one_body=one, accel=acc, two_body=two,
        dbic_accel=dbic_accel, dbic_two=dbic_two, ftest_accel_p=pA, ftest_two_p=pT,
        accel_snr=snr, f2_single=f2_single,
        stats=dict(
            chi2_red_1body=one.chi2_red, rms_1body=one.rms_mas,
            a_phot_1body=one.a_phot, incl_1body=one.incl_deg, P_1body=one.P, e_1body=one.e,
        ),
    )


def summarize(sel: SelectionResult) -> str:
    """Human-readable one-block summary of a selection result."""
    L = []
    L.append(f"VERDICT: {sel.verdict.upper()}  — {sel.reason}")
    o = sel.one_body
    L.append(f"  1-body: F2={o.f2:+.2f}  chi2_red={o.chi2_red:.3f}  "
             f"a_phot={o.a_phot:.3f} mas  i={o.incl_deg:.1f}°  P={o.P:.2f} d  e={o.e:.3f}  "
             f"RMS={o.rms_mas:.3f} mas  (BIC={o.bic:.1f}, {o.nparam} par, {o.ndata} obs)")
    if sel.accel:
        a = sel.accel
        L.append(f"  +accel: chi2_red={a.chi2_red:.3f}  ΔBIC(1body-accel)={sel.dbic_accel:+.1f}  "
                 f"F-test p={sel.ftest_accel_p:.2e}  accelSNR={sel.accel_snr:.2f}σ  "
                 f"|accel|={a.extra.get('accel_mag_mas_yr2', float('nan')):.4f} mas/yr²")
    if sel.two_body:
        t = sel.two_body
        L.append(f"  2-body: chi2_red={t.chi2_red:.3f}  ΔBIC(1body-2body)={sel.dbic_two:+.1f}  "
                 f"F-test p={sel.ftest_two_p:.2e}  P2={t.params.get('P2'):.1f} d  "
                 f"a_phot2={t.params.get('a_phot2'):.3f} mas")
    return '\n'.join(L)
