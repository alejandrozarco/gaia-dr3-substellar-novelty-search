"""Driver -- v3 acceleration-NSS cascade for the dormant compact-object hunt.

Queries `gaiadr3.nss_acceleration_astro` (joined with `gaia_source` and the
`astrophysical_parameters[_supp]` tables) for all sources with
`significance >= --min-significance` (default 50, see note below), runs the
PM-acceleration mass-function inversion + the F#29/30/31 demoting filters,
and writes data/derived/acceleration_v3.parquet.

Default significance cut:  The user spec said "significance >= 25" yields
"~5,800 sources" but the actual DR3 count at sig>=25 is 192k -- ~30x larger
than spec.  To keep the run inside the 45-minute budget we use sig>=50 by
default (16,949 sources, ~170 batches at ~2-3s each ≈ 8-10 min), with the
option to lower via --min-significance.

The inversion grids the orbital period in log-P across [P_yr_min, P_yr_max]
(default 3, 100 yr) and reports the M_2 envelope.  See
acceleration_inversion.py for the math.

Usage:
    python run_acceleration.py                              # default sig>=50
    python run_acceleration.py --min-significance 25        # full DR3 channel
    python run_acceleration.py --M1-prior 1.0
    python run_acceleration.py --P-yr-min 5 --P-yr-max 60
    python run_acceleration.py --limit 1000                 # quick smoke test
    python run_acceleration.py --use-cache                  # reuse cached supp
"""
from __future__ import annotations
import argparse
import datetime as dt
import math
import sys
import time
import warnings
warnings.filterwarnings('ignore')
from pathlib import Path

import pandas as pd
import numpy as np

THIS = Path(__file__).resolve().parent
sys.path.insert(0, str(THIS))
from acceleration_inversion import derive_row_v3  # noqa: E402

ROOT = Path('/Users/legbatterij/claude_projects/gaia-recovered-2026-05-27')
DERIVED = ROOT / 'data' / 'derived'
OUTPUT_PARQUET = DERIVED / 'acceleration_v3.parquet'
ACCEL_CACHE = DERIVED / 'acceleration_v3_raw.parquet'
SUPP_CACHE = DERIVED / 'acceleration_v3_supplementary.parquet'
LOG_PATH = Path('/tmp/v3_acceleration.log')

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------

def _log(msg, also_stdout=True):
    stamp = dt.datetime.now().strftime('%H:%M:%S')
    line = f'[{stamp}] {msg}\n'
    with open(LOG_PATH, 'a') as fh:
        fh.write(line)
    if also_stdout:
        print(line.rstrip(), flush=True)


# ---------------------------------------------------------------------------
# Step 1: fetch acceleration table (sig >= threshold)
# ---------------------------------------------------------------------------

ACCEL_FETCH_ADQL = """
SELECT source_id, nss_solution_type, accel_ra, accel_dec,
       accel_ra_error, accel_dec_error,
       deriv_accel_ra, deriv_accel_dec,
       deriv_accel_ra_error, deriv_accel_dec_error,
       parallax AS nss_parallax,
       parallax_error AS nss_parallax_error,
       pmra AS nss_pmra, pmdec AS nss_pmdec,
       significance, goodness_of_fit,
       astrometric_n_good_obs_al
FROM gaiadr3.nss_acceleration_astro
WHERE significance >= {sig}
"""


def fetch_acceleration_table(min_sig: float, limit: int = None):
    """One-shot fetch of the acceleration table at sig >= min_sig."""
    from astroquery.gaia import Gaia
    q = ACCEL_FETCH_ADQL.format(sig=min_sig)
    if limit:
        # ADQL TOP must come right after SELECT; rewrite carefully:
        q = q.replace('SELECT', f'SELECT TOP {limit}', 1)
    t0 = time.time()
    _log(f'Fetching nss_acceleration_astro at sig >= {min_sig} ...')
    job = Gaia.launch_job_async(q, verbose=False)
    tbl = job.get_results()
    df = tbl.to_pandas()
    df['source_id'] = df['source_id'].astype('int64')
    _log(f'  fetched {len(df)} rows in {time.time()-t0:.1f}s')
    return df


