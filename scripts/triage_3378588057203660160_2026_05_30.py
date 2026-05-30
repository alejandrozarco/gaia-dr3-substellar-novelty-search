#!/usr/bin/env python3
"""Single-source second-method archival-RV triage of Gaia DR3 3378588057203660160.

Reuses scripts/ns_pool_triage_2026_05_28.py for all heavy lifting:
  - fetch_nss_orbits  (P, e, T0=t_periastron, Thiele-Innes, significance)
  - census_archival_rv (LAMOST LRS V/164, LAMOST MRS V/162, APOGEE DR17 III/286,
                        RAVE DR6 III/283, GALAH DR3 J/MNRAS/506/150)
  - t_periastron_to_mjd, fit_nss_locked, K1_kms, fM_from_K1, fM_astrom

Differences from the pool driver (per the task spec):
  - >=1 km/s error floor on the RV epochs (pool used 0.1 km/s).
  - DISTINCT phase counting collapses clustered same-MJD epochs to ONE phase
    (an MRS visit emits up to 2 sub-exposure RVs at the same MJD; LRS/MRS on the
    same night cluster too).  We count distinct phases on de-duplicated epoch
    *times*, binning |dphase| < 0.02 (and same-night |dMJD| < 0.3 d) as one phase.
  - Result printed as JSON to stdout for the workflow to parse.
"""
from __future__ import annotations

import json
import math
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path('/Users/legbatterij/claude_projects/gaia-recovered-2026-05-27/scripts')))
import ns_pool_triage_2026_05_28 as P  # noqa: E402

SID = 3378588057203660160
PROJECT_ROOT = Path('/Users/legbatterij/claude_projects/gaia-recovered-2026-05-27')
PARQUET = PROJECT_ROOT / 'data/derived/main_hunt_derived_v2_M1corrected.parquet'
RV_ERR_FLOOR_KMS = 1.0


def fit_nss_locked_floor(epochs, P_d, e, T0_mjd, err_floor=RV_ERR_FLOOR_KMS):
    """Identical to P.fit_nss_locked but with a configurable error floor.

    We replicate the body so we can set the >=1 km/s floor without mutating the
    shared module.  (The only line that differs from P.fit_nss_locked is the
    np.maximum floor.)
    """
    from scipy.optimize import least_squares

    t = np.array([ep[0] for ep in epochs], dtype=float)
    rv = np.array([ep[1] for ep in epochs], dtype=float)
    err = np.array([ep[2] if (ep[2] and ep[2] > 0) else err_floor for ep in epochs], dtype=float)
    err = np.maximum(err, err_floor)  # >=1 km/s floor (task spec)
    n = len(t)
    dof = max(n - 3, 1)

    rv_mean = float(np.mean(rv))
    rv_span = float(np.ptp(rv)) if n > 1 else 0.0

    def resid(params):
        K1, gamma, omega = params
        return (P.kepler_rv_curve(t, P_d, e, T0_mjd, K1, gamma, omega) - rv) / err

    bounds = ([0.0, rv_mean - 150.0, -math.pi], [250.0, rv_mean + 150.0, math.pi])
    best = None
    for om0 in np.linspace(-math.pi, math.pi, 9, endpoint=False):
        for K0 in (max(rv_span / 2.0, 5.0), 20.0, 50.0):
            try:
                res = least_squares(resid, x0=[K0, rv_mean, om0], bounds=bounds, max_nfev=400)
                chi2 = float(np.sum(res.fun ** 2))
                if best is None or chi2 < best['chi2']:
                    best = {'x': res.x, 'chi2': chi2, 'jac': res.jac}
            except Exception:
                continue
    if best is None:
        return {'error': 'fit failed'}

    K1, gamma, omega = best['x']
    chi2 = best['chi2']
    sigma_K1 = float('nan')
    try:
        cov = np.linalg.inv(best['jac'].T @ best['jac'])
        sigma_K1 = float(np.sqrt(abs(cov[0, 0])))
    except Exception:
        pass

    w = 1.0 / err ** 2
    gamma_const = float(np.sum(w * rv) / np.sum(w))
    chi2_const = float(np.sum(((rv - gamma_const) / err) ** 2))
    dof_const = max(n - 1, 1)
    try:
        from scipy.stats import chi2 as chi2dist
        p_const = float(chi2dist.sf(chi2_const, dof_const))
    except Exception:
        p_const = float('nan')

    K1_signif = (K1 / sigma_K1) if (sigma_K1 and np.isfinite(sigma_K1) and sigma_K1 > 0) else float('nan')
    return {
        'K1_kms': float(K1), 'sigma_K1_kms': sigma_K1, 'K1_signif_sigma': K1_signif,
        'gamma_kms': float(gamma), 'omega_rad': float(omega),
        'chi2': chi2, 'dof': int(dof), 'chi2_dof': chi2 / dof, 'n_epochs': int(n),
        'chi2_const_null': chi2_const, 'dof_const_null': int(dof_const), 'p_const_null': p_const,
        'fM_rv_msun': P.fM_from_K1(K1, P_d, e), 'rv_span_kms': rv_span,
        'err_floor_kms': err_floor,
    }


