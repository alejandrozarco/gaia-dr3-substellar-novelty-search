"""Independent re-verification of the 4 surviving HEADLINE compact-object claims
of the Gaia DR3 dormant-companion search (2026-05-28).

Default skepticism: a claim is NOT confirmed until the evidence demands it.
Re-fetches NSS solutions, archival RVs, HGCA/Kervella PMa from scratch; reuses
the EXACT cascade math from scripts/web_tool/app.py (solve_m2, photocentric_a_mas,
K1_kms, _kepler_rv_curve) and the permutation-FAP discipline from the CV re-vet.

Outputs:
  /tmp/survivor_revet_{3155543,hd157033,5406907,5858574}.json
  /tmp/survivor_revet_report.md
"""
from __future__ import annotations
import warnings, json, math
warnings.filterwarnings('ignore')
import numpy as np

from astroquery.gaia import Gaia
from astroquery.vizier import Vizier
from astropy.coordinates import SkyCoord
from astropy import units as u
from scipy.optimize import least_squares
from scipy import stats

# ---------------------------------------------------------------------------
# Reused cascade math (verbatim from scripts/web_tool/app.py)
# ---------------------------------------------------------------------------
def photocentric_a_mas(A, B, F, G):
    if any(v is None for v in (A, B, F, G)): return None
    if any(isinstance(v, float) and math.isnan(v) for v in (A, B, F, G)): return None
    uu = 0.5 * (A*A + B*B + F*F + G*G)
    vv = A*G - B*F
    disc = max(0.0, uu*uu - vv*vv)
    return math.sqrt(uu + math.sqrt(disc))

def solve_m2(fM, M1):
    lo, hi = 1e-4, 1e3
    for _ in range(80):
        mid = 0.5*(lo+hi)
        if mid**3 > fM*(M1+mid)**2: hi = mid
        else: lo = mid
    return 0.5*(lo+hi)

def K1_kms(P_d, e, M1, M2, sini):
    if P_d <= 0 or e >= 1.0 or M1 <= 0 or M2 <= 0: return 0.0
    P_s = P_d*86400.0
    num = (2*math.pi*6.6743e-11/P_s)**(1/3) * (M2*1.989e30)*sini
    den = ((M1+M2)*1.989e30)**(2/3) * math.sqrt(1-e*e)
    return (num/den)/1000.0

def _kepler_rv_curve(t, P, e, T0, K1, gamma, omega):
    M = 2.0*math.pi*(t - T0)/P
    M = np.mod(M + math.pi, 2*math.pi) - math.pi
    E = M + e*np.sin(M)
    for _ in range(60):
        dE = (E - e*np.sin(E) - M)/(1.0 - e*np.cos(E))
        E = E - dE
        if np.max(np.abs(dE)) < 1e-12: break
    nu = 2.0*np.arctan2(np.sqrt(1+e)*np.sin(E/2.0), np.sqrt(1-e)*np.cos(E/2.0))
    return gamma + K1*(np.cos(nu+omega) + e*math.cos(omega))

# spectroscopic mass function from K1 (km/s), P (d), e
def f_spec_msun(K1_kms_val, P_d, e):
    if K1_kms_val <= 0 or P_d <= 0 or e >= 1: return 0.0
    K = K1_kms_val*1000.0
    P = P_d*86400.0
    G = 6.6743e-11
    fM = P*K**3*(1-e*e)**1.5/(2*math.pi*G)
    return fM/1.989e30

# ---------------------------------------------------------------------------
def gaia_nss(sid):
    t = Gaia.launch_job(f'SELECT * FROM gaiadr3.nss_two_body_orbit WHERE source_id={sid}').get_results()
    if len(t) == 0: return None
    def g(c):
        v = t[c][0]
        try:
            fv = float(v)
            return None if math.isnan(fv) else fv
        except (TypeError, ValueError):
            return str(v)
    return {c: g(c) for c in t.colnames if c != 'corr_vec'}

