#!/usr/bin/env python3
"""Dark-vs-luminous companion vetting of the PMa-corroborated accelerating source
Gaia DR3 4627264384502501248 = HD 21940 (2026-05-31).

Caller context: HGCA chi2=413.2, Kervella snrPMaH2G2=17.34, M2_median (accel grid /
Kervella M2_5AU MC) = 2.413 Msun, SIMBAD HD 21940, known_multiple=true. This is a
PMa / HGCA *acceleration* source. Per METHODOLOGY.md the Acceleration-NSS extension
is the deferred channel: M2 from a PM-acceleration is PERIOD-DEGENERATE, so the
"M2_median" is the median of M2(P) over a log-P 3-100 yr grid -- a GRID ARTEFACT,
not a measured mass (cf. HD 182379 sibling: caller M2_median=2.637 collapsed to
~0.46 Msun once the real SB1 orbit + SED were checked; HD 217209 likewise).

The decisive question is the SED. A 2-5 Msun main-sequence companion is an
EARLY-A / LATE-B star (Teff ~ 8500-13000 K, L ~ 20-150 Lsun) and would be
*conspicuous* unless the primary itself is far more luminous. So:

  (1) SED 2-component fit (GALEX/Gaia/2MASS/WISE): fit a single-star primary BB
      to the optical+IR anchors; then test whether adding a luminous A/B/F/G/K/M
      MS companion (grid spanning ~0.2-3.4 Msun) is REQUIRED or EXCLUDED, band by
      band with full errors. (HD157033 precedent: 7/8 Pile-A HGCA candidates were
      demoted as Kervella H2G2 *luminous* stellar companions at the 5-AU ref.)
  (2) Resolved / wide companion: Gaia DR3 cone (matching parallax + PM), WDS.
  (3) Gaia non_single_star / RVS SB2 (rv_amplitude_robust, vbroad, ipd) /
      ipd_frac_multi_peak / RUWE / luminous-secondary flag pattern; ALSO check for
      a Gaia NSS orbit (nss_two_body_orbit) or nss_acceleration_astro row -- a real
      orbit PINS the period and collapses the M2(P) degeneracy (decisive, as for HD182379).
  (4) Is Kervella M2_5AU=2.413 + HGCA chi2=413.2 consistent with a *luminous*
      stellar companion, or does a DARK companion remain required? CRITICAL UNIT
      CAVEAT: Kervella's M2-Xau columns are in JUPITER masses (HD182379: M2-5au=293
      MJup = 0.28 Msun). And M2(P) is mapped explicitly from the measured acceleration.

Classify companion_class = luminous_stellar / dark_candidate / ambiguous.

Env: /Users/legbatterij/claude_projects/ostinato/.venv/bin/python (no pip-install)
Outputs: /tmp/hd21940_pma.json , /tmp/hd21940_pma_report.md
Adapted from scripts/hd182379_pma_darkluminous_2026_05_31.py (same canonical SED BB
machinery), with the v3 acceleration M2(P) inversion from
scripts/streaming/v3_acceleration/acceleration_inversion.py.
"""
from __future__ import annotations
import warnings, math, json, sys
warnings.filterwarnings('ignore')
import numpy as np
from scipy.optimize import minimize_scalar, brentq

from astroquery.gaia import Gaia
from astroquery.vizier import Vizier
from astroquery.simbad import Simbad
from astropy.coordinates import SkyCoord
import astropy.units as u
import threading as _th

sys.path.insert(0, '/Users/legbatterij/claude_projects/gaia-recovered-2026-05-27/scripts/streaming/v3_acceleration')
try:
    from acceleration_inversion import (M2_from_acceleration, M2_range,
                                        acceleration_magnitude,
                                        acceleration_magnitude_error)
    _HAVE_ACCEL = True
except Exception as _e:
    _HAVE_ACCEL = False
    print(f"  [warn: could not import acceleration_inversion: {_e}]", file=sys.stderr)

# ------------------------------------------------------------------ constants
H_PLANCK = 6.62607015e-34
C_LIGHT  = 2.99792458e8
K_BOLTZ  = 1.380649e-23
SIGMA_SB = 5.670374419e-8
RSUN_M   = 6.957e8
LSUN_W   = 3.828e26
PC_M     = 3.0856775815e16
ZP_AB    = 3631.0
G_SI     = 6.6743e-11
MSUN     = 1.98892e30
MJUP_MSUN = 1.0 / 1047.57   # Jupiter mass in solar masses

SID = 4627264384502501248
HD_NAME = 'HD 21940'
CALLER = dict(HGCA_chi2=413.2, snrPMa=17.34, M2_median=2.413, known_multiple=True)

# ------------------------------------------------------------------ net helper
def _with_timeout(fn, secs, default):
    box = {}
    def runner():
        try: box['res'] = fn()
        except Exception as e: box['err'] = e
    th = _th.Thread(target=runner, daemon=True); th.start(); th.join(secs)
    if 'res' in box: return box['res']
    why = type(box['err']).__name__ if 'err' in box else 'Timeout'
    print(f"  [net timeout/err after {secs}s: {why}]", file=sys.stderr)
    return default

def _flt(v):
    try:
        f = float(v)
        return None if math.isnan(f) else f
    except (TypeError, ValueError):
        return None

def _tab_to_dict(t):
    out = {}
    for c in t.colnames:
        if c in ('corr_vec', 'bit_index'):
            continue
        v = t[c][0]
        fv = _flt(v)
        if fv is not None:
            out[c] = fv
        else:
            try: masked = bool(np.ma.is_masked(v))
            except Exception: masked = False
            out[c] = None if masked else str(v)
    return out

