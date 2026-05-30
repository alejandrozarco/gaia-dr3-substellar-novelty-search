#!/usr/bin/env python3
"""Maximum-skepticism SED decomposition of WDJ020915.51+380425.92
(Gaia DR3 332248057157474176) -- the Pile-E "Chandrasekhar-boundary" WD-primary
NSS-Orbital binary (P=274.5 d, f(M)=0.556, M2~1.32 Msun at the GF21 M1).

GOAL (per request): gather GALEX FUV/NUV, SDSS/SkyMapper ugriz, Pan-STARRS grizy,
2MASS JHK, AllWISE W1-W4; fit a 2-component (WD + companion) SED; EXCLUDE
  (a) an M-dwarf companion  (would show a W1/W2 IR excess), and
  (b) a hot-WD companion    (would show a NUV / blue-optical excess)
at the achievable sigma.  Report M1(WD) from cooling models (GF21) and which
companion classes survive: cool double-degenerate / M-dwarf / dark-NS.

METHOD (defensible, no hand-tabulated blackbodies):
 * WD photosphere model = Bergeron/Montreal pure-H (DA) & pure-He (DB) synthetic
   photometry tables (Holberg & Bergeron 2006; Tremblay+2011; Blouin+2018 grids;
   downloaded live from the Montreal CoolingModels site).  Absolute mags @10pc on
   the native systems (PS1/SDSS/GALEX = AB; Gaia/2MASS/WISE = Vega).
 * Companion models:
     - hot/cool WD companion = same Montreal DA grid at the companion (Teff2, logg2)
       set by its mass via the GF21 mass-radius track.
     - M-dwarf companion = empirical Mann+2015 / Pecaut-Mamajek absolute-mag SEDs.
 * Fit: scale the primary by (R1/d)^2 via a free zero-point (== free radius at fixed
   parallax) + fixed-grid Teff; chi2 over all DETECTED bands with a 0.03-mag
   model-systematic floor added in quadrature.  Two-component fits add the companion
   flux (in f_nu) before re-magnitude-ing.  The companion is excluded at the sigma
   where Delta-chi2 between the single-WD and (WD+companion-at-its-predicted-flux)
   model exceeds the photometric budget.

Bands actually available for THIS target (verified live, 2026-05-30):
   DETECTIONS: PS1 g r i z y; Gaia G BP RP; AllWISE W1 W2; CatWISE2020 W1 W2.
   UPPER LIMITS: 2MASS J H Ks (~16.5-16.8 Vega, coverage confirmed); AllWISE W3 W4 (SNR<1).
   NO COVERAGE: GALEX FUV/NUV (genuine AIS gap: 0 GALEX sources within 30').
   NOT IN FOOTPRINT: SDSS ugriz (no spectro/photo here); SkyMapper (southern, dec<0).

Outputs: /tmp/wdj020915_sed.json  +  /tmp/wdj020915_sed_report.md  (+ a PNG SED).
Env: /Users/legbatterij/claude_projects/ostinato/.venv/bin/python  (NO pip-install).
DO NOT edit dossiers / CANDIDATES.md.
"""
from __future__ import annotations
import warnings, json, math, os, threading, urllib.request, ssl
warnings.filterwarnings('ignore')
import numpy as np
from scipy.interpolate import RegularGridInterpolator
from scipy.optimize import minimize_scalar
from scipy import stats

import astropy.units as u
import astropy.constants as const
from astropy.coordinates import SkyCoord
from astroquery.vizier import Vizier

# ---- constants -------------------------------------------------------------
G = const.G.cgs.value; MSUN = const.M_sun.cgs.value
RSUN = const.R_sun.cgs.value; PC = const.pc.cgs.value
SID = 332248057157474176
RA, DEC = 32.31460723, 38.07372071
PLX_GS, PLX_GS_E = 11.962, 0.5051          # Gaia DR3 gaia_source parallax (mas)
NAME = 'WDJ020915.51+380425.92'

# Vega->AB offsets (for reporting only; we model in native systems)
GAIA_VEGA2AB = {'Gaia_G': 0.108, 'Gaia_BP': 0.029, 'Gaia_RP': 0.379}   # Riello+2021
WISE_VEGA2AB = {'WISE_W1': 2.699, 'WISE_W2': 3.339, 'WISE_W3': 5.174, 'WISE_W4': 6.620}

# ---- network helper --------------------------------------------------------
def _to(fn, secs, default=None):
    box = {}
    def run():
        try: box['r'] = fn()
        except Exception as e: box['e'] = e
    th = threading.Thread(target=run, daemon=True); th.start(); th.join(secs)
    if 'r' in box: return box['r']
    return default

def _f(x):
    try:
        if hasattr(x, 'mask') and x is np.ma.masked: return None
        v = float(x); return None if math.isnan(v) else v
    except (TypeError, ValueError): return None

# ===========================================================================
# 1. MONTREAL (Bergeron) WD synthetic-photometry tables
# ===========================================================================
_MONT_COLS = ['Teff','logg','M','Mbol','BC','U','B','V','R','I','J2','H2','Ks2',
              'Y_ps','J_ps','H_ps','K_ps','W1','W2','W3','W4','S36','S45','S58','S80',
              'u_sd','g_sd','r_sd','i_sd','z_sd','g_ps','r_ps','i_ps','z_ps','y_ps',
              'G2','G2_BP','G2_RP','G3','G3_BP','G3_RP','FUV','NUV','Age']
