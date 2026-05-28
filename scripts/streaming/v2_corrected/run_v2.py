"""Driver — bulk v2 re-run of the dormant compact-object cascade.

Reads data/derived/main_hunt_derived.parquet (the published 56,100-row
cascade output), fetches the missing fields (NSS parallax,
logg_gspspec_ann, logg_gspspec, teff_gspspec_ann) from Gaia DR3 ADQL for
all 56,100 sources (batched 100 IDs per query), applies the three v2
corrections, and writes data/derived/main_hunt_derived_v2.parquet.

The three corrections:
  A. NSS plx preferred over gaia_source.parallax for binaries with orbit fit
  B. K_obs = rv_amplitude_robust / 2 (peak-to-trough → semi-amplitude)
  C. Filter #30 logg fallback chain: gspphot → gspspec_ann → gspspec

Usage:
    python run_v2.py                            # full scope (default, ~20 min)
    python run_v2.py --scope v1-bhns            # only BH+NS-class sources from v1 (~1 min)
    python run_v2.py --skip-gaia                # skip ADQL lookup (only Correction B + cache fallback)
    python run_v2.py --M1-prior 1.0             # override the 1.5 M_sun default

Progress is logged to /tmp/v2_rerun.log (tail -f to monitor).
Outputs:
    data/derived/main_hunt_derived_v2.parquet
    data/derived/main_hunt_derived_v2_supplementary.parquet (Gaia lookup cache)
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
from consumer_v2 import derive_row_v2  # noqa: E402

ROOT = Path('/Users/legbatterij/claude_projects/gaia-recovered-2026-05-27')
DERIVED = ROOT / 'data' / 'derived'
INPUT_PARQUET = DERIVED / 'main_hunt_derived.parquet'
OUTPUT_PARQUET = DERIVED / 'main_hunt_derived_v2.parquet'
LOOKUP_CACHE = DERIVED / 'main_hunt_derived_v2_supplementary.parquet'
LOG_PATH = Path('/tmp/v2_rerun.log')


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
# Batched Gaia ADQL lookup
# ---------------------------------------------------------------------------

GAIA_LOOKUP_ADQL = """
SELECT g.source_id,
       n.parallax AS nss_parallax,
       n.parallax_error AS nss_parallax_error,
       ap.logg_gspphot, ap.logg_gspspec,
       ap.teff_gspphot, ap.teff_gspspec,
       aps.logg_gspspec_ann, aps.teff_gspspec_ann