# ------------------------------------------------------------------ Gaia fetch
def gaia_source(sid):
    cols = ('source_id, ra, dec, parallax, parallax_error, parallax_over_error, '
            'pmra, pmdec, pmra_error, pmdec_error, ruwe, '
            'phot_g_mean_mag, phot_bp_mean_mag, phot_rp_mean_mag, bp_rp, g_rp, bp_g, '
            'radial_velocity, radial_velocity_error, rv_amplitude_robust, '
            'rv_nb_transits, rv_expected_sig_to_noise, rv_renormalised_gof, '
            'rv_template_teff, rv_template_logg, rv_template_fe_h, vbroad, vbroad_error, '
            'ipd_frac_multi_peak, ipd_frac_odd_win, ipd_gof_harmonic_amplitude, '
            'astrometric_excess_noise, astrometric_excess_noise_sig, '
            'astrometric_gof_al, astrometric_chi2_al, '
            'visibility_periods_used, astrometric_n_good_obs_al, '
            'astrometric_params_solved, '
            'duplicated_source, non_single_star, phot_variable_flag, '
            'phot_bp_rp_excess_factor, l, b, '
            'teff_gspphot, logg_gspphot, mh_gspphot, distance_gspphot, '
            'ag_gspphot, ebpminrp_gspphot')
    def go():
        return Gaia.launch_job(f'SELECT {cols} FROM gaiadr3.gaia_source WHERE source_id={sid}').get_results()
    t = _with_timeout(go, 90, None)
    return _tab_to_dict(t) if (t is not None and len(t)) else {}

def gaia_ap(sid):
    def go():
        return Gaia.launch_job(
            'SELECT source_id, teff_gspphot, logg_gspphot, mh_gspphot, '
            'teff_gspspec, logg_gspspec, mh_gspspec, '
            'mass_flame, radius_flame, lum_flame, age_flame, evolstage_flame, '
            'mass_flame_lower, mass_flame_upper, radius_flame_lower, radius_flame_upper, '
            'lum_flame_lower, lum_flame_upper, '
            'teff_gspphot_lower, teff_gspphot_upper, '
            'logg_gspphot_lower, logg_gspphot_upper, '
            'spectraltype_esphs, libname_gspphot, ag_gspphot '
            f'FROM gaiadr3.astrophysical_parameters WHERE source_id={sid}').get_results()
    t = _with_timeout(go, 90, None)
    return _tab_to_dict(t) if (t is not None and len(t)) else {}

def gaia_ap_supp(sid):
    def go():
        return Gaia.launch_job(
            'SELECT source_id, logg_gspspec_ann, teff_gspspec_ann, mh_gspspec_ann '
            f'FROM gaiadr3.astrophysical_parameters_supp WHERE source_id={sid}').get_results()
    t = _with_timeout(go, 60, None)
    return _tab_to_dict(t) if (t is not None and len(t)) else {}

def gaia_nss(sid):
    def go():
        return Gaia.launch_job(f'SELECT * FROM gaiadr3.nss_two_body_orbit WHERE source_id={sid}').get_results()
    t = _with_timeout(go, 60, None)
    return _tab_to_dict(t) if (t is not None and len(t)) else None

def gaia_accel(sid):
    """nss_acceleration_astro: PM-acceleration solution (Acceleration7/9), period unconstrained."""
    def go():
        return Gaia.launch_job(f'SELECT * FROM gaiadr3.nss_acceleration_astro WHERE source_id={sid}').get_results()
    t = _with_timeout(go, 60, None)
    return _tab_to_dict(t) if (t is not None and len(t)) else None

def gaia_neighbours(ra, dec, plx, pmra, pmdec, radius_arcsec=30.0):
    """Cone search for resolved companions sharing parallax + PM (common proper motion)."""
    rad_deg = radius_arcsec / 3600.0
    cols = ('source_id, ra, dec, parallax, parallax_error, pmra, pmdec, '
            'phot_g_mean_mag, bp_rp, ruwe')
    def go():
        q = (f"SELECT {cols}, DISTANCE(POINT({ra},{dec}), POINT(ra,dec))*3600 AS sep_arcsec "
             f"FROM gaiadr3.gaia_source "
             f"WHERE 1=CONTAINS(POINT(ra,dec), CIRCLE({ra},{dec},{rad_deg})) "
             f"ORDER BY sep_arcsec ASC")
        return Gaia.launch_job(q).get_results()
    t = _with_timeout(go, 90, None)
    if t is None:
        return {'_err': 'cone search failed/timeout'}
    rows = []
    for i in range(len(t)):
        sidi = int(t['source_id'][i])
        sep = _flt(t['sep_arcsec'][i])
        plxi = _flt(t['parallax'][i]); pmrai = _flt(t['pmra'][i]); pmdeci = _flt(t['pmdec'][i])
        row = dict(source_id=sidi, sep_arcsec=(round(sep, 3) if sep is not None else None),
                   parallax=plxi, pmra=pmrai, pmdec=pmdeci,
                   G=_flt(t['phot_g_mean_mag'][i]), bp_rp=_flt(t['bp_rp'][i]),
                   ruwe=_flt(t['ruwe'][i]), is_target=(sidi == SID))
        if not row['is_target'] and plxi is not None and plx is not None:
            dplx = abs(plxi - plx)
            dpm = (math.hypot((pmrai or 0) - (pmra or 0), (pmdeci or 0) - (pmdec or 0))
                   if (pmrai is not None and pmdeci is not None) else None)
            row['dplx_mas'] = round(dplx, 4)
            row['dpm_masyr'] = (round(dpm, 4) if dpm is not None else None)
            row['cpm_candidate'] = bool(dplx < max(0.5, 5.0) and (dpm is not None and dpm < 5.0))
        rows.append(row)
    return {'n_within': len(rows), 'rows': rows[:25]}

# ------------------------------------------------------------------ photometry
BANDS = {
    'GALEX_FUV': (1549.0, 'AB', 0.0),
    'GALEX_NUV': (2304.7, 'AB', 0.0),
    'Gaia_BP'  : (5035.8, 'AB', 0.0),
    'Gaia_G'   : (5822.4, 'AB', 0.0),
    'Gaia_RP'  : (7619.9, 'AB', 0.0),
    '2MASS_J'  : (12350.0, 'Vega', 0.910),
    '2MASS_H'  : (16620.0, 'Vega', 1.390),
    '2MASS_K'  : (21590.0, 'Vega', 1.850),
    'WISE_W1'  : (33526.0, 'Vega', 2.699),
    'WISE_W2'  : (46028.0, 'Vega', 3.339),
    'WISE_W3'  : (115608.0, 'Vega', 5.174),
    'WISE_W4'  : (220883.0, 'Vega', 6.620),
}
GAIA_AB_OFF = {'Gaia_G': 0.105, 'Gaia_BP': 0.0292, 'Gaia_RP': 0.3542}

