#!/usr/bin/env python3
"""Dark-vs-luminous companion vetting of the PMa-corroborated accelerating source
Gaia DR3 5255177676822697216 = HD 91155 (2026-05-31).

Caller context: HGCA chi2=90.1, Kervella snrPMa=8.55, M2_median (Kervella/accel
grid) = 2.428 Msun, SIMBAD HD 91155, known_multiple=false.

Recon (this run) established:
  - nss_solution_type = Acceleration9 (PM-acceleration only; NO Thiele-Innes
    orbit -> period UNCONSTRAINED, M2 is period-degenerate). The caller's
    M2_median=2.428 is the *median over a log-P 3-100 yr grid at M1=1.5*, NOT a
    measurement. With the correct FLAME M1=1.19 the grid median is 2.344.
  - Primary is a LATE-F / EARLY-G DWARF: FLAME M1=1.187 Msun, Teff~6100-6235 K,
    logg~4.2, L~2.5 Lsun, R~1.35 Rsun, spectraltype_esphs=F, G=8.462, d~88 pc.
  - RUWE = 18.28 (!!), astrometric_excess_noise_sig = 9174, non_single_star=1,
    rv_amplitude_robust=15.6 km/s (K1~7.8), rv_chisq_pvalue=0, rv_renorm_gof=23.9
    -> a real, strongly-perturbing companion, astrometrically + spectroscopically.

The decisive question is the SED. With M1~1.19 Msun, a 2-5 Msun MS companion is
MORE LUMINOUS THAN THE PRIMARY -- an early-A / late-B star (Teff 8500-15000 K)
that would dominate the blue/UV and roughly DOUBLE-to-quadruple the optical flux.
It cannot hide. Even a ~1.4-2 Msun A-F companion is conspicuous on a G dwarf. So:

  (1) SED 2-component fit (GALEX/Gaia/2MASS/WISE): fit a single-star primary BB to
      the optical+IR anchors; then test, band by band with full errors, whether a
      luminous A/B/F/G/K/M MS companion (grid 0.2-3.4 Msun) is REQUIRED or EXCLUDED.
      Is the SED single-star, or does a 2nd luminous star appear? (HD157033/Pile-A
      precedent: 7 of 8 HGCA candidates demoted as Kervella H2G2 luminous companions.)
  (2) Resolved / wide companion: Gaia DR3 cone (matching parallax+PM), WDS.
  (3) Gaia non_single_star / RVS variability / ipd_frac_multi_peak / RUWE pattern.
  (4) Is Kervella M2_5AU=2.428 (a grid artifact) + HGCA chi2=90.1 consistent with a
      *luminous* companion of that mass, or does a DARK companion remain required?
      We map M2(P) from the measured |a|, and ask: at the period that produces
      M2~2.4 Msun, is that companion SED-hidden (NO) or conspicuous (YES)? And what
      M2 is implied at the period where a luminous companion WOULD be hidden?

Classify companion_class = luminous_stellar / dark_candidate / ambiguous.

Env: /Users/legbatterij/claude_projects/ostinato/.venv/bin/python (no pip-install)
Outputs: /tmp/hd91155_pma.json , /tmp/hd91155_pma_report.md
Reuses SED BB machinery + Gaia/SIMBAD/Vizier idiom from
scripts/hd182379_pma_darkluminous_2026_05_31.py and the v3 acceleration inversion
from scripts/streaming/v3_acceleration/acceleration_inversion.py.
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
from acceleration_inversion import (M2_from_acceleration, M2_range,
                                    acceleration_magnitude, acceleration_magnitude_error)

# ------------------------------------------------------------------ constants
H_PLANCK = 6.62607015e-34
C_LIGHT  = 2.99792458e8
K_BOLTZ  = 1.380649e-23
SIGMA_SB = 5.670374419e-8
RSUN_M   = 6.957e8
LSUN_W   = 3.828e26
PC_M     = 3.0856775815e16
ZP_AB    = 3631.0

SID = 5255177676822697216
HD_NAME = 'HD 91155'
# caller-stated inputs
CALLER = dict(HGCA_chi2=90.1, snrPMa=8.55, M2_median=2.428, known_multiple=False)

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
            'rv_nb_transits, rv_expected_sig_to_noise, rv_renormalised_gof, rv_chisq_pvalue, '
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

def gaia_accel(sid):
    def go():
        return Gaia.launch_job(f'SELECT * FROM gaiadr3.nss_acceleration_astro WHERE source_id={sid}').get_results()
    t = _with_timeout(go, 60, None)
    return _tab_to_dict(t) if (t is not None and len(t)) else {}

def gaia_nss(sid):
    def go():
        return Gaia.launch_job(f'SELECT * FROM gaiadr3.nss_two_body_orbit WHERE source_id={sid}').get_results()
    t = _with_timeout(go, 60, None)
    return _tab_to_dict(t) if (t is not None and len(t)) else None

def gaia_neighbours(ra, dec, plx, pmra, pmdec, radius_arcsec=60.0):
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
            # CPM companion: plx within ~3 mas AND dpm small relative to total PM
            totpm = math.hypot(pmra or 0, pmdec or 0)
            row['cpm_candidate'] = bool(dplx < max(0.5, 3.0 * (plxi and (_flt(t['parallax_error'][i]) or 0.1) or 0.1))
                                        and (dpm is not None and dpm < 0.2 * totpm + 3.0))
        rows.append(row)
    return {'n_within': len(rows), 'radius_arcsec': radius_arcsec, 'rows': rows[:30]}

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

    # ---- Gaia DR3 own photometry ----
    for b, key in (('Gaia_G', 'phot_g_mean_mag'), ('Gaia_BP', 'phot_bp_mean_mag'),
                   ('Gaia_RP', 'phot_rp_mean_mag')):
        m = gs.get(key)
        if isinstance(m, (int, float)):
            out[b] = dict(mag=m + GAIA_AB_OFF[b], err=0.01, system='AB', det='det', src='Gaia DR3')
    prov['Gaia'] = 'gaia_source phot_{g,bp,rp}_mean_mag'

    # ---- GALEX AIS (II/335) then DR5 (II/312) backup ----
    r = vquery('II/335/galex_ais', 8)
    got_galex = False
    if r and len(r):
        t = r[0]; i = int(np.argmin(t['_r']))
        for b, col in (('GALEX_FUV', 'FUVmag'), ('GALEX_NUV', 'NUVmag')):
            m = _flt(t[col][i]); e = _flt(t['e_' + col][i])
            if m is not None:
                out[b] = dict(mag=m, err=(e or 0.15), system='AB', det='det', src='II/335 GALEX-AIS')
                got_galex = True
        prov['GALEX'] = f"II/335 sep={float(t['_r'][i]):.2f}\""
    if not got_galex:
        r = vquery('II/312/ais', 8)
        if r and len(r):
            t = r[0]; i = int(np.argmin(t['_r']))
            for b, col in (('GALEX_FUV', 'FUV'), ('GALEX_NUV', 'NUV')):
                m = _flt(t[col][i]); e = _flt(t.get('e_' + col, t[col])[i] if ('e_' + col) in t.colnames else None)
                if m is not None:
                    out[b] = dict(mag=m, err=(e or 0.15), system='AB', det='det', src='II/312 GALEX-DR5')
                    got_galex = True
            prov['GALEX'] = (prov.get('GALEX', '') + f" | II/312 sep={float(t['_r'][i]):.2f}\"")
    if not got_galex:
        prov['GALEX'] = 'no GALEX match within 8\" (no UV detection)'

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
    """Kervella+2022 H2G2 PMa catalog (J/A+A/657/A7)."""
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
    return out

def fetch_hgca(ra, dec):
    """Brandt 2021 HGCA (J/ApJS/254/42)."""
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
    r = _with_timeout(lambda: v.query_region(co, radius=30 * u.arcsec, catalog='B/wds/wds'), 60, None)
    if not r or len(r) == 0:
        return {'match': False}
    t = r[0]
    rows = []
    for i in range(min(len(t), 8)):
        rows.append({c: (_flt(t[c][i]) if _flt(t[c][i]) is not None else str(t[c][i]))
                     for c in ('WDS', 'Disc', 'Comp', 'Obs1', 'Obs2', 'sep1', 'sep2',
                               'pa1', 'pa2', 'mag1', 'mag2', 'SpType') if c in t.colnames})
    return {'match': True, 'n_rows': len(t), 'rows': rows}

def lit_crossmatch(ra, dec):
    co = SkyCoord(ra, dec, unit='deg')
    cats = [
        ('J/MNRAS/518/2991', 'Shahaf+2023 Triage I (compact-companion)'),
        ('J/MNRAS/529/3729', 'Shahaf+2024 Triage II (WD census)'),
        ('J/A+A/674/A9', 'Gaia DR3 NSS astrometric orbits (Halbwachs 2023)'),
    ]
    out = {}
    for cat, label in cats:
        def go():
            v = Vizier(columns=['**'], row_limit=-1)
            return v.query_region(co, radius=5 * u.arcsec, catalog=cat)
        r = _with_timeout(go, 45, None)
        if r is None:
            out[label] = {'match': None}
        elif len(r) == 0:
            out[label] = {'match': False}
        else:
            t = r[0]
            out[label] = {'match': True, 'n_rows': int(len(t))}
    return out

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
                                    'title': str(row['title'])[:95]} for row in t][:40]
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
    """Add companion BB (T2,R2), RE-OPTIMISE primary radius against detected anchors,
    then report band-by-band sigma of (primary+companion) vs primary-alone. A grey
    flux offset is absorbed by R1; only SED-shape distortion discriminates."""
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
        if abs(row['sigma']) > 0 and (best is None or abs(row['sigma']) > abs(best['sigma'])):
            best = row
    maxff = round(max((r['flux_frac'] for r in rows if r['det'] == 'det'), default=0.0), 3)
    return dict(label=label, T2=T2, R2=round(R2, 4), R1_refit=round(R1, 5),
                delta_chi2=round(chi2_comp - chi2_pri, 1), max_flux_frac_det=maxff,
                best=best, rows=rows)

# ------------------------------------------------------------------ MS companion grid
# Pecaut & Mamajek (2013) main-sequence: SpT -> (Teff K, R_sun, M_sun).
MS_GRID = [
    ('B8V', 11400, 2.49, 3.38),
    ('B9V', 10600, 2.30, 3.00),
    ('A0V', 9700,  2.19, 2.60),
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
SPT_MASS = {g[0]: g[3] for g in MS_GRID}

# ------------------------------------------------------------------ main
def run():
    print('=' * 78)
    print(f'GAIA DR3 {SID} = {HD_NAME} -- PMa dark-vs-luminous companion vetting')
    print('=' * 78)

    gs = gaia_source(SID)
    ra = gs.get('ra'); dec = gs.get('dec')
    print(f"  RA,Dec = {ra},{dec}")
    ap = gaia_ap(SID); aps = gaia_ap_supp(SID); nss = gaia_nss(SID); acc = gaia_accel(SID)

    sim = simbad_otype_bibs(f'Gaia DR3 {SID}', hd_name=HD_NAME)

    phot, prov = fetch_photometry(ra, dec, gs)
    kerv = fetch_kervella(ra, dec)
    hgca = fetch_hgca(ra, dec)
    wds = fetch_wds(ra, dec)
    lit = lit_crossmatch(ra, dec)
    neigh = gaia_neighbours(ra, dec, gs.get('parallax'), gs.get('pmra'), gs.get('pmdec'))

    # ---- distance & extinction ----
    plx_gs = gs.get('parallax')
    plx_nss = (acc.get('parallax') if acc else None) or (nss.get('parallax') if nss else None)
    # Correction A: prefer NSS (orbit/accel-fit) parallax over gaia_source single-star plx
    plx_used = plx_nss if (plx_nss and plx_nss > 0) else plx_gs
    plx_src = 'NSS_accel' if (plx_nss and plx_nss > 0) else 'gaia_source'
    d_pc = 1000.0 / plx_used if plx_used else None
    d_gs = 1000.0 / plx_gs if plx_gs else None
    ag = gs.get('ag_gspphot') or (ap.get('ag_gspphot') if ap else None)
    A_V = ag if (ag and ag > 0.001) else 0.05   # very low AG reported; near, low |b| but bright
    EBV = A_V / 3.1

    # ---- single-star primary fit ----
    fit = fit_primary(phot, d_pc, A_V)
    T1, R1 = fit['T1'], fit['R1']
    L1 = 4 * math.pi * (R1 * RSUN_M)**2 * SIGMA_SB * T1**4 / LSUN_W
    M_G_primary = None
    if gs.get('phot_g_mean_mag') and plx_used:
        M_G_primary = gs['phot_g_mean_mag'] + 5 * math.log10(plx_used / 1000.0) + 5 - (A_V * ALAM_AV['Gaia_G'])

    M1_flame = ap.get('mass_flame') if ap else None
    M1 = M1_flame if (M1_flame and M1_flame > 0) else 1.19
    teff_p = (ap.get('teff_gspphot') if ap else None) or gs.get('teff_gspphot')
    logg_p = (ap.get('logg_gspphot') if ap else None) or gs.get('logg_gspphot')
    R_flame = ap.get('radius_flame') if ap else None
    L_flame = ap.get('lum_flame') if ap else None

    # ---- 2-component SED: luminous MS-companion grid ----
    all_bands = [b for b in phot]
    excl = []
    f1_G = fnu_blackbody(BANDS['Gaia_G'][0], T1, R1, d_pc)
    for (spt, T2, R2, M2_spt) in MS_GRID:
        e = companion_excess_sigma(phot, fit, d_pc, A_V, T2, R2, all_bands, spt)
        f2_G = fnu_blackbody(BANDS['Gaia_G'][0], T2, R2, d_pc)
        e['M2_spt'] = M2_spt
        e['G_flux_frac'] = round(f2_G / (f1_G + f2_G), 4)
        e['delta_G_comp_minus_pri'] = (round(-2.5 * math.log10(f2_G / f1_G), 3) if f1_G > 0 else None)
        excl.append(e)

    # ---- Kervella M2_median companion (2.428 Msun) specific test ----
    M2_med = CALLER['M2_median']
    rows_sorted = sorted(MS_GRID, key=lambda g: g[3])
    m_s = np.array([g[3] for g in rows_sorted])
    t_s = np.array([g[1] for g in rows_sorted])
    r_s = np.array([g[2] for g in rows_sorted])
    T2_med = float(np.interp(M2_med, m_s, t_s))
    R2_med = float(np.interp(M2_med, m_s, r_s))
    if M2_med > m_s.max():
        T2_med = float(t_s[-1]); R2_med = float(r_s[-1])
    e_med = companion_excess_sigma(phot, fit, d_pc, A_V, T2_med, R2_med, all_bands,
                                   f'M2med_{M2_med}Msun_A')
    f2_G = fnu_blackbody(BANDS['Gaia_G'][0], T2_med, R2_med, d_pc)
    e_med['G_flux_frac'] = round(f2_G / (f1_G + f2_G), 4)
    e_med['delta_G_comp_minus_pri'] = round(-2.5 * math.log10(f2_G / f1_G), 3) if f1_G > 0 else None
    e_med['T2_assumed'] = round(T2_med, 0); e_med['R2_assumed'] = round(R2_med, 3)
    e_med['L2_Lsun'] = round(4 * math.pi * (R2_med * RSUN_M)**2 * SIGMA_SB * T2_med**4 / LSUN_W, 2)

    # ---- PM-acceleration -> M2(P) map (the period-degeneracy) ----
    accel_mag = acceleration_magnitude(acc.get('accel_ra'), acc.get('accel_dec')) if acc else None
    accel_err = (acceleration_magnitude_error(acc.get('accel_ra'), acc.get('accel_dec'),
                 acc.get('accel_ra_error'), acc.get('accel_dec_error')) if acc else None)
    amap = None; M2_at_P = {}
    if accel_mag and plx_used:
        Pgrid = np.geomspace(1.0, 100.0, 80)
        curve = []
        for P in Pgrid:
            m2 = M2_from_acceleration(accel_mag, plx_used, M1, float(P))
            if m2 is not None:
                a_AU = ((M1 + m2) * P**2)**(1.0 / 3.0)
                curve.append(dict(P_yr=round(float(P), 3), M2_msun=round(float(m2), 4),
                                  a_tot_AU=round(a_AU, 3), sep_mas=round(a_AU * plx_used, 1)))
        def P_at_M2(target):
            for r in curve:
                if r['M2_msun'] >= target:
                    return r['P_yr']
            return None
        for P in (3, 5, 8, 10, 13, 15, 20, 30, 50):
            M2_at_P[f'P{P}yr'] = round(M2_from_acceleration(accel_mag, plx_used, M1, float(P)), 3)
        rng = M2_range(accel_mag, plx_used, M1=M1, P_yr_min=3.0, P_yr_max=100.0)
        amap = dict(accel_mag_mas_yr2=round(accel_mag, 4),
                    accel_err=round(accel_err, 4) if accel_err else None,
                    accel_snr=round(accel_mag / accel_err, 1) if accel_err else None,
                    M1_used=round(M1, 3), plx_used=round(plx_used, 4),
                    M2_at_P=M2_at_P,
                    P_for_M2_1p4=P_at_M2(1.4), P_for_M2_2p0=P_at_M2(2.0),
                    P_for_M2_2p428=P_at_M2(2.428), P_for_M2_3p0=P_at_M2(3.0),
                    M2_range_3_100yr=dict(min=round(rng[0], 3), median=round(rng[1], 3),
                                          max=round(rng[2], 3)) if rng else None,
                    curve=curve)

    # ---- assemble ----
    result = dict(
        source_id=SID, hd_name=HD_NAME, ra=ra, dec=dec,
        caller_inputs=CALLER,
        nss_solution_type=(acc.get('nss_solution_type') if acc else None),
        distances=dict(plx_gs=plx_gs, plx_nss=plx_nss, plx_used=plx_used, plx_src=plx_src,
                       d_gs_pc=(round(d_gs, 2) if d_gs else None),
                       d_used_pc=(round(d_pc, 2) if d_pc else None)),
        extinction=dict(A_V=round(A_V, 3), EBV=round(EBV, 3), ag_source=('gspphot' if ag else 'default')),
        gaia_source=gs, gaia_ap=ap, gaia_ap_supp=aps, nss=nss, gaia_accel=acc,
        primary_fit=dict(T1=round(T1, 0), T1_err=round(fit['T1_err'], 0), R1_rsun=round(R1, 4),
                         L1_lsun=round(L1, 3), chi2=round(fit['chi2'], 2), ndof=fit['ndof'],
                         redchi2=round(fit['chi2'] / max(fit['ndof'], 1), 2),
                         M_G_primary=(round(M_G_primary, 3) if M_G_primary else None),
                         anchor_bands=fit['bands'], resid={k: round(v, 3) for k, v in fit['resid'].items()}),
        primary_lit=dict(mass_flame=M1_flame, M1_used=M1, teff_gspphot=teff_p, logg_gspphot=logg_p,
                         radius_flame=R_flame, lum_flame=L_flame,
                         spectraltype_esphs=(ap.get('spectraltype_esphs') if ap else None),
                         teff_gspspec=(ap.get('teff_gspspec') if ap else None),
                         logg_gspspec=(ap.get('logg_gspspec') if ap else None)),
        photometry={b: dict(mag=round(phot[b]['mag'], 4), err=round(phot[b]['err'], 4),
                            system=phot[b]['system'], det=phot[b]['det'],
                            ab=round(to_ab(b, phot[b]), 4),
                            ab_dered=round(deredden_ab(b, to_ab(b, phot[b]), A_V), 4),
                            src=phot[b]['src']) for b in phot},
        photometry_provenance=prov,
        ms_companion_exclusion=excl,
        kervella_M2med_companion=e_med,
        accel_m2_map=amap,
        kervella=kerv, hgca=hgca, wds=wds, literature=lit, gaia_neighbours=neigh, simbad=sim,
    )

    with open('/tmp/hd91155_pma.json', 'w') as f:
        json.dump(result, f, indent=2, default=str)

    # ---- console summary ----
    print("\n================ DISTANCE / PRIMARY ================")
    print(f"  plx(GS)={plx_gs} mas (d={d_gs:.1f}pc)  plx(NSS)={plx_nss} -> USING {plx_src} plx={plx_used:.3f} d={d_pc:.1f}pc")
    print(f"  A_V={A_V:.3f} ({'gspphot' if ag else 'default'})  RUWE={gs.get('ruwe')}  nss_solution_type={acc.get('nss_solution_type') if acc else '-'}")
    print(f"  primary single-BB fit: T1={T1:.0f}+/-{fit['T1_err']:.0f} K, R1={R1:.3f} Rsun, "
          f"L1={L1:.2f} Lsun ; redchi2={fit['chi2']/max(fit['ndof'],1):.2f} (n={len(fit['bands'])})")
    print(f"  M_G(primary)={M_G_primary}  M1_flame={M1_flame} (M1_used={M1:.2f})  teff_gspphot={teff_p} "
          f"logg_gspphot={logg_p}  R_flame={R_flame}  L_flame={L_flame}  spt_esphs={ap.get('spectraltype_esphs') if ap else None}")
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
    print(f"  rv_chisq_pvalue      = {gs.get('rv_chisq_pvalue')}  rv_renorm_gof={gs.get('rv_renormalised_gof')}")
    print(f"  vbroad               = {gs.get('vbroad')} +/- {gs.get('vbroad_error')} km/s")
    print(f"  radial_velocity      = {gs.get('radial_velocity')} +/- {gs.get('radial_velocity_error')} "
          f"(nb_transits={gs.get('rv_nb_transits')}, exp_S/N={gs.get('rv_expected_sig_to_noise')})")
    print(f"  phot_bp_rp_excess    = {gs.get('phot_bp_rp_excess_factor')}")

    print("\n================ 2-COMPONENT SED: LUMINOUS MS COMPANION GRID ================")
    print("  (primary R refit per companion; sigma = worst real-detection colour residual;")
    print("   G_ff = companion fraction of system G-band flux; dG = m_G,comp - m_G,pri)")
    print(f"  {'SpT':5s} {'M2':>5s} {'T2':>6s} {'R2':>5s} {'G_ff':>6s} {'dG':>6s} {'maxFF':>6s} {'worst_sig':>10s} {'band':>9s} {'dX2':>9s}")
    for e in excl:
        b = e['best']
        bs = b['sigma'] if b else 0.0; bn = b['band'] if b else '-'
        print(f"  {e['label']:5s} {e['M2_spt']:5.2f} {e['T2']:6.0f} {e['R2']:5.2f} {e['G_flux_frac']:6.3f} "
              f"{(e['delta_G_comp_minus_pri'] if e['delta_G_comp_minus_pri'] is not None else 0):6.2f} "
              f"{e['max_flux_frac_det']:6.3f} {bs:10.1f} {bn:>9s} {e['delta_chi2']:9.1f}")

    print("\n================ KERVELLA M2_median COMPANION (2.428 Msun ~A-star) ================")
    em = e_med
    print(f"  Assumed luminous companion at M2={M2_med} Msun: SpT~A0-A2V, T2={em['T2_assumed']:.0f} K, "
          f"R2={em['R2_assumed']} Rsun, L2={em['L2_Lsun']} Lsun")
    print(f"  -> companion G-band flux fraction = {em['G_flux_frac']:.3f}  "
          f"(dG = {em['delta_G_comp_minus_pri']} mag vs primary -- NEGATIVE means companion BRIGHTER)")
    print(f"  -> worst real-detection SED tension = {em['best']['sigma'] if em['best'] else 0:.1f} sigma "
          f"@ {em['best']['band'] if em['best'] else '-'}  (delta-chi2={em['delta_chi2']})")
    print("  per-band (obs vs primary-only vs primary+A-companion):")
    for r in em['rows']:
        print(f"      {r['band']:10s} det={r['det']:3s} obs={r['obs']:+8.3f} "
              f"m_pri={r['m_pri']:+8.3f} m_tot={r['m_tot']:+8.3f} ff={r['flux_frac']:.3f} sig={r['sigma']:+.2f}")

    print("\n================ PM-ACCELERATION -> M2(P) PERIOD-DEGENERACY MAP ================")
    if amap:
        print(f"  |a|={amap['accel_mag_mas_yr2']} mas/yr^2 (S/N={amap['accel_snr']}), M1={amap['M1_used']}, plx={amap['plx_used']}")
        print(f"  M2 at fixed assumed period P:")
        for k, v in amap['M2_at_P'].items():
            print(f"      {k:7s} -> M2 = {v:7.3f} Msun")
        print(f"  Period needed to reach: M2>=1.4 (NS): {amap['P_for_M2_1p4']} yr ; "
              f"M2>=2.0: {amap['P_for_M2_2p0']} yr ; M2>=2.428: {amap['P_for_M2_2p428']} yr ; "
              f"M2>=3.0 (BH): {amap['P_for_M2_3p0']} yr")
        print(f"  M2_range over log-P[3,100]yr grid (the caller's 'M2_median' channel): {amap['M2_range_3_100yr']}")

    print("\n================ RESOLVED / WIDE COMPANION ================")
    print(f"  WDS: {('MATCH n=%d' % wds['n_rows']) if wds.get('match') else 'no entry within 30\"'}")
    if wds.get('match'):
        for r in wds['rows']:
            print(f"     {r}")
    if isinstance(neigh, dict) and 'rows' in neigh:
        print(f"  Gaia DR3 cone ({neigh.get('radius_arcsec')}\"): {neigh['n_within']} sources")
        for r in neigh['rows']:
            tag = 'TARGET' if r.get('is_target') else ''
            cpm = ' <-- CPM candidate' if r.get('cpm_candidate') else ''
            print(f"     sep={str(r['sep_arcsec']):>7s}\" G={str(r['G']):>6s} plx={str(r['parallax']):>7s} "
                  f"pmra={str(r['pmra']):>9s} pmdec={str(r['pmdec']):>9s} "
                  f"dplx={str(r.get('dplx_mas','-')):>7s} dpm={str(r.get('dpm_masyr','-')):>8s} {tag}{cpm}")

    print("\n================ KERVELLA / HGCA / LIT ================")
    if kerv.get('match'):
        for k in ('sep_arcsec', 'HIP', 'Name', 'SpType', 'Vmag', 'snrPMaHG1', 'snrPMaH2G2',
                  'BinHG1', 'RUWE', 'PlxH2', 'PlxG3'):
            if k in kerv:
                print(f"    Kervella {k:14s} = {kerv.get(k)}")
    else:
        print("    Kervella J/A+A/657/A7: no match within 10\"")
    if hgca.get('match'):
        print(f"    HGCA {hgca.get('catalog')} match sep={hgca.get('sep_arcsec')}\"")
        for k in ('chisq', 'chi2', 'Chi2', 'pmra_gaia', 'pmdec_gaia', 'sig'):
            if k in hgca:
                print(f"    HGCA {k:14s} = {hgca.get(k)}")
    else:
        print("    HGCA J/ApJS/254/42: no match")
    print(f"    Literature crossmatch: " + ", ".join(f"{k.split('(')[0].strip()}={v.get('match')}" for k, v in lit.items()))

    print("\nJSON -> /tmp/hd91155_pma.json")
    return result

if __name__ == '__main__':
    run()
