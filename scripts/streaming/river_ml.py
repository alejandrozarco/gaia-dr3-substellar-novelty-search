"""River-based online ML classifier — learns from each new chunk row.

Target: cascade-derived companion class (multi-class).
Features: held out from M_2 and fM (the cascade's defining quantities) —
this is the same experiment we did with sklearn RandomForest earlier, now
online. The BD class recall = 0.028 finding (cascade BD is essentially
M_2-threshold-only) should reproduce as more data flows in; we can watch
the per-class accuracy converge live.

Why River and not sklearn warm_start:
  - True streaming: model.learn_one(x, y) per row, no batch refit
  - Adaptive RF rebuilds individual trees as concepts drift
  - Memory: stays O(n_trees * tree_size), not O(N_examples)

Saves checkpoints to data/derived/{mode}_river_model.pkl every N learns
and writes accuracy stats to data/derived/{mode}_ml_stats.json.
"""
from __future__ import annotations
import json, pickle, warnings
warnings.filterwarnings('ignore')
from pathlib import Path
from datetime import datetime, timezone

import pandas as pd
from river import forest, metrics, preprocessing, compose

ROOT = Path('/Users/legbatterij/claude_projects/gaia-recovered-2026-05-27')
DERIVED = ROOT / 'data' / 'derived'

# Features for the held-out-M_2 multi-class problem
FEATS = ['P_d', 'e', 'significance', 'a_phot_mas', 'parallax',
         'G', 'bp_rp', 'ruwe', 'M1_msun', 'in_sb2']


def _row_to_x(row) -> dict:
    """Pandas row -> River feature dict, NaN-safe."""
    x = {}
    for f in FEATS:
        v = row.get(f)
        if v is None or (isinstance(v, float) and (v != v)):  # NaN check
            x[f] = -99.0
        else:
            x[f] = float(v) if not isinstance(v, bool) else (1.0 if v else 0.0)
    return x


class RiverClassifier:
    def __init__(self, mode: str, n_models: int = 10, max_features: int = 5,
                 checkpoint_every: int = 500):
        self.mode = mode
        self.checkpoint_every = checkpoint_every
        # Adaptive RF (ARFClassifier in River 0.24) + standard scaling
        self.model = compose.Pipeline(
            preprocessing.StandardScaler(),
            forest.ARFClassifier(
                n_models=n_models,
                max_features=max_features,
                seed=42,
            ),
        )
        # Multi-class accuracy + per-class F1
        self.metric_acc = metrics.Accuracy()
        self.metric_f1_macro = metrics.MacroF1()
        self.metric_cm = metrics.ConfusionMatrix()
        self.n_seen = 0
        self.checkpoint_path = DERIVED / f'{mode}_river_model.pkl'
        self.stats_path = DERIVED / f'{mode}_ml_stats.json'

        # Resume from checkpoint if exists
        if self.checkpoint_path.exists():
            try:
                with self.checkpoint_path.open('rb') as f:
                    state = pickle.load(f)
                self.model = state['model']
                self.metric_acc = state['acc']
                self.metric_f1_macro = state['f1']
                self.metric_cm = state['cm']
                self.n_seen = state['n_seen']
                print(f'[ml] Resumed from {self.checkpoint_path.name}: n_seen={self.n_seen}', flush=True)
            except Exception as e:
                print(f'[ml] Could not load checkpoint: {e}; starting fresh', flush=True)

    def learn_chunk(self, derived_df: pd.DataFrame):
        """Predict-then-learn (prequential evaluation) for each row in chunk."""
        for _, r in derived_df.iterrows():
            x = _row_to_x(r)
            y = r['class']
            # Predict first (interleaved test-then-train, prequential)
            try:
                y_pred = self.model.predict_one(x)
            except Exception:
                y_pred = None
            if y_pred is not None:
                self.metric_acc.update(y, y_pred)
                self.metric_f1_macro.update(y, y_pred)
                self.metric_cm.update(y, y_pred)
            # Then learn
            self.model.learn_one(x, y)
            self.n_seen += 1
            if self.n_seen % self.checkpoint_every == 0:
                self._checkpoint()
        # End-of-chunk checkpoint
        self._checkpoint()
        print(f'[ml] n_seen={self.n_seen}  acc={self.metric_acc.get():.3f}  '
              f'macroF1={self.metric_f1_macro.get():.3f}', flush=True)

    def _checkpoint(self):
        # Pickle the model + metrics
        tmp = self.checkpoint_path.with_suffix('.pkl.tmp')
        with tmp.open('wb') as f:
            pickle.dump({
                'model': self.model, 'acc': self.metric_acc,
                'f1': self.metric_f1_macro, 'cm': self.metric_cm,
                'n_seen': self.n_seen,
            }, f)
        tmp.replace(self.checkpoint_path)
        # Stats JSON (human-readable)
        cm_dict = {}
        try:
            cm_dict = {str(k): {str(k2): v2 for k2, v2 in v.items()}
                       for k, v in self.metric_cm.data.items()}
        except Exception:
            pass
        stats = {
            'mode': self.mode,
            'n_seen': self.n_seen,
            'accuracy': float(self.metric_acc.get()),
            'macro_f1': float(self.metric_f1_macro.get()),
            'updated_at': datetime.now(timezone.utc).isoformat(),
            'confusion_matrix': cm_dict,
        }
        tmp_s = self.stats_path.with_suffix('.json.tmp')
        tmp_s.write_text(json.dumps(stats, indent=2, default=str))
        tmp_s.replace(self.stats_path)


if __name__ == '__main__':
    import sys
    # CLI: refit on existing derived parquet (full pass)
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument('--mode', choices=['main', 'wider'], required=True)
    ap.add_argument('--refit', action='store_true', help='Refit from scratch on derived parquet')
    args = ap.parse_args()

    derived_path = DERIVED / f'{args.mode}_hunt_derived.parquet'
    if not derived_path.exists():
        print(f'No derived parquet at {derived_path}'); sys.exit(1)

    rc = RiverClassifier(mode=args.mode)
    if args.refit:
        if rc.checkpoint_path.exists():
            rc.checkpoint_path.unlink()
        rc = RiverClassifier(mode=args.mode)
    df = pd.read_parquet(derived_path)
    print(f'Refitting on {len(df)} rows...')
    rc.learn_chunk(df)
    print(f'Final: n_seen={rc.n_seen}  acc={rc.metric_acc.get():.3f}  macroF1={rc.metric_f1_macro.get():.3f}')
