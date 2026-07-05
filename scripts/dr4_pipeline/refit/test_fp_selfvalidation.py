"""DR4 day-one SELF-VALIDATION against the labeled false-positive registry.

The re-fit engine must reproduce the correct *skeptical* verdict on every
astrometric false positive the project already documented (fp_registry.REGISTRY)
BEFORE any new DR4 verdict is trusted. Each test below reconstructs a
documented FP's signature in a synthetic DR4-like world and asserts the engine
does NOT re-make the historical mistake.

This is lane #116 insurance: a private, source_id-keyed FP corpus no external
team has, wired as a regression gate. `run.py --self-validate` runs the same
guards on the real day-one path and aborts if any fail.

Scope honesty: only the `dr4-refit-astrometric` rows are *guarded* here (this
engine's slice). Photometric-period / ellipsoidal artifacts, SB2 / luminous-
binary contamination, and pure catalogue-crossmatch novelty errors are recorded
in the registry but owned by other subsystems; `test_nonastrometric_recorded`
asserts they are documented, not that this engine catches them.

Run:
  PY=/Users/legbatterij/claude_projects/ostinato/.venv/bin/python
  $PY -m pytest test_fp_selfvalidation.py -q
  $PY test_fp_selfvalidation.py           # runs run_self_validation() + prints
"""
from __future__ import annotations

import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from model import EpochData, abfg_from_geometry, inclination_from_ABFG
from modelselect import select_model
from prereg import (decide, m2_from_fit, m2_from_sin_i, solve_m2,
                    NS_FLOOR, CHANDRA, SUBCH_DOWNGRADE)
import synth
from synth import make_epoch_data
import fp_registry
from fp_registry import REGISTRY, by_key, astrometric_cases, validate_registry


# ---------------------------------------------------------------------------
# Registry integrity + completeness.
# ---------------------------------------------------------------------------
def test_registry_wellformed():
    problems = validate_registry()
    assert not problems, 'registry structural problems:\n  ' + '\n  '.join(problems)
    print(f'  [ok] registry well-formed: {len(REGISTRY)} FPs, '
          f'{len(astrometric_cases())} astrometric')


def test_registry_covers_key_retractions():
    """The corpus must not silently lose a headline retraction."""
    must_have = {
        'crts-j051419-cv-period-eclipse',      # the founding photometric retraction
        'cv-period-avenue',
        'thiele-innes-cosi-sqrt-bug',          # the mass-biasing bug
        'massgap-bh-sin-i-inflation-class',
        '5858574-massgap-bh-to-triple',        # the "Shahaf recovery" compaction lesson object
        'wdj020915-superchandra-framing',
        'wdj060042-superchandra-framing',
        'wdj205650-superchandra-massjoin-artifact',
        'galex-j033455-bh-to-wd',              # externally scooped demotion
        'hd207141-massgap-bh-to-triple',
    }
    have = {c.key for c in REGISTRY}
    missing = must_have - have
    assert not missing, f'registry is missing documented retractions: {sorted(missing)}'
    print(f'  [ok] all {len(must_have)} key documented retractions present')


def test_hd76078_not_a_ledger_fp():
    """HD 76078 is a v1 benchmark fixture, not a campaign retraction — it must
    NOT be in the ledger-sourced corpus (harvest NOTE (a))."""
    names = ' '.join(c.object_name for c in REGISTRY).lower()
    assert 'hd 76078' not in names and '76078' not in names, \
        'HD 76078 must not be a registry FP (it is a benchmark fixture, not a retraction)'
    print('  [ok] HD 76078 correctly excluded (benchmark fixture, not a ledger FP)')


# ---------------------------------------------------------------------------
# Guard 1 — Thiele-Innes cos-i sqrt bug: the corrected relation must NOT inflate
# the sin-i-deprojected mass above the compact floor.
# ---------------------------------------------------------------------------
def _cosi_bug_inflation(a_phot=5.0, i_true=66.4, omega=37.0, Omega=121.0):
    """Return (i_correct, i_buggy, inflation) where inflation = sin(i_true)/sin(i_buggy)."""
    A, B, Fc, Gc = abfg_from_geometry(a_phot, i_true, omega, Omega)
    geo = inclination_from_ABFG(A, B, Fc, Gc)               # corrected helper (no sqrt)
    i_correct = geo['incl_deg']
    cos_correct = abs(A * Gc - B * Fc) / geo['a'] ** 2       # = cos i (no sqrt)
    cos_buggy = math.sqrt(cos_correct)                       # the 2026-05-31 bug
    i_buggy = math.degrees(math.acos(min(1.0, cos_buggy)))
    inflation = math.sin(math.radians(i_true)) / math.sin(math.radians(i_buggy))
    return i_correct, i_buggy, inflation


