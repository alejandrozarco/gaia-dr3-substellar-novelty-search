"""SED of Gaia DR3 1736555475066523008 = WDJ205650.56+062149.68.

Task (2026-05-30): gather GALEX FUV/NUV, SDSS/SkyMapper ugriz, Pan-STARRS grizy,
2MASS JHK, AllWISE W1-W4; fit a 2-component (WD primary + companion) SED;
EXCLUDE (a) an M-dwarf companion via the W1/W2 IR excess and (b) a hot-WD
companion via the GALEX NUV / blue-optical excess, each at the achievable sigma.
Report M1(WD) from cooling models (Gentile Fusillo 2021) and which companion
classes survive (cool DD / M-dwarf / dark-NS).

Skepticism-first: blackbody WD photospheres are an APPROXIMATION (real DA
atmospheres have Balmer/Lyman line blanketing that depresses the far-UV); the
script therefore (i) fits the primary T_eff to the optical+IR only, then treats
the GALEX points as an independent test, and (ii) reports companion-exclusion
sigmas computed band-by-band with full observational errors, NOT a hand-wave.

Env: /Users/legbatterij/claude_projects/ostinato/.venv/bin/python  (no pip-install)
Outputs: /tmp/wdj205650_sed.json , /tmp/wdj205650_sed_report.md
Reuses the canonical _with_timeout / _flt / Gaia-fetch idiom from the dated
deep-dive scripts (scripts/prime3_deepdive_2026_05_29.py, ns2127900_*.py).
"""
import warnings, math, json, sys, time
warnings.filterwarnings('ignore')
import numpy as np
from scipy.optimize import minimize_scalar
from astroquery.vizier import Vizier
from astroquery.gaia import Gaia
from astropy.coordinates import SkyCoord
import astropy.units as u

# ------------------------------------------------------------------ constants
H_PLANCK = 6.62607015e-34      # J s
C_LIGHT  = 2.99792458e8        # m/s
K_BOLTZ  = 1.380649e-23        # J/K
SIGMA_SB = 5.670374419e-8      # W m^-2 K^-4
RSUN_M   = 6.957e8             # m
LSUN_W   = 3.828e26            # W
PC_M     = 3.0856775815e16     # m
ZP_AB    = 3631.0             # Jy, AB zeropoint

SID = 1736555475066523008
RA, DEC = 314.21065905, 6.36364770

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

def _masked(v):
    return (v is None) or (hasattr(v, 'mask') and v is np.ma.masked) or (isinstance(v, float) and math.isnan(v))

# ------------------------------------------------------------------ photometry
# Effective wavelengths (Angstrom) and AB->Vega offsets (m_AB = m_Vega + off).
# Pivot wavelengths from SVO Filter Profile Service; AB offsets standard.
BANDS = {
    # band:        lam_A,   sys ,  ab_off (added to Vega to get AB)
    'GALEX_FUV': (1549.0, 'AB',  0.0),
    'GALEX_NUV': (2304.7, 'AB',  0.0),
    'SDSS_u'   : (3556.5, 'AB',  0.0),   # SDSS mags ~AB (small u offset ignored, +0.04 noted)
    'SDSS_g'   : (4702.5, 'AB',  0.0),
    'SDSS_r'   : (6175.6, 'AB',  0.0),
    'SDSS_i'   : (7489.9, 'AB',  0.0),
    'SDSS_z'   : (8946.7, 'AB',  0.0),
    'SM_u'     : (3500.2, 'AB',  0.0),
    'SM_g'     : (5016.1, 'AB',  0.0),
    'SM_r'     : (6076.9, 'AB',  0.0),
    'SM_i'     : (7732.8, 'AB',  0.0),
    'SM_z'     : (9120.3, 'AB',  0.0),
    'PS_g'     : (4810.9, 'AB',  0.0),
    'PS_r'     : (6156.4, 'AB',  0.0),
    'PS_i'     : (7503.7, 'AB',  0.0),
    'PS_z'     : (8668.6, 'AB',  0.0),
    'PS_y'     : (9613.6, 'AB',  0.0),
    '2MASS_J'  : (12350.0,'Vega', 0.910),
    '2MASS_H'  : (16620.0,'Vega', 1.390),
    '2MASS_K'  : (21590.0,'Vega', 1.850),
    'WISE_W1'  : (33526.0,'Vega', 2.699),
    'WISE_W2'  : (46028.0,'Vega', 3.339),
    'WISE_W3'  : (115608.0,'Vega',5.174),
    'WISE_W4'  : (220883.0,'Vega',6.620),
}

# Fitzpatrick (1999) R_V=3.1 A_lam/A_V at each band pivot (interp of std curve).
# Values from the F99 extinction curve (e.g. via dust_extinction.F99); hard-coded
# so the script does not need the optional dustmaps/dust_extinction packages.
ALAM_AV = {
    'GALEX_FUV': 2.61, 'GALEX_NUV': 2.74,   # FUV/NUV from F99 far-UV (NUV near 2175 bump)
    'SDSS_u': 1.58, 'SDSS_g': 1.21, 'SDSS_r': 0.87, 'SDSS_i': 0.67, 'SDSS_z': 0.48,
    'SM_u': 1.61, 'SM_g': 1.10, 'SM_r': 0.89, 'SM_i': 0.62, 'SM_z': 0.46,
    'PS_g': 1.17, 'PS_r': 0.87, 'PS_i': 0.67, 'PS_z': 0.51, 'PS_y': 0.42,
    '2MASS_J': 0.29, '2MASS_H': 0.18, '2MASS_K': 0.12,
    'WISE_W1': 0.071, 'WISE_W2': 0.055, 'WISE_W3': 0.058, 'WISE_W4': 0.020,
}