def gaia_source(sid):
    cols = ('source_id, ra, dec, parallax, parallax_error, pmra, pmdec, ruwe, '
            'phot_g_mean_mag, bp_rp, radial_velocity, radial_velocity_error, '
            'rv_amplitude_robust, rv_chisq_pvalue, rv_nb_transits, rv_renormalised_gof, '
            'rv_expected_sig_to_noise, ipd_frac_multi_peak, non_single_star')
    t = Gaia.launch_job(f'SELECT {cols} FROM gaiadr3.gaia_source WHERE source_id={sid}').get_results()
    if len(t) == 0: return None
    def g(c):
        v = t[c][0]
        try:
            fv = float(v); return None if math.isnan(fv) else fv
        except (TypeError, ValueError):
            return str(v)
    return {c: g(c) for c in t.colnames}

def gaia_flame(sid):
    out = {}
    for tab, cols in (('gaiadr3.astrophysical_parameters',
                       'mass_flame, radius_flame, lum_flame, teff_gspphot, logg_gspphot, teff_gspspec, logg_gspspec'),):
        try:
            t = Gaia.launch_job(f'SELECT {cols} FROM {tab} WHERE source_id={sid}').get_results()
            if len(t):
                for c in t.colnames:
                    try:
                        fv = float(t[c][0]); out[c] = None if math.isnan(fv) else fv
                    except (TypeError, ValueError):
                        out[c] = str(t[c][0])
        except Exception as e:
            out['_ap_err'] = type(e).__name__
    return out

# ---------------------------------------------------------------------------
# Archival multi-epoch RV — expanded catalog set per the brief
# (LAMOST LRS V/164/stellar5 + V/156/dr7lrs, LAMOST MRS V/162/dr11sm,
#  APOGEE DR17 III/286, GALAH DR3/DR4, RAVE DR6)
# ---------------------------------------------------------------------------
def archival_rv(ra, dec, radius_arcsec=5.0):
    coord = SkyCoord(ra=ra*u.deg, dec=dec*u.deg, frame='icrs')
    radius = radius_arcsec*u.arcsec
    v = Vizier(columns=['**'], timeout=60); v.ROW_LIMIT = -1
    # (catalog, label, [mjd candidate cols], [rv cand cols], [err cand cols])
    archives = [
        ('V/164/stellar5',  'LAMOST DR5 LRS', ['MJD','ObsDate','JD'], ['RV','HRV','rv'], ['e_RV','e_HRV','rv_err']),
        ('V/156/dr7lrs',    'LAMOST DR7 LRS', ['MJD','JD'], ['RV','HRV','RVZ','rv'], ['e_RV','e_HRV','e_rv']),
        ('V/156/dr7slrs',   'LAMOST DR7 sLRS',['MJD','JD'], ['RV','HRV','rv'], ['e_RV','e_HRV','e_rv']),
        ('V/156/dr7melrs',  'LAMOST DR7 MELRS',['MJD','midmjmst','JD'], ['RV','HRV','rv'], ['e_RV','e_HRV','e_rv']),
        ('V/162/dr11sm',    'LAMOST DR11 MRS',['MJD','mmjd','MJM','JD'], ['RV','RVZ','rv','rv_lasp'], ['e_RV','e_rv']),
        ('III/286/catalog', 'APOGEE DR17',    ['MJD','JD'], ['HRV','Vhelio','RVCOM','VHELIO'], ['e_HRV','VERR','e_RV']),
        ('III/284/allvis',  'APOGEE DR17 vis',['MJD','JD'], ['VHELIO','HRV','Vhelio'], ['VRELERR','VERR']),
        ('III/297/galahdr3','GALAH DR3',      ['mjd','MJD','JD'], ['rv_obst','RV','HRV','rv_galah'], ['e_rv_obst','e_RV']),
        ('III/295/galah4',  'GALAH DR4',      ['mjd','MJD','JD'], ['rv_obst','RV','HRV'], ['e_rv_obst','e_RV']),
        ('III/279/rave_dr6','RAVE DR6',       ['MJD','JD'], ['HRV','RV'], ['e_HRV','eHRV']),
        ('III/283/rave6',   'RAVE DR6 alt',   ['MJD','JD'], ['HRV','RV'], ['eHRV','e_HRV']),
    ]
    result = {}
    for cat, label, mjdc, rvc, errc in archives:
        try:
            tab = v.query_region(coord, radius=radius, catalog=cat)
            if tab is None or len(tab) == 0:
                continue
            t = tab[0]
            avail = {c.lower(): c for c in t.colnames}
            mcol = next((avail[c.lower()] for c in mjdc if c.lower() in avail), None)
            rcol = next((avail[c.lower()] for c in rvc if c.lower() in avail), None)
            ecol = next((avail[c.lower()] for c in errc if c.lower() in avail), None)
            n = len(t)
            if rcol is None:
                result[label] = {'count': int(n), 'note': 'matched but no RV col', 'cols': list(t.colnames)[:25]}
                continue
            epochs = []
            for i in range(n):
                try: rv = float(t[rcol][i])
                except (TypeError, ValueError): continue
                if math.isnan(rv): continue
                mjd = None
                if mcol is not None:
                    try:
                        mjd = float(t[mcol][i])
                        if math.isnan(mjd): mjd = None
                    except (TypeError, ValueError):
                        mjd = None
                err = None
                if ecol is not None:
                    try:
                        err = float(t[ecol][i]); err = None if math.isnan(err) else err
                    except (TypeError, ValueError):
                        err = None
                epochs.append((mjd, rv, err))
            result[label] = {'count': len(epochs), 'epochs': epochs,
                             'mjd_col': mcol, 'rv_col': rcol, 'err_col': ecol}
        except Exception as e:
            result[label] = {'count': 0, 'note': f'skipped ({type(e).__name__})'}
    return result