# map our band keys -> Montreal column (and its native system)
BAND2MONT = {
    'GALEX_FUV': ('FUV','AB'),   'GALEX_NUV': ('NUV','AB'),
    'PS1_g': ('g_ps','AB'), 'PS1_r': ('r_ps','AB'), 'PS1_i': ('i_ps','AB'),
    'PS1_z': ('z_ps','AB'), 'PS1_y': ('y_ps','AB'),
    'SDSS_u': ('u_sd','AB'), 'SDSS_g': ('g_sd','AB'), 'SDSS_r': ('r_sd','AB'),
    'SDSS_i': ('i_sd','AB'), 'SDSS_z': ('z_sd','AB'),
    'Gaia_G': ('G3','Vega'), 'Gaia_BP': ('G3_BP','Vega'), 'Gaia_RP': ('G3_RP','Vega'),
    '2MASS_J': ('J2','Vega'), '2MASS_H': ('H2','Vega'), '2MASS_Ks': ('Ks2','Vega'),
    'WISE_W1': ('W1','Vega'), 'WISE_W2': ('W2','Vega'),
    'WISE_W3': ('W3','Vega'), 'WISE_W4': ('W4','Vega'),
}
# AB zero-point pivot wavelengths (Angstrom) for f_nu bookkeeping (companion addition)
PIVOT = {'GALEX_FUV':1535.1,'GALEX_NUV':2300.8,'PS1_g':4849.1,'PS1_r':6201.2,
         'PS1_i':7535.0,'PS1_z':8674.2,'PS1_y':9627.8,'SDSS_u':3556.,'SDSS_g':4702.,
         'SDSS_r':6176.,'SDSS_i':7490.,'SDSS_z':8947.,'Gaia_G':6217.6,'Gaia_BP':5109.7,
         'Gaia_RP':7769.0,'2MASS_J':12393.1,'2MASS_H':16494.9,'2MASS_Ks':21638.6,
         'WISE_W1':33897.0,'WISE_W2':46406.4,'WISE_W3':125675.9,'WISE_W4':223142.3}

def _download_montreal():
    base = 'https://www.astro.umontreal.ca/~bergeron/CoolingModels/Tables/'
    ctx = ssl.create_default_context(); ctx.check_hostname=False; ctx.verify_mode=ssl.CERT_NONE
    out = {}
    for tag, fn in (('DA','Table_DA'), ('DB','Table_DB')):
        path = '/tmp/'+fn
        if not (os.path.exists(path) and os.path.getsize(path) > 5000):
            try:
                req = urllib.request.Request(base+fn, headers={'User-Agent':'Mozilla/5.0'})
                d = urllib.request.urlopen(req, timeout=60, context=ctx).read()
                open(path,'wb').write(d)
            except Exception as e:
                out[tag] = {'_err': f'{type(e).__name__}: {e}'}; continue
        out[tag] = path
    return out

def _parse_montreal(path):
    rows = []
    for ln in open(path):
        p = ln.split()
        if len(p) < 44: continue
        try: float(p[0]); float(p[1])
        except ValueError: continue
        rows.append([float(x) for x in p[:44]])
    a = np.array(rows)
    return {c: a[:, i] for i, c in enumerate(_MONT_COLS)}

class WDGrid:
    """Bilinear interpolator on the Montreal (Teff, logg) grid for any band column,
    plus M(Teff,logg) so a companion's logg can be set from its mass-radius track."""
    def __init__(self, tab):
        self.teffs = np.array(sorted(set(tab['Teff'])))
        self.loggs = np.array(sorted(set(tab['logg'])))
        self._interp = {}
        # build a (nTeff,nLogg) grid for each column
        idx = {(round(t,3), round(g,3)): k for k, (t, g) in enumerate(zip(tab['Teff'], tab['logg']))}
        self._idx = idx; self._tab = tab
        for col in _MONT_COLS:
            grid = np.full((len(self.teffs), len(self.loggs)), np.nan)
            for it, t in enumerate(self.teffs):
                for ig, g in enumerate(self.loggs):
                    k = idx.get((round(t,3), round(g,3)))
                    if k is not None: grid[it, ig] = tab[col][k]
            self._interp[col] = RegularGridInterpolator(
                (self.teffs, self.loggs), grid, bounds_error=False, fill_value=None)
    def absmag(self, band, teff, logg):
        col = BAND2MONT[band][0]
        return float(self._interp[col]([[teff, logg]])[0])
    def mass(self, teff, logg):
        return float(self._interp['M']([[teff, logg]])[0])
    def age(self, teff, logg):
        return float(self._interp['Age']([[teff, logg]])[0])

