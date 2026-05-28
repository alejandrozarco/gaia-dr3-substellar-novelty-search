#!/usr/bin/env python3
"""Second-method archival-RV triage of the Tier-1 NS candidate pool (2026-05-28).

Context
-------
The Gaia DR3 dormant-companion search has ~148 surviving Tier-1 NS candidates in
``main_hunt_derived_v2_M1corrected.parquet`` (corrected column ``tier_v2_corrected``
== 'Tier-1 NS').  These are SINGLE-METHOD candidates: their NS classification rests
on the astrometric mass function alone (Thiele-Innes -> a_phot -> f(M) -> M_2).

The job: census ARCHIVAL radial-velocity coverage for each, and where >=2 epochs at
DISTINCT orbital phases exist, run the NSS-locked Keplerian fit (fix P, e, T0 from the
Gaia NSS orbit; fit K1, gamma, omega) to CORROBORATE / REFUTE / mark INCONCLUSIVE.
Default verdict: a candidate STAYS a candidate (NO_ARCHIVAL_RV) unless evidence moves it.

The 1593152 standard
--------------------
chi2/dof << 1 on 1-2 epochs is NOT a confirmation (3 free params will always fit a
handful of points).  CORROBORATED requires the constant-RV null be rejected AND a
K1 detection with the spectroscopic f(M) agreeing with the astrometric f_phot.
A single noisy epoch carrying the whole amplitude => at best MARGINAL, here folded
into INCONCLUSIVE (we are not minting new confirmations, only triaging).

Archival catalogs (Vizier handles VERIFIED 2026-05-28)
------------------------------------------------------
  LAMOST LRS    V/164/stellar5       MJD, HRV, e_HRV                (1 row = 1 epoch)
  LAMOST MRS    V/162/dr11sm         MJD, RVbr0/RVbr1 + errors      (1 row = 1 visit, <=2 subexp)
  APOGEE DR17   III/286/allvis       JD, VHelio, e_RV               (1 row = 1 visit)
  APOGEE DR17   III/286/catalog      HRV, s_HRV (scatter), Nvis     (combined; scatter = variability proxy)
  RAVE DR6      III/283/ravedr6      HRV, e_HRV, Obs.date           (mostly 1 epoch)
  GALAH DR3     J/MNRAS/506/150/rv   RVobst, e_RVobst, HJD/MJDlocal (mostly 1 epoch)

NOTE: must query Vizier with columns=['**'] — the default ['*'] HIDES the MJD/error
columns for the LAMOST tables (this is why an earlier census missed epochs).
GALAH DR4 is not on Vizier (only DR2/DR3); RAVE handle is III/283 (not /rave6).

Outputs
-------
  /tmp/ns_pool_triage_results.json  (per-source, written incrementally)
  /tmp/ns_pool_triage_report.md
"""
from __future__ import annotations

import json
import math
import os
import sys
import time
import warnings
from pathlib import Path

import numpy as np
import pandas as pd

warnings.filterwarnings('ignore')

PROJECT_ROOT = Path('/Users/legbatterij/claude_projects/gaia-recovered-2026-05-27')
PARQUET = PROJECT_ROOT / 'data/derived/main_hunt_derived_v2_M1corrected.parquet'
RELAXED = PROJECT_ROOT / 'data/derived/main_hunt_derived_v2_relaxed_M1corrected.parquet'
ALT = PROJECT_ROOT / 'data/derived/main_hunt_derived_v2_alt_M1corrected.parquet'
RESULTS_JSON = Path('/tmp/ns_pool_triage_results.json')
REPORT_MD = Path('/tmp/ns_pool_triage_report.md')

# Gaia DR3 NSS reference epoch for t_periastron: J2016.0 = JD 2457389.0
GAIA_REF_JD = 2457389.0
MJD_OFFSET = 2400000.5  # JD = MJD + 2400000.5

# ---------------------------------------------------------------------------
# Keplerian machinery (mirrors scripts/web_tool/app.py _kepler_rv_curve / K1_kms)
# ---------------------------------------------------------------------------

def kepler_rv_curve(t, P, e, T0, K1, gamma, omega):
    """Keplerian RV at times t (days).  RV = gamma + K1*(cos(nu+omega)+e*cos(omega))."""
    t = np.asarray(t, dtype=float)
    M = 2.0 * math.pi * (t - T0) / P
    M = np.mod(M + math.pi, 2 * math.pi) - math.pi
    E = M + e * np.sin(M)
    for _ in range(60):
        dE = (E - e * np.sin(E) - M) / (1.0 - e * np.cos(E))
        E = E - dE
        if np.max(np.abs(dE)) < 1e-11:
            break
    nu = 2.0 * np.arctan2(np.sqrt(1.0 + e) * np.sin(E / 2.0),
                          np.sqrt(1.0 - e) * np.cos(E / 2.0))
    return gamma + K1 * (np.cos(nu + omega) + e * math.cos(omega))