def query_hgca(ra, dec):
    v = Vizier(columns=['**'], timeout=40)
    try:
        coord = SkyCoord(ra=ra*u.deg, dec=dec*u.deg, frame='icrs')
        res = v.query_region(coord, radius=5*u.arcsec, catalog='J/ApJS/254/42/table1')
        if res is None or len(res) == 0:
            res = v.query_region(coord, radius=5*u.arcsec, catalog='J/ApJS/254/42')
        if res is None or len(res) == 0:
            return 'HGCA: no match within 5"'
        t = res[0]
        out = {}
        for c in t.colnames:
            try:
                fv = float(t[c][0]); out[c] = None if math.isnan(fv) else fv
            except (TypeError, ValueError):
                out[c] = str(t[c][0])
        return out
    except Exception as e:
        return f'HGCA: skipped ({type(e).__name__})'

def query_kervella(ra, dec):
    v = Vizier(columns=['**'], timeout=40)
    try:
        coord = SkyCoord(ra=ra*u.deg, dec=dec*u.deg, frame='icrs')
        res = v.query_region(coord, radius=5*u.arcsec, catalog='J/A+A/657/A7')
        if res is None or len(res) == 0:
            return 'Kervella: no match within 5"'
        t = res[0]
        out = {}
        for c in t.colnames:
            try:
                fv = float(t[c][0]); out[c] = None if math.isnan(fv) else fv
            except (TypeError, ValueError):
                out[c] = str(t[c][0])
        return out
    except Exception as e:
        return f'Kervella: skipped ({type(e).__name__})'

# ---------------------------------------------------------------------------
# Astrometric f(M), M_2 from NSS Thiele-Innes
# ---------------------------------------------------------------------------
def astrometric_M2(nss, M1, plx_override=None):
    A = nss.get('a_thiele_innes'); B = nss.get('b_thiele_innes')
    F = nss.get('f_thiele_innes'); G = nss.get('g_thiele_innes')
    a_mas = photocentric_a_mas(A, B, F, G)
    plx = plx_override if plx_override else nss.get('parallax')
    P = nss.get('period')
    if a_mas is None or not plx or not P:
        return None
    a_AU = a_mas/plx
    P_yr = P/365.25
    fM = a_AU**3/P_yr**2
    M2 = solve_m2(fM, M1)
    return {'a_phot_mas': a_mas, 'a_phot_AU': a_AU, 'P_yr': P_yr,
            'f_phot_msun': fM, 'M2_msun': M2, 'plx_used': plx, 'M1': M1}