def distinct_phases(all_eps, P_d, T0_mjd):
    """Count DISTINCT orbital phases, collapsing clustered same-MJD epochs to one.

    all_eps : list of (MJD, RV, err, archive).
    Returns (n_distinct, list_of_(phase, mjd, rv_mean, archive), dedup_eps_for_fit).
    Clustering rule: two epochs are the SAME phase if |dMJD| < 0.3 d OR the
    fractional phase difference (mod 1) < 0.02.  Within a cluster we error-weight
    average the RVs and keep the min MJD.
    """
    if T0_mjd is None or not P_d or P_d <= 0:
        return 0, [], []
    # Sort by MJD.
    eps = sorted(all_eps, key=lambda x: x[0])
    # First collapse exact / near-exact same-MJD (same visit, e.g. MRS RVbr0/RVbr1).
    clusters = []  # each: list of (mjd, rv, err, arch)
    for ep in eps:
        placed = False
        ph = ((ep[0] - T0_mjd) % P_d) / P_d
        for cl in clusters:
            cph = ((cl[0][0] - T0_mjd) % P_d) / P_d
            dph = abs(ph - cph)
            dph = min(dph, 1.0 - dph)  # circular
            if abs(ep[0] - cl[0][0]) < 0.3 or dph < 0.02:
                cl.append(ep)
                placed = True
                break
        if not placed:
            clusters.append([ep])
    dedup = []
    detail = []
    for cl in clusters:
        mjds = np.array([c[0] for c in cl])
        rvs = np.array([c[1] for c in cl])
        errs = np.array([c[2] if (c[2] and c[2] > 0) else RV_ERR_FLOOR_KMS for c in cl])
        errs = np.maximum(errs, RV_ERR_FLOOR_KMS)
        w = 1.0 / errs ** 2
        rv_w = float(np.sum(w * rvs) / np.sum(w))
        err_w = float(np.sqrt(1.0 / np.sum(w)))  # combined error of the weighted mean
        mjd0 = float(mjds.min())
        ph = ((mjd0 - T0_mjd) % P_d) / P_d
        archs = sorted(set(c[3] for c in cl))
        dedup.append((mjd0, rv_w, err_w))
        detail.append({'phase': round(ph, 4), 'mjd': mjd0, 'rv_kms': rv_w,
                       'err_kms': err_w, 'n_sub': len(cl), 'archives': archs,
                       'rv_members': [round(c[1], 3) for c in cl]})
    detail.sort(key=lambda d: d['phase'])
    return len(clusters), detail, dedup