def K1_kms(P_d, e, M1, M2, sini):
    """RV semi-amplitude K_1 [km/s] (consumer.K1_kms)."""
    if P_d <= 0 or e >= 1.0 or M1 <= 0 or M2 <= 0:
        return 0.0
    P_s = P_d * 86400.0
    num = (2 * math.pi * 6.6743e-11 / P_s) ** (1 / 3) * (M2 * 1.989e30) * sini
    den = ((M1 + M2) * 1.989e30) ** (2 / 3) * math.sqrt(1 - e * e)
    return (num / den) / 1000.0


def fM_from_K1(K1, P_d, e):
    """Spectroscopic mass function f(M) = P K1^3 (1-e^2)^{3/2} / (2 pi G) in Msun."""
    if K1 <= 0 or P_d <= 0 or e >= 1.0:
        return 0.0
    P_s = P_d * 86400.0
    K = K1 * 1000.0
    G = 6.6743e-11
    fM_kg = P_s * K ** 3 * (1 - e * e) ** 1.5 / (2 * math.pi * G)
    return fM_kg / 1.989e30


def fM_astrom(P_d, M1, M2):
    """Astrometric/photometric mass function f_phot = M2^3 sin^3 i /(M1+M2)^2.

    For the astrometric NS solutions the canonical comparison quantity is the
    edge-on (sin i = 1) mass function implied by (M1, M2):  M2^3/(M1+M2)^2.
    """
    if M1 <= 0 or M2 <= 0:
        return 0.0
    return M2 ** 3 / (M1 + M2) ** 2


# ---------------------------------------------------------------------------
# NSS-locked Keplerian fit:  P, e, T0 FIXED;  free = K1, gamma, omega.
# ---------------------------------------------------------------------------

def fit_nss_locked(epochs, P_d, e, T0_mjd):
    """Fix P,e,T0 from the Gaia NSS orbit; fit (K1, gamma, omega) by LSQ.

    epochs : list of (MJD, RV_kms, err_kms).
    Returns dict with K1, sigma_K1, gamma, omega, chi2, dof, chi2_dof,
    constant-null chi2/p, and the K1 detection significance.
    """
    from scipy.optimize import least_squares

    t = np.array([ep[0] for ep in epochs], dtype=float)
    rv = np.array([ep[1] for ep in epochs], dtype=float)
    err = np.array([ep[2] if (ep[2] and ep[2] > 0) else 1.0 for ep in epochs], dtype=float)
    err = np.maximum(err, 0.1)  # 100 m/s floor
    n = len(t)
    n_free = 3
    dof = max(n - n_free, 1)

    rv_mean = float(np.mean(rv))
    rv_span = float(np.ptp(rv)) if n > 1 else 0.0

    def resid(params):
        K1, gamma, omega = params
        return (kepler_rv_curve(t, P_d, e, T0_mjd, K1, gamma, omega) - rv) / err

    x0 = [max(rv_span / 2.0, 5.0), rv_mean, 0.0]
    bounds = ([0.0, rv_mean - 150.0, -math.pi],
              [250.0, rv_mean + 150.0, math.pi])
    best = None
    # Multi-start over omega to escape the K-omega degeneracy local minima.
    for om0 in np.linspace(-math.pi, math.pi, 9, endpoint=False):
        for K0 in (max(rv_span / 2.0, 5.0), 20.0, 50.0):
            try:
                res = least_squares(resid, x0=[K0, rv_mean, om0], bounds=bounds,
                                    max_nfev=400)
                chi2 = float(np.sum(res.fun ** 2))
                if best is None or chi2 < best['chi2']:
                    best = {'x': res.x, 'chi2': chi2, 'jac': res.jac}
            except Exception:
                continue
    if best is None:
        return {'error': 'fit failed'}

    K1, gamma, omega = best['x']
    chi2 = best['chi2']

    # Parameter covariance from the Jacobian (Gauss-Newton approx).
    sigma_K1 = float('nan')
    try:
        J = best['jac']
        JTJ = J.T @ J
        cov = np.linalg.inv(JTJ)
        sigma_K1 = float(np.sqrt(abs(cov[0, 0])))
    except Exception:
        pass

    # Constant-RV (no-orbit) null: chi2 about the error-weighted mean.
    w = 1.0 / err ** 2
    gamma_const = float(np.sum(w * rv) / np.sum(w))
    chi2_const = float(np.sum(((rv - gamma_const) / err) ** 2))
    dof_const = max(n - 1, 1)
    # p-value of the constant null via survival function of chi2.
    try:
        from scipy.stats import chi2 as chi2dist
        p_const = float(chi2dist.sf(chi2_const, dof_const))
    except Exception:
        p_const = float('nan')

    K1_signif = (K1 / sigma_K1) if (sigma_K1 and np.isfinite(sigma_K1) and sigma_K1 > 0) else float('nan')

    return {
        'K1_kms': float(K1),
        'sigma_K1_kms': sigma_K1,
        'K1_signif_sigma': K1_signif,
        'gamma_kms': float(gamma),
        'omega_rad': float(omega),
        'chi2': chi2,
        'dof': int(dof),
        'chi2_dof': chi2 / dof,
        'n_epochs': int(n),
        'chi2_const_null': chi2_const,
        'dof_const_null': int(dof_const),
        'p_const_null': p_const,
        'fM_rv_msun': fM_from_K1(K1, P_d, e),
        'rv_span_kms': rv_span,
    }


