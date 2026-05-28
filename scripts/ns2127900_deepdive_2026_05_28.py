#!/usr/bin/env python3
"""Skeptical deep-dive of the single second-method-corroborated NS candidate from the
161-source Gaia DR3 dormant-companion triage (2026-05-28).

PRIMARY: Gaia DR3 2127900555635640832 (2MASS J19170097+4718505 = KIC 10267850),
NSS AstroSpectroSB1, P=303.4 d.  The triage reported K1=16.5 km/s at "206 sigma"
and verdict CORROBORATED -- but that significance came from a 3-free-parameter fit
to 4 epochs (dof=1) with absurdly small APOGEE formal errors (+/-0.07 km/s).  This
script does the work properly:

  1. Re-fetch full NSS solution (incl. spectroscopic Thiele-Innes C,H) + gaia_source
     + astrophysical_parameters (FLAME mass, teff, logg).
  2. THE KEY INDEPENDENT TEST.  For AstroSpectroSB1, C,H ARE the spectroscopic orbit:
     C = a1 sin(omega) sin i, H = a1 cos(omega) sin i  [AU]  (Gaia DR3 doc eq 7.51).
     => K1 = 2*pi*sqrt(C^2+H^2)*AU / (P*sqrt(1-e^2))  with ZERO free orbital params.
     This is a fully-locked prediction the archival RVs must satisfy.
  3. Re-fit the NSS-locked Keplerian to the 4 archival epochs (P,e,T0 fixed; free
     K1,gamma,omega) with a REALISTIC APOGEE error floor (0.1-0.3 km/s); report the
     HONEST K1 significance, chi2/dof, and a constant-RV null with the same floor.
     Also a 1-free-param fit (gamma only) at the C,H-locked K1+omega -- the genuine test.
  4. M2 posterior: Monte-Carlo over M1 (FLAME / F3V-prior) and the astrometric
     inclination (from A,B,F,G), propagating C,H,parallax,period errors.  Is M2 above
     the NS floor (>~1.1 Msun) or at/below the WD ceiling (~1.4 Msun)?
  5. Dark-companion test: AMRF (Shahaf+2019)  A = (alpha/varpi) M1^-1/3 P_yr^-2/3,
     compared to A_max(MS)~0.36.  Plus Gaia multiplicity flags (ipd_frac_multi_peak,
     ruwe), SED second-light check (BP-RP vs F3V, 2MASS), and f_spec/f_phot ratio.
  6. Novelty: SIMBAD otype + ALL bibcodes; cross-match Shahaf+2023, Mueller-Horn+2026,
     Halbwachs+2023 via Vizier.

SANITY CHECKS (brief): 3378588057203660160 (HD 264291 -- is the 50-epoch LAMOST set
really single-phase?), 2129927539681151872 & 1379150557507688960 (confirm REFUTED).
NOVELTY pass: the 4 prime no-RV Tier-1 NS (5640825637852070016, 6419437207856851584,
1714530637958169600, 823243942431149568) -- SIMBAD otype + bibcodes.

Outputs: /tmp/ns2127900_*.json + /tmp/ns2127900_report.md
"""
from __future__ import annotations
import warnings, json, math, time
warnings.filterwarnings('ignore')
import numpy as np
from scipy.optimize import least_squares
from scipy import stats

from astroquery.gaia import Gaia
from astroquery.vizier import Vizier
from astroquery.simbad import Simbad
from astropy.coordinates import SkyCoord
from astropy import units as u

AU_KM = 1.495978707e8
GMSUN = 1.32712440018e20      # m^3/s^2 (G*Msun) -- exact-ish
G_SI = 6.6743e-11
MSUN = 1.98892e30
GAIA_REF_JD = 2457389.0
MJD_OFFSET = 2400000.5

PRIMARY = 2127900555635640832

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
            'phot_variable_flag')
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
# Orbit math
# --------------------------------------------------------------------------- #
def photocentric_a_mas(A, B, F, G):
    if any(v is None for v in (A, B, F, G)):
        return None
    uu = 0.5 * (A * A + B * B + F * F + G * G)
    vv = A * G - B * F
    disc = max(0.0, uu * uu - vv * vv)
    return math.sqrt(uu + math.sqrt(disc))

def inclination_from_ABFG(A, B, F, G):
    """Campbell inclination from Thiele-Innes (Halbwachs+2023 inversion)."""
    if any(v is None for v in (A, B, F, G)):
        return None
    p = (A * A + B * B + F * F + G * G)
    q = A * G - B * F
    omega_plus = math.atan2(B - F, A + G)   # omega+Omega
    omega_minus = math.atan2(B + F, A - G)  # omega-Omega
    # a*(1+cos^2 i)/2 and a*cos i :
    u_ = 0.5 * p
    v_ = q
    a2 = u_ + math.sqrt(max(u_ * u_ - v_ * v_, 0.0))   # = a^2
    a = math.sqrt(a2)
    # cos i = sqrt( |q| / a^2 )  (sign ambiguous)
    cosi = math.sqrt(max(min(abs(v_) / a2, 1.0), 0.0))
    incl = math.degrees(math.acos(cosi))
    return {'a_mas': a, 'cos_i': cosi, 'incl_deg': incl,
            'omega_plus_deg': math.degrees(omega_plus),
            'omega_minus_deg': math.degrees(omega_minus)}

def solve_m2(fM, M1):
    lo, hi = 1e-5, 1e3
    for _ in range(120):
        mid = 0.5 * (lo + hi)
        if mid ** 3 > fM * (M1 + mid) ** 2:
            hi = mid
        else:
            lo = mid
    return 0.5 * (lo + hi)

