"""Chunked NSS hunt producer — resumable, atomic chunk writes.

Fetches Gaia DR3 NSS Orbital + AstroSpectroSB1 sources in N RA chunks,
writes each chunk to its own parquet file the moment it lands. Maintains
STATE.json with completed chunk IDs so the script can be killed and
restarted without losing progress.

Each chunk additionally writes the per-source FLAME M_1 in-place (instead
of bulk pull at end), so downstream consumers can derive M_2 immediately
on chunk arrival.

Usage:
    python producer.py --mode main      # tight cuts (sig>=12, plx>=1, G<13)
    python producer.py --mode wider     # relaxed (sig>=30, plx>=0.5, G<14)
    python producer.py --mode main --restart   # ignore STATE, redownload all
    python producer.py --mode main --chunk-deg 30   # RA chunk width

Output: data/raw_chunks/{mode}_RA{NNN}.parquet + STATE_{mode}.json
"""
from __future__ import annotations
import argparse, json, math, os, sys, time, warnings
warnings.filterwarnings('ignore')
from pathlib import Path

import polars as pl
import pandas as pd
from astroquery.gaia import Gaia

ROOT = Path('/Users/legbatterij/claude_projects/gaia-recovered-2026-05-27')
RAW = ROOT / 'data' / 'raw_chunks'


CUTS = {
    'main': dict(sig_min=12, P_min=100, P_max=3000, plx_min=1.0, G_max=13,
                 nss_types=('Orbital','AstroSpectroSB1','OrbitalTargetedSearchValidated','OrbitalTargetedSearch')),
    'wider': dict(sig_min=30, P_min=100, P_max=3500, plx_min=0.5, G_max=14,
                  nss_types=('Orbital','AstroSpectroSB1','OrbitalTargetedSearchValidated')),
}


def load_state(state_path: Path) -> dict:
    if state_path.exists():
        return json.loads(state_path.read_text())
    return {'completed_chunks': [], 'started_at': None, 'last_chunk_at': None,
             'rows_total': 0, 'mode': None}


def save_state(state_path: Path, state: dict):
    tmp = state_path.with_suffix('.tmp')
    tmp.write_text(json.dumps(state, indent=2, default=str))
    tmp.replace(state_path)


def fetch_chunk(mode: str, ra_min: float, ra_max: float, cuts: dict) -> pd.DataFrame | None:
    nss_types_sql = "(" + ",".join(f"'{t}'" for t in cuts['nss_types']) + ")"
    q = f"""
    SELECT nss.source_id, nss.nss_solution_type, nss.period, nss.eccentricity,
           nss.significance, nss.flags, nss.a_thiele_innes, nss.b_thiele_innes,
           nss.f_thiele_innes, nss.g_thiele_innes,
           g.ra, g.dec, g.l, g.b,
           g.parallax, g.parallax_error,
           g.phot_g_mean_mag, g.bp_rp,
           g.ruwe, g.astrometric_excess_noise_sig, g.ipd_frac_multi_peak,
           g.rv_amplitude_robust, g.rv_chisq_pvalue, g.rv_nb_transits
    FROM gaiadr3.nss_two_body_orbit AS nss
    JOIN gaiadr3.gaia_source AS g ON g.source_id = nss.source_id
    WHERE nss.nss_solution_type IN {nss_types_sql}
      AND nss.significance >= {cuts['sig_min']}
      AND nss.period BETWEEN {cuts['P_min']} AND {cuts['P_max']}
      AND g.parallax >= {cuts['plx_min']}
      AND g.phot_g_mean_mag < {cuts['G_max']}
      AND nss.a_thiele_innes IS NOT NULL
      AND nss.b_thiele_innes IS NOT NULL
      AND g.ra >= {ra_min} AND g.ra < {ra_max}
    """
    for attempt in range(3):
        try:
            return Gaia.launch_job_async(q).get_results().to_pandas()
        except Exception as e:
            print(f'  attempt {attempt+1}: ERR {type(e).__name__}: {str(e)[:120]}', flush=True)
            time.sleep(15)
    return None