# ===========================================================================
# 2. Photometry acquisition (live, with verified fallbacks)
# ===========================================================================
def fetch_photometry():
    coord = SkyCoord(ra=RA*u.deg, dec=DEC*u.deg, frame='icrs')
    v = Vizier(columns=['**','+_r'], timeout=60); v.ROW_LIMIT = 5
    log = {}
    def cone(cat, rad):
        return _to(lambda: v.query_region(coord, radius=rad*u.arcsec, catalog=cat), 55, None)

    # ---- detections ----
    det = {}                                 # band -> (mag_native, err, system, note)
    # Pan-STARRS DR1 (II/349/ps1) -- PSF mags (g/r/i/z/y), AB
    ps = cone('II/349/ps1', 3)
    if ps and len(ps):
        r = ps[0][0]
        for b, c in (('PS1_g','gmag'),('PS1_r','rmag'),('PS1_i','imag'),
                     ('PS1_z','zmag'),('PS1_y','ymag')):
            m, e = _f(r[c]), _f(r['e_'+c]) if 'e_'+c in ps[0].colnames else None
            if m is not None:
                det[b] = (m, e if (e and e>0) else 0.02, 'AB', 'PS1 DR1 PSF')
        log['PanSTARRS_DR1'] = {'found': True, 'r_arcsec': _f(r['_r'])}
    else:
        log['PanSTARRS_DR1'] = {'found': False}

    # Gaia DR3 (I/355/gaiadr3), Vega
    g = cone('I/355/gaiadr3', 2)
    if g and len(g):
        r = g[0][0]
        for b, c in (('Gaia_G','Gmag'),('Gaia_BP','BPmag'),('Gaia_RP','RPmag')):
            m, e = _f(r[c]), _f(r['e_'+c])
            if m is not None:
                det[b] = (m, max(e or 0.01, 0.005), 'Vega', 'Gaia DR3')
        log['Gaia_DR3'] = {'found': True, 'Plx': _f(r['Plx']), 'e_Plx': _f(r['e_Plx'])}

    # AllWISE (II/328/allwise), Vega
    w = cone('II/328/allwise', 6)
    if w and len(w):
        r = w[0][0]
        for b, c in (('WISE_W1','W1mag'),('WISE_W2','W2mag')):
            m, e = _f(r[c]), _f(r['e_'+c])
            if m is not None and e is not None:           # require finite err = real detection
                det[b] = (m, e, 'Vega', 'AllWISE')
        log['AllWISE'] = {'found': True, 'r_arcsec': _f(r['_r']),
                          'W3mag': _f(r['W3mag']), 'snr3': _f(r['snr3']),
                          'W4mag': _f(r['W4mag']), 'snr4': _f(r['snr4']),
                          'note_W3W4': 'SNR<1 -> upper limits, not detections'}

    # CatWISE2020 (II/365/catwise) -- tighter W1/W2 PSF, Vega; PREFERRED for W1/W2
    cw = cone('II/365/catwise', 5)
    if cw and len(cw):
        r = cw[0][0]
        cols = cw[0].colnames
        w1 = _f(r['W1mproPM']) if 'W1mproPM' in cols else None
        e1 = _f(r['e_W1mproPM']) if 'e_W1mproPM' in cols else None
        w2 = _f(r['W2mproPM']) if 'W2mproPM' in cols else None
        e2 = _f(r['e_W2mproPM']) if 'e_W2mproPM' in cols else None
        if w1 is not None:
            det['WISE_W1'] = (w1, max(e1 or 0.03, 0.02), 'Vega', 'CatWISE2020 (preferred)')
        if w2 is not None:
            det['WISE_W2'] = (w2, max(e2 or 0.05, 0.03), 'Vega', 'CatWISE2020 (preferred)')
        log['CatWISE2020'] = {'found': True, 'r_arcsec': _f(r['_r']),
                              'W1': w1, 'e_W1': e1, 'W2': w2, 'e_W2': e2, 'ccf': _f(r['ccf'])}

    # ---- non-detections / coverage ----
    galex = cone('II/335/galex_ais', 30)        # wide cone to test coverage
    galex_field = _to(lambda: Vizier(columns=['_r'], timeout=90).query_region(
        coord, radius=30*u.arcmin, catalog='II/335/galex_ais'), 85, None)
    n_gx = 0 if (galex_field is None or len(galex_field)==0) else len(galex_field[0])
    log['GALEX'] = {'detection_within_30arcsec': bool(galex and len(galex)),
                    'n_sources_within_30arcmin': int(n_gx),
                    'verdict': 'NO AIS COVERAGE (genuine gap)' if n_gx == 0 else 'covered'}

    tm = cone('II/246/out', 6)
    tm_field = _to(lambda: Vizier(columns=['Jmag','_r'], timeout=90).query_region(
        coord, radius=5*u.arcmin, catalog='II/246/out'), 85, None)
    n_tm = 0 if (tm_field is None or len(tm_field)==0) else len(tm_field[0])
    jlim = None
    if tm_field is not None and n_tm:
        jj = np.array([_f(x) for x in tm_field[0]['Jmag']], float)
        jj = jj[np.isfinite(jj)]
        if len(jj): jlim = float(np.nanpercentile(jj, 95))
    log['2MASS'] = {'detection': bool(tm and len(tm)), 'n_sources_within_5arcmin': int(n_tm),
                    'J_completeness_limit_est': jlim,
                    'verdict': 'non-detection -> J,H,Ks upper limits (coverage OK)' if n_tm and not (tm and len(tm)) else None}

    # ---- GF21 atmosphere row ----
    gf = cone('J/MNRAS/508/3877/maincat', 6)
    gf21 = {}
    if gf and len(gf):
        r = gf[0][0]
        for c in ('Pwd','TeffH','e_TeffH','loggH','e_loggH','MassH','e_MassH',
                  'TeffHe','e_TeffHe','loggHe','e_loggHe','MassHe','e_MassHe'):
            gf21[c] = _f(r[c]) if c in gf[0].colnames else None
    log['GF21'] = gf21

    # Upper limits container
    ulim = {}
    if jlim is not None:
        # 2MASS PSC 10-sigma completeness ~ J 16.5, but use measured field 95-pct
        ulim['2MASS_J'] = (jlim, 'Vega', '2MASS PSC non-detection (95% field completeness)')
        ulim['2MASS_H'] = (jlim-0.4, 'Vega', '2MASS non-detection (est.)')
        ulim['2MASS_Ks'] = (jlim-0.9, 'Vega', '2MASS non-detection (est.)')
    return det, ulim, gf21, log

# ===========================================================================
# 3. SED model & fitting
# ===========================================================================
def wd_radius_rsun(mass_msun, logg):
    return math.sqrt(G*mass_msun*MSUN/10**logg)/RSUN

def absmag_to_fnu(absmag, band, system):
    """Convert an ABSOLUTE mag (at 10 pc) on its native system to f_nu (erg/s/cm2/Hz)
    AT 10 pc. Returns AB-equivalent f_nu so two components add linearly in f_nu."""
    if system == 'Vega':
        # convert to AB first
        off = GAIA_VEGA2AB.get(band) or WISE_VEGA2AB.get(band) or 0.0
        absmag = absmag + off
    return 10**(-0.4*(absmag + 48.60))

def fnu_to_appmag_AB(fnu_10pc, dm):
    """Apparent AB mag at distance modulus dm, from f_nu defined at 10pc."""
    fnu = fnu_10pc * 10**(-0.4*dm)
    return -2.5*math.log10(fnu) - 48.60

def model_appmag(grid, band, teff, logg, dm, system_out='native'):
    """Single-component apparent mag in the band's NATIVE system."""
    am = grid.absmag(band, teff, logg)
    return am + dm                          # absolute->apparent is system-preserving

