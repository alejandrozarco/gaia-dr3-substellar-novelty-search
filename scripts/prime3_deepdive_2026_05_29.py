#!/usr/bin/env python3
"""Maximum-skepticism deep-dive of the 3 FINAL prime NS candidates from the Gaia DR3
dormant-companion search (2026-05-29).

The central question for ALL three: the astrometric mass function (photocentre AMRF)
CANNOT by itself distinguish a single dark companion (NS) from a hierarchical triple
(unresolved inner main-sequence pair).  Resolving that is the whole job.

REUSED & VALIDATED logic (from scripts/ns2127900_deepdive_2026_05_28.py):
  * AMRF  A = (a_phot/varpi) M1^-1/3 P_yr^-2/3  -- reproduces Shahaf+2023's published
    A=0.6348 and M2min=1.972 for HD 264291 to 0.0%.
  * dark-companion inversion  A = q/(1+q)^(2/3).
  * Shahaf triple-vs-compact criterion via the system AMRF
        A(q,S) = q/(1+q)^(2/3) * (1 - S(1+q)/(q(1+S))),  S = light ratio.
    A single MS companion maxes at A~0.29; an unresolved MS inner pair (triple) maxes
    at A~0.45 (equal-mass inner pair).  A > A_max(triple) => a compact object is
    REQUIRED.  P(compact) is additionally calibrated against Shahaf+2023 table1
    (101380 rows) as an empirical P(III | A, M1) -- because the boundary depends on M1.

C,H CONVENTION (resolved empirically, this file): the Gaia archive labels
c_thiele_innes as 'AU'; the AstroSpectroSB1 K1 = 2*pi*hypot(C,H)*AU_km/(P_s*sqrt(1-e^2)).
Treating C,H as km/s (the survivor_revet shortcut) gives K1~0.5-1 km/s, far too small to
drive a 200-300 sigma detection and grossly inconsistent with the astrometric a_phot;
the AU formula gives K1~8-20 km/s consistent (to ~25-33%) with the astrometric
photocentre, confirming AU.

PER-TARGET:
  T1 HD 264291 (Orbital, NO C,H): astrometry MARGINAL (sig 12.5). FREE-PERIOD
     Lomb-Scargle + free-P Keplerian on 50 LAMOST MRS RVs -- does RV alone recover
     P~999 d?  M2 posterior; SB2/dark check; verdict.
  T2 HD 75567 & T3 1714530 (AstroSpectroSB1, NOVEL): compute AMRF + Shahaf P(compact);
     cross-check spectroscopic K1(C,H) mass function vs astrometric photocentre
     (single dark companion vs triple/SB2 tension); novelty; verdict.

Outputs: /tmp/prime3_{hd264291,hd75567,1714530}.json + /tmp/prime3_report.md
DO NOT edit dossiers / CANDIDATES.md.
"""
from __future__ import annotations
import warnings, json, math
warnings.filterwarnings('ignore')
import numpy as np
from scipy.optimize import least_squares
from scipy import stats

from astroquery.gaia import Gaia
from astroquery.vizier import Vizier
from astroquery.simbad import Simbad
from astropy.coordinates import SkyCoord
from astropy import units as u
from astropy.timeseries import LombScargle

AU_KM = 1.495978707e8
G_SI = 6.6743e-11
MSUN = 1.98892e30
GAIA_REF_JD = 2457389.0
MJD_OFFSET = 2400000.5

# Hard timeout wrapper -- the Gaia/Vizier servers are degraded ("DR4 evolution")
# and astroquery's own timeout does not always abort a stalled socket read.
import threading as _th
def _with_timeout(fn, secs, default):
    """Run fn in a DAEMON thread and abandon it if it stalls past `secs`.
    Uses raw threading (NOT ThreadPoolExecutor, whose atexit join + shutdown(wait=True)
    both block on a hung socket and defeat the timeout). A stalled daemon thread is
    silently dropped at interpreter exit, so the script always terminates."""
    box = {}
    def runner():
        try:
            box['res'] = fn()
        except Exception as e:
            box['err'] = e
    th = _th.Thread(target=runner, daemon=True)
    th.start()
    th.join(secs)
    if 'res' in box:
        return box['res']
    d = dict(default) if isinstance(default, dict) else {}
    why = type(box['err']).__name__ if 'err' in box else 'Timeout'
    d['_note'] = f'network call timed out/failed after {secs}s: {why}'
    return d

# Pre-verified novelty facts (from fast direct SIMBAD queries this session) used as
# fallbacks if the in-script cone searches stall on the degraded server.
KNOWN_FACTS = {
    3378588057203660160: {'main_id': 'HD 264291', 'otype': 'SB*', 'sp_type': 'A',
        'in_shahaf2023': True, 'shahaf_PIII': 0.753, 'shahaf_A': 0.6348, 'shahaf_M2min': 1.972,
        'novelty': 'IN Shahaf+2023 Triage I (NOT novel); the headline compact prospect'},
    5640825637852070016: {'main_id': 'HD 75567', 'otype': 'SB*', 'sp_type': 'G8III/IV',
        'in_shahaf2023': False,
        'bibcodes_summary': '6 bibs, all generic (HD cat, asteroseismic list, interferometric '
            'diameter cats, 2023A&A...674A..34G Gosset Gaia-DR3-multiplicity). SB* tag derives '
            'from the Gaia DR3 NSS solution itself, no independent companion characterization.',
        'novelty': 'NOVEL as compact candidate (absent Shahaf+2023); known SB* only via Gaia DR3'},
    1714530637958169600: {'main_id': 'TYC 4562-535-1', 'otype': 'SB*', 'sp_type': '',
        'in_shahaf2023': False,
        'bibcodes_summary': '1 bib (2023A&A...674A..34G Gosset Gaia-DR3-multiplicity only). '
            'SB* tag derives solely from the Gaia DR3 NSS solution.',
        'novelty': 'NOVEL as compact candidate (absent Shahaf+2023); known SB* only via Gaia DR3'},
}

HD264291 = 3378588057203660160
HD75567 = 5640825637852070016
G1714530 = 1714530637958169600

# --------------------------------------------------------------------------- #
# Gaia fetchers
# --------------------------------------------------------------------------- #
def _flt(v):
    try:
        f = float(v)
        return None if math.isnan(f) else f
    except (TypeError, ValueError):
        return None

def gaia_nss(sid):
    t = Gaia.launch_job(f'SELECT * FROM gaiadr3.nss_two_body_orbit WHERE source_id={sid}').get_results()
    if len(t) == 0:
        return None
    out = {}
    for c in t.colnames:
        if c == 'corr_vec':
            continue
        v = t[c][0]
        fv = _flt(v)
        out[c] = fv if fv is not None else (None if (hasattr(v, 'mask') and v is np.ma.masked) else str(v))
    return out

def gaia_source(sid):
    cols = ('source_id, ra, dec, parallax, parallax_error, pmra, pmdec, ruwe, '
            'phot_g_mean_mag, phot_bp_mean_mag, phot_rp_mean_mag, bp_rp, '
            'radial_velocity, radial_velocity_error, rv_amplitude_robust, '
            'rv_chisq_pvalue, rv_nb_transits, rv_renormalised_gof, '
            'rv_expected_sig_to_noise, ipd_frac_multi_peak, ipd_gof_harmonic_amplitude, '
            'astrometric_excess_noise, astrometric_excess_noise_sig, non_single_star, '
            'phot_variable_flag, phot_bp_rp_excess_factor')
    t = Gaia.launch_job(f'SELECT {cols} FROM gaiadr3.gaia_source WHERE source_id={sid}').get_results()
    if len(t) == 0:
        return None
    out = {}
    for c in t.colnames:
        v = t[c][0]
        fv = _flt(v)
        out[c] = fv if fv is not None else str(v)
    return out

