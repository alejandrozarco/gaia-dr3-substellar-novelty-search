"""Supervised classifier fine-tuned on the recovered known objects.

Training labels (from SIMBAD recoveries):
  POSITIVE_BD_PLANET: candidates that resolved to known exoplanets / BDs
    in the literature (HD 81040, HD 111232, plus any BD candidate with
    HD/HIP name and substellar/PM* otype).
  K_GIANT_FP: candidates with spectral type III/IV/V K class -> the
    chromatic photocentric bias FP class identified from 4 UMi.
  REAL_BH_CANDIDATE: 4 UMi is excluded; candidates with subgiant/dwarf
    F/G hosts in the BH/NS class (HD 207141, TYC 1363, TYC 1299 etc).
  STELLAR_BINARY: SB2/SB2C-flagged sources from the cascade Filter #29.
  UNSTUDIED: source_id with no SIMBAD entry / no HD/HIP designation.

Features (all from Gaia DR3):
  P_d, e, significance, a_phot_mas, parallax, G, bp_rp, ruwe,
  M1_msun, fM_msun, M2_msun, in_sb2, rv_amplitude_robust,
  rv_chisq_pvalue, Teff, logg, cbias_risk

Target: binary "is_K_giant_FP" — first cut at automating the Filter #30
generalization beyond the simple BP-RP / log g thresholds.

Output: trained model + predictions for the 212+ unstudied candidates.
"""
from __future__ import annotations
import sys, warnings, pickle, json
warnings.filterwarnings('ignore')
from pathlib import Path
import polars as pl
import numpy as np

ROOT = Path('/Users/legbatterij/claude_projects/gaia-recovered-2026-05-27')


def load_labeled_data():
    """Merge hidden_objects + ns_recoveries_expanded into one labeled set."""
    hidden = pl.read_csv(ROOT / 'hidden_objects_2026_05_27.csv',
                        infer_schema_length=2000)
    ns_exp_path = ROOT / 'ns_recoveries_expanded_2026_05_27.csv'
    if ns_exp_path.exists():
        ns_exp = pl.read_csv(ns_exp_path, infer_schema_length=2000)
        # Project to common columns
        # ns_exp has: source_id, sig, P_d, M2_msun, G, bp_rp, ruwe, cbias_risk,
        #             main_id, otype, sp_type, has_HD, has_HIP, sp_class
        # hidden has: cls, source_id, sig, P_d, M2_msun, G, bp_rp, simbad_main,
        #             otype, sp_type, has_HD, has_HIP, has_GJ, has_TYC, named_ids
        # Add cls='NS' to ns_exp and unify columns
        ns_exp = ns_exp.with_columns([
            pl.lit('NS').alias('cls'),
            pl.col('main_id').alias('simbad_main'),
        ])
        # Compute sp_class for hidden
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
        hidden = hidden.with_columns(
            pl.col('sp_type').map_elements(cls_sp, return_dtype=pl.String).alias('sp_class')
        )
        # Unify naming: both have main_id field
        if 'simbad_main' in hidden.columns:
            hidden = hidden.rename({'simbad_main': 'main_id'})
        # Common columns in both frames
        common = ['source_id','sig','P_d','M2_msun','G','bp_rp',
                  'main_id','otype','sp_type','has_HD','has_HIP','sp_class','cls']
        h_keep = [c for c in common if c in hidden.columns]
        n_keep = [c for c in common if c in ns_exp.columns]
        common_both = [c for c in common if c in h_keep and c in n_keep]
        return pl.concat([
            hidden.select(common_both),
            ns_exp.select(common_both),
        ])
    return hidden


def build_labels(labeled, hunt):
    """Join hunt features onto labeled set + assign target label."""
    labeled = labeled.with_columns(pl.col('source_id').cast(pl.Int64))
    hunt = hunt.with_columns(pl.col('source_id').cast(pl.Int64))
    feats = hunt.select([
        'source_id', 'parallax', 'ruwe', 'a_phot_mas', 'fM_msun',
        'in_sb2', 'rv_amplitude_robust', 'rv_chisq_pvalue',
        'Teff', 'logg', 'cbias_risk', 'filter31', 'M1_msun',
    ])
    df = labeled.join(feats, on='source_id', how='left')
    # Target: is this a K-giant FP candidate?
    df = df.with_columns(
        (pl.col('sp_class') == 'K_giant_FP').alias('is_K_giant_FP')
    )
    return df