# ---------------------------------------------------------------------------
# Gaia NSS fetch (Thiele-Innes + t_periastron) — one async ADQL per chunk.
# ---------------------------------------------------------------------------

def fetch_nss_orbits(source_ids):
    """Fetch t_periastron, A/B/F/G, period, ecc, ruwe, mass_flame for a list of ids.

    Returns {source_id: {...}}.  Chunks the ADQL (200 ids/query).
    """
    from astroquery.gaia import Gaia
    out = {}
    ids = [int(s) for s in source_ids]
    for i in range(0, len(ids), 200):
        chunk = ids[i:i + 200]
        idlist = ','.join(str(s) for s in chunk)
        adql = f"""
        SELECT g.source_id, g.ruwe, g.phot_g_mean_mag,
               n.nss_solution_type, n.period, n.eccentricity, n.t_periastron,
               n.a_thiele_innes, n.b_thiele_innes, n.f_thiele_innes, n.g_thiele_innes,
               n.significance,
               ap.mass_flame, ap.teff_gspphot, ap.logg_gspphot
        FROM gaiadr3.gaia_source AS g
        LEFT JOIN gaiadr3.nss_two_body_orbit AS n USING (source_id)
        LEFT JOIN gaiadr3.astrophysical_parameters AS ap USING (source_id)
        WHERE g.source_id IN ({idlist})
        """
        for attempt in range(3):
            try:
                job = Gaia.launch_job_async(adql)
                tbl = job.get_results()
                for r in tbl:
                    sid = int(r['source_id'])
                    out[sid] = {c: (None if (hasattr(r[c], 'mask') and r[c] is np.ma.masked)
                                    else (float(r[c]) if isinstance(r[c], (int, float, np.floating, np.integer))
                                          else str(r[c])))
                                for c in tbl.colnames}
                break
            except Exception as exc:
                print(f'  [Gaia] chunk {i} attempt {attempt} failed: {type(exc).__name__}: {str(exc)[:120]}',
                      flush=True)
                time.sleep(5)
        print(f'  [Gaia] fetched {len(out)}/{len(ids)} NSS orbits', flush=True)
    return out


def t_periastron_to_mjd(t_peri_days):
    """Gaia DR3 NSS t_periastron is in days relative to J2016.0 (JD 2457389.0)."""
    if t_peri_days is None or (isinstance(t_peri_days, float) and math.isnan(t_peri_days)):
        return None
    jd = GAIA_REF_JD + float(t_peri_days)
    return jd - MJD_OFFSET


# ---------------------------------------------------------------------------
# Archival RV census — Vizier cone search, columns=['**'] is ESSENTIAL.
# ---------------------------------------------------------------------------

def _to_float(x):
    try:
        if x is None:
            return None
        if hasattr(x, 'mask') and x is np.ma.masked:
            return None
        v = float(x)
        if math.isnan(v):
            return None
        return v
    except (TypeError, ValueError):
        return None


