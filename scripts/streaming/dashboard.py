"""Live text dashboard — refreshes every N seconds with current state.

Reads:
  data/raw_chunks/STATE_{mode}.json   ← producer progress
  data/derived/live_stats_{mode}.json ← consumer-derived stats
  data/derived/{mode}_ml_stats.json   ← River model metrics

Pure text output; no Streamlit dependency.

Usage:
    python dashboard.py --mode main
    python dashboard.py --mode main --refresh 5  # seconds
"""
from __future__ import annotations
import argparse, json, os, sys, time
from pathlib import Path
from datetime import datetime

ROOT = Path('/Users/legbatterij/claude_projects/gaia-recovered-2026-05-27')
RAW = ROOT / 'data' / 'raw_chunks'
DERIVED = ROOT / 'data' / 'derived'


def read_json(p: Path) -> dict | None:
    try:
        return json.loads(p.read_text())
    except Exception:
        return None


def render(mode: str) -> str:
    lines = []
    lines.append(f'== STREAMING HUNT DASHBOARD ({mode}) ==')
    lines.append(f'   refreshed at {datetime.now().strftime("%H:%M:%S")}\n')

    state = read_json(RAW / f'STATE_{mode}.json')
    if state:
        n_done = len(state.get('completed_chunks', []))
        lines.append(f'-- producer --')
        lines.append(f'  started: {state.get("started_at", "?")}')
        lines.append(f'  last chunk: {state.get("last_chunk_at", "?")}')
        lines.append(f'  chunks: {n_done}/12 done')
        lines.append(f'  total raw rows: {state.get("rows_total", 0)}')
    else:
        lines.append(f'-- producer -- (no STATE_{mode}.json yet)')

    stats = read_json(DERIVED / f'live_stats_{mode}.json')
    if stats:
        lines.append(f'\n-- consumer --')
        lines.append(f'  total derived rows: {stats["total_derived_rows"]}')
        lines.append(f'  class distribution:')
        for c, n in stats['class_distribution'].items():
            lines.append(f'    {c:<25} {n}')
        lines.append(f'  filter31 PASS: {stats["filter31_pass_count"]}, '
                     f'FAIL: {stats["filter31_fail_count"]}')
        lines.append(f'  in SB2: {stats["in_sb2_count"]}')
        lines.append(f'  cbias_risk: {stats["cbias_risk_count"]}')
        lines.append(f'  defensible BH: {stats["defensible_bh_count"]}')
        lines.append(f'  defensible NS: {stats["defensible_ns_count"]}')
        if stats.get('top_5_bh_by_sig'):
            lines.append(f'\n  Top 5 BH by significance:')
            for r in stats['top_5_bh_by_sig']:
                lines.append(f'    sid={r["source_id"]} sig={r["sig"]:.0f} '
                             f'M2={r["M2"]:.2f} G={r["G"]} f31={r["filter31"]} cbias={r["cbias"]}')
    else:
        lines.append(f'\n-- consumer -- (no live_stats_{mode}.json yet)')

    ml = read_json(DERIVED / f'{mode}_ml_stats.json')
    if ml:
        lines.append(f'\n-- River ML --')
        lines.append(f'  n_seen: {ml["n_seen"]}')
        lines.append(f'  accuracy: {ml["accuracy"]:.3f}')
        lines.append(f'  macro F1: {ml["macro_f1"]:.3f}')
        if ml.get('confusion_matrix'):
            lines.append('  confusion matrix (truncated):')
            cm = ml['confusion_matrix']
            classes = sorted(cm.keys())[:5]
            lines.append('    ' + ' '*20 + ' '.join(c[:10] for c in classes))
            for c in classes:
                row = cm.get(c, {})
                lines.append('    ' + c[:20].ljust(20)
                             + ' '.join(str(row.get(c2, 0))[:10].rjust(10) for c2 in classes))
    else:
        lines.append(f'\n-- River ML -- (not running or no data yet)')

    return '\n'.join(lines)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--mode', choices=['main', 'wider'], required=True)
    ap.add_argument('--refresh', type=float, default=10.0)
    ap.add_argument('--once', action='store_true')
    args = ap.parse_args()

    while True:
        os.system('clear' if os.name == 'posix' else 'cls')
        print(render(args.mode))
        if args.once: return
        try:
            time.sleep(args.refresh)
        except KeyboardInterrupt:
            return


if __name__ == '__main__':
    sys.exit(main() or 0)
