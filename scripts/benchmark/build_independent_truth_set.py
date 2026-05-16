"""Build INDEPENDENT truth set from Marcussen & Albrecht 2023 vetting.

This addresses the external-review critique that the original truth set
draws from Sahlmann 2025, which is ALSO one of our cascade filters —
making the recall measurement partly tautological.

Marcussen & Albrecht 2023 (AJ 165, 266) is a completely independent paper
that performed HARPS-N + literature vetting on Gaia DR3 NSS Orbital
substellar candidates. Their verdicts (`published_vetted_substellar_crossmatch.csv`):
  * CONFIRMED_PLANET       — literature-confirmed exoplanet (positive)
  * CONFIRMED_BD           — literature-confirmed brown dwarf (positive)
  * PLANET_LIT_PRIOR       — literature planet (positive)
  * PLANET_RV_INCONSISTENT — published planet, M&A RV didn't reconfirm
                             (positive — companion is real but params disputed)
  * STELLAR_IMPOSTER       — independently confirmed stellar binary (negative)
  * RV_K_INCONSISTENT      — RV check failed (ambiguous; excluded)
  * NOT_VETTED             — uncertain (excluded)

We use the four clear "positive" labels and STELLAR_IMPOSTER as
"negative" — none of which is from Sahlmann.

We also add the 4 Gaia DR3 documented-FP source IDs (same as in
the Sahlmann-based truth set, since these are independent of both).
"""
import polars as pl

REPO = "/tmp/gaia-novelty-publication"
OUT_DIR = "/Users/legbatterij/claude_projects/ostinato/notes/2026-05-13-cascade-benchmark"
MARCUSSEN_FILE = "/Users/legbatterij/claude_projects/ostinato/data/candidate_dossiers/marcussen_dalal_2023_vetting/published_vetted_substellar_crossmatch.csv"
GAIA_FPS_FILE = "/Users/legbatterij/claude_projects/ostinato/data/candidate_dossiers/gaia_dr3_nss_known_fps.csv"

POSITIVE_LABELS = {
    "CONFIRMED_PLANET", "CONFIRMED_BD", "PLANET_LIT_PRIOR",
    "PLANET_RV_INCONSISTENT",
}
NEGATIVE_LABELS = {"STELLAR_IMPOSTER"}

marc = pl.read_csv(MARCUSSEN_FILE)
v2 = pl.read_csv(f"{REPO}/v2_scan_full_pool.csv")
fps = pl.read_csv(GAIA_FPS_FILE)

print(f"Marcussen+Albrecht vetting: {marc.height} entries")
print(f"v2 scan full pool:          {v2.height} sources")
print(f"Gaia DR3 documented FPs:    {fps.height} sources")
print()

# Classify
marc = marc.with_columns(
    pl.when(pl.col("verdict").is_in(list(POSITIVE_LABELS)))
    .then(pl.lit("POSITIVE"))
    .when(pl.col("verdict").is_in(list(NEGATIVE_LABELS)))
    .then(pl.lit("NEGATIVE"))
    .otherwise(pl.lit(None))
    .alias("truth_bucket")
)

# Keep only high-confidence rows
marc_truth = marc.filter(pl.col("truth_bucket").is_not_null())
print(f"Marcussen high-confidence entries: {marc_truth.height}")
print(marc_truth.group_by(["truth_bucket", "verdict"]).agg(pl.len()).sort(["truth_bucket", "verdict"]))

# Join with v2 scan pool
marc_truth = marc_truth.with_columns(pl.col("source_id").cast(pl.Int64))
v2_join = v2.select([
    "source_id", "nss_solution_type", "period_d", "eccentricity",
    "significance", "ruwe", "M_2_mjup_face_on", "M_2_mjup_marginalized",
    "phot_g_mean_mag", "HIP", "Name", "Vmag", "SpType", "snrPMaH2G2",
    "sahl_confirmed", "in_stefansson", "documented_fp", "ruwe_pass",
    "nasa_exo_match", "hgca_chisq", "hgca_tier", "v2_verdict", "v2_score",
])
joined = marc_truth.join(v2_join, on="source_id", how="left").with_columns(
    pl.col("v2_verdict").is_not_null().alias("in_v2_pool")
)

print(f"\nMarcussen entries in v2 pool: {joined.filter(pl.col('in_v2_pool')).height} / {joined.height}")