ALAM_AV = {
    'GALEX_FUV': 2.61, 'GALEX_NUV': 2.74,
    'Gaia_BP': 1.06, 'Gaia_G': 0.83, 'Gaia_RP': 0.63,
    '2MASS_J': 0.29, '2MASS_H': 0.18, '2MASS_K': 0.12,
    'WISE_W1': 0.071, 'WISE_W2': 0.055, 'WISE_W3': 0.058, 'WISE_W4': 0.020,
}

def fetch_photometry(ra, dec, gs):
    co = SkyCoord(ra, dec, unit='deg')
    out = {}; prov = {}
    def vquery(cat, rad):
        v = Vizier(columns=['**'], row_limit=10)
        return _with_timeout(lambda: v.query_region(co, radius=rad * u.arcsec, catalog=cat), 60, None)

    for b, key in (('Gaia_G', 'phot_g_mean_mag'), ('Gaia_BP', 'phot_bp_mean_mag'),
                   ('Gaia_RP', 'phot_rp_mean_mag')):
        m = gs.get(key)
        if isinstance(m, (int, float)):
            out[b] = dict(mag=m + GAIA_AB_OFF[b], err=0.01, system='AB', det='det', src='Gaia DR3')
    prov['Gaia'] = 'gaia_source phot_{g,bp,rp}_mean_mag'

    r = vquery('II/335/galex_ais', 5)
    if r and len(r):
        t = r[0]; i = int(np.argmin(t['_r']))
        for b, col in (('GALEX_FUV', 'FUVmag'), ('GALEX_NUV', 'NUVmag')):
            m = _flt(t[col][i]); e = _flt(t['e_' + col][i])
            if m is not None:
                out[b] = dict(mag=m, err=(e or 0.15), system='AB', det='det', src='II/335 GALEX-AIS')
        prov['GALEX'] = f"II/335 sep={float(t['_r'][i]):.2f}\""
    else:
        prov['GALEX'] = 'no GALEX-AIS match within 5\" (no UV detection)'

    r = vquery('II/246/out', 5)
    if r and len(r):
        t = r[0]; i = int(np.argmin(t['_r']))
        qflg = str(t['Qflg'][i])
        for k, (b, col) in enumerate((('2MASS_J', 'Jmag'), ('2MASS_H', 'Hmag'), ('2MASS_K', 'Kmag'))):
            m = _flt(t[col][i]); e = _flt(t['e_' + col][i])
            q = qflg[k] if k < len(qflg) else 'U'
            if m is not None:
                det = 'det' if (q in 'ABC' and e is not None) else 'UL'
                out[b] = dict(mag=m, err=(e if e is not None else 0.30),
                              system='Vega', det=det, src=f'II/246 2MASS (Qflg={q})')
        prov['2MASS'] = f"II/246 Qflg={qflg} sep={float(t['_r'][i]):.2f}\""

    r = vquery('II/328/allwise', 8)
    if r and len(r):
        t = r[0]; i = int(np.argmin(t['_r']))
        qph = str(t['qph'][i]); ccf = str(t['ccf'][i])
        for k, (b, col) in enumerate((('WISE_W1', 'W1mag'), ('WISE_W2', 'W2mag'),
                                      ('WISE_W3', 'W3mag'), ('WISE_W4', 'W4mag'))):
            m = _flt(t[col][i]); e = _flt(t['e_' + col][i])
            q = qph[k] if k < len(qph) else 'U'
            if m is not None:
                det = 'det' if (q in 'ABC' and e is not None) else 'UL'
                out[b] = dict(mag=m, err=(e if e is not None else 0.30),
                              system='Vega', det=det, src=f'II/328 AllWISE (qph={q})')
        prov['AllWISE'] = f"II/328 qph={qph} ccf={ccf} sep={float(t['_r'][i]):.2f}\""
    return out, prov

def fetch_kervella(ra, dec):
    """Kervella+2022 H2G2 PMa catalog (J/A+A/657/A7). NB: M2-Xau columns are in JUPITER masses."""
    co = SkyCoord(ra, dec, unit='deg')
    v = Vizier(columns=['**'], row_limit=5)
    r = _with_timeout(lambda: v.query_region(co, radius=10 * u.arcsec, catalog='J/A+A/657/A7'), 60, None)
    if not r or len(r) == 0:
        return {'match': False}
    t = r[0]; i = int(np.argmin(t['_r']))
    out = {'match': True, 'sep_arcsec': round(float(t['_r'][i]), 2)}
    for c in t.colnames:
        out[c] = _flt(t[c][i]) if _flt(t[c][i]) is not None else (
            None if np.ma.is_masked(t[c][i]) else str(t[c][i]))
    # derived Msun versions of the MJup mass columns
    for col in ('M2-3', 'M2-5', 'M2-10', 'M2-1'):
        if out.get(col) is not None and isinstance(out[col], (int, float)):
            out[col + '_Msun'] = round(out[col] * MJUP_MSUN, 4)
    return out

def fetch_hgca(ra, dec):
    """Brandt 2021 HGCA (J/ApJS/254/42) chi2 acceleration."""
    co = SkyCoord(ra, dec, unit='deg')
    v = Vizier(columns=['**'], row_limit=5)
    for cat in ('J/ApJS/254/42/hgca', 'J/ApJS/254/42'):
        r = _with_timeout(lambda: v.query_region(co, radius=10 * u.arcsec, catalog=cat), 60, None)
        if r and len(r):
            t = r[0]; i = int(np.argmin(t['_r']))
            out = {'match': True, 'catalog': cat, 'sep_arcsec': round(float(t['_r'][i]), 2)}
            for c in t.colnames:
                out[c] = _flt(t[c][i]) if _flt(t[c][i]) is not None else (
                    None if np.ma.is_masked(t[c][i]) else str(t[c][i]))
            return out
    return {'match': False}

