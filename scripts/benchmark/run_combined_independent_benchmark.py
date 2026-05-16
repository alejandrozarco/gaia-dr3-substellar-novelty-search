"""Combined independent benchmark: Marcussen + Halbwachs (both non-Sahlmann).

Builds the largest independent truth set we can assemble from cached
catalogs:
  * Marcussen & Albrecht 2023 (AJ 165, 266): 15 high-conf entries
    (10 positives + 5 negatives + 4 documented FPs)
  * Halbwachs / Gaia DR3 binary_masses (I/360/binmass): ~120 entries
    in our v2 pool (23 substellar positives, 82 stellar negatives)
  * Deduplicate sources appearing in both

Reports v4 cascade metrics on the combined set with 95% Wilson CIs.
"""
from scipy import stats
import polars as pl

OUT_DIR = "/Users/legbatterij/claude_projects/ostinato/notes/2026-05-13-cascade-benchmark"
REPO = "/tmp/gaia-novelty-publication"


def wilson(k, n, conf=0.95):
    if n == 0:
        return (0, 0)
    p = k / n
    z = stats.norm.ppf((1 + conf) / 2)
    z2 = z * z
    c = (p + z2 / (2 * n)) / (1 + z2 / n)
    h = z * ((p * (1 - p) / n + z2 / (4 * n * n)) ** 0.5) / (1 + z2 / n)
    return (max(0, c - h), min(1, c + h))


# Load truth sets
marc = pl.read_csv(f"{REPO}/benchmark_output/truth_set_independent.csv")
halb = pl.read_csv(f"{REPO}/benchmark_output/truth_set_halbwachs.csv")
v4 = pl.read_csv(f"{REPO}/v4_scan_full_pool.csv")

print(f"Marcussen truth set:        {marc.height} rows (in pool: "
      f"{marc.filter(pl.col('v2_verdict').is_not_null()).height})")
print(f"Halbwachs truth set:        {halb.height} rows")

# Align schemas: build a common minimal schema
def align(df, src_label):
    cols = ["source_id", "Name", "truth_bucket"]
    if "v4_verdict" in df.columns:
        cols.append("v4_verdict")
    elif "v2_verdict" in df.columns:
        cols.append("v2_verdict")
    return df.select(cols).with_columns(pl.lit(src_label).alias("source_label"))


# Build both with the same column structure
# Halbwachs: has v4_verdict already
halb_a = halb.select(["source_id", "Name", "truth_bucket", "v4_verdict"]).with_columns(
    pl.lit("Halbwachs").alias("source_label")
)

# Marcussen: needs v4 lookup
marc_a = marc.with_columns(
    pl.col("our_Name").fill_null("").alias("Name")
).select(["source_id", "Name", "truth_bucket"]).join(
    v4.select(["source_id", "v4_verdict"]),
    on="source_id", how="left"
).with_columns(pl.lit("Marcussen").alias("source_label"))

# Filter out DOCUMENTED_FP rows from Marcussen for cleaner combined truth set
marc_a = marc_a.filter(pl.col("truth_bucket") != "DOCUMENTED_FP")

# Cast source_id to same dtype
halb_a = halb_a.with_columns(pl.col("source_id").cast(pl.Int64))
marc_a = marc_a.with_columns(pl.col("source_id").cast(pl.Int64))

# Combine; dedup keeping Halbwachs (more entries, gold-standard masses)
combined = pl.concat([halb_a, marc_a], how="vertical_relaxed").unique(
    subset=["source_id"], keep="first"
)
print(f"\nCombined (deduped) truth set: {combined.height} rows")
print(combined.group_by("truth_bucket").len().sort("truth_bucket"))

# Classify v4 verdicts
RETAINED_STRONG = {"CORROBORATED_real_companion"}
RETAINED_WEAK = {"FLAG_hgca_mass_ambiguous", "SURVIVOR_no_hgca_corroboration"}
CORRECT_REJ_PUB = {"REJECTED_published_nasa_exo"}
CORRECT_REJ_STELLAR = {"REJECTED_hgca_stellar"}
CORRECT_REJ_SB2 = {"REJECTED_sb2_low_face_on_no_corroboration"}


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
    if v in CORRECT_REJ_SB2:
        return "REJECTED_AS_SB2"
    if v.startswith("REJECTED_"):
        return "REJECTED_OTHER"
    return "OTHER"