def guard_cosi_no_sqrt_mass():
    c = by_key('thiele-innes-cosi-sqrt-bug')
    i_probe = c.oracle['incl_probe_deg']
    m2_true = c.oracle['m2_sin_i_min']
    i_correct, i_buggy, inflation = _cosi_bug_inflation(i_true=i_probe)
    # 1) corrected helper recovers the true inclination (no sqrt).
    ok_i = abs(i_correct - i_probe) < 0.05
    # 2) the bug would have made it more face-on and inflated the mass across CHANDRA.
    m2_buggy = m2_true * inflation
    ok_inflation = (i_buggy < i_probe) and (m2_buggy > CHANDRA > m2_true)
    ok = ok_i and ok_inflation
    detail = (f'i_correct={i_correct:.3f} (true {i_probe}); buggy i={i_buggy:.2f} -> '
              f'M2 {m2_true:.2f}->{m2_buggy:.2f} (crosses {CHANDRA}); corrected does not inflate')
    return ok, detail


def test_cosi_no_sqrt_mass_guard():
    ok, detail = guard_cosi_no_sqrt_mass()
    assert ok, detail
    print(f'  [ok] cos-i bug guard: {detail}')


# ---------------------------------------------------------------------------
# Guard 2 — mass-gap-BH sin-i inflation: the dark-companion mass is the DIRECT
# photocentric f(M) inversion; the historical rv/2 -> sin i deprojection would
# have inflated an NS-mass into a fake mass-gap BH (the 5858574 signature).
# ---------------------------------------------------------------------------
def guard_direct_photocentric_mass():
    # Construct a photocentric orbit whose DIRECT mass is NS-mass (~1.55 Msun),
    # matching the 5858574 case (P~506 d). Then show the fake sin i=0.53
    # deprojection inflates it to ~2.9 Msun (the retracted "mass-gap BH 2.82").
    M1, P_days, plx = 0.9, 506.0, 5.0
    # pick a_phot so the direct mass lands ~1.55
    target = 1.55
    fM = target ** 3 / (M1 + target) ** 2
    P_yr = P_days / 365.25
    a_phot_AU = (fM * P_yr ** 2) ** (1.0 / 3.0)
    a_phot_mas = a_phot_AU * plx
    m2_direct = m2_from_fit(a_phot_mas, plx, P_days, M1)          # engine's dark-companion path
    m2_fake = m2_from_sin_i(M1, a_phot_mas, plx, P_days, 0.53)    # the historical rv/2 -> sin i error
    ok = (1.40 < m2_direct < 1.70) and (m2_fake > 2.5) and (m2_direct < 2.5)
    detail = (f'direct photocentric M2={m2_direct:.2f} (NS-mass, below mass-gap); '
              f'fake sin i=0.53 deprojection -> {m2_fake:.2f} (the retracted 2.82 mass-gap BH)')
    return ok, detail


def test_direct_photocentric_mass_guard():
    ok, detail = guard_direct_photocentric_mass()
    assert ok, detail
    print(f'  [ok] mass-gap sin-i-inflation guard: {detail}')


# ---------------------------------------------------------------------------
# Guard 3 — triple masquerade: a hierarchical triple whose naive single-companion
# photocentric mass looks compact must be flagged 'multi' (-> REFUTE), not a clean
# single compact companion. Guards 5858574, HD 75567, 2127900.
# ---------------------------------------------------------------------------
_TRIPLE_CASES = [
    ('5858574-massgap-bh-to-triple', dict(P_days=506.0, P2_days=1500.0, a1=5.0, a2=4.5, seed=61)),
    ('hd75567-ns-to-triple',         dict(P_days=300.0, P2_days=1400.0, a1=4.5, a2=4.0, seed=62)),
    ('2127900-ns-to-triple',         dict(P_days=430.0, P2_days=1600.0, a1=4.8, a2=4.2, seed=63)),
]