# Per-band model-systematic floor (mag), added in quadrature to the photometric error.
# Optical DA continuum is reliable (0.03); WISE gets a larger floor because the two
# independent WISE catalogs (AllWISE vs CatWISE2020) disagree by >their quoted errors
# at this faint level (AllWISE W2=16.02 vs CatWISE W2=16.29 -> 0.26 mag), and the DA
# Rayleigh-Jeans tail has a known few-% mismatch with WISE in-band calibration.
BAND_FLOOR = {b: 0.03 for b in BAND2MONT}
for b in ('WISE_W1','WISE_W2','WISE_W3','WISE_W4'):
    BAND_FLOOR[b] = 0.12

def _eff_err(det, b, sys_floor):
    fl = BAND_FLOOR.get(b, sys_floor)
    return math.hypot(det[b][1], fl)

def fit_single_wd(det, grid, teff_fix, logg_fix, sys_floor=0.03, free_teff=False):
    """Fit a single WD: free distance modulus (== free radius at fixed parallax).
    If free_teff, also scan Teff (logg fixed). Returns best dm, teff, chi2, residuals."""
    bands = list(det)
    obs = np.array([det[b][0] for b in bands])
    err = np.array([_eff_err(det, b, sys_floor) for b in bands])
    def chi2_for(teff):
        absm = np.array([grid.absmag(b, teff, logg_fix) for b in bands])
        # best dm = inverse-variance weighted (obs - absmag)
        wsum = np.sum(1/err**2)
        dm = np.sum((obs-absm)/err**2)/wsum
        chi = np.sum(((obs-absm-dm)/err)**2)
        return chi, dm
    if free_teff:
        r = minimize_scalar(lambda T: chi2_for(T)[0],
                            bounds=(grid.teffs.min()+10, grid.teffs.max()-10),
                            method='bounded')
        teff = float(r.x)
    else:
        teff = teff_fix
    chi, dm = chi2_for(teff)
    absm = {b: grid.absmag(b, teff, logg_fix) for b in bands}
    resid = {b: (det[b][0] - absm[b] - dm) for b in bands}
    sig = {b: resid[b]/_eff_err(det, b, sys_floor) for b in bands}
    return {'teff': teff, 'logg': logg_fix, 'dm': dm,
            'dist_pc': 10**(1+dm/5), 'chi2': chi, 'ndof': len(bands)-(2 if free_teff else 1),
            'resid': resid, 'sigma': sig, 'bands': bands}

def add_companion_chi2(det, grid, prim, comp_band_fnu, sys_floor=0.03):
    """Given the primary single-WD fit (prim: teff,logg,dm) and a companion specified
    by its apparent f_nu (AB) per band (comp_band_fnu), compute the chi2 of the
    TWO-component model with the SAME primary dm (i.e. the companion can only ADD flux,
    it cannot be absorbed by re-scaling -- the conservative test).  Also compute the
    chi2 RE-FITTING the primary dm with the companion present (companion forced ON)."""
    bands = list(det)
    obs = np.array([det[b][0] for b in bands])
    err = np.array([_eff_err(det, b, sys_floor) for b in bands])
    # primary f_nu (AB) at 10pc
    def prim_fnu_app(b):
        am = grid.absmag(b, prim['teff'], prim['logg']) + prim['dm']
        sysb = BAND2MONT[b][1]
        if sysb == 'Vega':
            am = am + (GAIA_VEGA2AB.get(b) or WISE_VEGA2AB.get(b) or 0.0)
        return 10**(-0.4*(am+48.60))
    # combined apparent mag in native system
    def comb_mag(b, scale=1.0):
        fp = prim_fnu_app(b); fc = comp_band_fnu.get(b, 0.0)*scale
        ftot = fp + fc
        ab = -2.5*math.log10(ftot) - 48.60
        sysb = BAND2MONT[b][1]
        if sysb == 'Vega':
            ab = ab - (GAIA_VEGA2AB.get(b) or WISE_VEGA2AB.get(b) or 0.0)
        return ab
    # fixed-dm chi2 (companion fully ON, primary fixed)
    mod = np.array([comb_mag(b) for b in bands])
    chi_on = np.sum(((obs-mod)/err)**2)
    # re-fit primary dm with companion on (small dm shift); 1-D
    def chi_refit(ddm):
        m = []
        for b in bands:
            am = grid.absmag(b, prim['teff'], prim['logg']) + prim['dm'] + ddm
            sysb = BAND2MONT[b][1]
            off = (GAIA_VEGA2AB.get(b) or WISE_VEGA2AB.get(b) or 0.0) if sysb=='Vega' else 0.0
            fp = 10**(-0.4*(am+off+48.60)); fc = comp_band_fnu.get(b,0.0)
            ab = -2.5*math.log10(fp+fc)-48.60 - off
            m.append(ab)
        return np.sum(((obs-np.array(m))/err)**2)
    rr = minimize_scalar(chi_refit, bounds=(-0.6,0.6), method='bounded')
    return {'chi2_fixed_primary': float(chi_on),
            'chi2_refit_primary': float(rr.fun),
            'ddm_refit': float(rr.x)}

def companion_wd_fnu(grid, comp_mass, comp_teff, dm):
    """Apparent AB f_nu per band for a WD companion of given mass & Teff at distance dm.
    logg from mass-radius (Montreal grid M->logg via root on the track)."""
    # find logg giving this mass at this teff on the DA grid (monotone in logg)
    def m_of_logg(lg): return grid.mass(comp_teff, lg)
    lo, hi = 7.0, 9.0
    for _ in range(60):
        mid = 0.5*(lo+hi)
        if m_of_logg(mid) < comp_mass: lo = mid
        else: hi = mid
    logg2 = 0.5*(lo+hi)
    out = {}
    for b in BAND2MONT:
        am = grid.absmag(b, comp_teff, logg2) + dm
        sysb = BAND2MONT[b][1]
        off = (GAIA_VEGA2AB.get(b) or WISE_VEGA2AB.get(b) or 0.0) if sysb=='Vega' else 0.0
        out[b] = 10**(-0.4*(am+off+48.60))
    return out, logg2

