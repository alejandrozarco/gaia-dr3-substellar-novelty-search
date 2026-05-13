"""Inclination-marginalized M_2 posterior for NSS Orbital and NSS Acceleration candidates.

The central methodological issue:
- HD 150248 (NSS Accel) appeared substellar at M_2 ~ 62 M_J (sin(i)=1 minimum)
- Barbato 2023 joint Gaia+RV fit revealed i = 56°, true M_2 = 140 M_J (stellar)
- Unger 2023 found 13/32 of their sample (40%) reclassified stellar after inclination resolution

For NSS Orbital sources, the Thiele-Innes (A, B, F, G) elements already encode
inclination through the projected orbit shape. The Campbell transform gives a_phot
(deprojected semi-major axis) and cos(i) directly. However, the T-I parameter
UNCERTAINTIES propagate non-trivially to (a_phot, i), and from those to M_2.

This script:
1. For NSS Orbital: Monte-Carlo propagate T-I uncertainties to get
   M_2 posterior including inclination uncertainty.
2. For NSS Accel: combine the assumed-period-grid M_2 (sin(i)=1 floor) with
   an isotropic inclination prior (P(i) ∝ sin(i)) to get a marginalized posterior.
3. Output P(M_2 < 80 M_J) per source, rank by it, save tables and methodology doc.

Time budget: ~15-25 minutes wall-clock for N=10,000 MC samples per source.
"""

import numpy as np
import polars as pl
import json
import os
from pathlib import Path

N_SAMPLES = 10000
RNG = np.random.default_rng(20260512)
M_JUP_PER_M_SUN = 1047.57
SUBSTELLAR_THRESHOLD_MJUP = 80.0  # H-burning limit

OUT_DIR = Path('data/candidate_dossiers/incl_marginalized_2026_05_12')
OUT_DIR.mkdir(parents=True, exist_ok=True)


def direct_mass_solve_vec(a_phot_au, P_yr, M_host_msun, n_iter=5):
    """Solve M_2/M_sun from a_phot, P, M_host. Vectorized."""
    M_2 = a_phot_au * (M_host_msun ** (2/3)) / (P_yr ** (2/3))
    for _ in range(n_iter):
        M_total = M_host_msun + M_2
        M_2 = a_phot_au * (M_total ** (2/3)) / (P_yr ** (2/3))
    return M_2