def gaia_ap(sid):
    cols = ('mass_flame, radius_flame, lum_flame, age_flame, '
            'teff_gspphot, logg_gspphot, mh_gspphot, distance_gspphot, '
            'teff_gspspec, logg_gspspec, mh_gspspec, '
            'mass_flame_lower, mass_flame_upper, radius_flame_lower, radius_flame_upper')
    try:
        t = Gaia.launch_job(f'SELECT {cols} FROM gaiadr3.astrophysical_parameters WHERE source_id={sid}').get_results()
        if len(t) == 0:
            return {}
        out = {}
        for c in t.colnames:
            v = t[c][0]
            fv = _flt(v)
            out[c] = fv if fv is not None else str(v)
        return out
    except Exception as e:
        return {'_err': f'{type(e).__name__}: {e}'}

# --------------------------------------------------------------------------- #
# Orbit / AMRF math (validated against Shahaf+2023)
# --------------------------------------------------------------------------- #
def photocentric_a_mas(A, B, F, G):
    if any(v is None for v in (A, B, F, G)):
        return None
    uu = 0.5 * (A * A + B * B + F * F + G * G)
    vv = A * G - B * F
    disc = max(0.0, uu * uu - vv * vv)
    return math.sqrt(uu + math.sqrt(disc))

def inclination_from_ABFG(A, B, F, G):
    if any(v is None for v in (A, B, F, G)):
        return None
    p = (A * A + B * B + F * F + G * G)
    q = A * G - B * F
    u_ = 0.5 * p
    a2 = u_ + math.sqrt(max(u_ * u_ - q * q, 0.0))
    # cos i = |q| / a^2  (Halbwachs+2023: A*G - B*F = a^2 cos i; sign/orientation ambiguous)
    cosi = max(min(abs(q) / a2, 1.0), 0.0)
    return {'a_mas': math.sqrt(a2), 'cos_i': cosi, 'incl_deg': math.degrees(math.acos(cosi))}

def solve_m2(fM, M1):
    lo, hi = 1e-5, 1e3
    for _ in range(120):
        mid = 0.5 * (lo + hi)
        if mid ** 3 > fM * (M1 + mid) ** 2:
            hi = mid
        else:
            lo = mid
    return 0.5 * (lo + hi)

def amrf(a_phot_mas, parallax_mas, M1, P_yr):
    if not (a_phot_mas and parallax_mas and M1 and P_yr):
        return None
    return (a_phot_mas / parallax_mas) * M1 ** (-1.0 / 3.0) * P_yr ** (-2.0 / 3.0)

def q_from_amrf_dark(A):
    """Invert A=q/(1+q)^(2/3) for the DARK-companion mass ratio q=M2/M1."""
    lo, hi = 1e-4, 50.0
    for _ in range(120):
        mid = 0.5 * (lo + hi)
        if (mid / (1 + mid) ** (2.0 / 3.0)) > A:
            hi = mid
        else:
            lo = mid
    return 0.5 * (lo + hi)

def amrf_system(q, S):
    """Shahaf+2019 system AMRF: dark S=0 -> q/(1+q)^(2/3)."""
    return (q / (1 + q) ** (2.0 / 3.0)) * (1 - S * (1 + q) / (q * (1 + S)))

def amrf_ms_single_max(M1, beta=3.5):
    """Max AMRF from a SINGLE main-sequence companion (L=M^beta)."""
    best = 0.0
    L1 = M1 ** beta
    for q in np.linspace(0.02, 1.0, 500):
        S = (q * M1) ** beta / L1
        A = amrf_system(q, S)
        if A > best:
            best = A
    return best

def amrf_ms_triple_max(M1, beta=3.5):
    """Max AMRF from a hierarchical TRIPLE: companion = unresolved inner MS pair.
    Scan total companion mass M2=q*M1 and the inner split; both inner stars MS
    (L=M^beta). Maximised for an equal-mass inner pair. This is Shahaf's Class-III
    boundary: A above this REQUIRES a compact object (no MS triple can reach it)."""
    best = 0.0
    arg = None
    L1 = M1 ** beta
    for q in np.linspace(0.05, 1.6, 240):
        M2 = q * M1
        for fr in np.linspace(0.5, 1.0, 80):
            ma, mb = fr * M2, (1 - fr) * M2
            if mb < 0.075:           # below H-burning -> effectively dark
                L2 = ma ** beta
            else:
                L2 = ma ** beta + mb ** beta
            S = L2 / L1
            A = amrf_system(q, S)
            if A > best:
                best = A
                arg = {'q': float(q), 'inner_frac': float(fr), 'S': float(S)}
    return best, arg

# Spectroscopic Thiele-Innes (AstroSpectroSB1): C,H in AU.
def K1_from_CH(C, H, P_d, e):
    if C is None or H is None:
        return None
    a1sini = math.hypot(C, H)  # AU (validated: archive unit AU; AU formula matches astrometry)
    P_s = P_d * 86400.0
    K1 = 2.0 * math.pi * a1sini * AU_KM / (P_s * math.sqrt(1 - e * e))
    return {'a1sini_AU': a1sini, 'K1_kms': K1, 'omega_deg': math.degrees(math.atan2(C, H)),
            'omega_rad': math.atan2(C, H)}

def f_spec_msun(K1_kms, P_d, e):
    if K1_kms <= 0 or P_d <= 0 or e >= 1:
        return 0.0
    K = K1_kms * 1000.0
    P_s = P_d * 86400.0
    return (P_s * K ** 3 * (1 - e * e) ** 1.5 / (2 * math.pi * G_SI)) / MSUN

def kepler_rv(t, P, e, T0, K1, gamma, omega):
    M = 2.0 * math.pi * (np.asarray(t, float) - T0) / P
    M = np.mod(M + math.pi, 2 * math.pi) - math.pi
    E = M + e * np.sin(M)
    for _ in range(80):
        dE = (E - e * np.sin(E) - M) / (1.0 - e * np.cos(E))
        E -= dE
        if np.max(np.abs(dE)) < 1e-12:
            break
    nu = 2.0 * np.arctan2(np.sqrt(1 + e) * np.sin(E / 2.0), np.sqrt(1 - e) * np.cos(E / 2.0))
    return gamma + K1 * (np.cos(nu + omega) + e * math.cos(omega))

# --------------------------------------------------------------------------- #
# Shahaf P(compact) empirical calibration from table1 (P(III | A, M1))
# --------------------------------------------------------------------------- #
_SHAHAF_CACHE = {}
def shahaf_table1():
    if 'tbl' in _SHAHAF_CACHE:
        return _SHAHAF_CACHE['tbl']
    v = Vizier(columns=['GaiaDR3', 'M1', 'A', 'e_A', 'M2min', 'PII', 'PIII'], timeout=180)
    v.ROW_LIMIT = -1
    t = v.get_catalogs('J/MNRAS/518/2991/table1')[0]
    arr = {
        'M1': np.array([float(r['M1']) for r in t]),
        'A': np.array([float(r['A']) for r in t]),
        'M2min': np.array([float(r['M2min']) for r in t]),
        'PIII': np.array([float(r['PIII']) for r in t]),
        'PII': np.array([float(r['PII']) for r in t]),
    }
    _SHAHAF_CACHE['tbl'] = arr
    return arr

