"""End-to-end tests for the DR4 candidate re-fit engine (synthetic data).

Proves the pipeline runs on synthetic DR4-like epoch astrometry:
  1. cos-i relation has NO sqrt (the 2026-05-31 bugfix), by forward construction.
  2. a clean 1-body orbit is recovered (params + a 'single' model verdict).
  3. a 2-body (hierarchical-triple) signal is recovered AND modelselect picks
     'multi' (via an acceleration term and/or a 2nd Keplerian).
  4. the pre-registered decision wiring produces the right verdict on a
     synthetic "headline-true" WDJ020915 and a synthetic "triple" WDJ020915.
  5. UCAC4 313 inclination -> substellar/stellar decision flips with sin i.
  6. PREREG constants match the pre-registration document (no drift).

Run:
  /Users/legbatterij/claude_projects/ostinato/.venv/bin/python -m pytest test_refit.py -q
or simply:
  /Users/legbatterij/claude_projects/ostinato/.venv/bin/python test_refit.py   (runs all + prints)

These are tolerance-based scientific tests, not bit-exact; tolerances are loose
enough to be robust to the synthetic noise seed but tight enough to catch a real
regression in the forward model or fitter.
"""
from __future__ import annotations

import math
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from model import (abfg_from_geometry, inclination_from_ABFG, fit_one_body,
                   fit_two_body)
from modelselect import select_model, summarize
import synth
from synth import make_epoch_data
import prereg
from prereg import decide, PREREG, audit_against_doc

PREREG_DOC = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    '..', '..', '..', 'docs', 'dr4_preregistration_2026_06_01.md')


# ---------------------------------------------------------------------------
def test_cosi_has_no_sqrt():
    """Forward-construct (A,B,F,G) from known (a,i,ω,Ω); recover i exactly.

    The 2026-05-31 bug computed cos i = sqrt(|AG-BF|/a^2); the correct relation
    is cos i = |AG-BF|/a^2.  At i=46° the bug returned 33.5°.  Assert the
    corrected helper recovers i to <0.01°.
    """
    for i_true in (20.0, 46.0, 66.4, 77.1, 88.0):
        A, B, Fc, Gc = abfg_from_geometry(a_phot=5.0, incl_deg=i_true,
                                          omega_deg=37.0, Omega_deg=121.0)
        geo = inclination_from_ABFG(A, B, Fc, Gc)
        assert abs(geo['a'] - 5.0) < 1e-6, f'a_phot off: {geo["a"]}'
        assert abs(geo['incl_deg'] - i_true) < 1e-2, (
            f'inclination not recovered (sqrt bug regression?): '
            f'true={i_true} got={geo["incl_deg"]:.3f}')
    print('  [ok] cos-i relation has no sqrt; i recovered to <0.01°')


# ---------------------------------------------------------------------------
def test_one_body_recovery():
    """Inject a clean 1-body orbit; assert params recovered + verdict 'single'."""
    truth = dict(a_phot_mas=5.40, P_days=175.94, e=0.064, incl_deg=77.1,
                 parallax_mas=17.7, G=12.6)
    ep = make_epoch_data(pmra=12.0, pmdec=-8.0, omega_deg=40.0, Omega_deg=110.0,
                         n_transits=70, seed=11, **truth)
    sel = select_model(ep, P0=truth['P_days'], e0=0.05)
    one = sel.one_body
    # Parameter recovery.
    assert abs(one.P - truth['P_days']) / truth['P_days'] < 0.03, f'P={one.P}'
    assert abs(one.a_phot - truth['a_phot_mas']) / truth['a_phot_mas'] < 0.15, f'a_phot={one.a_phot}'
    assert abs(one.incl_deg - truth['incl_deg']) < 8.0, f'i={one.incl_deg}'
    assert one.e < 0.25, f'e={one.e}'
    # Goodness of fit: a clean 1-body should give chi2_red ~ 1 and F2 small.
    assert one.chi2_red < 1.6, f'chi2_red={one.chi2_red}'
    assert one.f2 < 3.0, f'F2={one.f2}'
    # Model selection should NOT prefer a multi-body model.
    assert sel.verdict in ('single', 'inconclusive'), f'verdict={sel.verdict}: {sel.reason}'
    print(f'  [ok] 1-body recovered: P={one.P:.2f} a_phot={one.a_phot:.3f} '
          f'i={one.incl_deg:.1f} F2={one.f2:+.2f} chi2r={one.chi2_red:.2f} -> {sel.verdict}')