# Add documented FPs
fps_truth = fps.join(v2_join, on="source_id", how="left").with_columns(
    pl.lit("DOCUMENTED_FP").alias("truth_bucket"),
    pl.lit("documented_fp").alias("verdict"),
    pl.col("common_name").alias("our_Name"),
    pl.col("v2_verdict").is_not_null().alias("in_v2_pool"),
)

# Align schemas for concat
common_cols = [c for c in joined.columns if c in fps_truth.columns]
truth = pl.concat(
    [joined.select(common_cols), fps_truth.select(common_cols)],
    how="vertical"
).unique(subset=["source_id", "truth_bucket"], keep="first")

truth.write_csv(f"{OUT_DIR}/truth_set_independent.csv")
truth.write_csv(f"{REPO}/benchmark_output/truth_set_independent.csv")
print(f"\nWrote independent truth set: {truth.height} rows")
print(truth.group_by("truth_bucket").agg(pl.len()).sort("truth_bucket"))
print()

# Now classify cascade outcomes
RETAINED_STRONG = {"CORROBORATED_real_companion"}
RETAINED_WEAK = {"FLAG_hgca_mass_ambiguous", "SURVIVOR_no_hgca_corroboration"}
CORRECT_REJ_PUB = {"REJECTED_published_nasa_exo"}
CORRECT_REJ_STELLAR = {"REJECTED_hgca_stellar"}


def classify(v):
    if v is None or v == "__NULL__":
        return "NOT_IN_POOL"
    if v in RETAINED_STRONG:
        return "RETAINED_STRONG"
    if v in RETAINED_WEAK:
        return "RETAINED_WEAK"
    if v in CORRECT_REJ_PUB:
        return "REJECTED_AS_PUBLISHED"
    if v in CORRECT_REJ_STELLAR:
        return "REJECTED_AS_STELLAR"
    if v.startswith("REJECTED_"):
        return "REJECTED_OTHER"
    return "OTHER"


truth = truth.with_columns(
    pl.col("v2_verdict").fill_null("__NULL__").map_elements(
        classify, return_dtype=pl.Utf8
    ).alias("retention_class")
)

# Confusion matrix
print("=" * 75)
print("INDEPENDENT BENCHMARK — Marcussen+Albrecht 2023 + Gaia FP truth set")
print("=" * 75)
confusion = truth.group_by(["truth_bucket", "retention_class"]).agg(
    pl.len().alias("n")
).pivot(on="retention_class", index="truth_bucket", values="n").fill_null(0)
print(confusion)

# Recall/specificity for v2 cascade
pos = truth.filter(pl.col("truth_bucket") == "POSITIVE")
pos_in_pool = pos.filter(pl.col("retention_class") != "NOT_IN_POOL")
pos_retained = pos.filter(
    pl.col("retention_class").is_in(["RETAINED_STRONG", "RETAINED_WEAK"])
)
pos_published = pos.filter(pl.col("retention_class") == "REJECTED_AS_PUBLISHED")
pos_fn = pos.filter(
    pl.col("retention_class").is_in(["REJECTED_OTHER", "REJECTED_AS_STELLAR"])
)
pos_notpool = pos.filter(pl.col("retention_class") == "NOT_IN_POOL")

neg = truth.filter(pl.col("truth_bucket") == "NEGATIVE")
neg_excluded = neg.filter(
    pl.col("retention_class").is_in([
        "NOT_IN_POOL", "REJECTED_OTHER", "REJECTED_AS_STELLAR",
        "REJECTED_AS_PUBLISHED"
    ])
)
neg_kept = neg.filter(
    pl.col("retention_class").is_in(["RETAINED_STRONG", "RETAINED_WEAK"])
)

fps_t = truth.filter(pl.col("truth_bucket") == "DOCUMENTED_FP")
fps_caught = fps_t.filter(pl.col("retention_class") == "NOT_IN_POOL")


def wilson_ci(k, n, conf=0.95):
    from scipy import stats
    if n == 0:
        return (0, 0)
    p = k / n
    z = stats.norm.ppf((1 + conf) / 2)
    z2 = z * z
    c = (p + z2 / (2 * n)) / (1 + z2 / n)
    h = z * ((p * (1 - p) / n + z2 / (4 * n * n)) ** 0.5) / (1 + z2 / n)
    return (max(0, c - h), min(1, c + h))


