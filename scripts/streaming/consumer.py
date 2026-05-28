"""Live consumer — watches data/raw_chunks/ and processes each new chunk.

Subscribes to filesystem events. When a new {mode}_RA{NNN}.parquet appears:
  1. Read the chunk
  2. Compute photocentric a, mass function f(M), and M_2 (Bayesian solve)
  3. Assign mass class
  4. Append to data/derived/{mode}_hunt_derived.parquet (atomic)
  5. Update live_stats.json with running class distribution + defensible counts
  6. Forward newly-derived rows to the River ML trainer

This means downstream analyses (defensible subsets, ML classifier, deep
dive on top candidates) can begin operating on partial data as soon as
the first chunk lands — no waiting for the producer to finish all 12.

Usage:
    python consumer.py --mode main
    python consumer.py --mode wider
"""
from __future__ import annotations
import argparse, json, math, sys, time, warnings
warnings.filterwarnings('ignore')
from pathlib import Path
from datetime import datetime, timezone

import polars as pl
import pandas as pd
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

ROOT = Path('/Users/legbatterij/claude_projects/gaia-recovered-2026-05-27')
RAW = ROOT / 'data' / 'raw_chunks'
DERIVED = ROOT / 'data' / 'derived'


def photocentric_a_mas(A, B, F, G):
    if any(v is None for v in (A, B, F, G)) or math.isnan(A) or math.isnan(B) \
       or math.isnan(F) or math.isnan(G):
        return None
    u = 0.5 * (A*A + B*B + F*F + G*G)
    v = A*G - B*F
    disc = max(0.0, u*u - v*v)
    return math.sqrt(u + math.sqrt(disc))


def solve_m2(fM, M1):
    lo, hi = 1e-4, 1e3
    for _ in range(80):
        mid = 0.5 * (lo + hi)
        if mid**3 > fM * (M1 + mid)**2:
            hi = mid
        else:
            lo = mid
    return 0.5 * (lo + hi)


def mass_class(m2):
    if m2 >= 3.0: return 'dormant_BH_candidate'
    if m2 >= 1.2: return 'dormant_NS_candidate'
    if m2 >= 0.5: return 'WD_or_low_mass_star'
    if m2 >= 0.08: return 'M_dwarf_companion'
    if m2 >= 0.013: return 'BD_candidate'
    return 'planet_candidate'


def K1_kms(P_d, e, M1, M2, sini):
    """Spectroscopic RV semi-amplitude of primary, in km/s."""
    if P_d <= 0 or e >= 1 or M1 <= 0 or M2 <= 0:
        return 0.0
    P_s = P_d * 86400.0
    num = (2 * math.pi * 6.6743e-11 / P_s) ** (1/3) * (M2 * 1.989e30) * sini
    den = ((M1 + M2) * 1.989e30) ** (2/3) * math.sqrt(1 - e * e)
    return (num / den) / 1000.0


def filter32(K_obs, P_d, e, M1, M2_astrom):
    """Filter #32: joint astrometric + RV consistency check.

    For a real binary, K_obs <= K_pred(M_2_astrom, sin i = 1).
    If K_obs / K_pred(i=90) > 1, K_obs is dominated by non-orbital noise
    (stellar pulsations, RVS systematics) and the candidate is REJECTED.

    Returns: ('PASS', 'FAIL_K_exceeds_max', 'NO_DATA', or 'CONSISTENT')
             plus the implied sin(i).
    """
    if K_obs is None or pd.isna(K_obs) or K_obs <= 0:
        return 'NO_DATA', None
    K_max = K1_kms(P_d, e, M1, M2_astrom, 1.0)
    if K_max <= 0:
        return 'NO_DATA', None
    sini_implied = K_obs / K_max
    if sini_implied > 1.05:  # 5% margin for K_obs uncertainty
        return 'FAIL', sini_implied
    return 'PASS', sini_implied