combined = combined.with_columns(
    pl.col("v4_verdict").fill_null("__NULL__").map_elements(
        classify, return_dtype=pl.Utf8
    ).alias("retention_class")
)

print()
print("=" * 75)
print("Combined truth set v4 confusion matrix")
print("=" * 75)
conf = combined.group_by(["truth_bucket", "retention_class"]).agg(
    pl.len().alias("n")
).pivot(on="retention_class", index="truth_bucket", values="n").fill_null(0)
print(conf)

# Metrics
pos = combined.filter(pl.col("truth_bucket") == "POSITIVE")
pos_retained = pos.filter(
    pl.col("retention_class").is_in(["RETAINED_STRONG", "RETAINED_WEAK"])
)
pos_published = pos.filter(
    pl.col("retention_class") == "REJECTED_AS_PUBLISHED"
)
pos_fn = pos.filter(pl.col("retention_class").is_in([
    "REJECTED_OTHER", "REJECTED_AS_STELLAR", "REJECTED_AS_SB2"
]))
pos_notpool = pos.filter(pl.col("retention_class") == "NOT_IN_POOL")

neg = combined.filter(pl.col("truth_bucket") == "NEGATIVE")
neg_excluded = neg.filter(pl.col("retention_class").is_in([
    "NOT_IN_POOL", "REJECTED_OTHER", "REJECTED_AS_STELLAR",
    "REJECTED_AS_PUBLISHED", "REJECTED_AS_SB2"
]))
neg_kept = neg.filter(
    pl.col("retention_class").is_in(["RETAINED_STRONG", "RETAINED_WEAK"])
)

# For positives, "correctly handled" = retained-novel OR rejected-as-published
correct_pos = pos_retained.height + pos_published.height
ch_lo, ch_hi = wilson(correct_pos, pos.height)
sp_lo, sp_hi = wilson(neg_excluded.height, neg.height)

# Retention recall (excludes published since those are correctly rejected)
r_lo, r_hi = wilson(pos_retained.height, pos_retained.height + pos_fn.height)

print()
print("=" * 75)
print(f"v4 cascade on COMBINED INDEPENDENT truth set "
      f"(n={pos.height} pos + {neg.height} neg)")
print("=" * 75)
print(f"  Positives correctly handled (retained or rejected-published):")
print(f"    {correct_pos}/{pos.height} = "
      f"{correct_pos / pos.height:.1%}  95% CI [{ch_lo:.1%}, {ch_hi:.1%}]")
print(f"  Positives retained as novel:")
print(f"    {pos_retained.height}/{pos_retained.height + pos_fn.height} = "
      f"{pos_retained.height / max(pos_retained.height + pos_fn.height, 1):.1%}  "
      f"95% CI [{r_lo:.1%}, {r_hi:.1%}]")
print(f"  Positives wrongly rejected (false neg): "
      f"{pos_fn.height}/{pos.height} = {pos_fn.height / pos.height:.1%}")
print(f"  Specificity (negatives excluded):")
print(f"    {neg_excluded.height}/{neg.height} = "
      f"{neg_excluded.height / neg.height:.1%}  "
      f"95% CI [{sp_lo:.1%}, {sp_hi:.1%}]")
print(f"  False positives (imposters escape):")
print(f"    {neg_kept.height}/{neg.height} = "
      f"{neg_kept.height / neg.height:.1%}")

# Save combined truth set
combined.write_csv(f"{REPO}/benchmark_output/truth_set_combined.csv")
combined.write_csv(f"{OUT_DIR}/truth_set_combined.csv")
print(f"\nSaved combined truth set ({combined.height} rows)")

# Where do the negatives escape?
print("\n" + "=" * 75)
print("False positives (imposters that escaped) — distribution by v4 verdict")
print("=" * 75)
print(neg_kept.group_by("v4_verdict").len().sort("len", descending=True))
