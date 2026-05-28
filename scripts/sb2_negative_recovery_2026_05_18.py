"""Cross-match v2 pool source IDs against Gaia DR3 NSS SB2/SB2C solutions.

Pulls K1, K2, mass ratio and computes M_2 for double-lined binaries
already in our pool. These are LEAK-FREE stellar-binary negatives (we
know they're luminous secondaries because they show two sets of lines).

Output: data/intermediate/sb2_negative_recovery.csv
"""
from __future__ import annotations
import sys
import warnings
from pathlib import Path
warnings.filterwarnings('ignore')
import polars as pl
from astroquery.gaia import Gaia

ROOT = Path('/Users/legbatterij/claude_projects/gaia-recovered-2026-05-27')


def main():
    pool = pl.read_csv(ROOT / 'v2_scan_full_pool.csv', infer_schema_length=20000)
    pool_ids = [int(x) for x in pool['source_id'].drop_nulls().to_list()]
    print(f'v2 pool source IDs: {len(pool_ids)}')

    chunks = []
    for i in range(0, len(pool_ids), 3000):
        sub = pool_ids[i:i+3000]
        ids = ','.join(str(x) for x in sub)
        q = f"""
        SELECT nss.source_id, nss.nss_solution_type, nss.period, nss.eccentricity,
               nss.significance, nss.semi_amplitude_primary, nss.semi_amplitude_secondary,
               nss.mass_ratio
        FROM gaiadr3.nss_two_body_orbit AS nss
        WHERE nss.source_id IN ({ids})
          AND nss.nss_solution_type IN ('SB2','SB2C')
        """
        try:
            df = Gaia.launch_job_async(q).get_results().to_pandas()
            chunks.append(df)
        except Exception as e:
            print(f'chunk {i}: ERR {type(e).__name__}: {str(e)[:80]}')

    import pandas as pd
    if chunks:
        all_sb2 = pd.concat(chunks, ignore_index=True)
    else:
        all_sb2 = pd.DataFrame()
    print(f'SB2/SB2C matches in v2 pool: {len(all_sb2)}')

    if len(all_sb2):
        all_sb2['source_id'] = all_sb2['source_id'].astype('int64')
        # Estimate M_2 from K1, K2, P, e (M_1 + M_2) sin³i = (P/2πG)*(K1+K2)³(1-e²)^1.5
        import math
        Msun = 1.989e30
        G_si = 6.674e-11
        rows = []
        for _, r in all_sb2.iterrows():
            P_s = (r.get('period') or 0) * 86400
            e = r.get('eccentricity') or 0
            K1 = r.get('semi_amplitude_primary') or 0
            K2 = r.get('semi_amplitude_secondary') or 0
            q_ratio = r.get('mass_ratio') or 0
            if P_s > 0 and K1 > 0 and K2 > 0:
                Mtot_sini3 = (P_s / (2*math.pi*G_si)) * ((K1+K2)*1000)**3 * (1-e*e)**1.5 / Msun
                M_2_sini3 = Mtot_sini3 * K1 / (K1 + K2)
                M_1_sini3 = Mtot_sini3 - M_2_sini3
            else:
                M_2_sini3 = None
                M_1_sini3 = None
            rows.append({
                'source_id': int(r['source_id']),
                'nss_solution_type': r['nss_solution_type'],
                'P_d': r.get('period'), 'e': r.get('eccentricity'),
                'sig': r.get('significance'),
                'K1': K1, 'K2': K2, 'q': q_ratio,
                'M1_sini3': M_1_sini3,
                'M2_sini3': M_2_sini3,
                'M2_MJ_sini3': (M_2_sini3 * 1047.348) if M_2_sini3 else None,
            })
        out = pl.DataFrame(rows)
        out_path = ROOT / 'data' / 'intermediate' / 'sb2_negative_recovery.csv'
        out.write_csv(out_path)
        print(f'Saved -> {out_path}')

        # Stats
        print('\nM_2 sin³i distribution (Msun):')
        if 'M2_sini3' in out.columns:
            print(out.select(pl.col('M2_sini3').drop_nulls()).describe().to_pandas().to_string())
        print(f'\nWith M2 > 80 MJ (stellar): {sum(1 for r in rows if r["M2_sini3"] and r["M2_sini3"] > 80/1047.348)}')

    return 0


if __name__ == '__main__':
    sys.exit(main())
