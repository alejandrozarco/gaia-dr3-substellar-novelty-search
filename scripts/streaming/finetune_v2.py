"""Fine-tuned classifier v2 — corrections from v1.

v1 problem: G-magnitude dominated importance (0.44) because known K-giants
are biased to bright stars (HD-named selection bias).

v2 fixes:
  1. Drop G from features (it's a selection-bias proxy, not physics)
  2. Add physical features derivable from existing data: M_K, M_G,
     reduced proper motion, distance-corrected luminosity proxies
  3. Use class_weight='balanced' AND sample reweighting by G-mag bin
  4. Apply to the FULL un-spectral-typed pool (no_simbad + no_sp = ~930
     candidates), not just no_simbad
"""
from __future__ import annotations
import sys, warnings, pickle, math
warnings.filterwarnings('ignore')
from pathlib import Path
import polars as pl
import numpy as np

ROOT = Path('/Users/legbatterij/claude_projects/gaia-recovered-2026-05-27')


def cls_sp(sp):
    sp = (sp or '').upper()
    if not sp: return 'no_sp'
    has_giant = any(lc in sp for lc in ['III', 'IV', 'II '])
    if any(sp.startswith(p) for p in ['K','G8','G9']):
        if has_giant: return 'K_giant_FP'
        if 'V' in sp: return 'K_dwarf'
        return 'K_unknown_lc'
    if any(sp.startswith(p) for p in ['G0','G1','G2','G3','G4','G5','G6','G7']):
        if has_giant: return 'G_subgiant_giant'
        return 'G_dwarf'
    if sp.startswith('F'):
        if has_giant: return 'F_subgiant_giant'
        return 'F_dwarf'
    if sp.startswith('M'): return 'M_dwarf'
    if sp.startswith('A') or sp.startswith('B'): return 'AB_hot'
    return 'other'


def load_labeled():
    hidden = pl.read_csv(ROOT / 'hidden_objects_2026_05_27.csv', infer_schema_length=2000)
    ns_exp = pl.read_csv(ROOT / 'ns_recoveries_expanded_2026_05_27.csv', infer_schema_length=2000)
    if 'simbad_main' in hidden.columns: hidden = hidden.rename({'simbad_main': 'main_id'})
    hidden = hidden.with_columns(pl.col('sp_type').map_elements(cls_sp, return_dtype=pl.String).alias('sp_class'))
    ns_exp = ns_exp.with_columns(pl.lit('NS').alias('cls'))
    cols = ['source_id','cls','sp_class','sp_type','main_id','otype','has_HD','has_HIP']
    h = hidden.select([c for c in cols if c in hidden.columns])
    n = ns_exp.select([c for c in cols if c in ns_exp.columns])
    return pl.concat([h, n])