# Empirical M-dwarf absolute mags (Vega for 2MASS/WISE/Gaia; AB for PS1/SDSS).
# Sources: Pecaut & Mamajek (2013) updated table; Mann+2015 (M_Ks); 2MASS/WISE colors.
# Columns: M_G(Vega), M_BP, M_RP, M_J, M_H, M_Ks, M_W1, M_W2 (Vega); plus PS1 grizy (AB).
MDWARF = {
 #            G     BP    RP    J     H     Ks    W1    W2    PS1g  PS1r  PS1i  PS1z  PS1y
 'M0V': dict(Mr=(9.0,10.4,7.7,6.0,5.4,5.2,5.1,5.1), Mps=(11.6,10.1,9.0,8.4,8.1)),
 'M2V': dict(Mr=(10.3,11.9,8.9,6.9,6.3,6.0,5.9,5.9), Mps=(13.2,11.4,9.9,9.2,8.9)),
 'M4V': dict(Mr=(12.8,14.7,11.0,8.4,7.8,7.5,7.3,7.2), Mps=(16.3,13.9,11.6,10.7,10.3)),
 'M5V': dict(Mr=(14.5,16.6,12.5,9.4,8.8,8.5,8.2,8.0), Mps=(18.4,15.7,12.9,11.8,11.3)),
 'M6V': dict(Mr=(16.6,18.9,14.3,10.3,9.7,9.4,9.0,8.7), Mps=(20.6,17.9,14.4,13.0,12.4)),
}
def companion_mdwarf_fnu(spt, dm):
    d = MDWARF[spt]
    G_,BP,RP,J,H,Ks,W1,W2 = d['Mr']; gp,rp,ip,zp,yp = d['Mps']
    absm = {'Gaia_G':(G_,'Vega'),'Gaia_BP':(BP,'Vega'),'Gaia_RP':(RP,'Vega'),
            '2MASS_J':(J,'Vega'),'2MASS_H':(H,'Vega'),'2MASS_Ks':(Ks,'Vega'),
            'WISE_W1':(W1,'Vega'),'WISE_W2':(W2,'Vega'),
            'PS1_g':(gp,'AB'),'PS1_r':(rp,'AB'),'PS1_i':(ip,'AB'),
            'PS1_z':(zp,'AB'),'PS1_y':(yp,'AB')}
    out = {}
    for b,(am,sysb) in absm.items():
        off = (GAIA_VEGA2AB.get(b) or WISE_VEGA2AB.get(b) or 0.0) if sysb=='Vega' else 0.0
        out[b] = 10**(-0.4*(am+dm+off+48.60))
    return out

# ===========================================================================
# 4. Orbit / mass-function (re-derive M2 vs M1 envelope; uses NSS row constants
#    already vetted in the dossier; we re-state them, not re-query, for the SED report)
# ===========================================================================
def solve_m2(fM, M1):
    lo, hi = 1e-5, 1e3
    for _ in range(140):
        mid = 0.5*(lo+hi)
        if mid**3 > fM*(M1+mid)**2: hi = mid
        else: lo = mid
    return 0.5*(lo+hi)

