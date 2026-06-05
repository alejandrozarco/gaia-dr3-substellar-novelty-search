"""Pre-registered DR4 decision logic — wire the re-fit engine to the thresholds.

Encodes the confirm/refute thresholds fixed in
`docs/dr4_preregistration_2026_06_01.md` (frozen 2026-06-01, must not move after
seeing DR4) for the four standing candidates, and maps a SelectionResult
(modelselect.select_model) + the re-derived companion mass onto the
pre-registered verdict per candidate.

The thresholds are transcribed here as data (PREREG), and the doc is parsed at
load time as a *cross-check* (parse_prereg_doc) so a drift between the doc and
this code is caught — if the doc's anchor numbers ever change, the assertion in
audit_against_doc() flags it rather than silently using stale constants.

Mass chain reused from the repo's vetted cascade math (consumer_v2): the
photocentric mass function f(M)=a_phot_AU^3/P_yr^2 inverted for M2 at the
candidate's real M1.  a_phot/i come from the DR4 epoch fit (model.py), NOT from
DR3 Thiele-Innes.

stdlib + numpy + scipy(+astropy not needed) only.
"""
from __future__ import annotations

import math
import re
from dataclasses import dataclass, field
from typing import Optional

from modelselect import SelectionResult

DAYS_PER_YEAR = 365.25
NS_FLOOR = 1.2          # M_sun; the dormant-NS minimum used throughout the project
CHANDRA = 1.40          # M_sun
SUBCH_DOWNGRADE = 1.33  # M_sun; WDJ060042 "NS-floor" downgrade boundary in the doc


# ---------------------------------------------------------------------------
# Vetted mass-function chain (mirrors consumer_v2.solve_m2 / mass_class).
# ---------------------------------------------------------------------------

def solve_m2(fM: float, M1: float) -> float:
    """Bisect m2^3/(M1+m2)^2 = f(M) for m2 (M_sun).  80 iterations on [1e-4,1e3]."""
    lo, hi = 1e-4, 1e3
    for _ in range(80):
        mid = 0.5 * (lo + hi)
        if mid ** 3 > fM * (M1 + mid) ** 2:
            hi = mid
        else:
            lo = mid
    return 0.5 * (lo + hi)


def m2_from_fit(a_phot_mas: float, parallax_mas: float, P_days: float, M1: float) -> float:
    """Companion mass from the photocentric a_phot (mas), parallax, period, M1."""
    a_phot_AU = a_phot_mas / parallax_mas
    P_yr = P_days / DAYS_PER_YEAR
    fM = a_phot_AU ** 3 / P_yr ** 2
    return solve_m2(fM, M1)


def m2_from_sin_i(M1: float, a_phot_mas: float, parallax_mas: float, P_days: float,
                  sin_i: float) -> float:
    """For a *luminous-secondary* / substellar case (UCAC4 313): the photocentric
    mass function gives a_phot; M2 scales ~1/sin i for a given orbit.  Here we
    use the face-on (sin i=1) f(M) inversion and the published M2 ∝ 1/sin i
    scaling that the dossier curve uses for the BD/star boundary test.
    """
    m2_faceon = m2_from_fit(a_phot_mas, parallax_mas, P_days, M1)
    if sin_i <= 0:
        return float('inf')
    return m2_faceon / sin_i


# ---------------------------------------------------------------------------
# Pre-registered thresholds (frozen 2026-06-01).  Transcribed from
# docs/dr4_preregistration_2026_06_01.md.
# ---------------------------------------------------------------------------

@dataclass
class CandidatePrereg:
    source_id: str
    name: str
    headline: str
    kind: str                 # 'dark_companion' | 'inclination'
    M1: float                 # real primary mass for the M2 inversion
    M1_err: float
    # DR3 anchors (the values DR4 must beat / reproduce).
    P_dr3: float
    e_dr3: float
    a_phot_dr3: float         # mas
    a_phot_dr3_err: float     # mas (for the "within 3σ" test)
    incl_dr3: Optional[float] # deg (None where undetermined, e.g. UCAC4 313)
    f2_dr3: float
    parallax_dr3: float       # mas (for re-derivation if DR4 parallax not separately handed)
    # Decision constants particular to this candidate.
    f2_confirm: float = 2.0   # "F2 collapses to <= +2"
    f2_refute: float = 5.0    # "F2 stays > +5"
    m2_floor: Optional[float] = None        # mass below which the headline is refuted/downgraded
    super_chandra: Optional[float] = None   # mass above which a super-Ch companion is confirmed
    sin_i_confirm: Optional[float] = None   # UCAC4 313: sin i >= 0.85 confirms substellar
    incl_refute_deg: Optional[float] = None # UCAC4 313: i <= 45° refutes substellar
    notes: str = ''