# K1, omega from the spectroscopic Thiele-Innes C,H (AstroSpectroSB1 ONLY).
# RV - gamma = C*X + H*Y with X=cos E - e, Y = sqrt(1-e^2) sin E.
# => K1 = sqrt(C^2+H^2)/sqrt(...) ; for the Pourbaix spec-TI convention used in
# Gaia DR3, semi-amplitude K1 = sqrt(C^2 + H^2) (km/s) and omega = atan2(-H, C)
# is recoverable up to the documented convention. We compute K1 from (C,H)
# directly so the orbit is FULLY SPECIFIED with NO free phase parameter.
def k1_omega_from_CH(nss):
    C = nss.get('c_thiele_innes'); H = nss.get('h_thiele_innes')
    if C is None or H is None: return None
    K1 = math.hypot(C, H)
    omega = math.atan2(-H, C)
    return {'C': C, 'H': H, 'K1_CH_kms': K1, 'omega_CH_rad': omega,
            'omega_CH_deg': math.degrees(omega)}

# ---------------------------------------------------------------------------
# Orbital-phase / distinct-bin diagnostics for a set of RV epochs vs NSS orbit
# ---------------------------------------------------------------------------
def phase_of(mjd, nss, t_ref_bjd=2457389.0):
    P = nss['period']
    tperi = t_ref_bjd + nss['t_periastron']
    bjd = mjd + 2400000.5
    return ((bjd - tperi) % P)/P

def distinct_phase_bins(phases, nbins=10, sep=0.08):
    """Count distinct phase bins; two epochs within `sep` in phase (mod 1) are
    the SAME bin. Returns count of well-separated phase clusters."""
    if not phases: return 0
    ph = sorted(p % 1.0 for p in phases)
    clusters = [[ph[0]]]
    for p in ph[1:]:
        if min(abs(p - clusters[-1][-1]), 1 - abs(p - clusters[-1][-1])) > sep:
            clusters.append([p])
        else:
            clusters[-1].append(p)
    # merge wrap-around
    if len(clusters) > 1 and min(abs(clusters[0][0]-clusters[-1][-1]),
                                  1-abs(clusters[0][0]-clusters[-1][-1])) <= sep:
        clusters[0] = clusters[-1] + clusters[0]; clusters.pop()
    return len(clusters)