def marginalize_nss_orbital(df_orb):
    """For each NSS Orbital source, MC-propagate T-I uncertainty to M_2.

    Returns list of dicts with marginalized stats per source.
    """
    results = []
    n_rows = df_orb.height
    print(f'Marginalizing {n_rows} NSS Orbital sources (N_samp={N_SAMPLES})...')

    A_all = df_orb['a_thiele_innes'].to_numpy()
    B_all = df_orb['b_thiele_innes'].to_numpy()
    F_all = df_orb['f_thiele_innes'].to_numpy()
    G_all = df_orb['g_thiele_innes'].to_numpy()
    A_err_all = df_orb['a_thiele_innes_error'].to_numpy()
    B_err_all = df_orb['b_thiele_innes_error'].to_numpy()
    F_err_all = df_orb['f_thiele_innes_error'].to_numpy()
    G_err_all = df_orb['g_thiele_innes_error'].to_numpy()
    P_d_all = df_orb['period'].to_numpy()
    P_err_all = df_orb['period_error'].to_numpy()
    parallax_all = df_orb['parallax'].to_numpy()
    parallax_err_all = df_orb['parallax_error'].to_numpy()
    M_host_all = df_orb['M_host_msun_used'].to_numpy()
    source_id_all = df_orb['source_id'].to_numpy()

    # vector replace none
    def safe(x, fill=np.nan):
        return np.where(np.isfinite(x), x, fill)

    for i_row in range(n_rows):
        if i_row % 200 == 0 and i_row > 0:
            print(f'  ... {i_row}/{n_rows}')

        A = A_all[i_row]; A_err = A_err_all[i_row] if np.isfinite(A_err_all[i_row]) else abs(A) * 0.3
        B = B_all[i_row]; B_err = B_err_all[i_row] if np.isfinite(B_err_all[i_row]) else abs(B) * 0.3
        F = F_all[i_row]; F_err = F_err_all[i_row] if np.isfinite(F_err_all[i_row]) else abs(F) * 0.3
        G = G_all[i_row]; G_err = G_err_all[i_row] if np.isfinite(G_err_all[i_row]) else abs(G) * 0.3

        # Skip if any T-I element invalid
        if not (np.isfinite(A) and np.isfinite(B) and np.isfinite(F) and np.isfinite(G)):
            results.append(dict(source_id=source_id_all[i_row], i_constraint_quality='INVALID_TI',
                                M_2_median_true=np.nan, M_2_1sigma_lo=np.nan, M_2_1sigma_hi=np.nan,
                                M_2_2sigma_lo=np.nan, M_2_2sigma_hi=np.nan,
                                P_substellar=np.nan, i_median_deg=np.nan, i_1sigma_lo=np.nan, i_1sigma_hi=np.nan,
                                a_phot_au_median=np.nan, a_phot_au_sigma=np.nan,
                                ti_snr_median=np.nan))
            continue

        # MC sample
        A_s = RNG.normal(A, A_err, N_SAMPLES)
        B_s = RNG.normal(B, B_err, N_SAMPLES)
        F_s = RNG.normal(F, F_err, N_SAMPLES)
        G_s = RNG.normal(G, G_err, N_SAMPLES)

        u = (A_s**2 + B_s**2 + F_s**2 + G_s**2) / 2
        v = A_s*G_s - B_s*F_s
        inside = u**2 - v**2
        inside = np.where(inside < 0, 0, inside)
        a_phot_mas = np.sqrt(u + np.sqrt(inside))
        # Avoid div-by-zero
        a_phot_mas = np.where(a_phot_mas > 1e-9, a_phot_mas, 1e-9)
        cos_i_s = v / (a_phot_mas ** 2)
        cos_i_s = np.clip(cos_i_s, -1.0, 1.0)
        i_deg_s = np.degrees(np.arccos(cos_i_s))
        sin_i_s = np.sin(np.radians(i_deg_s))

        # Period sampling
        P_d = P_d_all[i_row]
        P_err = P_err_all[i_row] if np.isfinite(P_err_all[i_row]) else P_d * 0.02
        if not np.isfinite(P_d) or P_d <= 0:
            results.append(dict(source_id=source_id_all[i_row], i_constraint_quality='INVALID_P',
                                M_2_median_true=np.nan, M_2_1sigma_lo=np.nan, M_2_1sigma_hi=np.nan,
                                M_2_2sigma_lo=np.nan, M_2_2sigma_hi=np.nan,
                                P_substellar=np.nan, i_median_deg=np.nan, i_1sigma_lo=np.nan, i_1sigma_hi=np.nan,
                                a_phot_au_median=np.nan, a_phot_au_sigma=np.nan,
                                ti_snr_median=np.nan))
            continue
        P_d_s = RNG.normal(P_d, P_err, N_SAMPLES)
        P_d_s = np.where(P_d_s > 1.0, P_d_s, 1.0)
        P_yr_s = P_d_s / 365.25

        # Parallax sampling
        plx = parallax_all[i_row]
        plx_err = parallax_err_all[i_row] if np.isfinite(parallax_err_all[i_row]) else plx * 0.05
        if not np.isfinite(plx) or plx <= 0:
            plx_s = np.full(N_SAMPLES, np.nan)
        else:
            plx_s = RNG.normal(plx, plx_err, N_SAMPLES)
            plx_s = np.where(plx_s > 1e-3, plx_s, 1e-3)

        # a_phot in AU
        a_phot_au_s = a_phot_mas / plx_s  # mas/mas = AU

        # M_host sampling (small uncertainty assumed: 10%)
        M_host = M_host_all[i_row] if np.isfinite(M_host_all[i_row]) else 1.0
        M_host_s = RNG.normal(M_host, M_host * 0.10, N_SAMPLES)
        M_host_s = np.where(M_host_s > 0.05, M_host_s, 0.05)

        # M_2 (M_sun) — iterative Kepler solver (vectorized)
        M_2_s = direct_mass_solve_vec(a_phot_au_s, P_yr_s, M_host_s)
        M_2_mjup = M_2_s * M_JUP_PER_M_SUN

        # Mask non-finite
        valid = np.isfinite(M_2_mjup) & (M_2_mjup > 0) & (M_2_mjup < 1e6)
        if valid.sum() < 100:
            results.append(dict(source_id=source_id_all[i_row], i_constraint_quality='MC_FAIL',
                                M_2_median_true=np.nan, M_2_1sigma_lo=np.nan, M_2_1sigma_hi=np.nan,
                                M_2_2sigma_lo=np.nan, M_2_2sigma_hi=np.nan,
                                P_substellar=np.nan, i_median_deg=np.nan, i_1sigma_lo=np.nan, i_1sigma_hi=np.nan,
                                a_phot_au_median=np.nan, a_phot_au_sigma=np.nan,
                                ti_snr_median=np.nan))
            continue

        m2_valid = M_2_mjup[valid]
        i_valid = i_deg_s[valid]
        a_valid = a_phot_au_s[valid]

        # T-I S/N (typical magnitude vs uncertainty across A,B,F,G)
        ti_snr_med = np.median([abs(A)/A_err if A_err>0 else 0,
                                abs(B)/B_err if B_err>0 else 0,
                                abs(F)/F_err if F_err>0 else 0,
                                abs(G)/G_err if G_err>0 else 0])

        # i_constraint_quality
        i_sigma = (np.percentile(i_valid, 84) - np.percentile(i_valid, 16)) / 2
        if i_sigma < 5:
            i_qual = 'TIGHT'
        elif i_sigma < 15:
            i_qual = 'MODERATE'
        elif i_sigma < 30:
            i_qual = 'LOOSE'
        else:
            i_qual = 'PRIOR_DOMINATED'

        results.append(dict(
            source_id=int(source_id_all[i_row]),
            i_constraint_quality=i_qual,
            M_2_median_true=float(np.median(m2_valid)),
            M_2_1sigma_lo=float(np.percentile(m2_valid, 16)),
            M_2_1sigma_hi=float(np.percentile(m2_valid, 84)),
            M_2_2sigma_lo=float(np.percentile(m2_valid, 2.5)),
            M_2_2sigma_hi=float(np.percentile(m2_valid, 97.5)),
            P_substellar=float(np.mean(m2_valid < SUBSTELLAR_THRESHOLD_MJUP)),
            i_median_deg=float(np.median(i_valid)),
            i_1sigma_lo=float(np.percentile(i_valid, 16)),
            i_1sigma_hi=float(np.percentile(i_valid, 84)),
            a_phot_au_median=float(np.median(a_valid)),
            a_phot_au_sigma=float(np.std(a_valid)),
            ti_snr_median=float(ti_snr_med),
        ))
    return results