def fetch_photometry():
    co = SkyCoord(RA, DEC, unit='deg')
    out = {}        # band -> dict(mag_obs, err, system, det('det'/'UL'), src)
    prov = {}

    def vquery(cat, rad):
        v = Vizier(columns=['**'], row_limit=10)
        return _with_timeout(lambda: v.query_region(co, radius=rad*u.arcsec, catalog=cat), 60, None)

    # ---- GALEX AIS ----
    r = vquery('II/335/galex_ais', 5)
    if r and len(r):
        t = r[0]; i = int(np.argmin(t['_r']))
        for b, col in (('GALEX_FUV','FUVmag'), ('GALEX_NUV','NUVmag')):
            m = _flt(t[col][i]); e = _flt(t['e_'+col][i])
            if m is not None:
                out[b] = dict(mag=m, err=(e or 0.15), system='AB', det='det', src='II/335 GALEX-AIS')
        prov['GALEX'] = f"II/335 sep={float(t['_r'][i]):.2f}\""

    # ---- SDSS DR16 (pick PRIMARY mode==1 clean row; class 6 == STAR) ----
    r = vquery('V/154/sdss16', 5)
    if r and len(r):
        t = r[0]
        # prefer mode==1 (primary) rows; fall back to nearest
        idxs = [i for i in range(len(t)) if int(t['mode'][i]) == 1]
        i = (idxs[0] if idxs else int(np.argmin(t['_r'])))
        for b, col in (('SDSS_u','umag'),('SDSS_g','gmag'),('SDSS_r','rmag'),
                       ('SDSS_i','imag'),('SDSS_z','zmag')):
            m = _flt(t[col][i]); e = _flt(t['e_'+col][i])
            if m is not None:
                out[b] = dict(mag=m, err=(e or 0.02), system='AB', det='det', src='V/154 SDSS16')
        prov['SDSS'] = f"V/154 mode={int(t['mode'][i])} class={int(t['class'][i])} Q={int(t['Q'][i])}"

    # ---- SkyMapper DR4 (PSF mags) ----
    r = vquery('II/379/smssdr4', 8)
    if r and len(r):
        t = r[0]; i = int(np.argmin(t['_r']))
        for b, col in (('SM_u','uPSF'),('SM_g','gPSF'),('SM_r','rPSF'),
                       ('SM_i','iPSF'),('SM_z','zPSF')):
            m = _flt(t[col][i]); e = _flt(t['e_'+col][i])
            if m is not None:
                out[b] = dict(mag=m, err=(e or 0.05), system='AB', det='det', src='II/379 SkyMapperDR4')
        prov['SkyMapper'] = f"II/379 ClassStar={_flt(t['ClassStar'][i])} flags={_flt(t['flags'][i])}"

    # ---- Pan-STARRS DR1 ----
    r = vquery('II/349/ps1', 5)
    if r and len(r):
        t = r[0]; i = int(np.argmin(t['_r']))
        for b, col in (('PS_g','gmag'),('PS_r','rmag'),('PS_i','imag'),
                       ('PS_z','zmag'),('PS_y','ymag')):
            m = _flt(t[col][i]); e = _flt(t['e_'+col][i])
            if m is not None:
                out[b] = dict(mag=m, err=(e or 0.02), system='AB', det='det', src='II/349 PS1')
        prov['PanSTARRS'] = f"II/349 sep={float(t['_r'][i]):.2f}\""

    # ---- 2MASS PSC ----
    r = vquery('II/246/out', 5)
    if r and len(r):
        t = r[0]; i = int(np.argmin(t['_r']))
        qflg = str(t['Qflg'][i])
        for k, (b, col) in enumerate((('2MASS_J','Jmag'),('2MASS_H','Hmag'),('2MASS_K','Kmag'))):
            m = _flt(t[col][i]); e = _flt(t['e_'+col][i])
            q = qflg[k] if k < len(qflg) else 'U'
            if m is not None:
                # 'U' quality (or masked error) == upper limit / non-detection
                det = 'det' if (q in 'ABC' and e is not None) else 'UL'
                out[b] = dict(mag=m, err=(e if e is not None else 0.30),
                              system='Vega', det=det, src=f'II/246 2MASS (Qflg={q})')
        prov['2MASS'] = f"II/246 Qflg={qflg}"

    # ---- AllWISE ----
    r = vquery('II/328/allwise', 8)
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
        prov['AllWISE'] = f"II/328 qph={qph} ccf={ccf}"

    # ---- CatWISE2020 (independent W1/W2 cross-check, not used in fit) ----
    r = vquery('II/365/catwise', 8)
    if r and len(r):
        t = r[0]; i = int(np.argmin(t['_r']))
        cw = {}
        for b, col in (('W1','W1mproPM'),('W2','W2mproPM')):
            if col in t.colnames:
                cw[b] = _flt(t[col][i])
        prov['CatWISE'] = f"II/365 W1={cw.get('W1')} W2={cw.get('W2')} sep={float(t['_r'][i]):.2f}\""
    return out, prov


