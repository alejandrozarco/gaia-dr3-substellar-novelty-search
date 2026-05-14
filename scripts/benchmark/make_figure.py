"""Benchmark visualization — 2-panel figure for BENCHMARK.md."""
import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import polars as pl

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _config import get_args  # noqa: E402

args = get_args(description="Generate benchmark figure")
OUT_DIR = str(args.out_dir)

# Reload truth set and reclassify (same logic as run_benchmark_v2.py)
truth = pl.read_csv(f"{OUT_DIR}/truth_set.csv")
truth = truth.unique(subset=["source_id", "truth_bucket"], keep="first")
HIGH_CONF = {
    "CONFIRMED_BROWN_DWARF", "CONFIRMED_EXOPLANET", "HIGH_PROB_SUBSTELLAR",
    "SAHL_HIGH_PROB_BD_CAND", "SAHL_TOP_EXOPLANET_CAND",
    "SAHL_EXOPLANET_CAND", "SAHL_CONFIRMED_BD", "SAHL_BD_CAND",
    "CONFIRMED_BINARY_FP", "SAHL_FALSE_POSITIVE_BINARY",
    "VLMS_FP_NOT_SUBSTELLAR", "SAHL_VERY_LOW_MASS_STAR",
    "SAHL_LOW_MASS_STAR", "SAHL_RETRACTED_BY_GAIA",
    "GAIA_DR3_RETRACTED_FP", "documented_fp",
}
truth_hc = truth.filter(pl.col("verdict").is_in(HIGH_CONF))

RETAINED_STRONG = {"CORROBORATED_real_companion"}
RETAINED_WEAK = {"FLAG_hgca_mass_ambiguous", "SURVIVOR_no_hgca_corroboration"}
CORRECT_REJECT_PUBLISHED = {"REJECTED_published_nasa_exo"}
CORRECT_REJECT_STELLAR = {"REJECTED_hgca_stellar"}


def classify(v):
    if v is None or v == "__NOT_IN_POOL__":
        return "NOT_IN_POOL"
    if v in RETAINED_STRONG:
        return "RETAINED_STRONG"
    if v in RETAINED_WEAK:
        return "RETAINED_WEAK"
    if v in CORRECT_REJECT_PUBLISHED:
        return "REJECTED_AS_PUBLISHED"
    if v in CORRECT_REJECT_STELLAR:
        return "REJECTED_AS_STELLAR"
    if v.startswith("REJECTED_"):
        return "REJECTED_OTHER"
    return "OTHER"


truth_hc = truth_hc.with_columns(
    pl.col("v2_verdict").fill_null("__NOT_IN_POOL__").alias("_v2v_filled")
).with_columns(
    pl.col("_v2v_filled").map_elements(classify, return_dtype=pl.Utf8)
    .alias("retention_class")
).drop("_v2v_filled")

# ============================================================
# Figure
# ============================================================

fig, (axL, axR) = plt.subplots(1, 2, figsize=(16, 7),
                                gridspec_kw={"width_ratios": [1, 1.2]})

# Order of outcome categories (from "good for novelty mining" to "bad")
categories = [
    ("RETAINED_STRONG",       "Retained: corroborated", "#1f7a3a"),
    ("RETAINED_WEAK",         "Retained: weak/flagged", "#2ca02c"),
    ("REJECTED_AS_PUBLISHED", "Correctly rejected: already published", "#7eb8d6"),
    ("REJECTED_AS_STELLAR",   "Correctly rejected: HGCA stellar", "#5a9fd4"),
    ("REJECTED_OTHER",        "Wrongly rejected (false negative)", "#d62728"),
    ("NOT_IN_POOL",           "Pre-filtered out (Stage 1 quality)", "#999999"),
]

# Panel L — stacked bars by truth bucket
buckets = ["POSITIVE", "NEGATIVE", "DOCUMENTED_FP"]
bucket_labels = ["POSITIVE\n(real substellar)\nn=56",
                 "NEGATIVE\n(real imposter)\nn=11",
                 "DOCUMENTED FP\n(Gaia known-issue)\nn=4"]
totals = {b: truth_hc.filter(pl.col("truth_bucket") == b).height for b in buckets}
bucket_labels[0] = f"POSITIVE\n(real substellar)\nn={totals['POSITIVE']}"
bucket_labels[1] = f"NEGATIVE\n(real imposter)\nn={totals['NEGATIVE']}"
bucket_labels[2] = f"DOCUMENTED FP\n(Gaia known-issue)\nn={totals['DOCUMENTED_FP']}"

x_pos = np.arange(len(buckets))
bottoms = np.zeros(len(buckets))