def shahaf_pcompact(A_obs, M1, dA=0.04, dM1=0.30):
    """Empirical P(compact) = mean PIII of Shahaf table1 sources within a box in
    (A, M1) around the target. Falls back to widening the box if too few neighbours."""
    tb = shahaf_table1()
    for (da, dm) in ((dA, dM1), (0.06, 0.5), (0.10, 0.8), (0.15, 1.2)):
        m = (np.abs(tb['A'] - A_obs) < da) & (np.abs(tb['M1'] - M1) < dm)
        if m.sum() >= 15:
            return {'p_compact_PIII_mean': float(tb['PIII'][m].mean()),
                    'p_innerbinary_PII_mean': float(tb['PII'][m].mean()),
                    'n_neighbours': int(m.sum()), 'box_dA': da, 'box_dM1': dm,
                    'M2min_mean': float(tb['M2min'][m].mean())}
    # very sparse (high A region): use all sources with A within +/-0.06 regardless of M1
    m = np.abs(tb['A'] - A_obs) < 0.06
    return {'p_compact_PIII_mean': float(tb['PIII'][m].mean()) if m.sum() else None,
            'p_innerbinary_PII_mean': float(tb['PII'][m].mean()) if m.sum() else None,
            'n_neighbours': int(m.sum()), 'box_dA': 0.06, 'box_dM1': 'any',
            'note': 'sparse high-A region; M1-marginalised'}

# --------------------------------------------------------------------------- #
# SIMBAD + literature
# --------------------------------------------------------------------------- #
def simbad_otype_bibs(gaia_id_str):
    s = Simbad()
    for flds in (('otype', 'ids', 'sp_type', 'plx_value', 'V'),
                 ('otype', 'ids', 'sp_type', 'plx_value'), ('otype', 'ids', 'sp_type')):
        try:
            s.add_votable_fields(*flds)
            break
        except Exception:
            continue
    out = {'query': gaia_id_str}
    try:
        r = s.query_object(gaia_id_str)
        if r is not None and len(r):
            out['main_id'] = str(r['main_id'][0])
            out['otype'] = str(r['otype'][0]) if 'otype' in r.colnames else None
            out['sp_type'] = str(r['sp_type'][0]) if 'sp_type' in r.colnames else None
            out['ids'] = str(r['ids'][0]) if 'ids' in r.colnames else None
        else:
            out['main_id'] = None
    except Exception as e:
        out['_obj_err'] = f'{type(e).__name__}: {e}'
    q = (f"SELECT b.bibcode, b.journal, b.title FROM basic AS ba "
         f"JOIN ident AS i ON i.oidref = ba.oid "
         f"JOIN has_ref AS hr ON hr.oidref = ba.oid "
         f"JOIN ref AS b ON b.oidbib = hr.oidbibref "
         f"WHERE i.id = '{gaia_id_str}'")
    try:
        t = s.query_tap(q)
        out['n_bibcodes'] = len(t)
        out['bibcodes'] = [{'bibcode': str(row['bibcode']), 'journal': str(row['journal']),
                            'title': str(row['title'])[:95]} for row in t]
    except Exception as e:
        out['_bib_err'] = f'{type(e).__name__}: {e}'
    return out

def lit_crossmatch(ra, dec):
    coord = SkyCoord(ra=ra * u.deg, dec=dec * u.deg, frame='icrs')
    v = Vizier(columns=['**'], timeout=60)
    v.ROW_LIMIT = -1
    cats = [
        ('J/MNRAS/518/2991', 'Shahaf+2023 Triage I (compact-companion sample)'),
        ('J/MNRAS/529/3729', 'Shahaf+2024 Triage II (WD census)'),
        ('J/A+A/674/A9', 'Gaia DR3 NSS astrometric orbits (Halbwachs/Holl 2023)'),
        ('J/A+A/674/A34', 'Gaia DR3 SB orbits validation (Gosset 2023)'),
    ]
    out = {}
    for cat, label in cats:
        try:
            res = v.query_region(coord, radius=5 * u.arcsec, catalog=cat)
            if res is None or len(res) == 0:
                out[label] = {'match': False}
            else:
                out[label] = {'match': True, 'n_rows': int(len(res[0]))}
        except Exception as e:
            out[label] = {'match': None, 'note': f'{type(e).__name__}'}
    return out

# --------------------------------------------------------------------------- #
# M1 prior
# --------------------------------------------------------------------------- #
def m1_prior(ap, fallback_mean, fallback_sig, label):
    mf = ap.get('mass_flame')
    mf = mf if isinstance(mf, (int, float)) else None
    if mf and mf > 0.3:
        lo = ap.get('mass_flame_lower') or mf * 0.95
        hi = ap.get('mass_flame_upper') or mf * 1.05
        return mf, max((hi - lo) / 2.0, 0.05), f'FLAME {mf:.2f} (+/- {max((hi-lo)/2.0,0.05):.2f})'
    return fallback_mean, fallback_sig, label

# --------------------------------------------------------------------------- #
# AMRF / Shahaf compact-vs-triple analysis for an AstroSpectroSB1 (or Orbital)
# --------------------------------------------------------------------------- #
def amrf_analysis(nss, gs, ap, M1, M1sig, n=300000, seed=3):
    rng = np.random.default_rng(seed)
    A, B, F, G = (nss['a_thiele_innes'], nss['b_thiele_innes'],
                  nss['f_thiele_innes'], nss['g_thiele_innes'])
    Ae, Be, Fe, Ge = (nss['a_thiele_innes_error'], nss['b_thiele_innes_error'],
                      nss['f_thiele_innes_error'], nss['g_thiele_innes_error'])
    plx, plxe = nss['parallax'], nss['parallax_error']
    P, Pe = nss['period'], nss.get('period_error') or 0.0
    P_yr = P / 365.25

    a_phot = photocentric_a_mas(A, B, F, G)
    A_obs = amrf(a_phot, plx, M1, P_yr)
    A_single_max = amrf_ms_single_max(M1)
    A_triple_max, triple_arg = amrf_ms_triple_max(M1)
    q_dark = q_from_amrf_dark(A_obs) if A_obs else None
    M2_dark = q_dark * M1 if q_dark else None
    incl = inclination_from_ABFG(A, B, F, G)

    # MC AMRF distribution (propagate ABFG, plx, P, M1)
    As = rng.normal(A, Ae, n); Bs = rng.normal(B, Be, n)
    Fs = rng.normal(F, Fe, n); Gs_ = rng.normal(G, Ge, n)
    plxs = np.clip(rng.normal(plx, plxe, n), 1e-3, None)
    Ps = rng.normal(P, Pe, n) if Pe else np.full(n, P)
    M1s = np.clip(rng.normal(M1, M1sig, n), 0.5, 3.0)
    uu = 0.5 * (As ** 2 + Bs ** 2 + Fs ** 2 + Gs_ ** 2)
    vv = As * Gs_ - Bs * Fs
    a_phot_s = np.sqrt(np.maximum(uu + np.sqrt(np.maximum(uu ** 2 - vv ** 2, 0.0)), 0.0))
    A_s = (a_phot_s / plxs) * M1s ** (-1.0 / 3.0) * (Ps / 365.25) ** (-2.0 / 3.0)
    A_s = A_s[np.isfinite(A_s)]

    # fraction of AMRF posterior above the MS-triple ceiling (analytic compact-required test)
    P_above_triple = float(np.mean(A_s > A_triple_max))
    P_above_single = float(np.mean(A_s > A_single_max))

    # Shahaf empirical P(compact) at the central (A,M1)
    sh = shahaf_pcompact(A_obs, M1) if A_obs else None

    def pct(x):
        return {'p2.5': float(np.percentile(x, 2.5)), 'p16': float(np.percentile(x, 16)),
                'p50': float(np.percentile(x, 50)), 'p84': float(np.percentile(x, 84)),
                'p97.5': float(np.percentile(x, 97.5))}

    return {
        'M1_used': M1, 'M1_sig': M1sig, 'a_phot_mas': a_phot, 'parallax_mas': plx,
        'P_yr': P_yr, 'incl_from_ABFG': incl,
        'AMRF_obs': A_obs, 'AMRF_posterior': pct(A_s) if len(A_s) else None,
        'AMRF_ms_single_max': A_single_max, 'AMRF_ms_triple_max': A_triple_max,
        'triple_max_config': triple_arg,
        'compact_required_analytic': (A_obs > A_triple_max) if A_obs else None,
        'P_AMRF_above_triple_ceiling': P_above_triple,
        'P_AMRF_above_single_ceiling': P_above_single,
        'q_dark_implied': q_dark, 'M2_dark_implied_msun': M2_dark,
        'shahaf_empirical_Pcompact': sh,
    }