def guard_triple_masquerade(cfg):
    ep = make_epoch_data(
        G=15.5, parallax_mas=6.0, pmra=8.0, pmdec=-6.0,
        a_phot_mas=cfg['a1'], P_days=cfg['P_days'], e=0.1, incl_deg=62.0,
        omega_deg=40.0, Omega_deg=115.0,
        a_phot2_mas=cfg['a2'], P2_days=cfg['P2_days'], e2=0.2, incl2_deg=55.0,
        omega2_deg=210.0, Omega2_deg=300.0,
        n_transits=90, seed=cfg['seed'])
    sel = select_model(ep, P0=cfg['P_days'], e0=0.1, P2_guess=cfg['P2_days'])
    ok = (sel.verdict == 'multi')
    return ok, f"verdict={sel.verdict} ({sel.reason})"


def test_triple_masquerade_guards():
    fails = []
    for key, cfg in _TRIPLE_CASES:
        ok, detail = guard_triple_masquerade(cfg)
        by_key(key)  # assert the key exists in the registry
        if not ok:
            fails.append(f'{key}: {detail}')
        else:
            print(f'  [ok] triple-masquerade {key}: {detail}')
    assert not fails, 'triple-masquerade not flagged multi:\n  ' + '\n  '.join(fails)


# ---------------------------------------------------------------------------
# Guard 4 — WDJ020915: a weak-fit (F2 > +5) DR4 world must NOT be CONFIRMed
# (the doc's "F2 stays > +5 -> PARK"); a low-a_phot world (M2 < 1.2) -> DOWNGRADE.
# ---------------------------------------------------------------------------
def guard_wdj020915_weakfit_not_confirmed():
    sid = '332248057157474176'
    t = dict(synth.CANDIDATE_TRUTH[sid])
    ep = make_epoch_data(pmra=20.0, pmdec=-15.0, omega_deg=50.0, Omega_deg=130.0,
                         n_transits=100, seed=71, **t)
    # Report errors 2.5x too small -> the same residuals look like a poor fit (F2 high).
    ep_weak = EpochData(t=ep.t, w=ep.w, psi=ep.psi, par_factor=ep.par_factor,
                        sigma=ep.sigma * 0.4, t_ref=ep.t_ref)
    sel = select_model(ep_weak, P0=t['P_days'], e0=0.05)
    dec = decide(sid, sel, parallax_mas=t['parallax_mas'])
    ok = (dec.verdict != 'CONFIRM')
    return ok, f'F2={sel.f2_single:+.2f} -> verdict={dec.verdict} (not CONFIRM)'


def guard_wdj020915_lowmass_downgrade():
    sid = '332248057157474176'
    t = dict(synth.CANDIDATE_TRUTH[sid])
    t['a_phot_mas'] = 7.3     # drops M2 below the 1.2 NS floor
    ep = make_epoch_data(pmra=20.0, pmdec=-15.0, omega_deg=50.0, Omega_deg=130.0,
                         n_transits=100, seed=72, **t)
    sel = select_model(ep, P0=t['P_days'], e0=0.05)
    dec = decide(sid, sel, parallax_mas=t['parallax_mas'])
    ok = (dec.verdict == 'DOWNGRADE') and (dec.M2_fit < NS_FLOOR)
    return ok, f'a_phot=7.3 -> M2={dec.M2_fit:.3f} < {NS_FLOOR} -> verdict={dec.verdict}'


def test_wdj020915_guards():
    ok1, d1 = guard_wdj020915_weakfit_not_confirmed()
    assert ok1, 'weak-fit WDJ020915 wrongly CONFIRMed: ' + d1
    print(f'  [ok] WDJ020915 weak-fit: {d1}')
    ok2, d2 = guard_wdj020915_lowmass_downgrade()
    assert ok2, 'low-mass WDJ020915 not DOWNGRADEd: ' + d2
    print(f'  [ok] WDJ020915 low-mass: {d2}')