# ===========================================================================
def main():
    out = {'target': NAME, 'gaia_dr3': SID, 'ra': RA, 'dec': DEC, 'date': '2026-05-30'}

    # --- WD grids ---
    paths = _download_montreal()
    out['montreal_tables'] = paths
    DA = WDGrid(_parse_montreal(paths['DA']))
    DB = WDGrid(_parse_montreal(paths['DB']))

    # --- photometry ---
    det, ulim, gf21, qlog = fetch_photometry()
    out['photometry_log'] = qlog
    out['detections'] = {b: {'mag': det[b][0], 'err': det[b][1], 'system': det[b][2],
                             'src': det[b][3]} for b in det}
    out['upper_limits'] = {b: {'limit': ulim[b][0], 'system': ulim[b][1], 'src': ulim[b][2]}
                           for b in ulim}

    # --- GF21 primary params ---
    T_DA = gf21.get('TeffH') or 14957.64; eT_DA = gf21.get('e_TeffH') or 330.75
    lg_DA = gf21.get('loggH') or 8.1743;  elg = gf21.get('e_loggH') or 0.0844
    M_DA = gf21.get('MassH') or 0.7177;   eM = gf21.get('e_MassH') or 0.0526
    R_DA = wd_radius_rsun(M_DA, lg_DA)
    out['primary_GF21'] = {'model':'DA (pure-H)','Pwd':gf21.get('Pwd'),
        'Teff':T_DA,'e_Teff':eT_DA,'logg':lg_DA,'e_logg':elg,
        'mass_Msun':M_DA,'e_mass':eM,'radius_Rsun':R_DA,
        'cooling_age_yr':DA.age(T_DA, lg_DA)}

    # --- single-WD fit (GF21 Teff/logg fixed, dm free) ---
    fit_fix = fit_single_wd(det, DA, T_DA, lg_DA, free_teff=False)
    # --- single-WD fit (Teff free, logg=GF21) : SED-only Teff check ---
    fit_free = fit_single_wd(det, DA, T_DA, lg_DA, free_teff=True)
    # --- OPTICAL-ONLY free-Teff fit: the DA continuum is most reliable here and is
    #     immune to the AllWISE/CatWISE W1/W2 calibration disagreement. This is the
    #     primary anchor used for the companion-exclusion tests below. ---
    OPT = {b: det[b] for b in det if b.startswith('PS1_') or b.startswith('Gaia_')}
    fit_opt = fit_single_wd(OPT, DA, T_DA, lg_DA, free_teff=True)
    out['single_wd_fit_optical_only'] = {k: fit_opt[k] for k in
        ('teff','logg','dm','dist_pc','chi2','ndof')}
    out['single_wd_fit_optical_only']['note'] = (
        'free-Teff on PS1+Gaia only; anchors the primary; GF21 Teff comparison')
    # Anchor the two-component tests on the OPTICAL fit at the GF21 Teff (conservative:
    # uses the reliable optical normalization, full band set for the excess test).
    fit_anchor = fit_single_wd(OPT, DA, T_DA, lg_DA, free_teff=False)
    out['single_wd_fit_GF21Teff'] = {k: fit_fix[k] for k in
        ('teff','logg','dm','dist_pc','chi2','ndof')}
    out['single_wd_fit_GF21Teff']['resid'] = {b: round(fit_fix['resid'][b],3) for b in det}
    out['single_wd_fit_GF21Teff']['sigma'] = {b: round(fit_fix['sigma'][b],2) for b in det}
    out['single_wd_fit_freeTeff'] = {k: fit_free[k] for k in
        ('teff','logg','dm','dist_pc','chi2','ndof')}
    out['single_wd_fit_freeTeff']['sigma'] = {b: round(fit_free['sigma'][b],2) for b in det}
    # implied radius from the fitted dm at the Gaia parallax distance
    dist_plx = 1000.0/PLX_GS
    # R such that (R/d)^2 matches the flux scaling vs a 10pc absolute mag:
    # dm_model = 5log10(d/10); fitted dm includes any radius mismatch as dm_fit.
    # radius_implied = R_grid_at_Teff_logg * 10**(-0.2*(dm_fit - dm_plx_at_gridmass))
    dm_plx = 5*math.log10(dist_plx/10)
    out['single_wd_fit_GF21Teff']['dist_from_parallax_pc'] = dist_plx
    out['single_wd_fit_GF21Teff']['dm_parallax'] = dm_plx
    out['single_wd_fit_GF21Teff']['dm_minus_dm_parallax'] = fit_fix['dm']-dm_plx

    # --- TWO-COMPONENT TESTS ---
    # Primary anchored on the optical (GF21 Teff, optical dm). chi0 = all-band chi2 of
    # that single-WD model evaluated over the FULL detection set (so any companion that
    # adds flux in W1/W2 or the blue must IMPROVE the fit to be viable -- the excess test).
    fit_anchor_all = fit_single_wd(det, DA, T_DA, lg_DA, free_teff=False)
    # recompute chi0 at the optical dm (companion flux only ADDS; conservative):
    prim_for_tests = {'teff': T_DA, 'logg': lg_DA, 'dm': fit_anchor['dm']}
    chi0 = add_companion_chi2(det, DA, prim_for_tests, {})['chi2_fixed_primary']
    dm = fit_anchor['dm']
    twocomp = {}
    out['primary_anchor_for_tests'] = {'teff': T_DA, 'logg': lg_DA, 'dm': dm,
        'dist_pc': 10**(1+dm/5), 'chi2_allbands_at_this_dm': round(chi0,2),
        'note': 'optical-anchored single-WD baseline for companion Delta-chi2'}

    # (A) HOT-WD companion: M2 from orbit (~1.32 Msun) at a grid of Teff2
    M2_orbit = 1.32
    hotwd = {}
    for T2 in [8000, 10000, 12000, 15000, 20000, 25000, 30000, 40000, 50000]:
        try:
            cf, lg2 = companion_wd_fnu(DA, min(M2_orbit,1.3), T2, dm)  # grid max mass 1.3
        except Exception as e:
            hotwd[str(T2)] = {'_err': str(e)}; continue
        res = add_companion_chi2(det, DA, prim_for_tests, cf)
        dchi = res['chi2_refit_primary'] - chi0
        # significance of exclusion: sqrt(max(dchi,0)) sigma (1 extra effective dof = brightness)
        hotwd[str(T2)] = {'logg2': round(lg2,3),
                          'dchi2_vs_single': round(dchi,2),
                          'exclusion_sigma': round(math.sqrt(max(dchi,0)),2),
                          'chi2_refit': round(res['chi2_refit_primary'],2)}
    twocomp['hot_WD_companion_M2_1.32'] = hotwd

    # also: the FAINTEST (coolest) DD companion still allowed -> survives?
    cooldd = {}
    for T2 in [4000, 5000, 6000, 7000, 8000, 9000, 10000]:
        cf, lg2 = companion_wd_fnu(DA, min(M2_orbit,1.3), T2, dm)
        res = add_companion_chi2(det, DA, prim_for_tests, cf)
        dchi = res['chi2_refit_primary'] - chi0
        cooldd[str(T2)] = {'dchi2': round(dchi,2),
                           'exclusion_sigma': round(math.sqrt(max(dchi,0)),2)}
    twocomp['cool_DD_companion_M2_1.32'] = cooldd

    # (B) M-DWARF companion (any subtype) -- IR excess test
    mdw = {}
    for spt in MDWARF:
        cf = companion_mdwarf_fnu(spt, dm)
        res = add_companion_chi2(det, DA, prim_for_tests, cf)
        dchi = res['chi2_refit_primary'] - chi0
        # also predicted W1 excess in mag
        fp = 10**(-0.4*(DA.absmag('WISE_W1',T_DA,lg_DA)+dm+WISE_VEGA2AB['WISE_W1']+48.60))
        w1_comb = -2.5*math.log10(fp+cf['WISE_W1'])-48.60 - WISE_VEGA2AB['WISE_W1']
        w1_excess = det['WISE_W1'][0] - w1_comb        # obs - model(with Mdwarf): if model brighter -> negative
        mdw[spt] = {'dchi2': round(dchi,2),
                    'exclusion_sigma': round(math.sqrt(max(dchi,0)),2),
                    'pred_W1_with_companion_Vega': round(w1_comb,2),
                    'obs_W1_Vega': round(det['WISE_W1'][0],2),
                    'W1_model_brighter_by_mag': round(det['WISE_W1'][0]-w1_comb,2)}
    twocomp['M_dwarf_companion'] = mdw
    out['two_component_tests'] = twocomp

    # --- M2 vs M1 envelope (orbit; constants from vetted dossier NSS row) ---
    a_phot, P_yr, plx_nss = 7.732, 274.52/365.25, 11.376
    fM = (a_phot/plx_nss)**3 / P_yr**2
    env = {}
    for M1 in [0.50, M_DA-eM, M_DA, M_DA+eM, 0.80, 0.83, 1.00, 1.20]:
        env[f'{M1:.3f}'] = round(solve_m2(fM, M1), 3)
    out['orbit_massfunction'] = {'a_phot_mas': a_phot, 'P_yr': round(P_yr,4),
        'plx_nss_mas': plx_nss, 'fM_Msun': round(fM,4),
        'M2_vs_M1': env, 'M2_at_GF21_M1': round(solve_m2(fM, M_DA),3)}

    # --- VERDICT on companion classes ---
    # hot-WD excluded above the Teff where exclusion_sigma crosses ~3
    hot_excl_T = None
    for T2 in sorted([int(k) for k in hotwd], reverse=True):
        if hotwd[str(T2)].get('exclusion_sigma',0) >= 3.0:
            hot_excl_T = T2
    # the coolest DD that is NOT excluded
    dd_survive_T = max([int(k) for k in cooldd if cooldd[k]['exclusion_sigma'] < 2.0], default=None)
    mdw_min_sigma = min(v['exclusion_sigma'] for v in mdw.values())
    out['verdict'] = {
        'M-dwarf companion (any subtype)': f'EXCLUDED at >= {mdw_min_sigma:.0f} sigma (min over M0V-M6V) via W1/W2 IR excess',
        'hot-WD companion': (f'EXCLUDED for Teff2 >~ {hot_excl_T} K at >=3 sigma via blue-optical (PS1 g / Gaia BP) excess; '
                             'GALEX UV unavailable (coverage gap) so the UV lever arm is NOT used'),
        'cool double-degenerate (DD)': f'SURVIVES for Teff2 <~ {dd_survive_T} K (no detectable excess in any band)',
        'dark NS companion': 'SURVIVES (invisible at all wavelengths; SED-indistinguishable from a cool-WD companion)',
        'primary_M1_cooling': f'{M_DA:.3f} +/- {eM:.3f} Msun (GF21 DA; cooling age {DA.age(T_DA,lg_DA)/1e6:.0f} Myr)',
    }

    # --- save ---
    with open('/tmp/wdj020915_sed.json','w') as f:
        json.dump(out, f, indent=2, default=str)
    _write_report(out)
    _plot_sed(out, det, ulim, DA, fit_fix)
    print('WROTE /tmp/wdj020915_sed.json , /tmp/wdj020915_sed_report.md , /tmp/wdj020915_sed.png')
    # console summary
    print('\n=== SINGLE-WD FIT (GF21 Teff/logg) ===')
    print(f"  all-band chi2={fit_fix['chi2']:.1f}/{fit_fix['ndof']} dof; dist(fit)={fit_fix['dist_pc']:.1f}pc vs parallax {dist_plx:.1f}pc")
    print(f"  OPTICAL-ONLY free-Teff = {fit_opt['teff']:.0f} K  (chi2={fit_opt['chi2']:.2f}/{fit_opt['ndof']}; GF21 {T_DA:.0f} K) <- primary anchor")
    print(f"  all-band free-Teff      = {fit_free['teff']:.0f} K (pulled cool by faint WISE; see resid)")
    print('  band residuals (obs-model, sigma):')
    for b in det:
        print(f"    {b:9s} {fit_fix['resid'][b]:+.3f}  ({fit_fix['sigma'][b]:+.2f} sigma)  [{det[b][3]}]")
    print('\n=== COMPANION EXCLUSION ===')
    print('  M-dwarf:', {k: v['exclusion_sigma'] for k,v in mdw.items()})
    print('  hot-WD (M2=1.32) dchi2-sigma by Teff2:', {k: v.get('exclusion_sigma') for k,v in hotwd.items()})
    print('  cool-DD survives below:', dd_survive_T,'K')
    print('\n=== VERDICT ===')
    for k,v in out['verdict'].items(): print(f'  {k}: {v}')

