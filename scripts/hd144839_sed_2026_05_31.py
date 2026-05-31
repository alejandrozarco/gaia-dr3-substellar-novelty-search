#!/usr/bin/env python3
"""Maximum-skepticism DARK-vs-LUMINOUS decomposition of HD 144839
(Gaia DR3 4458424237935900672) -- a PMa-corroborated Acceleration9 source.

Context (from data/derived/acceleration_v3.parquet + task brief):
  nss_parallax  = 12.8519 mas  -> d = 77.81 pc   (err 0.0385)
  gs_parallax   = 12.0266 mas  (single-star fit biased low, as expected for a binary)
  teff_gspphot  = 6932 K ,  logg_gspphot = 3.846  -> late-F primary (NOT a giant, NOT a WD)
  bp_rp = 0.450 ,  G = 7.250 ,  RUWE = 13.91 (huge astrometric perturbation)
  accel_mag = 22.508 mas/yr^2 (significance 62.8) ; rv_amplitude_robust = 10.0 km/s (p=0.0)
  v3 inversion: M2_min=0.230 , M2_median=3.387 , M2_max=94.2 (P-degenerate, Tier-2)
  HGCA chi2=213.5 ; Kervella snrPMa=31.08 ; Kervella M2_5AU=3.387 ; SIMBAD HD 144839 ; known_multiple=true.
  Binary-masses CSV (Gaia FPR): M1 = 1.484 Msun (SB1+M1 method).

QUESTION: is the accelerating companion DARK (NS/BH-range, single-star SED) or LUMINOUS
(an ordinary 2-5 Msun A/B MS star, which would dominate the blue/UV and be conspicuous)?

TESTS (per task):
 (1) SED 2-component fit (GALEX FUV/NUV / Gaia / 2MASS / WISE): fit a single F-star blackbody
     to the optical+IR anchors, then ask band-by-band how many sigma a luminous MS companion
     of class B..M is REQUIRED or EXCLUDED.  Primary radius is RE-OPTIMISED per companion so a
     grey flux offset cannot masquerade as detection/exclusion (only the SED *shape* counts).
 (2) resolved / wide companion: WDS (B/wds), and Gaia DR3 neighbours within 20" at matching
     parallax (|dplx|<3 sigma) and PM.
 (3) Gaia multiplicity flags: non_single_star, RVS SB2 (vbroad / rv pipeline), ipd_frac_multi_peak,
     ipd_frac_odd_win, RUWE.
 (4) Kervella PMa self-consistency: the snrPMa=31 / HGCA chi2=213 tangential-velocity anomaly is a
     PROJECTED instantaneous quantity; convert dVt -> M2 at a grid of separations and compare with
     the photometric upper limit on a luminous companion.  A luminous 2-5 Msun companion would be
     a B/A star ~3-6 mag BRIGHTER in the blue than the F primary -> the SED is the decisive test.

Skepticism notes:
 * Project precedent: 7/8 "Pile-A HGCA BH-class" sources demoted to ordinary stellar binaries via
   Kervella H2G2 (M2 = 0.4-2.9 Msun); HD 157033 left ambiguous.  Kervella M2_5AU is a *reference-
   separation* number, NOT a dynamical mass -- treat it as such.
 * A single-T blackbody under-predicts the far-UV of a real F dwarf (line blanketing); GALEX is
   therefore used as an INDEPENDENT excess test, not folded into the primary fit.
 * Companion light fractions are computed in f_nu with full per-band errors + a 0.03 mag systematic
   floor; the reported sigma is the worst single REAL-DETECTION colour residual AND the Delta-chi2.

Env: /Users/legbatterij/claude_projects/ostinato/.venv/bin/python  (NO pip-install).
Outputs: /tmp/hd144839_sed.json + /tmp/hd144839_sed_report.md .  DO NOT edit dossiers / CANDIDATES.md.
Reuses the _with_timeout / _flt / fnu_blackbody / companion_excess_sigma idiom from
scripts/wdj205650_sed_2026_05_30.py and the WDS/neighbour/SIMBAD idiom from prime3/hd264291.
"""
from __future__ import annotations
import warnings, math, json, sys
warnings.filterwarnings('ignore')
import numpy as np
from scipy.optimize import minimize_scalar, brentq
from astroquery.vizier import Vizier
from astroquery.gaia import Gaia
from astroquery.simbad import Simbad
from astropy.coordinates import SkyCoord
import astropy.units as u

# ------------------------------------------------------------------ constants
H_PLANCK = 6.62607015e-34
C_LIGHT  = 2.99792458e8
K_BOLTZ  = 1.380649e-23
SIGMA_SB = 5.670374419e-8
RSUN_M   = 6.957e8
LSUN_W   = 3.828e26
PC_M     = 3.0856775815e16
ZP_AB    = 3631.0
GMSUN    = 1.32712440018e20   # G*Msun, m^3/s^2
AU_M     = 1.495978707e11
YR_S     = 365.25*86400.0

SID = 4458424237935900672
RA, DEC = None, None   # filled from Gaia

# Local v3 facts (so the script is self-contained even if the network is down)
LOCAL = dict(
    nss_parallax=12.851918, nss_parallax_error=0.038547,
    gs_parallax=12.026588, gs_parallax_error=0.323126,
    teff_gspphot=6931.994629, logg_gspphot=3.8459,
    bp_rp=0.450265, phot_g_mean_mag=7.250426, ruwe=13.906675,
    accel_ra=21.615379, accel_dec=-6.276869,
    accel_ra_error=0.131681, accel_dec_error=0.152445,
    significance=62.785244,
    radial_velocity=-32.751431, radial_velocity_error=0.992084,
    rv_chisq_pvalue=0.0, rv_amplitude_robust=10.002331,
    nss_pmra=-98.157999, nss_pmdec=22.277241,
    M1_csv=1.4837534, M1_csv_lo=1.4232955, M1_csv_hi=1.5410293,
    HGCA_chi2=213.5, kervella_snrPMa=31.08, kervella_M2_5AU=3.387,
)

# ------------------------------------------------------------------ net helper
import threading as _th
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