# --------------------------------------------------------------------------- #
# Spectroscopic-vs-astrometric cross-check (single-dark vs triple/SB2 tension)
# --------------------------------------------------------------------------- #
def spec_vs_astrom(nss, M1, M1sig, amrf_res, n=300000, seed=5):
    """For AstroSpectroSB1: the spectroscopic C,H give a1*sin i directly. For a SINGLE
    dark companion the photocentre == primary, so the astrometric a_phot*sin i must
    equal the spectroscopic a1*sin i. Tension (spec > astrom) hints at an inner
    luminous pair (triple) where the photocentre is displaced toward the companion,
    OR an SB2. Also compares the spectroscopic mass function with the photocentric one."""
    rng = np.random.default_rng(seed)
    C, H = nss.get('c_thiele_innes'), nss.get('h_thiele_innes')
    Ce, He = nss.get('c_thiele_innes_error'), nss.get('h_thiele_innes_error')
    if C is None:
        return {'note': 'no spectroscopic Thiele-Innes (not AstroSpectroSB1)'}
    P, Pe = nss['period'], nss.get('period_error') or 0.0
    e, ee = nss['eccentricity'], nss.get('eccentricity_error') or 0.0
    A, B, F, G = (nss['a_thiele_innes'], nss['b_thiele_innes'],
                  nss['f_thiele_innes'], nss['g_thiele_innes'])
    Ae, Be, Fe, Ge = (nss['a_thiele_innes_error'], nss['b_thiele_innes_error'],
                      nss['f_thiele_innes_error'], nss['g_thiele_innes_error'])
    plx, plxe = nss['parallax'], nss['parallax_error']

    ch = K1_from_CH(C, H, P, e)
    K1_spec = ch['K1_kms']
    f_spec = f_spec_msun(K1_spec, P, e)

    # MC
    Cs = rng.normal(C, Ce, n); Hs = rng.normal(H, He, n)
    Ps = rng.normal(P, Pe, n) if Pe else np.full(n, P)
    es = np.clip(rng.normal(e, ee, n), 0, 0.95)
    plxs = np.clip(rng.normal(plx, plxe, n), 1e-3, None)
    M1s = np.clip(rng.normal(M1, M1sig, n), 0.5, 3.0)
    As = rng.normal(A, Ae, n); Bs = rng.normal(B, Be, n)
    Fs = rng.normal(F, Fe, n); Gs_ = rng.normal(G, Ge, n)

    a1sini_spec = np.hypot(Cs, Hs)                      # AU
    K1s = 2 * np.pi * a1sini_spec * AU_KM / (Ps * 86400.0 * np.sqrt(1 - es ** 2))
    fspec = (Ps * 86400.0) * (K1s * 1000.0) ** 3 * (1 - es ** 2) ** 1.5 / (2 * np.pi * G_SI) / MSUN

    # astrometric a_phot * sin i
    uu = 0.5 * (As ** 2 + Bs ** 2 + Fs ** 2 + Gs_ ** 2)
    vv = As * Gs_ - Bs * Fs
    a2 = uu + np.sqrt(np.maximum(uu ** 2 - vv ** 2, 0.0))
    a_phot = np.sqrt(np.maximum(a2, 0.0))               # mas
    cosi = np.clip(np.abs(vv) / a2, 0, 1)               # cos i = |A*G-B*F|/a^2 (no sqrt)
    sini = np.sqrt(np.clip(1 - cosi ** 2, 1e-6, 1))
    a_phot_AU = a_phot / plxs
    a_phot_sini = a_phot_AU * sini                      # AU (== a1 sin i if dark companion)

    ratio = a1sini_spec / a_phot_sini                   # ~1 if single dark companion
    ratio = ratio[np.isfinite(ratio)]

    # photocentric mass function and dark-companion M2 (edge-on equiv used elsewhere)
    P_yr = Ps / 365.25
    fphot = a_phot_AU ** 3 / P_yr ** 2
    M2_phot = np.array([solve_m2(max(f, 1e-6), m1) for f, m1 in zip(fphot, M1s)])

    # M2 from spectroscopic K1 + astrometric inclination (the proper photocentric route)
    rhs = fspec / sini ** 3
    M2_specincl = np.array([solve_m2(max(r, 1e-6), m1) for r, m1 in zip(rhs, M1s)])

    def pct(x):
        x = x[np.isfinite(x)]
        return {'p2.5': float(np.percentile(x, 2.5)), 'p16': float(np.percentile(x, 16)),
                'p50': float(np.percentile(x, 50)), 'p84': float(np.percentile(x, 84)),
                'p97.5': float(np.percentile(x, 97.5))}

    return {
        'K1_spec_from_CH_kms': K1_spec, 'f_spec_from_CH_msun': f_spec,
        'a1sini_spec_AU': ch['a1sini_AU'],
        'K1_spec_posterior_kms': pct(K1s),
        'spec_vs_astrom_a1sini_ratio': pct(ratio),
        'ratio_p50': float(np.median(ratio)),
        'consistent_single_dark': bool(0.7 < float(np.median(ratio)) < 1.4),
        'f_spec_msun_posterior': pct(fspec),
        'f_phot_msun_posterior': pct(fphot),
        'M2_phot_route_msun': pct(M2_phot),
        'M2_spec_plus_astromincl_msun': pct(M2_specincl),
        'P_M2_above_2.2_(BH)': float(np.mean(M2_specincl > 2.2)),
        'P_M2_in_NS_1.1_2.2': float(np.mean((M2_specincl > 1.1) & (M2_specincl < 2.2))),
        'P_M2_below_1.4': float(np.mean(M2_specincl < 1.4)),
        'note': ('ratio>1 => spectroscopic photocentre excursion exceeds astrometric; '
                 'mild->triple/SB2 hint. ~1 => single dark companion consistent.'),
    }

# --------------------------------------------------------------------------- #
# HD 264291: free-period RV analysis on 50 LAMOST MRS epochs
# --------------------------------------------------------------------------- #
def load_lamost_epochs(sid):
    d = json.load(open('/tmp/ns_pool_triage_results.json'))
    cen = d[str(sid)]['census']
    eps = []
    for arch in ('LAMOST_MRS', 'LAMOST_LRS', 'APOGEE_visits', 'RAVE', 'GALAH_DR3'):
        for ep in cen.get(arch, {}).get('epochs', []):
            if ep[0] is not None and ep[1] is not None:
                eps.append((ep[0], ep[1], ep[2] if ep[2] else 0.5, arch))
    return eps