def marginalize_nss_accel(df_acc):
    """For each NSS Accel source, marginalize over inclination prior and assumed P.

    NSS Accel doesn't have an orbital period. The published m2_mjup_P{N}yr columns
    are sin(i)=1 minimum masses assuming P = N years.

    True M_2 = M_2_min / sin(i) where i has isotropic prior P(i) ∝ sin(i)
    The marginalized posterior over isotropic i is:
        f(M_2 | M_2_min) = M_2_min² / M_2³ for M_2 >= M_2_min (when normalized)

    We also marginalize over period uncertainty: combine the P=5,10,25 yr grid with
    P(P) = log-uniform [5, 30] yr.
    """
    print(f'Marginalizing {df_acc.height} NSS Accel sources...')

    M5 = df_acc['m2_mjup_P5yr'].to_numpy()
    M10 = df_acc['m2_mjup_P10yr'].to_numpy()
    M25 = df_acc['m2_mjup_P25yr'].to_numpy()
    source_ids = df_acc['source_id'].to_numpy()
    names = df_acc['Name'].to_list()

    results = []
    for k in range(df_acc.height):
        if k % 500 == 0 and k > 0:
            print(f'  ... {k}/{df_acc.height}')

        m5 = M5[k]; m10 = M10[k]; m25 = M25[k]

        if not (np.isfinite(m5) and np.isfinite(m10) and np.isfinite(m25)):
            results.append(dict(source_id=int(source_ids[k]), Name=names[k],
                                i_constraint_quality='NO_M2_GRID',
                                M_2_median_true=np.nan, M_2_1sigma_lo=np.nan, M_2_1sigma_hi=np.nan,
                                M_2_2sigma_lo=np.nan, M_2_2sigma_hi=np.nan,
                                P_substellar=np.nan, i_median_deg=np.nan, i_1sigma_lo=np.nan, i_1sigma_hi=np.nan,
                                P_assumed_median_yr=np.nan))
            continue

        # Sample log-uniform P in [5, 30] yr (typical Acceleration regime)
        log_P = RNG.uniform(np.log10(5.0), np.log10(30.0), N_SAMPLES)
        P_yr_s = 10**log_P

        # Log-log interpolate M_2_min as function of P (Brandt-style scaling)
        # m2 ~ P^(2/3) for fixed acceleration (a ~ G*M_2/r² and r~P^(2/3))
        # Use the actual grid values to fit the trend
        log_P_grid = np.log10([5.0, 10.0, 25.0])
        log_M_grid = np.log10([m5, m10, m25])
        # Linear fit in log-log
        # Mean slope from the grid
        log_M_at_P = np.interp(log_P, log_P_grid, log_M_grid)
        M_2_min_s = 10**log_M_at_P  # sin(i)=1 minimum

        # Sample inclination from isotropic prior P(i) ∝ sin(i), i ∈ (0, π/2)
        # CDF: 1 - cos(i), so cos(i) ~ Uniform(0, 1), i = arccos(U)
        cos_i_s = RNG.uniform(0.0, 1.0, N_SAMPLES)
        sin_i_s = np.sqrt(1 - cos_i_s**2)
        i_deg_s = np.degrees(np.arccos(cos_i_s))

        # True M_2 = M_2_min / sin(i)
        # But sin(i)=0 (face-on) gives unbounded mass — cap at sin(i) > 0.01 (i > 0.57°)
        sin_i_floor = np.maximum(sin_i_s, 0.01)
        M_2_true_s = M_2_min_s / sin_i_floor

        # Clip extreme values
        valid = np.isfinite(M_2_true_s) & (M_2_true_s < 1e5)
        m2_valid = M_2_true_s[valid]
        i_valid = i_deg_s[valid]
        p_valid = P_yr_s[valid]

        results.append(dict(
            source_id=int(source_ids[k]),
            Name=names[k],
            i_constraint_quality='ISOTROPIC_PRIOR',
            M_2_median_true=float(np.median(m2_valid)),
            M_2_1sigma_lo=float(np.percentile(m2_valid, 16)),
            M_2_1sigma_hi=float(np.percentile(m2_valid, 84)),
            M_2_2sigma_lo=float(np.percentile(m2_valid, 2.5)),
            M_2_2sigma_hi=float(np.percentile(m2_valid, 97.5)),
            P_substellar=float(np.mean(m2_valid < SUBSTELLAR_THRESHOLD_MJUP)),
            i_median_deg=float(np.median(i_valid)),
            i_1sigma_lo=float(np.percentile(i_valid, 16)),
            i_1sigma_hi=float(np.percentile(i_valid, 84)),
            P_assumed_median_yr=float(np.median(p_valid)),
        ))
    return results


