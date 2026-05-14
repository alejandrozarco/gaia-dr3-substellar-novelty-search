"""Build truth set for cascade benchmark.

Combines:
  * Sahlmann 2025 verdicts (1933 entries, 18 verdict categories)
  * Gaia DR3 documented NSS false-positive list (4 entries)
  * v2 scan full pool data (9498 sources with cascade verdicts and parameters)

Outputs:
  * truth_set.csv — joined table, one row per source_id with ground-truth
    label + cascade verdict + NSS parameters + Sahlmann/published references.

Usage:
  python build_truth_set.py --config config.yaml --out-dir benchmark_output
"""
import sys
from pathlib import Path

import polars as pl

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _config import get_args, resolve_path  # noqa: E402

args = get_args(description="Build truth set for cascade benchmark")
config = args.config_data
OUT_DIR = args.out_dir

V2_POOL = resolve_path(config["benchmark"]["v2_scan_pool"])
SAHLMANN = resolve_path(config["benchmark"].get("sahlmann_verdicts"))
GAIA_FPS = resolve_path(config["benchmark"].get("gaia_fp_list"))

if SAHLMANN is None or not SAHLMANN.exists():
    print(f"ERROR: Sahlmann verdicts file missing. Set "
          f"`benchmark.sahlmann_verdicts` in config.yaml.\n"
          f"  Expected: {SAHLMANN}", file=sys.stderr)
    sys.exit(2)
if GAIA_FPS is None or not GAIA_FPS.exists():
    print(f"ERROR: Gaia DR3 FP list missing. Set "
          f"`benchmark.gaia_fp_list` in config.yaml.\n"
          f"  Expected: {GAIA_FPS}", file=sys.stderr)
    sys.exit(2)

LABEL_TO_BUCKET = {
    "CONFIRMED_BROWN_DWARF":      ("POSITIVE", "high"),
    "CONFIRMED_EXOPLANET":        ("POSITIVE", "high"),
    "HIGH_PROB_SUBSTELLAR":       ("POSITIVE", "high"),
    "SAHL_HIGH_PROB_BD_CAND":     ("POSITIVE", "high"),
    "SAHL_TOP_EXOPLANET_CAND":    ("POSITIVE", "high"),
    "SAHL_EXOPLANET_CAND":        ("POSITIVE", "high"),
    "SAHL_CONFIRMED_BD":          ("POSITIVE", "high"),
    "SAHL_BD_CAND":               ("POSITIVE", "med"),
    "SAHL_BD_VLMS_BOUNDARY":      ("POSITIVE", "low"),
    "SAHL_LOWER_CONF_CAND":       ("POSITIVE", "low"),
    "CONFIRMED_BINARY_FP":        ("NEGATIVE", "high"),
    "SAHL_FALSE_POSITIVE_BINARY": ("NEGATIVE", "high"),
    "VLMS_FP_NOT_SUBSTELLAR":     ("NEGATIVE", "high"),
    "SAHL_VERY_LOW_MASS_STAR":    ("NEGATIVE", "high"),
    "SAHL_LOW_MASS_STAR":         ("NEGATIVE", "high"),
    "SAHL_RETRACTED_BY_GAIA":     ("DOCUMENTED_FP", "high"),
    "GAIA_DR3_RETRACTED_FP":      ("DOCUMENTED_FP", "high"),
}

sahl = pl.read_csv(SAHLMANN)
v2 = pl.read_csv(V2_POOL)
fps = pl.read_csv(GAIA_FPS)

print(f"Sahlmann verdicts:          {sahl.height} rows")
print(f"v2 scan full pool:          {v2.height} rows")
print(f"Documented Gaia DR3 FPs:    {fps.height} rows")

sahl = sahl.with_columns(
    pl.col("verdict").map_elements(
        lambda v: LABEL_TO_BUCKET.get(v, (None, None))[0], return_dtype=pl.Utf8
    ).alias("truth_bucket"),
    pl.col("verdict").map_elements(
        lambda v: LABEL_TO_BUCKET.get(v, (None, None))[1], return_dtype=pl.Utf8
    ).alias("truth_confidence"),
)
sahl_truth = sahl.filter(pl.col("truth_bucket").is_not_null())
print(f"\nSahlmann high+med+low confidence truth-bucket entries: {sahl_truth.height}")
print(sahl_truth.group_by("truth_bucket").agg(pl.len()).sort("truth_bucket"))

sahl_truth = sahl_truth.with_columns(pl.col("source_id").cast(pl.Int64))
v2_join = v2.select([
    "source_id", "nss_solution_type", "period_d", "eccentricity",
    "significance", "ruwe", "M_2_mjup_face_on", "M_2_mjup_marginalized",
    "phot_g_mean_mag", "HIP", "Name", "Vmag", "SpType", "snrPMaH2G2",
    "sahl_confirmed", "in_stefansson", "documented_fp", "ruwe_pass",
    "nasa_exo_match", "hgca_chisq", "hgca_tier", "v2_verdict", "v2_score",
])
joined = sahl_truth.join(v2_join, on="source_id", how="left").with_columns(
    pl.col("v2_verdict").is_not_null().alias("in_v2_pool"),
)

print(f"\nTruth-set entries crossed with v2 scan pool: {joined.height}")
print(f"  ...of which in v2 pool: {joined.filter(pl.col('in_v2_pool')).height}")

fps_v2 = fps.join(v2_join, on="source_id", how="left").with_columns(
    pl.lit("DOCUMENTED_FP").alias("truth_bucket"),
    pl.lit("high").alias("truth_confidence"),
    pl.lit("Gaia DR3 known-issues").alias("reference"),
    pl.lit("documented_fp").alias("verdict"),
    pl.col("common_name").alias("name"),
    pl.col("v2_verdict").is_not_null().alias("in_v2_pool"),
).with_columns(
    pl.lit(None, dtype=pl.Float64).alias("P_d_Gaia"),
    pl.lit(None, dtype=pl.Float64).alias("M_2_MJup_true"),
    pl.lit("FP_LIST").alias("table"),
)

common_cols = [c for c in joined.columns if c in fps_v2.columns]
truth_set = pl.concat(
    [joined.select(common_cols), fps_v2.select(common_cols)],
    how="vertical"
)

out_csv = OUT_DIR / "truth_set.csv"
truth_set.write_csv(out_csv)
print(f"\nWrote {out_csv} ({truth_set.height} rows, "
      f"{len(truth_set.columns)} columns)")
