"""Relaxed-cuts NSS producer — extends ``producer.py --mode main`` to faint sources.

Same query/structure as producer.py main mode, but with:
    G_max:  13   -> 15      (capture ~82k extra faint AstroSpectroSB1 rows)
    plx_min: 1.0 -> 0.5     (include sources to ~2 kpc instead of 1 kpc)
All other cuts unchanged (sig>=12, P 100-3000 d, same NSS types).

Writes one parquet per RA chunk so the script is fully resumable.

Usage:
    python producer_relaxed.py                 # default chunk_deg=30, all 12 chunks
    python producer_relaxed.py --chunk-deg 30  # explicit
    python producer_relaxed.py --restart       # ignore STATE, redownload all
"""
from __future__ import annotations
import argparse, json, sys, time, warnings
warnings.filterwarnings('ignore')
from pathlib import Path

import pandas as pd
from astroquery.gaia import Gaia

ROOT = Path('/Users/legbatterij/claude_projects/gaia-recovered-2026-05-27')
RAW = ROOT / 'data' / 'raw_chunks'
RAW.mkdir(parents=True, exist_ok=True)

# Relaxed cuts (the ONLY changes vs producer.py main mode):
CUTS = dict(
    sig_min=12, P_min=100, P_max=3000,
    plx_min=0.5,   # was 1.0
    G_max=15,      # was 13
    nss_types=('Orbital', 'AstroSpectroSB1',
               'OrbitalTargetedSearchValidated', 'OrbitalTargetedSearch'),
)
MODE = 'relaxed'


def load_state(state_path: Path) -> dict:
    if state_path.exists():
        return json.loads(state_path.read_text())
    return {'completed_chunks': [], 'started_at': None, 'last_chunk_at': None,
            'rows_total': 0, 'mode': MODE}


def save_state(state_path: Path, state: dict):
    tmp = state_path.with_suffix('.tmp')
    tmp.write_text(json.dumps(state, indent=2, default=str))
    tmp.replace(state_path)