# ---------------------------------------------------------------------------
# Step 2: batched gaia_source + astrophysical_parameters[_supp] join
# ---------------------------------------------------------------------------

SUPP_ADQL = """
SELECT g.source_id,
       g.parallax AS gs_parallax,
       g.parallax_error AS gs_parallax_error,
       g.bp_rp,
       g.phot_g_mean_mag,
       g.ruwe,
       g.radial_velocity,
       g.radial_velocity_error,
       g.rv_chisq_pvalue,
       g.rv_amplitude_robust,
       g.in_qso_candidates, g.in_galaxy_candidates, g.in_andromeda_survey,
       ap.logg_gspphot, ap.logg_gspspec,
       ap.teff_gspphot, ap.teff_gspspec,
       aps.logg_gspspec_ann, aps.teff_gspspec_ann
FROM gaiadr3.gaia_source AS g
LEFT JOIN gaiadr3.astrophysical_parameters AS ap USING (source_id)
LEFT JOIN gaiadr3.astrophysical_parameters_supp AS aps USING (source_id)
WHERE g.source_id IN ({ids})
"""


def _gaia_query(ids):
    from astroquery.gaia import Gaia
    ids_str = ','.join(str(int(s)) for s in ids)
    q = SUPP_ADQL.format(ids=ids_str)
    job = Gaia.launch_job_async(q, verbose=False)
    return job.get_results().to_pandas()


def fetch_supp_batched(source_ids, batch_size=100, max_retries=2):
    chunks, skipped = [], []
    total = len(source_ids)
    n_batches = (total + batch_size - 1) // batch_size
    _log(f'Fetching gaia_source+AP join for {total} ids in {n_batches} batches')

    for i in range(0, total, batch_size):
        batch = source_ids[i:i + batch_size]
        batch_idx = i // batch_size + 1
        t0 = time.time()
        ok = False
        for attempt in range(max_retries):
            try:
                df = _gaia_query(batch)
                dt_s = time.time() - t0
                if df is not None and len(df) > 0:
                    chunks.append(df)
                    _log(f'  batch {batch_idx}/{n_batches}: {len(df)} rows in {dt_s:.1f}s'
                         + ('' if attempt == 0 else f' (retry #{attempt})'))
                    ok = True
                    break
                else:
                    _log(f'  batch {batch_idx}/{n_batches}: empty result in {dt_s:.1f}s')
                    if attempt + 1 < max_retries:
                        time.sleep(5)
            except Exception as exc:  # noqa: BLE001
                _log(f'  batch {batch_idx}/{n_batches}: attempt {attempt+1} ERR '
                     f'{type(exc).__name__}: {str(exc)[:120]}')
                if attempt + 1 < max_retries:
                    time.sleep(5)
        if not ok:
            skipped.extend(int(s) for s in batch)
            _log(f'  batch {batch_idx}/{n_batches}: SKIPPED ({len(batch)} ids) '
                 f'after {max_retries} attempts')

    if chunks:
        result = pd.concat(chunks, ignore_index=True)
        result['source_id'] = result['source_id'].astype('int64')
        result = result.drop_duplicates(subset=['source_id'], keep='first').reset_index(drop=True)
    else:
        result = pd.DataFrame(columns=[
            'source_id', 'gs_parallax', 'gs_parallax_error', 'bp_rp',
            'phot_g_mean_mag', 'ruwe', 'radial_velocity', 'radial_velocity_error',
            'rv_chisq_pvalue', 'rv_amplitude_robust',
            'in_qso_candidates', 'in_galaxy_candidates', 'in_andromeda_survey',
            'logg_gspphot', 'logg_gspspec', 'teff_gspphot', 'teff_gspspec',
            'logg_gspspec_ann', 'teff_gspspec_ann',
        ])
    return result, skipped