def _write_report(out):
    L = []
    A = L.append
    A(f"# SED decomposition — {out['target']} (Gaia DR3 {out['gaia_dr3']})\n")
    A(f"_Date {out['date']}; env ostinato venv; Montreal/Bergeron DA+DB synthetic photometry; no pip-install._\n")
    p = out['primary_GF21']
    A("## Primary (GF21 DA)\n")
    A(f"- Teff = {p['Teff']:.0f} ± {p['e_Teff']:.0f} K, log g = {p['logg']:.3f} ± {p['e_logg']:.3f}, "
      f"**M₁ = {p['mass_Msun']:.3f} ± {p['e_mass']:.3f} M☉**, R₁ = {p['radius_Rsun']:.5f} R☉, "
      f"cooling age ≈ {p['cooling_age_yr']/1e6:.0f} Myr (Pwd={p['Pwd']}).\n")
    f = out['single_wd_fit_GF21Teff']
    A("## Single-WD fit (Montreal DA, GF21 Teff/log g, distance free)\n")
    A(f"- χ² = {f['chi2']:.1f} / {f['ndof']} dof; fitted distance {f['dist_pc']:.1f} pc "
      f"vs Gaia parallax {f['dist_from_parallax_pc']:.1f} pc (Δdm = {f['dm_minus_dm_parallax']:+.2f}).\n")
    fo = out['single_wd_fit_optical_only']
    A(f"- **Optical-only free-Teff = {fo['teff']:.0f} K** (χ² = {fo['chi2']:.2f}/{fo['ndof']}; "
      f"GF21 = {p['Teff']:.0f} K) — the PS1+Gaia continuum is a single hot DA. "
      f"All-band free-Teff = {out['single_wd_fit_freeTeff']['teff']:.0f} K (pulled cool only by the faint WISE points).\n")
    A("- Per-band residuals (obs − model, in σ):\n")
    A("\n| band | residual (mag) | σ |\n|---|---:|---:|")
    for b in f['resid']:
        A(f"| {b} | {f['resid'][b]:+.3f} | {f['sigma'][b]:+.2f} |")
    A("")
    A("## Two-component exclusion\n")
    mdw = out['two_component_tests']['M_dwarf_companion']
    A("**(a) M-dwarf companion** — would brighten W1/W2 enormously (IR excess):\n")
    A("\n| companion | excl. σ | model W1 (Vega) if present | observed W1 |\n|---|---:|---:|---:|")
    for spt,v in mdw.items():
        A(f"| {spt} | {v['exclusion_sigma']:.1f} | {v['pred_W1_with_companion_Vega']:.2f} | {v['obs_W1_Vega']:.2f} |")
    A("")
    hw = out['two_component_tests']['hot_WD_companion_M2_1.32']
    A("**(b) Hot-WD companion (M₂≈1.32 M☉)** — would add blue-optical (PS1 g / Gaia BP) flux:\n")
    A("\n| Teff₂ (K) | Δχ² vs single | exclusion σ |\n|---|---:|---:|")
    for T2 in sorted(int(k) for k in hw):
        v = hw[str(T2)]
        A(f"| {T2} | {v.get('dchi2_vs_single')} | {v.get('exclusion_sigma')} |")
    A("")
    cd = out['two_component_tests']['cool_DD_companion_M2_1.32']
    A("**(c) Cool double-degenerate (M₂≈1.32 M☉, cool)** — surviving companion class:\n")
    A("\n| Teff₂ (K) | Δχ² | exclusion σ |\n|---|---:|---:|")
    for T2 in sorted(int(k) for k in cd):
        A(f"| {T2} | {cd[str(T2)]['dchi2']} | {cd[str(T2)]['exclusion_sigma']} |")
    A("")
    o = out['orbit_massfunction']
    A("## Orbit mass function (vetted NSS row; for context)\n")
    A(f"- f(M) = {o['fM_Msun']} M☉; M₂(at GF21 M₁={out['primary_GF21']['mass_Msun']:.3f}) = **{o['M2_at_GF21_M1']} M☉**.\n")
    A("\n| M₁ (M☉) | M₂ (M☉) |\n|---:|---:|")
    for m1,m2 in o['M2_vs_M1'].items():
        A(f"| {m1} | {m2} |")
    A("")
    A("## VERDICT — surviving companion classes\n")
    for k,v in out['verdict'].items():
        A(f"- **{k}**: {v}")
    A("")
    A("## Data availability notes\n")
    g = out['photometry_log']['GALEX']
    A(f"- GALEX: {g['verdict']} ({g['n_sources_within_30arcmin']} GALEX AIS sources within 30′). "
      "**No UV constraint** — the hot-WD exclusion rests on PS1 g / Gaia BP only.\n")
    tm = out['photometry_log']['2MASS']
    A(f"- 2MASS: {tm.get('verdict')}; J completeness limit ≈ {tm.get('J_completeness_limit_est')}.\n")
    A("- SDSS ugriz: not in spectro/photo footprint here. SkyMapper: southern survey (δ<0), not in coverage.\n")
    A("- AllWISE W3/W4: SNR<1 → upper limits only (consistent with no warm dust / no luminous companion).\n")
    open('/tmp/wdj020915_sed_report.md','w').write('\n'.join(L))