for cat_key, cat_label, color in categories:
    heights = []
    for b in buckets:
        n = truth_hc.filter(
            (pl.col("truth_bucket") == b) &
            (pl.col("retention_class") == cat_key)
        ).height
        heights.append(n)
    heights = np.array(heights)
    bars = axL.bar(x_pos, heights, bottom=bottoms, color=color, edgecolor="black",
                    linewidth=0.6, label=cat_label)
    # Add count labels inside bars
    for i, (h, b) in enumerate(zip(heights, bottoms)):
        if h > 0:
            axL.text(x_pos[i], b + h / 2, str(int(h)),
                     ha="center", va="center", fontsize=10,
                     color="white" if "REJECTED" in cat_key or cat_key == "NOT_IN_POOL"
                     else "black", fontweight="bold")
    bottoms += heights

axL.set_xticks(x_pos)
axL.set_xticklabels(bucket_labels, fontsize=10)
axL.set_ylabel("Number of truth-set entries", fontsize=11)
axL.set_title("Cascade outcome by truth bucket\n(stacked: outcome categories)",
              fontsize=12)
axL.grid(axis="y", alpha=0.3)
axL.set_ylim(0, max(totals.values()) * 1.1)
axL.legend(loc="upper right", fontsize=8.5, framealpha=0.95)

# Panel R — per-filter destruction breakdown
print("Per-filter table:")
per_filter = truth_hc.filter(
    pl.col("retention_class") != "NOT_IN_POOL"
).group_by(["v2_verdict", "truth_bucket"]).agg(
    pl.len().alias("n")
).sort(["v2_verdict", "truth_bucket"])
print(per_filter)

# Reorganize: rows = filter outcome, columns = POSITIVE/NEGATIVE counts
verdict_order = [
    "CORROBORATED_real_companion",
    "FLAG_hgca_mass_ambiguous",
    "SURVIVOR_no_hgca_corroboration",
    "REJECTED_published_nasa_exo",
    "REJECTED_hgca_stellar",
    "REJECTED_sahlmann_ml_imposter",
    "REJECTED_ruwe_quality",
]
verdict_labels = [
    "CORROBORATED\n(retained)",
    "FLAG\n(retained, weak)",
    "SURVIVOR\n(retained, weak)",
    "REJECTED published\n(correct)",
    "REJECTED HGCA stellar\n(correct)",
    "REJECTED Sahlmann ML\n(false-neg risk)",
    "REJECTED RUWE\n(false-neg risk)",
]
pos_counts = []
neg_counts = []
for v in verdict_order:
    p = truth_hc.filter(
        (pl.col("v2_verdict") == v) & (pl.col("truth_bucket") == "POSITIVE")
    ).height
    n = truth_hc.filter(
        (pl.col("v2_verdict") == v) & (pl.col("truth_bucket") == "NEGATIVE")
    ).height
    pos_counts.append(p)
    neg_counts.append(n)

y_pos = np.arange(len(verdict_order))
width = 0.4
axR.barh(y_pos + width / 2, pos_counts, height=width, color="#2ca02c",
         edgecolor="black", linewidth=0.6, label=f"Positives (n={totals['POSITIVE']})")
axR.barh(y_pos - width / 2, neg_counts, height=width, color="#d62728",
         edgecolor="black", linewidth=0.6, label=f"Negatives (n={totals['NEGATIVE']})")

for i, (p, n) in enumerate(zip(pos_counts, neg_counts)):
    if p > 0:
        axR.text(p + 0.2, i + width / 2, str(p), va="center", fontsize=9,
                 color="#2ca02c", fontweight="bold")
    if n > 0:
        axR.text(n + 0.2, i - width / 2, str(n), va="center", fontsize=9,
                 color="#d62728", fontweight="bold")

axR.set_yticks(y_pos)
axR.set_yticklabels(verdict_labels, fontsize=9)
axR.set_xlabel("Number of truth-set entries", fontsize=11)
axR.set_title("Per-filter outcome breakdown\n(positives vs negatives by cascade verdict)",
              fontsize=12)
axR.grid(axis="x", alpha=0.3)
axR.legend(loc="lower right", fontsize=10)
axR.invert_yaxis()

# Overall title
fig.suptitle(
    "HD Gaia DR3 NSS Cascade — Benchmark vs Sahlmann 2025 truth set\n"
    f"71 high-confidence entries · In-pool novelty recall = 58.8% · "
    f"End-to-end specificity = 72.7% · Documented-FP catch = 100%",
    fontsize=13.5, fontweight="bold", y=1.02)

plt.tight_layout()
plt.savefig(f"{OUT_DIR}/benchmark_figure.png", dpi=300, bbox_inches="tight",
            facecolor="white")
plt.close()
print(f"\nWrote {OUT_DIR}/benchmark_figure.png (300 dpi)")