def nss_locked_fit(epochs, nss, fit_omega=True):
    """Fit K1,gamma,(omega) with P,e,T0 LOCKED to NSS. Returns K1, its sigma
    (from the covariance), chi2/dof, and the constant-RV null comparison.

    If fit_omega=False AND C,H present, omega+K1 are taken from spectroscopic
    TI (fully locked) and only gamma is a free offset."""
    ev = [(m, r, e) for (m, r, e) in epochs if m is not None]
    if len(ev) < 2:
        return {'error': f'<2 dated epochs ({len(ev)})'}
    t = np.array([e[0] for e in ev], float)
    rv = np.array([e[1] for e in ev], float)
    err = np.array([e[2] if e[2] and e[2] > 0 else 5.0 for e in ev], float)
    err = np.maximum(err, 0.3)
    P = nss['period']; e_orb = nss['eccentricity']
    T0 = nss['t_periastron'] + 2457389.0 - 2400000.5  # back to MJD frame
    gamma0 = nss.get('center_of_mass_velocity') or float(np.mean(rv))

    n_phase = distinct_phase_bins([phase_of(m, nss) for m in t])

    out = {'n_epochs': len(ev), 'n_distinct_phase_bins': n_phase,
           'phases': [round(phase_of(m, nss), 4) for m in t],
           'rv_span_kms': float(np.ptp(rv))}

    # ---- constant-RV null ----
    w = 1.0/err**2
    gamma_const = float(np.sum(w*rv)/np.sum(w))
    chi2_const = float(np.sum(((rv - gamma_const)/err)**2))
    dof_const = max(len(ev) - 1, 1)
    out['constant_null'] = {'gamma': gamma_const, 'chi2': chi2_const,
                            'dof': dof_const, 'chi2_dof': chi2_const/dof_const,
                            'p_value': float(stats.chi2.sf(chi2_const, dof_const))}

    # ---- free-omega NSS-locked Keplerian (K1, gamma, omega) ----
    def resid_free(params):
        K1, gamma, omega = params
        return (_kepler_rv_curve(t, P, e_orb, T0, K1, gamma, omega) - rv)/err
    x0 = [max(np.ptp(rv)/2, 3.0), gamma0, 0.0]
    res = least_squares(resid_free, x0=x0,
                        bounds=([0.0, gamma0-80, -math.pi],[150.0, gamma0+80, math.pi]),
                        max_nfev=4000)
    K1f, gammaf, omegaf = res.x
    chi2f = float(np.sum(res.fun**2))
    npar_free = 3
    dof_free = len(ev) - npar_free
    # K1 sigma from Jacobian covariance
    K1_sig = None
    try:
        J = res.jac
        cov = np.linalg.inv(J.T @ J)
        s2 = chi2f/max(dof_free, 1) if dof_free > 0 else 1.0
        K1_sig = float(math.sqrt(abs(cov[0, 0]) * max(s2, 1.0)))
    except Exception:
        K1_sig = None
    out['free_omega_fit'] = {
        'K1_kms': float(K1f), 'K1_sigma_kms': K1_sig,
        'K1_significance_sigma': (float(K1f/K1_sig) if K1_sig and K1_sig > 0 else None),
        'gamma_kms': float(gammaf), 'omega_deg': math.degrees(omegaf),
        'chi2': chi2f, 'n_free_params': npar_free, 'dof': dof_free,
        'chi2_dof': (chi2f/dof_free if dof_free > 0 else None),
        'dof_note': ('UNDERCONSTRAINED: dof<=0, chi2 is meaningless'
                     if dof_free <= 0 else 'ok'),
    }

    # ---- FULLY-LOCKED test using spectroscopic TI (C,H) if available ----
    ch = k1_omega_from_CH(nss)
    if ch is not None:
        # Only gamma is free; K1 and omega come from C,H. This is the genuinely
        # independent test: the NSS already fixed the phase + amplitude.
        K1_lock = ch['K1_CH_kms']; omega_lock = ch['omega_CH_rad']
        best = None
        for rot in (0.0, math.pi/2, math.pi, 3*math.pi/2):
            om = omega_lock + rot
            def resid_lock(params, om=om):
                gamma = params[0]
                return (_kepler_rv_curve(t, P, e_orb, T0, K1_lock, gamma, om) - rv)/err
            r2 = least_squares(resid_lock, x0=[gamma0],
                               bounds=([gamma0-80],[gamma0+80]), max_nfev=2000)
            c2 = float(np.sum(r2.fun**2))
            if best is None or c2 < best['chi2']:
                best = {'rotation_deg': math.degrees(rot), 'omega_deg': math.degrees(om),
                        'gamma_kms': float(r2.x[0]), 'chi2': c2,
                        'dof': max(len(ev)-1, 1), 'chi2_dof': c2/max(len(ev)-1, 1)}
        out['spectro_TI_locked_fit'] = {**best, 'K1_from_CH_kms': K1_lock,
            'note': ('omega+K1 FIXED from spectroscopic Thiele-Innes C,H; only '
                     'gamma free. This is the real NSS-locked test. The 4 rotations '
                     'probe the documented Pourbaix convention ambiguity.')}
    return out

# ===========================================================================
TARGETS = {
    '3155543': 3155543945892767232,
    '5406907': 5406907085973524224,
    '5858574': 5858574810404752256,
    'hd157033': 4111149395881722496,
}

def m1_consensus(sid, flame, default):
    mf = flame.get('mass_flame')
    if mf and mf > 0.05:
        return mf, 'FLAME'
    return default, 'dossier-prior'