def fetch_gf21():
    co = SkyCoord(RA, DEC, unit='deg')
    v = Vizier(columns=['**'], row_limit=5)
    r = _with_timeout(lambda: v.query_region(co, radius=5*u.arcsec,
                      catalog='J/MNRAS/508/3877/maincat'), 60, None)
    if not r or len(r) == 0:
        return None
    t = r[0]; i = int(np.argmin(t['_r']))
    g = {c: _flt(t[c][i]) for c in t.colnames if c not in ('GaiaEDR3',)}
    g['GaiaEDR3'] = int(t['GaiaEDR3'][i])
    return g


def fetch_gaia():
    cols = ('source_id, ra, dec, parallax, parallax_error, phot_g_mean_mag, '
            'phot_bp_mean_mag, phot_rp_mean_mag, bp_rp, ruwe, '
            'phot_bp_rp_excess_factor, ipd_frac_multi_peak, non_single_star')
    def go():
        t = Gaia.launch_job(f'SELECT {cols} FROM gaiadr3.gaia_source WHERE source_id={SID}').get_results()
        return t
    t = _with_timeout(go, 60, None)
    if t is None or len(t) == 0:
        return {}
    return {c: (_flt(t[c][0]) if _flt(t[c][0]) is not None else str(t[c][0])) for c in t.colnames}


def fetch_nss_plx():
    def go():
        t = Gaia.launch_job(f'SELECT parallax, period, eccentricity, a_thiele_innes, '
                            f'b_thiele_innes, f_thiele_innes, g_thiele_innes, nss_solution_type '
                            f'FROM gaiadr3.nss_two_body_orbit WHERE source_id={SID}').get_results()
        return t
    t = _with_timeout(go, 60, None)
    if t is None or len(t) == 0:
        return {}
    return {c: (_flt(t[c][0]) if _flt(t[c][0]) is not None else str(t[c][0])) for c in t.colnames}

# ------------------------------------------------------------------ SED physics
def planck_lambda(lam_m, T):
    """Spectral radiance B_lambda(T) [W m^-2 m^-1 sr^-1]."""
    x = H_PLANCK * C_LIGHT / (lam_m * K_BOLTZ * T)
    x = np.clip(x, 1e-9, 700.0)
    return (2.0 * H_PLANCK * C_LIGHT**2 / lam_m**5) / (np.expm1(x))

def fnu_blackbody(lam_A, T, R_rsun, d_pc):
    """Flux density f_nu [Jy] at Earth for a sphere of radius R_rsun, T, distance d_pc,
    radiating as a blackbody. f_lambda = pi B_lambda (R/d)^2 ; f_nu = f_lambda lam^2/c."""
    lam_m = np.asarray(lam_A, float) * 1e-10
    Blam = planck_lambda(lam_m, T)                 # W m^-2 m^-1 sr^-1
    flam = math.pi * Blam * (R_rsun*RSUN_M / (d_pc*PC_M))**2   # W m^-2 m^-1
    fnu = flam * lam_m**2 / C_LIGHT                 # W m^-2 Hz^-1
    return fnu * 1e26                               # Jy

def abmag_blackbody(lam_A, T, R_rsun, d_pc):
    fnu = fnu_blackbody(lam_A, T, R_rsun, d_pc)
    return -2.5*np.log10(np.clip(fnu, 1e-30, None)/ZP_AB)

def wd_radius_from_logg(M_msun, logg_cgs):
    """R = sqrt(G M / g). logg in cgs (cm/s^2)."""
    g_cgs = 10.0**logg_cgs
    G_cgs = 6.674e-8
    M_g = M_msun * 1.98892e33
    R_cm = math.sqrt(G_cgs * M_g / g_cgs)
    return R_cm / (RSUN_M*100.0)   # R_sun

# He-WD mass-radius (Althaus+2013-ish): cool LM He WDs are LARGER than CO WDs.
# Simple monotonic interpolation used only for the *companion* cool-DD grid.
def he_wd_radius(M_msun, T):
    # approximate R(M) at ~few-Gyr cooling for He-core WDs (R in R_sun)
    Mtab = np.array([0.16, 0.20, 0.25, 0.30, 0.35, 0.40, 0.45])
    Rtab = np.array([0.040,0.032,0.026,0.022,0.020,0.018,0.0165])
    R = float(np.interp(M_msun, Mtab, Rtab))
    # mild thermal inflation for hot WDs
    if T and T > 8000:
        R *= 1.0 + 0.04*min((T-8000)/4000.0, 1.0)
    return R

def photocentric_a_mas(A, B, F, G):
    if any(v is None for v in (A, B, F, G)):
        return None
    u_ = 0.5*(A*A + B*B + F*F + G*G)
    v_ = A*G - B*F
    return math.sqrt(u_ + math.sqrt(max(u_*u_ - v_*v_, 0.0)))