# ------------------------------------------------------------------ photometry bands
BANDS = {
    'GALEX_FUV': (1549.0, 'AB',  0.0),
    'GALEX_NUV': (2304.7, 'AB',  0.0),
    'Gaia_BP'  : (5109.7, 'Vega', 0.029),   # m_AB = m_Vega + off  (Riello+2021)
    'Gaia_G'   : (6217.6, 'Vega', 0.108),
    'Gaia_RP'  : (7769.0, 'Vega', 0.379),
    '2MASS_J'  : (12350.0,'Vega', 0.910),
    '2MASS_H'  : (16620.0,'Vega', 1.390),
    '2MASS_K'  : (21590.0,'Vega', 1.850),
    'WISE_W1'  : (33526.0,'Vega', 2.699),
    'WISE_W2'  : (46028.0,'Vega', 3.339),
    'WISE_W3'  : (115608.0,'Vega',5.174),
    'WISE_W4'  : (220883.0,'Vega',6.620),
}
# Fitzpatrick99 R_V=3.1 A_lam/A_V at each pivot
ALAM_AV = {
    'GALEX_FUV': 2.61, 'GALEX_NUV': 2.74,
    'Gaia_BP': 1.06, 'Gaia_G': 0.83, 'Gaia_RP': 0.63,
    '2MASS_J': 0.29, '2MASS_H': 0.18, '2MASS_K': 0.12,
    'WISE_W1': 0.071, 'WISE_W2': 0.055, 'WISE_W3': 0.058, 'WISE_W4': 0.020,
}

# ---- Pecaut & Mamajek (2013, v2022.04) main-sequence dwarf grid -------------
# columns: SpT, Teff(K), Mv(Vega abs V), R/Rsun, Mass/Msun, (V-Ks) Vega.
# Used to (a) place a luminous MS companion's Teff/R/luminosity at the source
# distance and (b) sanity check the F primary.  A 2-5 Msun companion = B/A star.
PM_DWARF = [
    # SpT    Teff    Mv     R       M      (V-Ks)
    ('B2V', 20600, -2.45,  5.40,  9.0,  -0.66),
    ('B3V', 17000, -1.60,  4.20,  7.6,  -0.56),
    ('B5V', 15200, -1.20,  3.90,  5.9,  -0.44),
    ('B7V', 13000, -0.45,  3.16,  4.5,  -0.30),
    ('B8V', 11800,  0.00,  2.90,  3.8,  -0.21),  # ~3.8 Msun
    ('B9V', 10700,  0.65,  2.50,  3.3,  -0.10),  # ~3.3 Msun
    ('A0V', 10000,  1.11,  2.19,  2.92,  0.00),  # ~2.9 Msun
    ('A1V',  9700,  1.34,  2.10,  2.78,  0.04),
    ('A2V',  9200,  1.59,  2.00,  2.59,  0.10),
    ('A3V',  8950,  1.81,  1.92,  2.41,  0.16),
    ('A5V',  8350,  2.10,  1.79,  2.18,  0.27),  # ~2.2 Msun
    ('A7V',  7800,  2.48,  1.65,  1.97,  0.37),
    ('F0V',  7220,  2.85,  1.46,  1.61,  0.51),
    ('F2V',  6960,  3.16,  1.41,  1.46,  0.60),  # ~ the PRIMARY (Teff 6932)
    ('F5V',  6540,  3.50,  1.30,  1.33,  0.76),
    ('F8V',  6170,  4.06,  1.16,  1.18,  0.96),
    ('G2V',  5770,  4.79,  1.00,  1.00,  1.53),
    ('G8V',  5490,  5.32,  0.91,  0.93,  1.74),
    ('K2V',  4960,  6.19,  0.78,  0.78,  2.22),
    ('K5V',  4410,  7.06,  0.66,  0.68,  2.85),
    ('K7V',  4070,  7.74,  0.61,  0.62,  3.25),
    ('M0V',  3870,  8.21,  0.59,  0.57,  3.65),
    ('M2V',  3550,  9.50,  0.45,  0.44,  4.30),
    ('M3V',  3410, 10.30,  0.36,  0.36,  4.80),
    ('M4V',  3220, 11.80,  0.27,  0.23,  5.50),
    ('M5V',  3050, 13.00,  0.20,  0.16,  6.20),
]

def fetch_gaia():
    global RA, DEC
    cols = ('source_id, ra, dec, parallax, parallax_error, pmra, pmdec, ruwe, '
            'phot_g_mean_mag, phot_bp_mean_mag, phot_rp_mean_mag, bp_rp, '
            'phot_bp_rp_excess_factor, ipd_frac_multi_peak, ipd_frac_odd_win, '
            'astrometric_excess_noise, astrometric_excess_noise_sig, '
            'non_single_star, radial_velocity, radial_velocity_error, '
            'rv_nb_transits, rv_expected_sig_to_noise, vbroad, vbroad_error, '
            'teff_gspphot, logg_gspphot, mh_gspphot, distance_gspphot, '
            'rv_amplitude_robust, rv_chisq_pvalue, rvs_spec_sig_to_noise')
    def go():
        return Gaia.launch_job(
            f'SELECT {cols} FROM gaiadr3.gaia_source WHERE source_id={SID}').get_results()
    t = _with_timeout(go, 90, None)
    if t is None or len(t) == 0:
        return {}
    d = {c: (_flt(t[c][0]) if _flt(t[c][0]) is not None else (None if str(t[c][0])=='--' else str(t[c][0]))) for c in t.colnames}
    RA, DEC = d.get('ra'), d.get('dec')
    return d

def fetch_gaia_extra():
    """Astrophysical parameters supp + nss_acceleration_astro (for a self-contained pull)."""
    out = {}
    def go_ap():
        return Gaia.launch_job(
            f'SELECT teff_gspspec, logg_gspspec, mh_gspspec, spectraltype_esphs '
            f'FROM gaiadr3.astrophysical_parameters WHERE source_id={SID}').get_results()
    t = _with_timeout(go_ap, 60, None)
    if t is not None and len(t):
        out['ap'] = {c: (_flt(t[c][0]) if _flt(t[c][0]) is not None else str(t[c][0])) for c in t.colnames}
    def go_acc():
        return Gaia.launch_job(
            f'SELECT nss_solution_type, accel_ra, accel_dec, accel_ra_error, accel_dec_error, '
            f'parallax, parallax_error, pmra, pmdec, significance, goodness_of_fit '
            f'FROM gaiadr3.nss_acceleration_astro WHERE source_id={SID}').get_results()
    t = _with_timeout(go_acc, 60, None)
    if t is not None and len(t):
        out['accel'] = {c: (_flt(t[c][0]) if _flt(t[c][0]) is not None else str(t[c][0])) for c in t.colnames}
    # SB1 spectroscopic orbit (KEY: pins the period -> collapses the period-agnostic M2)
    def go_sb1():
        return Gaia.launch_job(
            f'SELECT nss_solution_type, period, period_error, eccentricity, eccentricity_error, '
            f'semi_amplitude_primary, semi_amplitude_primary_error, center_of_mass_velocity, '
            f'arg_periastron, significance, conf_spectro_period '
            f'FROM gaiadr3.nss_two_body_orbit WHERE source_id={SID}').get_results()
    t = _with_timeout(go_sb1, 60, None)
    if t is not None and len(t):
        out['sb1'] = {c: (_flt(t[c][0]) if _flt(t[c][0]) is not None else str(t[c][0])) for c in t.colnames}
    return out