def fetch_flame(source_ids: list[int]) -> pd.DataFrame:
    if not source_ids:
        return pd.DataFrame()
    chunks = []
    for i in range(0, len(source_ids), 3000):
        sub = source_ids[i:i+3000]
        ids = ','.join(str(int(x)) for x in sub)
        q = (f"SELECT source_id, mass_flame, teff_gspphot, logg_gspphot, radius_flame "
             f"FROM gaiadr3.astrophysical_parameters WHERE source_id IN ({ids})")
        for attempt in range(3):
            try:
                chunks.append(Gaia.launch_job_async(q).get_results().to_pandas())
                break
            except Exception as e:
                print(f'  FLAME chunk attempt {attempt+1}: ERR', flush=True)
                time.sleep(10)
    if chunks:
        return pd.concat(chunks, ignore_index=True)
    return pd.DataFrame()


def write_chunk_atomic(df: pd.DataFrame, path: Path):
    """Atomic write: parquet to .tmp, then rename to final."""
    tmp = path.with_suffix('.parquet.tmp')
    df.to_parquet(tmp, index=False)
    tmp.replace(path)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--mode', choices=list(CUTS), required=True)
    ap.add_argument('--chunk-deg', type=int, default=30)
    ap.add_argument('--restart', action='store_true')
    args = ap.parse_args()

    cuts = CUTS[args.mode]
    state_path = RAW / f'STATE_{args.mode}.json'
    if args.restart and state_path.exists():
        state_path.unlink()
    state = load_state(state_path)
    if state['mode'] not in (None, args.mode):
        print(f'STATE.json mode mismatch ({state["mode"]} != {args.mode}); use --restart')
        return 1
    state['mode'] = args.mode
    if state['started_at'] is None:
        state['started_at'] = pd.Timestamp.utcnow().isoformat()
    save_state(state_path, state)

    completed = set(state['completed_chunks'])
    print(f'Mode={args.mode}, chunk_deg={args.chunk_deg}, '
          f'completed_chunks={sorted(completed)}', flush=True)

    for ra_min in range(0, 360, args.chunk_deg):
        if ra_min in completed:
            print(f'Skipping RA {ra_min} (already complete)', flush=True)
            continue
        ra_max = ra_min + args.chunk_deg
        t0 = time.time()
        print(f'\nFetching {args.mode} RA {ra_min}-{ra_max} ...', flush=True)
        df = fetch_chunk(args.mode, ra_min, ra_max, cuts)
        if df is None:
            print(f'  FAILED — will retry on next run', flush=True)
            continue
        n_nss = len(df)
        print(f'  {n_nss} NSS rows in {time.time()-t0:.1f}s', flush=True)

        if n_nss > 0:
            t1 = time.time()
            print(f'  Pulling FLAME for {n_nss} sources ...', flush=True)
            flame = fetch_flame(df['source_id'].astype(int).tolist())
            print(f'  FLAME in {time.time()-t1:.1f}s', flush=True)
            if not flame.empty:
                flame['source_id'] = flame['source_id'].astype('int64')
                df['source_id'] = df['source_id'].astype('int64')
                df = df.merge(flame, on='source_id', how='left')

            # SB2/SB2C flag for these sources
            t2 = time.time()
            ids = ','.join(str(int(x)) for x in df['source_id'])
            try:
                sb2 = Gaia.launch_job_async(
                    f"SELECT source_id FROM gaiadr3.nss_two_body_orbit "
                    f"WHERE source_id IN ({ids}) AND nss_solution_type IN ('SB2','SB2C')"
                ).get_results().to_pandas()
                sb2_ids = set(int(x) for x in sb2['source_id'])
            except Exception:
                sb2_ids = set()
            df['in_sb2'] = df['source_id'].apply(lambda x: int(x) in sb2_ids)
            print(f'  SB2 flag in {time.time()-t2:.1f}s ({df["in_sb2"].sum()} flagged)', flush=True)

        out_path = RAW / f'{args.mode}_RA{ra_min:03d}.parquet'
        write_chunk_atomic(df, out_path)
        state['completed_chunks'] = sorted(set(state['completed_chunks']) | {ra_min})
        state['last_chunk_at'] = pd.Timestamp.utcnow().isoformat()
        state['rows_total'] = state.get('rows_total', 0) + n_nss
        save_state(state_path, state)
        print(f'  Wrote {out_path.name} | total_rows={state["rows_total"]} | '
              f'completed={len(state["completed_chunks"])}/12', flush=True)

    print(f'\nAll {360 // args.chunk_deg} chunks done. Total rows: {state["rows_total"]}', flush=True)
    return 0


if __name__ == '__main__':
    sys.exit(main())