def free_period_rv(sid, nss, M1, M1sig):
    eps = load_lamost_epochs(sid)
    t = np.array([e[0] for e in eps]); rv = np.array([e[1] for e in eps])
    er = np.maximum(np.array([e[2] for e in eps]), 0.3)
    P_nss = nss['period']
    Pe_nss = nss.get('period_error') or 0.0
    e_nss = nss['eccentricity']
    T0_nss = nss['t_periastron'] + GAIA_REF_JD - MJD_OFFSET

    out = {'n_epochs': len(t), 'mjd_min': float(t.min()), 'mjd_max': float(t.max()),
           'baseline_d': float(t.max() - t.min()), 'n_cycles_at_Pnss': float((t.max() - t.min()) / P_nss),
           'rv_span_kms': float(np.ptp(rv)), 'rv_median_err_kms': float(np.median(er)),
           'P_nss_d': P_nss, 'P_nss_err_d': Pe_nss}

    # ---- 1. FREE-period Lomb-Scargle (P NOT fixed) ----
    ls = LombScargle(t, rv, er)
    freq, power = ls.autopower(minimum_frequency=1 / 3000., maximum_frequency=1 / 20.,
                               samples_per_peak=15)
    pk = int(np.argmax(power))
    P_ls = float(1 / freq[pk])
    fap = float(ls.false_alarm_probability(power[pk], method='baluev'))
    # top peaks
    from scipy.signal import find_peaks
    idx, _ = find_peaks(power, height=0.15)
    top = sorted(idx, key=lambda i: -power[i])[:6]
    out['lomb_scargle'] = {
        'best_period_d': P_ls, 'best_power': float(power[pk]), 'FAP_baluev': fap,
        'top_peaks': [{'P_d': float(1 / freq[i]), 'power': float(power[i])} for i in top],
        'P_ls_vs_Pnss_pct': 100 * (P_ls - P_nss) / P_nss,
        'P_ls_within_2sig_of_Pnss': bool(abs(P_ls - P_nss) < 2 * Pe_nss) if Pe_nss else None,
    }

    # ---- 2. FREE-period Keplerian (fit P, e, T0, K1, gamma, omega ALL free) ----
    def resid(p, tt, yy, ee):
        P, e, T0, K1, g, om = p
        if e < 0 or e >= 0.95 or P <= 0:
            return np.full_like(yy, 1e6)
        return (kepler_rv(tt, P, e, T0, K1, g, om) - yy) / ee
    gamma0 = float(np.median(rv))
    best = None
    # multi-start over period near the LS peak AND broadly, plus eccentricity/omega
    Pseeds = sorted(set([P_ls, P_nss, P_ls / 2, P_ls * 2, 527.6, 268.4]
                        + list(np.linspace(200, 1500, 14))))
    for P0 in Pseeds:
        for e0 in (0.1, 0.35, 0.55):
            for om0 in np.linspace(-math.pi, math.pi, 6, endpoint=False):
                try:
                    r = least_squares(
                        resid, [P0, e0, T0_nss % P0, max(np.ptp(rv) / 2, 5), gamma0, om0],
                        bounds=([20, 0, -1e5, 0, gamma0 - 60, -math.pi],
                                [3000, 0.94, 1e5, 120, gamma0 + 60, math.pi]),
                        args=(t, rv, er), max_nfev=4000)
                    c2 = float(np.sum(r.fun ** 2))
                    if best is None or c2 < best['c2']:
                        best = {'x': r.x, 'c2': c2, 'jac': r.jac}
                except Exception:
                    continue
    Pf, ef, T0f, K1f, gf, omf = best['x']
    dof = len(t) - 6
    # uncertainties
    sig = {}
    try:
        cov = np.linalg.inv(best['jac'].T @ best['jac']) * max(best['c2'] / dof, 1.0)
        for i, nm in enumerate(['P', 'e', 'T0', 'K1', 'gamma', 'omega']):
            sig[nm] = float(math.sqrt(abs(cov[i, i])))
    except Exception:
        pass
    # constant-RV null
    w = 1 / er ** 2
    gc = float(np.sum(w * rv) / np.sum(w))
    chi2_const = float(np.sum(((rv - gc) / er) ** 2))
    out['free_keplerian'] = {
        'P_d': float(Pf), 'P_err_d': sig.get('P'), 'e': float(ef), 'e_err': sig.get('e'),
        'K1_kms': float(K1f), 'K1_err_kms': sig.get('K1'),
        'K1_signif': (float(K1f / sig['K1']) if sig.get('K1') else None),
        'gamma_kms': float(gf), 'omega_deg': math.degrees(omf),
        'chi2': best['c2'], 'dof': dof, 'chi2_dof': best['c2'] / dof,
        'f_spec_msun': f_spec_msun(K1f, Pf, ef),
        'P_free_vs_Pnss_pct': 100 * (Pf - P_nss) / P_nss,
        'constant_null_chi2': chi2_const, 'constant_null_dof': len(t) - 1,
        'constant_null_pvalue': float(stats.chi2.sf(chi2_const, len(t) - 1)),
        'delta_chi2_orbit_vs_const': chi2_const - best['c2'],
    }

    # ---- 3. NSS-period-LOCKED Keplerian (P,e,T0 fixed) for comparison ----
    def resid_lock(p, tt, yy, ee):
        K1, g, om = p
        return (kepler_rv(tt, P_nss, e_nss, T0_nss, K1, g, om) - yy) / ee
    bl = None
    for om0 in np.linspace(-math.pi, math.pi, 12, endpoint=False):
        r = least_squares(resid_lock, [max(np.ptp(rv) / 2, 5), gamma0, om0],
                          bounds=([0, gamma0 - 60, -math.pi], [120, gamma0 + 60, math.pi]),
                          args=(t, rv, er), max_nfev=3000)
        c2 = float(np.sum(r.fun ** 2))
        if bl is None or c2 < bl['c2']:
            bl = {'x': r.x, 'c2': c2, 'jac': r.jac}
    dofL = len(t) - 3
    sigKL = None
    try:
        covL = np.linalg.inv(bl['jac'].T @ bl['jac']) * max(bl['c2'] / dofL, 1.0)
        sigKL = float(math.sqrt(abs(covL[0, 0])))
    except Exception:
        pass
    out['nss_locked_keplerian'] = {
        'P_locked_d': P_nss, 'K1_kms': float(bl['x'][0]), 'K1_err_kms': sigKL,
        'K1_signif': (float(bl['x'][0] / sigKL) if sigKL else None),
        'omega_deg': math.degrees(bl['x'][2]), 'chi2': bl['c2'], 'dof': dofL,
        'chi2_dof': bl['c2'] / dofL, 'f_spec_msun': f_spec_msun(bl['x'][0], P_nss, e_nss)}

    # ---- 4. SB2 / second-peak check: are there bimodal RVs at any epoch? ----
    # LAMOST MRS gives RVbr0/RVbr1 per visit (pairs at identical MJD). Large within-MJD
    # scatter would hint SB2. Compute per-MJD spread.
    from collections import defaultdict
    bym = defaultdict(list)
    for m, r, e2, lab in eps:
        bym[round(m)].append(r)
    spreads = [max(v) - min(v) for v in bym.values() if len(v) > 1]
    out['sb2_check'] = {
        'n_mjd_with_pairs': len(spreads),
        'median_within_mjd_spread_kms': float(np.median(spreads)) if spreads else None,
        'max_within_mjd_spread_kms': float(max(spreads)) if spreads else None,
        'note': 'large within-epoch RV spread (>>few km/s) would indicate SB2 (two sets of lines)',
    }

    # ---- 5. M2 posterior from the data-preferred (free-P) K1 + astrometric inclination ----
    incl = inclination_from_ABFG(nss['a_thiele_innes'], nss['b_thiele_innes'],
                                 nss['f_thiele_innes'], nss['g_thiele_innes'])
    K1_use = float(K1f); K1_use_err = sig.get('K1') or max(0.1 * K1_use, 1.0)
    e_use = float(ef)
    rng = np.random.default_rng(7)
    nmc = 300000
    K1s = np.clip(rng.normal(K1_use, K1_use_err, nmc), 0.1, None)
    es = np.clip(rng.normal(e_use, sig.get('e') or 0.05, nmc), 0, 0.94)
    Ps = rng.normal(Pf, sig.get('P') or P_nss * 0.04, nmc)
    M1s = np.clip(rng.normal(M1, M1sig, nmc), 0.5, 3.0)
    # inclination from ABFG samples
    A, B, F, G = (nss['a_thiele_innes'], nss['b_thiele_innes'],
                  nss['f_thiele_innes'], nss['g_thiele_innes'])
    Ae, Be, Fe, Ge = (nss['a_thiele_innes_error'], nss['b_thiele_innes_error'],
                      nss['f_thiele_innes_error'], nss['g_thiele_innes_error'])
    As = rng.normal(A, Ae, nmc); Bs = rng.normal(B, Be, nmc)
    Fs = rng.normal(F, Fe, nmc); Gs_ = rng.normal(G, Ge, nmc)
    uu = 0.5 * (As ** 2 + Bs ** 2 + Fs ** 2 + Gs_ ** 2); vv = As * Gs_ - Bs * Fs
    a2 = uu + np.sqrt(np.maximum(uu ** 2 - vv ** 2, 0.0))
    cosi = np.clip(np.abs(vv) / a2, 0, 1); sini = np.sqrt(np.clip(1 - cosi ** 2, 1e-6, 1))  # cos i (no sqrt)
    fM = (Ps * 86400.0) * (K1s * 1000.0) ** 3 * (1 - es ** 2) ** 1.5 / (2 * np.pi * G_SI) / MSUN
    rhs = fM / sini ** 3
    M2 = np.array([solve_m2(max(r, 1e-6), m1) for r, m1 in zip(rhs, M1s)])
    def pct(x):
        x = x[np.isfinite(x)]
        return {'p2.5': float(np.percentile(x, 2.5)), 'p16': float(np.percentile(x, 16)),
                'p50': float(np.percentile(x, 50)), 'p84': float(np.percentile(x, 84)),
                'p97.5': float(np.percentile(x, 97.5))}
    out['M2_posterior_from_freeP_RV'] = {
        'M1_prior': f'{M1:.2f}+/-{M1sig:.2f}', 'K1_used_kms': K1_use, 'K1_err_used': K1_use_err,
        'incl_from_ABFG_deg': incl['incl_deg'] if incl else None,
        'f_spec_msun': pct(fM), 'M2_msun': pct(M2),
        'P_M2_above_2.2_BH': float(np.mean(M2 > 2.2)),
        'P_M2_in_NS_1.1_2.2': float(np.mean((M2 > 1.1) & (M2 < 2.2))),
        'P_M2_above_mass_gap_floor_1.4': float(np.mean(M2 > 1.4)),
        'P_M2_below_1.0_WD': float(np.mean(M2 < 1.0)),
    }
    out['epochs_used'] = [(round(m, 2), round(r, 2), round(e2, 2), lab) for m, r, e2, lab in eps]
    return out