def fetch_chunk(ra_min: float, ra_max: float) -> pd.DataFrame | None:
    nss_types_sql = "(" + ",".join(f"'{t}'" for t in CUTS['nss_types']) + ")"
    q = f"""
    SELECT nss.source_id, nss.nss_solution_type, nss.period, nss.eccentricity,
           nss.significance, nss.a_thiele_innes, nss.b_thiele_innes,
           nss.f_thiele_innes, nss.g_thiele_innes,
           nss.parallax AS nss_parallax, nss.parallax_error AS nss_parallax_error,
           g.ra, g.dec, g.l, g.b,
           g.parallax, g.parallax_error,
           g.phot_g_mean_mag, g.bp_rp,
           g.ruwe, g.astrometric_excess_noise_sig, g.ipd_frac_multi_peak,
           g.rv_amplitude_robust, g.rv_chisq_pvalue, g.rv_nb_transits
    FROM gaiadr3.nss_two_body_orbit AS nss
    JOIN gaiadr3.gaia_source AS g ON g.source_id = nss.source_id
    WHERE nss.nss_solution_type IN {nss_types_sql}
      AND nss.significance >= {CUTS['sig_min']}
      AND nss.period BETWEEN {CUTS['P_min']} AND {CUTS['P_max']}
      AND g.parallax >= {CUTS['plx_min']}
      AND g.phot_g_mean_mag < {CUTS['G_max']}
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


def fetch_supp(source_ids: list[int]) -> pd.DataFrame:
    """FLAME + AP (logg/teff variants) lookup, same as run_v2.py."""
    if not source_ids:
        return pd.DataFrame()
    chunks = []
    for i in range(0, len(source_ids), 1500):
        sub = source_ids[i:i + 1500]
        ids = ','.join(str(int(x)) for x in sub)
        q = f"""
        SELECT ap.source_id,
               ap.mass_flame, ap.radius_flame,
               ap.logg_gspphot, ap.logg_gspspec,
               ap.teff_gspphot, ap.teff_gspspec,
               aps.logg_gspspec_ann, aps.teff_gspspec_ann
        FROM gaiadr3.astrophysical_parameters AS ap
        LEFT JOIN gaiadr3.astrophysical_parameters_supp AS aps USING (source_id)
        WHERE ap.source_id IN ({ids})
        """
        for attempt in range(3):
            try:
                chunks.append(Gaia.launch_job_async(q).get_results().to_pandas())
                break
            except Exception as exc:
                print(f'  AP chunk attempt {attempt+1}: ERR {type(exc).__name__}', flush=True)
                time.sleep(10)
    if chunks:
        return pd.concat(chunks, ignore_index=True)
    return pd.DataFrame()


def fetch_sb2_flag(source_ids: list[int]) -> set[int]:
    """Which of the input source_ids also have an SB2/SB2C NSS solution?"""
    if not source_ids:
        return set()
    out_set: set[int] = set()
    for i in range(0, len(source_ids), 3000):
        sub = source_ids[i:i + 3000]
        ids = ','.join(str(int(x)) for x in sub)
        q = (f"SELECT source_id FROM gaiadr3.nss_two_body_orbit "
             f"WHERE source_id IN ({ids}) AND nss_solution_type IN ('SB2','SB2C')")
        try:
            sb2 = Gaia.launch_job_async(q).get_results().to_pandas()
            out_set.update(int(x) for x in sb2['source_id'])
        except Exception:
            pass
    return out_set


def write_chunk_atomic(df: pd.DataFrame, path: Path):
    tmp = path.with_suffix('.parquet.tmp')
    df.to_parquet(tmp, index=False)
    tmp.replace(path)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--chunk-deg', type=int, default=30)
    ap.add_argument('--restart', action='store_true')
    args = ap.parse_args()

    state_path = RAW / f'STATE_{MODE}.json'
    if args.restart and state_path.exists():
        state_path.unlink()
    state = load_state(state_path)
    if state.get('mode') not in (None, MODE):
        print(f'STATE.json mode mismatch ({state.get("mode")} != {MODE}); use --restart')
        return 1
    state['mode'] = MODE
    if state.get('started_at') is None:
        state['started_at'] = pd.Timestamp.utcnow().isoformat()
    save_state(state_path, state)

    completed = set(state['completed_chunks'])
    n_chunks = 360 // args.chunk_deg
    print(f'Mode={MODE}, chunk_deg={args.chunk_deg}, '
          f'completed_chunks={sorted(completed)} / {n_chunks}', flush=True)

    for ra_min in range(0, 360, args.chunk_deg):
        if ra_min in completed:
            print(f'Skipping RA {ra_min} (already complete)', flush=True)
            continue
        ra_max = ra_min + args.chunk_deg
        t0 = time.time()
        print(f'\nFetching {MODE} RA {ra_min}-{ra_max} ...', flush=True)
        df = fetch_chunk(ra_min, ra_max)
        if df is None:
            print(f'  FAILED — will retry on next run', flush=True)
            continue
        n_nss = len(df)
        print(f'  {n_nss} NSS rows in {time.time()-t0:.1f}s', flush=True)

        if n_nss > 0:
            t1 = time.time()
            supp = fetch_supp(df['source_id'].astype(int).tolist())
            print(f'  Supp(AP+FLAME) in {time.time()-t1:.1f}s (n={len(supp)})', flush=True)
            if not supp.empty:
                supp['source_id'] = supp['source_id'].astype('int64')
                df['source_id'] = df['source_id'].astype('int64')
                # Dedup supp rows (AP table can yield multiple rows per source)
                supp = supp.drop_duplicates(subset=['source_id'], keep='first')
                df = df.merge(supp, on='source_id', how='left')

            t2 = time.time()
            sb2_ids = fetch_sb2_flag(df['source_id'].astype(int).tolist())
            df['in_sb2'] = df['source_id'].apply(lambda x: int(x) in sb2_ids)
            print(f'  SB2 flag in {time.time()-t2:.1f}s ({df["in_sb2"].sum()} flagged)', flush=True)

        out_path = RAW / f'{MODE}_RA{ra_min:03d}.parquet'
        write_chunk_atomic(df, out_path)
        state['completed_chunks'] = sorted(set(state['completed_chunks']) | {ra_min})
        state['last_chunk_at'] = pd.Timestamp.utcnow().isoformat()
        state['rows_total'] = state.get('rows_total', 0) + n_nss
        save_state(state_path, state)
        print(f'  Wrote {out_path.name} | total_rows={state["rows_total"]} | '
              f'completed={len(state["completed_chunks"])}/{n_chunks}', flush=True)

    print(f'\nAll {n_chunks} chunks done. Total rows: {state["rows_total"]}', flush=True)
    return 0


if __name__ == '__main__':
    sys.exit(main())
