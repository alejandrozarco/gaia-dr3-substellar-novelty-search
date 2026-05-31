#!/usr/bin/env python3
"""Dark-vs-luminous companion vetting of the PMa-corroborated accelerating source
Gaia DR3 5575983077771827584 = HD 48797 (2026-05-31).

Caller context: HGCA chi2=61.5, Kervella snrPMa=7.55, M2_median (Kervella
M2_5AU MC) = 2.276 Msun, SIMBAD HD 48797, known_multiple=true. This is a PMa /
HGCA *acceleration* source -- NOT (a priori) a Thiele-Innes orbit and (per
METHODOLOGY.md) the Acceleration-NSS extension is the deferred channel: M2 comes
from the proper-motion anomaly + assumed period, not an algebraic mass-function
inversion. (We still QUERY nss_two_body_orbit: if a Gaia SB1/Orbital/Accel row
exists it pins the period and collapses the M2 posterior, as for HD182379.)

The decisive question is the SED. A 2-5 Msun main-sequence companion is an
EARLY-A / LATE-B star (Teff ~ 8500-13000 K, L ~ 20-150 Lsun) and would be
*conspicuous* unless the primary itself is far more luminous. So:

  (1) SED 2-component fit (GALEX/Gaia/2MASS/WISE): fit a single-star primary BB
      to the optical+IR anchors; then test whether adding a luminous A/B/F/G/K/M
      MS companion (grid spanning ~0.5-3 Msun) is REQUIRED or EXCLUDED, band by
      band with full errors. Is the SED single-star, or does a 2nd luminous star
      appear? (The HD157033 precedent: 7 of 8 Pile-A HGCA candidates were demoted
      as Kervella H2G2 *luminous* stellar companions at the 5-AU reference.)
  (2) Resolved / wide companion: Gaia DR3 cone (matching parallax + PM), WDS.
  (3) Gaia non_single_star / RVS SB2 (rv_amplitude_robust, vbroad, ipd) /
      ipd_frac_multi_peak / RUWE / luminous-secondary flag pattern.
  (4) Is Kervella M2_5AU=2.276 + HGCA chi2=61.5 consistent with a *luminous*
      stellar companion of that mass, or does a DARK companion remain required?
      Decisive cross-check: the M2~2.28 Msun A-star's delta-G vs the primary and
      its absolute contribution to G/J/W1; an A-star secondary cannot hide.

Classify companion_class = luminous_stellar / dark_candidate / ambiguous.

Env: /Users/legbatterij/claude_projects/ostinato/.venv/bin/python (no pip-install)
Outputs: /tmp/hd48797_pma.json , /tmp/hd48797_pma_report.md
Reuses canonical SED BB machinery from scripts/wdj205650_sed_2026_05_30.py and the
Gaia/SIMBAD/Vizier fetch idiom from prime3_deepdive / sb1_*_deepdive /
hd182379_pma_darkluminous + hd221469_pma_darkluminous (the direct templates).
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

SID = 5575983077771827584
HD_NAME = 'HD 48797'
CALLER = dict(HGCA_chi2=61.5, snrPMa=7.55, M2_median=2.276, known_multiple=True)

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

def gaia_neighbours(ra, dec, plx, pmra, pmdec, radius_arcsec=30.0):
    """Cone search for resolved companions sharing parallax + PM (common proper motion).
    Returns rows within radius with their plx/PM so we can flag a CPM secondary."""
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
        # CPM test vs target
        if not row['is_target'] and plxi is not None and plx is not None:
            dplx = abs(plxi - plx)
            dpm = (math.hypot((pmrai or 0) - (pmra or 0), (pmdeci or 0) - (pmdec or 0))
                   if (pmrai is not None and pmdeci is not None) else None)
            row['dplx_mas'] = round(dplx, 4)
            row['dpm_masyr'] = (round(dpm, 4) if dpm is not None else None)
            # CPM companion if plx within ~3x its error of target AND dpm small
            row['cpm_candidate'] = bool(dplx < max(0.5, 5.0) and (dpm is not None and dpm < 5.0))
        rows.append(row)
    return {'n_within': len(rows), 'rows': rows[:25]}

# ------------------------------------------------------------------ photometry
# pivot wavelengths (Angstrom), system, Vega->AB offset
BANDS = {
    'GALEX_FUV': (1549.0, 'AB', 0.0),
    'GALEX_NUV': (2304.7, 'AB', 0.0),
    'Gaia_BP'  : (5035.8, 'AB', 0.0),   # Gaia EDR3 BP/G/RP pivot; we treat Gaia mags as ~AB w/ offsets below
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
# Gaia EDR3 Vega->AB offsets (G,BP,RP) from Riello+2021 / SVO; m_AB = m_Vega + off
GAIA_AB_OFF = {'Gaia_G': 0.105, 'Gaia_BP': 0.0292, 'Gaia_RP': 0.3542}

# Fitzpatrick99 R_V=3.1 A_lam/A_V at each pivot
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

    # ---- Gaia DR3 own photometry (from gaia_source we already pulled) ----
    for b, key in (('Gaia_G', 'phot_g_mean_mag'), ('Gaia_BP', 'phot_bp_mean_mag'),
                   ('Gaia_RP', 'phot_rp_mean_mag')):
        m = gs.get(key)
        if isinstance(m, (int, float)):
            # Gaia mags are Vega; convert to AB with the EDR3 offset; small phot error
            out[b] = dict(mag=m + GAIA_AB_OFF[b], err=0.01, system='AB', det='det', src='Gaia DR3')
    prov['Gaia'] = 'gaia_source phot_{g,bp,rp}_mean_mag'

    # ---- GALEX AIS ----
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

    # ---- 2MASS PSC ----
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

    # ---- AllWISE ----
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
    """Kervella+2022 H2G2 PMa catalog (J/A+A/657/A7) -- M2_5AU, snrPMa, primary mass."""
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
    """Washington Double Star catalog (B/wds/wds)."""
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
    # bibcodes
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

# anchors used to FIT the single-star primary: optical+NIR detections, exclude UV
# (independent test) and WISE W3/W4 (low S/N) and 2MASS UL.
ANCHOR_BANDS = ['Gaia_BP', 'Gaia_G', 'Gaia_RP', '2MASS_J', '2MASS_H', '2MASS_K',
                'WISE_W1', 'WISE_W2']

def fit_primary(phot, d_pc, A_V, T_lo=4000, T_hi=15000):
    bands = [b for b in ANCHOR_BANDS if b in phot and phot[b]['det'] == 'det']
    lam = np.array([BANDS[b][0] for b in bands])
    obs = np.array([deredden_ab(b, to_ab(b, phot[b]), A_V) for b in bands])
    err = np.array([max(phot[b]['err'], 0.02) for b in bands])
    err = np.sqrt(err**2 + 0.03**2)   # cross-survey + BB-vs-atmosphere floor

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
    """Add a companion BB (T2,R2), RE-OPTIMISE primary radius against the detected
    anchors, then report band-by-band sigma of (primary+companion) vs primary-alone.
    A grey flux offset is absorbed by R1; only SED-shape distortion discriminates.
    Returns worst real-detection tension and total delta-chi2."""
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
# Pecaut & Mamajek (2013) main-sequence: SpT -> (Teff K, R_sun, M_sun, M_G abs).
# M_G computed from Mamajek M_V + Gaia (G-V)~ -0.1..-0.4; we instead derive companion
# absolute G self-consistently from its BB (T2,R2) at d, which is what the SED test uses.
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

# ------------------------------------------------------------------ verdict logic
def classify(result):
    """Synthesise companion_class from the 4 evidence channels.

    Decision ladder (skepticism-first; HD157033/Pile-A precedent):
      * If a luminous MS companion at ~M2_median is EXCLUDED by the SED (it would
        over-brighten a detected band at high sigma / contribute a large G flux
        fraction that is not seen) AND the primary SED is single-star clean
        (redchi2 ~1, no UV/IR excess) AND no resolved/CPM luminous neighbour ->
        the accelerating mass is DARK -> dark_candidate.
      * If the SED is consistent with (or requires) a 2nd luminous star at the
        Kervella mass (an A/F secondary that fits within the photometric errors,
        OR a resolved CPM companion, OR Gaia luminous-secondary / SB2 flags) ->
        luminous_stellar (ordinary binary -> rejected).
      * Otherwise ambiguous.
    """
    em = result['kervella_M2med_companion']
    fit = result['primary_fit']
    gs = result['gaia_source']
    neigh = result['gaia_neighbours']
    M2 = result['caller_inputs']['M2_median']

    redchi2 = fit.get('redchi2')
    # SED single-star quality
    sed_single_star_clean = (redchi2 is not None and redchi2 < 5.0)

    # Is the M2_median luminous A-star EXCLUDED by the SED?
    worst_sig = em['best']['sigma'] if em.get('best') else 0.0
    Gff = em.get('G_flux_frac') or 0.0
    dchi2 = em.get('delta_chi2') or 0.0
    # An A-star at 2-3 Msun contributes a large fraction of G flux unless the
    # primary is hugely more luminous. EXCLUDED if it would distort a detected
    # band strongly (>3 sigma) or blow up the fit (delta-chi2 large +ve) while
    # also contributing a non-trivial flux fraction (>~8%).
    lum_comp_excluded = bool((worst_sig >= 3.0 or dchi2 >= 9.0) and Gff >= 0.05)

    # Resolved / CPM luminous companion?
    cpm_lum = False
    if isinstance(neigh, dict) and 'rows' in neigh:
        for r in neigh['rows']:
            if r.get('cpm_candidate') and not r.get('is_target'):
                # luminous if it is a real Gaia star at comparable brightness/sep
                cpm_lum = True
    wds_match = bool(result.get('wds', {}).get('match'))

    # Gaia spectroscopic/astrometric SB2 / luminous-secondary indicators
    ipd_mp = gs.get('ipd_frac_multi_peak')
    nss_present = result.get('nss') is not None
    nss_type = (result['nss'].get('nss_solution_type') if nss_present else None)
    sb2_like = bool((ipd_mp is not None and ipd_mp >= 2) or
                    (nss_type is not None and 'SB2' in str(nss_type)))

    # ---- ladder ----
    flags = dict(sed_single_star_clean=sed_single_star_clean,
                 lum_comp_excluded=lum_comp_excluded,
                 worst_sig_at_M2med=round(worst_sig, 2), G_flux_frac_at_M2med=Gff,
                 delta_chi2_at_M2med=dchi2,
                 cpm_luminous_neighbour=cpm_lum, wds_match=wds_match,
                 sb2_like=sb2_like, ipd_frac_multi_peak=ipd_mp,
                 nss_present=nss_present, nss_type=nss_type)

    if cpm_lum or wds_match or sb2_like:
        cls = 'luminous_stellar'
        why = ('A resolved/CPM Gaia neighbour or WDS pair or Gaia SB2 indicator '
               'points to a SEPARATE luminous star producing the acceleration.')
    elif lum_comp_excluded and sed_single_star_clean:
        cls = 'dark_candidate'
        why = (f'SED is single-star (redchi2={redchi2}); a luminous ~{M2} Msun A-star '
               f'companion is EXCLUDED (worst {worst_sig:.1f}sigma, would supply '
               f'{Gff*100:.0f}% of G flux). The PMa/HGCA acceleration therefore '
               f'requires a DARK companion of compact-object/heavy-WD mass.')
    elif not lum_comp_excluded:
        # the A-star is NOT excluded by the SED -> ordinary luminous binary
        cls = 'luminous_stellar'
        why = (f'A luminous ~{M2} Msun A/F companion is NOT excluded by the SED '
               f'(worst {worst_sig:.1f}sigma, G flux frac {Gff*100:.0f}%); the '
               f'acceleration is consistent with an ordinary stellar secondary.')
    else:
        cls = 'ambiguous'
        why = ('Evidence is mixed: SED quality or companion-exclusion is '
               'inconclusive; needs a direct RV epoch / deeper imaging.')

    return cls, bool(cls == 'dark_candidate'), why, flags


def write_report(result, cls, dark, why, flags):
    sid = result['source_id']; hd = result['hd_name']
    ci = result['caller_inputs']; fit = result['primary_fit']; gs = result['gaia_source']
    em = result['kervella_M2med_companion']; kerv = result.get('kervella', {})
    d = result['distances']; ext = result['extinction']; lit = result['primary_lit']
    sim = result.get('simbad', {}); nss = result.get('nss')
    L = []
    L.append(f"# {hd} / Gaia DR3 {sid} -- PMa dark-vs-luminous vetting\n")
    L.append(f"**Verdict: companion_class = `{cls}`  (dark={dark})**\n")
    L.append(f"> {why}\n")
    L.append("## Caller inputs")
    L.append(f"- HGCA chi2 = {ci['HGCA_chi2']}, Kervella snrPMa = {ci['snrPMa']}, "
             f"M2_median (Kervella M2_5AU MC) = {ci['M2_median']} Msun, "
             f"known_multiple = {ci['known_multiple']}\n")
    L.append("## (0) Identity / distance / primary")
    L.append(f"- SIMBAD: main_id={sim.get('main_id')}, otype={sim.get('otype')}, "
             f"sp_type={sim.get('sp_type')}, V={sim.get('V')}, n_bibcodes={sim.get('n_bibcodes')}")
    L.append(f"- plx(GS)={d.get('plx_gs')} mas, plx(NSS)={d.get('plx_nss')}, "
             f"d_used={d.get('d_used_pc')} pc; A_V={ext.get('A_V')} ({ext.get('ag_source')})")
    L.append(f"- Primary single-BB fit: T1={fit['T1']:.0f}+/-{fit['T1_err']:.0f} K, "
             f"R1={fit['R1_rsun']} Rsun, L1={fit['L1_lsun']} Lsun, "
             f"redchi2={fit['redchi2']} (n_anchor={len(fit['anchor_bands'])}); M_G={fit['M_G_primary']}")
    L.append(f"- Primary lit: mass_flame={lit['mass_flame']}, teff_gspphot={lit['teff_gspphot']}, "
             f"logg_gspphot={lit['logg_gspphot']}, radius_flame={lit['radius_flame']}, "
             f"lum_flame={lit['lum_flame']}, SpT_esphs={lit['spectraltype_esphs']}\n")
    L.append("## (1) SED 2-component test -- is a luminous companion required or excluded?")
    L.append(f"- Primary-fit per-band residuals (obs-model, dered AB): "
             + ", ".join(f"{k}={v:+.3f}" for k, v in fit['resid'].items()))
    L.append(f"- **Kervella M2_median companion ({ci['M2_median']} Msun, "
             f"T2={em.get('T2_assumed')} K, R2={em.get('R2_assumed')} Rsun, "
             f"L2={em.get('L2_Lsun')} Lsun, ~A-star):**")
    L.append(f"  - companion G-band flux fraction = {em.get('G_flux_frac')}  "
             f"(dG = {em.get('delta_G_comp_minus_pri')} mag vs primary)")
    L.append(f"  - worst real-detection SED tension = "
             f"{em['best']['sigma'] if em.get('best') else 0:.1f} sigma @ "
             f"{em['best']['band'] if em.get('best') else '-'}  (delta-chi2={em.get('delta_chi2')})")
    L.append("  - per-band obs vs primary-only vs primary+A-companion:")
    for r in em['rows']:
        L.append(f"    - {r['band']:9s} det={r['det']:3s} obs={r['obs']:+8.3f} "
                 f"m_pri={r['m_pri']:+8.3f} m_tot={r['m_tot']:+8.3f} "
                 f"ff={r['flux_frac']:.3f} sig={r['sigma']:+.2f}")
    L.append("\n- MS-companion grid (worst detected-band sigma / G flux frac per SpT):")
    L.append(f"  | SpT | T2 | R2 | G_ff | dG | maxFF | worst_sig | band | dChi2 |")
    L.append(f"  |---|---|---|---|---|---|---|---|---|")
    for e in result['ms_companion_exclusion']:
        b = e['best']; bs = b['sigma'] if b else 0.0; bn = b['band'] if b else '-'
        dG = e['delta_G_comp_minus_pri'] if e['delta_G_comp_minus_pri'] is not None else 0.0
        L.append(f"  | {e['label']} | {e['T2']:.0f} | {e['R2']:.2f} | {e['G_flux_frac']:.3f} | "
                 f"{dG:.2f} | {e['max_flux_frac_det']:.3f} | {bs:.1f} | {bn} | {e['delta_chi2']:.1f} |")
    L.append("\n## (2) Resolved / wide companion")
    wds = result.get('wds', {})
    L.append(f"- WDS: {('MATCH n=%d' % wds['n_rows']) if wds.get('match') else 'no entry within 15 arcsec'}")
    neigh = result['gaia_neighbours']
    if isinstance(neigh, dict) and 'rows' in neigh:
        L.append(f"- Gaia DR3 cone (30 arcsec): {neigh['n_within']} sources")
        for r in neigh['rows']:
            tag = 'TARGET' if r.get('is_target') else ''
            cpm = ' <-- CPM candidate' if r.get('cpm_candidate') else ''
            L.append(f"  - sep={r['sep_arcsec']} arcsec G={r['G']} plx={r['parallax']} "
                     f"pmra={r['pmra']} pmdec={r['pmdec']} dplx={r.get('dplx_mas','-')} "
                     f"dpm={r.get('dpm_masyr','-')} {tag}{cpm}")
    L.append("\n## (3) Gaia multiplicity flags")
    L.append(f"- non_single_star={gs.get('non_single_star')}, RUWE={gs.get('ruwe')}, "
             f"ipd_frac_multi_peak={gs.get('ipd_frac_multi_peak')}%, "
             f"ipd_frac_odd_win={gs.get('ipd_frac_odd_win')}%")
    L.append(f"- astrom_excess_noise={gs.get('astrometric_excess_noise')} "
             f"(sig={gs.get('astrometric_excess_noise_sig')}), "
             f"phot_bp_rp_excess={gs.get('phot_bp_rp_excess_factor')}")
    L.append(f"- rv_amplitude_robust={gs.get('rv_amplitude_robust')} km/s "
             f"(K1~{(gs.get('rv_amplitude_robust') or 0)/2:.2f}), "
             f"vbroad={gs.get('vbroad')}+/-{gs.get('vbroad_error')} km/s, "
             f"RV={gs.get('radial_velocity')}+/-{gs.get('radial_velocity_error')} "
             f"(nb={gs.get('rv_nb_transits')})")
    L.append(f"- NSS row present={nss is not None} "
             f"({nss.get('nss_solution_type') if nss else '-'})")
    L.append("\n## (4) Kervella M2_5AU + HGCA chi2 -- luminous or dark?")
    L.append(f"- Kervella catalog match: {kerv.get('match')}")
    if kerv.get('match'):
        for k in ('sep_arcsec', 'HD', 'HIP', 'Mass', 'e_Mass', 'M2-5', 'b_M2-5', 'B_M2-5',
                  'M2-3', 'M2-10', 'dVt', 'e_dVt', 'snrPMaH2G2', 'snrPMaHG1', 'Plx'):
            if k in kerv:
                L.append(f"  - {k} = {kerv.get(k)}")
    L.append("\n## Decision flags")
    for k, v in flags.items():
        L.append(f"- {k} = {v}")
    with open(f'/tmp/{REPORT_STEM}_report.md', 'w') as f:
        f.write("\n".join(L) + "\n")


# ------------------------------------------------------------------ main
REPORT_STEM = 'hd48797_pma'

def run():
    print('=' * 78)
    print(f'GAIA DR3 {SID} = {HD_NAME} -- PMa dark-vs-luminous companion vetting')
    print('=' * 78)

    gs = gaia_source(SID)
    ra = gs.get('ra'); dec = gs.get('dec')
    print(f"  RA,Dec = {ra},{dec}")
    ap = gaia_ap(SID); aps = gaia_ap_supp(SID); nss = gaia_nss(SID)

    sim = simbad_otype_bibs(f'Gaia DR3 {SID}', hd_name=HD_NAME)
    hd_name = HD_NAME

    phot, prov = fetch_photometry(ra, dec, gs)
    kerv = fetch_kervella(ra, dec)
    hgca = fetch_hgca(ra, dec)
    wds = fetch_wds(ra, dec)
    neigh = gaia_neighbours(ra, dec, gs.get('parallax'), gs.get('pmra'), gs.get('pmdec'))

    # ---- distance & extinction ----
    plx_gs = gs.get('parallax')
    plx_nss = nss.get('parallax') if nss else None
    d_gs = 1000.0 / plx_gs if plx_gs else None
    d_pc = d_gs
    # extinction from Gaia AG if present, else SFD-ish via (l,b)
    ag = gs.get('ag_gspphot') or (ap.get('ag_gspphot') if ap else None)
    A_V = ag if (ag and ag > 0) else 0.10   # default modest A_V; this is a bright nearby HD star
    EBV = A_V / 3.1

    # ---- single-star primary fit ----
    fit = fit_primary(phot, d_pc, A_V)
    T1, R1 = fit['T1'], fit['R1']
    L1 = 4 * math.pi * (R1 * RSUN_M)**2 * SIGMA_SB * T1**4 / LSUN_W
    M_G_primary = None
    if gs.get('phot_g_mean_mag') and plx_gs:
        M_G_primary = gs['phot_g_mean_mag'] + 5 * math.log10(plx_gs / 1000.0) + 5 - (A_V * ALAM_AV['Gaia_G'])

    # FLAME / spectroscopic primary mass
    M1_flame = ap.get('mass_flame') if ap else None
    teff_p = (ap.get('teff_gspphot') if ap else None) or gs.get('teff_gspphot')
    logg_p = (ap.get('logg_gspphot') if ap else None) or gs.get('logg_gspphot')
    R_flame = ap.get('radius_flame') if ap else None
    L_flame = ap.get('lum_flame') if ap else None

    # ---- 2-component SED: luminous MS-companion grid ----
    # test bands span UV->IR; a luminous A/F companion brightens BLUE bands, a K/M
    # companion brightens RED/IR. Use all detections.
    all_bands = [b for b in phot]
    excl = []
    for (spt, T2, R2, MG2) in MS_GRID:
        e = companion_excess_sigma(phot, fit, d_pc, A_V, T2, R2, all_bands, spt)
        # companion absolute/apparent G from its own BB, and delta-G vs primary
        f2_G = fnu_blackbody(BANDS['Gaia_G'][0], T2, R2, d_pc)
        f1_G = fnu_blackbody(BANDS['Gaia_G'][0], T1, R1, d_pc)
        e['G_flux_frac'] = round(f2_G / (f1_G + f2_G), 4)
        e['delta_G_comp_minus_pri'] = (round(-2.5 * math.log10(f2_G / f1_G), 3) if f1_G > 0 else None)
        excl.append(e)

    # ---- Kervella M2 sanity vs a luminous A-star ----
    # M2_median (caller) = 2.276 -> approx A2-A3V (Teff~8400-8800, R~1.9-2.05).
    # Build that specific companion and report its G/J/W1 flux fraction.
    M2_med = CALLER['M2_median']
    # MS_GRID tuples are (SpT, Teff_K, R_sun, M_G_abs); there is no M_sun column.
    # Map SpT -> M_sun via Pecaut & Mamajek, then interpolate Teff/R at M2_med.
    SPT_MASS = {'B8V':3.38,'B9V':3.00,'A0V':2.60,'A1V':2.40,'A2V':2.20,'A5V':1.92,'A7V':1.78,
                'F0V':1.59,'F5V':1.33,'G0V':1.06,'G5V':0.97,'K0V':0.88,'K5V':0.70,'M0V':0.59,
                'M2V':0.44,'M4V':0.20}
    # build mass-sorted arrays from SPT_MASS + grid Teff/R
    rows_sorted = sorted(MS_GRID, key=lambda g: SPT_MASS[g[0]])
    m_s = np.array([SPT_MASS[g[0]] for g in rows_sorted])
    t_s = np.array([g[1] for g in rows_sorted])
    r_s = np.array([g[2] for g in rows_sorted])
    T2_med = float(np.interp(M2_med, m_s, t_s))
    R2_med = float(np.interp(M2_med, m_s, r_s))
    # if M2_med exceeds grid top, extrapolate gently
    if M2_med > m_s.max():
        T2_med = float(t_s[-1]); R2_med = float(r_s[-1])
    e_med = companion_excess_sigma(phot, fit, d_pc, A_V, T2_med, R2_med, all_bands,
                                   f'M2med_{M2_med}Msun_A')
    f2_G = fnu_blackbody(BANDS['Gaia_G'][0], T2_med, R2_med, d_pc)
    f1_G = fnu_blackbody(BANDS['Gaia_G'][0], T1, R1, d_pc)
    e_med['G_flux_frac'] = round(f2_G / (f1_G + f2_G), 4)
    e_med['delta_G_comp_minus_pri'] = round(-2.5 * math.log10(f2_G / f1_G), 3) if f1_G > 0 else None
    e_med['T2_assumed'] = round(T2_med, 0); e_med['R2_assumed'] = round(R2_med, 3)
    e_med['L2_Lsun'] = round(4 * math.pi * (R2_med * RSUN_M)**2 * SIGMA_SB * T2_med**4 / LSUN_W, 2)

    # ---- assemble ----
    result = dict(
        source_id=SID, hd_name=hd_name, ra=ra, dec=dec,
        caller_inputs=dict(HGCA_chi2=CALLER['HGCA_chi2'], snrPMa=CALLER['snrPMa'],
                           M2_median=CALLER['M2_median'],
                           known_multiple=CALLER['known_multiple']),
        distances=dict(plx_gs=plx_gs, plx_nss=plx_nss, d_gs_pc=(round(d_gs, 2) if d_gs else None),
                       d_used_pc=(round(d_pc, 2) if d_pc else None)),
        extinction=dict(A_V=round(A_V, 3), EBV=round(EBV, 3), ag_source=('gspphot' if ag else 'default')),
        gaia_source=gs, gaia_ap=ap, gaia_ap_supp=aps, nss=nss,
        primary_fit=dict(T1=round(T1, 0), T1_err=round(fit['T1_err'], 0), R1_rsun=round(R1, 4),
                         L1_lsun=round(L1, 3), chi2=round(fit['chi2'], 2), ndof=fit['ndof'],
                         redchi2=round(fit['chi2'] / max(fit['ndof'], 1), 2),
                         M_G_primary=(round(M_G_primary, 3) if M_G_primary else None),
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
        kervella=kerv, hgca=hgca, wds=wds, gaia_neighbours=neigh, simbad=sim,
    )

    with open(f'/tmp/{REPORT_STEM}.json', 'w') as f:
        json.dump(result, f, indent=2, default=str)

    # ---- console summary ----
    print("\n================ DISTANCE / PRIMARY ================")
    print(f"  plx(GS)={plx_gs} mas -> d={d_gs:.1f} pc  (plx_NSS={plx_nss})")
    print(f"  A_V={A_V:.3f} ({'gspphot' if ag else 'default'})  RUWE={gs.get('ruwe')}")
    print(f"  primary single-BB fit: T1={T1:.0f}+/-{fit['T1_err']:.0f} K, R1={R1:.3f} Rsun, "
          f"L1={L1:.2f} Lsun ; redchi2={fit['chi2']/max(fit['ndof'],1):.2f} (n={len(fit['bands'])})")
    print(f"  M_G(primary)={M_G_primary}  mass_flame={M1_flame}  teff_gspphot={teff_p} "
          f"logg_gspphot={logg_p}  R_flame={R_flame}  L_flame={L_flame}")
    print(f"  SIMBAD: main_id={sim.get('main_id')} otype={sim.get('otype')} "
          f"sp_type={sim.get('sp_type')} V={sim.get('V')} n_bib={sim.get('n_bibcodes')}")
    print("  primary-fit per-band residuals (obs-model, dered AB):")
    for b in fit['bands']:
        print(f"      {b:10s} {fit['resid'][b]:+.3f}")

    print("\n================ GAIA MULTIPLICITY FLAGS ================")
    print(f"  non_single_star      = {gs.get('non_single_star')}")
    print(f"  RUWE                 = {gs.get('ruwe')}")
    print(f"  ipd_frac_multi_peak  = {gs.get('ipd_frac_multi_peak')} %")
    print(f"  ipd_frac_odd_win     = {gs.get('ipd_frac_odd_win')} %")
    print(f"  astrom_excess_noise  = {gs.get('astrometric_excess_noise')} (sig={gs.get('astrometric_excess_noise_sig')})")
    print(f"  rv_amplitude_robust  = {gs.get('rv_amplitude_robust')} km/s  (K1~{(gs.get('rv_amplitude_robust') or 0)/2:.2f})")
    print(f"  vbroad               = {gs.get('vbroad')} +/- {gs.get('vbroad_error')} km/s")
    print(f"  radial_velocity      = {gs.get('radial_velocity')} +/- {gs.get('radial_velocity_error')} "
          f"(nb_transits={gs.get('rv_nb_transits')})")
    print(f"  phot_bp_rp_excess    = {gs.get('phot_bp_rp_excess_factor')}")
    print(f"  NSS row present      = {nss is not None} ({nss.get('nss_solution_type') if nss else '-'})")

    print("\n================ 2-COMPONENT SED: LUMINOUS MS COMPANION GRID ================")
    print("  (primary R refit per companion; sigma = worst real-detection colour residual;")
    print("   G_ff = companion fraction of system G-band flux; dG = m_G,comp - m_G,pri)")
    print(f"  {'SpT':5s} {'T2':>6s} {'R2':>5s} {'G_ff':>6s} {'dG':>6s} {'maxFF':>6s} {'worst_sig':>10s} {'band':>9s} {'dX2':>8s}")
    for e in excl:
        b = e['best']
        bs = b['sigma'] if b else 0.0; bn = b['band'] if b else '-'
        print(f"  {e['label']:5s} {e['T2']:6.0f} {e['R2']:5.2f} {e['G_flux_frac']:6.3f} "
              f"{(e['delta_G_comp_minus_pri'] if e['delta_G_comp_minus_pri'] is not None else 0):6.2f} "
              f"{e['max_flux_frac_det']:6.3f} {bs:10.1f} {bn:>9s} {e['delta_chi2']:8.1f}")

    print(f"\n================ KERVELLA M2_median COMPANION ({M2_med} Msun A-star) ================")
    em = e_med
    print(f"  Assumed luminous companion at M2={M2_med} Msun: SpT~A2-A3V, T2={em['T2_assumed']:.0f} K, "
          f"R2={em['R2_assumed']} Rsun, L2={em['L2_Lsun']} Lsun")
    print(f"  -> companion G-band flux fraction = {em['G_flux_frac']:.3f}  "
          f"(dG = {em['delta_G_comp_minus_pri']} mag vs primary)")
    print(f"  -> worst real-detection SED tension = {em['best']['sigma'] if em['best'] else 0:.1f} sigma "
          f"@ {em['best']['band'] if em['best'] else '-'}  (delta-chi2={em['delta_chi2']})")
    print("  per-band (obs vs primary-only vs primary+A-companion):")
    for r in em['rows']:
        print(f"      {r['band']:10s} det={r['det']:3s} obs={r['obs']:+8.3f} "
              f"m_pri={r['m_pri']:+8.3f} m_tot={r['m_tot']:+8.3f} ff={r['flux_frac']:.3f} sig={r['sigma']:+.2f}")

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

    # ---- verdict ----
    cls, dark, why, flags = classify(result)
    result['verdict'] = dict(companion_class=cls, dark=dark, rationale=why, flags=flags)
    with open(f'/tmp/{REPORT_STEM}.json', 'w') as f:
        json.dump(result, f, indent=2, default=str)
    write_report(result, cls, dark, why, flags)

    print("\n================ VERDICT ================")
    print(f"  companion_class = {cls}   (dark={dark})")
    print(f"  rationale: {why}")
    print("  flags:")
    for k, v in flags.items():
        print(f"      {k:28s} = {v}")

    print(f"\nJSON   -> /tmp/{REPORT_STEM}.json")
    print(f"REPORT -> /tmp/{REPORT_STEM}_report.md")
    return result

if __name__ == '__main__':
    run()