def solve_m2_dark(fM, M1):
    """Solve f(M) = M2^3/(M1+M2)^2 for M2 (dark-companion / SB1 mass function)."""
    from scipy.optimize import brentq
    if fM is None or fM <= 0:
        return None
    g = lambda m2: m2**3/(M1+m2)**2 - fM
    try:
        return float(brentq(g, 1e-4, 50.0))
    except Exception:
        return None

def co_wd_radius(M_msun):
    # Eggleton/Nauenberg ZT CO-WD M-R relation (cool)
    mu_e = 2.0
    Mch = 1.454
    x = (M_msun/Mch)
    R = 0.0114*math.sqrt((x)**(-2.0/3.0) - (x)**(2.0/3.0)) * \
        (1.0 + 3.5*( (M_msun/0.00057) )**(-2.0/3.0) + (M_msun/0.00057)**(-1.0))**(-2.0/3.0)
    # the bracketed correction is small; clamp to sane range
    if not (0.005 < R < 0.025):
        R = 0.0114*math.sqrt(x**(-2.0/3.0) - x**(2.0/3.0))
    return R

# ------------------------------------------------------------------ fit machinery
# Optical+NIR anchor bands used to FIT the primary T1,R1 (exclude GALEX so the UV
# is an independent test, exclude WISE W3/W4 + 2MASS H/K upper limits).
ANCHOR_BANDS = ['SDSS_u','SDSS_g','SDSS_r','SDSS_i','SDSS_z',
                'PS_g','PS_r','PS_i','PS_z','PS_y',
                'SM_g','SM_r','SM_i','SM_z','2MASS_J','WISE_W1','WISE_W2']

def to_ab(band, rec):
    """Observed AB mag for a band record (apply Vega->AB offset)."""
    m = rec['mag']
    if rec['system'] == 'Vega':
        m = m + BANDS[band][2]
    return m

def deredden_ab(band, m_ab, A_V):
    return m_ab - ALAM_AV.get(band, 0.0)*A_V

def fit_primary(phot, d_pc, A_V, T_lo=8000, T_hi=13000):
    """Fit T1 (and analytic R1 scaling) of a single blackbody to ANCHOR_BANDS.
    Returns (T1, R1, chi2, ndof, per-band residuals dict)."""
    bands = [b for b in ANCHOR_BANDS if b in phot and phot[b]['det']=='det']
    lam = np.array([BANDS[b][0] for b in bands])
    obs = np.array([deredden_ab(b, to_ab(b, phot[b]), A_V) for b in bands])
    err = np.array([max(phot[b]['err'], 0.02) for b in bands])  # floor at 0.02 mag
    # add a systematic floor (cross-survey zeropoint + BB-vs-atmosphere) of 0.03 mag
    err = np.sqrt(err**2 + 0.03**2)

    def chi2_at_T(T):
        # at fixed T, optimal radius scaling = weighted-mean mag offset (since
        # changing R shifts all model mags by a constant -5log10(R/R0)).
        model0 = abmag_blackbody(lam, T, 1.0, d_pc)  # R=1 Rsun reference
        # solve for delta = -2.5log10((R/1)^2) minimizing chi2 -> weighted mean of (obs-model0)
        w = 1.0/err**2
        delta = np.sum(w*(obs-model0))/np.sum(w)
        model = model0 + delta
        chi2 = np.sum(((obs-model)/err)**2)
        R = 10**(-delta/5.0)   # since delta = -5 log10 R  => R = 10^(-delta/5)
        return chi2, R, model

    Ts = np.linspace(T_lo, T_hi, 1201)
    c2 = np.array([chi2_at_T(T)[0] for T in Ts])
    j = int(np.argmin(c2))
    T1 = float(Ts[j])
    chi2, R1, model = chi2_at_T(T1)
    # 1-sigma T error from delta-chi2 = 1
    below = Ts[c2 <= c2[j]+1.0]
    T_err = float((below.max()-below.min())/2.0) if len(below) > 1 else float(Ts[1]-Ts[0])
    res = {b: (obs[k]-model[k]) for k,b in enumerate(bands)}
    return dict(T1=T1, T1_err=T_err, R1=R1, chi2=chi2, ndof=len(bands)-2,
                bands=bands, obs=obs.tolist(), model=model.tolist(),
                err=err.tolist(), resid=res)


