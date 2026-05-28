"""Derive defensible BH/NS subsets from the main companions hunt.

Applies quality cuts:
  BH: sig >= 30, RUWE < 10, parallax >= 1.5
  NS: sig >= 30, RUWE < 5, parallax >= 1.5

Outputs:
  - dormant_bh_candidates_2026_05_18.csv  (all M_2 >= 3 from main hunt)
  - dormant_bh_candidates_defensible_2026_05_18.csv (post-cuts)
  - dormant_ns_candidates_2026_05_18.csv
  - dormant_ns_candidates_defensible_2026_05_18.csv
"""
from __future__ import annotations
import sys, warnings
warnings.filterwarnings('ignore')
from pathlib import Path
import polars as pl

ROOT = Path('/Users/legbatterij/claude_projects/gaia-recovered-2026-05-27')


def main():
    hunt = ROOT / 'data' / 'intermediate' / 'companions_hunt_all_classes_2026_05_18.csv'
    if not hunt.exists():
        print(f'Hunt CSV missing: {hunt}'); return 1
    df = pl.read_csv(hunt)
    print(f'Hunt rows: {len(df)}')

    bh = df.filter(pl.col('class') == 'dormant_BH_candidate') \
            .sort('significance', descending=True)
    ns = df.filter(pl.col('class') == 'dormant_NS_candidate') \
            .sort('significance', descending=True)
    bh.write_csv(ROOT / 'dormant_bh_candidates_2026_05_18.csv')
    ns.write_csv(ROOT / 'dormant_ns_candidates_2026_05_18.csv')
    print(f'Saved {len(bh)} BH + {len(ns)} NS candidates')

    bh_q = bh.filter((pl.col('significance') >= 30) & (pl.col('ruwe') < 10) &
                     (pl.col('parallax') >= 1.5)).sort('significance', descending=True)
    ns_q = ns.filter((pl.col('significance') >= 30) & (pl.col('ruwe') < 5) &
                     (pl.col('parallax') >= 1.5)).sort('significance', descending=True)
    bh_q.write_csv(ROOT / 'dormant_bh_candidates_defensible_2026_05_18.csv')
    ns_q.write_csv(ROOT / 'dormant_ns_candidates_defensible_2026_05_18.csv')
    print(f'Defensible: {len(bh_q)} BH + {len(ns_q)} NS')

    print('\n=== Top 12 defensible BH ===')
    print(bh_q.head(12).select(['source_id','nss_solution_type','P_d','e','significance',
                                  'a_phot_mas','parallax','G','ruwe','M1_msun','M2_msun']).to_pandas().to_string())
    print('\n=== Top 10 defensible NS by sig ===')
    print(ns_q.head(10).select(['source_id','nss_solution_type','P_d','e','significance',
                                  'M1_msun','M2_msun','G','ruwe']).to_pandas().to_string())
    return 0


if __name__ == '__main__':
    sys.exit(main())