def K1_from_CH(C, H, P_d, e):
    """AstroSpectroSB1: C,H in AU = a1 sin(omega) sin i, a1 cos(omega) sin i.
    K1 = 2*pi*(a1 sin i)/(P sqrt(1-e^2)).  Returns K1 [km/s], omega, a1sini[AU]."""
    if C is None or H is None:
        return None
    a1sini = math.hypot(C, H)  # AU
    P_s = P_d * 86400.0
    K1 = 2.0 * math.pi * a1sini * AU_KM / (P_s * math.sqrt(1 - e * e))
    omega = math.atan2(C, H)
    return {'a1sini_AU': a1sini, 'K1_kms': K1, 'omega_deg': math.degrees(omega), 'omega_rad': omega}

def f_spec_msun(K1_kms, P_d, e):
    if K1_kms <= 0 or P_d <= 0 or e >= 1:
        return 0.0
    K = K1_kms * 1000.0
    P_s = P_d * 86400.0
    fM = P_s * K ** 3 * (1 - e * e) ** 1.5 / (2 * math.pi * G_SI)
    return fM / MSUN

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

def phase_of(mjd, P, T0_mjd):
    return ((mjd - T0_mjd) % P) / P

# --------------------------------------------------------------------------- #
# AMRF (Shahaf+2019)
# --------------------------------------------------------------------------- #
def amrf(a_phot_mas, parallax_mas, M1, P_yr):
    """A = (alpha/varpi) * M1^-1/3 * P_yr^-2/3.  alpha,varpi in mas; M1 Msun; P yr."""
    if not (a_phot_mas and parallax_mas and M1 and P_yr):
        return None
    return (a_phot_mas / parallax_mas) * M1 ** (-1.0 / 3.0) * P_yr ** (-2.0 / 3.0)

def amrf_of_q_dark(q):
    """Dark companion (S=0): A = q/(1+q)^(2/3)."""
    return q / (1 + q) ** (2.0 / 3.0)

def q_from_amrf_dark(A):
    """Invert A=q/(1+q)^2/3 for the DARK-companion mass ratio q=M2/M1."""
    lo, hi = 1e-4, 50.0
    for _ in range(120):
        mid = 0.5 * (lo + hi)
        if amrf_of_q_dark(mid) > A:
            hi = mid
        else:
            lo = mid
    return 0.5 * (lo + hi)

def amrf_ms_max(M1, beta=4.0):
    """Max AMRF achievable by a single main-sequence companion (S=q^beta).
    Scan q in (0,1]; for each q the MS flux ratio S=q^beta; A(q,S)."""
    best = 0.0
    for q in np.linspace(0.02, 1.0, 400):
        S = q ** beta
        A = (q / (1 + q) ** (2.0 / 3.0)) * (1 - S * (1 + q) / (q * (1 + S)))
        if A > best:
            best = A
    return best

# --------------------------------------------------------------------------- #
# SIMBAD
# --------------------------------------------------------------------------- #
def simbad_otype_bibs(gaia_id_str):
    s = Simbad()
    try:
        s.add_votable_fields('otype', 'ids', 'sp_type', 'plx_value', 'V')
    except Exception:
        try:
            s.add_votable_fields('otype', 'ids', 'sp_type', 'plx_value')
        except Exception:
            pass
    out = {'query': gaia_id_str}
    try:
        r = s.query_object(gaia_id_str)
        if r is not None and len(r):
            out['main_id'] = str(r['main_id'][0])
            out['otype'] = str(r['otype'][0]) if 'otype' in r.colnames else None
            out['sp_type'] = str(r['sp_type'][0]) if 'sp_type' in r.colnames else None
            out['ids'] = str(r['ids'][0]) if 'ids' in r.colnames else None
            out['plx_value'] = _flt(r['plx_value'][0]) if 'plx_value' in r.colnames else None
        else:
            out['main_id'] = None
    except Exception as e:
        out['_obj_err'] = f'{type(e).__name__}: {e}'
    # bibcodes via TAP
    q = (f"SELECT b.bibcode, b.journal, b.title FROM basic AS ba "
         f"JOIN ident AS i ON i.oidref = ba.oid "
         f"JOIN has_ref AS hr ON hr.oidref = ba.oid "
         f"JOIN ref AS b ON b.oidbib = hr.oidbibref "
         f"WHERE i.id = '{gaia_id_str}'")
    try:
        t = s.query_tap(q)
        bibs = [{'bibcode': str(row['bibcode']), 'journal': str(row['journal']),
                 'title': str(row['title'])[:90]} for row in t]
        out['n_bibcodes'] = len(bibs)
        out['bibcodes'] = bibs
    except Exception as e:
        out['_bib_err'] = f'{type(e).__name__}: {e}'
    return out

# --------------------------------------------------------------------------- #
# Literature Vizier cross-match (Shahaf 2023 Triage I, Mueller-Horn 2026, Halbwachs 2023)
# --------------------------------------------------------------------------- #
def lit_crossmatch(ra, dec):
    coord = SkyCoord(ra=ra * u.deg, dec=dec * u.deg, frame='icrs')
    rad = 5 * u.arcsec
    v = Vizier(columns=['**'], timeout=60)
    v.ROW_LIMIT = -1
    cats = [
        ('J/MNRAS/518/2991', 'Shahaf+2023 Triage I (compact-companion sample)'),
        ('J/MNRAS/529/3729', 'Shahaf+2024 Triage II (white-dwarf census)'),
        ('J/A+A/674/A9', 'Gaia DR3 NSS astrometric orbits (Halbwachs/Holl 2023)'),
        ('J/A+A/674/A34', 'Gaia DR3 SB orbits validation (Gosset/Damerdji)'),
    ]
    out = {}
    for cat, label in cats:
        try:
            res = v.query_region(coord, radius=rad, catalog=cat)
            if res is None or len(res) == 0:
                out[label] = {'match': False}
            else:
                t = res[0]
                out[label] = {'match': True, 'n_rows': int(len(t)), 'cols': list(t.colnames)[:18]}
        except Exception as e:
            out[label] = {'match': None, 'note': f'{type(e).__name__}'}
    return out