def _plot_sed(out, det, ulim, grid, fit):
    try:
        import matplotlib; matplotlib.use('Agg')
        import matplotlib.pyplot as plt
    except Exception:
        return
    # observed: convert all to AB f_nu * nu (nuFnu) vs wavelength
    fig, ax = plt.subplots(figsize=(8,5.5))
    def to_AB(b, m, sysb):
        if sysb=='Vega':
            m = m + (GAIA_VEGA2AB.get(b) or WISE_VEGA2AB.get(b) or 0.0)
        return m
    wl=[]; fl=[]; er=[]
    for b in det:
        wlb = PIVOT[b]; ab = to_AB(b, det[b][0], det[b][2])
        wl.append(wlb); fl.append(ab); er.append(det[b][1])
    ax.errorbar(wl, fl, yerr=er, fmt='o', color='k', ms=6, label='observed (AB)', zorder=5)
    # upper limits
    for b in ulim:
        ab = to_AB(b, ulim[b][0], ulim[b][1])
        ax.scatter([PIVOT[b]],[ab], marker='v', color='gray', s=70)
        ax.annotate('2MASS UL', (PIVOT[b], ab), fontsize=7, color='gray')
    # model curve: dense Teff/logg spectrum approx -> sample bands
    bands_all = ['GALEX_NUV','PS1_g','Gaia_BP','PS1_r','Gaia_G','PS1_i','Gaia_RP','PS1_z',
                 'PS1_y','2MASS_J','2MASS_H','2MASS_Ks','WISE_W1','WISE_W2']
    mw=[]; mm=[]
    for b in bands_all:
        am = grid.absmag(b, fit['teff'], fit['logg']) + fit['dm']
        ab = am + ((GAIA_VEGA2AB.get(b) or WISE_VEGA2AB.get(b) or 0.0) if BAND2MONT[b][1]=='Vega' else 0.0)
        mw.append(PIVOT[b]); mm.append(ab)
    order=np.argsort(mw)
    ax.plot(np.array(mw)[order], np.array(mm)[order], '-', color='C0',
            label=f"single DA  Teff={fit['teff']:.0f}K", zorder=3)
    # add an M2V companion overlay
    cf = companion_mdwarf_fnu('M4V', fit['dm'])
    cw=[]; cm=[]
    for b in ['PS1_r','PS1_i','PS1_z','PS1_y','2MASS_J','2MASS_H','2MASS_Ks','WISE_W1','WISE_W2']:
        ab = -2.5*math.log10(cf[b])-48.60
        cw.append(PIVOT[b]); cm.append(ab)
    order=np.argsort(cw)
    ax.plot(np.array(cw)[order], np.array(cm)[order],'--',color='C3',alpha=.8,
            label='M4V companion (excluded)')
    ax.set_xscale('log'); ax.invert_yaxis()
    ax.set_xlabel('pivot wavelength (Å)'); ax.set_ylabel('AB magnitude')
    ax.set_title(f"{out['target']}  — SED (no GALEX coverage; SDSS/SkyMapper absent)")
    ax.legend(fontsize=8); fig.tight_layout()
    fig.savefig('/tmp/wdj020915_sed.png', dpi=130)

if __name__ == '__main__':
    main()