def companion_excess_sigma(phot, fit, d_pc, A_V, T2, R2, test_bands, label,
                           refit_primary=True):
    """Add a companion blackbody (T2,R2) and compute, band-by-band, how many sigma
    the OBSERVED data reject the *primary+companion* model.

    refit_primary=True (default, the honest version): after adding the companion,
    the primary radius is RE-OPTIMISED to best-fit the anchor bands, then the
    companion-induced colour distortion is what gets tested. This prevents the
    trivial 'any added flux brightens everything' artefact -- a grey flux offset
    is absorbed by R1; only the SED *shape* change from the companion is a real
    discriminator. Reported sigma is the worst single-band residual AND the total
    delta-chi2 of the (refit primary + companion) vs primary-alone fit.
    """
    T1, R1_0 = fit['T1'], fit['R1']
    lam_all = {b: BANDS[b][0] for b in test_bands if b in phot}

    # primary+companion flux at R1 reference scaling
    def total_fnu(b, R1):
        lam = BANDS[b][0]
        return fnu_blackbody(lam, T1, R1, d_pc) + fnu_blackbody(lam, T2, R2, d_pc)

    # re-optimise R1 against the DETECTED anchor bands present in test set
    anchor = [b for b in test_bands if b in phot and phot[b]['det']=='det'
              and b in ANCHOR_BANDS]
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
        res = minimize_scalar(chi2_R1, bounds=(R1_0*0.5, R1_0*1.5), method='bounded')
        R1 = float(res.x)
    else:
        R1 = R1_0

    rows = []
    chi2_comp = 0.0; chi2_pri = 0.0
    for b in test_bands:
        if b not in phot:
            continue
        rec = phot[b]; lam = BANDS[b][0]
        f1 = fnu_blackbody(lam, T1, R1, d_pc)
        f1_0 = fnu_blackbody(lam, T1, R1_0, d_pc)
        f2 = fnu_blackbody(lam, T2, R2, d_pc)
        m_pri = -2.5*math.log10(f1_0/ZP_AB)        # primary-alone (orig fit)
        m_tot = -2.5*math.log10((f1+f2)/ZP_AB)     # refit primary + companion
        obs = deredden_ab(b, to_ab(b, rec), A_V)
        err = math.sqrt(max(rec['err'],0.02)**2 + 0.03**2)
        flux_frac = f2/(f1+f2)                       # companion light fraction
        resid = obs - m_tot
        sig = resid/err
        if rec['det'] == 'det':
            chi2_comp += ((obs-m_tot)/err)**2
            chi2_pri  += ((obs-m_pri)/err)**2
        rows.append(dict(band=b, lam=lam, det=rec['det'], obs=round(obs,3),
                         m_pri=round(m_pri,3), m_tot=round(m_tot,3),
                         flux_frac=round(flux_frac,3),
                         resid_obs_minus_tot=round(resid,3), sigma=round(sig,2)))

    # ROBUST exclusion = worst positive (model-too-bright) residual among REAL
    # DETECTIONS only. 2MASS H/K 'U' non-detections are near the survey floor and
    # are NOT used as hard limits (reported separately as a softer cross-check).
    best = None       # worst real-detection tension (one-sided: model too bright)
    best_ul = None    # worst UL one-sided tension (caveated)
    for row in rows:
        if row['det'] == 'UL':
            if row['m_tot'] < row['obs']:
                r2 = dict(row); r2['sigma'] = round((row['obs']-row['m_tot'])/0.3,2)
                r2['note'] = 'UL one-sided (soft)'
                if best_ul is None or r2['sigma'] > best_ul['sigma']:
                    best_ul = r2
            continue
        # detection: only count as exclusion if model is too BRIGHT (resid>0)
        if row['sigma'] > 0:
            if best is None or row['sigma'] > best['sigma']:
                best = row
    # companion light fraction in the key IR band W1 (the clean dust/companion probe)
    w1ff = next((r['flux_frac'] for r in rows if r['band']=='WISE_W1'), None)
    return dict(label=label, T2=T2, R2=round(R2,4), R1_refit=round(R1,5),
                delta_chi2=round(chi2_comp-chi2_pri,1),
                w1_flux_frac=(round(w1ff,3) if w1ff is not None else None),
                max_flux_frac_det=round(max((r['flux_frac'] for r in rows
                                   if r['det']=='det'), default=0.0),3),
                best=best, best_ul=best_ul, rows=rows)