def main():
    # --- derived-pool parameters (M1, M2, e, P already vetted in v2 pipeline) ---
    df = pd.read_parquet(PARQUET)
    row = df[df['source_id'] == SID].iloc[0]
    ra, dec = float(row['ra']), float(row['dec'])
    P_d = float(row['P_d'])
    e = float(row['e_v2'])
    M1 = float(row['M1_used'])
    M2 = float(row['M2_msun_v2_corrected'])
    fphot_pool = float(row['fM_msun_v2'])
    sig = float(row['significance'])
    ruwe = float(row['ruwe'])
    G = float(row['G'])

    print(f'[src] {SID}  ra={ra:.6f} dec={dec:.6f}  P={P_d:.3f}d e={e:.4f}', flush=True)
    print(f'[src] M1={M1:.3f} M2={M2:.3f} fphot_pool={fphot_pool:.4f} sig={sig:.1f} ruwe={ruwe:.2f} G={G:.2f}', flush=True)

    # --- Gaia NSS orbit (authoritative P, e, t_periastron, significance) ---
    nss_map = P.fetch_nss_orbits([SID])
    nss = nss_map.get(SID, {})
    print('[nss]', json.dumps(nss, default=str)[:600], flush=True)

    # Prefer the NSS-table P, e for the locked fit (task: "NSS-locked").
    P_nss = nss.get('period') if nss.get('period') else P_d
    e_nss = nss.get('eccentricity') if nss.get('eccentricity') is not None else e
    T0_mjd = P.t_periastron_to_mjd(nss.get('t_periastron'))
    print(f'[nss] using P={P_nss} e={e_nss} T0_mjd={T0_mjd} (t_peri={nss.get("t_periastron")})', flush=True)

    # --- archival RV census (5 arcsec cone) ---
    census = P.census_archival_rv(ra, dec, radius_arcsec=5.0, timeout_s=90)
    for arch, a in census.items():
        if isinstance(a, dict) and 'n_epochs' in a:
            print(f'[rv] {arch}: n_epochs={a.get("n_epochs")} with_mjd={a.get("n_epochs_with_mjd")} '
                  f'span={a.get("rv_span")} note={a.get("note","")}', flush=True)
        else:
            print(f'[rv] {arch}: {a}', flush=True)

    # Gather phase-able epochs (MJD present) across archives.
    all_eps = []
    for arch in ('LAMOST_LRS', 'LAMOST_MRS', 'APOGEE_visits', 'RAVE', 'GALAH_DR3'):
        for ep in census.get(arch, {}).get('epochs', []):
            if ep[0] is not None:
                all_eps.append((ep[0], ep[1], ep[2], arch))
    total_any = sum(census.get(a, {}).get('n_epochs', 0)
                    for a in ('LAMOST_LRS', 'LAMOST_MRS', 'APOGEE_visits', 'RAVE', 'GALAH_DR3'))
    n_phaseable_raw = len(all_eps)

    n_distinct, phase_detail, dedup_eps = distinct_phases(all_eps, P_nss, T0_mjd)
    print(f'[phase] total_any={total_any} phaseable_raw={n_phaseable_raw} '
          f'n_distinct_phases={n_distinct}', flush=True)
    for d in phase_detail:
        print(f'   phase={d["phase"]:.4f} mjd={d["mjd"]:.3f} rv={d["rv_kms"]:.3f}+/-{d["err_kms"]:.3f} '
              f'n_sub={d["n_sub"]} archives={d["archives"]} members={d["rv_members"]}', flush=True)

    # Astrometric (edge-on) predictions for the comparison.
    K1_pred = P.K1_kms(P_nss, e_nss, M1, M2, 1.0)
    fphot = P.fM_astrom(P_nss, M1, M2)

    result = {
        'source_id': str(SID), 'ra': ra, 'dec': dec,
        'P_d_pool': P_d, 'P_d_nss': P_nss, 'e_pool': e, 'e_nss': e_nss,
        'M1_used': M1, 'M2_corr': M2, 'significance': sig, 'ruwe': ruwe, 'G': G,
        'nss_solution_type': str(row.get('nss_solution_type')),
        'nss_significance': nss.get('significance'),
        't_periastron_days': nss.get('t_periastron'), 'T0_mjd': T0_mjd,
        'fphot_edgeon_msun': fphot, 'K1_pred_edgeon_kms': K1_pred,
        'total_archival_epochs_any': total_any,
        'n_phaseable_epochs_raw': n_phaseable_raw,
        'n_distinct_phases': n_distinct,
        'phase_detail': phase_detail,
        'rv_span_all_kms': (max(e[1] for e in all_eps) - min(e[1] for e in all_eps)) if all_eps else None,
        'census_summary': {a: {k: v for k, v in census.get(a, {}).items() if k != 'epochs'}
                           for a in census},
    }

    # --- Verdict logic (mirrors P.classify thresholds; >=1 km/s floor) ---
    if total_any == 0:
        ap = census.get('APOGEE_allstar', {})
        result['verdict'] = 'NO_ARCHIVAL_RV'
        result['note'] = 'no archival RV epochs in LAMOST LRS/MRS, APOGEE DR17, RAVE DR6, or GALAH DR3'
        if ap.get('s_HRV_scatter') is not None:
            result['note'] += f"; APOGEE allStar s_HRV scatter={ap['s_HRV_scatter']}"
        print('\n[VERDICT]', result['verdict'], '-', result['note'], flush=True)
        print('JSON_RESULT_START'); print(json.dumps(result, default=str)); print('JSON_RESULT_END')
        return

    if T0_mjd is None or n_distinct < 2 or len(dedup_eps) < 2:
        result['verdict'] = 'INCONCLUSIVE'
        bits = []
        if T0_mjd is None:
            bits.append('no NSS t_periastron (cannot phase)')
        bits.append(f'{total_any} archival epoch(s) -> {n_distinct} DISTINCT phase(s) after collapsing clustered same-MJD epochs')
        if result['rv_span_all_kms'] is not None:
            bits.append(f"raw RV span across epochs = {result['rv_span_all_kms']:.2f} km/s")
        result['note'] = '; '.join(bits) + ' -- too few distinct phases for an NSS-locked fit (1593152 standard)'
        print('\n[VERDICT]', result['verdict'], '-', result['note'], flush=True)
        print('JSON_RESULT_START'); print(json.dumps(result, default=str)); print('JSON_RESULT_END')
        return

    # >=2 distinct phases => NSS-locked fit with >=1 km/s floor.
    fit = fit_nss_locked_floor(dedup_eps, P_nss, e_nss, T0_mjd)
    result['nss_locked_fit'] = fit
    if 'error' in fit:
        result['verdict'] = 'INCONCLUSIVE'
        result['note'] = f"locked fit failed: {fit['error']}"
        print('\n[VERDICT]', result['verdict'], '-', result['note'], flush=True)
        print('JSON_RESULT_START'); print(json.dumps(result, default=str)); print('JSON_RESULT_END')
        return

    K1 = fit['K1_kms']; K1_sig = fit['K1_signif_sigma']
    p_const = fit['p_const_null']; fM_rv = fit['fM_rv_msun']; chi2_dof = fit['chi2_dof']
    fM_ratio = (fM_rv / fphot) if (fphot and fphot > 0) else float('nan')
    result['fM_ratio_rv_over_phot'] = fM_ratio if np.isfinite(fM_ratio) else None
    result['fM_rv_msun'] = fM_rv

    predicted_ptp = 2.0 * K1_pred
    observed_span = result['rv_span_all_kms'] or 0.0
    const_not_rejected = (not np.isfinite(p_const)) or (p_const > 0.05)

    refuted = corroborated = False
    reason = []
    if predicted_ptp > 10.0 and observed_span < 0.25 * predicted_ptp and const_not_rejected and n_distinct >= 3:
        refuted = True
        reason.append(f'orbit predicts ~{predicted_ptp:.1f} km/s peak-to-peak but observed span only '
                      f'{observed_span:.2f} km/s and constant-RV null not rejected (p={p_const:.3f})')
    if np.isfinite(fM_ratio) and np.isfinite(K1_sig) and K1_sig > 3 and fM_ratio > 5.0:
        refuted = True
        reason.append(f'spectroscopic f(M)={fM_rv:.2f} >> astrometric f_phot={fphot:.3f} '
                      f'(ratio {fM_ratio:.1f}) with K1 at {K1_sig:.1f} sigma -> closer/inner binary or SB2')
    if (not refuted) and np.isfinite(p_const) and p_const < 0.01 and np.isfinite(K1_sig) and K1_sig > 3.0 \
            and np.isfinite(fM_ratio) and 0.3 < fM_ratio < 3.0:
        corroborated = True
        reason.append(f'constant-RV null rejected (p={p_const:.2e}), K1={K1:.1f}+/-{fit["sigma_K1_kms"]:.1f} '
                      f'km/s ({K1_sig:.1f}sigma), f(M)_RV={fM_rv:.3f} vs f_phot={fphot:.3f} (ratio {fM_ratio:.2f})')

    if refuted:
        result['verdict'] = 'REFUTED'
    elif corroborated:
        result['verdict'] = 'CORROBORATED'
    else:
        result['verdict'] = 'INCONCLUSIVE'
        if chi2_dof < 1 and fit['dof'] <= 2:
            reason.append(f'chi2/dof={chi2_dof:.3f} with dof={fit["dof"]} is a weak statistic (few epochs)')
        if np.isfinite(K1_sig) and K1_sig <= 3:
            reason.append(f'K1 detected at only {K1_sig:.1f} sigma (<3)')
        if np.isfinite(p_const) and p_const >= 0.01:
            reason.append(f'constant-RV null not strongly rejected (p={p_const:.3f})')
        if not reason:
            reason.append('insufficient evidence to corroborate or refute')
    result['note'] = '; '.join(reason)

    print('\n[VERDICT]', result['verdict'], flush=True)
    print('[fit]', json.dumps(fit, default=str), flush=True)
    print('[cmp] f(M)_RV=%.4f  f_phot=%.4f  ratio=%s  K1_pred_edgeon=%.2f km/s'
          % (fM_rv, fphot, f'{fM_ratio:.2f}' if np.isfinite(fM_ratio) else 'nan', K1_pred), flush=True)
    print('[note]', result['note'], flush=True)
    print('JSON_RESULT_START'); print(json.dumps(result, default=str)); print('JSON_RESULT_END')


if __name__ == '__main__':
    main()