# --------------------------------------------------------------------------- #
# NSS-locked RV fits (honest errors)
# --------------------------------------------------------------------------- #
def rv_fits(epochs, nss, err_floor=0.3, apogee_floor=0.3):
    """epochs: list of (mjd, rv, err, source_label). Returns dict of fits.
    Applies a realistic error floor (APOGEE visit RV systematic ~0.1-0.3 km/s)."""
    P = nss['period']
    e = nss['eccentricity']
    T0 = nss['t_periastron'] + GAIA_REF_JD - MJD_OFFSET  # MJD frame
    ch = K1_from_CH(nss.get('c_thiele_innes'), nss.get('h_thiele_innes'), P, e)

    ev = [(m, r, er, lab) for (m, r, er, lab) in epochs if m is not None]
    t = np.array([x[0] for x in ev], float)
    rv = np.array([x[1] for x in ev], float)
    # error floor: APOGEE formal errors are wildly under-reported; impose floor
    err = np.array([(x[2] if (x[2] and x[2] > 0) else 5.0) for x in ev], float)
    floors = np.array([apogee_floor if 'APOGEE' in x[3] else err_floor for x in ev])
    err = np.maximum(err, floors)
    gamma0 = nss.get('center_of_mass_velocity') or float(np.mean(rv))

    phases = [round(phase_of(m, P, T0), 4) for m in t]
    out = {'n_epochs': len(ev), 'phases': phases, 'rv_span_kms': float(np.ptp(rv)),
           'errors_used_kms': [round(float(x), 3) for x in err],
           'epochs_used': [(round(m, 3), round(r, 3), round(float(er), 3), lab)
                           for (m, r, er, lab), er2 in zip(ev, err)
                           for er in [er2]]}

    # ---- constant-RV null (with floor) ----
    w = 1.0 / err ** 2
    gc = float(np.sum(w * rv) / np.sum(w))
    chi2c = float(np.sum(((rv - gc) / err) ** 2))
    dofc = max(len(ev) - 1, 1)
    out['constant_null'] = {'gamma': gc, 'chi2': chi2c, 'dof': dofc,
                            'chi2_dof': chi2c / dofc,
                            'p_value': float(stats.chi2.sf(chi2c, dofc))}

    # ---- free (K1,gamma,omega) NSS-locked fit ----
    def resid_free(p):
        K1, g, om = p
        return (kepler_rv(t, P, e, T0, K1, g, om) - rv) / err
    best = None
    for om0 in np.linspace(-math.pi, math.pi, 12, endpoint=False):
        for K0 in (5.0, 15.0, 25.0, 40.0):
            try:
                r = least_squares(resid_free, [K0, gamma0, om0],
                                  bounds=([0, gamma0 - 80, -math.pi], [120, gamma0 + 80, math.pi]),
                                  max_nfev=2000)
                c2 = float(np.sum(r.fun ** 2))
                if best is None or c2 < best['c2']:
                    best = {'x': r.x, 'c2': c2, 'jac': r.jac}
            except Exception:
                continue
    K1f, gf, omf = best['x']
    dof_free = len(ev) - 3
    sigK1 = None
    try:
        cov = np.linalg.inv(best['jac'].T @ best['jac'])
        s2 = best['c2'] / dof_free if dof_free > 0 else 1.0
        sigK1 = float(math.sqrt(abs(cov[0, 0]) * max(s2, 1.0)))
    except Exception:
        pass
    out['free_fit'] = {
        'K1_kms': float(K1f), 'K1_sigma_kms': sigK1,
        'K1_signif': (float(K1f / sigK1) if sigK1 and sigK1 > 0 else None),
        'gamma_kms': float(gf), 'omega_deg': math.degrees(omf),
        'chi2': best['c2'], 'dof': dof_free,
        'chi2_dof': (best['c2'] / dof_free if dof_free > 0 else None),
        'f_spec_msun': f_spec_msun(K1f, P, e),
        'dof_note': 'UNDERCONSTRAINED (dof<=0); chi2 not meaningful' if dof_free <= 0 else 'ok',
    }

    # ---- C,H-locked test: K1 (& nominally omega) FIXED from spectroscopic TI ----
    # The Gaia DR3 RV sign + periastron-reference conventions admit a phase/sign
    # ambiguity in omega (the well-documented Pourbaix degeneracy), and t_periastron
    # itself has a sizeable error. We therefore test the C,H-LOCKED K1 against the
    # data under (a) gamma-only fits over the 4 omega-convention rotations, and
    # (b) the same but ALSO marginalising T0 over +/- its NSS error. The cleanest
    # statement is: with K1 held at the spectroscopic value, what is the best
    # achievable chi2 (gamma free, omega+T0 within their conventions/errors)?
    if ch is not None:
        K1L, omL = ch['K1_kms'], ch['omega_rad']
        Te = nss.get('t_periastron_error') or 0.0
        rotations = [0.0, math.pi / 2, math.pi, 3 * math.pi / 2]
        T0_grid = [T0] if Te == 0 else [T0 - Te, T0 - 0.5 * Te, T0, T0 + 0.5 * Te, T0 + Te]
        best_lock = None
        for rot in rotations:
            om = omL + rot
            for T0t in T0_grid:
                def resid_lock(p, om=om, T0t=T0t):
                    return (kepler_rv(t, P, e, T0t, K1L, p[0], om) - rv) / err
                rL = least_squares(resid_lock, [gamma0], bounds=([gamma0 - 80], [gamma0 + 80]), max_nfev=2000)
                c2L = float(np.sum(rL.fun ** 2))
                if best_lock is None or c2L < best_lock['chi2']:
                    best_lock = {'gamma_kms': float(rL.x[0]), 'chi2': c2L,
                                 'omega_deg': math.degrees(om) % 360,
                                 'rotation_deg': math.degrees(rot),
                                 'T0_offset_d': round(T0t - T0, 2)}
        dofL = max(len(ev) - 1, 1)
        # ALSO: free-K1 fit but omega+T0 still locked-ish — i.e. how much does the
        # data WANT to lower K1 below the spectroscopic value? (K1,gamma free at C,H omega)
        best_k1g = None
        for rot in rotations:
            om = omL + rot
            for T0t in T0_grid:
                def resid_k1g(p, om=om, T0t=T0t):
                    return (kepler_rv(t, P, e, T0t, p[0], p[1], om) - rv) / err
                rK = least_squares(resid_k1g, [K1L, gamma0],
                                   bounds=([0, gamma0 - 80], [120, gamma0 + 80]), max_nfev=2000)
                c2K = float(np.sum(rK.fun ** 2))
                if best_k1g is None or c2K < best_k1g['chi2']:
                    best_k1g = {'K1_kms': float(rK.x[0]), 'gamma_kms': float(rK.x[1]),
                                'chi2': c2K, 'omega_deg': math.degrees(om) % 360,
                                'T0_offset_d': round(T0t - T0, 2)}
        out['CH_locked_fit'] = {
            'K1_from_CH_kms': K1L, 'omega_from_CH_deg': ch['omega_deg'],
            'a1sini_AU': ch['a1sini_AU'],
            'f_spec_from_CH_msun': f_spec_msun(K1L, P, e),
            'gamma_only_best': {**best_lock, 'dof': dofL, 'chi2_dof': best_lock['chi2'] / dofL},
            'K1gamma_at_CHomega_best': {**best_k1g, 'dof': max(len(ev) - 2, 1),
                                        'chi2_dof': best_k1g['chi2'] / max(len(ev) - 2, 1)},
            'note': ('gamma_only_best: K1 & omega FIXED from spectroscopic Thiele-Innes C,H, '
                     'only gamma free, omega-convention rotations + T0 within NSS error scanned. '
                     'K1gamma_at_CHomega_best: K1 freed (omega from C,H) to see the data-preferred K1.'),
        }
    return out