# ---------------------------------------------------------------------------
def test_two_body_recovery():
    """Inject inner+outer (hierarchical triple); assert modelselect picks 'multi'.

    Inner: the WDJ020915-like 274-d orbit. Outer: a long (~3.6-yr) wobble with a
    comparable photocentric amplitude -> should be detected as a 2nd period
    and/or a significant acceleration.
    """
    ep = make_epoch_data(
        G=14.0, parallax_mas=12.0, pmra=6.0, pmdec=4.0,
        a_phot_mas=5.0, P_days=274.0, e=0.05, incl_deg=66.0,
        omega_deg=40.0, Omega_deg=110.0,
        # Outer body: long period, healthy amplitude.
        a_phot2_mas=4.0, P2_days=1300.0, e2=0.2, incl2_deg=55.0,
        omega2_deg=200.0, Omega2_deg=300.0,
        n_transits=85, seed=23)
    sel = select_model(ep, P0=274.0, e0=0.05, P2_guess=1300.0)
    assert sel.verdict == 'multi', (
        f'expected multi, got {sel.verdict}: {sel.reason}\n' + summarize(sel))
    # The 1-body fit of a true 2-body should be visibly poor.
    assert sel.one_body.chi2_red > 1.5 or sel.one_body.f2 > 3.0, (
        f'1-body fit too good for a true 2-body: chi2r={sel.one_body.chi2_red} F2={sel.one_body.f2}')
    print(f'  [ok] 2-body detected as MULTI: {sel.reason}')
    print('       ' + summarize(sel).replace('\n', '\n       '))


# ---------------------------------------------------------------------------
def test_two_body_explicit_outer_recovery():
    """The explicit double-Keplerian fit should recover BOTH periods reasonably."""
    P1, P2 = 250.0, 1400.0
    ep = make_epoch_data(
        G=13.5, parallax_mas=15.0, pmra=3.0, pmdec=-5.0,
        a_phot_mas=4.5, P_days=P1, e=0.1, incl_deg=70.0,
        a_phot2_mas=5.0, P2_days=P2, e2=0.15, incl2_deg=50.0,
        n_transits=90, seed=31)
    fit2 = fit_two_body(ep, P1_0=P1, P2_0=P2, e1_0=0.1, e2_0=0.1)
    Ps = sorted([fit2.params['P'], fit2.params['P2']])
    assert abs(Ps[0] - P1) / P1 < 0.08, f'inner P not recovered: {Ps}'
    assert abs(Ps[1] - P2) / P2 < 0.12, f'outer P not recovered: {Ps}'
    assert fit2.chi2_red < 1.6, f'2-body chi2_red={fit2.chi2_red}'
    print(f'  [ok] explicit 2-body recovered periods ~{Ps[0]:.0f} & {Ps[1]:.0f} d '
          f'(truth {P1:.0f}, {P2:.0f}); chi2r={fit2.chi2_red:.2f}')


# ---------------------------------------------------------------------------
def test_prereg_decision_headline_confirm():
    """Synthetic 'headline-true' WDJ020915: clean single 274-d orbit -> CONFIRM, M2>=1.2.

    NOTE on the knife-edge: the bare photocentric mass-function inversion at the
    pre-registered DR3 anchors (a_phot=7.73, M1=0.718, P=274.52) gives M2=1.223 —
    sitting *exactly* on the 1.2 M_sun NS floor, so even a perfect fit scatters
    ~15% of noise realisations below the floor (the doc's realistic M2=1.322 uses
    the full-TI-covariance MC, slightly above the bare inversion).  To exercise
    the CONFIRM *wiring* in the world the doc describes (M2≈1.3, a_phot a few %
    above the lower edge of its 3σ band 7.37–8.09), we inject a_phot=8.0
    (-> M2≈1.30, comfortably ≥1.2 AND within 3σ of 7.73).  The triple-REFUTE and
    boundary behaviour are tested separately."""
    t = dict(synth.CANDIDATE_TRUTH['332248057157474176'])
    t['a_phot_mas'] = 8.0      # M2≈1.30 (headline-true world); within 3σ of 7.73±0.12
    ep = make_epoch_data(pmra=20.0, pmdec=-15.0, omega_deg=50.0, Omega_deg=130.0,
                         n_transits=110, seed=42, **t)
    sel = select_model(ep, P0=t['P_days'], e0=0.05)
    dec = decide('332248057157474176', sel, parallax_mas=t['parallax_mas'])
    assert dec.verdict == 'CONFIRM', f'{dec.verdict}: {dec.detail}\n{summarize(sel)}'
    assert dec.M2_fit >= 1.2, f'M2={dec.M2_fit}'
    print(f'  [ok] WDJ020915 headline-true -> {dec.verdict}: M2={dec.M2_fit:.2f}, '
          f'F2={dec.f2_single:+.2f}, a_phot={dec.a_phot_fit:.2f}')
    print(f'       followup: {dec.followup}')