# --------------------------------------------------------------------------- #
def run_hd264291():
    print('=' * 72, '\nT1  HD 264291  Gaia DR3', HD264291, '\n', '=' * 72)
    rec = {'source_id': HD264291, 'name': 'HD 264291', 'role': 'best compact prospect (Shahaf PIII=0.75)'}
    nss = gaia_nss(HD264291); rec['nss'] = nss
    gs = gaia_source(HD264291); rec['gaia_source'] = gs
    ap = gaia_ap(HD264291); rec['astrophysical_parameters'] = ap
    M1, M1sig, M1lbl = m1_prior(ap, 1.95, 0.10, 'Shahaf M1 1.95')
    rec['M1_prior'] = M1lbl
    print(f"  NSS type={nss['nss_solution_type']} P={nss['period']:.1f}+/-{nss.get('period_error'):.0f}d "
          f"e={nss['eccentricity']:.3f} sig={nss['significance']:.1f} gof={nss['goodness_of_fit']:.2f}")
    print(f"  ruwe={gs['ruwe']:.2f} rv_ampl_robust={gs.get('rv_amplitude_robust')} "
          f"rv_nb={gs.get('rv_nb_transits')} ipd_multi={gs.get('ipd_frac_multi_peak')} M1={M1lbl}")

    # AMRF / Shahaf
    rec['amrf'] = amrf_analysis(nss, gs, ap, M1, M1sig)
    a = rec['amrf']
    print(f"  AMRF_obs={a['AMRF_obs']:.3f} (Shahaf A=0.635); MS-single max={a['AMRF_ms_single_max']:.3f}, "
          f"MS-triple max={a['AMRF_ms_triple_max']:.3f}; compact-req(analytic)={a['compact_required_analytic']}")
    print(f"  Shahaf empirical P(compact|A,M1)={a['shahaf_empirical_Pcompact']}")
    print(f"  q_dark={a['q_dark_implied']:.2f} -> M2_dark={a['M2_dark_implied_msun']:.2f} Msun")

    # FREE-PERIOD RV (the decisive test)
    print('  >> FREE-PERIOD RV ANALYSIS (50 LAMOST MRS epochs):')
    rec['free_period_rv'] = free_period_rv(HD264291, nss, M1, M1sig)
    fp = rec['free_period_rv']
    ls = fp['lomb_scargle']; fk = fp['free_keplerian']
    print(f"    LS best P={ls['best_period_d']:.1f}d FAP={ls['FAP_baluev']:.1e} "
          f"({ls['P_ls_vs_Pnss_pct']:+.1f}% vs NSS P=999.4)")
    print(f"    LS top peaks: {[(round(p['P_d'],0),round(p['power'],2)) for p in ls['top_peaks']]}")
    print(f"    FREE-P Keplerian: P={fk['P_d']:.1f}+/-{fk.get('P_err_d')}d e={fk['e']:.2f} "
          f"K1={fk['K1_kms']:.1f} ({fk['K1_signif']}sig) chi2/dof={fk['chi2_dof']:.2f} "
          f"({fk['P_free_vs_Pnss_pct']:+.1f}% vs NSS)")
    print(f"    const-null p={fk['constant_null_pvalue']:.1e} dchi2(orbit vs const)={fk['delta_chi2_orbit_vs_const']:.0f}")
    print(f"    NSS-locked K1={fp['nss_locked_keplerian']['K1_kms']:.1f} "
          f"chi2/dof={fp['nss_locked_keplerian']['chi2_dof']:.2f}")
    print(f"    SB2 check: median within-epoch spread={fp['sb2_check']['median_within_mjd_spread_kms']} km/s")
    m2 = fp['M2_posterior_from_freeP_RV']
    print(f"    M2 (free-P K1 + astrom incl) = {m2['M2_msun']['p50']:.2f} "
          f"[{m2['M2_msun']['p16']:.2f},{m2['M2_msun']['p84']:.2f}] Msun | "
          f"P(NS 1.1-2.2)={m2['P_M2_in_NS_1.1_2.2']:.2f} P(>2.2 BH)={m2['P_M2_above_2.2_BH']:.2f} "
          f"P(<1.0 WD)={m2['P_M2_below_1.0_WD']:.2f}")

    # Write science JSON BEFORE the (slow, degraded-server) novelty queries so results persist.
    rec['known_facts'] = KNOWN_FACTS[HD264291]
    rec['VERDICT'] = verdict_for(rec, is_novel=False)
    json.dump(rec, open('/tmp/prime3_hd264291.json', 'w'), indent=1, default=str)
    print('  [science JSON written -> /tmp/prime3_hd264291.json]')

    rec['simbad'] = _with_timeout(lambda: simbad_otype_bibs(f'Gaia DR3 {HD264291}'), 45,
                                  {'otype': KNOWN_FACTS[HD264291]['otype'], 'note': 'fallback'})
    rec['literature'] = _with_timeout(lambda: lit_crossmatch(gs['ra'], gs['dec']), 60,
                                      {'Shahaf+2023 Triage I (compact-companion sample)': {'match': True}})
    print(f"  SIMBAD otype={rec['simbad'].get('otype')} sp={rec['simbad'].get('sp_type')} "
          f"n_bibs={rec['simbad'].get('n_bibcodes')}")
    print(f"  LIT (in Shahaf+2023?): {rec['literature']}")
    json.dump(rec, open('/tmp/prime3_hd264291.json', 'w'), indent=1, default=str)
    return rec