def census_archival_rv(ra, dec, radius_arcsec=5.0, timeout_s=60):
    """Cone-search the archival-RV catalogs.  Returns per-archive epochs+meta.

    epochs are (MJD_or_None, RV_kms, err_kms).  We keep epochs even when MJD is
    missing (for variability via the catalog's own RV scatter), but only epochs
    WITH an MJD can be phase-folded into the NSS-locked fit.
    """
    from astroquery.vizier import Vizier
    from astropy.coordinates import SkyCoord
    from astropy import units as u

    coord = SkyCoord(ra=float(ra) * u.deg, dec=float(dec) * u.deg, frame='icrs')
    radius = radius_arcsec * u.arcsec
    v = Vizier(columns=['**'], timeout=timeout_s)
    v.ROW_LIMIT = -1
    res = {}

    def cone(cat):
        for attempt in range(2):
            try:
                return v.query_region(coord, radius=radius, catalog=cat)
            except Exception as exc:
                if attempt == 1:
                    return f'ERR:{type(exc).__name__}'
                time.sleep(3)
        return None

    # --- LAMOST LRS V/164/stellar5: 1 row = 1 epoch -----------------------
    r = cone('V/164/stellar5')
    if isinstance(r, str):
        res['LAMOST_LRS'] = {'note': r, 'n_epochs': 0, 'epochs': []}
    elif r and len(r):
        t = r[0]
        col = {c.lower(): c for c in t.colnames}
        eps = []
        for row in t:
            mjd = _to_float(row[col['mjd']]) if 'mjd' in col else None
            rv = _to_float(row[col['hrv']]) if 'hrv' in col else None
            err = _to_float(row[col['e_hrv']]) if 'e_hrv' in col else None
            if rv is not None:
                eps.append((mjd, rv, err))
        res['LAMOST_LRS'] = _summ(eps)
    else:
        res['LAMOST_LRS'] = {'n_epochs': 0, 'epochs': []}

    # --- LAMOST MRS V/162/dr11sm: 1 row = 1 visit, up to 2 subexposures ----
    r = cone('V/162/dr11sm')
    if isinstance(r, str):
        res['LAMOST_MRS'] = {'note': r, 'n_epochs': 0, 'epochs': []}
    elif r and len(r):
        t = r[0]
        col = {c.lower(): c for c in t.colnames}
        eps = []
        for row in t:
            mjd = _to_float(row[col['mjd']]) if 'mjd' in col else None
            # RVbr0 / RVbr1 are the two combined blue+red sub-exposure RVs.
            for rvc, ec in (('rvbr0', 'e_rvbr0'), ('rvbr1', 'e_rvbr1')):
                rv = _to_float(row[col[rvc]]) if rvc in col else None
                err = _to_float(row[col[ec]]) if ec in col else None
                if rv is not None and abs(rv) < 9000:  # guard sentinel -9999
                    eps.append((mjd, rv, err))
        res['LAMOST_MRS'] = _summ(eps)
    else:
        res['LAMOST_MRS'] = {'n_epochs': 0, 'epochs': []}

    # --- APOGEE DR17 visits III/286/allvis: 1 row = 1 visit ----------------
    r = cone('III/286/allvis')
    if isinstance(r, str):
        res['APOGEE_visits'] = {'note': r, 'n_epochs': 0, 'epochs': []}
    elif r and len(r):
        t = r[0]
        col = {c.lower(): c for c in t.colnames}
        eps = []
        for row in t:
            jd = _to_float(row[col['jd']]) if 'jd' in col else None
            mjd = (jd - MJD_OFFSET) if jd is not None else None
            rv = _to_float(row[col['vhelio']]) if 'vhelio' in col else None
            if rv is None and 'rv' in col:
                rv = _to_float(row[col['rv']])
            err = _to_float(row[col['e_rv']]) if 'e_rv' in col else None
            if rv is not None and abs(rv) < 9000:
                eps.append((mjd, rv, err))
        res['APOGEE_visits'] = _summ(eps)
    else:
        res['APOGEE_visits'] = {'n_epochs': 0, 'epochs': []}

    # --- APOGEE DR17 allStar III/286/catalog: combined HRV + scatter s_HRV --
    r = cone('III/286/catalog')
    if isinstance(r, str):
        res['APOGEE_allstar'] = {'note': r}
    elif r and len(r):
        t = r[0]
        col = {c.lower(): c for c in t.colnames}
        row = t[0]
        res['APOGEE_allstar'] = {
            'HRV': _to_float(row[col['hrv']]) if 'hrv' in col else None,
            's_HRV_scatter': _to_float(row[col['s_hrv']]) if 's_hrv' in col else None,
            'e_HRV': _to_float(row[col['e_hrv']]) if 'e_hrv' in col else None,
            'Nvis': _to_float(row[col['nvis']]) if 'nvis' in col else None,
        }
    else:
        res['APOGEE_allstar'] = {}

    # --- RAVE DR6 III/283/ravedr6 ------------------------------------------
    r = cone('III/283/ravedr6')
    if isinstance(r, str):
        res['RAVE'] = {'note': r, 'n_epochs': 0, 'epochs': []}
    elif r and len(r):
        t = r[0]
        col = {c.lower(): c for c in t.colnames}
        eps = []
        for row in t:
            rv = _to_float(row[col['hrv']]) if 'hrv' in col else None
            err = _to_float(row[col['e_hrv']]) if 'e_hrv' in col else None
            # RAVE has Obs.date (string) and Obs.st (start) — keep MJD None
            # unless a numeric MJD/JD col exists.
            mjd = None
            for k in ('mjd', 'jd', 'obs.st'):
                if k in col:
                    mjd = _to_float(row[col[k]])
                    if mjd is not None:
                        break
            if rv is not None and abs(rv) < 9000:
                eps.append((mjd, rv, err))
        res['RAVE'] = _summ(eps)
    else:
        res['RAVE'] = {'n_epochs': 0, 'epochs': []}

    # --- GALAH DR3 J/MNRAS/506/150/rv --------------------------------------
    r = cone('J/MNRAS/506/150/rv')
    if isinstance(r, str):
        res['GALAH_DR3'] = {'note': r, 'n_epochs': 0, 'epochs': []}
    elif r and len(r):
        t = r[0]
        col = {c.lower(): c for c in t.colnames}
        eps = []
        for row in t:
            rv = None
            for rc in ('rvobst', 'rvgalah'):
                if rc in col:
                    rv = _to_float(row[col[rc]])
                    if rv is not None:
                        break
            err = None
            for ec in ('e_rvobst', 'e_rvgalah'):
                if ec in col:
                    err = _to_float(row[col[ec]])
                    if err is not None:
                        break
            mjd = None
            if 'mjdlocal' in col:
                mjd = _to_float(row[col['mjdlocal']])
            elif 'hjd' in col:
                hjd = _to_float(row[col['hjd']])
                mjd = (hjd - MJD_OFFSET) if hjd is not None else None
            if rv is not None and abs(rv) < 9000:
                eps.append((mjd, rv, err))
        res['GALAH_DR3'] = _summ(eps)
    else:
        res['GALAH_DR3'] = {'n_epochs': 0, 'epochs': []}

    return res