# ---------------------------------------------------------------------------
# Driver
# ---------------------------------------------------------------------------

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--min-significance', type=float, default=50.0,
                    help='Lower bound on `significance`.  Default 50 keeps '
                         'the run inside the 45-min budget (~17k sources).')
    ap.add_argument('--limit', type=int, default=None,
                    help='Optional cap on number of sources (after sig cut).')
    ap.add_argument('--batch-size', type=int, default=100)
    ap.add_argument('--M1-prior', type=float, default=1.5,
                    help='Fixed M_1 in M_sun (default 1.5)')
    ap.add_argument('--P-yr-min', type=float, default=3.0)
    ap.add_argument('--P-yr-max', type=float, default=100.0)
    ap.add_argument('--use-cache', action='store_true',
                    help='Reuse acceleration_v3_raw and _supplementary caches '
                         'if present.')
    args = ap.parse_args()

    LOG_PATH.write_text('')
    t_start = time.time()
    _log(f'v3 acceleration-NSS run starting '
         f'(sig>={args.min_significance}, M1={args.M1_prior}, '
         f'P_yr in [{args.P_yr_min}, {args.P_yr_max}])')

    # 45-min budget check
    BUDGET_S = 45 * 60

    # ------------------------------------------------------------------
    # Step 1: fetch acceleration table
    # ------------------------------------------------------------------
    if args.use_cache and ACCEL_CACHE.exists():
        _log(f'Cache hit: {ACCEL_CACHE.name}')
        accel_df = pd.read_parquet(ACCEL_CACHE)
        # Apply current sig cut on cached data
        accel_df = accel_df[accel_df['significance'] >= args.min_significance].copy()
        if args.limit:
            accel_df = accel_df.head(args.limit)
        _log(f'  loaded {len(accel_df)} rows after applying sig>={args.min_significance}')
    else:
        accel_df = fetch_acceleration_table(args.min_significance, limit=args.limit)
        accel_df.to_parquet(ACCEL_CACHE, index=False)
        _log(f'  cached to {ACCEL_CACHE.name}')

    if len(accel_df) == 0:
        _log('No acceleration sources -- exiting')
        return 0

    elapsed = time.time() - t_start
    if elapsed > BUDGET_S:
        _log(f'Budget exceeded after step 1 ({elapsed:.1f}s); aborting')
        return 1

    # ------------------------------------------------------------------
    # Step 2: fetch supplementary (gaia_source + AP)
    # ------------------------------------------------------------------
    source_ids = accel_df['source_id'].astype(int).tolist()
    if args.use_cache and SUPP_CACHE.exists():
        _log(f'Cache hit: {SUPP_CACHE.name}')
        supp = pd.read_parquet(SUPP_CACHE)
        supp['source_id'] = supp['source_id'].astype('int64')
        cached_ids = set(int(s) for s in supp['source_id'])
        missing = [s for s in source_ids if s not in cached_ids]
        if missing:
            _log(f'  cache missing {len(missing)} ids -- fetching')
            new_supp, sk = fetch_supp_batched(missing, batch_size=args.batch_size)
            if sk:
                _log(f'  {len(sk)} ids skipped during fetch')
            supp = pd.concat([supp, new_supp], ignore_index=True)
            supp = supp.drop_duplicates(subset=['source_id'], keep='first').reset_index(drop=True)
            supp.to_parquet(SUPP_CACHE, index=False)
        else:
            _log('  cache covers all needed ids')
    else:
        supp, skipped = fetch_supp_batched(source_ids, batch_size=args.batch_size)
        if skipped:
            _log(f'WARNING: {len(skipped)} ids skipped during supp fetch')
        if len(supp) > 0:
            supp.to_parquet(SUPP_CACHE, index=False)
            _log(f'  wrote supp cache to {SUPP_CACHE.name} ({len(supp)} rows)')

    elapsed = time.time() - t_start
    if elapsed > BUDGET_S:
        _log(f'Budget exceeded after step 2 ({elapsed:.1f}s); aborting')
        return 1

    # ------------------------------------------------------------------
    # Step 3: merge & derive
    # ------------------------------------------------------------------
    if len(supp) > 0:
        supp['source_id'] = supp['source_id'].astype('int64')
        merged = accel_df.merge(supp, on='source_id', how='left')
    else:
        merged = accel_df.copy()
        for c in ['gs_parallax', 'bp_rp', 'phot_g_mean_mag', 'ruwe',
                  'radial_velocity', 'rv_chisq_pvalue', 'rv_amplitude_robust',
                  'logg_gspphot', 'logg_gspspec', 'logg_gspspec_ann',
                  'teff_gspphot', 'teff_gspspec', 'teff_gspspec_ann']:
            if c not in merged.columns:
                merged[c] = float('nan')

    # Prefer NSS parallax (from acceleration table) over gaia_source parallax.
    # acceleration_inversion expects a single 'parallax' field.
    def _pick_plx(row):
        nss = row.get('nss_parallax')
        gs = row.get('gs_parallax')
        if nss is not None and not (isinstance(nss, float) and math.isnan(nss)) and nss > 0:
            return float(nss), 'NSS-accel'
        if gs is not None and not (isinstance(gs, float) and math.isnan(gs)) and gs > 0:
            return float(gs), 'gaia_source'
        return None, None

    _log(f'Merged {len(merged)} rows.  Deriving v3 quantities ...')
    t_derive = time.time()

    derived_rows = []
    err_count = 0
    for idx, r in merged.iterrows():
        plx, plx_source = _pick_plx(r)
        row_in = {
            'accel_ra': r.get('accel_ra'),
            'accel_dec': r.get('accel_dec'),
            'accel_ra_error': r.get('accel_ra_error'),
            'accel_dec_error': r.get('accel_dec_error'),
            'parallax': plx,
            'bp_rp': r.get('bp_rp'),
            'logg_gspphot': r.get('logg_gspphot'),
            'logg_gspspec_ann': r.get('logg_gspspec_ann'),
            'logg_gspspec': r.get('logg_gspspec'),
            'teff_gspphot': r.get('teff_gspphot'),
            'teff_gspspec_ann': r.get('teff_gspspec_ann'),
            'rv_amplitude_robust': r.get('rv_amplitude_robust'),
            'rv_chisq_pvalue': r.get('rv_chisq_pvalue'),
            'in_sb2': False,  # nss_acceleration_astro has no SB2 flag
            'nss_solution_type': r.get('nss_solution_type'),
        }
        result = derive_row_v3(row_in,
                               M1_prior=args.M1_prior,
                               P_yr_min=args.P_yr_min,
                               P_yr_max=args.P_yr_max)
        if 'error' in result:
            err_count += 1
            result = {k: None for k in [
                'accel_mag_mas_yr2', 'accel_mag_err', 'plx_used',
                'M1_msun_v3', 'P_yr_min_grid', 'P_yr_max_grid',
                'M2_min_v3', 'M2_median_v3', 'M2_max_v3',
                'logg_used_v3', 'logg_source_v3', 'cbias_risk_v3',
                'filter29_v3', 'filter30_v3', 'filter30_reason_v3',
                'filter31_v3', 'tier_v3']}
            result['tier_v3'] = f'ERROR ({err_count})'
        result['source_id'] = int(r['source_id'])
        result['plx_source_v3'] = plx_source
        derived_rows.append(result)

    _log(f'  derived in {time.time()-t_derive:.1f}s ({err_count} errors)')

    der_df = pd.DataFrame(derived_rows)
    der_df = der_df.drop_duplicates(subset=['source_id']).reset_index(drop=True)
    merged_dd = merged.drop_duplicates(subset=['source_id']).reset_index(drop=True)
    out = merged_dd.merge(der_df, on='source_id', how='left')

    out.to_parquet(OUTPUT_PARQUET, index=False)
    _log(f'Wrote {OUTPUT_PARQUET.name} ({len(out)} rows, {len(out.columns)} cols)')

    # ------------------------------------------------------------------
    # Step 4: summary
    # ------------------------------------------------------------------
    _log('')
    _log('=== v3 tier_v3 counts ===')
    counts = out['tier_v3'].value_counts(dropna=False)
    for tname, n in counts.items():
        _log(f'  {str(tname):<60s}  {n:>7d}')
    _log('')

    # Top 10 Tier-1 BH
    t1bh = out[out['tier_v3'] == 'Tier-1 BH'].copy()
    t1bh = t1bh.sort_values('M2_min_v3', ascending=False)
    _log(f'=== Top 10 Tier-1 BH (n={len(t1bh)}) ===')
    cols = ['source_id', 'M2_min_v3', 'M2_median_v3', 'M2_max_v3',
            'accel_mag_mas_yr2', 'plx_used', 'plx_source_v3',
            'significance', 'phot_g_mean_mag']
    cols = [c for c in cols if c in t1bh.columns]
    for _, r in t1bh.head(10).iterrows():
        bits = []
        for c in cols:
            v = r.get(c)
            if isinstance(v, (int, np.integer)):
                bits.append(f'{c}={v}')
            elif isinstance(v, float) and not pd.isna(v):
                bits.append(f'{c}={v:.3f}')
            else:
                bits.append(f'{c}={v}')
        _log('  ' + '  '.join(bits))
    _log('')

    # Top 10 Tier-1 NS
    t1ns = out[out['tier_v3'] == 'Tier-1 NS'].copy()
    t1ns = t1ns.sort_values('M2_min_v3', ascending=False)
    _log(f'=== Top 10 Tier-1 NS (n={len(t1ns)}) ===')
    for _, r in t1ns.head(10).iterrows():
        bits = []
        for c in cols:
            v = r.get(c)
            if isinstance(v, (int, np.integer)):
                bits.append(f'{c}={v}')
            elif isinstance(v, float) and not pd.isna(v):
                bits.append(f'{c}={v:.3f}')
            else:
                bits.append(f'{c}={v}')
        _log('  ' + '  '.join(bits))
    _log('')

    # Cross-ref with v2 catalog
    V2_PATH = DERIVED / 'main_hunt_derived_v2.parquet'
    if V2_PATH.exists():
        import polars as pl
        v2 = pl.read_parquet(V2_PATH).to_pandas()
        v2_ids = set(int(s) for s in v2['source_id'])
        v3_ids = set(int(s) for s in out['source_id'])
        overlap = v2_ids & v3_ids
        _log(f'=== Cross-ref with v2 catalog ===')
        _log(f'  v2 sources: {len(v2_ids)}')
        _log(f'  v3 sources (acceleration): {len(v3_ids)}')
        _log(f'  Overlap: {len(overlap)} '
             f'(expected ~0 -- acceleration is for P > Gaia baseline)')
        if overlap:
            v2_sub = v2[v2['source_id'].isin(overlap)]
            v3_sub = out[out['source_id'].isin(overlap)]
            joint = v2_sub.merge(v3_sub[['source_id', 'tier_v3', 'M2_min_v3', 'M2_max_v3']],
                                 on='source_id', how='left')
            for _, r in joint.head(20).iterrows():
                _log(f'  sid={r["source_id"]:<22} v2_tier="{r.get("tier_v2"):<40}"'
                     f'  v3_tier="{r.get("tier_v3"):<40}"')

    _log(f'\nTotal runtime: {time.time()-t_start:.1f}s')
    _log(f'Output: {OUTPUT_PARQUET}')
    _log('v3 acceleration run complete')
    return 0


if __name__ == '__main__':
    sys.exit(main())