def run_novel(sid, name, m1_fallback, m1_sig, m1_lbl):
    print('=' * 72, f'\nNOVEL  {name}  Gaia DR3', sid, '\n', '=' * 72)
    rec = {'source_id': sid, 'name': name}
    nss = gaia_nss(sid); rec['nss'] = nss
    gs = gaia_source(sid); rec['gaia_source'] = gs
    ap = gaia_ap(sid); rec['astrophysical_parameters'] = ap
    M1, M1sig, M1lbl = m1_prior(ap, m1_fallback, m1_sig, m1_lbl)
    rec['M1_prior'] = M1lbl
    print(f"  NSS type={nss['nss_solution_type']} P={nss['period']:.1f}+/-{nss.get('period_error'):.1f}d "
          f"e={nss['eccentricity']:.3f} sig={nss['significance']:.1f} gof={nss['goodness_of_fit']:.2f}")
    print(f"  ruwe={gs['ruwe']:.2f} G={gs.get('phot_g_mean_mag'):.2f} bp_rp={gs.get('bp_rp')} "
          f"ipd_multi={gs.get('ipd_frac_multi_peak')} rv_n_primary={nss.get('rv_n_obs_primary')}")
    print(f"  C,H = {nss.get('c_thiele_innes'):.4f}, {nss.get('h_thiele_innes'):.4f} AU; M1={M1lbl}")

    # AMRF / Shahaf compact-vs-triple (THE KEY MISSING TEST)
    rec['amrf'] = amrf_analysis(nss, gs, ap, M1, M1sig)
    a = rec['amrf']
    print(f"  >> AMRF_obs={a['AMRF_obs']:.3f} [{a['AMRF_posterior']['p16']:.3f},{a['AMRF_posterior']['p84']:.3f}]")
    print(f"     MS-single max={a['AMRF_ms_single_max']:.3f}, MS-TRIPLE max={a['AMRF_ms_triple_max']:.3f}")
    print(f"     compact REQUIRED (analytic, A>triple ceiling)? {a['compact_required_analytic']}  "
          f"| P(AMRF>triple ceiling)={a['P_AMRF_above_triple_ceiling']:.2f}")
    print(f"     Shahaf empirical P(compact|A,M1): {a['shahaf_empirical_Pcompact']}")
    print(f"     q_dark={a['q_dark_implied']:.2f} -> M2_dark={a['M2_dark_implied_msun']:.2f}; "
          f"incl={a['incl_from_ABFG']['incl_deg']:.1f}deg")

    # spectroscopic vs astrometric cross-check
    rec['spec_vs_astrom'] = spec_vs_astrom(nss, M1, M1sig, a)
    s = rec['spec_vs_astrom']
    print(f"  >> SPEC vs ASTROM: K1(C,H)={s['K1_spec_from_CH_kms']:.2f} km/s, f_spec(C,H)={s['f_spec_from_CH_msun']:.3f}")
    print(f"     a1sini_spec/a_phot_sini ratio = {s['ratio_p50']:.2f} "
          f"[{s['spec_vs_astrom_a1sini_ratio']['p16']:.2f},{s['spec_vs_astrom_a1sini_ratio']['p84']:.2f}] "
          f"-> single-dark consistent? {s['consistent_single_dark']}")
    print(f"     M2 (spec K1 + astrom incl) = {s['M2_spec_plus_astromincl_msun']['p50']:.2f} "
          f"[{s['M2_spec_plus_astromincl_msun']['p16']:.2f},{s['M2_spec_plus_astromincl_msun']['p84']:.2f}] Msun")
    print(f"     P(NS 1.1-2.2)={s['P_M2_in_NS_1.1_2.2']:.2f} P(>2.2 BH)={s['P_M2_above_2.2_(BH)']:.2f} "
          f"P(<1.4)={s['P_M2_below_1.4']:.2f}")

    # Persist science JSON BEFORE slow novelty queries.
    rec['known_facts'] = KNOWN_FACTS[sid]
    rec['VERDICT'] = verdict_for(rec, is_novel=True)
    jkey = 'hd75567' if sid == HD75567 else '1714530'
    json.dump(rec, open(f'/tmp/prime3_{jkey}.json', 'w'), indent=1, default=str)
    print(f'  [science JSON written -> /tmp/prime3_{jkey}.json]')

    rec['simbad'] = _with_timeout(lambda: simbad_otype_bibs(f'Gaia DR3 {sid}'), 45,
                                  {'otype': KNOWN_FACTS[sid]['otype'], 'main_id': KNOWN_FACTS[sid]['main_id'],
                                   'sp_type': KNOWN_FACTS[sid]['sp_type'], 'note': 'fallback'})
    rec['literature'] = _with_timeout(lambda: lit_crossmatch(gs['ra'], gs['dec']), 60,
                                      {'Shahaf+2023 Triage I (compact-companion sample)': {'match': False}})
    print(f"  SIMBAD otype={rec['simbad'].get('otype')} sp={rec['simbad'].get('sp_type')} "
          f"main_id={rec['simbad'].get('main_id')} n_bibs={rec['simbad'].get('n_bibcodes')}")
    print(f"  NOVELTY (absent from Shahaf+2023?): {rec['literature']}")
    json.dump(rec, open(f'/tmp/prime3_{jkey}.json', 'w'), indent=1, default=str)
    return rec

def verdict_for(rec, is_novel):
    """Synthesize a per-target verdict.

    DECISION DRIVER (novel AstroSpectroSB1): Shahaf+2023's EMPIRICAL P(compact) =
    P(III | A, M1), calibrated on hundreds of real neighbours in the published
    Triage-I sample -- this is exactly the classifier the brief asks to reproduce.
    The simple analytic 'A > MS-triple ceiling' test (beta=3.5 power-law M-L) is a
    SECONDARY cross-check and is KNOWN TO BE OPTIMISTIC: it ignores the steepening
    of the real M-L relation and the luminosity of the (massive, evolved) primaries,
    so it over-calls 'compact required'. Where the two disagree, Shahaf's empirical
    probability governs (skeptical default: a candidate is not compact unless the
    calibrated classifier demands it).

    The spectroscopic-vs-astrometric a1sin(i) ratio is a tie-breaker: ratio ~ 1 ->
    single dark companion; ratio systematically > 1 -> the photocentre excursion is
    SMALLER than the spectroscopic one, i.e. light from the companion side is pulling
    the photocentre back -> an inner LUMINOUS pair (triple) / SB2, NOT a dark object."""
    a = rec['amrf']
    if is_novel:
        s = rec['spec_vs_astrom']
        compact_req_analytic = a['compact_required_analytic']
        p_above_triple = a['P_AMRF_above_triple_ceiling']
        shp = (a['shahaf_empirical_Pcompact'] or {}).get('p_compact_PIII_mean')
        pII = (a['shahaf_empirical_Pcompact'] or {}).get('p_innerbinary_PII_mean')
        ratio = s['ratio_p50']
        # ratio>1 means a_phot*sin i < a1*sin i -> photocentre pulled by companion light:
        # a positive-light (triple/SB2) indicator, NOT single-dark.
        ratio_triple_leaning = ratio > 1.12
        single_dark_strict = 0.85 < ratio < 1.15
        # Shahaf empirical probability is the governing statistic.
        if shp is not None and shp >= 0.6:
            v = 'COMPACT-FAVORED'
        elif shp is not None and shp <= 0.35:
            v = 'TRIPLE-FAVORED'          # inner MS pair strongly preferred by Shahaf classifier
        else:
            v = 'AMBIGUOUS'
        return {'verdict': v,
                'driver': 'Shahaf empirical P(compact|A,M1)',
                'AMRF': a['AMRF_obs'], 'AMRF_ms_triple_ceiling': a['AMRF_ms_triple_max'],
                'shahaf_P_compact': shp, 'shahaf_P_innerbinary_triple': pII,
                'analytic_compact_required': compact_req_analytic,
                'analytic_note': ('analytic ceiling beta=3.5 is OPTIMISTIC and is OVERRIDDEN by '
                                  'the Shahaf empirical classifier where they disagree'),
                'spec_astrom_a1sini_ratio': ratio,
                'ratio_interpretation': ('triple/SB2-leaning (ratio>1.12: companion light pulls '
                                         'photocentre)' if ratio_triple_leaning else
                                         ('single-dark consistent' if single_dark_strict else 'marginal')),
                'M2_dark_if_compact_msun': a['M2_dark_implied_msun'],
                'M2_spec_plus_incl_p50': s['M2_spec_plus_astromincl_msun']['p50']}
    else:
        fp = rec['free_period_rv']
        ls = fp['lomb_scargle']; fk = fp['free_keplerian']
        rv_confirms = (ls['FAP_baluev'] < 1e-6 and abs(fk['P_free_vs_Pnss_pct']) < 20
                       and fk['constant_null_pvalue'] < 1e-3)
        return {'verdict': ('RV-CONFIRMED ORBIT' if rv_confirms else 'RV-AMBIGUOUS'),
                'LS_P_d': ls['best_period_d'], 'LS_FAP': ls['FAP_baluev'],
                'freeP_Keplerian_P_d': fk['P_d'], 'freeP_vs_NSS_pct': fk['P_free_vs_Pnss_pct'],
                'AMRF': a['AMRF_obs'], 'shahaf_Pcompact': 0.753,
                'M2_p50': fp['M2_posterior_from_freeP_RV']['M2_msun']['p50']}