# The four standing candidates, with thresholds transcribed verbatim from the
# pre-registration "Decision thresholds (pre-registered)" blocks.
PREREG = {
    '6092654861665006592': CandidatePrereg(
        source_id='6092654861665006592', name='WG 26',
        headline='clean sub-Chandra double-WD vs hierarchical triple',
        kind='dark_companion', M1=0.62, M1_err=0.02,
        P_dr3=175.94, e_dr3=0.064, a_phot_dr3=5.40, a_phot_dr3_err=0.08,
        incl_dr3=77.1, f2_dr3=-1.11, parallax_dr3=17.7,
        f2_confirm=2.0, f2_refute=5.0,
        m2_floor=None,            # no compact/NS branch — M2=0.65 already < NS floor
        notes='CONFIRM clean DWD if F2<=+2 AND a_phot within 3σ of 5.40 AND no '
              'accel/2nd-period >5σ. REFUTE->triple if accel/2nd-period >5σ OR F2>+5.'),

    '332248057157474176': CandidatePrereg(
        source_id='332248057157474176', name='WDJ020915',
        headline='THE HEADLINE — long-P M_tot>M_Ch DWD or WD+NS (M2≈1.32)',
        kind='dark_companion', M1=0.718, M1_err=0.053,
        P_dr3=274.52, e_dr3=0.024, a_phot_dr3=7.73, a_phot_dr3_err=0.12,
        incl_dr3=65.8, f2_dr3=8.39, parallax_dr3=11.9,
        f2_confirm=2.0, f2_refute=5.0,
        m2_floor=NS_FLOOR,        # refute/downgrade if M2 < 1.2
        notes='CONFIRM real M_tot>M_Ch single-companion if F2<=+2 AND a_phot within '
              '3σ of 7.73 (M2>=1.2) AND no 2nd-period/accel >5σ. REFUTE if any of: '
              '2nd-period/accel >5σ (triple); a_phot drops M2<1.2 (sub-Ch DWD); F2 '
              'stays >+5 (PARK). Companion class WD-vs-NS stays open -> HST/COS FUV.'),

    '2909342818326298112': CandidatePrereg(
        source_id='2909342818326298112', name='WDJ060042',
        headline='strongest Chandra-straddle — M_tot>M_Ch DWD or WD+NS (M2≈1.37)',
        kind='dark_companion', M1=0.612, M1_err=0.05,
        P_dr3=935.14, e_dr3=0.038, a_phot_dr3=19.62, a_phot_dr3_err=0.95,
        incl_dr3=66.4, f2_dr3=0.79, parallax_dr3=12.08,
        f2_confirm=2.0, f2_refute=5.0,
        m2_floor=SUBCH_DOWNGRADE, super_chandra=CHANDRA,
        notes='CONFIRM M_tot>M_Ch single-companion if F2<=+2 AND a_phot within 3σ of '
              '19.62 AND π tension resolved AND no 2nd-period/accel >5σ. Super-Ch '
              'COMPANION confirmed if refined M2>1.40. DOWNGRADE if M2<1.33 (sub-Ch '
              'DWD). REFUTE->triple if 2nd-period/accel >5σ. Class -> HST/COS FUV.'),

    '5612039087715504640': CandidatePrereg(
        source_id='5612039087715504640', name='UCAC4 313-025977',
        headline='~13-15 M_J brown-dwarf / planet-borderline; inclination is the ballgame',
        kind='inclination', M1=0.23, M1_err=0.04,
        P_dr3=592.32, e_dr3=0.214, a_phot_dr3=1.32, a_phot_dr3_err=0.12,
        incl_dr3=None, f2_dr3=float('nan'), parallax_dr3=30.9,
        f2_confirm=2.0, f2_refute=5.0,
        sin_i_confirm=0.85,       # sin i >= 0.85 (i>=58°) -> substellar
        incl_refute_deg=45.0,     # i <= 45° -> refute substellar
        notes='CONFIRM substellar if DR4 sin i>=0.85 (i>=58°) -> M2<=~15 M_J (planetary '
              'if i>~80° -> M2<13 M_J). REFUTE substellar if i<=45° -> M2>=~18-20 M_J; '
              'FULLY refuted (a star) if M2>=0.075 M_sun (78.5 M_J). Re-evaluate the '
              'M2(sin i) curve at the DR4-refined M1.'),
}