def _summ(epochs):
    """Summarise an archive's epoch list."""
    epochs = [e for e in epochs if e[1] is not None]
    rvs = [e[1] for e in epochs]
    with_mjd = [e for e in epochs if e[0] is not None]
    return {
        'n_epochs': len(epochs),
        'n_epochs_with_mjd': len(with_mjd),
        'epochs': epochs,
        'rv_min': min(rvs) if rvs else None,
        'rv_max': max(rvs) if rvs else None,
        'rv_span': (max(rvs) - min(rvs)) if rvs else None,
    }


# ---------------------------------------------------------------------------
# Per-source triage.
# ---------------------------------------------------------------------------

def classify(src, census, nss):
    """Aggregate epochs across archives, compute distinct phases, run the
    NSS-locked fit if >=2 epochs at distinct phases, and return a verdict."""
    P_d = src['P_d']
    e = src['e_v2']
    T0_mjd = t_periastron_to_mjd(nss.get('t_periastron')) if nss else None

    # Gather all phase-able epochs (MJD present) across archives.
    all_eps = []
    for arch in ('LAMOST_LRS', 'LAMOST_MRS', 'APOGEE_visits', 'RAVE', 'GALAH_DR3'):
        a = census.get(arch, {})
        for ep in a.get('epochs', []):
            if ep[0] is not None:
                all_eps.append((ep[0], ep[1], ep[2], arch))

    total_epochs_any = sum(census.get(a, {}).get('n_epochs', 0)
                           for a in ('LAMOST_LRS', 'LAMOST_MRS', 'APOGEE_visits',
                                     'RAVE', 'GALAH_DR3'))
    n_phaseable = len(all_eps)

    # Distinct orbital phases (bin width 0.05) using P, T0.
    phases = []
    distinct_phase_bins = set()
    if T0_mjd is not None and P_d and P_d > 0:
        for ep in all_eps:
            ph = ((ep[0] - T0_mjd) % P_d) / P_d
            phases.append(round(ph, 4))
            distinct_phase_bins.add(round(ph / 0.05))
    n_distinct_phase = len(distinct_phase_bins)

    out = {
        'total_archival_epochs_any': total_epochs_any,
        'n_phaseable_epochs': n_phaseable,
        'n_distinct_phase_bins': n_distinct_phase,
        'T0_mjd': T0_mjd,
        'phases': phases,
        'rv_span_all_kms': (max(ep[1] for ep in all_eps) - min(ep[1] for ep in all_eps))
                           if all_eps else None,
    }

    # Astrometric prediction for the comparison.
    M1 = src.get('M1_used') or (nss.get('mass_flame') if nss else None) or 1.0
    M2 = src['M2_msun_v2_corrected']
    K1_pred = K1_kms(P_d, e, M1, M2, 1.0)  # edge-on prediction
    fphot = fM_astrom(P_d, M1, M2)
    out['M1_used'] = M1
    out['M2_corr'] = M2
    out['K1_pred_edgeon_kms'] = K1_pred
    out['fphot_msun'] = fphot

    # --- Verdict logic ----------------------------------------------------
    if total_epochs_any == 0:
        out['verdict'] = 'NO_ARCHIVAL_RV'
        out['reason'] = 'no archival RV epochs found in any of LAMOST/APOGEE/RAVE/GALAH'
        # APOGEE allStar scatter as a backstop signal even with 0 visit epochs
        ap = census.get('APOGEE_allstar', {})
        if ap.get('s_HRV_scatter') is not None:
            out['reason'] += f"; APOGEE allStar s_HRV={ap['s_HRV_scatter']}"
        return out

    if n_phaseable < 2 or n_distinct_phase < 2 or T0_mjd is None:
        out['verdict'] = 'INCONCLUSIVE'
        bits = []
        if T0_mjd is None:
            bits.append('no NSS t_periastron (cannot phase)')
        bits.append(f'{n_phaseable} phaseable epoch(s), {n_distinct_phase} distinct phase bin(s)')
        # If multiple epochs exist but cannot be phased, still report RV scatter.
        if total_epochs_any >= 2 and out['rv_span_all_kms'] is not None:
            bits.append(f"RV span across epochs = {out['rv_span_all_kms']:.2f} km/s")
        out['reason'] = '; '.join(bits) + ' — too few distinct phases for a locked fit (1593152 standard)'
        return out

    # >=2 phaseable epochs at >=2 distinct phases => run the NSS-locked fit.
    fit_eps = [(ep[0], ep[1], ep[2]) for ep in all_eps]
    fit = fit_nss_locked(fit_eps, P_d, e, T0_mjd)
    out['nss_locked_fit'] = fit
    if 'error' in fit:
        out['verdict'] = 'INCONCLUSIVE'
        out['reason'] = f"locked fit failed: {fit['error']}"
        return out

    K1 = fit['K1_kms']
    K1_sig = fit['K1_signif_sigma']
    p_const = fit['p_const_null']
    fM_rv = fit['fM_rv_msun']
    chi2_dof = fit['chi2_dof']

    # Agreement of spectroscopic f(M) with astrometric f_phot.
    fM_ratio = (fM_rv / fphot) if (fphot and fphot > 0) else float('nan')

    # REFUTED: orbit predicts a large swing but RV is flat, OR f(M) grossly off.
    # "Large predicted swing" = peak-to-peak 2*K1_pred; flat = const null NOT
    # rejected AND observed span << predicted.
    predicted_ptp = 2.0 * K1_pred
    observed_span = out['rv_span_all_kms'] or 0.0
    const_not_rejected = (not np.isfinite(p_const)) or (p_const > 0.05)

    refuted = False
    corroborated = False
    reason = []

    if predicted_ptp > 10.0 and observed_span < 0.25 * predicted_ptp and const_not_rejected \
            and n_distinct_phase >= 3:
        # Need >=3 distinct phases incl. one near a predicted extremum to be
        # confident the flatness isn't a phase-sampling artefact.
        refuted = True
        reason.append(f'orbit predicts ~{predicted_ptp:.1f} km/s peak-to-peak but observed span only '
                      f'{observed_span:.2f} km/s and constant-RV null not rejected (p={p_const:.3f})')

    # Gross f(M) inconsistency (spectroscopic >> astrometric by >5x with K1 well detected).
    if np.isfinite(fM_ratio) and np.isfinite(K1_sig) and K1_sig > 3 and fM_ratio > 5.0:
        refuted = True
        reason.append(f'spectroscopic f(M)={fM_rv:.2f} >> astrometric f_phot={fphot:.3f} (ratio {fM_ratio:.1f}) with K1 at {K1_sig:.1f} sigma')

    # CORROBORATED: const null rejected, K1 detected >3sigma, f(M) agrees within ~1sigma-ish.
    if (not refuted) and np.isfinite(p_const) and p_const < 0.01 \
            and np.isfinite(K1_sig) and K1_sig > 3.0 \
            and np.isfinite(fM_ratio) and 0.3 < fM_ratio < 3.0:
        corroborated = True
        reason.append(f'constant-RV null rejected (p={p_const:.2e}), K1={K1:.1f}+/-{fit["sigma_K1_kms"]:.1f} '
                      f'km/s ({K1_sig:.1f}sigma), spectroscopic f(M)={fM_rv:.3f} vs astrometric f_phot={fphot:.3f} '
                      f'(ratio {fM_ratio:.2f})')

    if refuted:
        out['verdict'] = 'REFUTED'
    elif corroborated:
        out['verdict'] = 'CORROBORATED'
    else:
        out['verdict'] = 'INCONCLUSIVE'
        # Explain why it's not a confirmation per the 1593152 standard.
        if chi2_dof < 1 and fit['dof'] <= 2:
            reason.append(f'chi2/dof={chi2_dof:.3f} with dof={fit["dof"]} is a weak statistic (few epochs)')
        if np.isfinite(K1_sig) and K1_sig <= 3:
            reason.append(f'K1 detected at only {K1_sig:.1f} sigma (<3)')
        if np.isfinite(p_const) and p_const >= 0.01:
            reason.append(f'constant-RV null not strongly rejected (p={p_const:.3f})')
        if not reason:
            reason.append('insufficient evidence to corroborate or refute')
    out['reason'] = '; '.join(reason)
    out['fM_ratio_rv_over_phot'] = fM_ratio if np.isfinite(fM_ratio) else None
    return out