# --------------------------------------------------------------------------- #
# M2 posterior via Monte Carlo
# --------------------------------------------------------------------------- #
def m2_posterior(nss, gs, ap, n=200000, seed=1, K1_rvfit=None, K1_rvfit_err=None):
    """MC over M1 (FLAME if available else F3V prior 1.3-1.6) and inclination from
    the astrometric Thiele-Innes (with A,B,F,G errors), propagating C,H,P,parallax.
    Returns M2 percentiles from the spectroscopic mass function f(M)=K1^3 P (1-e^2)^1.5/2piG
    combined with sin i, AND independently the astrometric-photocenter f_phot route,
    AND (if K1_rvfit given) the data-preferred-RV-amplitude route -- the most defensible
    M2 since it uses the OBSERVED archival RV amplitude rather than the noisy C,H."""
    rng = np.random.default_rng(seed)
    P = nss['period']
    e = nss['eccentricity']
    A, B, F, Gt = nss['a_thiele_innes'], nss['b_thiele_innes'], nss['f_thiele_innes'], nss['g_thiele_innes']
    Ae, Be, Fe, Ge = (nss['a_thiele_innes_error'], nss['b_thiele_innes_error'],
                      nss['f_thiele_innes_error'], nss['g_thiele_innes_error'])
    C, H = nss['c_thiele_innes'], nss['h_thiele_innes']
    Ce, He = nss['c_thiele_innes_error'], nss['h_thiele_innes_error']
    plx, plxe = nss['parallax'], nss['parallax_error']
    Pe = nss.get('period_error') or 0.0
    ee = nss.get('eccentricity_error') or 0.0

    # M1 prior
    mflame = ap.get('mass_flame')
    mflame = mflame if isinstance(mflame, (int, float)) else None
    if mflame and mflame > 0.3:
        m1lo = ap.get('mass_flame_lower') or mflame * 0.93
        m1hi = ap.get('mass_flame_upper') or mflame * 1.07
        sig1 = max((m1hi - m1lo) / 2.0, 0.05)
        M1s = rng.normal(mflame, sig1, n)
        m1_src = f'FLAME {mflame:.2f} (+/- {sig1:.2f})'
    else:
        # F3V dwarf prior: 1.30-1.55 Msun, take 1.42 +/- 0.10
        M1s = rng.normal(1.42, 0.10, n)
        m1_src = 'F3V spectral-type prior 1.42 +/- 0.10'
    M1s = np.clip(M1s, 0.5, 3.0)

    Ps = rng.normal(P, Pe, n)
    es = np.clip(rng.normal(e, ee, n), 0.0, 0.95)
    plxs = np.clip(rng.normal(plx, plxe, n), 1e-3, None)

    # --- route 1: spectroscopic K1 (C,H) + astrometric inclination -> M2 ---
    Cs = rng.normal(C, Ce, n)
    Hs = rng.normal(H, He, n)
    a1sini = np.hypot(Cs, Hs)  # AU
    K1 = 2 * np.pi * a1sini * AU_KM / (Ps * 86400.0 * np.sqrt(1 - es ** 2))  # km/s
    fM_spec = (Ps * 86400.0) * (K1 * 1000.0) ** 3 * (1 - es ** 2) ** 1.5 / (2 * np.pi * G_SI) / MSUN

    # inclination from A,B,F,G samples
    As = rng.normal(A, Ae, n); Bs = rng.normal(B, Be, n)
    Fs = rng.normal(F, Fe, n); Gs_ = rng.normal(Gt, Ge, n)
    pp = As ** 2 + Bs ** 2 + Fs ** 2 + Gs_ ** 2
    qq = As * Gs_ - Bs * Fs
    a2 = 0.5 * pp + np.sqrt(np.maximum((0.5 * pp) ** 2 - qq ** 2, 0.0))
    cosi = np.sqrt(np.clip(np.abs(qq) / a2, 0.0, 1.0))
    sini = np.sqrt(np.clip(1 - cosi ** 2, 1e-6, 1.0))

    # solve M2 from f(M) = M2^3 sin^3 i /(M1+M2)^2  => with f_spec and sin i
    # f_spec already includes sin^3 i. So M2^3/(M1+M2)^2 = f_spec / sin^3 i.
    rhs = fM_spec / sini ** 3
    M2_spec = np.array([solve_m2(max(r, 1e-6), m1) for r, m1 in zip(rhs[:n], M1s[:n])])

    # --- route 2: astrometric photocenter f_phot (edge-on-equivalent) ---
    a_phot = np.array([photocentric_a_mas(a, b, f, g) for a, b, f, g in zip(As, Bs, Fs, Gs_)])
    a_AU = a_phot / plxs
    P_yr = Ps / 365.25
    fphot = a_AU ** 3 / P_yr ** 2
    # photocenter f_phot = (M2/(M1+M2))^3 (M1+M2) = M2^3/(M1+M2)^2 ONLY if companion dark
    # (photocenter == primary). Solve M2 assuming dark companion:
    M2_phot = np.array([solve_m2(max(f, 1e-6), m1) for f, m1 in zip(fphot, M1s)])

    def pct(x):
        x = x[np.isfinite(x)]
        return {'p2.5': float(np.percentile(x, 2.5)), 'p16': float(np.percentile(x, 16)),
                'p50': float(np.percentile(x, 50)), 'p84': float(np.percentile(x, 84)),
                'p97.5': float(np.percentile(x, 97.5)), 'mean': float(np.mean(x))}

    # --- route 3: data-preferred RV-fit K1 + astrometric inclination -> M2 ---
    res3 = {}
    if K1_rvfit is not None:
        K1e = K1_rvfit_err if (K1_rvfit_err and K1_rvfit_err > 0) else max(0.1 * K1_rvfit, 0.5)
        K1d = np.clip(rng.normal(K1_rvfit, K1e, n), 0.1, None)
        fM_d = (Ps * 86400.0) * (K1d * 1000.0) ** 3 * (1 - es ** 2) ** 1.5 / (2 * np.pi * G_SI) / MSUN
        rhs_d = fM_d / sini ** 3
        M2_d = np.array([solve_m2(max(r, 1e-6), m1) for r, m1 in zip(rhs_d, M1s)])
        res3 = {
            'K1_rvfit_used_kms': K1_rvfit, 'K1_rvfit_err_used': K1e,
            'f_spec_rvfit_msun': pct(fM_d),
            'M2_rvfit_route_msun': pct(M2_d),
            'P_above_1.4Msun_rvfit': float(np.mean(M2_d > 1.4)),
            'P_below_1.1Msun_rvfit': float(np.mean(M2_d < 1.1)),
            'P_in_NS_window_1.1_2.5_rvfit': float(np.mean((M2_d > 1.1) & (M2_d < 2.5))),
            'P_below_WD_1.0_rvfit': float(np.mean(M2_d < 1.0)),
        }

    # AMRF distribution
    amrf_s = (a_phot / plxs) * M1s ** (-1.0 / 3.0) * P_yr ** (-2.0 / 3.0)

    return {
        'M1_prior': m1_src,
        'incl_deg': pct(np.degrees(np.arccos(cosi))),
        'sini': pct(sini),
        'K1_spec_from_CH_kms': pct(K1),
        'f_spec_msun': pct(fM_spec),
        'f_phot_msun': pct(fphot),
        'M2_spec_route_msun': pct(M2_spec),
        'M2_phot_route_msun': pct(M2_phot),
        'AMRF': pct(amrf_s),
        'P_below_1.1Msun_spec': float(np.mean(M2_spec < 1.1)),
        'P_above_1.4Msun_spec': float(np.mean(M2_spec > 1.4)),
        'P_in_NS_window_1.1_2.5_spec': float(np.mean((M2_spec > 1.1) & (M2_spec < 2.5))),
        'P_above_1.4Msun_phot': float(np.mean(M2_phot > 1.4)),
        'P_in_NS_window_1.1_2.5_phot': float(np.mean((M2_phot > 1.1) & (M2_phot < 2.5))),
        'rvfit_route': res3,
    }