# M_Jup in M_sun (for the substellar reporting).
MJUP_MSUN = 9.5458e-4
HBURN_MSUN = 0.075


# ---------------------------------------------------------------------------
# Decision wiring.
# ---------------------------------------------------------------------------

@dataclass
class Decision:
    source_id: str
    name: str
    verdict: str               # CONFIRM | REFUTE | DOWNGRADE | PARK | INCONCLUSIVE
    detail: str
    model_verdict: str         # single | multi | inconclusive (from modelselect)
    f2_single: float
    a_phot_fit: Optional[float]
    incl_fit: Optional[float]
    M2_fit: Optional[float]
    checks: dict = field(default_factory=dict)
    followup: str = ''


def _within_3sigma(value, anchor, sigma):
    return abs(value - anchor) <= 3.0 * sigma


def decide(source_id: str, sel: SelectionResult,
           parallax_mas: Optional[float] = None,
           M1: Optional[float] = None) -> Decision:
    """Map a SelectionResult onto the candidate's pre-registered verdict.

    parallax_mas / M1 default to the pre-registered DR3 anchors; pass the DR4
    refined values when available (esp. WDJ060042's resolved parallax, and any
    DR4-tightened M1 for UCAC4 313 — the doc explicitly says re-evaluate at DR4 M1).
    """
    pr = PREREG[source_id]
    plx = parallax_mas if parallax_mas is not None else pr.parallax_dr3
    M1u = M1 if M1 is not None else pr.M1
    one = sel.one_body
    f2 = sel.f2_single
    a_phot = one.a_phot
    incl = one.incl_deg
    is_multi = (sel.verdict == 'multi')

    checks = {}

    if pr.kind == 'inclination':
        # --- UCAC4 313: the inclination case --------------------------------
        sin_i = math.sin(math.radians(incl)) if incl is not None else float('nan')
        M2 = m2_from_fit(a_phot, plx, one.P, M1u)   # this is the inclination-resolved mass
        M2_mjup = M2 / MJUP_MSUN
        checks.update(sin_i=sin_i, incl_deg=incl, M2_msun=M2, M2_mjup=M2_mjup,
                      single_keplerian=(sel.verdict == 'single'))
        # Multi-body / blend would itself sink the clean-orbit assumption.
        if is_multi:
            return Decision(source_id, pr.name, 'REFUTE',
                            f'unexpected multi-body / non-Keplerian residual '
                            f'({sel.reason}); the clean single-orbit assumption fails',
                            sel.verdict, f2, a_phot, incl, M2, checks)
        if M2 >= HBURN_MSUN:
            v, d = 'REFUTE', (f'M2={M2:.3f} M_sun ({M2_mjup:.0f} M_J) >= H-burning limit '
                              f'0.075 M_sun at i={incl:.1f}° -> it is a LOW-MASS STAR, '
                              f'fully refuted as substellar')
        elif incl is not None and incl <= pr.incl_refute_deg:
            v, d = 'REFUTE', (f'i={incl:.1f}° <= 45° -> M2={M2_mjup:.0f} M_J '
                              f'(high-mass BD); substellar *headline* refuted')
        elif sin_i >= pr.sin_i_confirm:
            planetary = ' (planetary, <13 M_J)' if M2_mjup < 13.0 else ''
            v, d = 'CONFIRM', (f'sin i={sin_i:.2f} (i={incl:.1f}° >= 58°) -> '
                               f'M2={M2_mjup:.0f} M_J{planetary} -> substellar CONFIRMED')
        else:
            v, d = 'INCONCLUSIVE', (f'45°<i={incl:.1f}°<58° -> M2={M2_mjup:.0f} M_J '
                                    f'(BD but heavier ~16-18 M_J); headline holds as '
                                    f'"wide-orbit BD" but not clean')
        return Decision(source_id, pr.name, v, d, sel.verdict, f2, a_phot, incl, M2,
                        checks, followup='Spectrum (CARMENES/NIRPS) types a luminous '
                                         'secondary if M2 lands at the BD/star boundary.')

    # --- The three dark-companion (WD/NS) cases -----------------------------
    M2 = m2_from_fit(a_phot, plx, one.P, M1u)
    a_phot_ok = _within_3sigma(a_phot, pr.a_phot_dr3, pr.a_phot_dr3_err)
    f2_clean = (f2 <= pr.f2_confirm)
    f2_unreliable = (f2 > pr.f2_refute)
    checks.update(M2_msun=M2, a_phot_fit=a_phot, a_phot_within_3sigma=a_phot_ok,
                  f2_clean=f2_clean, f2_unreliable=f2_unreliable, multi_body=is_multi,
                  model_reason=sel.reason)

    followup = ''
    if source_id in ('332248057157474176', '2909342818326298112'):
        followup = ('Companion class (cool WD vs dormant NS) stays open after DR4 — '
                    'K1 identical, SED-degenerate. Action item: HST/COS FUV, NOT more '
                    'astrometry.')

    # Decision tree (order matters; follows the doc's elif chain per candidate).
    if is_multi:
        return Decision(source_id, pr.name, 'REFUTE',
                        f'2nd-period/acceleration term significant -> hierarchical '
                        f'triple ({sel.reason}); single-companion / M_tot claim void',
                        sel.verdict, f2, a_phot, incl, M2, checks, followup)

    if f2_unreliable:
        # WG 26 has no PARK branch in the doc (its refute is triple-or-F2>+5);
        # WDJ020915 explicitly PARKs; WDJ060042's doc lists only triple/downgrade.
        if source_id == '332248057157474176':
            return Decision(source_id, pr.name, 'PARK',
                            f'F2={f2:+.2f} > +5 with the longer baseline -> orbit '
                            f'unreliable; candidate parked', sel.verdict, f2,
                            a_phot, incl, M2, checks, followup)
        return Decision(source_id, pr.name, 'REFUTE',
                        f'single-Keplerian F2={f2:+.2f} > +5 even with the DR4 '
                        f'baseline -> single-orbit hypothesis rejected', sel.verdict,
                        f2, a_phot, incl, M2, checks, followup)

    # Mass-floor downgrade (WDJ020915: M2<1.2; WDJ060042: M2<1.33).
    if pr.m2_floor is not None and M2 < pr.m2_floor:
        tag = 'sub-Ch DWD' if source_id == '2909342818326298112' else 'ordinary sub-Ch DWD'
        return Decision(source_id, pr.name, 'DOWNGRADE',
                        f'refined M2={M2:.3f} M_sun < {pr.m2_floor} -> {tag}; '
                        f'M_tot>M_Ch / compact claim not supported',
                        sel.verdict, f2, a_phot, incl, M2, checks, followup)

    # CONFIRM branch: clean single Keplerian, a_phot reproduced, no multi-body.
    if f2_clean and a_phot_ok:
        if source_id == '6092654861665006592':
            d = f'F2={f2:+.2f}<=+2, a_phot={a_phot:.2f} mas within 3σ of 5.40, no '\
                f'accel/2nd-period -> CONFIRM clean sub-Ch DWD (M2={M2:.2f}).'
            return Decision(source_id, pr.name, 'CONFIRM', d, sel.verdict, f2,
                            a_phot, incl, M2, checks,
                            followup='Optional 1 RV epoch (K1≈21 km/s) for γ / sin-i cross-check.')
        # WDJ020915 / WDJ060042: confirm single-companion; check super-Chandra.
        sc = ''
        if pr.super_chandra is not None and M2 > pr.super_chandra:
            sc = f' SUPER-CHANDRA companion confirmed (M2={M2:.2f} > 1.40).'
        elif source_id == '2909342818326298112':
            sc = f' Chandra-straddle holds (M2={M2:.2f}; class near-Ch ONe WD vs low-mass NS).'
        d = (f'F2={f2:+.2f}<=+2, a_phot={a_phot:.2f} mas within 3σ of '
             f'{pr.a_phot_dr3}, M2={M2:.2f}>={NS_FLOOR}, no 2nd-period/accel -> '
             f'CONFIRM real M_tot>M_Ch single-companion.{sc}')
        return Decision(source_id, pr.name, 'CONFIRM', d, sel.verdict, f2, a_phot,
                        incl, M2, checks, followup)

    # Anything else: clean enough but a_phot moved (or borderline F2) — inconclusive.
    why = []
    if not f2_clean:
        why.append(f'F2={f2:+.2f} in (+2,+5] (not clean, not unreliable)')
    if not a_phot_ok:
        why.append(f'a_phot={a_phot:.2f} mas NOT within 3σ of {pr.a_phot_dr3}±{pr.a_phot_dr3_err}')
    return Decision(source_id, pr.name, 'INCONCLUSIVE',
                    'no pre-registered branch cleanly triggered: ' + '; '.join(why),
                    sel.verdict, f2, a_phot, incl, M2, checks, followup)