def fetch_wds(ra, dec):
    co = SkyCoord(ra, dec, unit='deg')
    v = Vizier(columns=['**'], row_limit=10)
    r = _with_timeout(lambda: v.query_region(co, radius=15 * u.arcsec, catalog='B/wds/wds'), 60, None)
    if not r or len(r) == 0:
        return {'match': False}
    t = r[0]
    rows = []
    for i in range(min(len(t), 8)):
        rows.append({c: (_flt(t[c][i]) if _flt(t[c][i]) is not None else str(t[c][i]))
                     for c in ('WDS', 'Disc', 'Comp', 'Obs1', 'Obs2', 'sep1', 'sep2',
                               'pa1', 'pa2', 'mag1', 'mag2') if c in t.colnames})
    return {'match': True, 'n_rows': len(t), 'rows': rows}

def simbad_otype_bibs(gaia_id_str, hd_name=None):
    s = Simbad()
    for flds in (('otype', 'ids', 'sp_type', 'plx_value', 'V', 'rvz_radvel'),
                 ('otype', 'ids', 'sp_type', 'plx_value'), ('otype', 'ids', 'sp_type')):
        try:
            s.add_votable_fields(*flds); break
        except Exception:
            s = Simbad(); continue
    out = {'query': gaia_id_str}
    target = hd_name or gaia_id_str
    try:
        r = s.query_object(target)
        if r is None or len(r) == 0:
            r = s.query_object(gaia_id_str)
        if r is not None and len(r):
            cn = r.colnames
            out['main_id'] = str(r['main_id'][0]) if 'main_id' in cn else None
            out['otype'] = str(r['otype'][0]) if 'otype' in cn else None
            out['sp_type'] = str(r['sp_type'][0]) if 'sp_type' in cn else None
            out['ids'] = str(r['ids'][0]) if 'ids' in cn else None
            out['V'] = _flt(r['V'][0]) if 'V' in cn else None
            out['plx_value'] = _flt(r['plx_value'][0]) if 'plx_value' in cn else None
    except Exception as e:
        out['_obj_err'] = f'{type(e).__name__}: {e}'
    for qid in (hd_name, gaia_id_str):
        if not qid:
            continue
        q = (f"SELECT b.bibcode, b.journal, b.title FROM basic AS ba "
             f"JOIN ident AS i ON i.oidref = ba.oid "
             f"JOIN has_ref AS hr ON hr.oidref = ba.oid "
             f"JOIN ref AS b ON b.oidbib = hr.oidbibref WHERE i.id = '{qid}'")
        try:
            t = s.query_tap(q)
            if len(t):
                out['n_bibcodes'] = len(t)
                out['bibcodes'] = [{'bibcode': str(row['bibcode']),
                                    'title': str(row['title'])[:95]} for row in t][:30]
                out['bib_query_id'] = qid
                break
        except Exception as e:
            out['_bib_err'] = f'{type(e).__name__}: {e}'
    return out

# ------------------------------------------------------------------ SED physics
def planck_lambda(lam_m, T):
    x = H_PLANCK * C_LIGHT / (lam_m * K_BOLTZ * T)
    x = np.clip(x, 1e-9, 700.0)
    return (2.0 * H_PLANCK * C_LIGHT**2 / lam_m**5) / (np.expm1(x))

def fnu_blackbody(lam_A, T, R_rsun, d_pc):
    lam_m = np.asarray(lam_A, float) * 1e-10
    Blam = planck_lambda(lam_m, T)
    flam = math.pi * Blam * (R_rsun * RSUN_M / (d_pc * PC_M))**2
    fnu = flam * lam_m**2 / C_LIGHT
    return fnu * 1e26

def abmag_blackbody(lam_A, T, R_rsun, d_pc):
    fnu = fnu_blackbody(lam_A, T, R_rsun, d_pc)
    return -2.5 * np.log10(np.clip(fnu, 1e-30, None) / ZP_AB)

def to_ab(band, rec):
    m = rec['mag']
    if rec['system'] == 'Vega':
        m = m + BANDS[band][2]
    return m

def deredden_ab(band, m_ab, A_V):
    return m_ab - ALAM_AV.get(band, 0.0) * A_V

ANCHOR_BANDS = ['Gaia_BP', 'Gaia_G', 'Gaia_RP', '2MASS_J', '2MASS_H', '2MASS_K',
                'WISE_W1', 'WISE_W2']

def fit_primary(phot, d_pc, A_V, T_lo=4000, T_hi=15000):
    bands = [b for b in ANCHOR_BANDS if b in phot and phot[b]['det'] == 'det']
    lam = np.array([BANDS[b][0] for b in bands])
    obs = np.array([deredden_ab(b, to_ab(b, phot[b]), A_V) for b in bands])
    err = np.array([max(phot[b]['err'], 0.02) for b in bands])
    err = np.sqrt(err**2 + 0.03**2)

    def chi2_at_T(T):
        model0 = abmag_blackbody(lam, T, 1.0, d_pc)
        w = 1.0 / err**2
        delta = np.sum(w * (obs - model0)) / np.sum(w)
        model = model0 + delta
        chi2 = np.sum(((obs - model) / err)**2)
        R = 10**(-delta / 5.0)
        return chi2, R, model

    Ts = np.linspace(T_lo, T_hi, 1101)
    c2 = np.array([chi2_at_T(T)[0] for T in Ts])
    j = int(np.argmin(c2))
    T1 = float(Ts[j])
    chi2, R1, model = chi2_at_T(T1)
    below = Ts[c2 <= c2[j] + 1.0]
    T_err = float((below.max() - below.min()) / 2.0) if len(below) > 1 else float(Ts[1] - Ts[0])
    res = {b: float(obs[k] - model[k]) for k, b in enumerate(bands)}
    return dict(T1=T1, T1_err=T_err, R1=R1, chi2=float(chi2), ndof=len(bands) - 2,
                bands=bands, resid=res)