# --------------------------------------------------------------------------- #
# Primary archival epochs (from the triage census, re-stated explicitly)
# --------------------------------------------------------------------------- #
PRIMARY_EPOCHS = [
    (55876.064999999944, 17.605, 0.07322, 'APOGEE'),
    (56447.445999999996, 27.626, 0.07106, 'APOGEE'),
    (56850.42599999998, -2.319, 0.07095, 'APOGEE'),
    (56918.0, -15.609999656677246, 4.71, 'LAMOST_LRS'),
]

# --------------------------------------------------------------------------- #
def run_primary():
    print('=' * 70, '\nPRIMARY', PRIMARY, '\n', '=' * 70)
    rec = {'source_id': PRIMARY}
    nss = gaia_nss(PRIMARY); rec['nss'] = nss
    gs = gaia_source(PRIMARY); rec['gaia_source'] = gs
    ap = gaia_ap(PRIMARY); rec['astrophysical_parameters'] = ap
    print(f"  NSS: type={nss['nss_solution_type']} P={nss['period']:.2f} e={nss['eccentricity']:.3f} "
          f"sig={nss['significance']:.1f} gof={nss['goodness_of_fit']:.2f} "
          f"rv_n={nss['rv_n_obs_primary']:.0f}")
    print(f"  C,H = {nss['c_thiele_innes']:.4f}+/-{nss['c_thiele_innes_error']:.4f}, "
          f"{nss['h_thiele_innes']:.4f}+/-{nss['h_thiele_innes_error']:.4f} AU")
    print(f"  gaia_source: ruwe={gs['ruwe']:.2f} ipd_multi={gs.get('ipd_frac_multi_peak')} "
          f"rv_ampl_robust={gs.get('rv_amplitude_robust')} bp_rp={gs.get('bp_rp')}")
    print(f"  AP: mass_flame={ap.get('mass_flame')} teff={ap.get('teff_gspphot')} "
          f"logg={ap.get('logg_gspphot')} dist={ap.get('distance_gspphot')}")

    # C,H-locked K1
    ch = K1_from_CH(nss['c_thiele_innes'], nss['h_thiele_innes'], nss['period'], nss['eccentricity'])
    rec['CH_locked_K1'] = ch
    print(f"  >> C,H-LOCKED K1 = {ch['K1_kms']:.2f} km/s, a1sini={ch['a1sini_AU']:.3f} AU, "
          f"omega={ch['omega_deg']:.1f} deg; f_spec(C,H)={f_spec_msun(ch['K1_kms'], nss['period'], nss['eccentricity']):.3f} Msun")

    # RV fits
    fits = rv_fits(PRIMARY_EPOCHS, nss); rec['rv_fits'] = fits
    print('  RV FITS:')
    print('    phases:', fits['phases'])
    print('    constant_null:', {k: round(v, 4) if isinstance(v, float) else v for k, v in fits['constant_null'].items()})
    ff = fits['free_fit']
    print(f"    free_fit: K1={ff['K1_kms']:.2f}+/-{ff['K1_sigma_kms']} ({ff['K1_signif']}) "
          f"chi2/dof={ff['chi2_dof']} dof={ff['dof']} [{ff['dof_note']}]")
    cl = fits.get('CH_locked_fit', {})
    if cl:
        go = cl['gamma_only_best']; kg = cl['K1gamma_at_CHomega_best']
        print(f"    CH_locked (K1={cl['K1_from_CH_kms']:.2f} fixed, gamma-only): chi2={go['chi2']:.1f} "
              f"chi2/dof={go['chi2_dof']:.1f} (omega={go['omega_deg']:.0f}, T0off={go['T0_offset_d']}d)")
        print(f"    K1 freed at C,H-omega: K1={kg['K1_kms']:.2f} chi2={kg['chi2']:.1f} chi2/dof={kg['chi2_dof']:.1f}")

    # M2 posterior -- pass the data-preferred RV-fit K1 (most defensible amplitude)
    K1rv = fits['free_fit']['K1_kms']; K1rv_e = fits['free_fit']['K1_sigma_kms']
    post = m2_posterior(nss, gs, ap, K1_rvfit=K1rv, K1_rvfit_err=K1rv_e); rec['M2_posterior'] = post
    print('  M2 POSTERIOR (MC):')
    print(f"    M1 prior: {post['M1_prior']}")
    print(f"    incl = {post['incl_deg']['p50']:.1f} [{post['incl_deg']['p16']:.1f},{post['incl_deg']['p84']:.1f}] deg")
    print(f"    K1(C,H) = {post['K1_spec_from_CH_kms']['p50']:.1f} [{post['K1_spec_from_CH_kms']['p16']:.1f},{post['K1_spec_from_CH_kms']['p84']:.1f}] km/s")
    print(f"    M2 (C,H spec route) = {post['M2_spec_route_msun']['p50']:.2f} "
          f"[{post['M2_spec_route_msun']['p16']:.2f},{post['M2_spec_route_msun']['p84']:.2f}] Msun "
          f"| P(M2>1.4)={post['P_above_1.4Msun_spec']:.2f}")
    print(f"    M2 (phot/dark route) = {post['M2_phot_route_msun']['p50']:.2f} "
          f"[{post['M2_phot_route_msun']['p16']:.2f},{post['M2_phot_route_msun']['p84']:.2f}] Msun "
          f"| P(M2>1.4)={post['P_above_1.4Msun_phot']:.2f}")
    rv3 = post.get('rvfit_route', {})
    if rv3:
        m = rv3['M2_rvfit_route_msun']
        print(f"    M2 (RV-fit K1={K1rv:.1f} route) = {m['p50']:.2f} [{m['p16']:.2f},{m['p84']:.2f}] Msun "
              f"| P(M2>1.4)={rv3['P_above_1.4Msun_rvfit']:.2f} P(<1.0 WD)={rv3['P_below_WD_1.0_rvfit']:.2f}")

    # AMRF dark-companion test
    _mf = ap.get('mass_flame'); _mf = _mf if isinstance(_mf, (int, float)) else None
    M1_use = _mf if (_mf and _mf > 0.3) else 1.42
    a_phot = photocentric_a_mas(nss['a_thiele_innes'], nss['b_thiele_innes'],
                                nss['f_thiele_innes'], nss['g_thiele_innes'])
    P_yr = nss['period'] / 365.25
    A_obs = amrf(a_phot, nss['parallax'], M1_use, P_yr)
    A_ms_max = amrf_ms_max(M1_use, beta=4.0)
    A_ms_max5 = amrf_ms_max(M1_use, beta=5.0)
    q_dark = q_from_amrf_dark(A_obs) if A_obs else None
    incl = inclination_from_ABFG(nss['a_thiele_innes'], nss['b_thiele_innes'],
                                 nss['f_thiele_innes'], nss['g_thiele_innes'])
    rec['amrf'] = {'a_phot_mas': a_phot, 'A_obs': A_obs, 'A_ms_max_beta4': A_ms_max,
                   'A_ms_max_beta5': A_ms_max5, 'M1_used': M1_use,
                   'q_dark_implied': q_dark,
                   'M2_dark_implied_msun': (q_dark * M1_use if q_dark else None),
                   'dark_required': (A_obs > A_ms_max) if A_obs else None,
                   'incl_from_ABFG': incl}
    print('  AMRF (Shahaf+2019):')
    print(f"    a_phot={a_phot:.3f} mas, A_obs={A_obs:.3f}, A_ms_max(beta=4)={A_ms_max:.3f}, "
          f"(beta=5)={A_ms_max5:.3f}")
    print(f"    dark companion required? {A_obs > A_ms_max}  (q_dark={q_dark:.2f} -> "
          f"M2_dark={q_dark*M1_use:.2f} Msun)")
    print(f"    incl from A,B,F,G = {incl['incl_deg']:.1f} deg (cos i={incl['cos_i']:.3f})")

    # SED second-light check
    rec['sed_check'] = sed_check(gs, ap)
    print('  SED:', rec['sed_check'])

    # SIMBAD + literature
    rec['simbad'] = simbad_otype_bibs(f'Gaia DR3 {PRIMARY}')
    print(f"  SIMBAD: otype={rec['simbad'].get('otype')} sp={rec['simbad'].get('sp_type')} "
          f"n_bibs={rec['simbad'].get('n_bibcodes')}")
    rec['literature'] = lit_crossmatch(gs['ra'], gs['dec'])
    print('  LIT:', {k: v.get('match') for k, v in rec['literature'].items()})
    return rec

