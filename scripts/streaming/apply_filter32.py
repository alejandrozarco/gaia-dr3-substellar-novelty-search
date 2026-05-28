"""Post-process: apply Filter #32 (joint astrometric + RV consistency) to the
existing main_hunt_derived.parquet without re-running the hunt.

Filter #32: For each candidate, compute K_pred(M_2_astrom, i=90°) from the
orbital parameters and cascade M_2. If K_obs > K_pred(i=90°), the
candidate is REJECTED because K_obs is dominated by non-orbital noise
(stellar pulsations, RVS systematics, rotation) and the binary cannot
physically produce that K_obs at the cascade's M_2.

Updates main_hunt_derived.parquet IN PLACE with new columns:
  filter32 ∈ {'PASS', 'FAIL', 'NO_DATA'}
  sini_implied (= K_obs / K_pred(i=90°))

Also recomputes the defensible-after-all-filters list and writes new
defensible_*_post32.parquet artifacts.
"""
from __future__ import annotations
import math, sys, warnings
warnings.filterwarnings('ignore')
from pathlib import Path
import polars as pl

ROOT = Path('/Users/legbatterij/claude_projects/gaia-recovered-2026-05-27')


def K1_kms_safe(P_d, e, M1, M2, sini):
    if P_d <= 0 or e >= 1.0 or M1 <= 0 or M2 <= 0:
        return 0.0
    P_s = P_d * 86400.0
    num = (2 * math.pi * 6.6743e-11 / P_s) ** (1/3) * (M2 * 1.989e30) * sini
    den = ((M1 + M2) * 1.989e30) ** (2/3) * math.sqrt(1 - e * e)
    return (num / den) / 1000.0


def apply_filter32_row(P_d, e, M1, M2, K_obs):
    if K_obs is None or K_obs <= 0:
        return ('NO_DATA', None, None)
    K_max = K1_kms_safe(P_d, e, M1, M2, 1.0)
    if K_max <= 0:
        return ('NO_DATA', None, K_max)
    sini = K_obs / K_max
    status = 'PASS' if sini <= 1.05 else 'FAIL'
    return (status, round(sini, 3), round(K_max, 2))