def derive_chunk(chunk_df: pd.DataFrame) -> pd.DataFrame:
    """Apply Thiele-Innes -> M_2 derivation row-by-row."""
    rows = []
    for _, r in chunk_df.iterrows():
        a_phot_mas = photocentric_a_mas(
            r.get('a_thiele_innes'), r.get('b_thiele_innes'),
            r.get('f_thiele_innes'), r.get('g_thiele_innes'),
        )
        plx = r.get('parallax')
        P = r.get('period')
        if a_phot_mas is None or plx is None or plx <= 0 or P is None or P <= 0:
            continue
        a_phot_AU = a_phot_mas / plx
        P_yr = P / 365.25
        fM = a_phot_AU**3 / P_yr**2
        M1_raw = r.get('mass_flame')
        M1 = float(M1_raw) if (M1_raw is not None and not pd.isna(M1_raw) and M1_raw > 0.05) else 1.0
        M2 = solve_m2(fM, M1)
        cls = mass_class(M2)
        e_val = r.get('eccentricity')
        e_val = float(e_val) if (e_val is not None and not pd.isna(e_val)) else 0.0
        # Filter #30 chromatic-bias risk
        bp_rp = r.get('bp_rp')
        logg = r.get('logg_gspphot')
        cbias_risk = ((bp_rp is not None and not pd.isna(bp_rp) and bp_rp > 1.2)
                      or (logg is not None and not pd.isna(logg) and logg < 2.7))
        # Filter #31 paired check
        K_obs = r.get('rv_amplitude_robust')
        pval = r.get('rv_chisq_pvalue')
        if K_obs is None or pval is None or pd.isna(K_obs) or pd.isna(pval):
            f31 = 'NO_DATA'
        elif K_obs > 5 and pval < 0.05:
            f31 = 'PASS'
        elif K_obs > 5 and pval > 0.5:
            f31 = 'FAIL'
        else:
            f31 = 'AMBIGUOUS'
        # Filter #32 joint astrom + RV consistency
        f32, sini_implied = filter32(K_obs, P, e_val, M1, M2)
        rows.append({
            'source_id': int(r['source_id']),
            'nss_solution_type': r.get('nss_solution_type'),
            'P_d': P, 'e': r.get('eccentricity'),
            'significance': r.get('significance'),
            'ra': r.get('ra'), 'dec': r.get('dec'),
            'l': r.get('l'), 'b': r.get('b'),
            'a_phot_mas': round(a_phot_mas, 4),
            'parallax': plx,
            'G': r.get('phot_g_mean_mag'), 'bp_rp': bp_rp,
            'ruwe': r.get('ruwe'),
            'aen_sig': r.get('astrometric_excess_noise_sig'),
            'rv_amplitude_robust': K_obs, 'rv_chisq_pvalue': pval,
            'rv_nb_transits': r.get('rv_nb_transits'),
            'Teff': r.get('teff_gspphot'), 'logg': logg,
            'M1_msun': round(M1, 3),
            'fM_msun': round(fM, 4),
            'M2_msun': round(M2, 4),
            'in_sb2': bool(r.get('in_sb2', False)),
            'cbias_risk': bool(cbias_risk),
            'filter31': f31,
            'filter32': f32,
            'sini_implied': round(sini_implied, 3) if sini_implied is not None else None,
            'class': cls,
        })
    return pd.DataFrame(rows)


def append_parquet(df: pd.DataFrame, path: Path):
    """Append by reading + concat + atomic write. OK for our scale (~50k rows total)."""
    if path.exists():
        existing = pd.read_parquet(path)
        df = pd.concat([existing, df], ignore_index=True)
        df = df.drop_duplicates(subset=['source_id'])
    tmp = path.with_suffix('.parquet.tmp')
    df.to_parquet(tmp, index=False)
    tmp.replace(path)


def update_live_stats(mode: str, derived_path: Path):
    if not derived_path.exists(): return
    df = pl.read_parquet(derived_path)
    has_f32 = 'filter32' in df.columns
    stats = {
        'mode': mode,
        'updated_at': datetime.now(timezone.utc).isoformat(),
        'total_derived_rows': len(df),
        'class_distribution': dict(
            df.group_by('class').len().sort('len', descending=True).iter_rows()
        ),
        'cbias_risk_count': int(df.filter(pl.col('cbias_risk')).height),
        'filter31_pass_count': int(df.filter(pl.col('filter31') == 'PASS').height),
        'filter31_fail_count': int(df.filter(pl.col('filter31') == 'FAIL').height),
        'in_sb2_count': int(df.filter(pl.col('in_sb2')).height),
    }
    if has_f32:
        stats['filter32_pass_count'] = int(df.filter(pl.col('filter32') == 'PASS').height)
        stats['filter32_fail_count'] = int(df.filter(pl.col('filter32') == 'FAIL').height)
    # Defensible BH/NS subset stats (in-line counts only — full CSV separate)
    bh_def = df.filter(
        (pl.col('class') == 'dormant_BH_candidate') &
        (pl.col('significance') >= 30) & (pl.col('ruwe') < 10) &
        (pl.col('parallax') >= 1.5)
    )
    ns_def = df.filter(
        (pl.col('class') == 'dormant_NS_candidate') &
        (pl.col('significance') >= 30) & (pl.col('ruwe') < 5) &
        (pl.col('parallax') >= 1.5)
    )
    stats['defensible_bh_count'] = len(bh_def)
    stats['defensible_ns_count'] = len(ns_def)
    # SURVIVORS of all 4 filters (#29 SB2, #30 cbias, #31 RV-real, #32 joint-consistency)
    if has_f32:
        survivors_bh = df.filter(
            (pl.col('class') == 'dormant_BH_candidate') &
            (~pl.col('in_sb2')) &  # #29
            (~pl.col('cbias_risk')) &  # #30
            (pl.col('filter31') == 'PASS') &  # #31
            (pl.col('filter32') == 'PASS')  # #32
        )
        survivors_ns = df.filter(
            (pl.col('class') == 'dormant_NS_candidate') &
            (~pl.col('in_sb2')) & (~pl.col('cbias_risk')) &
            (pl.col('filter31') == 'PASS') & (pl.col('filter32') == 'PASS')
        )
        stats['all_filters_pass_BH'] = len(survivors_bh)
        stats['all_filters_pass_NS'] = len(survivors_ns)
        stats['top_BH_all_filters'] = [
            {'source_id': int(r['source_id']), 'sig': float(r['significance']),
             'M2_astrom': float(r['M2_msun']),
             'sini_implied': float(r['sini_implied']) if r['sini_implied'] is not None else None,
             'G': float(r['G']) if r['G'] is not None else None}
            for r in survivors_bh.sort('significance', descending=True).head(10).iter_rows(named=True)
        ]
    stats['top_5_bh_by_sig'] = [
        {'source_id': int(r['source_id']), 'sig': float(r['significance']),
         'M2': float(r['M2_msun']), 'G': float(r['G']) if r['G'] is not None else None,
         'filter31': r['filter31'], 'cbias': r['cbias_risk']}
        for r in bh_def.sort('significance', descending=True).head(5).iter_rows(named=True)
    ]
    tmp = DERIVED / f'live_stats_{mode}.json.tmp'
    tmp.write_text(json.dumps(stats, indent=2, default=str))
    tmp.replace(DERIVED / f'live_stats_{mode}.json')
    return stats