def sed_check(gs, ap):
    """Crude SED second-light check. F3V: BP-RP ~ 0.55-0.70, M_G ~ 2.8-3.3.
    A bright luminous companion (e.g. another F/G star) would (a) redden/brighten,
    (b) push the photocenter wobble down (S>0 reduces AMRF), (c) show ipd_multi_peak."""
    bp_rp = gs.get('bp_rp')
    G = gs.get('phot_g_mean_mag')
    plx = gs.get('parallax')
    M_G = (G + 5 * math.log10(plx / 1000.0) + 5) if (G and plx and plx > 0) else None
    teff = ap.get('teff_gspphot')
    return {
        'bp_rp': bp_rp, 'G': G, 'abs_G': M_G, 'teff_gspphot': teff,
        'expected_F3V_bp_rp': '0.55-0.70', 'expected_F3V_absG': '2.6-3.2',
        'ipd_frac_multi_peak': gs.get('ipd_frac_multi_peak'),
        'astrometric_excess_noise_sig': gs.get('astrometric_excess_noise_sig'),
        'phot_variable_flag': gs.get('phot_variable_flag'),
        'note': ('single luminous F3V consistent if bp_rp & absG match and '
                 'ipd_frac_multi_peak is low (no resolved second source)'),
    }

# --------------------------------------------------------------------------- #
# Sanity checks
# --------------------------------------------------------------------------- #
def sanity_hd264291():
    """3378588057203660160: re-check whether the 50 LAMOST MRS epochs are single-phase.
    Pull the actual MJDs from the triage census and compute phase coverage with the
    NSS orbit; test K1 constrainability."""
    sid = 3378588057203660160
    print('\n', '=' * 70, '\nSANITY: HD 264291', sid, '\n', '=' * 70)
    nss = gaia_nss(sid)
    d = json.load(open('/tmp/ns_pool_triage_results.json'))
    cen = d[str(sid)]['census']
    eps = []
    for arch in ('LAMOST_LRS', 'LAMOST_MRS', 'APOGEE_visits', 'RAVE', 'GALAH_DR3'):
        for ep in cen.get(arch, {}).get('epochs', []):
            if ep[0] is not None:
                eps.append((ep[0], ep[1], ep[2], arch))
    P = nss['period']; e = nss['eccentricity']
    T0 = nss['t_periastron'] + GAIA_REF_JD - MJD_OFFSET
    mjds = sorted(set(round(x[0], 1) for x in eps))
    phs = sorted(set(round(phase_of(m, P, T0), 3) for m in [x[0] for x in eps]))
    # distinct phase bins (width 0.05)
    bins = set(round(p / 0.05) for p in phs)
    fits = rv_fits(eps, nss, err_floor=0.3, apogee_floor=0.3)
    rec = {'source_id': sid, 'P_d': P, 'e': e, 'sig': nss['significance'], 'ruwe': nss.get('ruwe'),
           'n_epochs': len(eps), 'mjd_min': min(mjds), 'mjd_max': max(mjds),
           'mjd_baseline_d': max(mjds) - min(mjds), 'n_cycles_covered': (max(mjds) - min(mjds)) / P,
           'distinct_mjd_clusters': mjds, 'phase_values': phs,
           'n_distinct_phase_bins_0.05': len(bins),
           'phase_min': min(phs), 'phase_max': max(phs), 'rv_fits': fits}
    print(f"  P={P:.1f}d e={e:.2f} sig={nss['significance']:.1f}; {len(eps)} epochs over "
          f"MJD {min(mjds):.0f}-{max(mjds):.0f} = {max(mjds)-min(mjds):.0f}d ({(max(mjds)-min(mjds))/P:.2f} cycles)")
    print(f"  phase range {min(phs):.3f}-{max(phs):.3f}, distinct 0.05-bins={len(bins)}")
    print(f"  free_fit K1={fits['free_fit']['K1_kms']:.2f}+/-{fits['free_fit']['K1_sigma_kms']} "
          f"chi2/dof={fits['free_fit']['chi2_dof']:.2f}")
    print(f"  CH_locked K1={fits.get('CH_locked_fit',{}).get('K1_from_CH_kms')}")
    return rec