FROM gaiadr3.gaia_source AS g
LEFT JOIN gaiadr3.nss_two_body_orbit AS n  USING (source_id)
LEFT JOIN gaiadr3.astrophysical_parameters AS ap USING (source_id)
LEFT JOIN gaiadr3.astrophysical_parameters_supp AS aps USING (source_id)
WHERE g.source_id IN ({ids})
"""


def _gaia_query(ids, attempt_no=1):
    """Single ADQL query for one batch of source_ids.  Returns DataFrame or None."""
    try:
        from astroquery.gaia import Gaia
    except ImportError:
        _log('astroquery not installed; cannot do Gaia lookup')
        return None
    Gaia.MAIN_GAIA_TABLE = 'gaiadr3.gaia_source'
    ids_str = ','.join(str(int(s)) for s in ids)
    q = GAIA_LOOKUP_ADQL.format(ids=ids_str)
    job = Gaia.launch_job_async(q, verbose=False)
    tbl = job.get_results()
    return tbl.to_pandas()


def fetch_lookup_batched(source_ids, batch_size=100, max_retries=2):
    """Fetch NSS plx + logg fields for a list of source_ids in batches.

    Wraps each batch in try/except; on failure retries once after 5s wait;
    if second attempt fails, the batch is skipped and source_ids logged.

    Returns (concat_df, skipped_ids_list).
    """
    chunks = []
    skipped = []
    total = len(source_ids)
    n_batches = (total + batch_size - 1) // batch_size
    _log(f'Fetching NSS plx + logg from Gaia for {total} source_ids in '
         f'{n_batches} batches of {batch_size}')

    for i in range(0, total, batch_size):
        batch = source_ids[i:i + batch_size]
        batch_idx = i // batch_size + 1
        t0 = time.time()
        try:
            df = _gaia_query(batch)
            dt_s = time.time() - t0
            if df is not None and len(df) > 0:
                chunks.append(df)
                _log(f'  batch {batch_idx}/{n_batches}: {len(df)} rows in {dt_s:.1f}s')
            else:
                _log(f'  batch {batch_idx}/{n_batches}: empty result in {dt_s:.1f}s')
        except Exception as exc:  # noqa: BLE001
            _log(f'  batch {batch_idx}/{n_batches}: 1st attempt ERR '
                 f'{type(exc).__name__}: {str(exc)[:120]} — retrying after 5s')
            time.sleep(5)
            try:
                df = _gaia_query(batch)
                dt_s = time.time() - t0
                if df is not None and len(df) > 0:
                    chunks.append(df)
                    _log(f'  batch {batch_idx}/{n_batches}: retry OK, {len(df)} rows in {dt_s:.1f}s')
                else:
                    skipped.extend(int(s) for s in batch)
                    _log(f'  batch {batch_idx}/{n_batches}: retry empty — skipped {len(batch)} ids')
            except Exception as exc2:  # noqa: BLE001
                skipped.extend(int(s) for s in batch)
                _log(f'  batch {batch_idx}/{n_batches}: retry ERR '
                     f'{type(exc2).__name__}: {str(exc2)[:120]} — skipped {len(batch)} ids')

    if chunks:
        result = pd.concat(chunks, ignore_index=True)
        result['source_id'] = result['source_id'].astype('int64')
        # Some sources have multiple NSS rows / multiple AP rows — dedup, preferring
        # rows with non-null nss_parallax.
        result = result.sort_values(
            ['source_id', 'nss_parallax'],
            ascending=[True, False],
            na_position='last',
        ).drop_duplicates(subset=['source_id'], keep='first').reset_index(drop=True)
    else:
        result = pd.DataFrame(columns=[
            'source_id', 'nss_parallax', 'nss_parallax_error',
            'logg_gspphot', 'logg_gspspec',
            'teff_gspphot', 'teff_gspspec',
            'logg_gspspec_ann', 'teff_gspspec_ann',
        ])
    return result, skipped


# ---------------------------------------------------------------------------
# Driver
# ---------------------------------------------------------------------------

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--limit', type=int, default=None,
                    help='Optional limit on number of BH+NS sources to look up')
    ap.add_argument('--skip-gaia', action='store_true',
                    help='Skip Gaia ADQL lookup (only apply Correction B)')
    ap.add_argument('--batch-size', type=int, default=100)
    ap.add_argument('--use-cache', action='store_true', default=True,
                    help='Reuse main_hunt_derived_v2_supplementary.parquet if present')
    ap.add_argument('--M1-prior', type=float, default=1.5,
                    help='Fixed M_1 (M_sun) prior used to invert the mass function. '
                         'Defaults to 1.5 (web-tool default).  v1 cascade used '
                         'FLAME mass with fallback to 1.0 — see CASCADE_CORRECTIONS_2026_05_28.md.')
    ap.add_argument('--scope', choices=('all', 'v1-bhns'), default='all',
                    help='Which sources need NSS plx lookup.  "all" covers all '
                         '56,100 input sources (cleanest, ~20 min); "v1-bhns" '
                         'covers only sources that were dormant_BH/NS class in '
                         'v1 (~13 batches, ~1 min).')
    args = ap.parse_args()

    # Truncate the log
    LOG_PATH.write_text('')
    t_start = time.time()
    _log(f'v2 corrected re-run starting (input={INPUT_PARQUET})')

    # ------------------------------------------------------------------
    # Load the 56,100-row published cascade output
    # ------------------------------------------------------------------
    df = pl.read_parquet(INPUT_PARQUET).to_pandas()
    _log(f'Loaded {len(df)} rows from {INPUT_PARQUET.name}')

    # ------------------------------------------------------------------
    # Identify which sources need Gaia ADQL lookup.
    #
    # Original strategy (v2.0): only BH+NS candidates from v1 (1,254 sources).
    # Problem: with M_1=1.5 fixed and NSS plx preferred, many v1 'WD' class
    # sources get re-classified as NS after only Correction B (K_obs/2) is
    # applied — without NSS plx they're spurious Tier-1 NS.
    #
    # Updated strategy (v2.1): look up NSS plx for ALL 56,100 sources.  All
    # of them came from `gaiadr3.nss_two_body_orbit` so all should have an
    # NSS parallax.  Total: ~561 batches @ 2s = ~20 minutes (within budget).
    #
    # Use --scope=v1-bhns to fall back to the v1-candidate-only strategy.
    # ------------------------------------------------------------------
    if args.scope == 'all':
        needs_lookup_ids = df['source_id'].astype(int).tolist()
    elif args.scope == 'v1-bhns':
        needs_lookup_mask = df['class'].isin(['dormant_BH_candidate', 'dormant_NS_candidate'])
        needs_lookup_ids = df.loc[needs_lookup_mask, 'source_id'].astype(int).tolist()
    else:
        raise ValueError(f'unknown scope {args.scope!r}')
    if args.limit:
        needs_lookup_ids = needs_lookup_ids[:args.limit]
    _log(f'{len(needs_lookup_ids)} sources need NSS plx + logg lookup (scope={args.scope})')

    # ------------------------------------------------------------------
    # Fetch supplementary fields (or load from cache)
    # ------------------------------------------------------------------
    skipped = []
    if args.skip_gaia:
        _log('--skip-gaia: skipping ADQL lookup, all corrections use existing data only')
        supp = pd.DataFrame(columns=[
            'source_id', 'nss_parallax', 'nss_parallax_error',
            'logg_gspphot', 'logg_gspspec',
            'teff_gspphot', 'teff_gspspec',
            'logg_gspspec_ann', 'teff_gspspec_ann',
        ])
    elif args.use_cache and LOOKUP_CACHE.exists():
        _log(f'Cache exists at {LOOKUP_CACHE.name} — re-using')
        supp = pl.read_parquet(LOOKUP_CACHE).to_pandas()
        # Dedup cache on load (older cache versions had duplicates from
        # multi-row LEFT JOIN results)
        supp = supp.sort_values(
            ['source_id', 'nss_parallax'],
            ascending=[True, False],
            na_position='last',
        ).drop_duplicates(subset=['source_id'], keep='first').reset_index(drop=True)
        cached_ids = set(int(s) for s in supp['source_id'])
        missing = [s for s in needs_lookup_ids if s not in cached_ids]
        if missing:
            _log(f'Cache missing {len(missing)} ids — fetching those')
            new_supp, sk = fetch_lookup_batched(missing, batch_size=args.batch_size)
            skipped.extend(sk)
            supp = pd.concat([supp, new_supp], ignore_index=True)
            supp = supp.drop_duplicates(subset=['source_id'], keep='first').reset_index(drop=True)
            supp.to_parquet(LOOKUP_CACHE, index=False)
        else:
            _log('Cache covers all needed sources')
            # Re-save the deduplicated cache so future runs start clean
            supp.to_parquet(LOOKUP_CACHE, index=False)
    else:
        supp, skipped = fetch_lookup_batched(needs_lookup_ids, batch_size=args.batch_size)
        if len(supp) > 0:
            supp.to_parquet(LOOKUP_CACHE, index=False)
            _log(f'Wrote supplementary cache to {LOOKUP_CACHE.name} ({len(supp)} rows)')

    if skipped:
        _log(f'WARNING: {len(skipped)} source_ids skipped due to Gaia failures: {skipped[:10]}...')

    # ------------------------------------------------------------------
    # Build the v2 input by merging supplementary fields
    # ------------------------------------------------------------------
    df['source_id'] = df['source_id'].astype('int64')
    if len(supp) > 0:
        supp['source_id'] = supp['source_id'].astype('int64')
        # Drop columns that already exist in df to avoid suffixes
        existing_cols = set(df.columns) - {'source_id'}
        supp_cols = [c for c in supp.columns if c not in existing_cols]
        merged = df.merge(supp[supp_cols], on='source_id', how='left')
    else:
        merged = df.copy()
        for c in ['nss_parallax', 'logg_gspphot', 'logg_gspspec',
                  'teff_gspphot', 'teff_gspspec',
                  'logg_gspspec_ann', 'teff_gspspec_ann']:
            if c not in merged.columns:
                merged[c] = float('nan')

    # Mass_flame is not in the derived parquet (only M1_msun is) — pass through.
    # logg_gspphot in derived parquet was stored as `logg` (lowercase) — keep both.
    # Ensure all columns derive_row_v2 expects exist:
    for c in ['nss_parallax', 'logg_gspphot', 'logg_gspspec', 'logg_gspspec_ann',
              'teff_gspphot', 'teff_gspspec_ann']:
        if c not in merged.columns:
            merged[c] = float('nan')

    _log(f'Merged supplementary fields ({len(merged)} rows). '
         f'Sources with nss_parallax: {merged["nss_parallax"].notna().sum()}, '
         f'with logg_gspspec_ann: {merged["logg_gspspec_ann"].notna().sum()}, '
         f'with logg_gspspec: {merged["logg_gspspec"].notna().sum() if "logg_gspspec" in merged else 0}')

    # ------------------------------------------------------------------
    # Apply v2 derivation row by row
    # ------------------------------------------------------------------
    _log('Applying v2 corrections to all rows ...')
    v2_rows = []
    err_count = 0
    t_derive = time.time()
    for idx, r in merged.iterrows():
        # Build the per-row dict the v2 derive function expects
        row_in = {
            'a_phot_mas': r.get('a_phot_mas'),
            'parallax': r.get('parallax'),  # gaia_source.parallax (from original)
            'nss_parallax': r.get('nss_parallax'),
            'period': r.get('P_d'),
            'P_d': r.get('P_d'),
            'eccentricity': r.get('e'),
            'e': r.get('e'),
            'mass_flame': r.get('M1_msun'),  # stored M1; pre-applied 1.0 fallback
            'M1_msun': r.get('M1_msun'),
            'bp_rp': r.get('bp_rp'),
            # Correction C: use the new lookup if available, else fall back to
            # the `logg` column that was the original logg_gspphot.
            'logg_gspphot': r.get('logg_gspphot') if pd.notna(r.get('logg_gspphot')) else r.get('logg'),
            'logg_gspspec_ann': r.get('logg_gspspec_ann'),
            'logg_gspspec': r.get('logg_gspspec'),
            'teff_gspphot': r.get('teff_gspphot') if pd.notna(r.get('teff_gspphot')) else r.get('Teff'),
            'teff_gspspec_ann': r.get('teff_gspspec_ann'),
            'rv_amplitude_robust': r.get('rv_amplitude_robust'),
            'rv_chisq_pvalue': r.get('rv_chisq_pvalue'),
            'in_sb2': bool(r.get('in_sb2', False)),
            'nss_solution_type': r.get('nss_solution_type'),
        }
        result = derive_row_v2(row_in, M1_prior=args.M1_prior)
        if 'error' in result:
            err_count += 1
            # Keep the source in the output anyway, mark as undefined
            result = {k: None for k in [
                'a_phot_mas', 'plx_used', 'plx_source', 'a_phot_AU_v2',
                'P_yr_v2', 'e_v2', 'M1_msun_v2', 'fM_msun_v2', 'M2_msun_v2',
                'class_v2', 'logg_used', 'logg_source', 'cbias_risk_v2',
                'filter29_v2', 'filter30_v2', 'filter30_reason_v2',
                'filter31_v2', 'filter32_v2', 'sini_implied_v2',
                'K_pred_i90_v2', 'tier_v2']}
            result['tier_v2'] = 'ERROR'
            result['class_v2'] = r.get('class')
        # Always include source_id for join
        result['source_id'] = int(r['source_id'])
        v2_rows.append(result)
    _log(f'Derivation done in {time.time()-t_derive:.1f}s ({err_count} errors)')

    v2_df = pd.DataFrame(v2_rows)
    # Dedup the v2 output by source_id (the merged input may have had duplicate
    # rows for sources with multiple NSS solutions — we already chose the row
    # with non-null nss_parallax, but the iteration emits one v2 row per input
    # row, so dedup the v2 frame too).
    v2_df = v2_df.drop_duplicates(subset=['source_id'], keep='first').reset_index(drop=True)
    # Likewise dedup the merged frame on source_id before joining.
    merged_dedup = merged.drop_duplicates(subset=['source_id'], keep='first').reset_index(drop=True)
    # Merge v2 columns onto the original (keep ALL original columns + add v2 ones)
    out = merged_dedup.merge(v2_df, on='source_id', how='left',
                              suffixes=('', '_v2_redundant'))
    # drop any redundant duplicate columns from the merge
    drop_cols = [c for c in out.columns if c.endswith('_v2_redundant')]
    out = out.drop(columns=drop_cols)

    # Convert to polars for writing
    out_pl = pl.from_pandas(out)
    out_pl.write_parquet(OUTPUT_PARQUET)
    _log(f'Wrote v2 parquet ({len(out_pl)} rows, {len(out_pl.columns)} cols) to '
         f'{OUTPUT_PARQUET.name}')

    # ------------------------------------------------------------------
    # Summary by tier (counts only)
    # ------------------------------------------------------------------
    _log('')
    _log('=== v2 cascade tier counts ===')
    tier_counts = out_pl.group_by('tier_v2').len().sort('len', descending=True)
    for row in tier_counts.iter_rows(named=True):
        _log(f'  {row["tier_v2"]:<55s}  {row["len"]:>7d}')
    _log('')
    _log('=== v2 class_v2 counts ===')
    class_counts = out_pl.group_by('class_v2').len().sort('len', descending=True)
    for row in class_counts.iter_rows(named=True):
        _log(f'  {row["class_v2"]:<25s}  {row["len"]:>7d}')

    # Tier-1 BH and NS detail
    t1_bh = out_pl.filter(pl.col('tier_v2') == 'Tier-1 BH').sort('M2_msun_v2', descending=True)
    t1_ns = out_pl.filter(pl.col('tier_v2') == 'Tier-1 NS').sort('M2_msun_v2', descending=True)
    _log('')
    _log(f'=== Tier-1 BH (n={len(t1_bh)}) ===')
    for r in t1_bh.head(20).iter_rows(named=True):
        sini = r.get('sini_implied_v2')
        sini_s = f'{sini:.3f}' if sini is not None else 'n/a'
        _log(f'  source_id={r["source_id"]:<25d} M2={r["M2_msun_v2"]:.3f}  sini={sini_s}')
    _log('')
    _log(f'=== Tier-1 NS (n={len(t1_ns)}) ===')
    for r in t1_ns.head(40).iter_rows(named=True):
        sini = r.get('sini_implied_v2')
        sini_s = f'{sini:.3f}' if sini is not None else 'n/a'
        _log(f'  source_id={r["source_id"]:<25d} M2={r["M2_msun_v2"]:.3f}  sini={sini_s}')

    # ------------------------------------------------------------------
    # 7 Tier-1 candidates from the smoke test — print expected vs actual
    # ------------------------------------------------------------------
    smoke = [
        (6811355413155399040, 'HD 207141',          1.31, 0.83, 'Tier-1 NS'),
        (2543788153077017344, 'HD 1957',            2.02, 0.57, 'Demoted F#30'),
        ( 666596383384888320, 'TYC 1363-2339-1',    1.12, 0.90, 'Rejected (WD class)'),
        (3396420280383215360, 'TYC 1299-727-1',     1.18, 0.86, 'Rejected (WD class)'),
        (1913089145012902016, 'TYC 2773-348-1',     1.03, 0.71, 'Rejected (WD class)'),
        (3020944382416549632, 'TYC 4791-2322-1',    1.34, 0.75, 'Tier-1 NS'),
        (6471824298353396736, 'TYC 8785-1657-1',    1.06, 0.90, 'Rejected (WD class)'),
    ]
    _log('')
    _log('=== Smoke test: 7 original Tier-1 candidates ===')
    smoke_ids = [s[0] for s in smoke]
    sub = out_pl.filter(pl.col('source_id').is_in(smoke_ids)).to_pandas()
    sub = sub.set_index('source_id')
    for sid, name, m2_exp, sini_exp, tier_exp in smoke:
        if sid not in sub.index:
            _log(f'  {sid} ({name}) — NOT FOUND in v2 output')
            continue
        r = sub.loc[sid]
        m2_v2 = r.get('M2_msun_v2')
        sini_v2 = r.get('sini_implied_v2')
        tier_v2 = r.get('tier_v2')
        plx_src = r.get('plx_source')
        plx = r.get('plx_used')
        m2_s = f'{m2_v2:.3f}' if m2_v2 is not None and not pd.isna(m2_v2) else 'n/a'
        sini_s = f'{sini_v2:.3f}' if sini_v2 is not None and not pd.isna(sini_v2) else 'n/a'
        plx_s = f'{plx:.3f}' if plx is not None and not pd.isna(plx) else 'n/a'
        _log(f'  {sid:<25} {name:<22} M2={m2_s} (exp {m2_exp:.3f})  '
             f'sini={sini_s} (exp {sini_exp:.3f})  '
             f'tier="{tier_v2}"  (plx={plx_s} from {plx_src})')

    _log('')
    _log(f'Total runtime: {time.time()-t_start:.1f}s')
    _log(f'Output: {OUTPUT_PARQUET}')
    _log('v2 corrected re-run complete')
    return 0


if __name__ == '__main__':
    sys.exit(main())