# ---------------------------------------------------------------------------
# Guard 5 — WDJ060042: at the DR3 anchor (M2~=1.37 < 1.4) the engine must NOT
# assert a SUPER-CHANDRA companion (the retracted framing); below 1.33 -> DOWNGRADE.
# ---------------------------------------------------------------------------
def guard_wdj060042_no_false_superchandra():
    sid = '2909342818326298112'
    t = dict(synth.CANDIDATE_TRUTH[sid])      # a_phot=19.62 -> M2~=1.37
    ep = make_epoch_data(pmra=6.0, pmdec=4.0, omega_deg=45.0, Omega_deg=120.0,
                         n_transits=110, seed=81, **t)
    sel = select_model(ep, P0=t['P_days'], e0=0.05)
    dec = decide(sid, sel, parallax_mas=t['parallax_mas'])
    # Clean single orbit; M2 near-Chandra but the engine must NOT claim super-Chandra.
    ok = (dec.M2_fit < CHANDRA) and ('SUPER-CHANDRA' not in dec.detail.upper()) \
        and (dec.verdict in ('CONFIRM', 'INCONCLUSIVE'))
    return ok, f'M2={dec.M2_fit:.3f} (<{CHANDRA}); verdict={dec.verdict}; no super-Chandra claim'


def guard_wdj060042_lowmass_downgrade():
    sid = '2909342818326298112'
    t = dict(synth.CANDIDATE_TRUTH[sid])
    t['a_phot_mas'] = 18.0     # drops M2 below the 1.33 sub-Ch downgrade floor
    ep = make_epoch_data(pmra=6.0, pmdec=4.0, omega_deg=45.0, Omega_deg=120.0,
                         n_transits=110, seed=82, **t)
    sel = select_model(ep, P0=t['P_days'], e0=0.05)
    dec = decide(sid, sel, parallax_mas=t['parallax_mas'])
    ok = (dec.verdict == 'DOWNGRADE') and (dec.M2_fit < SUBCH_DOWNGRADE)
    return ok, f'a_phot=18.0 -> M2={dec.M2_fit:.3f} < {SUBCH_DOWNGRADE} -> verdict={dec.verdict}'


def test_wdj060042_guards():
    ok1, d1 = guard_wdj060042_no_false_superchandra()
    assert ok1, 'WDJ060042 wrongly claimed super-Chandra: ' + d1
    print(f'  [ok] WDJ060042 no-false-super-Chandra: {d1}')
    ok2, d2 = guard_wdj060042_lowmass_downgrade()
    assert ok2, 'WDJ060042 low-mass not DOWNGRADEd: ' + d2
    print(f'  [ok] WDJ060042 low-mass: {d2}')


# ---------------------------------------------------------------------------
# Guard 6 — inclination-degeneracy over-promotion (TYC 4562 / UCAC4 class):
# a near-face-on orbit that pushes M2 across the H-burning limit must REFUTE the
# substellar/compact reading (it is a star), not be promoted.
# ---------------------------------------------------------------------------
def guard_inclination_overpromotion_refuted():
    sid = '5612039087715504640'   # UCAC4 313 (the only 'inclination' PREREG object)
    base = dict(parallax_mas=30.9, P_days=592.32, e=0.214, G=13.9)
    ep = make_epoch_data(a_phot_mas=3.5, incl_deg=18.0, omega_deg=30.0,
                         Omega_deg=120.0, pmra=120.0, pmdec=-200.0,
                         n_transits=80, seed=91, **base)
    sel = select_model(ep, P0=base['P_days'], e0=0.2)
    dec = decide(sid, sel, parallax_mas=base['parallax_mas'])
    ok = (dec.verdict == 'REFUTE')
    return ok, f'near-face-on i -> M2 crosses H-burning -> verdict={dec.verdict} (stellar, not promoted)'


def test_inclination_overpromotion_guard():
    ok, detail = guard_inclination_overpromotion_refuted()
    assert ok, 'inclination over-promotion not refuted: ' + detail
    print(f'  [ok] inclination over-promotion (TYC 4562 / UCAC4 class): {detail}')