def sanity_refuted(sid):
    print('\n', '=' * 70, '\nSANITY (REFUTED?):', sid, '\n', '=' * 70)
    nss = gaia_nss(sid)
    d = json.load(open('/tmp/ns_pool_triage_results.json'))
    cen = d[str(sid)]['census']
    eps = []
    for arch in ('LAMOST_LRS', 'LAMOST_MRS', 'APOGEE_visits', 'RAVE', 'GALAH_DR3'):
        for ep in cen.get(arch, {}).get('epochs', []):
            if ep[0] is not None:
                eps.append((ep[0], ep[1], ep[2], arch))
    ch = K1_from_CH(nss.get('c_thiele_innes'), nss.get('h_thiele_innes'), nss['period'], nss['eccentricity'])
    fits = rv_fits(eps, nss, err_floor=0.3, apogee_floor=0.3)
    # astrometric f_phot
    a_phot = photocentric_a_mas(nss['a_thiele_innes'], nss['b_thiele_innes'],
                                nss['f_thiele_innes'], nss['g_thiele_innes'])
    P_yr = nss['period'] / 365.25
    fphot = (a_phot / nss['parallax']) ** 3 / P_yr ** 2 if a_phot else None
    rec = {'source_id': sid, 'P_d': nss['period'], 'e': nss['eccentricity'],
           'sig': nss['significance'], 'ruwe': nss.get('ruwe'),
           'CH_locked_K1_kms': ch['K1_kms'] if ch else None,
           'f_spec_from_CH_msun': f_spec_msun(ch['K1_kms'], nss['period'], nss['eccentricity']) if ch else None,
           'f_phot_msun': fphot,
           'free_fit_K1_kms': fits['free_fit']['K1_kms'],
           'free_fit_f_spec_msun': fits['free_fit']['f_spec_msun'],
           'free_fit_chi2_dof': fits['free_fit']['chi2_dof'],
           'phases': fits['phases'], 'rv_span_kms': fits['rv_span_kms'],
           'n_epochs': fits['n_epochs']}
    rec['ratio_freefit_fspec_over_fphot'] = (rec['free_fit_f_spec_msun'] / fphot) if fphot else None
    rec['ratio_CHlocked_fspec_over_fphot'] = (rec['f_spec_from_CH_msun'] / fphot) if (fphot and ch) else None
    print(f"  P={nss['period']:.0f}d e={nss['eccentricity']:.2f} sig={nss['significance']:.0f} ruwe={nss.get('ruwe')}")
    print(f"  free-fit K1={rec['free_fit_K1_kms']:.1f} -> f_spec={rec['free_fit_f_spec_msun']:.1f}; "
          f"f_phot={fphot:.3f}; ratio={rec['ratio_freefit_fspec_over_fphot']:.0f}")
    if rec['CH_locked_K1_kms'] is not None:
        print(f"  C,H-locked K1={rec['CH_locked_K1_kms']:.1f} -> f_spec(C,H)={rec['f_spec_from_CH_msun']:.2f}; "
              f"ratio_CH={rec['ratio_CHlocked_fspec_over_fphot']:.1f}")
    else:
        print(f"  C,H-locked K1=N/A (no spectroscopic Thiele-Innes -> {nss['nss_solution_type']}, not AstroSpectroSB1)")
    print(f"  RV span={rec['rv_span_kms']:.1f} km/s over {rec['n_epochs']} epochs, phases={rec['phases']}")
    return rec

