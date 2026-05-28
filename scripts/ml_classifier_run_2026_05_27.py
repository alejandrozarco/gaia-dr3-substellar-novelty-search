"""ML companion classifier — Experiment 1: held-out M_2 + fM features.

Tests whether the cascade's class label is recoverable from secondary
features (P, e, sig, a_phot, parallax, G, BP-RP, RUWE, M_1, in_sb2) ALONE,
without M_2/fM. If accuracy ≈ 100%, the cascade is doing pure threshold-
on-M_2. If accuracy < 100%, secondary features carry independent signal.

Output: ml_classifier_run_2026_05_27.log + console
"""
from __future__ import annotations
import sys, warnings
warnings.filterwarnings('ignore')
from pathlib import Path
import polars as pl
import numpy as np

ROOT = Path('/Users/legbatterij/claude_projects/gaia-recovered-2026-05-27')


def main():
    hunt_path = ROOT / 'data' / 'intermediate' / 'companions_hunt_all_classes_2026_05_18.csv'
    if not hunt_path.exists():
        print(f'Hunt CSV missing: {hunt_path}\nRun companions_hunt_all_mass_classes_2026_05_18.py first.')
        return 1
    df = pl.read_csv(hunt_path)
    print(f'Hunt pool: {len(df)}')
    print('\nClass distribution:')
    print(df.group_by('class').len().sort('len', descending=True).to_pandas().to_string(index=False))

    print('\n=== EXPERIMENT 1: held-out M_2/fM ===')
    feats = ['P_d', 'e', 'significance', 'a_phot_mas', 'parallax', 'G',
             'bp_rp', 'ruwe', 'M1_msun', 'in_sb2']
    X = df.select(feats).with_columns([
        pl.col(c).cast(pl.Float64, strict=False).fill_null(-99.0)
        if df[c].dtype != pl.Boolean else pl.col(c).cast(pl.Int8)
        for c in feats
    ])
    Xa = X.to_numpy()
    ya = df['class'].to_numpy()

    rng = np.random.RandomState(7)
    if len(Xa) > 10000:
        idx = rng.choice(len(Xa), 10000, replace=False)
        Xa = Xa[idx]; ya = ya[idx]

    classes, counts = np.unique(ya, return_counts=True)
    keep = {c for c, n in zip(classes, counts) if n >= 10}
    mask = np.isin(ya, list(keep))
    Xa = Xa[mask]; ya = ya[mask]
    print(f'Training set: {len(Xa)} rows, classes: {sorted(keep)}')

    try:
        from sklearn.ensemble import RandomForestClassifier
        from sklearn.model_selection import StratifiedKFold, cross_val_predict
        from sklearn.metrics import classification_report, confusion_matrix
    except ImportError:
        print('sklearn not available'); return 0

    clf = RandomForestClassifier(n_estimators=300, max_depth=10,
                                    n_jobs=-1, random_state=7)
    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=7)
    yp = cross_val_predict(clf, Xa, ya, cv=cv, n_jobs=-1)

    print('\nClassification report (M2/fM held out):')
    print(classification_report(ya, yp, digits=3, zero_division=0))
    print('\nConfusion matrix (rows=true, cols=pred):')
    sorted_classes = sorted(set(ya))
    cm = confusion_matrix(ya, yp, labels=sorted_classes)
    print(f'  {"":28} {" ".join(c[:12].rjust(12) for c in sorted_classes)}')
    for c, row in zip(sorted_classes, cm):
        print(f'  {c:<28} {" ".join(str(x).rjust(12) for x in row)}')

    clf.fit(Xa, ya)
    imp = sorted(zip(feats, clf.feature_importances_), key=lambda kv: -kv[1])
    print('\nFeature importances (without M_2/fM):')
    for f, v in imp:
        print(f'  {f:<20} {v:.4f}  {"#" * int(v*80)}')

    return 0


if __name__ == '__main__':
    sys.exit(main())
