"""Simulate Sahlmann tie-breaking rule on existing v2 cascade data.

Rule: if a source is flagged by Sahlmann's ML imposter table BUT also appears
in Sahlmann's verdicts table with a positive substellar label, defer to the
verdicts table (DON'T reject as imposter).

This is the v3 cascade behavior. We simulate it by re-classifying the 12
REJECTED_sahlmann_ml_imposter sources in our truth set using their other
v2 cascade parameters (HGCA chi^2, NASA Exo match, RUWE, etc.).
"""
import sys
from pathlib import Path

import polars as pl

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _config import get_args  # noqa: E402

args = get_args(description="Simulate Sahlmann tie-breaking on v2 cascade data")
OUT_DIR = str(args.out_dir)
truth = pl.read_csv(f"{OUT_DIR}/truth_set.csv")
truth = truth.unique(subset=["source_id", "truth_bucket"], keep="first")

# Sahlmann-positive labels (overrides ML imposter flag under tie-breaking)
SAHL_POSITIVE_LABELS = {
    "CONFIRMED_BROWN_DWARF", "CONFIRMED_EXOPLANET", "HIGH_PROB_SUBSTELLAR",
    "SAHL_HIGH_PROB_BD_CAND", "SAHL_TOP_EXOPLANET_CAND",
    "SAHL_EXOPLANET_CAND", "SAHL_CONFIRMED_BD", "SAHL_BD_CAND",
    "SAHL_BD_VLMS_BOUNDARY",
}


def reclassify_with_tiebreaking(row):
    """Given a row's v2 cascade fields, decide the v3 verdict.

    Returns a string verdict matching the v2 verdict vocabulary.
    """
    v = row["v2_verdict"]
    if v != "REJECTED_sahlmann_ml_imposter":
        # Nothing to change
        return v
    # Apply tie-breaking: did Sahlmann's verdicts table also label this positive?
    sahl_verdict = row["verdict"]
    if sahl_verdict not in SAHL_POSITIVE_LABELS:
        # ML imposter flag stands (no positive label disagreement)
        return v
    # Override: continue cascade as if Sahlmann ML didn't fire
    # Now apply remaining filters in cascade order:
    # 1. NASA Exo PS match → REJECTED_published_nasa_exo
    if row["nasa_exo_match"] is True:
        return "REJECTED_published_nasa_exo"
    # 2. documented FP → REJECTED_documented_fp (but those aren't in pool)
    if row["documented_fp"] is True:
        return "REJECTED_documented_fp"
    # 3. HGCA chi^2 tier (Filter #29)
    hgca = row["hgca_chisq"]
    if hgca is not None and hgca > 100:
        return "REJECTED_hgca_stellar"
    # 4. RUWE quality (conditional per solution type — Filter #30)
    # Orbit-reflex solution types skip the RUWE cut
    ORBIT_REFLEX = {"Orbital", "AstroSpectroSB1", "OrbitalTargetedSearchValidated"}
    sol = row["nss_solution_type"]
    ruwe = row["ruwe"]
    if sol not in ORBIT_REFLEX and ruwe is not None and ruwe > 2.0:
        return "REJECTED_ruwe_quality"
    # 5. HGCA tier classification (CORROBORATED vs FLAG vs SURVIVOR)
    if hgca is not None and 30 <= hgca <= 100:
        return "FLAG_hgca_mass_ambiguous"
    if hgca is not None and 5 <= hgca < 30:
        return "CORROBORATED_real_companion"
    # else: passed all filters but no HGCA corroboration
    return "SURVIVOR_no_hgca_corroboration"


# Apply tie-breaking
truth = truth.with_columns(
    pl.struct(["v2_verdict", "verdict", "nasa_exo_match", "documented_fp",
               "hgca_chisq", "nss_solution_type", "ruwe"])
    .map_elements(reclassify_with_tiebreaking, return_dtype=pl.Utf8)
    .alias("v3_verdict")
)

# Check what changed
changed = truth.filter(pl.col("v2_verdict") != pl.col("v3_verdict"))
print(f"Reclassified sources: {changed.height}")
print()
print(changed.select([
    "source_id", "name", "verdict", "v2_verdict", "v3_verdict",
    "hgca_chisq", "ruwe", "nss_solution_type"
]).to_pandas().to_string())