def companion_excess_sigma(phot, fit, d_pc, A_V, T2, R2, test_bands, label):
    T1, R1_0 = fit['T1'], fit['R1']

    def total_fnu(b, R1):
        lam = BANDS[b][0]
        return fnu_blackbody(lam, T1, R1, d_pc) + fnu_blackbody(lam, T2, R2, d_pc)

    anchor = [b for b in test_bands if b in phot and phot[b]['det'] == 'det' and b in ANCHOR_BANDS]
    if not anchor:
        anchor = [b for b in test_bands if b in phot and phot[b]['det'] == 'det']
    if anchor:
        def chi2_R1(R1):
            s = 0.0
            for b in anchor:
                m = -2.5 * math.log10(total_fnu(b, R1) / ZP_AB)
                obs = deredden_ab(b, to_ab(b, phot[b]), A_V)
                err = math.sqrt(max(phot[b]['err'], 0.02)**2 + 0.03**2)
                s += ((obs - m) / err)**2
            return s
        res = minimize_scalar(chi2_R1, bounds=(R1_0 * 0.3, R1_0 * 1.5), method='bounded')
        R1 = float(res.x)
    else:
        R1 = R1_0

    rows = []; chi2_comp = 0.0; chi2_pri = 0.0
    for b in test_bands:
        if b not in phot:
            continue
        rec = phot[b]; lam = BANDS[b][0]
        f1 = fnu_blackbody(lam, T1, R1, d_pc)
        f1_0 = fnu_blackbody(lam, T1, R1_0, d_pc)
        f2 = fnu_blackbody(lam, T2, R2, d_pc)
        m_pri = -2.5 * math.log10(f1_0 / ZP_AB)
        m_tot = -2.5 * math.log10((f1 + f2) / ZP_AB)
        obs = deredden_ab(b, to_ab(b, rec), A_V)
        err = math.sqrt(max(rec['err'], 0.02)**2 + 0.03**2)
        flux_frac = f2 / (f1 + f2)
        resid = obs - m_tot
        sig = resid / err
        if rec['det'] == 'det':
            chi2_comp += ((obs - m_tot) / err)**2
            chi2_pri += ((obs - m_pri) / err)**2
        rows.append(dict(band=b, lam=lam, det=rec['det'], obs=round(obs, 3),
                         m_pri=round(m_pri, 3), m_tot=round(m_tot, 3),
                         flux_frac=round(flux_frac, 3), sigma=round(sig, 2)))
    best = None
    for row in rows:
        if row['det'] != 'det':
            continue
        if row['sigma'] > 0 and (best is None or row['sigma'] > best['sigma']):
            best = row
    maxff = round(max((r['flux_frac'] for r in rows if r['det'] == 'det'), default=0.0), 3)
    return dict(label=label, T2=T2, R2=round(R2, 4), R1_refit=round(R1, 5),
                delta_chi2=round(chi2_comp - chi2_pri, 1), max_flux_frac_det=maxff,
                best=best, rows=rows)

def solve_m2_dark(fM, M1):
    if fM is None or fM <= 0:
        return None
    g = lambda m2: m2**3 / (M1 + m2)**2 - fM
    try:
        return float(brentq(g, 1e-4, 50.0))
    except Exception:
        return None

# ------------------------------------------------------------------ MS companion grid
# Pecaut & Mamajek (2013) main-sequence: SpT -> (Teff K, R_sun, M_G abs proxy).
MS_GRID = [
    ('B8V', 11400, 2.49, 3.38),
    ('B9V', 10600, 2.30, 3.00),
    ('A0V', 9700,  2.19, 2.60),
    ('A1V', 9300,  2.14, 2.40),
    ('A2V', 8800,  2.05, 2.20),
    ('A5V', 8000,  1.79, 1.92),
    ('A7V', 7800,  1.65, 1.78),
    ('F0V', 7220,  1.46, 1.59),
    ('F5V', 6500,  1.31, 1.33),
    ('G0V', 5930,  1.10, 1.06),
    ('G5V', 5660,  0.98, 0.97),
    ('K0V', 5280,  0.85, 0.88),
    ('K5V', 4410,  0.70, 0.70),
    ('M0V', 3870,  0.59, 0.59),
    ('M2V', 3550,  0.45, 0.44),
    ('M4V', 3160,  0.26, 0.20),
]
SPT_MASS = {'B8V':3.38,'B9V':3.00,'A0V':2.60,'A1V':2.40,'A2V':2.20,'A5V':1.92,'A7V':1.78,
            'F0V':1.59,'F5V':1.33,'G0V':1.06,'G5V':0.97,'K0V':0.88,'K5V':0.70,'M0V':0.59,
            'M2V':0.44,'M4V':0.20}

def spt_to_TR(M2, T1_primary=None):
    """Interpolate (Teff, R) at companion mass M2 from MS_GRID. If M2>grid top use top."""
    rows_sorted = sorted(MS_GRID, key=lambda g: SPT_MASS[g[0]])
    m_s = np.array([SPT_MASS[g[0]] for g in rows_sorted])
    t_s = np.array([g[1] for g in rows_sorted])
    r_s = np.array([g[2] for g in rows_sorted])
    if M2 > m_s.max():
        return float(t_s[-1]), float(r_s[-1])
    return float(np.interp(M2, m_s, t_s)), float(np.interp(M2, m_s, r_s))