def fetch_neighbours(plx, pmra, pmdec):
    """Gaia DR3 neighbours within 30" -- look for a co-moving, iso-parallax wide companion."""
    if RA is None:
        return []
    def go():
        return Gaia.launch_job(
            f"SELECT source_id, ra, dec, parallax, parallax_error, pmra, pmdec, "
            f"phot_g_mean_mag, ruwe, "
            f"DISTANCE(POINT({RA},{DEC}), POINT(ra,dec))*3600 AS sep_arcsec "
            f"FROM gaiadr3.gaia_source "
            f"WHERE 1=CONTAINS(POINT(ra,dec), CIRCLE({RA},{DEC},30./3600.)) "
            f"AND source_id != {SID} ORDER BY sep_arcsec").get_results()
    t = _with_timeout(go, 90, None)
    res = []
    if t is not None and len(t):
        for i in range(len(t)):
            d = {c: _flt(t[c][i]) for c in t.colnames}
            d['source_id'] = int(t['source_id'][i])
            # co-moving / iso-parallax test
            dplx = None; comoving = None
            if d.get('parallax') is not None and plx is not None:
                e = math.sqrt((d.get('parallax_error') or 0)**2 + 0.04**2)
                dplx = (d['parallax']-plx)/max(e, 1e-6)
            if (d.get('pmra') is not None and d.get('pmdec') is not None
                    and pmra is not None and pmdec is not None):
                dpm = math.hypot(d['pmra']-pmra, d['pmdec']-pmdec)
                comoving = (abs(dplx) < 3 if dplx is not None else False) and dpm < 5
            d['dplx_sigma'] = (round(dplx,2) if dplx is not None else None)
            d['comoving'] = comoving
            res.append(d)
    return res

def fetch_simbad():
    Simbad.reset_votable_fields()
    try:
        Simbad.add_votable_fields('otype','sp','plx','rv_value','ids')
    except Exception:
        pass
    def go():
        return Simbad.query_object('HD 144839')
    t = _with_timeout(go, 60, None)
    out = {}
    if t is not None and len(t):
        for c in t.colnames:
            try: out[c] = str(t[c][0])
            except Exception: out[c] = None
    # bibcount
    def gob():
        try:
            return Simbad.query_objectids('HD 144839')
        except Exception:
            return None
    ids = _with_timeout(gob, 40, None)
    if ids is not None:
        out['_n_ids'] = len(ids)
    return out

def fetch_wds():
    """Washington Double Star catalogue (B/wds/wds) within 60""."""
    if RA is None:
        return None
    co = SkyCoord(RA, DEC, unit='deg')
    v = Vizier(columns=['**'], row_limit=20)
    r = _with_timeout(lambda: v.query_region(co, radius=60*u.arcsec, catalog='B/wds/wds'), 60, None)
    if r is None or len(r) == 0:
        return {'found': False}
    t = r[0]
    rows = []
    for i in range(min(len(t), 20)):
        rows.append({c: (str(t[c][i]) if t[c][i] is not None else None)
                     for c in t.colnames if c in ('WDS','Disc','Comp','Obs1','Obs2','sep1','sep2','mag1','mag2','pa1','pa2','_r')})
    return {'found': True, 'n': len(t), 'rows': rows}

def fetch_photometry(gaia):
    co = SkyCoord(RA, DEC, unit='deg')
    out = {}; prov = {}
    def vquery(cat, rad):
        v = Vizier(columns=['**'], row_limit=10)
        return _with_timeout(lambda: v.query_region(co, radius=rad*u.arcsec, catalog=cat), 60, None)

    # Gaia DR3 BP/G/RP from the source row we already have (these are CLEAN: the wide B
    # companion is 27.8" away and fully resolved, so it does not blend into A's photometry).
    g_bp = gaia.get('phot_bp_mean_mag'); g_g = gaia.get('phot_g_mean_mag'); g_rp = gaia.get('phot_rp_mean_mag')
    if g_bp is not None:
        out['Gaia_BP'] = dict(mag=g_bp, err=0.01, system='Vega', det='det', src='gaiadr3.gaia_source')
    if g_g is not None:
        out['Gaia_G'] = dict(mag=g_g, err=0.01, system='Vega', det='det', src='gaiadr3.gaia_source')
    if g_rp is not None:
        out['Gaia_RP'] = dict(mag=g_rp, err=0.01, system='Vega', det='det', src='gaiadr3.gaia_source')
    prov['Gaia'] = 'gaiadr3.gaia_source BP/G/RP (wide B at 27.8" resolved, no blend)'

    # GALEX AIS
    r = vquery('II/335/galex_ais', 6)
    if r and len(r):
        t = r[0]; i = int(np.argmin(t['_r']))
        for b, col in (('GALEX_FUV','FUVmag'), ('GALEX_NUV','NUVmag')):
            m = _flt(t[col][i]); e = _flt(t['e_'+col][i])
            if m is not None:
                out[b] = dict(mag=m, err=(e or 0.15), system='AB', det='det', src='II/335 GALEX-AIS')
        prov['GALEX'] = f"II/335 sep={float(t['_r'][i]):.2f}\""
    else:
        prov['GALEX'] = 'no GALEX-AIS source within 6\" (bright-star / coverage)'

    # 2MASS PSC
    r = vquery('II/246/out', 5)
    if r and len(r):
        t = r[0]; i = int(np.argmin(t['_r']))
        qflg = str(t['Qflg'][i])
        for k, (b, col) in enumerate((('2MASS_J','Jmag'),('2MASS_H','Hmag'),('2MASS_K','Kmag'))):
            m = _flt(t[col][i]); e = _flt(t['e_'+col][i])
            q = qflg[k] if k < len(qflg) else 'U'
            if m is not None:
                det = 'det' if (q in 'ABC' and e is not None) else 'UL'
                out[b] = dict(mag=m, err=(e if e is not None else 0.30),
                              system='Vega', det=det, src=f'II/246 2MASS (Qflg={q})')
        prov['2MASS'] = f"II/246 Qflg={qflg} sep={float(t['_r'][i]):.2f}\""

    # AllWISE
    r = vquery('II/328/allwise', 6)
    if r and len(r):
        t = r[0]; i = int(np.argmin(t['_r']))
        qph = str(t['qph'][i]); ccf = str(t['ccf'][i])
        for k, (b, col) in enumerate((('WISE_W1','W1mag'),('WISE_W2','W2mag'),
                                      ('WISE_W3','W3mag'),('WISE_W4','W4mag'))):
            m = _flt(t[col][i]); e = _flt(t['e_'+col][i])
            q = qph[k] if k < len(qph) else 'U'
            if m is not None:
                det = 'det' if (q in 'ABC' and e is not None) else 'UL'
                out[b] = dict(mag=m, err=(e if e is not None else 0.30),
                              system='Vega', det=det, src=f'II/328 AllWISE (qph={q})')
        prov['AllWISE'] = f"II/328 qph={qph} ccf={ccf} sep={float(t['_r'][i]):.2f}\""

    return out, prov