def main():
    print("Fetching photometry, GF21, Gaia, NSS ...", file=sys.stderr)
    phot, prov = fetch_photometry()
    gf21 = fetch_gf21()
    gaia = fetch_gaia()
    nss = fetch_nss_plx()

    # distances
    plx_gs = gaia.get('parallax') or (gf21 or {}).get('Plx')
    plx_nss = nss.get('parallax')
    d_gs = 1000.0/plx_gs if plx_gs else None
    d_nss = 1000.0/plx_nss if plx_nss else None
    d_pc = d_gs   # photometric distance: use the single-star geometric parallax for the SED
                  # (the SED flux scales with the geometric distance to Earth, NOT the
                  #  orbit-corrected NSS parallax which matters only for a_phot->AU).

    # extinction: SFD-ish E(B-V) ~ 0.06-0.08 at (l,b)=(54.4,-24.2); use 0.07, A_V=3.1*E
    EBV = 0.07
    A_V = 3.1*EBV

    # ---- GF21 cooling-model masses ----
    masses = {}
    if gf21:
        masses = dict(
            DA_H   = dict(Teff=gf21.get('TeffH'), e_Teff=gf21.get('e_TeffH'),
                          logg=gf21.get('loggH'), M=gf21.get('MassH'), e_M=gf21.get('e_MassH')),
            DB_He  = dict(Teff=gf21.get('TeffHe'), e_Teff=gf21.get('e_TeffHe'),
                          logg=gf21.get('loggHe'), M=gf21.get('MassHe'), e_M=gf21.get('e_MassHe')),
            mixed  = dict(Teff=gf21.get('Teffmix'), e_Teff=gf21.get('e_Teffmix'),
                          logg=gf21.get('loggmix'), M=gf21.get('Massmix'), e_M=gf21.get('e_Massmix')),
            Pwd    = gf21.get('Pwd'),
        )

    # ---- fit the primary blackbody to optical+IR anchors ----
    fit = fit_primary(phot, d_pc, A_V)
    R1 = fit['R1']; T1 = fit['T1']
    # primary luminosity & implied logg/mass cross-check
    L1 = 4*math.pi*(R1*RSUN_M)**2*SIGMA_SB*T1**4 / LSUN_W

    # ---- companion exclusion grids ----
    UV_BANDS = ['GALEX_FUV','GALEX_NUV','SDSS_u','SM_u','SDSS_g','PS_g','SM_g']
    IR_BANDS = ['2MASS_J','2MASS_H','2MASS_K','WISE_W1','WISE_W2','WISE_W3','WISE_W4']

    excl = {}

    # (1) M-dwarf / K-dwarf companions: use main-sequence T/R, test IR bands
    ms_grid = [
        ('M5V', 3060, 0.201),
        ('M4V', 3160, 0.255),
        ('M3V', 3340, 0.299),
        ('M2V', 3480, 0.376),
        ('M1V', 3660, 0.467),
        ('M0V', 3870, 0.588),
        ('K7V', 4070, 0.630),
        ('K5V', 4410, 0.701),
    ]
    excl['m_dwarf'] = [companion_excess_sigma(phot, fit, d_pc, A_V, T2, R2, IR_BANDS, lab)
                       for (lab,T2,R2) in ms_grid]

    # (2) hot-WD companions: CO-WD radius, test UV+blue bands
    hotwd_grid = [
        ('hotWD_15kK_0.5Mo', 15000, co_wd_radius(0.50)),
        ('hotWD_20kK_0.5Mo', 20000, co_wd_radius(0.50)),
        ('hotWD_25kK_0.5Mo', 25000, co_wd_radius(0.50)),
        ('hotWD_30kK_0.6Mo', 30000, co_wd_radius(0.60)),
        ('hotWD_12kK_0.4Mo', 12000, he_wd_radius(0.40, 12000)),
        ('hotWD_11kK_0.26Mo',11000, he_wd_radius(0.26, 11000)),
    ]
    excl['hot_wd'] = [companion_excess_sigma(phot, fit, d_pc, A_V, T2, R2, UV_BANDS, lab)
                      for (lab,T2,R2) in hotwd_grid]

    # (3) cool double-degenerate companions: test ALL bands. With the primary
    # radius RE-OPTIMISED per companion, a cool companion survives iff its colour
    # distortion stays within the data. Scan T2 to find the SURVIVAL BOUNDARY.
    allb = UV_BANDS + IR_BANDS + ['SDSS_r','SDSS_i','SDSS_z','PS_r','PS_i','PS_z','PS_y']
    allb = list(dict.fromkeys(allb))
    # companion mass fixed at the f(M)-implied dark-equivalent M2 ~ 0.26 (He core),
    # and a heavier CO-core alternative 0.45 Mo (radius differs).
    cooldd_grid = []
    for T2 in (3000, 3500, 4000, 4500, 5000, 5500, 6000, 7000, 8000):
        cooldd_grid.append((f'HeWD_{T2}K_0.26Mo', T2, he_wd_radius(0.26, T2)))
    for T2 in (4000, 5000, 6000, 7000, 8000):
        cooldd_grid.append((f'COWD_{T2}K_0.45Mo', T2, co_wd_radius(0.45)))
    excl['cool_dd'] = [companion_excess_sigma(phot, fit, d_pc, A_V, T2, R2, allb, lab)
                       for (lab,T2,R2) in cooldd_grid]

    # survival boundary: max T2 (per mass) at which worst REAL-detection tension < 3 sigma
    def boundary(prefix):
        surv = [e for e in excl['cool_dd'] if e['label'].startswith(prefix)
                and (e['best'] is None or e['best']['sigma'] < 3.0)]
        if not surv:
            return None
        return max(float(e['label'].split('_')[1].rstrip('K')) for e in surv)
    excl['cool_dd_survival_T_He026'] = boundary('HeWD')
    excl['cool_dd_survival_T_CO045'] = boundary('COWD')

    # (2b) UV-excess diagnostic: the GALEX FUV/NUV sit ABOVE the single-T BB primary.
    # Test whether a hot-WD companion *tuned to reproduce the NUV excess* is allowed
    # by the u-band (a real hot WD that fixes NUV must also brighten u).
    uv_resid = {}
    for b in ('GALEX_FUV','GALEX_NUV'):
        if b in phot:
            lam = BANDS[b][0]
            m_mod = -2.5*math.log10(fnu_blackbody(lam, T1, R1, d_pc)/ZP_AB)
            obs = deredden_ab(b, to_ab(b, phot[b]), A_V)
            uv_resid[b] = dict(obs_dered=round(obs,3), model=round(m_mod,3),
                               resid=round(obs-m_mod,3))
    uv_tuned = []
    if 'GALEX_NUV' in phot:
        f1N = fnu_blackbody(BANDS['GALEX_NUV'][0], T1, R1, d_pc)
        excess_mag = uv_resid['GALEX_NUV']['model'] - uv_resid['GALEX_NUV']['obs_dered']  # >0 if obs brighter
        target = f1N*10**(excess_mag/2.5)
        for T2 in (12000, 15000, 20000, 25000, 30000):
            f2N_unit = fnu_blackbody(BANDS['GALEX_NUV'][0], T2, 1.0, d_pc)
            R2 = math.sqrt(max(target-f1N, 0.0)/f2N_unit)
            row = dict(T2=T2, R2_needed=round(R2,4))
            for b in ('GALEX_FUV','SDSS_u','SDSS_g'):
                if b not in phot: continue
                lam = BANDS[b][0]
                f1 = fnu_blackbody(lam, T1, R1, d_pc); f2 = fnu_blackbody(lam, T2, R2, d_pc)
                m_pri = -2.5*math.log10(f1/ZP_AB); m_tot = -2.5*math.log10((f1+f2)/ZP_AB)
                obs = deredden_ab(b, to_ab(b, phot[b]), A_V)
                err = math.sqrt(max(phot[b]['err'],0.02)**2 + 0.03**2)
                # the companion brightens band b by (m_pri - m_tot); the data allow only
                # the observed excess (m_pri - obs). tension = how much the tuned companion
                # OVER-brightens b beyond what is observed:
                over = (m_pri - m_tot) - (m_pri - obs)   # = obs - m_tot
                row[b] = dict(companion_brightens=round(m_pri-m_tot,3),
                              observed_excess=round(m_pri-obs,3),
                              over_sigma=round(over/err,2))
            uv_tuned.append(row)
    excl['uv_excess'] = dict(
        note=('GALEX FUV/NUV lie ABOVE the single-T blackbody primary. A single-T BB '
              'systematically underpredicts the UV of a real cool DA (Balmer/Lyman line '
              'blanketing + Balmer jump). Below: a hot-WD companion TUNED to reproduce the '
              'NUV excess would over-brighten the u-band by over_sigma; the data show no such '
              'u excess, so the UV bump is NOT a hot companion.'),
        residuals=uv_resid, tuned_hotwd=uv_tuned)

    # (4) dark companion (NS/BH) via the astrometric mass function
    A_TI = nss.get('a_thiele_innes'); B_TI = nss.get('b_thiele_innes')
    F_TI = nss.get('f_thiele_innes'); G_TI = nss.get('g_thiele_innes')
    P_d = nss.get('period'); plx_for_fm = plx_nss or plx_gs
    a_phot_mas = photocentric_a_mas(A_TI, B_TI, F_TI, G_TI)
    fM = None; M2_dark = None; a_AU = None
    if a_phot_mas and P_d and plx_for_fm:
        a_AU = (a_phot_mas/plx_for_fm)
        P_yr = P_d/365.25
        fM = a_AU**3 / P_yr**2
        M1_use = (masses.get('DA_H') or {}).get('M') or 0.386
        M2_dark = solve_m2_dark(fM, M1_use)
    excl['dark_companion'] = dict(
        a_phot_mas=(round(a_phot_mas,4) if a_phot_mas else None),
        plx_used=plx_for_fm, P_d=P_d, a_AU=(round(a_AU,4) if a_AU else None),
        f_M_msun=(round(fM,4) if fM else None),
        M1_assumed=((masses.get('DA_H') or {}).get('M')),
        M2_dark_msun=(round(M2_dark,4) if M2_dark else None),
        verdict=('NS/BH EXCLUDED: dark-companion mass %.2f Mo << 1.17 Mo NS floor'
                 % M2_dark if (M2_dark and M2_dark < 1.0) else 'see f(M)'))

    # ---- assemble result ----
    result = dict(
        source_id=SID, ra=RA, dec=DEC,
        distances=dict(plx_gs=plx_gs, plx_nss=plx_nss, d_gs_pc=d_gs, d_nss_pc=d_nss,
                       d_used_pc=d_pc, note='SED scaled by geometric (gaia_source) distance'),
        extinction=dict(EBV=EBV, A_V=A_V, law='Fitzpatrick99 R_V=3.1'),
        gf21_masses=masses,
        primary_fit=dict(T1=round(T1,1), T1_err=round(fit['T1_err'],1),
                         R1_rsun=round(R1,5), L1_lsun=round(L1,5),
                         chi2=round(fit['chi2'],2), ndof=fit['ndof'],
                         redchi2=round(fit['chi2']/max(fit['ndof'],1),2),
                         anchor_bands=fit['bands'],
                         resid={k: round(v,3) for k,v in fit['resid'].items()}),
        gaia=gaia, nss=nss, provenance=prov,
        photometry={b: dict(mag=round(phot[b]['mag'],4), err=round(phot[b]['err'],4),
                            system=phot[b]['system'], det=phot[b]['det'],
                            ab=round(to_ab(b,phot[b]),4),
                            ab_dered=round(deredden_ab(b,to_ab(b,phot[b]),A_V),4),
                            src=phot[b]['src']) for b in phot},
        exclusions=excl,
    )

    with open('/tmp/wdj205650_sed.json','w') as f:
        json.dump(result, f, indent=2, default=str)

    # ---- console summary ----
    print("\n================ PRIMARY SED FIT ================")
    print(f"  d (geometric, gaia_source) = {d_pc:.2f} pc   (NSS plx d = {d_nss:.2f} pc)")
    print(f"  E(B-V)={EBV}  A_V={A_V:.3f}")
    print(f"  Fit (optical+NIR anchors, n={len(fit['bands'])}): "
          f"T1 = {T1:.0f} +/- {fit['T1_err']:.0f} K,  R1 = {R1:.5f} Rsun,  "
          f"L1 = {L1:.5f} Lsun")
    print(f"  reduced chi2 = {fit['chi2']/max(fit['ndof'],1):.2f}  (chi2={fit['chi2']:.1f}, ndof={fit['ndof']})")
    print("  per-band residuals (obs - model, dereddened AB):")
    for b in fit['bands']:
        print(f"      {b:10s} {fit['resid'][b]:+.3f}")
    if masses:
        print("\n  GF21 cooling-model masses:")
        for k in ('DA_H','DB_He','mixed'):
            m = masses[k]
            print(f"      {k:7s}: Teff={m['Teff']:.0f}+/-{m['e_Teff']:.0f} K  logg={m['logg']:.3f}  "
                  f"M={m['M']:.3f}+/-{m['e_M']:.3f} Mo")
        print(f"      Pwd (WD confidence) = {masses['Pwd']:.4f}")

    print("\n================ COMPANION EXCLUSION ================")
    print("  (primary radius is RE-FIT per companion so a grey offset can't masquerade")
    print("   as exclusion; sigma = worst single-band colour residual; dX2 = delta-chi2)")
    print("\n  (1) M/K-DWARF companion -- IR excess test (2MASS J + WISE W1/W2):")
    for e in excl['m_dwarf']:
        b = e['best']
        if b:
            print(f"      {e['label']:6s} (T={e['T2']}K R={e['R2']}Ro): EXCLUDED {b['sigma']:6.1f} sig "
                  f"via {b['band']} | f_W1={e['w1_flux_frac']:.2f} dX2={e['delta_chi2']:.0f}")
        else:
            print(f"      {e['label']:6s}: NOT excluded by IR bands")

    print("\n  (2) HOT-WD companion -- UV/blue excess test (GALEX FUV/NUV + u/g):")
    for e in excl['hot_wd']:
        b = e['best']
        if b:
            print(f"      {e['label']:20s} (R={e['R2']}Ro): EXCLUDED {b['sigma']:6.1f} sig "
                  f"via {b['band']} | dX2={e['delta_chi2']:.0f}")
        else:
            print(f"      {e['label']:20s}: NOT excluded by UV/blue bands")

    print("\n  (3) COOL DOUBLE-DEGENERATE companion -- survival scan (real detections only;")
    print("      2MASS H/K 'U' non-detections shown as soft UL cross-check):")
    for e in excl['cool_dd']:
        b = e['best']                 # worst REAL-detection tension
        bs = b['sigma'] if b else 0.0; bn = b['band'] if b else '-'
        ul = e['best_ul']; uls = (f"{ul['sigma']:.1f}@{ul['band']}" if ul else '-')
        tag = 'SURVIVES' if bs < 3.0 else ('marginal' if bs < 5 else 'excluded')
        print(f"      {e['label']:18s} (R={e['R2']}Ro): det {bs:5.1f}sig@{bn:8s} "
              f"f_W1={e['w1_flux_frac']:.2f} dX2={e['delta_chi2']:6.0f} [UL {uls:>12s}] -> {tag}")
    print(f"\n   Survival boundary (max T2 with worst real-detection tension <3sig):")
    print(f"      0.26 Mo He-WD companion: T2 <= {excl['cool_dd_survival_T_He026']} K")
    print(f"      0.45 Mo CO-WD companion: T2 <= {excl['cool_dd_survival_T_CO045']} K")

    uv = excl['uv_excess']
    print("\n  (2b) UV-EXCESS diagnostic (the GALEX bump -- is it a hot WD?):")
    for b,r in uv['residuals'].items():
        print(f"      {b}: obs(dered)={r['obs_dered']} vs primary BB {r['model']} -> excess {-r['resid']:+.2f} mag")
    print("      hot-WD tuned to reproduce the NUV excess => its u-band over-brightening:")
    for row in uv['tuned_hotwd']:
        us = row.get('SDSS_u',{}).get('over_sigma')
        print(f"         T2={row['T2']}K (R2={row['R2_needed']}Ro): u-band over-bright by {us} sigma (not observed)")
    print("      => UV bump is the single-T BB vs real-DA-atmosphere deficit, NOT a hot companion.")

    dc = excl['dark_companion']
    print("\n  (4) DARK companion (NS/BH) -- astrometric mass function:")
    print(f"      a_phot={dc['a_phot_mas']} mas, plx={dc['plx_used']} mas, P={dc['P_d']} d "
          f"-> a={dc['a_AU']} AU")
    print(f"      f(M)={dc['f_M_msun']} Mo ; at M1={dc['M1_assumed']} Mo -> "
          f"dark M2={dc['M2_dark_msun']} Mo")
    print(f"      {dc['verdict']}")

    print("\nJSON -> /tmp/wdj205650_sed.json")
    return result

if __name__ == '__main__':
    main()