# ============================================================
# Recompute benchmark with v3 verdicts
# ============================================================

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
    pl.col("v3_verdict").fill_null("__NOT_IN_POOL__").alias("_v3_filled")
).with_columns(
    pl.col("_v3_filled").map_elements(classify, return_dtype=pl.Utf8)
    .alias("retention_class")
).drop("_v3_filled")

pos = truth_hc.filter(pl.col("truth_bucket") == "POSITIVE")
pos_retained = pos.filter(
    pl.col("retention_class").is_in(["RETAINED_STRONG", "RETAINED_WEAK"])
)
pos_published = pos.filter(pl.col("retention_class") == "REJECTED_AS_PUBLISHED")
pos_fn = pos.filter(
    pl.col("retention_class").is_in(["REJECTED_OTHER", "REJECTED_AS_STELLAR"])
)
pos_notpool = pos.filter(pl.col("retention_class") == "NOT_IN_POOL")

neg = truth_hc.filter(pl.col("truth_bucket") == "NEGATIVE")
neg_excluded = neg.filter(
    pl.col("retention_class").is_in(["NOT_IN_POOL", "REJECTED_OTHER",
                                      "REJECTED_AS_STELLAR", "REJECTED_AS_PUBLISHED"])
)
neg_kept = neg.filter(
    pl.col("retention_class").is_in(["RETAINED_STRONG", "RETAINED_WEAK"])
)

in_pool_recall = pos_retained.height / max(pos_retained.height + pos_fn.height, 1)
e2e_recall = pos_retained.height / max(
    pos_retained.height + pos_fn.height + pos_notpool.height, 1
)
specificity = neg_excluded.height / max(neg.height, 1)

print("\n" + "=" * 70)
print("v3 BENCHMARK (with Sahlmann tie-breaking rule)")
print("=" * 70)
print(f"  Positives in pool retained:   {pos_retained.height}")
print(f"  Positives correctly published: {pos_published.height}")
print(f"  Positives false-negative:     {pos_fn.height}")
print(f"  Positives not in pool:        {pos_notpool.height}")
print()
print(f"  In-pool novelty recall:    {in_pool_recall:.1%}")
print(f"  End-to-end novelty recall: {e2e_recall:.1%}")
print(f"  End-to-end specificity:    {specificity:.1%}")
print()
print(f"  Comparison vs v2:")
print(f"    Recall:      58.8% -> {in_pool_recall:.1%}")
print(f"    E2E recall:  42.6% -> {e2e_recall:.1%}")
print(f"    Specificity: 72.7% -> {specificity:.1%}")

# Per-filter destruction for v3
print("\n" + "=" * 70)
print("v3 per-filter destruction (positives)")
print("=" * 70)
v3_per_filter = pos.filter(
    pl.col("retention_class").is_in(["REJECTED_OTHER", "REJECTED_AS_STELLAR"])
).group_by("v3_verdict").agg(pl.len().alias("n_lost")).sort("n_lost", descending=True)
print(v3_per_filter)

# Save v3 truth set
truth.write_csv(f"{OUT_DIR}/truth_set_v3.csv")
print(f"\nWrote {OUT_DIR}/truth_set_v3.csv with v3_verdict column")

# Save numeric summary
with open(f"{OUT_DIR}/v3_metrics_summary.txt", "w") as f:
    f.write(f"v3 cascade benchmark (Sahlmann tie-breaking rule applied)\n")
    f.write(f"=" * 70 + "\n\n")
    f.write(f"In-pool novelty recall:    {in_pool_recall:.1%} "
            f"(v2: 58.8%, delta: +{(in_pool_recall - 0.588)*100:.1f}pp)\n")
    f.write(f"End-to-end novelty recall: {e2e_recall:.1%} "
            f"(v2: 42.6%, delta: +{(e2e_recall - 0.426)*100:.1f}pp)\n")
    f.write(f"End-to-end specificity:    {specificity:.1%} "
            f"(v2: 72.7%, delta: +{(specificity - 0.727)*100:.1f}pp)\n")
    f.write(f"\nReclassified sources: {changed.height}\n")
    f.write(f"\nv3 false-negative breakdown:\n")
    for row in v3_per_filter.iter_rows(named=True):
        f.write(f"  {row['v3_verdict']}: {row['n_lost']}\n")
print(f"Wrote {OUT_DIR}/v3_metrics_summary.txt")