def main():
    p = ROOT / 'data' / 'derived' / 'main_hunt_derived.parquet'
    if not p.exists():
        print(f'No derived parquet at {p}', file=sys.stderr)
        return 1

    df = pl.read_parquet(p)
    print(f'Loaded {len(df)} rows from {p.name}')

    # Compute filter32 row-by-row in pandas for the math (polars-friendly result)
    import pandas as pd
    pdf = df.to_pandas()
    f32, sini, k90 = [], [], []
    for _, r in pdf.iterrows():
        K_obs = r.get('rv_amplitude_robust')
        P_d = r.get('P_d')
        e = r.get('e') if r.get('e') is not None and not pd.isna(r.get('e')) else 0.0
        M1 = r.get('M1_msun') if r.get('M1_msun') is not None else 1.0
        M2 = r.get('M2_msun')
        if K_obs is None or pd.isna(K_obs) or M2 is None or P_d is None or M1 <= 0:
            f32.append('NO_DATA'); sini.append(None); k90.append(None); continue
        status, s, K_max = apply_filter32_row(float(P_d), float(e), float(M1), float(M2), float(K_obs))
        f32.append(status); sini.append(s); k90.append(K_max)
    pdf['filter32'] = f32
    pdf['sini_implied'] = sini
    pdf['K_pred_i90'] = k90

    out = pl.from_pandas(pdf)
    out.write_parquet(p)
    print(f'Wrote {len(out)} rows back to {p.name}')

    # Filter #32 stats
    print('\n=== Filter #32 statistics ===')
    f32_dist = out.group_by('filter32').len().sort('len', descending=True)
    print(f32_dist.to_pandas().to_string(index=False))

    # By class
    print('\n=== Filter #32 by class ===')
    cb = out.group_by(['class', 'filter32']).len().sort(['class', 'filter32'])
    print(cb.to_pandas().to_string(index=False))

    # ALL FILTERS PASS (FINAL survivors)
    print('\n=== Survivors of ALL 4 filters (Filter #29 + #30 + #31 + #32) ===')
    survivors = out.filter(
        (pl.col('class').is_in(['dormant_BH_candidate', 'dormant_NS_candidate'])) &
        (~pl.col('in_sb2')) &
        (~pl.col('cbias_risk')) &
        (pl.col('filter31') == 'PASS') &
        (pl.col('filter32') == 'PASS')
    ).sort('significance', descending=True)
    print(f'Total: {len(survivors)} (BH + NS combined)')
    survivors_bh = survivors.filter(pl.col('class') == 'dormant_BH_candidate')
    survivors_ns = survivors.filter(pl.col('class') == 'dormant_NS_candidate')
    print(f'  Dormant BH survivors: {len(survivors_bh)}')
    print(f'  Dormant NS survivors: {len(survivors_ns)}')

    if len(survivors_bh):
        print('\n=== Top 20 BH survivors (all 4 filters PASS) ===')
        keep = ['source_id', 'P_d', 'e', 'significance', 'M2_msun', 'G', 'bp_rp',
                'ruwe', 'rv_amplitude_robust', 'sini_implied', 'K_pred_i90',
                'Teff', 'logg', 'M1_msun']
        keep = [k for k in keep if k in survivors_bh.columns]
        print(survivors_bh.head(20).select(keep).to_pandas().to_string(index=False))
        survivors_bh.write_parquet(ROOT / 'data' / 'derived' / 'main_BH_all_filters_pass.parquet')
        survivors_bh.write_csv(ROOT / 'data' / 'derived' / 'main_BH_all_filters_pass.csv')

    if len(survivors_ns):
        print('\n=== Top 20 NS survivors (all 4 filters PASS) ===')
        keep = ['source_id', 'P_d', 'e', 'significance', 'M2_msun', 'G', 'bp_rp',
                'ruwe', 'rv_amplitude_robust', 'sini_implied', 'K_pred_i90',
                'Teff', 'logg', 'M1_msun']
        keep = [k for k in keep if k in survivors_ns.columns]
        print(survivors_ns.head(20).select(keep).to_pandas().to_string(index=False))
        survivors_ns.write_parquet(ROOT / 'data' / 'derived' / 'main_NS_all_filters_pass.parquet')
        survivors_ns.write_csv(ROOT / 'data' / 'derived' / 'main_NS_all_filters_pass.csv')

    # FALSE-positive class that Filter #32 catches: previously-defensible BH/NS that fail #32
    print('\n=== Filter #32 demotions (previously defensible, now flagged) ===')
    demoted_bh = out.filter(
        (pl.col('class') == 'dormant_BH_candidate') &
        (~pl.col('in_sb2')) & (~pl.col('cbias_risk')) &
        (pl.col('filter31') == 'PASS') &
        (pl.col('filter32') == 'FAIL')
    ).sort('significance', descending=True)
    demoted_ns = out.filter(
        (pl.col('class') == 'dormant_NS_candidate') &
        (~pl.col('in_sb2')) & (~pl.col('cbias_risk')) &
        (pl.col('filter31') == 'PASS') &
        (pl.col('filter32') == 'FAIL')
    ).sort('significance', descending=True)
    print(f'BH demoted by Filter #32: {len(demoted_bh)}')
    print(f'NS demoted by Filter #32: {len(demoted_ns)}')

    if len(demoted_ns):
        print('\nTop 10 NS demoted by Filter #32 (these were previously "defensible NS"):')
        keep = ['source_id', 'significance', 'M2_msun', 'G', 'bp_rp', 'ruwe',
                'rv_amplitude_robust', 'sini_implied', 'K_pred_i90', 'Teff', 'logg']
        keep = [k for k in keep if k in demoted_ns.columns]
        print(demoted_ns.head(10).select(keep).to_pandas().to_string(index=False))
        demoted_ns.write_csv(ROOT / 'data' / 'derived' / 'demoted_by_filter32_NS.csv')

    return 0


if __name__ == '__main__':
    sys.exit(main())