def run_one(key, sid):
    print(f'\n{"="*70}\n=== {key}  (Gaia DR3 {sid}) ===\n{"="*70}')
    rec = {'key': key, 'source_id': sid}
    gs = gaia_source(sid); rec['gaia_source'] = gs
    nss = gaia_nss(sid); rec['nss'] = nss
    flame = gaia_flame(sid); rec['flame'] = flame
    ra = gs['ra']; dec = gs['dec']
    print(f'  RUWE={gs.get("ruwe")}, plx_GS={gs.get("parallax")}, '
          f'rv_ampl_robust={gs.get("rv_amplitude_robust")}, '
          f'rv_chisq_p={gs.get("rv_chisq_pvalue")}, rv_nb={gs.get("rv_nb_transits")}')
    if nss:
        print(f'  NSS type={nss.get("nss_solution_type")}, P={nss.get("period")}, '
              f'e={nss.get("eccentricity")}, sig={nss.get("significance")}, '
              f'gof={nss.get("goodness_of_fit")}, plx_NSS={nss.get("parallax")}')

    # ---- archival RV ----
    print('  querying archival RV epochs ...')
    arv = archival_rv(ra, dec); rec['archival_rv'] = arv
    for lab, d in arv.items():
        if d.get('count', 0) > 0:
            print(f'    {lab}: {d["count"]} epoch(s)  cols(mjd={d.get("mjd_col")},'
                  f'rv={d.get("rv_col")},err={d.get("err_col")})  -> {d.get("epochs")}')

    # ---- astrometric M2 ----
    M1, M1src = m1_consensus(sid, flame, {'3155543': 1.4, '5406907': 0.85,
                                          '5858574': 1.5, 'hd157033': 1.6}[key])
    rec['M1_adopted'] = M1; rec['M1_source'] = M1src
    if nss and nss.get('a_thiele_innes') is not None:
        am = astrometric_M2(nss, M1)
        rec['astrometric'] = am
        if am:
            print(f'  ASTROMETRIC: a_phot={am["a_phot_mas"]:.3f} mas, '
                  f'f_phot={am["f_phot_msun"]:.3f} Msun, M2={am["M2_msun"]:.2f} Msun '
                  f'(M1={M1:.2f} {M1src})')

    # ---- HGCA + Kervella (for HD157033 especially) ----
    if key == 'hd157033':
        rec['hgca'] = query_hgca(ra, dec)
        rec['kervella'] = query_kervella(ra, dec)
        print('  HGCA:', (rec['hgca'] if isinstance(rec['hgca'], str) else
                          {k: rec['hgca'].get(k) for k in list(rec['hgca'])[:12]}))
        print('  KERVELLA:', (rec['kervella'] if isinstance(rec['kervella'], str) else
                              {k: rec['kervella'].get(k) for k in rec['kervella']
                               if 'PMa' in k or 'snr' in k.lower() or 'M2' in k or 'Mass' in k}))

    # ---- assemble all dated RV epochs from all archives ----
    all_ep = []
    for lab, d in arv.items():
        for ep in d.get('epochs', []):
            all_ep.append(ep)
    rec['n_archival_rv_epochs_total'] = len([e for e in all_ep if e[1] is not None])
    rec['n_dated_rv_epochs'] = len([e for e in all_ep if e[0] is not None])

    # ---- NSS-locked Keplerian + phase diagnostics ----
    if nss and nss.get('period') and nss.get('eccentricity') is not None and len(
            [e for e in all_ep if e[0] is not None]) >= 2:
        fit = nss_locked_fit(all_ep, nss)
        rec['nss_locked_fit'] = fit
        print('  NSS-LOCKED FIT:', json.dumps(fit, indent=1, default=str)[:1400])

    # ---- spectroscopic f(M) vs astrometric f(M) ----
    if nss and gs.get('rv_amplitude_robust'):
        K1_robust = gs['rv_amplitude_robust']/2.0
        fsp = f_spec_msun(K1_robust, nss['period'], nss['eccentricity'] or 0.0)
        rec['f_spec_from_rvampl'] = {'K1_robust_kms': K1_robust, 'f_spec_msun': fsp}
        if rec.get('astrometric'):
            print(f'  f_spec(rvampl/2={K1_robust:.1f})={fsp:.3f} vs '
                  f'f_phot={rec["astrometric"]["f_phot_msun"]:.3f} Msun')
    return rec

def main():
    out = {}
    for key, sid in TARGETS.items():
        try:
            out[key] = run_one(key, sid)
        except Exception as e:
            import traceback; traceback.print_exc()
            out[key] = {'key': key, 'source_id': sid, 'ERROR': f'{type(e).__name__}: {e}'}
        json.dump(out[key], open(f'/tmp/survivor_revet_{key}.json', 'w'), indent=1, default=str)
        print(f'  saved /tmp/survivor_revet_{key}.json')
    json.dump(out, open('/tmp/survivor_revet_all.json', 'w'), indent=1, default=str)
    print('\nDONE. all -> /tmp/survivor_revet_all.json')

if __name__ == '__main__':
    main()