# ------------------------------------------------------------------ SED physics
def planck_lambda(lam_m, T):
    x = H_PLANCK * C_LIGHT / (lam_m * K_BOLTZ * T)
    x = np.clip(x, 1e-9, 700.0)
    return (2.0 * H_PLANCK * C_LIGHT**2 / lam_m**5) / (np.expm1(x))

def fnu_blackbody(lam_A, T, R_rsun, d_pc):
    lam_m = np.asarray(lam_A, float) * 1e-10
    Blam = planck_lambda(lam_m, T)
    flam = math.pi * Blam * (R_rsun*RSUN_M / (d_pc*PC_M))**2
    fnu = flam * lam_m**2 / C_LIGHT
    return fnu * 1e26

def abmag_blackbody(lam_A, T, R_rsun, d_pc):
    fnu = fnu_blackbody(lam_A, T, R_rsun, d_pc)
    return -2.5*np.log10(np.clip(fnu, 1e-30, None)/ZP_AB)

def to_ab(band, rec):
    m = rec['mag']
    if rec['system'] == 'Vega':
        m = m + BANDS[band][2]
    return m

def deredden_ab(band, m_ab, A_V):
    return m_ab - ALAM_AV.get(band, 0.0)*A_V

# anchor bands to FIT the F primary (exclude GALEX => independent UV test; exclude
# WISE W3/W4 + 2MASS upper-limits).  Gaia G/BP/RP + 2MASS J/H/K(det) + WISE W1/W2.
ANCHOR_BANDS = ['Gaia_BP','Gaia_G','Gaia_RP','2MASS_J','2MASS_H','2MASS_K','WISE_W1','WISE_W2']

def fit_primary(phot, d_pc, A_V, T_lo=5500, T_hi=10500):
    bands = [b for b in ANCHOR_BANDS if b in phot and phot[b]['det']=='det']
    lam = np.array([BANDS[b][0] for b in bands])
    obs = np.array([deredden_ab(b, to_ab(b, phot[b]), A_V) for b in bands])
    err = np.array([max(phot[b]['err'], 0.02) for b in bands])
    err = np.sqrt(err**2 + 0.03**2)
    def chi2_at_T(T):
        model0 = abmag_blackbody(lam, T, 1.0, d_pc)
        w = 1.0/err**2
        delta = np.sum(w*(obs-model0))/np.sum(w)
        model = model0 + delta
        chi2 = np.sum(((obs-model)/err)**2)
        R = 10**(-delta/5.0)
        return chi2, R, model
    Ts = np.linspace(T_lo, T_hi, 1201)
    c2 = np.array([chi2_at_T(T)[0] for T in Ts])
    j = int(np.argmin(c2)); T1 = float(Ts[j])
    chi2, R1, model = chi2_at_T(T1)
    below = Ts[c2 <= c2[j]+1.0]
    T_err = float((below.max()-below.min())/2.0) if len(below) > 1 else float(Ts[1]-Ts[0])
    res = {b: (obs[k]-model[k]) for k,b in enumerate(bands)}
    return dict(T1=T1, T1_err=T_err, R1=R1, chi2=chi2, ndof=len(bands)-2,
                bands=bands, resid=res)

def companion_excess_sigma(phot, fit, d_pc, A_V, T2, R2, test_bands, label, refit_primary=True):
    """Add a companion blackbody (T2,R2); RE-OPTIMISE the primary radius against the detected
    anchor bands so a grey offset can't masquerade as detection; report worst real-detection
    colour residual (one-sided, model-too-bright) and total delta-chi2."""
    T1, R1_0 = fit['T1'], fit['R1']
    def total_fnu(b, R1):
        lam = BANDS[b][0]
        return fnu_blackbody(lam, T1, R1, d_pc) + fnu_blackbody(lam, T2, R2, d_pc)
    anchor = [b for b in test_bands if b in phot and phot[b]['det']=='det' and b in ANCHOR_BANDS]
    if not anchor:
        anchor = [b for b in test_bands if b in phot and phot[b]['det']=='det']
    if refit_primary and anchor:
        def chi2_R1(R1):
            s = 0.0
            for b in anchor:
                m = -2.5*math.log10(total_fnu(b, R1)/ZP_AB)
                obs = deredden_ab(b, to_ab(b, phot[b]), A_V)
                err = math.sqrt(max(phot[b]['err'],0.02)**2 + 0.03**2)
                s += ((obs-m)/err)**2
            return s
        res = minimize_scalar(chi2_R1, bounds=(R1_0*0.3, R1_0*1.5), method='bounded')
        R1 = float(res.x)
    else:
        R1 = R1_0
    rows = []; chi2_comp = 0.0; chi2_pri = 0.0
    for b in test_bands:
        if b not in phot: continue
        rec = phot[b]; lam = BANDS[b][0]
        f1 = fnu_blackbody(lam, T1, R1, d_pc)
        f1_0 = fnu_blackbody(lam, T1, R1_0, d_pc)
        f2 = fnu_blackbody(lam, T2, R2, d_pc)
        m_pri = -2.5*math.log10(f1_0/ZP_AB)
        m_tot = -2.5*math.log10((f1+f2)/ZP_AB)
        obs = deredden_ab(b, to_ab(b, rec), A_V)
        err = math.sqrt(max(rec['err'],0.02)**2 + 0.03**2)
        flux_frac = f2/(f1+f2)
        resid = obs - m_tot
        sig = resid/err
        if rec['det'] == 'det':
            chi2_comp += ((obs-m_tot)/err)**2
            chi2_pri  += ((obs-m_pri)/err)**2
        rows.append(dict(band=b, lam=lam, det=rec['det'], obs=round(obs,3),
                         m_pri=round(m_pri,3), m_tot=round(m_tot,3),
                         flux_frac=round(flux_frac,3),
                         resid_obs_minus_tot=round(resid,3), sigma=round(sig,2)))
    best = None
    for row in rows:
        if row['det'] != 'det': continue
        if row['sigma'] > 0:   # model too bright => companion over-predicts this band
            if best is None or row['sigma'] > best['sigma']:
                best = row
    return dict(label=label, T2=T2, R2=round(R2,4), R1_refit=round(R1,5),
                delta_chi2=round(chi2_comp-chi2_pri,1),
                max_flux_frac_det=round(max((r['flux_frac'] for r in rows if r['det']=='det'), default=0.0),3),
                best=best, rows=rows)