def main():
    labeled = load_labeled_data()
    hunt = pl.read_parquet(ROOT / 'data' / 'derived' / 'main_hunt_derived.parquet')
    df = build_labels(labeled, hunt)
    print(f'Labeled set: {len(df)} candidates joined with hunt features')

    print('\nLabel distribution by sp_class:')
    print(df.group_by('sp_class').len().sort('len', descending=True).to_pandas().to_string(index=False))

    print(f'\nTarget breakdown:')
    print(f'  is_K_giant_FP=True : {df["is_K_giant_FP"].sum()}')
    print(f'  is_K_giant_FP=False: {(~df["is_K_giant_FP"]).sum()}')

    # Filter #30 (cbias_risk) confusion matrix
    print('\nFilter #30 (cbias_risk) vs ground-truth K_giant_FP label:')
    df_known = df.filter(pl.col('sp_class') != 'no_simbad')
    if 'cbias_risk' in df_known.columns:
        cm = df_known.group_by(['is_K_giant_FP', 'cbias_risk']).len()
        print(cm.to_pandas().to_string(index=False))
        TP = df_known.filter(pl.col('is_K_giant_FP') & pl.col('cbias_risk')).height
        FN = df_known.filter(pl.col('is_K_giant_FP') & ~pl.col('cbias_risk')).height
        FP = df_known.filter(~pl.col('is_K_giant_FP') & pl.col('cbias_risk')).height
        TN = df_known.filter(~pl.col('is_K_giant_FP') & ~pl.col('cbias_risk')).height
        if TP + FN > 0:
            recall = TP / (TP + FN)
            print(f'\nFilter #30 K-giant-FP recall: {recall:.3f} (TP={TP}, FN={FN})')
        if TP + FP > 0:
            precision = TP / (TP + FP)
            print(f'Filter #30 precision: {precision:.3f}')

    # Train supervised classifier
    print('\n=== Supervised classifier (RandomForest) ===')
    features = ['P_d', 'M2_msun', 'G', 'bp_rp', 'parallax', 'ruwe',
                'Teff', 'logg', 'M1_msun', 'fM_msun', 'a_phot_mas']
    feat_df = df.filter(pl.col('sp_class') != 'no_simbad').select(features + ['is_K_giant_FP'])
    feat_df = feat_df.with_columns([
        pl.col(c).cast(pl.Float64, strict=False).fill_null(-99.0)
        for c in features
    ])
    print(f'Training set: {len(feat_df)} labeled candidates')

    try:
        from sklearn.ensemble import RandomForestClassifier
        from sklearn.model_selection import StratifiedKFold, cross_val_predict
        from sklearn.metrics import classification_report
    except ImportError:
        print('sklearn not available'); return 0

    X = feat_df.select(features).to_numpy()
    y = feat_df['is_K_giant_FP'].to_numpy()
    if y.sum() < 5 or (~y).sum() < 5:
        print(f'Insufficient labels for CV: {y.sum()} positive, {(~y).sum()} negative')
        return 0

    clf = RandomForestClassifier(n_estimators=300, max_depth=8, n_jobs=-1,
                                    random_state=7, class_weight='balanced')
    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=7)
    yp = cross_val_predict(clf, X, y, cv=cv, n_jobs=-1)
    print('\nClassification report (5-fold CV):')
    print(classification_report(y, yp, digits=3, target_names=['not_K_giant_FP', 'K_giant_FP']))

    # Train on full data + feature importances
    clf.fit(X, y)
    imp = sorted(zip(features, clf.feature_importances_), key=lambda kv: -kv[1])
    print('\nFeature importances:')
    for f, v in imp:
        print(f'  {f:<18} {v:.4f}  {"#"*int(v*60)}')

    # Predict on UNSTUDIED candidates
    unstudied = df.filter(pl.col('sp_class') == 'no_simbad')
    print(f'\nApplying to {len(unstudied)} unstudied candidates...')
    X_u = unstudied.select(features).with_columns([
        pl.col(c).cast(pl.Float64, strict=False).fill_null(-99.0)
        for c in features
    ]).to_numpy()
    if len(X_u) > 0:
        probs = clf.predict_proba(X_u)[:, 1]  # P(K_giant_FP)
        unstudied = unstudied.with_columns(pl.Series('p_K_giant_FP_pred', probs))
        # Sort by predicted P(not FP) = real-candidate probability
        unstudied = unstudied.sort('p_K_giant_FP_pred')
        print(f'\nTop 15 unstudied candidates LEAST LIKELY to be K-giant FPs (real-candidate ranked):')
        keep = ['source_id', 'cls', 'sig', 'P_d', 'M2_msun', 'G', 'bp_rp', 'ruwe',
                'cbias_risk', 'p_K_giant_FP_pred']
        keep = [k for k in keep if k in unstudied.columns]
        print(unstudied.head(15).select(keep).to_pandas().to_string(index=False))
        unstudied.write_csv(ROOT / 'finetune_predictions_2026_05_27.csv')
        print(f'\nSaved to finetune_predictions_2026_05_27.csv ({len(unstudied)} rows)')

    # Persist model
    with (ROOT / 'finetune_kgiantFP_classifier.pkl').open('wb') as f:
        pickle.dump({'model': clf, 'features': features}, f)
    print('Model saved to finetune_kgiantFP_classifier.pkl')


if __name__ == '__main__':
    sys.exit(main() or 0)
