"""DuckDB analytical view layer over the streaming data lake.

Provides instant SQL queries against the partial / growing parquet dirs:
  - raw_chunks   : raw NSS+gaia_source rows (per-chunk parquet)
  - hunt_derived : derived rows with M_2 + class

DuckDB auto-discovers new parquet files in the directory, so queries
always reflect current state.

Usage:
    python duckdb_views.py             # opens interactive shell
    python duckdb_views.py --query "SELECT class, COUNT(*) FROM hunt_derived GROUP BY 1"
"""
from __future__ import annotations
import argparse
from pathlib import Path

import duckdb

ROOT = Path('/Users/legbatterij/claude_projects/gaia-recovered-2026-05-27')
RAW = ROOT / 'data' / 'raw_chunks'
DERIVED = ROOT / 'data' / 'derived'


def create_views(con: duckdb.DuckDBPyConnection):
    """Set up unified views that auto-discover all parquet files.
    Skips modes with no chunks yet — duckdb errors on empty glob."""
    for mode in ('main', 'wider'):
        chunks = list(RAW.glob(f'{mode}_RA*.parquet'))
        if chunks:
            con.execute(f"""
                CREATE OR REPLACE VIEW raw_{mode} AS
                SELECT * FROM read_parquet('{RAW}/{mode}_RA*.parquet', union_by_name=true)
            """)

    # Derived (single parquet per mode, maintained by consumer)
    for mode in ('main', 'wider'):
        derived = DERIVED / f'{mode}_hunt_derived.parquet'
        if derived.exists():
            con.execute(f"""
                CREATE OR REPLACE VIEW {mode}_derived AS
                SELECT * FROM read_parquet('{derived}')
            """)
        bh = DERIVED / f'{mode}_defensible_bh.parquet'
        if bh.exists():
            con.execute(f"""
                CREATE OR REPLACE VIEW {mode}_defensible_bh AS
                SELECT * FROM read_parquet('{bh}')
            """)
        ns = DERIVED / f'{mode}_defensible_ns.parquet'
        if ns.exists():
            con.execute(f"""
                CREATE OR REPLACE VIEW {mode}_defensible_ns AS
                SELECT * FROM read_parquet('{ns}')
            """)


COMMON_QUERIES = {
    'class_dist_main': "SELECT class, COUNT(*) AS n FROM main_derived GROUP BY 1 ORDER BY 2 DESC",
    'class_dist_wider': "SELECT class, COUNT(*) AS n FROM wider_derived GROUP BY 1 ORDER BY 2 DESC",
    'top10_bh_main': """SELECT source_id, P_d, significance, M2_msun, G, bp_rp,
                                rv_amplitude_robust, rv_chisq_pvalue, filter31, cbias_risk
                         FROM main_derived
                         WHERE class = 'dormant_BH_candidate' AND NOT in_sb2
                         ORDER BY significance DESC LIMIT 10""",
    'top10_ns_main': """SELECT source_id, P_d, significance, M2_msun, G, bp_rp,
                                filter31, cbias_risk
                         FROM main_derived
                         WHERE class = 'dormant_NS_candidate' AND NOT in_sb2
                         ORDER BY significance DESC LIMIT 10""",
    'filter31_summary': """SELECT class, filter31, COUNT(*) AS n
                            FROM main_derived
                            GROUP BY 1, 2 ORDER BY 1, 2""",
    'survivors_all_filters': """SELECT source_id, P_d, significance, M2_msun, G, filter31
                                 FROM main_derived
                                 WHERE class IN ('dormant_BH_candidate', 'dormant_NS_candidate')
                                   AND NOT in_sb2 AND NOT cbias_risk
                                   AND filter31 = 'PASS'
                                 ORDER BY significance DESC""",
}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--query', help='Run a single SQL query and exit')
    ap.add_argument('--preset', choices=list(COMMON_QUERIES), help='Run a named preset')
    ap.add_argument('--list-presets', action='store_true')
    args = ap.parse_args()

    if args.list_presets:
        for name, sql in COMMON_QUERIES.items():
            print(f'\n== {name} ==\n{sql.strip()}')
        return

    con = duckdb.connect()
    create_views(con)

    if args.query:
        print(con.sql(args.query).df().to_string())
        return
    if args.preset:
        sql = COMMON_QUERIES[args.preset]
        print(con.sql(sql).df().to_string())
        return

    # Interactive
    print('DuckDB views ready: raw_main, raw_wider, main_derived, wider_derived,')
    print('                     main_defensible_bh, main_defensible_ns, ...')
    print(f"Presets: {list(COMMON_QUERIES)}")
    print('Enter SQL, blank line to exit:')
    while True:
        try:
            line = input('> ').strip()
        except (EOFError, KeyboardInterrupt):
            break
        if not line: break
        try:
            print(con.sql(line).df().to_string())
        except Exception as e:
            print(f'ERR: {e}')


if __name__ == '__main__':
    main()
