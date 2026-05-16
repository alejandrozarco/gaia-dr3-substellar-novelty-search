"""Run v4 cascade benchmark on BOTH Sahlmann and Independent (Marcussen) truth sets."""
from scipy import stats
import polars as pl

REPO = "/tmp/gaia-novelty-publication"
OUT_DIR = "/Users/legbatterij/claude_projects/ostinato/notes/2026-05-13-cascade-benchmark"

v4 = pl.read_csv(f"{REPO}/v4_scan_full_pool.csv")
print(f"Loaded v4 pool: {v4.height} rows")


def wilson(k, n, conf=0.95):
    if n == 0:
        return (0, 0)
    p = k / n
    z = stats.norm.ppf((1 + conf) / 2)
    z2 = z * z
    c = (p + z2 / (2 * n)) / (1 + z2 / n)
    h = z * ((p * (1 - p) / n + z2 / (4 * n * n)) ** 0.5) / (1 + z2 / n)
    return (max(0, c - h), min(1, c + h))


# ============================================================
# Sahlmann benchmark
# ============================================================

print("\n" + "=" * 70)
print("v4 BENCHMARK on Sahlmann-derived truth set (n=71)")
print("=" * 70)

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

# Join v4 verdicts
v4_join = v4.select([pl.col("source_id").cast(pl.Int64), "v4_verdict"])
truth_hc = truth_hc.with_columns(pl.col("source_id").cast(pl.Int64))
truth_hc = truth_hc.join(v4_join, on="source_id", how="left")


def classify(v):
    if v is None or v == "__NULL__":
        return "NOT_IN_POOL"
    if v == "CORROBORATED_real_companion":
        return "RETAINED_STRONG"
    if v in {"FLAG_hgca_mass_ambiguous", "SURVIVOR_no_hgca_corroboration"}:
        return "RETAINED_WEAK"
    if v == "REJECTED_published_nasa_exo":
        return "REJECTED_AS_PUBLISHED"
    if v == "REJECTED_hgca_stellar":
        return "REJECTED_AS_STELLAR"
    if v == "REJECTED_sb2_low_face_on_no_corroboration":
        return "REJECTED_AS_SB2_IMPOSTER"
    if v.startswith("REJECTED_"):
        return "REJECTED_OTHER"
    return "OTHER"


truth_hc = truth_hc.with_columns(
    pl.col("v4_verdict").fill_null("__NULL__").map_elements(
        classify, return_dtype=pl.Utf8
    ).alias("retention_class")
)

pos = truth_hc.filter(pl.col("truth_bucket") == "POSITIVE")
pos_retained = pos.filter(
    pl.col("retention_class").is_in(["RETAINED_STRONG", "RETAINED_WEAK"])
)
pos_published = pos.filter(pl.col("retention_class") == "REJECTED_AS_PUBLISHED")
pos_fn = pos.filter(pl.col("retention_class").is_in([
    "REJECTED_OTHER", "REJECTED_AS_STELLAR", "REJECTED_AS_SB2_IMPOSTER"
]))
pos_notpool = pos.filter(pl.col("retention_class") == "NOT_IN_POOL")

neg = truth_hc.filter(pl.col("truth_bucket") == "NEGATIVE")
neg_excluded = neg.filter(pl.col("retention_class").is_in([
    "NOT_IN_POOL", "REJECTED_OTHER", "REJECTED_AS_STELLAR",
    "REJECTED_AS_PUBLISHED", "REJECTED_AS_SB2_IMPOSTER"
]))
neg_kept = neg.filter(
    pl.col("retention_class").is_in(["RETAINED_STRONG", "RETAINED_WEAK"])
)

fps_t = truth_hc.filter(pl.col("truth_bucket") == "DOCUMENTED_FP")
fps_caught = fps_t.filter(pl.col("retention_class") == "NOT_IN_POOL")

k_recall_inpool = pos_retained.height
n_recall_inpool = pos_retained.height + pos_fn.height
k_recall_e2e = pos_retained.height
n_recall_e2e = pos_retained.height + pos_fn.height + pos_notpool.height

ri_lo, ri_hi = wilson(k_recall_inpool, n_recall_inpool)
re_lo, re_hi = wilson(k_recall_e2e, n_recall_e2e)
s_lo, s_hi = wilson(neg_excluded.height, neg.height)
fp_lo, fp_hi = wilson(fps_caught.height, fps_t.height)

