#!/usr/bin/env python3
"""Dark-vs-luminous companion vetting of the PMa-corroborated accelerating source
Gaia DR3 5549320092596023168 = HD 44206 (2026-05-31).

Caller context: HGCA chi2=130.6, Kervella snrPMa=9.45, M2_median (Kervella
M2_5AU MC) = 2.413 Msun, SIMBAD HD 44206, known_multiple=false. This is a PMa /
HGCA *acceleration* source -- NOT (claimed) a Thiele-Innes orbit; per
METHODOLOGY.md the Acceleration-NSS extension is the deferred channel: M2 comes
from the proper-motion anomaly + assumed period, not an algebraic mass-function
inversion. BUT: always check whether Gaia DR3 actually has an SB1/Orbital NSS
solution (the HD182379 precedent collapsed M2 2.6 -> 0.46 once the SB1 orbit
pinned the period).

Decisive questions:
  (1) SED 2-component fit (GALEX/Gaia/2MASS/WISE): single-star primary BB; then
      test whether a luminous A/B/F/G/K/M MS companion (0.2-3.4 Msun grid) is
      REQUIRED or EXCLUDED band-by-band. A 2-5 Msun MS companion is an early-A /
      late-B star (Teff 8500-13000 K, L 20-150 Lsun) and is conspicuous.
  (2) Resolved / wide companion: Gaia DR3 cone (matching plx+PM), WDS.
  (3) Gaia non_single_star / RVS SB2 (rv_amplitude_robust, vbroad, ipd) /
      ipd_frac_multi_peak / RUWE.
  (4) Is Kervella M2_5AU + HGCA chi2 consistent with a *luminous* stellar
      companion of that mass, or does a DARK companion remain required?
      KEY: Kervella M2-Xau columns are in JUPITER masses (HD182379 precedent) --
      convert. And the caller's period-marginalised M2_median can be inflated by
      a broad period prior; the SB1 orbit (if present) is the truth.

Classify companion_class = luminous_stellar / dark_candidate / ambiguous.

Env: /Users/legbatterij/claude_projects/ostinato/.venv/bin/python (no pip-install)
Outputs: /tmp/hd44206_pma.json , /tmp/hd44206_pma_report.md
Reuses canonical SED BB machinery + Gaia/SIMBAD/Vizier fetch from
scripts/hd182379_pma_darkluminous_2026_05_31.py and MC-posterior from
scripts/sb1_5355234746758153728_deepdive_2026_05_31.py.
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
MJUP     = 1.89813e27
MJUP_PER_MSUN = MSUN / MJUP   # ~1047.6

SID = 5549320092596023168
HD_NAME = 'HD 44206'
CALLER = dict(HGCA_chi2=130.6, snrPMa=9.45, M2_median=2.413, known_multiple=False)

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

def gaia_nss_accel(sid):
    """Acceleration NSS (nss_acceleration_astro) -- the PMa channel solution."""
    def go():
        return Gaia.launch_job(f'SELECT * FROM gaiadr3.nss_acceleration_astro WHERE source_id={sid}').get_results()
    t = _with_timeout(go, 60, None)
    return _tab_to_dict(t) if (t is not None and len(t)) else None

def gaia_neighbours(ra, dec, plx, pmra, pmdec, radius_arcsec=30.0):
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
            row['cpm_candidate'] = bool(dplx < 0.5 and (dpm is not None and dpm < 5.0))
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
    co = SkyCoord(ra, dec, unit='deg')
    v = Vizier(columns=['**'], row_limit=5)
    r = _with_timeout(lambda: v.query_region(co, radius=10 * u.arcsec, catalog='J/A+A/657/A7'), 60, None)
    if not r or len(r) == 0:
        return {'match': False}
    t = r[0]; i = int(np.argmin(t['_r']))
    want = ['HD', 'HIP', 'GaiaEDR3', 'Mass', 'e_Mass', 'M2-5', 'b_M2-5', 'B_M2-5',
            'M2-3', 'M2-10', 'dVt', 'e_dVt', 'snrPMaH2G2', 'snrPMaHG1', 'PMaRAH2G3',
            'PMaDEH2G3', 'snrPMaH2EG3b', 'Plx']
    out = {'match': True, 'sep_arcsec': round(float(t['_r'][i]), 2)}
    for c in t.colnames:
        out[c] = _flt(t[c][i]) if _flt(t[c][i]) is not None else (
            None if np.ma.is_masked(t[c][i]) else str(t[c][i]))
    out['_wanted_present'] = [w for w in want if w in t.colnames]
    return out

def fetch_hgca(ra, dec):
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
            out['rvz_radvel'] = _flt(r['rvz_radvel'][0]) if 'rvz_radvel' in cn else None
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

# ------------------------------------------------------------------ MS companion grid
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

# ------------------------------------------------------------------ orbit / mass-function
def f_spec_msun(K1_kms, P_d, e):
    if not (K1_kms and P_d):
        return None
    P_s = P_d * 86400.0
    K = K1_kms * 1000.0
    fM = P_s * K ** 3 * (1 - e * e) ** 1.5 / (2 * math.pi * G_SI)
    return fM / MSUN

def solve_m2_min(fM, M1):
    if fM is None or fM <= 0:
        return None
    g = lambda m2: m2**3 / (M1 + m2)**2 - fM
    try:
        return float(brentq(g, 1e-4, 80.0))
    except Exception:
        return None

def mc_m2_posterior(fM, M1, M1_err=0.15, P_d=None, e=0.0, K1=None, K1_err=None, n=200000):
    """MC M2 posterior. If K1/P available, propagate their errors; isotropic-i prior."""
    rng = np.random.default_rng(7)
    M1s = np.clip(rng.normal(M1, M1_err, n), 0.3, 5.0)
    if K1 is not None and P_d is not None:
        K1s = np.clip(rng.normal(K1, (K1_err or 0.1 * K1), n), 1e-3, None)
        es = np.clip(e + rng.normal(0, 0.03, n), 0, 0.95)
        Ps = np.full(n, P_d)
        fMs = (Ps * 86400.0) * (K1s * 1000.0) ** 3 * (1 - es ** 2) ** 1.5 / (2 * math.pi * G_SI) / MSUN
    else:
        fMs = np.full(n, fM)
    cosi = rng.uniform(0, 1, n)
    sini = np.sqrt(np.clip(1 - cosi ** 2, 1e-6, 1.0))
    # solve (M2 sini)^3/(M1+M2)^2 = fM per draw via vectorised bisection
    lo = np.full(n, 1e-4); hi = np.full(n, 80.0)
    for _ in range(60):
        mid = 0.5 * (lo + hi)
        f_mid = (mid * sini) ** 3 / (M1s + mid) ** 2
        gt = f_mid > fMs
        hi = np.where(gt, mid, hi); lo = np.where(gt, lo, mid)
    M2_iso = 0.5 * (lo + hi)
    # i=90 distribution
    lo = np.full(n, 1e-4); hi = np.full(n, 80.0)
    for _ in range(60):
        mid = 0.5 * (lo + hi)
        f_mid = mid ** 3 / (M1s + mid) ** 2
        gt = f_mid > fMs
        hi = np.where(gt, mid, hi); lo = np.where(gt, lo, mid)
    M2_min = 0.5 * (lo + hi)
    def pct(x):
        return {str(p): round(float(np.percentile(x, p)), 4) for p in (2.5, 16, 50, 84, 97.5)}
    return {
        'M2_min_pctile': pct(M2_min), 'M2_isotropic_pctile': pct(M2_iso),
        'P_M2_gt_1.4_iso': round(float(np.mean(M2_iso > 1.4)), 4),
        'P_M2_gt_3_iso': round(float(np.mean(M2_iso > 3.0)), 4),
        'P_M2_gt_1.4_min': round(float(np.mean(M2_min > 1.4)), 4),
        'P_M2_gt_3_min': round(float(np.mean(M2_min > 3.0)), 4),
    }

# ------------------------------------------------------------------ main
def run():
    print('=' * 78)
    print(f'GAIA DR3 {SID} = {HD_NAME} -- PMa dark-vs-luminous companion vetting')
    print('=' * 78)

    gs = gaia_source(SID)
    ra = gs.get('ra'); dec = gs.get('dec')
    print(f"  RA,Dec = {ra},{dec}")
    ap = gaia_ap(SID); aps = gaia_ap_supp(SID)
    nss = gaia_nss(SID); nss_acc = gaia_nss_accel(SID)

    sim = simbad_otype_bibs(f'Gaia DR3 {SID}', hd_name=HD_NAME)

    phot, prov = fetch_photometry(ra, dec, gs)
    kerv = fetch_kervella(ra, dec)
    hgca = fetch_hgca(ra, dec)
    wds = fetch_wds(ra, dec)
    neigh = gaia_neighbours(ra, dec, gs.get('parallax'), gs.get('pmra'), gs.get('pmdec'))

    # ---- distance & extinction ----
    plx_gs = gs.get('parallax')
    plx_nss = nss.get('parallax') if nss else None
    plx_use = plx_nss if (plx_nss and plx_nss > 0) else plx_gs
    plx_src = 'NSS' if (plx_nss and plx_nss > 0) else 'gaia_source'
    d_gs = 1000.0 / plx_gs if plx_gs else None
    d_use = 1000.0 / plx_use if plx_use else None
    d_pc = d_use
    ag = gs.get('ag_gspphot') or (ap.get('ag_gspphot') if ap else None)
    A_V = ag if (ag and ag > 0) else 0.10
    EBV = A_V / 3.1

    # ---- single-star primary fit ----
    fit = fit_primary(phot, d_pc, A_V)
    T1, R1 = fit['T1'], fit['R1']
    L1 = 4 * math.pi * (R1 * RSUN_M)**2 * SIGMA_SB * T1**4 / LSUN_W
    M_G_primary = None
    if gs.get('phot_g_mean_mag') and plx_use:
        M_G_primary = gs['phot_g_mean_mag'] + 5 * math.log10(plx_use / 1000.0) + 5 - (A_V * ALAM_AV['Gaia_G'])

    M1_flame = ap.get('mass_flame') if ap else None
    teff_p = (ap.get('teff_gspphot') if ap else None) or gs.get('teff_gspphot')
    logg_p = (ap.get('logg_gspphot') if ap else None) or gs.get('logg_gspphot')
    R_flame = ap.get('radius_flame') if ap else None
    L_flame = ap.get('lum_flame') if ap else None
    # primary mass: FLAME, else from L1/T1 MS proxy
    M1_use = M1_flame
    M1_src = 'FLAME'
    if not M1_use:
        # crude MS mass-luminosity: M ~ L^(1/3.5) for L>1
        M1_use = float(np.clip(L1 ** (1 / 3.5), 0.5, 5.0)) if L1 else 1.0
        M1_src = 'L-M proxy from SED'

    # ---- 2-component SED: luminous MS-companion grid ----
    all_bands = [b for b in phot]
    excl = []
    for (spt, T2, R2, MG2) in MS_GRID:
        e = companion_excess_sigma(phot, fit, d_pc, A_V, T2, R2, all_bands, spt)
        f2_G = fnu_blackbody(BANDS['Gaia_G'][0], T2, R2, d_pc)
        f1_G = fnu_blackbody(BANDS['Gaia_G'][0], T1, R1, d_pc)
        e['G_flux_frac'] = round(f2_G / (f1_G + f2_G), 4)
        e['delta_G_comp_minus_pri'] = (round(-2.5 * math.log10(f2_G / f1_G), 3) if f1_G > 0 else None)
        e['M2_msun'] = SPT_MASS[spt]
        excl.append(e)

    # ---- Kervella M2_median companion at the caller mass ----
    M2_med = CALLER['M2_median']
    rows_sorted = sorted(MS_GRID, key=lambda g: SPT_MASS[g[0]])
    m_s = np.array([SPT_MASS[g[0]] for g in rows_sorted])
    t_s = np.array([g[1] for g in rows_sorted])
    r_s = np.array([g[2] for g in rows_sorted])
    T2_med = float(np.interp(M2_med, m_s, t_s))
    R2_med = float(np.interp(M2_med, m_s, r_s))
    if M2_med > m_s.max():
        T2_med = float(t_s[-1]); R2_med = float(r_s[-1])
    e_med = companion_excess_sigma(phot, fit, d_pc, A_V, T2_med, R2_med, all_bands,
                                   f'M2med_{M2_med}Msun')
    f2_G = fnu_blackbody(BANDS['Gaia_G'][0], T2_med, R2_med, d_pc)
    f1_G = fnu_blackbody(BANDS['Gaia_G'][0], T1, R1, d_pc)
    e_med['G_flux_frac'] = round(f2_G / (f1_G + f2_G), 4)
    e_med['delta_G_comp_minus_pri'] = round(-2.5 * math.log10(f2_G / f1_G), 3) if f1_G > 0 else None
    e_med['T2_assumed'] = round(T2_med, 0); e_med['R2_assumed'] = round(R2_med, 3)
    e_med['L2_Lsun'] = round(4 * math.pi * (R2_med * RSUN_M)**2 * SIGMA_SB * T2_med**4 / LSUN_W, 2)

    # ---- Kervella mass interpretation (Jupiter masses!) ----
    kerv_interp = {}
    if kerv.get('match'):
        for col, au in (('M2-3', 3), ('M2-5', 5), ('M2-10', 10)):
            v = kerv.get(col)
            if isinstance(v, (int, float)):
                kerv_interp[f'{col}_MJup'] = round(v, 2)
                kerv_interp[f'{col}_Msun'] = round(v / MJUP_PER_MSUN, 4)
        kerv_interp['Mass_primary'] = kerv.get('Mass')
        kerv_interp['snrPMaH2G2'] = kerv.get('snrPMaH2G2')

    # ---- orbit / mass-function (if SB1 or astrometric orbit present) ----
    orbit = {'nss_present': nss is not None}
    if nss:
        P = nss.get('period'); ecc = nss.get('eccentricity') or 0.0
        K1col = nss.get('semi_amplitude_primary') or nss.get('k1')
        rv_rob = gs.get('rv_amplitude_robust')
        K1_from_rob = (rv_rob / 2.0) if rv_rob else None
        K1_use = K1col or K1_from_rob
        fM_gaia = nss.get('mass_function')
        fM_recomp = f_spec_msun(K1_use, P, ecc) if (K1_use and P) else None
        orbit.update(nss_solution_type=nss.get('nss_solution_type'), period=P, ecc=ecc,
                     K1_col=K1col, rv_amplitude_robust=rv_rob, K1_from_rob=K1_from_rob,
                     K1_used=K1_use, fM_gaia_col=fM_gaia, fM_recomp=fM_recomp,
                     a_thiele_innes=nss.get('a_thiele_innes'),
                     significance=nss.get('significance'))
        fM = fM_recomp if fM_recomp else fM_gaia
        if fM and M1_use:
            orbit['M2_min_sini1'] = round(solve_m2_min(fM, M1_use), 4)
            orbit['mc'] = mc_m2_posterior(fM, M1_use, M1_err=0.15, P_d=P, e=ecc,
                                          K1=K1_use, K1_err=(0.1 * K1_use if K1_use else None))

    # ---- assemble ----
    result = dict(
        source_id=SID, hd_name=HD_NAME, ra=ra, dec=dec,
        caller_inputs=CALLER,
        distances=dict(plx_gs=plx_gs, plx_nss=plx_nss, plx_used=plx_use, plx_source=plx_src,
                       d_gs_pc=(round(d_gs, 2) if d_gs else None),
                       d_used_pc=(round(d_use, 2) if d_use else None)),
        extinction=dict(A_V=round(A_V, 3), EBV=round(EBV, 3), ag_source=('gspphot' if ag else 'default')),
        gaia_source=gs, gaia_ap=ap, gaia_ap_supp=aps, nss=nss, nss_acceleration=nss_acc,
        primary_fit=dict(T1=round(T1, 0), T1_err=round(fit['T1_err'], 0), R1_rsun=round(R1, 4),
                         L1_lsun=round(L1, 3), chi2=round(fit['chi2'], 2), ndof=fit['ndof'],
                         redchi2=round(fit['chi2'] / max(fit['ndof'], 1), 2),
                         M_G_primary=(round(M_G_primary, 3) if M_G_primary else None),
                         M1_used=round(M1_use, 3), M1_src=M1_src,
                         anchor_bands=fit['bands'], resid={k: round(v, 3) for k, v in fit['resid'].items()}),
        primary_lit=dict(mass_flame=M1_flame, teff_gspphot=teff_p, logg_gspphot=logg_p,
                         radius_flame=R_flame, lum_flame=L_flame,
                         spectraltype_esphs=(ap.get('spectraltype_esphs') if ap else None)),
        photometry={b: dict(mag=round(phot[b]['mag'], 4), err=round(phot[b]['err'], 4),
                            system=phot[b]['system'], det=phot[b]['det'],
                            ab=round(to_ab(b, phot[b]), 4),
                            ab_dered=round(deredden_ab(b, to_ab(b, phot[b]), A_V), 4),
                            src=phot[b]['src']) for b in phot},
        photometry_provenance=prov,
        ms_companion_exclusion=excl,
        kervella_M2med_companion=e_med,
        kervella=kerv, kervella_interp=kerv_interp,
        hgca=hgca, wds=wds, gaia_neighbours=neigh, simbad=sim, orbit=orbit,
    )

    with open('/tmp/hd44206_pma.json', 'w') as f:
        json.dump(result, f, indent=2, default=str)

    # ---- console summary ----
    print("\n================ DISTANCE / PRIMARY ================")
    print(f"  plx(GS)={plx_gs} mas  plx(NSS)={plx_nss}  -> plx_used={plx_use} ({plx_src})  d={d_use:.1f} pc")
    print(f"  A_V={A_V:.3f} ({'gspphot' if ag else 'default'})  RUWE={gs.get('ruwe')}")
    print(f"  primary single-BB fit: T1={T1:.0f}+/-{fit['T1_err']:.0f} K, R1={R1:.3f} Rsun, "
          f"L1={L1:.2f} Lsun ; redchi2={fit['chi2']/max(fit['ndof'],1):.2f} (n={len(fit['bands'])})")
    print(f"  M_G(primary)={M_G_primary}  mass_flame={M1_flame}  M1_used={M1_use:.2f} ({M1_src})")
    print(f"  teff_gspphot={teff_p} logg_gspphot={logg_p} R_flame={R_flame} L_flame={L_flame}")
    print(f"  SIMBAD: main_id={sim.get('main_id')} otype={sim.get('otype')} "
          f"sp_type={sim.get('sp_type')} V={sim.get('V')} RV={sim.get('rvz_radvel')} n_bib={sim.get('n_bibcodes')}")
    print("  primary-fit per-band residuals (obs-model, dered AB):")
    for b in fit['bands']:
        print(f"      {b:10s} {fit['resid'][b]:+.3f}")

    print("\n================ GAIA MULTIPLICITY FLAGS ================")
    print(f"  non_single_star      = {gs.get('non_single_star')}")
    print(f"  astrometric_params_solved = {gs.get('astrometric_params_solved')}")
    print(f"  RUWE                 = {gs.get('ruwe')}")
    print(f"  ipd_frac_multi_peak  = {gs.get('ipd_frac_multi_peak')} %")
    print(f"  ipd_frac_odd_win     = {gs.get('ipd_frac_odd_win')} %")
    print(f"  astrom_excess_noise  = {gs.get('astrometric_excess_noise')} (sig={gs.get('astrometric_excess_noise_sig')})")
    print(f"  rv_amplitude_robust  = {gs.get('rv_amplitude_robust')} km/s  (K1~{(gs.get('rv_amplitude_robust') or 0)/2:.2f})")
    print(f"  vbroad               = {gs.get('vbroad')} +/- {gs.get('vbroad_error')} km/s")
    print(f"  radial_velocity      = {gs.get('radial_velocity')} +/- {gs.get('radial_velocity_error')} "
          f"(nb_transits={gs.get('rv_nb_transits')}, rv_renorm_gof={gs.get('rv_renormalised_gof')})")
    print(f"  phot_bp_rp_excess    = {gs.get('phot_bp_rp_excess_factor')}")
    print(f"  NSS Orbital/SB1 row  = {nss is not None} ({nss.get('nss_solution_type') if nss else '-'})")
    print(f"  NSS Acceleration row = {nss_acc is not None} ({nss_acc.get('nss_solution_type') if nss_acc else '-'})")

    print("\n================ 2-COMPONENT SED: LUMINOUS MS COMPANION GRID ================")
    print("  (primary R refit per companion; sigma = worst real-detection colour residual;")
    print("   G_ff = companion fraction of system G-band flux; dG = m_G,comp - m_G,pri)")
    print(f"  {'SpT':5s} {'M2':>5s} {'T2':>6s} {'R2':>5s} {'G_ff':>6s} {'dG':>6s} {'maxFF':>6s} {'worst_sig':>10s} {'band':>9s} {'dX2':>8s}")
    for e in excl:
        b = e['best']
        bs = b['sigma'] if b else 0.0; bn = b['band'] if b else '-'
        print(f"  {e['label']:5s} {e['M2_msun']:5.2f} {e['T2']:6.0f} {e['R2']:5.2f} {e['G_flux_frac']:6.3f} "
              f"{(e['delta_G_comp_minus_pri'] if e['delta_G_comp_minus_pri'] is not None else 0):6.2f} "
              f"{e['max_flux_frac_det']:6.3f} {bs:10.1f} {bn:>9s} {e['delta_chi2']:8.1f}")

    print(f"\n================ KERVELLA M2_median COMPANION ({M2_med} Msun) ================")
    em = e_med
    print(f"  Assumed luminous companion at M2={M2_med} Msun: T2={em['T2_assumed']:.0f} K, "
          f"R2={em['R2_assumed']} Rsun, L2={em['L2_Lsun']} Lsun")
    print(f"  -> companion G-band flux fraction = {em['G_flux_frac']:.3f}  "
          f"(dG = {em['delta_G_comp_minus_pri']} mag vs primary)")
    print(f"  -> worst real-detection SED tension = {em['best']['sigma'] if em['best'] else 0:.1f} sigma "
          f"@ {em['best']['band'] if em['best'] else '-'}  (delta-chi2={em['delta_chi2']})")
    print("  per-band (obs vs primary-only vs primary+companion):")
    for r in em['rows']:
        print(f"      {r['band']:10s} det={r['det']:3s} obs={r['obs']:+8.3f} "
              f"m_pri={r['m_pri']:+8.3f} m_tot={r['m_tot']:+8.3f} ff={r['flux_frac']:.3f} sig={r['sigma']:+.2f}")

    print("\n================ KERVELLA MASS INTERPRETATION (cols in M_Jup!) ================")
    if kerv_interp:
        for k, v in kerv_interp.items():
            print(f"    {k:20s} = {v}")
    else:
        print("    no Kervella match")

    print("\n================ ORBIT / MASS FUNCTION ================")
    if nss:
        for k in ('nss_solution_type', 'period', 'ecc', 'K1_used', 'fM_gaia_col', 'fM_recomp',
                  'significance', 'M2_min_sini1'):
            print(f"    {k:18s} = {orbit.get(k)}")
        if 'mc' in orbit:
            print(f"    MC M2 (isotropic-i): {orbit['mc']['M2_isotropic_pctile']}")
            print(f"    MC M2 (i=90 min):    {orbit['mc']['M2_min_pctile']}")
            print(f"    P(M2>1.4|iso)={orbit['mc']['P_M2_gt_1.4_iso']}  P(M2>3|iso)={orbit['mc']['P_M2_gt_3_iso']}")
    else:
        print("    No NSS two_body_orbit row -> pure PMa/acceleration source (M2 period-prior dependent)")

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

    print("\n================ KERVELLA / HGCA CATALOG VALUES ================")
    if kerv.get('match'):
        for k in ('sep_arcsec', 'HD', 'HIP', 'Mass', 'e_Mass', 'M2-5', 'b_M2-5', 'B_M2-5',
                  'M2-3', 'M2-10', 'dVt', 'e_dVt', 'snrPMaH2G2', 'snrPMaHG1', 'Plx'):
            if k in kerv:
                print(f"    Kervella {k:14s} = {kerv.get(k)}")
    else:
        print("    Kervella J/A+A/657/A7: no match within 10\"")
    if hgca.get('match'):
        print(f"    HGCA {hgca.get('catalog')} match sep={hgca.get('sep_arcsec')}\"")
        for k in ('chisq', 'chi2', 'Chi2', 'pmra_gaia', 'pmdec_gaia'):
            if k in hgca:
                print(f"    HGCA {k:14s} = {hgca.get(k)}")
    else:
        print("    HGCA J/ApJS/254/42: no match")

    print(f"\n  SIMBAD bibcodes (n={sim.get('n_bibcodes')}):")
    for bc in (sim.get('bibcodes') or [])[:12]:
        print(f"     {bc['bibcode']}  {bc['title']}")

    print("\nJSON -> /tmp/hd44206_pma.json")
    return result

if __name__ == '__main__':
    run()