# ---------------------------------------------------------------------------
# Driver.
# ---------------------------------------------------------------------------

def load_pool():
    df = pd.read_parquet(PARQUET)
    ns = df[df['tier_v2_corrected'] == 'Tier-1 NS'].copy()
    cols = ['source_id', 'ra', 'dec', 'P_d', 'e_v2', 'M2_msun_v2_corrected',
            'significance', 'ruwe', 'G', 'M1_used', 'fM_msun_v2',
            'nss_solution_type']
    ns = ns[[c for c in cols if c in ns.columns]]
    # Union in the relaxed-pool Tier-1 NS not already present.
    try:
        rdf = pd.read_parquet(RELAXED)
        rcol = 'tier_v2_corrected' if 'tier_v2_corrected' in rdf.columns else 'tier_v2'
        rns = rdf[rdf[rcol] == 'Tier-1 NS'].copy()
        rns = rns[[c for c in cols if c in rns.columns]]
        extra = rns[~rns['source_id'].isin(ns['source_id'])]
        if len(extra):
            ns = pd.concat([ns, extra], ignore_index=True)
            print(f'  + {len(extra)} extra Tier-1 NS from relaxed pool', flush=True)
    except Exception as exc:
        print(f'  relaxed-pool union skipped: {exc}', flush=True)
    # Priority: significance desc, then brightness (G asc).
    ns = ns.sort_values(['significance', 'G'], ascending=[False, True]).reset_index(drop=True)
    return ns