print(f"  In-pool novelty recall: {k_recall_inpool}/{n_recall_inpool} = "
      f"{k_recall_inpool / max(n_recall_inpool, 1):.1%}  CI = [{ri_lo:.1%}, {ri_hi:.1%}]")
print(f"  E2E novelty recall:     {k_recall_e2e}/{n_recall_e2e} = "
      f"{k_recall_e2e / max(n_recall_e2e, 1):.1%}  CI = [{re_lo:.1%}, {re_hi:.1%}]")
print(f"  E2E specificity:        {neg_excluded.height}/{neg.height} = "
      f"{neg_excluded.height / max(neg.height, 1):.1%}  CI = [{s_lo:.1%}, {s_hi:.1%}]")
print(f"  Documented-FP catch:    {fps_caught.height}/{fps_t.height} = "
      f"{fps_caught.height / max(fps_t.height, 1):.1%}  CI = [{fp_lo:.1%}, {fp_hi:.1%}]")
print()
print(f"  False negatives (positives wrongly rejected):")
if pos_fn.height > 0:
    print(pos_fn.select(["source_id", "name", "verdict", "v4_verdict"]).head(20))
else:
    print("  (none)")
print()
print(f"  Specificity comparison: v3 was 72.7% / v4 is "
      f"{neg_excluded.height / max(neg.height, 1):.1%}")

# ============================================================
# Independent benchmark
# ============================================================

print("\n" + "=" * 70)
print("v4 BENCHMARK on INDEPENDENT (Marcussen+Albrecht 2023) truth set")
print("=" * 70)

truth_i = pl.read_csv(f"{REPO}/benchmark_output/truth_set_independent.csv")
truth_i = truth_i.with_columns(pl.col("source_id").cast(pl.Int64))
truth_i = truth_i.join(v4_join, on="source_id", how="left")
truth_i = truth_i.with_columns(
    pl.col("v4_verdict").fill_null("__NULL__").map_elements(
        classify, return_dtype=pl.Utf8
    ).alias("retention_class")
)

pos_i = truth_i.filter(pl.col("truth_bucket") == "POSITIVE")
pos_i_retained = pos_i.filter(
    pl.col("retention_class").is_in(["RETAINED_STRONG", "RETAINED_WEAK"])
)
pos_i_published = pos_i.filter(
    pl.col("retention_class") == "REJECTED_AS_PUBLISHED"
)
pos_i_fn = pos_i.filter(pl.col("retention_class").is_in([
    "REJECTED_OTHER", "REJECTED_AS_STELLAR", "REJECTED_AS_SB2_IMPOSTER"
]))
neg_i = truth_i.filter(pl.col("truth_bucket") == "NEGATIVE")
neg_i_excluded = neg_i.filter(pl.col("retention_class").is_in([
    "NOT_IN_POOL", "REJECTED_OTHER", "REJECTED_AS_STELLAR",
    "REJECTED_AS_PUBLISHED", "REJECTED_AS_SB2_IMPOSTER"
]))
neg_i_kept = neg_i.filter(
    pl.col("retention_class").is_in(["RETAINED_STRONG", "RETAINED_WEAK"])
)

correct_pos_i = pos_i_retained.height + pos_i_published.height
n_pos_i = pos_i.height
cp_lo, cp_hi = wilson(correct_pos_i, n_pos_i)
si_lo, si_hi = wilson(neg_i_excluded.height, neg_i.height)

print(f"  Positives correctly handled: {correct_pos_i}/{n_pos_i} = "
      f"{correct_pos_i / max(n_pos_i, 1):.1%}  CI = [{cp_lo:.1%}, {cp_hi:.1%}]")
print(f"  Positives wrongly rejected:  {pos_i_fn.height}/{n_pos_i}")
print(f"  Specificity:                 {neg_i_excluded.height}/{neg_i.height} = "
      f"{neg_i_excluded.height / max(neg_i.height, 1):.1%}  CI = [{si_lo:.1%}, {si_hi:.1%}]")

print(f"\nIndependent specificity comparison: v3 was 20% / v4 is "
      f"{neg_i_excluded.height / max(neg_i.height, 1):.1%}")
print(f"\nEscaped imposters (false positives):")
if neg_i_kept.height > 0:
    print(neg_i_kept.select(["source_id", "our_Name", "verdict", "v4_verdict"]))
else:
    print("  (none — all 5 Marcussen imposters now rejected)")