def write_defensible(mode: str, derived_path: Path):
    if not derived_path.exists(): return
    df = pl.read_parquet(derived_path)
    bh = df.filter(
        (pl.col('class') == 'dormant_BH_candidate') &
        (pl.col('significance') >= 30) & (pl.col('ruwe') < 10) &
        (pl.col('parallax') >= 1.5)
    ).sort('significance', descending=True)
    ns = df.filter(
        (pl.col('class') == 'dormant_NS_candidate') &
        (pl.col('significance') >= 30) & (pl.col('ruwe') < 5) &
        (pl.col('parallax') >= 1.5)
    ).sort('significance', descending=True)
    bh.write_parquet(DERIVED / f'{mode}_defensible_bh.parquet')
    ns.write_parquet(DERIVED / f'{mode}_defensible_ns.parquet')
    return len(bh), len(ns)


def process_chunk(chunk_path: Path, mode: str, ml=None):
    print(f'[{datetime.now().strftime("%H:%M:%S")}] processing {chunk_path.name}', flush=True)
    chunk_df = pd.read_parquet(chunk_path)
    if len(chunk_df) == 0:
        print(f'  empty chunk', flush=True); return
    derived = derive_chunk(chunk_df)
    if len(derived) == 0:
        print(f'  no derivable rows', flush=True); return

    derived_path = DERIVED / f'{mode}_hunt_derived.parquet'
    append_parquet(derived, derived_path)
    stats = update_live_stats(mode, derived_path)
    n_bh, n_ns = write_defensible(mode, derived_path)

    print(f'  +{len(derived)} derived rows | total={stats["total_derived_rows"]} | '
          f'classes={stats["class_distribution"]} | def_BH={n_bh} def_NS={n_ns}', flush=True)

    if ml is not None:
        ml.learn_chunk(derived)


class ChunkHandler(FileSystemEventHandler):
    def __init__(self, mode: str, ml=None):
        self.mode = mode
        self.ml = ml

    def on_closed(self, event):
        # watchdog 'closed' is fired when the rename completes
        if event.is_directory: return
        p = Path(event.src_path)
        if not p.name.startswith(f'{self.mode}_RA') or not p.name.endswith('.parquet'):
            return
        # Wait briefly for atomic-write rename to fully complete
        time.sleep(0.5)
        try:
            process_chunk(p, self.mode, self.ml)
        except Exception as e:
            print(f'  ERR processing {p.name}: {type(e).__name__}: {e}', flush=True)

    def on_moved(self, event):
        # File rename from .tmp to .parquet shows up as a move
        if event.is_directory: return
        p = Path(event.dest_path)
        if not p.name.startswith(f'{self.mode}_RA') or not p.name.endswith('.parquet'):
            return
        time.sleep(0.5)
        try:
            process_chunk(p, self.mode, self.ml)
        except Exception as e:
            print(f'  ERR processing {p.name}: {type(e).__name__}: {e}', flush=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--mode', choices=['main', 'wider'], required=True)
    ap.add_argument('--enable-ml', action='store_true')
    ap.add_argument('--catchup', action='store_true',
                     help='Process any existing chunks before starting watcher')
    args = ap.parse_args()

    ml = None
    if args.enable_ml:
        from river_ml import RiverClassifier
        ml = RiverClassifier(mode=args.mode)

    # Catch up on existing chunks first
    if args.catchup:
        existing = sorted(RAW.glob(f'{args.mode}_RA*.parquet'))
        print(f'Catching up on {len(existing)} existing chunks', flush=True)
        for p in existing:
            process_chunk(p, args.mode, ml)

    print(f'\nWatching {RAW} for {args.mode}_RA*.parquet ...', flush=True)
    handler = ChunkHandler(args.mode, ml=ml)
    obs = Observer()
    obs.schedule(handler, str(RAW), recursive=False)
    obs.start()
    try:
        while True:
            time.sleep(5)
    except KeyboardInterrupt:
        obs.stop()
    obs.join()


if __name__ == '__main__':
    sys.path.insert(0, str(Path(__file__).parent))
    sys.exit(main() or 0)