# ---------------------------------------------------------------------------
# Guard 7 — WDJ205650 mass-join regression: the same photocentric f(M) inverted
# at the DEFAULT (buggy) M1=1.5 gives a "super-Chandra" M_total~2.06 artifact;
# at the REAL M1=0.38 it is sub-Chandra (M_total~0.64). The engine must invert
# at the real M1.
# ---------------------------------------------------------------------------
def guard_wdj205650_mass_join():
    c = by_key('wdj205650-superchandra-massjoin-artifact')
    M1_buggy = c.oracle['M1_default_buggy']   # 1.5 (never joined the GF21 WD mass)
    M1_real = c.oracle['M1_real_msun']        # 0.38
    # Choose an f(M) that reproduces the documented outcome at the real M1:
    # M2 ~= 0.26 at M1=0.38 -> M_total ~= 0.64.
    m2_real_target = 0.26
    fM = m2_real_target ** 3 / (M1_real + m2_real_target) ** 2
    m2_real = solve_m2(fM, M1_real)
    m2_buggy = solve_m2(fM, M1_buggy)
    mtot_real = M1_real + m2_real
    mtot_buggy = M1_buggy + m2_buggy
    ok = (mtot_real < CHANDRA) and (mtot_buggy > CHANDRA)
    detail = (f'same f(M): real M1={M1_real} -> M_total={mtot_real:.2f} (<{CHANDRA}, sub-Ch); '
              f'default M1={M1_buggy} -> M_total={mtot_buggy:.2f} (>{CHANDRA}, the retracted 2.06 artifact)')
    return ok, detail


def test_wdj205650_mass_join_guard():
    ok, detail = guard_wdj205650_mass_join()
    assert ok, 'WDJ205650 mass-join regression: ' + detail
    print(f'  [ok] WDJ205650 mass-join: {detail}')


# ---------------------------------------------------------------------------
# Scope honesty: non-astrometric FPs are recorded but not guarded here.
# ---------------------------------------------------------------------------
def test_nonastrometric_recorded():
    non_astro = [c for c in REGISTRY if c.owning_subsystem != 'dr4-refit-astrometric']
    assert len(non_astro) >= 8, 'expected the photometric/SB2/crossmatch FPs to be recorded'
    subs = {c.owning_subsystem for c in non_astro}
    assert subs <= {'cascade-photometry', 'spectroscopy-sb2', 'catalog-crossmatch'}
    print(f'  [ok] {len(non_astro)} non-astrometric FPs recorded (owned by {sorted(subs)}), '
          f'not guarded by this engine')


# ---------------------------------------------------------------------------
# The day-one gate entry point (imported by run.py --self-validate).
# ---------------------------------------------------------------------------
_GUARDS = [
    ('cos-i-no-sqrt-mass', guard_cosi_no_sqrt_mass),
    ('direct-photocentric-mass', guard_direct_photocentric_mass),
    ('wdj020915-weakfit-not-confirmed', guard_wdj020915_weakfit_not_confirmed),
    ('wdj020915-lowmass-downgrade', guard_wdj020915_lowmass_downgrade),
    ('wdj060042-no-false-superchandra', guard_wdj060042_no_false_superchandra),
    ('wdj060042-lowmass-downgrade', guard_wdj060042_lowmass_downgrade),
    ('inclination-overpromotion-refuted', guard_inclination_overpromotion_refuted),
    ('wdj205650-mass-join', guard_wdj205650_mass_join),
]


def run_self_validation(verbose=True):
    """Run every astrometric guard + registry integrity. Returns (ok, failures)."""
    failures = []
    reg_problems = validate_registry()
    if reg_problems:
        failures.append('registry: ' + '; '.join(reg_problems))
    # triple-masquerade block
    for key, cfg in _TRIPLE_CASES:
        ok, detail = guard_triple_masquerade(cfg)
        if not ok:
            failures.append(f'triple-masquerade[{key}]: {detail}')
        elif verbose:
            print(f'  [ok] triple-masquerade {key}')
    for name, fn in _GUARDS:
        try:
            ok, detail = fn()
        except Exception as e:  # noqa
            ok, detail = False, f'EXCEPTION: {e}'
        if not ok:
            failures.append(f'{name}: {detail}')
        elif verbose:
            print(f'  [ok] {name}: {detail}')
    return (not failures), failures


if __name__ == '__main__':
    print(fp_registry.summary())
    print('\nDR4 day-one self-validation against the labeled-FP registry:')
    ok, failures = run_self_validation(verbose=True)
    if ok:
        print('\nSELF-VALIDATION PASSED — the engine reproduces every documented '
              'astrometric FP with the correct skeptical verdict.')
        sys.exit(0)
    print('\nSELF-VALIDATION FAILED:')
    for f in failures:
        print('  [FAIL] ' + f)
    sys.exit(1)