def main():
    limit = int(os.environ.get('NS_LIMIT', '0'))  # 0 = all
    ns = load_pool()
    if limit:
        ns = ns.head(limit)
    print(f'Tier-1 NS pool to triage: {len(ns)} sources', flush=True)

    # Resume support: load any partial results.
    results = {}
    if RESULTS_JSON.exists():
        try:
            results = json.loads(RESULTS_JSON.read_text())
            print(f'  resuming: {len(results)} already done', flush=True)
        except Exception:
            results = {}

    # Fetch NSS orbits (Thiele-Innes + t_periastron) for all in chunks up front.
    need_nss = [int(s) for s in ns['source_id'] if str(int(s)) not in results
                or 'nss' not in results.get(str(int(s)), {})]
    nss_map = {}
    if need_nss:
        print(f'Fetching Gaia NSS orbits for {len(need_nss)} sources...', flush=True)
        nss_map = fetch_nss_orbits(need_nss)

    t_start = time.time()
    for idx, row in ns.iterrows():
        sid = int(row['source_id'])
        skey = str(sid)
        if skey in results and results[skey].get('_complete'):
            continue
        src = {k: (None if pd.isna(row[k]) else (float(row[k]) if k not in ('source_id', 'nss_solution_type')
                                                  else row[k]))
               for k in ns.columns}
        nss = nss_map.get(sid, {})
        try:
            census = census_archival_rv(float(row['ra']), float(row['dec']))
        except Exception as exc:
            census = {'_error': f'{type(exc).__name__}: {str(exc)[:120]}'}
        try:
            cls = classify(src, census, nss) if '_error' not in census else {
                'verdict': 'CENSUS_ERROR', 'reason': census['_error']}
        except Exception as exc:
            cls = {'verdict': 'CLASSIFY_ERROR', 'reason': f'{type(exc).__name__}: {str(exc)[:160]}'}

        results[skey] = {
            'source_id': sid,
            'ra': float(row['ra']), 'dec': float(row['dec']),
            'P_d': float(row['P_d']), 'e_v2': float(row['e_v2']),
            'M2_corr': float(row['M2_msun_v2_corrected']),
            'significance': float(row['significance']),
            'ruwe': float(row['ruwe']) if not pd.isna(row['ruwe']) else None,
            'G': float(row['G']) if 'G' in row and not pd.isna(row['G']) else None,
            'nss_solution_type': row.get('nss_solution_type'),
            'nss_t_periastron': nss.get('t_periastron'),
            'nss_significance': nss.get('significance'),
            'ruwe_flag': (float(row['ruwe']) > 1.4) if not pd.isna(row['ruwe']) else None,
            'low_signif_flag': float(row['significance']) < 20.0,
            'census': census,
            'triage': cls,
            '_complete': True,
        }
        # Incremental write every source (cheap; protects partial progress).
        RESULTS_JSON.write_text(json.dumps(results, indent=1, default=str))
        v = cls.get('verdict', '?')
        n_any = cls.get('total_archival_epochs_any', 0)
        elapsed = time.time() - t_start
        done = sum(1 for r in results.values() if r.get('_complete'))
        print(f'[{done}/{len(ns)}] {sid} sig={row["significance"]:.0f} G={row.get("G", float("nan")):.1f} '
              f'-> {v} (epochs_any={n_any}) [{elapsed:.0f}s]', flush=True)

    write_report(results)
    print(f'\nDONE. {len(results)} sources. Report: {REPORT_MD}', flush=True)