def test_prereg_decision_triple_refute():
    """Synthetic 'triple' WDJ020915: inner 274-d + an outer wobble -> the engine
    must REFUTE (2nd-period/accel detected -> hierarchical triple)."""
    ep = make_epoch_data(
        G=16.2, parallax_mas=11.9, pmra=20.0, pmdec=-15.0,
        a_phot_mas=6.0, P_days=274.52, e=0.05, incl_deg=65.8,
        a_phot2_mas=5.0, P2_days=1500.0, e2=0.2, incl2_deg=50.0,
        n_transits=85, seed=43)
    sel = select_model(ep, P0=274.52, e0=0.05, P2_guess=1500.0)
    dec = decide('332248057157474176', sel, parallax_mas=11.9)
    assert dec.verdict == 'REFUTE', f'{dec.verdict}: {dec.detail}\n{summarize(sel)}'
    assert dec.model_verdict == 'multi'
    print(f'  [ok] WDJ020915 triple -> {dec.verdict}: {dec.detail}')


# ---------------------------------------------------------------------------
def test_ucac4_inclination_flip():
    """UCAC4 313: edge-on -> substellar CONFIRM; near face-on -> stellar REFUTE.

    Build two synthetic orbits with the SAME mass function (so a_phot scales
    with sin i for fixed dynamical content). We instead hold a_phot at the DR3
    value and vary i; the decision logic computes M2 from (a_phot, i) and the
    M2 ∝ behaviour vs the sin-i thresholds drives the flip.
    """
    base = dict(parallax_mas=30.9, P_days=592.32, e=0.214, G=13.9)
    # High inclination (edge-on): substellar.
    ep_hi = make_epoch_data(a_phot_mas=1.32, incl_deg=80.0, omega_deg=30.0,
                            Omega_deg=120.0, pmra=120.0, pmdec=-200.0,
                            n_transits=80, seed=51, **base)
    sel_hi = select_model(ep_hi, P0=base['P_days'], e0=0.2)
    dec_hi = decide('5612039087715504640', sel_hi, parallax_mas=base['parallax_mas'])
    assert dec_hi.verdict == 'CONFIRM', f'edge-on: {dec_hi.verdict}: {dec_hi.detail}'

    # Low inclination (near face-on): the same a_phot at low i -> large M2.
    # To make M2 cross the H-burning limit we use a larger a_phot consistent with
    # a low-i / massive-secondary scenario (a_phot grows with M2 at fixed P,plx).
    ep_lo = make_epoch_data(a_phot_mas=3.5, incl_deg=18.0, omega_deg=30.0,
                            Omega_deg=120.0, pmra=120.0, pmdec=-200.0,
                            n_transits=80, seed=52, **base)
    sel_lo = select_model(ep_lo, P0=base['P_days'], e0=0.2)
    dec_lo = decide('5612039087715504640', sel_lo, parallax_mas=base['parallax_mas'])
    assert dec_lo.verdict == 'REFUTE', f'low-i: {dec_lo.verdict}: {dec_lo.detail}'
    print(f'  [ok] UCAC4 313 edge-on -> {dec_hi.verdict} '
          f'(i={dec_hi.incl_fit:.0f}°, M2={dec_hi.checks["M2_mjup"]:.0f} M_J); '
          f'low-i -> {dec_lo.verdict} (i={dec_lo.incl_fit:.0f}°, M2={dec_lo.M2_fit:.3f} M_sun)')


# ---------------------------------------------------------------------------
def test_prereg_matches_doc():
    """The hard-coded PREREG constants must match the pre-registration doc."""
    if not os.path.exists(PREREG_DOC):
        print(f'  [skip] doc not found at {PREREG_DOC}')
        return
    problems = audit_against_doc(PREREG_DOC)
    assert not problems, 'PREREG drifted from the doc:\n  ' + '\n  '.join(problems)
    print('  [ok] PREREG anchor constants match docs/dr4_preregistration_2026_06_01.md')


# ---------------------------------------------------------------------------
def _run_all():
    tests = [
        ('cos-i no-sqrt (bugfix guard)', test_cosi_has_no_sqrt),
        ('1-body recovery + single verdict', test_one_body_recovery),
        ('2-body detected as multi', test_two_body_recovery),
        ('explicit 2-body period recovery', test_two_body_explicit_outer_recovery),
        ('prereg WDJ020915 headline -> CONFIRM', test_prereg_decision_headline_confirm),
        ('prereg WDJ020915 triple -> REFUTE', test_prereg_decision_triple_refute),
        ('UCAC4 313 inclination flip', test_ucac4_inclination_flip),
        ('PREREG matches doc', test_prereg_matches_doc),
    ]
    fails = 0
    for name, fn in tests:
        print(f'- {name}')
        try:
            fn()
        except AssertionError as e:
            fails += 1
            print(f'  [FAIL] {e}')
        except Exception as e:               # noqa
            fails += 1
            import traceback
            print(f'  [ERROR] {e}')
            traceback.print_exc()
    print('\n' + ('ALL TESTS PASSED' if fails == 0 else f'{fails} TEST(S) FAILED'))
    return fails


if __name__ == '__main__':
    sys.exit(_run_all())