# --------------------------------------------------------------------------- #
# Novelty pass
# --------------------------------------------------------------------------- #
def novelty(sid):
    print(f'\n  NOVELTY {sid} ...', flush=True)
    rec = {'source_id': sid}
    sb = simbad_otype_bibs(f'Gaia DR3 {sid}')
    rec['simbad'] = sb
    gs = gaia_source(sid)
    rec['ra'] = gs['ra']; rec['dec'] = gs['dec']
    rec['literature'] = lit_crossmatch(gs['ra'], gs['dec'])
    print(f"    otype={sb.get('otype')} sp={sb.get('sp_type')} main_id={sb.get('main_id')} "
          f"n_bibs={sb.get('n_bibcodes')} lit={ {k: v.get('match') for k, v in rec['literature'].items()} }")
    if sb.get('bibcodes'):
        for b in sb['bibcodes']:
            print('       ', b['bibcode'], '|', b['title'][:65])
    return rec

# --------------------------------------------------------------------------- #
def main():
    out = {}
    out['primary'] = run_primary()
    json.dump(out, open('/tmp/ns2127900_primary.json', 'w'), indent=1, default=str)

    out['sanity'] = {}
    out['sanity']['hd264291_3378588057203660160'] = sanity_hd264291()
    out['sanity']['refuted_2129927539681151872'] = sanity_refuted(2129927539681151872)
    out['sanity']['refuted_1379150557507688960'] = sanity_refuted(1379150557507688960)
    json.dump(out['sanity'], open('/tmp/ns2127900_sanity.json', 'w'), indent=1, default=str)

    out['novelty'] = {}
    for sid in (5640825637852070016, 6419437207856851584, 1714530637958169600, 823243942431149568):
        out['novelty'][str(sid)] = novelty(sid)
    json.dump(out['novelty'], open('/tmp/ns2127900_novelty.json', 'w'), indent=1, default=str)

    json.dump(out, open('/tmp/ns2127900_all.json', 'w'), indent=1, default=str)
    print('\nSaved /tmp/ns2127900_{primary,sanity,novelty,all}.json')
    return out

if __name__ == '__main__':
    main()