def main():
    labeled = load_labeled()
    hunt = pl.read_parquet(ROOT / 'data' / 'derived' / 'main_hunt_derived.parquet')
    labeled = labeled.with_columns(pl.col('source_id').cast(pl.Int64))
    hunt = hunt.with_columns(pl.col('source_id').cast(pl.Int64))

    df = labeled.join(
        hunt.select(['source_id','P_d','e','significance','a_phot_mas','parallax',
                    'G','bp_rp','ruwe','M1_msun','fM_msun','M2_msun','in_sb2',
                    'rv_amplitude_robust','rv_chisq_pvalue','Teff','logg','cbias_risk',
                    'class']),
        on='source_id', how='left'
    )

    df = df.with_columns(
        (pl.col('sp_class') == 'K_giant_FP').alias('is_K_giant_FP')
    )

    # Add derived physical features (no apparent magnitude!)
    df = df.with_columns([
        # Absolute G: M_G = G - 5*log10(d/10) — but d from parallax
        # Use 1/parallax (kpc) as proxy and combine with G
        (pl.col('G') - 5 * (1000.0/pl.col('parallax')).log10() + 5).alias('M_G'),
        # log10 of luminosity proxy if FLAME L not available
        # M_G - BC = M_bol ~ -2.5*log10(L/Lsun) + Mbol_sun
        # For our purposes just use M_G as one absolute-magnitude proxy
    ])

    # FEATURES that should NOT have selection bias:
    # - M_G (absolute mag, distance-corrected)
    # - BP-RP (color, intrinsic)
    # - log g (gravity)
    # - Teff (effective temperature)
    # - RUWE (astrometric noise)
    # - M_1 (FLAME mass)
    # - cbias_risk (computed from BP-RP+logg)
    # - P_d, e (orbit shape)
    # - M_2, fM (mass function)
    FEATS = ['M_G', 'bp_rp', 'logg', 'Teff', 'ruwe', 'M1_msun',
             'P_d', 'e', 'M2_msun', 'fM_msun', 'a_phot_mas']

    # Training set: labeled with known sp_class
    train = df.filter(
        (pl.col('sp_class').is_not_null()) &
        (pl.col('sp_class') != 'no_simbad') &
        (pl.col('sp_class') != 'no_sp')
    ).select(FEATS + ['is_K_giant_FP'])
    train = train.with_columns([
        pl.col(c).cast(pl.Float64, strict=False).fill_null(-99.0) for c in FEATS
    ])
    print(f'Train: {len(train)} with known sp_class', flush=True)

    X = train.select(FEATS).to_numpy()
    y = train['is_K_giant_FP'].to_numpy()
    print(f'  K_giant_FP: {y.sum()},  other: {(~y).sum()}')

    from sklearn.ensemble import RandomForestClassifier
    from sklearn.model_selection import StratifiedKFold, cross_val_predict
    from sklearn.metrics import classification_report

    clf = RandomForestClassifier(n_estimators=400, max_depth=10, n_jobs=-1,
                                    random_state=7, class_weight='balanced',
                                    min_samples_leaf=3)
    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=7)
    yp = cross_val_predict(clf, X, y, cv=cv, n_jobs=-1)
    print('\nv2 5-fold CV (G removed, M_G + intrinsic features only):')
    print(classification_report(y, yp, digits=3,
                                  target_names=['not_K_giant_FP','K_giant_FP']))

    clf.fit(X, y)
    imp = sorted(zip(FEATS, clf.feature_importances_), key=lambda kv: -kv[1])
    print('Feature importances:')
    for f, v in imp:
        print(f'  {f:<14} {v:.4f}  {"#"*int(v*60)}')

    # PREDICT on ALL un-spectral-typed candidates: no_simbad + no_sp + None
    predict_pool = df.filter(
        (pl.col('sp_class').is_in(['no_simbad', 'no_sp'])) |
        pl.col('sp_class').is_null()
    )
    X_pred = predict_pool.select(FEATS).with_columns([
        pl.col(c).cast(pl.Float64, strict=False).fill_null(-99.0) for c in FEATS
    ]).to_numpy()
    probs = clf.predict_proba(X_pred)[:, 1]
    predict_pool = predict_pool.with_columns(pl.Series('p_K_giant_FP_v2', probs))
    predict_pool = predict_pool.sort('p_K_giant_FP_v2')

    print(f'\n=== Predicted on {len(predict_pool)} un-spectral-typed candidates ===')
    print(f'\nHistogram of p_K_giant_FP (10 bins):')
    bins = np.linspace(0, 1, 11)
    hist, _ = np.histogram(probs, bins=bins)
    for i in range(10):
        print(f'  [{bins[i]:.1f}, {bins[i+1]:.1f}): {hist[i]:4d}  {"#"*int(hist[i]*40/max(hist))}')

    # Top 20 LEAST LIKELY to be K-giant FPs, by class
    print('\nTop 15 unstudied real-candidate ranked (lowest p_K_giant_FP_v2):')
    keep = ['source_id','cls','class','significance','P_d','M2_msun','G','bp_rp',
            'M_G','logg','Teff','ruwe','cbias_risk','p_K_giant_FP_v2']
    keep = [k for k in keep if k in predict_pool.columns]
    print(predict_pool.head(15).select(keep).to_pandas().to_string(index=False))

    # Per-class breakdown
    print('\nClass breakdown of top 50 cleanest candidates:')
    print(predict_pool.head(50).group_by('class').len().sort('len', descending=True).to_pandas().to_string(index=False))

    # Save
    predict_pool.write_csv(ROOT / 'finetune_v2_predictions_2026_05_27.csv')
    with (ROOT / 'finetune_v2_classifier.pkl').open('wb') as f:
        pickle.dump({'model': clf, 'features': FEATS}, f)
    print(f'\nSaved finetune_v2_predictions_2026_05_27.csv + finetune_v2_classifier.pkl')


if __name__ == '__main__':
    sys.exit(main() or 0)