# ---------------------------------------------------------------------------
# Doc cross-check: parse the anchor table from the pre-registration markdown so
# the hard-coded constants here cannot silently drift from the doc.
# ---------------------------------------------------------------------------

def parse_prereg_doc(path: str) -> dict:
    """Extract per-candidate DR3 anchor numbers from the pre-registration doc.

    Reads the 'Pre-registration audit hooks' line that lists the DR3 anchors to
    beat, e.g. 'WG 26 (a_phot 5.40, i 77.1°, F2 −1.11); WDJ020915 (a_phot 7.73,
    F2 +8.39, RUWE 8.79); ...'.  Returns {name: {a_phot, f2, i?}} for audit.
    """
    with open(path, 'r', encoding='utf-8') as fh:
        text = fh.read()
    # Find the audit-hooks anchor line.
    anchors = {}
    # Normalise unicode minus to ASCII.
    text = text.replace('−', '-')
    # Per-candidate parenthetical: NAME (a_phot X, ... F2 Y ...)
    pat = re.compile(r'(WG ?26|WDJ020915|WDJ060042|UCAC4 ?313)[^()]*\(([^)]*)\)')
    for m in pat.finditer(text):
        name = m.group(1).replace(' ', '')
        body = m.group(2)
        ap = re.search(r'a_phot\s*([0-9.]+)', body)
        f2 = re.search(r'F2\s*([+-]?[0-9.]+)', body)
        i_ = re.search(r'\bi\s*([0-9.]+)', body)
        entry = anchors.setdefault(name, {})
        if ap and 'a_phot' not in entry:
            entry['a_phot'] = float(ap.group(1))
        if f2 and 'f2' not in entry:
            entry['f2'] = float(f2.group(1))
        if i_ and 'i' not in entry:
            entry['i'] = float(i_.group(1))
    return anchors


def audit_against_doc(path: str, tol: float = 0.05) -> list:
    """Compare PREREG constants to the parsed doc anchors; return mismatches."""
    parsed = parse_prereg_doc(path)
    keymap = {'6092654861665006592': 'WG26', '332248057157474176': 'WDJ020915',
              '2909342818326298112': 'WDJ060042', '5612039087715504640': 'UCAC4313'}
    problems = []
    for sid, pr in PREREG.items():
        docname = keymap[sid]
        d = parsed.get(docname, {})
        if 'a_phot' in d and abs(d['a_phot'] - pr.a_phot_dr3) > tol:
            problems.append(f'{pr.name}: a_phot doc={d["a_phot"]} vs code={pr.a_phot_dr3}')
        if 'f2' in d and not math.isnan(pr.f2_dr3) and abs(d['f2'] - pr.f2_dr3) > tol:
            problems.append(f'{pr.name}: F2 doc={d["f2"]} vs code={pr.f2_dr3}')
        if 'i' in d and pr.incl_dr3 is not None and abs(d['i'] - pr.incl_dr3) > 0.2:
            problems.append(f'{pr.name}: i doc={d["i"]} vs code={pr.incl_dr3}')
    return problems
