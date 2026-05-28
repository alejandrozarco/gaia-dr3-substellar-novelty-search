"""Apply v2 cascade to the relaxed-cuts NSS chunks.

Reads each `data/raw_chunks/relaxed_RA{NNN}.parquet` chunk produced by
``producer_relaxed.py``, filters to rows NOT already present in
``main_hunt_derived_v2.parquet`` (the existing 56,100-row v2 catalog),
applies ``derive_row_v2`` from consumer_v2.py with the same M1_prior=1.5
default, and writes incrementally to
``data/derived/main_hunt_derived_v2_relaxed.parquet``.

Output schema mirrors main_hunt_derived_v2.parquet exactly (so the two can
be concatenated downstream).

Usage:
    python run_v2_relaxed.py                 # process all relaxed chunks
    python run_v2_relaxed.py --append-only   # skip writing if output exists
    python run_v2_relaxed.py --M1-prior 1.0
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
import polars as pl

THIS = Path(__file__).resolve().parent
sys.path.insert(0, str(THIS))
from consumer_v2 import derive_row_v2, photocentric_a_mas  # noqa: E402

ROOT = Path('/Users/legbatterij/claude_projects/gaia-recovered-2026-05-27')
RAW = ROOT / 'data' / 'raw_chunks'
DERIVED = ROOT / 'data' / 'derived'
EXISTING_V2 = DERIVED / 'main_hunt_derived_v2.parquet'
OUTPUT_PARQUET = DERIVED / 'main_hunt_derived_v2_relaxed.parquet'
LOG_PATH = Path('/tmp/v2_relaxed_rerun.log')


def _log(msg, also_stdout=True):
    stamp = dt.datetime.now().strftime('%H:%M:%S')
    line = f'[{stamp}] {msg}\n'
    with open(LOG_PATH, 'a') as fh:
        fh.write(line)
    if also_stdout:
        print(line.rstrip(), flush=True)


def process_chunk(chunk_path: Path, existing_ids: set[int], M1_prior: float) -> pd.DataFrame:
    """Apply v2 derivation to one raw chunk, return only NEW rows."""
    df = pl.read_parquet(chunk_path).to_pandas()
    df['source_id'] = df['source_id'].astype('int64')
    pre = len(df)
    df = df[~df['source_id'].isin(existing_ids)].copy()
    post = len(df)
    _log(f'  {chunk_path.name}: {pre} chunk rows, {post} are new (not in main v2)')
    if post == 0:
        return pd.DataFrame()

    # Compute photocentric a_phot_mas from Thiele-Innes
    df['a_phot_mas'] = [
        photocentric_a_mas(r['a_thiele_innes'], r['b_thiele_innes'],
                           r['f_thiele_innes'], r['g_thiele_innes'])
        for _, r in df.iterrows()
    ]

    # Build row inputs in the schema derive_row_v2 expects
    out_rows = []
    err_count = 0
    for _, r in df.iterrows():
        row_in = {
            'a_phot_mas': r.get('a_phot_mas'),
            'parallax': r.get('parallax'),
            'nss_parallax': r.get('nss_parallax'),
            'period': r.get('period'),
            'P_d': r.get('period'),
            'eccentricity': r.get('eccentricity'),
            'e': r.get('eccentricity'),
            'mass_flame': r.get('mass_flame'),
            'M1_msun': r.get('mass_flame'),
            'bp_rp': r.get('bp_rp'),
            'logg_gspphot': r.get('logg_gspphot'),
            'logg_gspspec_ann': r.get('logg_gspspec_ann'),
            'logg_gspspec': r.get('logg_gspspec'),
            'teff_gspphot': r.get('teff_gspphot'),
            'teff_gspspec_ann': r.get('teff_gspspec_ann'),
            'rv_amplitude_robust': r.get('rv_amplitude_robust'),
            'rv_chisq_pvalue': r.get('rv_chisq_pvalue'),
            'in_sb2': bool(r.get('in_sb2', False)),
            'nss_solution_type': r.get('nss_solution_type'),
        }
        result = derive_row_v2(row_in, M1_prior=M1_prior)
        if 'error' in result:
            err_count += 1
            result = {k: None for k in [
                'a_phot_mas', 'plx_used', 'plx_source', 'a_phot_AU_v2',
                'P_yr_v2', 'e_v2', 'M1_msun_v2', 'fM_msun_v2', 'M2_msun_v2',
                'class_v2', 'logg_used', 'logg_source', 'cbias_risk_v2',
                'filter29_v2', 'filter30_v2', 'filter30_reason_v2',
                'filter31_v2', 'filter32_v2', 'sini_implied_v2',
                'K_pred_i90_v2', 'tier_v2']}
            result['tier_v2'] = 'ERROR'
            result['class_v2'] = None

        # Merge with the raw chunk fields the existing v2 schema expects
        merged_row = {
            'source_id': int(r['source_id']),
            'nss_solution_type': r.get('nss_solution_type'),
            'P_d': r.get('period'),
            'e': r.get('eccentricity'),
            'significance': r.get('significance'),
            'ra': r.get('ra'),
            'dec': r.get('dec'),
            'l': r.get('l'),
            'b': r.get('b'),
            'parallax': r.get('parallax'),
            'G': r.get('phot_g_mean_mag'),
            'bp_rp': r.get('bp_rp'),
            'ruwe': r.get('ruwe'),
            'aen_sig': r.get('astrometric_excess_noise_sig'),
            'rv_amplitude_robust': r.get('rv_amplitude_robust'),
            'rv_chisq_pvalue': r.get('rv_chisq_pvalue'),
            'rv_nb_transits': r.get('rv_nb_transits'),
            'Teff': r.get('teff_gspphot'),
            'logg': r.get('logg_gspphot'),
            'M1_msun': r.get('mass_flame'),
            'in_sb2': bool(r.get('in_sb2', False)),
            'nss_parallax': r.get('nss_parallax'),
            'nss_parallax_error': r.get('nss_parallax_error'),
            'logg_gspphot': r.get('logg_gspphot'),
            'logg_gspspec': r.get('logg_gspspec'),
            'teff_gspphot': r.get('teff_gspphot'),
            'teff_gspspec': r.get('teff_gspspec'),
            'logg_gspspec_ann': r.get('logg_gspspec_ann'),
            'teff_gspspec_ann': r.get('teff_gspspec_ann'),
            **result,  # v2 columns
        }
        out_rows.append(merged_row)

    _log(f'  {chunk_path.name}: derived {len(out_rows)} rows ({err_count} errors)')
    return pd.DataFrame(out_rows)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--M1-prior', type=float, default=1.5)
    ap.add_argument('--chunks-glob', type=str, default='relaxed_RA*.parquet')
    args = ap.parse_args()

    LOG_PATH.write_text('')
    t_start = time.time()
    _log(f'v2 RELAXED re-run starting')

    # ------------------------------------------------------------------
    # Load existing v2 source_ids so we only process NEW rows
    # ------------------------------------------------------------------
    existing = pl.read_parquet(EXISTING_V2, columns=['source_id']).to_pandas()
    existing_ids = set(int(s) for s in existing['source_id'])
    _log(f'Loaded {len(existing_ids)} existing v2 source_ids from main_hunt_derived_v2')

    # ------------------------------------------------------------------
    # Process each chunk that exists, accumulate
    # ------------------------------------------------------------------
    chunks = sorted(RAW.glob(args.chunks_glob))
    _log(f'Found {len(chunks)} relaxed chunks under {RAW}')
    if not chunks:
        _log('No relaxed chunks yet — exiting (re-run after producer finishes)')
        return 0

    all_new_rows = []
    for cp in chunks:
        t0 = time.time()
        new_df = process_chunk(cp, existing_ids, M1_prior=args.M1_prior)
        if len(new_df) > 0:
            all_new_rows.append(new_df)
            # mid-run tier counts on the per-chunk slice
            tcounts = new_df['tier_v2'].value_counts().to_dict()
            _log(f'    chunk tier_v2 counts: {tcounts}')
        _log(f'  chunk processed in {time.time()-t0:.1f}s')

    if not all_new_rows:
        _log('No new rows produced — exiting')
        return 0

    out = pd.concat(all_new_rows, ignore_index=True)
    # Dedup on source_id (in case Gaia returned a source twice across chunks at RA boundary)
    out = out.drop_duplicates(subset=['source_id'], keep='first').reset_index(drop=True)
    _log(f'Total NEW rows after dedup: {len(out)}')

    out_pl = pl.from_pandas(out)
    out_pl.write_parquet(OUTPUT_PARQUET)
    _log(f'Wrote {OUTPUT_PARQUET.name} ({len(out_pl)} rows, {len(out_pl.columns)} cols)')

    # ------------------------------------------------------------------
    # Summary
    # ------------------------------------------------------------------
    _log('')
    _log('=== NEW v2 tier_v2 counts (relaxed-pool rows only) ===')
    tier_counts = out_pl.group_by('tier_v2').len().sort('len', descending=True)
    for row in tier_counts.iter_rows(named=True):
        _log(f'  {row["tier_v2"]:<55s}  {row["len"]:>7d}')

    _log('')
    _log('=== NEW v2 class_v2 counts ===')
    class_counts = out_pl.group_by('class_v2').len().sort('len', descending=True)
    for row in class_counts.iter_rows(named=True):
        _log(f'  {str(row["class_v2"]):<25s}  {row["len"]:>7d}')

    _log(f'Total runtime: {time.time()-t_start:.1f}s')
    return 0


if __name__ == '__main__':
    sys.exit(main())