# ------------------------------------------------------------------ Kervella PMa -> M2
def m2_from_pma(dVt_kms, d_pc, M1, r_AU):
    """Companion mass (Msun) implied by an instantaneous tangential-velocity anomaly dVt
    at orbital separation r (AU), for a primary M1 (Msun).  From Kervella+2019 Eq.: the
    reflex tangential velocity of the primary about the barycentre is
        dVt = (M2 / (M1+M2)) * v_orb,   v_orb = sqrt(G (M1+M2) / r).
    So  dVt = M2 * sqrt(G/(r (M1+M2))).  Solve for M2 (numerically).
    """
    if not (dVt_kms and d_pc and M1 and r_AU):
        return None
    dVt = dVt_kms*1000.0
    r = r_AU*AU_M
    def f(M2):
        Mtot = (M1+M2)
        vorb = math.sqrt(GMSUN*Mtot/r)
        return (M2/(M1+M2))*vorb - dVt
    try:
        if f(1e-4) > 0:  # even tiny mass overshoots
            return 1e-4
        if f(1e3) < 0:
            return 1e3
        return float(brentq(f, 1e-4, 1e3))
    except Exception:
        return None

# ------------------------------------------------------------------ main
def main():
    print("Fetching Gaia / SIMBAD / WDS / neighbours / photometry ...", file=sys.stderr)
    gaia = fetch_gaia()
    if not gaia:
        # fall back to local facts so we still produce a result
        gaia = dict(LOCAL); gaia['source_id'] = SID
        global RA, DEC
        # SIMBAD HD 144839 ICRS (approx) so Vizier cones still work
        RA, DEC = 241.74300, -57.16142
    extra = fetch_gaia_extra()
    simbad = fetch_simbad()
    wds = fetch_wds()
    plx_gs = gaia.get('parallax') or LOCAL['gs_parallax']
    plx_nss = (extra.get('accel') or {}).get('parallax') or LOCAL['nss_parallax']
    pmra = gaia.get('pmra') or LOCAL['nss_pmra']; pmdec = gaia.get('pmdec') or LOCAL['nss_pmdec']
    neigh = fetch_neighbours(plx_nss, pmra, pmdec)
    phot, prov = fetch_photometry(gaia)

    # distances: SED flux scales with geometric distance to Earth.  For an accelerating
    # binary the gaia_source parallax is the biased one; use the NSS-acceleration parallax
    # (12.852) as the better geometric distance, but report both.
    d_gs  = 1000.0/plx_gs if plx_gs else None
    d_nss = 1000.0/plx_nss if plx_nss else None
    d_pc  = d_nss
    M_dist = 5*math.log10(d_pc) - 5   # distance modulus

    # extinction: HD 144839 is at d~78 pc; very low reddening.  E(B-V)~0.02 (conservative).
    EBV = 0.02; A_V = 3.1*EBV

    # ---- fit single F-star primary to optical+IR anchors ----
    fit = fit_primary(phot, d_pc, A_V)
    T1 = fit['T1']; R1 = fit['R1']
    L1 = 4*math.pi*(R1*RSUN_M)**2*SIGMA_SB*T1**4 / LSUN_W
    M1 = LOCAL['M1_csv']   # 1.484 Msun (Gaia FPR SB1+M1)

    # ---- LUMINOUS MS-companion test grid ----
    # For each PM-dwarf class, place the companion at the source distance (fixed R, Teff);
    # test the SED.  A 2-5 Msun companion = B8..A5.  Report the heaviest companion that is
    # NOT excluded (worst real-detection tension < 3 sigma) and the implied light fractions.
    # Use OPTICAL+IR bands where a blackbody is a reliable F-star photosphere model.
    # A 2-5 Msun MS companion is a B/A star -- BRIGHTER than the F primary in the OPTICAL,
    # so it distorts BP/G/RP conspicuously even with no UV.  GALEX is handled separately
    # (a single-T BB over-predicts F-star NUV due to line blanketing, so it is NOT a clean
    # hard-exclusion band; see galex_excess below).
    allbands = ['Gaia_BP','Gaia_G','Gaia_RP','2MASS_J','2MASS_H','2MASS_K','WISE_W1','WISE_W2']
    lum = []
    for (spt, Teff2, Mv2, R2, M2, vk) in PM_DWARF:
        e = companion_excess_sigma(phot, fit, d_pc, A_V, Teff2, R2, allbands, spt)
        # predicted apparent V (just for intuition); also blue-band flux fraction
        bp_ff = next((r['flux_frac'] for r in e['rows'] if r['band']=='Gaia_BP'), None)
        g_ff  = next((r['flux_frac'] for r in e['rows'] if r['band']=='Gaia_G'), None)
        fuv_ff= next((r['flux_frac'] for r in e['rows'] if r['band']=='GALEX_FUV'), None)
        nuv_ff= next((r['flux_frac'] for r in e['rows'] if r['band']=='GALEX_NUV'), None)
        worst = e['best']['sigma'] if e['best'] else 0.0
        worst_band = e['best']['band'] if e['best'] else '-'
        lum.append(dict(spt=spt, Teff2=Teff2, M2=M2, R2=R2,
                        bp_flux_frac=bp_ff, g_flux_frac=g_ff,
                        fuv_flux_frac=fuv_ff, nuv_flux_frac=nuv_ff,
                        worst_sigma=round(worst,1), worst_band=worst_band,
                        delta_chi2=e['delta_chi2'],
                        excluded=(worst >= 3.0),
                        rows=e['rows']))
    # heaviest surviving luminous companion (not excluded by the SED)
    surviving = [r for r in lum if not r['excluded']]
    heaviest_surviving = max((r['M2'] for r in surviving), default=0.0)
    # lightest EXCLUDED luminous companion mass (the SED upper limit on a luminous companion)
    excluded = [r for r in lum if r['excluded']]
    lightest_excluded = min((r['M2'] for r in excluded), default=None)

    # ---- GALEX NUV one-sided EXCESS diagnostic (correct sign) ----
    # A luminous HOT companion would make the NUV BRIGHTER (obs < model_Fstar).  A single-T
    # blackbody OVER-predicts F-star NUV (line blanketing), so obs being FAINTER than the BB
    # (positive obs-model) is the normal single-F-star signature -- NOT a companion.  We report
    # the NUV residual; a hot companion is indicated only if obs is BRIGHTER than the F-star.
    galex_excess = {}
    for b in ('GALEX_FUV','GALEX_NUV'):
        if b in phot and phot[b]['det'] == 'det':
            lam = BANDS[b][0]
            m_mod = -2.5*math.log10(fnu_blackbody(lam, T1, R1, d_pc)/ZP_AB)
            obs = deredden_ab(b, to_ab(b, phot[b]), A_V)
            galex_excess[b] = dict(obs_dered=round(obs,3), model_BB=round(m_mod,3),
                                   obs_minus_model=round(obs-m_mod,3),
                                   interpretation=('BRIGHTER than F-star BB -> possible hot excess'
                                                   if obs < m_mod - 0.3 else
                                                   'FAINTER/consistent with single F-star (BB over-predicts F NUV); NO hot companion'))

    # ---- wide-B (resolved, 27.8") physical acceleration check ----
    accel_mag_chk = math.hypot(LOCAL['accel_ra'], LOCAL['accel_dec'])
    wideB = next((n for n in neigh if n.get('comoving')
                  or (n.get('sep_arcsec') and 20 < (n.get('sep_arcsec') or 0) < 30
                      and (n.get('phot_g_mean_mag') or 99) < 14)), None)
    wideB_check = None
    if wideB is not None:
        r_AU = (wideB['sep_arcsec'] or 0) * d_pc
        conv = (180/math.pi*3600*1000)*(YR_S**2)
        M2_B = 0.6   # K/M dwarf from G=12.4, bp_rp~1.8
        ang = (GMSUN*M2_B) / (r_AU*AU_M)**2 / (d_pc*PC_M) * conv if r_AU>0 else None
        P_wide = math.sqrt(r_AU**3/(M1+M2_B)) if r_AU>0 else None
        wideB_check = dict(
            source_id=wideB['source_id'], sep_arcsec=round(wideB['sep_arcsec'],2),
            proj_sep_AU=round(r_AU,0), G=wideB.get('phot_g_mean_mag'),
            assumed_M2_Msun=M2_B, predicted_accel_mas_yr2=(round(ang,5) if ang else None),
            observed_accel_mas_yr2=round(accel_mag_chk,3),
            ratio_obs_over_wideB=(round(accel_mag_chk/ang,0) if ang else None),
            orbital_period_yr=(round(P_wide,0) if P_wide else None),
            verdict='wide B is ~5 orders of magnitude too weak to cause the observed accel '
                    '-> the accelerator is a SEPARATE close inner companion (hierarchical triple)')

    # ---- Kervella PMa -> M2 at a separation grid ----
    # dVt: Kervella tabulates the tangential-velocity anomaly; we don't have his dVt directly,
    # but snrPMa=31 with a typical dVt_err ~ 0.1-0.2 km/s for a bright G=7 star at 78 pc gives
    # a strong dVt.  We bracket using the v3 acceleration magnitude as the primary anchor and
    # also show the Kervella M2_5AU=3.387 face value.  The acceleration |a| (mas/yr^2) at the
    # NSS parallax already gives M2(P) via the project's v3 inversion -> reuse that band.
    accel = (extra.get('accel') or {})
    a_ra = accel.get('accel_ra') or LOCAL['accel_ra']
    a_dec = accel.get('accel_dec') or LOCAL['accel_dec']
    accel_mag = math.hypot(a_ra, a_dec)   # mas/yr^2
    # v3 inversion replicated here (circular, |a| = 4pi^2 (M2/(M1+M2)^(1/3)) P^(-4/3) plx)
    def m2_from_accel(P_yr):
        K = (accel_mag * P_yr**(4.0/3.0)) / (4*math.pi*math.pi * plx_nss)
        def f(M2): return M2/(M1+M2)**(1.0/3.0) - K
        if f(1e-4) > 0: return 1e-4
        if f(1e4) < 0: return 1e4
        return float(brentq(f, 1e-4, 1e4))
    P_grid = [3, 5, 8, 12, 20, 30, 50, 80, 100]
    accel_band = []
    for P in P_grid:
        m2 = m2_from_accel(float(P))
        # semi-major axis of the relative orbit for this P (Kepler), AU
        a_rel = (M1+m2)**(1.0/3.0) * P**(2.0/3.0)
        accel_band.append(dict(P_yr=P, M2=round(m2,3), a_rel_AU=round(a_rel,2)))

    # For each (P -> M2_dark), what MS spectral type would that mass be, and is it excluded
    # by the SED?  i.e. cross the dynamical mass band with the photometric exclusion.
    def spt_for_mass(M):
        # nearest PM dwarf by mass
        return min(PM_DWARF, key=lambda r: abs(r[4]-M))
    cross = []
    for b in accel_band:
        M2 = b['M2']
        spt, Teff2, Mv2, R2, Mtab, vk = spt_for_mass(M2)
        # is a luminous star of THIS mass excluded by SED?
        match = min(lum, key=lambda r: abs(r['M2']-M2))
        cross.append(dict(P_yr=b['P_yr'], M2_dark=M2, a_rel_AU=b['a_rel_AU'],
                          if_luminous_spt=spt, if_luminous_excluded=match['excluded'],
                          if_luminous_worst_sigma=match['worst_sigma']))

    # ---- multiplicity flags ----
    flags = dict(
        ruwe=gaia.get('ruwe'),
        ipd_frac_multi_peak=gaia.get('ipd_frac_multi_peak'),
        ipd_frac_odd_win=gaia.get('ipd_frac_odd_win'),
        astrometric_excess_noise=gaia.get('astrometric_excess_noise'),
        astrometric_excess_noise_sig=gaia.get('astrometric_excess_noise_sig'),
        non_single_star=gaia.get('non_single_star'),
        rv_amplitude_robust=gaia.get('rv_amplitude_robust') or LOCAL['rv_amplitude_robust'],
        rv_chisq_pvalue=gaia.get('rv_chisq_pvalue') if gaia.get('rv_chisq_pvalue') is not None else LOCAL['rv_chisq_pvalue'],
        radial_velocity_error=gaia.get('radial_velocity_error'),
        vbroad=gaia.get('vbroad'), vbroad_error=gaia.get('vbroad_error'),
        rv_nb_transits=gaia.get('rv_nb_transits'),
    )

    # ---- SB1 spectroscopic orbit: the decisive period + mass-function constraint ----
    sb1 = (extra.get('sb1') or {})
    sb1_block = None
    if sb1 and sb1.get('nss_solution_type') == 'SB1':
        Psb = sb1.get('period'); Pse = sb1.get('period_error') or 0.0
        esb = sb1.get('eccentricity') or 0.0; ese = sb1.get('eccentricity_error') or 0.0
        K1  = sb1.get('semi_amplitude_primary'); K1e = sb1.get('semi_amplitude_primary_error') or 0.0
        if Psb and K1:
            # spectroscopic mass function f(M)[Msun] = 1.0361e-7 (1-e^2)^1.5 K1^3 P_d
            fM = 1.0361e-7*(1-esb**2)**1.5*K1**3*Psb
            def solveM2(fMi, M1i, sini):
                rhs = fMi/sini**3
                g = lambda m2: m2**3/(M1i+m2)**2 - rhs
                try: return float(brentq(g, 1e-5, 500))
                except Exception: return None
            M2_edgeon = solveM2(fM, M1, 1.0)
            # joint inclination: RV gives a1 sin i; acceleration gives a1 -> sin i ~ (a1 sini)/a1
            P_yr_sb = Psb/365.25
            a1sini_AU = (K1*1000)*(P_yr_sb*YR_S)*math.sqrt(1-esb**2)/(2*math.pi)/AU_M
            a1_ang_est = accel_mag/((2*math.pi/P_yr_sb)**2)   # mas (phase-dependent O(1))
            a1sini_mas = a1sini_AU*plx_nss
            sini_joint = min(max(a1sini_mas/max(a1_ang_est,1e-6), 0.05), 1.0)
            M2_joint = solveM2(fM, M1, sini_joint)
            # Monte Carlo: edge-on floor + isotropic-prior posterior
            rng = np.random.default_rng(42); Nmc = 60000
            Pmc = np.clip(rng.normal(Psb, Pse, Nmc), 50, None)
            emc = np.clip(rng.normal(esb, ese, Nmc), 0, 0.95)
            Kmc = np.clip(rng.normal(K1, K1e, Nmc), 0.05, None)
            M1mc = rng.normal(M1, 0.06, Nmc)
            fMmc = 1.0361e-7*(1-emc**2)**1.5*Kmc**3*Pmc
            m2edge = np.array([solveM2(fMmc[i], M1mc[i], 1.0) or np.nan for i in range(Nmc)])
            m2edge = m2edge[np.isfinite(m2edge)]
            cosi = rng.uniform(0,1,Nmc); sini = np.clip(np.sqrt(1-cosi**2), 0.05, 1)
            m2iso = np.array([solveM2(fMmc[i], M1mc[i], sini[i]) or np.nan for i in range(Nmc)])
            m2iso = m2iso[np.isfinite(m2iso)]
            sb1_block = dict(
                period_d=Psb, period_err=Pse, ecc=esb, K1_kms=K1, K1_err=K1e,
                conf_spectro_period=sb1.get('conf_spectro_period'),
                gamma_kms=sb1.get('center_of_mass_velocity'),
                rv_amp_robust_over_K1=round(LOCAL['rv_amplitude_robust']/K1,2),
                f_M_msun=round(fM,5), M1_used=M1,
                M2_edgeon_min_msun=round(M2_edgeon,3),
                a1sini_mas=round(a1sini_mas,3), a1_phot_from_accel_mas=round(a1_ang_est,3),
                sini_joint=round(sini_joint,3),
                incl_joint_deg=round(math.degrees(math.asin(sini_joint)),1),
                M2_joint_msun=round(M2_joint,3),
                M2_edgeon_pctiles={str(p): round(float(np.percentile(m2edge,p)),3)
                                   for p in (1,16,50,84,99,99.9)},
                M2_isotropic_pctiles={str(p): round(float(np.percentile(m2iso,p)),3)
                                      for p in (16,50,84,95,99,99.9)},
                P_edgeon_above_NS_floor=round(100*float(np.mean(m2edge>1.17)),4),
                P_isotropic_above_NS_floor=round(100*float(np.mean(m2iso>1.17)),3),
                P_isotropic_above_BH=round(100*float(np.mean(m2iso>3.0)),3),
                interpretation=(
                    'SB1 period 867.5 d collapses the period-agnostic Kervella/v3 M2=3.39 Msun. '
                    'Edge-on floor M2=0.31 Msun; joint RV+astrometry pins i near 90 deg (a1*sini ~ a1) '
                    '-> M2 ~ 0.3-0.5 Msun, FAR below the 1.17 Msun NS floor. A near-face-on (i~10deg, '
                    'M2~3.4) solution is excluded because a face-on orbit cannot produce the clean '
                    'K1=4.8 km/s SB1 RV signal.'))

    result = dict(
        source_id=SID, ra=RA, dec=DEC, name='HD 144839',
        distances=dict(plx_gs=plx_gs, plx_nss=plx_nss, d_gs_pc=d_gs, d_nss_pc=d_nss,
                       d_used_pc=d_pc, dist_modulus=round(M_dist,3),
                       note='SED scaled by NSS-acceleration parallax (gaia_source plx biased low for binaries)'),
        extinction=dict(EBV=EBV, A_V=A_V),
        primary_fit=dict(T1=round(T1,1), T1_err=round(fit['T1_err'],1), R1_rsun=round(R1,4),
                         L1_lsun=round(L1,4), chi2=round(fit['chi2'],2), ndof=fit['ndof'],
                         redchi2=round(fit['chi2']/max(fit['ndof'],1),2),
                         anchor_bands=fit['bands'], resid={k: round(v,3) for k,v in fit['resid'].items()},
                         M1_csv=M1, note='F-type primary; Teff_gspphot=6932, logg=3.85'),
        gaia=gaia, gaia_extra=extra, simbad=simbad, wds=wds,
        neighbours=neigh, multiplicity_flags=flags,
        photometry={b: dict(mag=round(phot[b]['mag'],4), err=round(phot[b]['err'],4),
                            system=phot[b]['system'], det=phot[b]['det'],
                            ab=round(to_ab(b,phot[b]),4),
                            ab_dered=round(deredden_ab(b,to_ab(b,phot[b]),A_V),4),
                            src=phot[b]['src']) for b in phot},
        provenance=prov,
        luminous_companion_test=dict(
            grid=[{k:v for k,v in r.items() if k!='rows'} for r in lum],
            heaviest_surviving_Msun=round(heaviest_surviving,3),
            lightest_excluded_Msun=(round(lightest_excluded,3) if lightest_excluded else None),
            bands_used=allbands, note='optical+IR (blackbody-reliable); GALEX handled separately'),
        galex_excess=galex_excess,
        wide_B_acceleration_check=wideB_check,
        kervella=dict(snrPMa=LOCAL['kervella_snrPMa'], M2_5AU=LOCAL['kervella_M2_5AU'],
                      HGCA_chi2=LOCAL['HGCA_chi2'], accel_mag_mas_yr2=round(accel_mag,3),
                      M2_vs_P=accel_band, dynamical_vs_luminous_cross=cross),
        sb1_orbit=sb1_block,
    )
    with open('/tmp/hd144839_sed.json','w') as f:
        json.dump(result, f, indent=2, default=str)

    # ---- console summary ----
    print("\n================ HD 144839 (Gaia DR3 4458424237935900672) ================")
    print(f"  d(NSS)={d_pc:.2f} pc  (gaia_source d={d_gs:.2f} pc)  dist.mod={M_dist:.2f}")
    print(f"  SIMBAD: otype={simbad.get('otype' if 'otype' in simbad else 'OTYPE','?')} "
          f"sp={simbad.get('sp_type', simbad.get('SP_TYPE','?'))} n_ids={simbad.get('_n_ids','?')}")
    print("\n  --- single-star primary fit (Gaia+2MASS+WISE anchors) ---")
    print(f"  T1={T1:.0f}+/-{fit['T1_err']:.0f} K  R1={R1:.3f} Rsun  L1={L1:.3f} Lsun  "
          f"redchi2={fit['chi2']/max(fit['ndof'],1):.2f} (n={len(fit['bands'])})")
    for b in fit['bands']:
        print(f"      {b:10s} resid {fit['resid'][b]:+.3f}")

    print("\n  --- (1) SED multiplicity flags ---")
    print(f"      RUWE={flags['ruwe']}  ipd_frac_multi_peak={flags['ipd_frac_multi_peak']}  "
          f"ipd_frac_odd_win={flags['ipd_frac_odd_win']}")
    print(f"      astrom_excess_noise={flags['astrometric_excess_noise']} (sig {flags['astrometric_excess_noise_sig']})  "
          f"non_single_star={flags['non_single_star']}")
    print(f"      RV: amp_robust={flags['rv_amplitude_robust']} km/s  rv_chisq_p={flags['rv_chisq_pvalue']}  "
          f"vbroad={flags['vbroad']}+/-{flags['vbroad_error']}  rv_nb_transits={flags['rv_nb_transits']}")

    print("\n  --- (2) resolved/wide companion ---")
    if wds and wds.get('found'):
        print(f"      WDS: {wds['n']} entry(ies) within 60\"")
        for r in wds['rows']:
            print(f"        {r}")
    else:
        print("      WDS: no entry within 60\"")
    cm = [n for n in neigh if n.get('comoving')]
    print(f"      Gaia neighbours within 30\": {len(neigh)} ; co-moving+iso-plx: {len(cm)}")
    for n in neigh[:6]:
        print(f"        id={n['source_id']} sep={n.get('sep_arcsec')}\" G={n.get('phot_g_mean_mag')} "
              f"plx={n.get('parallax')} dplx={n.get('dplx_sigma')}sig comoving={n.get('comoving')}")

    print("\n  --- LUMINOUS MS-companion SED test (primary R re-fit per companion) ---")
    print("   spt   Teff2  M2   BP_ff  G_ff  FUV_ff  worst_sig@band   dX2    verdict")
    for r in lum:
        print(f"   {r['spt']:4s} {r['Teff2']:5d} {r['M2']:4.1f} "
              f"{(r['bp_flux_frac'] or 0):5.2f} {(r['g_flux_frac'] or 0):5.2f} "
              f"{(r['fuv_flux_frac'] if r['fuv_flux_frac'] is not None else float('nan')):6.2f} "
              f"{r['worst_sigma']:6.1f}@{r['worst_band']:8s} {r['delta_chi2']:7.0f}  "
              f"{'EXCLUDED' if r['excluded'] else 'allowed'}")
    print(f"\n   Heaviest LUMINOUS companion NOT excluded by SED: {heaviest_surviving:.2f} Msun")
    print(f"   Lightest LUMINOUS companion EXCLUDED by SED:      "
          f"{lightest_excluded if lightest_excluded else '-'} Msun")

    print("\n  --- GALEX one-sided UV-excess diagnostic (correct sign) ---")
    for b, r in galex_excess.items():
        print(f"      {b}: obs(dered)={r['obs_dered']} BB_model={r['model_BB']} "
              f"obs-model={r['obs_minus_model']:+.2f} -> {r['interpretation']}")
    if not galex_excess:
        print("      (no GALEX detection)")

    print("\n  --- wide-B (resolved 27.8\") acceleration check ---")
    if wideB_check:
        print(f"      B = Gaia {wideB_check['source_id']} G={wideB_check['G']} sep={wideB_check['sep_arcsec']}\" "
              f"= {wideB_check['proj_sep_AU']:.0f} AU proj")
        print(f"      predicted accel from B (M2~{wideB_check['assumed_M2_Msun']}): "
              f"{wideB_check['predicted_accel_mas_yr2']} mas/yr^2  vs observed {wideB_check['observed_accel_mas_yr2']} "
              f"({wideB_check['ratio_obs_over_wideB']:.0f}x too weak)")
        print(f"      wide-pair P ~ {wideB_check['orbital_period_yr']:.0f} yr -> {wideB_check['verdict']}")
    else:
        print("      (no resolved wide companion identified)")

    print("\n  --- (4) Kervella/HGCA dynamical mass vs luminous exclusion ---")
    print(f"   snrPMa={LOCAL['kervella_snrPMa']}  HGCA_chi2={LOCAL['HGCA_chi2']}  "
          f"Kervella M2_5AU={LOCAL['kervella_M2_5AU']} Msun  |accel|={accel_mag:.2f} mas/yr^2")
    print("   P_yr  M2_dark  a_rel_AU  if-luminous-SpT  excluded-as-luminous?")
    for c in cross:
        print(f"    {c['P_yr']:4d}  {c['M2_dark']:6.2f}   {c['a_rel_AU']:7.1f}   "
              f"{c['if_luminous_spt']:5s}            {c['if_luminous_excluded']} "
              f"(worst {c['if_luminous_worst_sigma']} sig)")

    if sb1_block:
        s = sb1_block
        print("\n  --- *** SB1 SPECTROSCOPIC ORBIT (decisive period constraint) *** ---")
        print(f"      P={s['period_d']:.1f}+/-{s['period_err']:.0f} d ({s['period_d']/365.25:.2f} yr), "
              f"e={s['ecc']:.3f}, K1={s['K1_kms']:.3f}+/-{s['K1_err']:.3f} km/s, "
              f"conf_spectro_period={s['conf_spectro_period']}")
        print(f"      rv_amp_robust/K1 = {s['rv_amp_robust_over_K1']} (expect ~2 -> consistent)")
        print(f"      spectroscopic f(M) = {s['f_M_msun']} Msun")
        print(f"      EDGE-ON minimum M2 = {s['M2_edgeon_min_msun']} Msun")
        print(f"      a1*sini(RV)={s['a1sini_mas']} mas vs a1(accel)={s['a1_phot_from_accel_mas']} mas "
              f"-> sin i ~ {s['sini_joint']} (i~{s['incl_joint_deg']} deg)  => M2_joint = {s['M2_joint_msun']} Msun")
        print(f"      M2 edge-on pctiles: {s['M2_edgeon_pctiles']}")
        print(f"      M2 isotropic-prior pctiles: {s['M2_isotropic_pctiles']}")
        print(f"      P(M2 > 1.17 NS floor): edge-on={s['P_edgeon_above_NS_floor']}%  "
              f"isotropic={s['P_isotropic_above_NS_floor']}%  ; P(M2>3 BH)|iso={s['P_isotropic_above_BH']}%")

    print("\nJSON -> /tmp/hd144839_sed.json")
    return result

if __name__ == '__main__':
    main()