def write_report(results):
    rows = [r for r in results.values() if r.get('_complete')]
    n = len(rows)
    by_verdict = {}
    for r in rows:
        v = r['triage'].get('verdict', '?')
        by_verdict.setdefault(v, []).append(r)

    # Pool-level: how many have ANY archival RV at all.
    any_rv = [r for r in rows if r['triage'].get('total_archival_epochs_any', 0) > 0]
    phaseable2 = [r for r in rows if r['triage'].get('n_phaseable_epochs', 0) >= 2
                  and r['triage'].get('n_distinct_phase_bins', 0) >= 2]

    lines = []
    lines.append('# Tier-1 NS pool — archival-RV second-method triage')
    lines.append(f'\n_2026-05-28. Sources processed: **{n}**._\n')
    lines.append('## Headline')
    lines.append(f'- **{len(any_rv)}/{n}** Tier-1 NS have ANY archival RV second-method data '
                 f'(LAMOST LRS/MRS, APOGEE DR17, RAVE DR6, GALAH DR3).')
    lines.append(f'- **{len(phaseable2)}/{n}** have >=2 epochs at >=2 distinct orbital phases '
                 f'(eligible for an NSS-locked Keplerian fit).')
    lines.append('\n## Verdict distribution')
    for v in ('CORROBORATED', 'REFUTED', 'INCONCLUSIVE', 'NO_ARCHIVAL_RV',
              'CENSUS_ERROR', 'CLASSIFY_ERROR'):
        if v in by_verdict:
            lines.append(f'- {v}: {len(by_verdict[v])}')

    # Archive coverage breakdown.
    cov = {a: 0 for a in ('LAMOST_LRS', 'LAMOST_MRS', 'APOGEE_visits', 'RAVE', 'GALAH_DR3')}
    for r in rows:
        for a in cov:
            if r['census'].get(a, {}).get('n_epochs', 0) > 0:
                cov[a] += 1
    lines.append('\n## Archive coverage (sources with >=1 epoch)')
    for a, c in cov.items():
        lines.append(f'- {a}: {c}')

    # CORROBORATED / REFUTED tables.
    for v in ('CORROBORATED', 'REFUTED'):
        lst = by_verdict.get(v, [])
        lines.append(f'\n## {v} ({len(lst)})')
        if not lst:
            lines.append('- (none)')
            continue
        lines.append('| source_id | P_d | M2 | sig | ruwe | epochs | K1(km/s) | evidence |')
        lines.append('|---|---|---|---|---|---|---|---|')
        for r in lst:
            t = r['triage']
            fit = t.get('nss_locked_fit', {})
            k1 = f"{fit.get('K1_kms', float('nan')):.1f}+/-{fit.get('sigma_K1_kms', float('nan')):.1f}" if fit else '-'
            lines.append(f"| {r['source_id']} | {r['P_d']:.1f} | {r['M2_corr']:.2f} | "
                         f"{r['significance']:.0f} | {r['ruwe']:.1f} | "
                         f"{t.get('n_phaseable_epochs', 0)} | {k1} | {t.get('reason', '')} |")

    # Sources with multi-epoch RV that ended INCONCLUSIVE (most informative for follow-up).
    inc_multi = [r for r in by_verdict.get('INCONCLUSIVE', [])
                 if r['triage'].get('total_archival_epochs_any', 0) >= 2]
    lines.append(f'\n## INCONCLUSIVE with >=2 archival epochs ({len(inc_multi)}) — follow-up priority')
    if inc_multi:
        lines.append('| source_id | P_d | M2 | sig | epochs_any | phaseable | distinct_phase | reason |')
        lines.append('|---|---|---|---|---|---|---|---|')
        for r in sorted(inc_multi, key=lambda x: -x['significance']):
            t = r['triage']
            lines.append(f"| {r['source_id']} | {r['P_d']:.1f} | {r['M2_corr']:.2f} | "
                         f"{r['significance']:.0f} | {t.get('total_archival_epochs_any', 0)} | "
                         f"{t.get('n_phaseable_epochs', 0)} | {t.get('n_distinct_phase_bins', 0)} | "
                         f"{t.get('reason', '')} |")

    # Astrometric-quality flags.
    hi_ruwe = [r for r in rows if r.get('ruwe_flag')]
    lo_sig = [r for r in rows if r.get('low_signif_flag')]
    lines.append(f'\n## Astrometric-quality flags')
    lines.append(f'- ruwe > 1.4: {len(hi_ruwe)}/{n}')
    lines.append(f'- NSS significance < 20: {len(lo_sig)}/{n}')

    REPORT_MD.write_text('\n'.join(lines))


if __name__ == '__main__':
    main()
