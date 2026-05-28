"""Reconstruct v1.18 headline = v1.17.0 26 candidates + 6 widened-66 Tier-2.

The 6 widened-66 promotions all have:
  - HD names, TENTATIVE_SB1_WIDENED_TYCHO_CORROB_TIER2 status
  - M2_marg <= 25 MJ, Tycho-Gaia corroborated, RUWE<2
  - tycho_gaia_corrob_purity = 0.72

Also adds companion_class column = 'substellar_BD' for all 32 rows.
"""
from __future__ import annotations
import sys
from pathlib import Path
import polars as pl

ROOT = Path('/Users/legbatterij/claude_projects/gaia-recovered-2026-05-27')


def main():
    nov = pl.read_csv(ROOT / 'novelty_candidates.csv')
    print(f'v1.17.0 base: {len(nov)} candidates')

    # 6 widened-66 Tier-2 promotions from chat. Use None (not '?') for unknown fields.
    NEW = [
        ('HD 151672', None, None, 7.86, None, None, 'filter_survivor_widened66_tier2',
         'nss_orbital', '358', 10, 9, 11,
         None, None, None, 1.09, None, None, 0.95, '35/35',
         'TENTATIVE_SB1_WIDENED_TYCHO_CORROB_TIER2', 'Tycho-Gaia chi2=7.0',
         'medium', 0.9, 0.85, 0.77, 'substellar_BD'),
        ('HD 15405', None, None, 9.13, None, None, 'filter_survivor_widened66_tier2',
         'nss_orbital', '11.6', 14, 12, 16,
         None, None, None, 1.59, None, None, 0.92, '35/35',
         'TENTATIVE_SB1_WIDENED_TYCHO_CORROB_TIER2', 'Tycho-Gaia chi2=14.6; FLAG K-giant',
         'medium', 0.85, 0.8, 0.7, 'substellar_BD'),
        ('HD 206933', None, None, 8.24, None, None, 'filter_survivor_widened66_tier2',
         'nss_orbital', '13.6', 16, 14, 18,
         None, None, None, 1.70, None, None, 0.91, '35/35',
         'TENTATIVE_SB1_WIDENED_TYCHO_CORROB_TIER2', 'Tycho-Gaia chi2=14.0',
         'medium', 0.85, 0.8, 0.7, 'substellar_BD'),
        ('HD 71160', None, None, 7.46, None, None, 'filter_survivor_widened66_tier2',
         'nss_orbital', '507', 17, 15, 19,
         None, None, None, 1.09, None, None, 0.93, '35/35',
         'TENTATIVE_SB1_WIDENED_TYCHO_CORROB_TIER2', 'Tycho-Gaia chi2=5.7',
         'medium', 0.9, 0.85, 0.77, 'substellar_BD'),
        ('HD 194390', None, None, 7.52, None, None, 'filter_survivor_widened66_tier2',
         'nss_orbital', '63', 19, 17, 21,
         None, None, None, 1.52, None, None, 0.91, '35/35',
         'TENTATIVE_SB1_WIDENED_TYCHO_CORROB_TIER2', 'Tycho-Gaia chi2=14.2',
         'medium', 0.85, 0.8, 0.7, 'substellar_BD'),
        ('HD 53924', None, None, 7.50, None, None, 'filter_survivor_widened66_tier2',
         'nss_orbital', '15.7', 20, 18, 22,
         None, None, None, 0.88, None, None, 0.93, '35/35',
         'TENTATIVE_SB1_WIDENED_TYCHO_CORROB_TIER2', 'Tycho-Gaia chi2=6.3; RUWE=0.88 below baseline',
         'low', 0.92, 0.87, 0.80, 'substellar_BD'),
    ]
    # Add companion_class column to original
    nov = nov.with_columns(pl.lit('substellar_BD').alias('companion_class'))

    # Build new rows with matching schema
    schema_cols = nov.columns
    new_rows = []
    for tup in NEW:
        row = dict(zip([
            'name','hip','gaia_dr3_source_id','vmag','spectral_type','distance_pc',
            'category','nss_pool','p_orb_d','m2_mj_marginalized_median',
            'm2_marginalized_1sigma_lo','m2_marginalized_1sigma_hi',
            'hgca_snrpma','kervella_m2_5au_mj','kervella_snrpma',
            'penoyre_ruwe_value','gaia_rv_amplitude_robust_kms','archival_rv_summary',
            'p_substellar_marginalized','filters_passed','status_tentative_only',
            'notes','fp_risk_tier','P_real_companion','P_substellar_given_real',
            'P_real_substellar','companion_class'], tup))
        # fill missing schema cols
        row_full = {c: row.get(c) for c in schema_cols}
        new_rows.append(row_full)
    new_df = pl.DataFrame(new_rows, schema=nov.schema)
    v118 = pl.concat([nov, new_df])
    v118.write_csv(ROOT / 'novelty_candidates_v1.18.csv')
    print(f'v1.18: {len(v118)} candidates ({len(NEW)} widened-66 Tier-2 added)')
    print('\nNew Tier-2 rows:')
    print(new_df.select(['name','vmag','p_orb_d','m2_mj_marginalized_median',
                          'penoyre_ruwe_value','status_tentative_only']).to_pandas().to_string())
    return 0


if __name__ == '__main__':
    sys.exit(main())