k_recall = pos_retained.height
n_recall_inpool = pos_retained.height + pos_fn.height
n_recall_e2e = pos_retained.height + pos_fn.height + pos_notpool.height
recall_inpool = k_recall / max(n_recall_inpool, 1)
recall_e2e = k_recall / max(n_recall_e2e, 1)
r_lo_i, r_hi_i = wilson_ci(k_recall, n_recall_inpool)
r_lo_e, r_hi_e = wilson_ci(k_recall, n_recall_e2e)

k_spec = neg_excluded.height
n_spec = neg.height
specificity = k_spec / max(n_spec, 1)
s_lo, s_hi = wilson_ci(k_spec, n_spec)

k_fp = fps_caught.height
n_fp = fps_t.height
fp_rate = k_fp / max(n_fp, 1)
fp_lo, fp_hi = wilson_ci(k_fp, n_fp)

print()
print(f"v2 cascade (released) metrics on INDEPENDENT truth set:")
print(f"  In-pool novelty recall:     {k_recall}/{n_recall_inpool} = "
      f"{recall_inpool:.1%}  CI = [{r_lo_i:.1%}, {r_hi_i:.1%}]")
print(f"  End-to-end novelty recall:  {k_recall}/{n_recall_e2e} = "
      f"{recall_e2e:.1%}  CI = [{r_lo_e:.1%}, {r_hi_e:.1%}]")
print(f"  End-to-end specificity:     {k_spec}/{n_spec} = "
      f"{specificity:.1%}  CI = [{s_lo:.1%}, {s_hi:.1%}]")
print(f"  Documented-FP catch:        {k_fp}/{n_fp} = "
      f"{fp_rate:.1%}  CI = [{fp_lo:.1%}, {fp_hi:.1%}]")
print()
print(f"Positives in pool retained:     {pos_retained.height}")
print(f"Positives correctly published:  {pos_published.height}")
print(f"Positives wrongly rejected:     {pos_fn.height}")
print(f"Positives not in pool:          {pos_notpool.height}")

if pos_fn.height > 0:
    print(f"\nWrongly-rejected positives (false negatives):")
    print(pos_fn.select(["source_id", "our_Name", "verdict", "v2_verdict"]))

if neg_kept.height > 0:
    print(f"\nEscaped imposters (false positives):")
    print(neg_kept.select(["source_id", "our_Name", "verdict", "v2_verdict"]))

# Save
with open(f"{REPO}/benchmark_output/independent_metrics_summary.txt", "w") as f:
    f.write(f"INDEPENDENT BENCHMARK — Marcussen+Albrecht 2023 + Gaia FP truth set\n")
    f.write(f"=" * 75 + "\n\n")
    f.write(f"This truth set is INDEPENDENT of Sahlmann 2025.\n")
    f.write(f"Positives: {pos.height} (CONFIRMED_PLANET, CONFIRMED_BD, "
            f"PLANET_LIT_PRIOR, PLANET_RV_INCONSISTENT from Marcussen)\n")
    f.write(f"Negatives: {neg.height} (STELLAR_IMPOSTER from Marcussen)\n")
    f.write(f"DOCUMENTED_FP: {fps_t.height} (Gaia DR3 known-issues)\n\n")
    f.write(f"v2 cascade metrics on independent truth set:\n")
    f.write(f"  In-pool novelty recall:     "
            f"{k_recall}/{n_recall_inpool} = {recall_inpool:.1%}  "
            f"95% CI [{r_lo_i:.1%}, {r_hi_i:.1%}]\n")
    f.write(f"  End-to-end novelty recall:  "
            f"{k_recall}/{n_recall_e2e} = {recall_e2e:.1%}  "
            f"95% CI [{r_lo_e:.1%}, {r_hi_e:.1%}]\n")
    f.write(f"  End-to-end specificity:     "
            f"{k_spec}/{n_spec} = {specificity:.1%}  "
            f"95% CI [{s_lo:.1%}, {s_hi:.1%}]\n")
    f.write(f"  Documented-FP catch:        "
            f"{k_fp}/{n_fp} = {fp_rate:.1%}  "
            f"95% CI [{fp_lo:.1%}, {fp_hi:.1%}]\n")

print(f"\nWrote independent benchmark summary to "
      f"{REPO}/benchmark_output/independent_metrics_summary.txt")