# ------------------------------------------------------------------ main
def run():
    print('=' * 78)
    print(f'GAIA DR3 {SID} = {HD_NAME} -- PMa dark-vs-luminous companion vetting')
    print('=' * 78)

    gs = gaia_source(SID)
    ra = gs.get('ra'); dec = gs.get('dec')
    print(f"  RA,Dec = {ra},{dec}")
    ap = gaia_ap(SID); aps = gaia_ap_supp(SID)
    nss = gaia_nss(SID); accel = gaia_accel(SID)

    sim = simbad_otype_bibs(f'Gaia DR3 {SID}', hd_name=HD_NAME)

    phot, prov = fetch_photometry(ra, dec, gs)
    kerv = fetch_kervella(ra, dec)
    hgca = fetch_hgca(ra, dec)
    wds = fetch_wds(ra, dec)
    neigh = gaia_neighbours(ra, dec, gs.get('parallax'), gs.get('pmra'), gs.get('pmdec'))

    # ---- distance & extinction ----
    plx_gs = gs.get('parallax')
    plx_nss = nss.get('parallax') if nss else None
    plx_accel = accel.get('parallax') if accel else None
    plx_used = plx_nss or plx_accel or plx_gs
    d_gs = 1000.0 / plx_gs if plx_gs else None
    d_pc = 1000.0 / plx_used if plx_used else d_gs
    ag = gs.get('ag_gspphot') or (ap.get('ag_gspphot') if ap else None)
    A_V = ag if (ag and ag > 0) else 0.10
    EBV = A_V / 3.1

    # ---- single-star primary fit ----
    fit = fit_primary(phot, d_pc, A_V)
    T1, R1 = fit['T1'], fit['R1']
    L1 = 4 * math.pi * (R1 * RSUN_M)**2 * SIGMA_SB * T1**4 / LSUN_W
    M_G_primary = None
    if gs.get('phot_g_mean_mag') and plx_used:
        M_G_primary = gs['phot_g_mean_mag'] + 5 * math.log10(plx_used / 1000.0) + 5 - (A_V * ALAM_AV['Gaia_G'])

    M1_flame = ap.get('mass_flame') if ap else None
    teff_p = (ap.get('teff_gspphot') if ap else None) or gs.get('teff_gspphot')
    logg_p = (ap.get('logg_gspphot') if ap else None) or gs.get('logg_gspphot')
    R_flame = ap.get('radius_flame') if ap else None
    L_flame = ap.get('lum_flame') if ap else None
    # primary mass estimate for acceleration inversion
    M1 = M1_flame if (M1_flame and M1_flame > 0) else (kerv.get('Mass') if kerv.get('Mass') else 1.5)

    # ---- 2-component SED: luminous MS-companion grid ----
    all_bands = [b for b in phot]
    excl = []
    for (spt, T2, R2, MG2) in MS_GRID:
        e = companion_excess_sigma(phot, fit, d_pc, A_V, T2, R2, all_bands, spt)
        f2_G = fnu_blackbody(BANDS['Gaia_G'][0], T2, R2, d_pc)
        f1_G = fnu_blackbody(BANDS['Gaia_G'][0], T1, R1, d_pc)
        e['G_flux_frac'] = round(f2_G / (f1_G + f2_G), 4)
        e['delta_G_comp_minus_pri'] = (round(-2.5 * math.log10(f2_G / f1_G), 3) if f1_G > 0 else None)
        e['M2_Msun'] = SPT_MASS[spt]
        excl.append(e)

    # ---- the caller's M2_median as a luminous companion ----
    M2_med = CALLER['M2_median']
    T2_med, R2_med = spt_to_TR(M2_med)
    e_med = companion_excess_sigma(phot, fit, d_pc, A_V, T2_med, R2_med, all_bands,
                                   f'M2med_{M2_med}Msun')
    f2_G = fnu_blackbody(BANDS['Gaia_G'][0], T2_med, R2_med, d_pc)
    f1_G = fnu_blackbody(BANDS['Gaia_G'][0], T1, R1, d_pc)
    e_med['G_flux_frac'] = round(f2_G / (f1_G + f2_G), 4)
    e_med['delta_G_comp_minus_pri'] = round(-2.5 * math.log10(f2_G / f1_G), 3) if f1_G > 0 else None
    e_med['T2_assumed'] = round(T2_med, 0); e_med['R2_assumed'] = round(R2_med, 3)
    e_med['L2_Lsun'] = round(4 * math.pi * (R2_med * RSUN_M)**2 * SIGMA_SB * T2_med**4 / LSUN_W, 2)

    # ---- Acceleration M2(P) inversion: map the period-degeneracy explicitly ----
    accel_block = {'have_module': _HAVE_ACCEL, 'have_accel_row': accel is not None}
    if _HAVE_ACCEL and accel is not None:
        # acceleration components in nss_acceleration_astro: accel_ra/accel_dec (mas/yr^2),
        # for Acceleration7; Acceleration9 adds deriv terms. Use what is present.
        ar = accel.get('accel_ra'); ad = accel.get('accel_dec')
        ar_e = accel.get('accel_ra_error'); ad_e = accel.get('accel_dec_error')
        amag = acceleration_magnitude(ar, ad)
        amag_e = acceleration_magnitude_error(ar, ad, ar_e, ad_e) if (ar_e and ad_e) else None
        accel_block.update(nss_solution_type=accel.get('nss_solution_type'),
                           accel_ra=ar, accel_dec=ad, accel_mag_mas_yr2=amag,
                           accel_mag_err=amag_e, significance=accel.get('significance'))
        if amag and plx_used:
            rng = M2_range(amag, plx_used, M1=M1, P_yr_min=3.0, P_yr_max=100.0)
            if rng:
                accel_block['M2_min_P3yr'] = round(rng[0], 3)
                accel_block['M2_median_logP'] = round(rng[1], 3)
                accel_block['M2_max_P100yr'] = round(rng[2], 3)
            # M2 at the SED-hidden period sweet spot: where a luminous companion is still hidden,
            # tabulate M2 at a handful of periods
            curve = []
            for P in (3, 5, 8, 12, 20, 30, 50, 100):
                m2 = M2_from_acceleration(amag, plx_used, M1, float(P))
                curve.append(dict(P_yr=P, M2_Msun=(round(m2, 3) if m2 else None)))
            accel_block['M2_of_P_curve'] = curve
    elif _HAVE_ACCEL:
        # No nss_acceleration_astro row: derive |a| consistent with the HGCA/Kervella M2_median.
        # We invert the reported M2_median back to |a| at the grid-median period as a sanity proxy.
        accel_block['note'] = 'no nss_acceleration_astro row; M2(P) curve derived from Kervella PMa not available here'

    # ---- assemble ----
    result = dict(
        source_id=SID, hd_name=HD_NAME, ra=ra, dec=dec,
        caller_inputs=CALLER,
        distances=dict(plx_gs=plx_gs, plx_nss=plx_nss, plx_accel=plx_accel,
                       plx_used=plx_used, plx_used_src=('NSS' if plx_nss else ('accel' if plx_accel else 'gaia_source')),
                       d_gs_pc=(round(d_gs, 2) if d_gs else None),
                       d_used_pc=(round(d_pc, 2) if d_pc else None)),
        extinction=dict(A_V=round(A_V, 3), EBV=round(EBV, 3), ag_source=('gspphot' if ag else 'default')),
        gaia_source=gs, gaia_ap=ap, gaia_ap_supp=aps,
        nss_two_body_orbit=nss, nss_acceleration_astro=accel,
        primary_fit=dict(T1=round(T1, 0), T1_err=round(fit['T1_err'], 0), R1_rsun=round(R1, 4),
                         L1_lsun=round(L1, 3), chi2=round(fit['chi2'], 2), ndof=fit['ndof'],
                         redchi2=round(fit['chi2'] / max(fit['ndof'], 1), 2),
                         M_G_primary=(round(M_G_primary, 3) if M_G_primary else None),
                         anchor_bands=fit['bands'], resid={k: round(v, 3) for k, v in fit['resid'].items()}),
        primary_lit=dict(mass_flame=M1_flame, M1_used=M1, teff_gspphot=teff_p, logg_gspphot=logg_p,
                         radius_flame=R_flame, lum_flame=L_flame,
                         spectraltype_esphs=(ap.get('spectraltype_esphs') if ap else None)),
        photometry={b: dict(mag=round(phot[b]['mag'], 4), err=round(phot[b]['err'], 4),
                            system=phot[b]['system'], det=phot[b]['det'],
                            ab=round(to_ab(b, phot[b]), 4),
                            ab_dered=round(deredden_ab(b, to_ab(b, phot[b]), A_V), 4),
                            src=phot[b]['src']) for b in phot},
        photometry_provenance=prov,
        ms_companion_exclusion=excl,
        caller_M2med_companion=e_med,
        acceleration_inversion=accel_block,
        kervella=kerv, hgca=hgca, wds=wds, gaia_neighbours=neigh, simbad=sim,
    )

    with open('/tmp/hd21940_pma.json', 'w') as f:
        json.dump(result, f, indent=2, default=str)

    # ---- console summary ----
    print("\n================ DISTANCE / PRIMARY ================")
    print(f"  plx(GS)={plx_gs}  plx(NSS)={plx_nss}  plx(accel)={plx_accel}  -> plx_used={plx_used} "
          f"({'NSS' if plx_nss else ('accel' if plx_accel else 'GS')})  d={d_pc:.1f} pc")
    print(f"  A_V={A_V:.3f} ({'gspphot' if ag else 'default'})  RUWE={gs.get('ruwe')}")
    print(f"  primary single-BB fit: T1={T1:.0f}+/-{fit['T1_err']:.0f} K, R1={R1:.3f} Rsun, "
          f"L1={L1:.2f} Lsun ; redchi2={fit['chi2']/max(fit['ndof'],1):.2f} (n={len(fit['bands'])})")
    print(f"  M_G(primary)={M_G_primary}  mass_flame={M1_flame}  M1_used={M1}  teff_gspphot={teff_p} "
          f"logg_gspphot={logg_p}  R_flame={R_flame}  L_flame={L_flame}")
    print(f"  SIMBAD: main_id={sim.get('main_id')} otype={sim.get('otype')} "
          f"sp_type={sim.get('sp_type')} V={sim.get('V')} n_bib={sim.get('n_bibcodes')}")
    print("  primary-fit per-band residuals (obs-model, dered AB):")
    for b in fit['bands']:
        print(f"      {b:10s} {fit['resid'][b]:+.3f}")

    print("\n================ GAIA MULTIPLICITY / ORBIT FLAGS ================")
    print(f"  non_single_star      = {gs.get('non_single_star')}")
    print(f"  RUWE                 = {gs.get('ruwe')}")
    print(f"  ipd_frac_multi_peak  = {gs.get('ipd_frac_multi_peak')} %")
    print(f"  ipd_frac_odd_win     = {gs.get('ipd_frac_odd_win')} %")
    print(f"  astrom_excess_noise  = {gs.get('astrometric_excess_noise')} (sig={gs.get('astrometric_excess_noise_sig')})")
    print(f"  astrom_params_solved = {gs.get('astrometric_params_solved')}")
    print(f"  rv_amplitude_robust  = {gs.get('rv_amplitude_robust')} km/s  (K1~{(gs.get('rv_amplitude_robust') or 0)/2:.2f})")
    print(f"  vbroad               = {gs.get('vbroad')} +/- {gs.get('vbroad_error')} km/s")
    print(f"  radial_velocity      = {gs.get('radial_velocity')} +/- {gs.get('radial_velocity_error')} "
          f"(nb_transits={gs.get('rv_nb_transits')})")
    print(f"  phot_bp_rp_excess    = {gs.get('phot_bp_rp_excess_factor')}")
    print(f"  NSS 2-body orbit row = {nss is not None} ({nss.get('nss_solution_type') if nss else '-'})")
    print(f"  NSS accel row        = {accel is not None} ({accel.get('nss_solution_type') if accel else '-'})")
    if nss:
        for k in ('period', 'eccentricity', 'a_thiele_innes', 'rv_amplitude_robust',
                  'significance', 'parallax', 'inclination'):
            if k in nss:
                print(f"      NSS {k:22s} = {nss.get(k)}")

    print("\n================ 2-COMPONENT SED: LUMINOUS MS COMPANION GRID ================")
    print("  (primary R refit per companion; sigma = worst real-detection colour residual;")
    print("   G_ff = companion fraction of system G-band flux; dG = m_G,comp - m_G,pri)")
    print(f"  {'SpT':5s} {'M2':>5s} {'T2':>6s} {'R2':>5s} {'G_ff':>6s} {'dG':>6s} {'maxFF':>6s} {'worst_sig':>10s} {'band':>9s} {'dX2':>9s}")
    for e in excl:
        b = e['best']
        bs = b['sigma'] if b else 0.0; bn = b['band'] if b else '-'
        print(f"  {e['label']:5s} {e['M2_Msun']:5.2f} {e['T2']:6.0f} {e['R2']:5.2f} {e['G_flux_frac']:6.3f} "
              f"{(e['delta_G_comp_minus_pri'] if e['delta_G_comp_minus_pri'] is not None else 0):6.2f} "
              f"{e['max_flux_frac_det']:6.3f} {bs:10.1f} {bn:>9s} {e['delta_chi2']:9.1f}")

    print(f"\n================ CALLER M2_median COMPANION ({M2_med} Msun) AS A LUMINOUS STAR ================")
    em = e_med
    print(f"  If the {M2_med} Msun companion were main-sequence: SpT~{'A' if T2_med>7500 else 'F/G'}, "
          f"T2={em['T2_assumed']:.0f} K, R2={em['R2_assumed']} Rsun, L2={em['L2_Lsun']} Lsun")
    print(f"  -> companion G-band flux fraction = {em['G_flux_frac']:.3f}  "
          f"(dG = {em['delta_G_comp_minus_pri']} mag vs primary)")
    print(f"  -> worst real-detection SED tension = {em['best']['sigma'] if em['best'] else 0:.1f} sigma "
          f"@ {em['best']['band'] if em['best'] else '-'}  (delta-chi2={em['delta_chi2']})")
    print("  per-band (obs vs primary-only vs primary+companion):")
    for r in em['rows']:
        print(f"      {r['band']:10s} det={r['det']:3s} obs={r['obs']:+8.3f} "
              f"m_pri={r['m_pri']:+8.3f} m_tot={r['m_tot']:+8.3f} ff={r['flux_frac']:.3f} sig={r['sigma']:+.2f}")

    print("\n================ ACCELERATION M2(P) INVERSION ================")
    ab = accel_block
    if ab.get('have_accel_row'):
        print(f"  nss_solution_type = {ab.get('nss_solution_type')}  |a|={ab.get('accel_mag_mas_yr2')} "
              f"+/- {ab.get('accel_mag_err')} mas/yr^2  significance={ab.get('significance')}")
        if 'M2_min_P3yr' in ab:
            print(f"  M2 over log-P[3,100]yr grid: min(P=3yr)={ab['M2_min_P3yr']}  "
                  f"median={ab['M2_median_logP']}  max(P=100yr)={ab['M2_max_P100yr']} Msun")
            print("  M2(P) curve (monotone: longer P -> larger M2):")
            for c in ab.get('M2_of_P_curve', []):
                print(f"      P={c['P_yr']:>4} yr  ->  M2={c['M2_Msun']} Msun")
    else:
        print(f"  No nss_acceleration_astro row found. {ab.get('note','')}")
        print("  (M2_median is then the Kervella H2G2 M2_5AU MC / external accel-grid value.)")

    print("\n================ KERVELLA / HGCA CATALOG VALUES ================")
    if kerv.get('match'):
        for k in ('sep_arcsec', 'HD', 'HIP', 'GaiaEDR3', 'Mass', 'e_Mass',
                  'M2-1', 'M2-1_Msun', 'M2-3', 'M2-3_Msun', 'M2-5', 'M2-5_Msun',
                  'M2-10', 'M2-10_Msun', 'dVt', 'e_dVt', 'snrPMaH2G2', 'snrPMaHG1', 'Plx'):
            if k in kerv:
                print(f"    Kervella {k:14s} = {kerv.get(k)}")
        print("    [NB: Kervella M2-Xau columns are in JUPITER masses; *_Msun = converted]")
    else:
        print("    Kervella J/A+A/657/A7: no match within 10\"")
    if hgca.get('match'):
        print(f"    HGCA {hgca.get('catalog')} match sep={hgca.get('sep_arcsec')}\"")
        for k in ('chisq', 'chi2', 'Chi2', 'pmra_gaia', 'pmdec_gaia', 'sig'):
            if k in hgca:
                print(f"    HGCA {k:14s} = {hgca.get(k)}")
    else:
        print("    HGCA J/ApJS/254/42: no match")

    print("\n================ RESOLVED / WIDE COMPANION ================")
    print(f"  WDS: {('MATCH n=%d' % wds['n_rows']) if wds.get('match') else 'no entry within 15\"'}")
    if wds.get('match'):
        for r in wds['rows']:
            print(f"     {r}")
    if isinstance(neigh, dict) and 'rows' in neigh:
        print(f"  Gaia DR3 cone (30\"): {neigh['n_within']} sources")
        for r in neigh['rows']:
            tag = 'TARGET' if r.get('is_target') else ''
            cpm = ' <-- CPM candidate' if r.get('cpm_candidate') else ''
            print(f"     sep={str(r['sep_arcsec']):>7s}\" G={str(r['G']):>6s} plx={str(r['parallax']):>7s} "
                  f"pmra={str(r['pmra']):>8s} pmdec={str(r['pmdec']):>8s} "
                  f"dplx={str(r.get('dplx_mas','-')):>7s} dpm={str(r.get('dpm_masyr','-')):>7s} {tag}{cpm}")

    print(f"\n  n_bibcodes={sim.get('n_bibcodes')}  (novelty check)")
    print("\nJSON -> /tmp/hd21940_pma.json")
    return result

if __name__ == '__main__':
    run()