def main():
    print('=== Inclination-Marginalized M_2 Posterior Pipeline ===\n')

    # --- NSS ORBITAL (2,678 substellar candidates) ---
    print('Loading NSS Orbital substellar candidates...')
    df_orb = pl.read_csv('data/candidate_dossiers/full_nss_orbital_2026_05_12/substellar_2678_ranked.csv',
                          null_values=['null', 'NaN', ''], infer_schema_length=10000)
    print(f'  rows: {df_orb.height}')

    orb_results = marginalize_nss_orbital(df_orb)
    print(f'NSS Orbital marginalization complete: {len(orb_results)} rows')

    # Merge with input columns
    orb_marg = pl.DataFrame(orb_results)
    # Keep useful identifying columns from original
    keep_cols = ['source_id', 'nss_solution_type', 'period', 'eccentricity',
                 'a_phot_mas', 'sin_i', 'cos_i', 'i_deg', 'a_phot_au',
                 'parallax', 'distance_pc', 'M_host_msun_used',
                 'M_2_mjup_ours', 'phot_g_mean_mag', 'bp_rp',
                 'ruwe', 'significance',
                 'HIP', 'Name', 'Vmag', 'SpType', 'snrPMaH2G2', 'BinH2G2',
                 'tier_a', 'sahl_confirmed', 'hgca_strong', 'priority_score',
                 'in_stefansson', 'astrometric_excess_noise_sig']
    keep_cols = [c for c in keep_cols if c in df_orb.columns]
    orb_keep = df_orb.select(keep_cols)
    orb_keep = orb_keep.with_columns(pl.col('source_id').cast(pl.Int64))
    orb_marg = orb_marg.with_columns(pl.col('source_id').cast(pl.Int64))
    orb_merged = orb_keep.join(orb_marg, on='source_id', how='inner')
    orb_merged = orb_merged.sort('P_substellar', descending=True, nulls_last=True)
    orb_out = OUT_DIR / 'nss_orbital_2678_marginalized.csv'
    orb_merged.write_csv(orb_out)
    print(f'Saved {orb_out}')

    # --- NSS ACCELERATION (6,825 priority candidates) ---
    print('\nLoading NSS Accel priority candidates...')
    df_acc = pl.read_csv('data/candidate_dossiers/nss_acceleration_deep_mining_2026_05_12/nss_accel_master_inventory.csv',
                          null_values=['null', 'NaN', ''], infer_schema_length=10000)
    print(f'  rows: {df_acc.height}')

    acc_results = marginalize_nss_accel(df_acc)
    print(f'NSS Accel marginalization complete: {len(acc_results)} rows')

    acc_marg = pl.DataFrame(acc_results)
    keep_cols_acc = ['source_id', 'HIP_hgca', 'Name', 'V_combined', 'G_combined', 'SpType_combined',
                     'RUWE_combined', 'parallax', 'distance_pc', 'accel_mag_recompute', 'accel_mag_snr',
                     'significance', 'nss_solution_type', 'm2_mjup_P5yr', 'm2_mjup_P10yr', 'm2_mjup_P25yr',
                     'M1', 'snrPMaH2EG3a', 'dVt', 'M23au', 'M25au', 'M210au', 'M230au',
                     'tokovinin_known_multiple', 'penoyre_match', 'has_apogee', 'has_harps',
                     'hgca_pma_strong', 'hgca_pma_very_strong', 'tier_S_score_final', 'roi_score', 'substellar_rank_score']
    keep_cols_acc = [c for c in keep_cols_acc if c in df_acc.columns]
    acc_keep = df_acc.select(keep_cols_acc)
    acc_keep = acc_keep.with_columns(pl.col('source_id').cast(pl.Int64))
    acc_marg = acc_marg.with_columns(pl.col('source_id').cast(pl.Int64))
    # Drop duplicate Name col before join
    acc_marg2 = acc_marg.drop('Name') if 'Name' in acc_marg.columns else acc_marg
    acc_merged = acc_keep.join(acc_marg2, on='source_id', how='inner')
    acc_merged = acc_merged.sort('P_substellar', descending=True, nulls_last=True)
    acc_out = OUT_DIR / 'nss_accel_6825_marginalized.csv'
    acc_merged.write_csv(acc_out)
    print(f'Saved {acc_out}')

    # --- VALIDATION on benchmark targets ---
    print('\n=== Validation on benchmark targets ===')
    for name in ['HD 5433', 'HD 89707', 'HD 128717', 'HD 150248']:
        row_orb = orb_merged.filter(pl.col('Name') == name) if 'Name' in orb_merged.columns else None
        row_acc = acc_merged.filter(pl.col('Name') == name) if 'Name' in acc_merged.columns else None
        print(f'\n{name}:')
        if row_orb is not None and row_orb.height > 0:
            r = row_orb.row(0, named=True)
            print(f'  [NSS Orbital]  M_2 median = {r.get("M_2_median_true", np.nan):.1f} M_J')
            print(f'                1σ: [{r.get("M_2_1sigma_lo", np.nan):.1f}, {r.get("M_2_1sigma_hi", np.nan):.1f}]')
            print(f'                2σ: [{r.get("M_2_2sigma_lo", np.nan):.1f}, {r.get("M_2_2sigma_hi", np.nan):.1f}]')
            print(f'                P(<80 M_J) = {r.get("P_substellar", np.nan):.3f}')
            print(f'                i median = {r.get("i_median_deg", np.nan):.1f} deg ({r.get("i_constraint_quality", "?")})')
        if row_acc is not None and row_acc.height > 0:
            r = row_acc.row(0, named=True)
            print(f'  [NSS Accel]   M_2 median = {r.get("M_2_median_true", np.nan):.1f} M_J')
            print(f'                1σ: [{r.get("M_2_1sigma_lo", np.nan):.1f}, {r.get("M_2_1sigma_hi", np.nan):.1f}]')
            print(f'                2σ: [{r.get("M_2_2sigma_lo", np.nan):.1f}, {r.get("M_2_2sigma_hi", np.nan):.1f}]')
            print(f'                P(<80 M_J) = {r.get("P_substellar", np.nan):.3f}')

    # --- TOP 20 NEW candidates after re-ranking ---
    top20 = orb_merged.filter(pl.col('P_substellar') > 0).head(20)
    top20_acc = acc_merged.filter(pl.col('P_substellar') > 0).head(20)

    # Write top-20 summary CSV
    top20_combined_cols = ['source_id', 'Name', 'HIP', 'Vmag', 'SpType', 'period', 'i_median_deg',
                            'M_2_median_true', 'M_2_1sigma_lo', 'M_2_1sigma_hi', 'P_substellar',
                            'i_constraint_quality', 'tier_a', 'priority_score']
    avail = [c for c in top20_combined_cols if c in top20.columns]
    top20.select(avail).write_csv(OUT_DIR / 'top20_nss_orbital_marginalized.csv')

    top20_acc_cols = ['source_id', 'Name', 'HIP_hgca', 'V_combined', 'SpType_combined', 'P_assumed_median_yr',
                      'i_median_deg', 'M_2_median_true', 'M_2_1sigma_lo', 'M_2_1sigma_hi',
                      'P_substellar', 'i_constraint_quality', 'tier_S_score_final', 'substellar_rank_score']
    avail_acc = [c for c in top20_acc_cols if c in top20_acc.columns]
    top20_acc.select(avail_acc).write_csv(OUT_DIR / 'top20_nss_accel_marginalized.csv')

    # --- Summary stats ---
    summary = dict(
        n_orbital_total=orb_merged.height,
        n_orbital_valid=orb_merged.filter(pl.col('P_substellar').is_not_null()).height,
        n_orbital_high_psub=orb_merged.filter(pl.col('P_substellar') > 0.9).height,
        n_orbital_mid_psub=orb_merged.filter((pl.col('P_substellar') > 0.5) & (pl.col('P_substellar') <= 0.9)).height,
        n_orbital_low_psub=orb_merged.filter((pl.col('P_substellar') > 0.1) & (pl.col('P_substellar') <= 0.5)).height,
        n_orbital_stellar_imposter=orb_merged.filter(pl.col('P_substellar') <= 0.1).height,
        n_orbital_tight=orb_merged.filter(pl.col('i_constraint_quality') == 'TIGHT').height,
        n_orbital_moderate=orb_merged.filter(pl.col('i_constraint_quality') == 'MODERATE').height,
        n_orbital_loose=orb_merged.filter(pl.col('i_constraint_quality') == 'LOOSE').height,
        n_orbital_prior_dom=orb_merged.filter(pl.col('i_constraint_quality') == 'PRIOR_DOMINATED').height,
        n_accel_total=acc_merged.height,
        n_accel_valid=acc_merged.filter(pl.col('P_substellar').is_not_null()).height,
        n_accel_high_psub=acc_merged.filter(pl.col('P_substellar') > 0.5).height,
        n_accel_mid_psub=acc_merged.filter((pl.col('P_substellar') > 0.2) & (pl.col('P_substellar') <= 0.5)).height,
        n_accel_likely_stellar=acc_merged.filter(pl.col('P_substellar') < 0.2).height,
        N_MC_samples=N_SAMPLES,
    )
    with open(OUT_DIR / 'SUMMARY.json', 'w') as f:
        json.dump(summary, f, indent=2)
    print(f'\nSummary stats written to {OUT_DIR}/SUMMARY.json')
    print(json.dumps(summary, indent=2))

    return orb_merged, acc_merged


if __name__ == '__main__':
    main()
