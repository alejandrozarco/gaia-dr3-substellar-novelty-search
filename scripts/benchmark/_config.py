"""Tiny config loader for benchmark scripts.

Reads config.yaml from the repo root (or path specified via --config arg)
and exposes resolved paths as attributes. Falls back to sensible defaults
if config.yaml is absent (uses bundled in-repo paths only).
"""
import argparse
import os
import sys
from pathlib import Path

try:
    import yaml
except ImportError:
    yaml = None


def _find_repo_root():
    """Find the publication repo root by walking up looking for README.md
    + novelty_candidates.csv."""
    here = Path(__file__).resolve()
    for parent in [here.parent, *here.parents]:
        if (parent / "README.md").exists() and (parent / "novelty_candidates.csv").exists():
            return parent
    return Path.cwd()


REPO_ROOT = _find_repo_root()


def load_config(config_path=None):
    """Load config.yaml or fall back to defaults."""
    if config_path is None:
        config_path = REPO_ROOT / "config.yaml"
    config_path = Path(config_path)
    if not config_path.exists():
        # No user config — try the example
        example = REPO_ROOT / "config.yaml.example"
        if example.exists():
            print(f"[config] No config.yaml; using {example.name} defaults.",
                  file=sys.stderr)
            config_path = example
        else:
            print(f"[config] No config found; using built-in defaults.",
                  file=sys.stderr)
            return _default_config()
    if yaml is None:
        print(f"[config] yaml package missing; using built-in defaults.",
              file=sys.stderr)
        return _default_config()
    with open(config_path) as f:
        return yaml.safe_load(f)


def _default_config():
    return {
        "release": "1.1.0",
        "benchmark": {
            "v2_scan_pool": "v2_scan_full_pool.csv",
            "novelty_candidates": "novelty_candidates.csv",
            "sahlmann_verdicts": None,
            "gaia_fp_list": None,
        },
    }


def resolve_path(p):
    """Resolve a possibly-relative path against REPO_ROOT."""
    if p is None:
        return None
    p = Path(p)
    if not p.is_absolute():
        p = REPO_ROOT / p
    return p


def get_args(description=""):
    """Standard argparse for benchmark scripts."""
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument("--config", default=None,
                        help="Path to config.yaml (default: ./config.yaml or example)")
    parser.add_argument("--out-dir", default="benchmark_output",
                        help="Where to write output CSVs and figures")
    args = parser.parse_args()
    args.out_dir = resolve_path(args.out_dir)
    Path(args.out_dir).mkdir(parents=True, exist_ok=True)
    args.config_data = load_config(args.config)
    return args