# --------------------------------------------------------------------------- #
def main():
    out = {}
    # run_* now compute VERDICT and write their JSON internally (before slow novelty queries).
    out['hd264291'] = run_hd264291()
    # HD 75567: SIMBAD sp_type G8 III/IV (giant/subgiant), no FLAME mass. A G8IV ~ 1.3-1.6,
    # G8III could be higher; adopt 1.5 +/- 0.25 to span the evolutionary ambiguity.
    out['hd75567'] = run_novel(HD75567, 'HD 75567', 1.5, 0.25,
                               'G8III/IV sp-type prior 1.5 +/- 0.25 (no FLAME; evolved)')
    # 1714530: FLAME 1.41 but teff=5300/logg=3.56/R=2.75 -> subgiant; FLAME used with its band.
    out['1714530'] = run_novel(G1714530, 'Gaia DR3 1714530637958169600', 1.41, 0.12,
                               'FLAME subgiant prior')
    # report
    write_report(out)
    print('\nSaved /tmp/prime3_{hd264291,hd75567,1714530}.json + /tmp/prime3_report.md')
    return out

def write_report(out):
    L = []
    L.append('# Prime-3 NS candidate deep-dive (2026-05-29)\n')
    L.append('Maximum skepticism. Central test: can the astrometric mass function be '
             'explained by a hierarchical MS triple (inner pair) rather than a single '
             'compact object? AMRF computation reproduces Shahaf+2023 A=0.635 / M2min=1.97 '
             'for HD 264291 to 0.0%. C,H confirmed in AU (K1 formula validated against the '
             'astrometric photocentre).\n')
    for key, label in (('hd264291', 'T1 HD 264291'), ('hd75567', 'T2 HD 75567 (NOVEL)'),
                       ('1714530', 'T3 Gaia DR3 1714530637958169600 (NOVEL)')):
        r = out[key]; v = r['VERDICT']; a = r['amrf']; nss = r['nss']
        L.append(f'\n## {label} — VERDICT: {v["verdict"]}')
        L.append(f'- Gaia DR3 {r["source_id"]}; NSS {nss["nss_solution_type"]}, '
                 f'P={nss["period"]:.1f} d, e={nss["eccentricity"]:.3f}, sig={nss["significance"]:.1f}, '
                 f'ruwe={r["gaia_source"]["ruwe"]:.1f}, G={r["gaia_source"].get("phot_g_mean_mag"):.2f}')
        L.append(f'- M1 prior: {r["M1_prior"]}')
        L.append(f'- AMRF = {a["AMRF_obs"]:.3f}; MS-single ceiling {a["AMRF_ms_single_max"]:.3f}, '
                 f'MS-TRIPLE ceiling {a["AMRF_ms_triple_max"]:.3f} (beta=3.5, OPTIMISTIC); '
                 f'analytic compact-required: {a["compact_required_analytic"]}')
        sh = a.get('shahaf_empirical_Pcompact') or {}
        L.append(f'- **Shahaf empirical P(compact|A,M1) = {sh.get("p_compact_PIII_mean"):.3f}** '
                 f'[P(inner-binary/triple) = {sh.get("p_innerbinary_PII_mean"):.3f}], '
                 f'n_neighbours={sh.get("n_neighbours")} -- GOVERNING classifier')
        L.append(f'- q_dark = {a["q_dark_implied"]:.2f} -> M2_dark = {a["M2_dark_implied_msun"]:.2f} Msun')
        if key == 'hd264291':
            fp = r['free_period_rv']; ls = fp['lomb_scargle']; fk = fp['free_keplerian']
            L.append(f'- FREE-PERIOD RV (50 LAMOST MRS): LS P={ls["best_period_d"]:.1f} d '
                     f'(FAP={ls["FAP_baluev"]:.1e}, {ls["P_ls_vs_Pnss_pct"]:+.1f}% vs NSS); '
                     f'free-P Keplerian P={fk["P_d"]:.1f} d, K1={fk["K1_kms"]:.1f} km/s '
                     f'({fk["K1_signif"]}sig), chi2/dof={fk["chi2_dof"]:.2f}, '
                     f'const-null p={fk["constant_null_pvalue"]:.1e}')
            m2 = fp['M2_posterior_from_freeP_RV']
            L.append(f'- M2 (free-P RV K1 + astrom incl) = {m2["M2_msun"]["p50"]:.2f} '
                     f'[{m2["M2_msun"]["p16"]:.2f},{m2["M2_msun"]["p84"]:.2f}] Msun; '
                     f'P(NS 1.1-2.2)={m2["P_M2_in_NS_1.1_2.2"]:.2f}, P(>2.2 BH)={m2["P_M2_above_2.2_BH"]:.2f}, '
                     f'P(<1.0 WD)={m2["P_M2_below_1.0_WD"]:.2f}')
            L.append(f'- SB2 check: median within-epoch RV spread '
                     f'{fp["sb2_check"]["median_within_mjd_spread_kms"]} km/s')
        else:
            s = r['spec_vs_astrom']
            L.append(f'- Spectroscopic K1(C,H) = {s["K1_spec_from_CH_kms"]:.2f} km/s, '
                     f'f_spec = {s["f_spec_from_CH_msun"]:.3f} Msun')
            L.append(f'- Spec-vs-astrom a1sini ratio = {s["ratio_p50"]:.2f} '
                     f'({v.get("ratio_interpretation")}) -- ratio>1 means photocentre excursion '
                     f'< spectroscopic, i.e. companion light pulls photocentre (triple/SB2 hint)')
            L.append(f'- M2 (spec K1 + astrom incl) = {s["M2_spec_plus_astromincl_msun"]["p50"]:.2f} '
                     f'[{s["M2_spec_plus_astromincl_msun"]["p16"]:.2f},'
                     f'{s["M2_spec_plus_astromincl_msun"]["p84"]:.2f}] Msun; '
                     f'P(NS)={s["P_M2_in_NS_1.1_2.2"]:.2f}, P(<1.4)={s["P_M2_below_1.4"]:.2f}')
        lit = r['literature']
        in_shahaf = lit.get('Shahaf+2023 Triage I (compact-companion sample)', {}).get('match')
        L.append(f'- In Shahaf+2023 Triage I: {in_shahaf}; SIMBAD otype='
                 f'{r["simbad"].get("otype")}, n_bibs={r["simbad"].get("n_bibcodes")}')
    open('/tmp/prime3_report.md', 'w').write('\n'.join(L))

if __name__ == '__main__':
    main()
