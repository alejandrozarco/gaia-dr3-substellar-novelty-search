"""v5 cascade benchmark: test conservative and aggressive variants
against Sahlmann + combined-independent truth sets, verify no recall loss
on our 9 substellar candidates.
"""
from scipy import stats
import polars as pl

REPO = "/tmp/gaia-novelty-publication"
OUT_DIR = "/Users/legbatterij/claude_projects/ostinato/notes/2026-05-13-cascade-benchmark"


def wilson(k, n, conf=0.95):
    if n == 0:
        return (0, 0)
    p = k / n
    z = stats.norm.ppf((1 + conf) / 2)
    z2 = z * z
    c = (p + z2 / (2 * n)) / (1 + z2 / n)
    h = z * ((p * (1 - p) / n + z2 / (4 * n * n)) ** 0.5) / (1 + z2 / n)
    return (max(0, c - h), min(1, c + h))


# Load v5 variants
v5_cons = pl.read_csv(f"{REPO}/v5_scan_conservative.csv").select([
    pl.col("source_id").cast(pl.Int64),
    pl.col("v5_verdict").alias("v5_cons_verdict"),
])
v5_aggr = pl.read_csv(f"{REPO}/v5_scan_full_pool.csv").select([
    pl.col("source_id").cast(pl.Int64),
    pl.col("v5_verdict").alias("v5_aggr_verdict"),
])

# Load truth sets
truth_sah = pl.read_csv(f"{OUT_DIR}/truth_set.csv").unique(
    subset=["source_id", "truth_bucket"], keep="first"
)
HIGH_CONF = {
    "CONFIRMED_BROWN_DWARF", "CONFIRMED_EXOPLANET", "HIGH_PROB_SUBSTELLAR",
    "SAHL_HIGH_PROB_BD_CAND", "SAHL_TOP_EXOPLANET_CAND",
    "SAHL_EXOPLANET_CAND", "SAHL_CONFIRMED_BD", "SAHL_BD_CAND",
    "CONFIRMED_BINARY_FP", "SAHL_FALSE_POSITIVE_BINARY",
    "VLMS_FP_NOT_SUBSTELLAR", "SAHL_VERY_LOW_MASS_STAR",
    "SAHL_LOW_MASS_STAR", "SAHL_RETRACTED_BY_GAIA",
    "GAIA_DR3_RETRACTED_FP", "documented_fp",
}
truth_sah = truth_sah.filter(pl.col("verdict").is_in(HIGH_CONF))
truth_sah = truth_sah.with_columns(pl.col("source_id").cast(pl.Int64))

truth_comb = pl.read_csv(f"{REPO}/benchmark_output/truth_set_combined.csv")
truth_comb = truth_comb.with_columns(pl.col("source_id").cast(pl.Int64))


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
    if v in {"REJECTED_sb2_low_face_on_no_corroboration",
              "REJECTED_halbwachs_dpac_stellar",
              "REJECTED_v5_stage1_stellar_mass"}:
        return "REJECTED_AS_STELLAR_IMPOSTER"
    if v.startswith("REJECTED_"):
        return "REJECTED_OTHER"
    return "OTHER"


def bench(truth, verdict_col, label):
    """Run benchmark on a truth set with given verdict column."""
    t = truth.with_columns(
        pl.col(verdict_col).fill_null("__NULL__").map_elements(
            classify, return_dtype=pl.Utf8
        ).alias("rc")
    )
    pos = t.filter(pl.col("truth_bucket") == "POSITIVE")
    neg = t.filter(pl.col("truth_bucket") == "NEGATIVE")
    pos_r = pos.filter(pl.col("rc").is_in(["RETAINED_STRONG", "RETAINED_WEAK"]))
    pos_p = pos.filter(pl.col("rc") == "REJECTED_AS_PUBLISHED")
    pos_fn = pos.filter(pl.col("rc").is_in([
        "REJECTED_OTHER", "REJECTED_AS_STELLAR",
        "REJECTED_AS_STELLAR_IMPOSTER",
    ]))
    pos_np = pos.filter(pl.col("rc") == "NOT_IN_POOL")
    neg_ex = neg.filter(pl.col("rc").is_in([
        "NOT_IN_POOL", "REJECTED_OTHER", "REJECTED_AS_STELLAR",
        "REJECTED_AS_PUBLISHED", "REJECTED_AS_STELLAR_IMPOSTER",
    ]))

    correct_pos = pos_r.height + pos_p.height
    cp_lo, cp_hi = wilson(correct_pos, pos.height)
    sp_lo, sp_hi = wilson(neg_ex.height, neg.height)
    r_lo, r_hi = wilson(pos_r.height, pos_r.height + pos_fn.height)

    print(f"\n{label} (truth: {pos.height} pos + {neg.height} neg)")
    print(f"  Correct pos:  {correct_pos}/{pos.height} = "
          f"{correct_pos / max(pos.height, 1):.1%}  CI [{cp_lo:.1%}, {cp_hi:.1%}]")
    print(f"  Retained (excl. published): "
          f"{pos_r.height}/{pos_r.height + pos_fn.height} = "
          f"{pos_r.height / max(pos_r.height + pos_fn.height, 1):.1%}  "
          f"CI [{r_lo:.1%}, {r_hi:.1%}]")
    print(f"  False neg:    {pos_fn.height}")
    print(f"  Specificity: {neg_ex.height}/{neg.height} = "
          f"{neg_ex.height / max(neg.height, 1):.1%}  CI [{sp_lo:.1%}, {sp_hi:.1%}]")
    return {
        "correct_pos_n": correct_pos, "pos_n": pos.height,
        "retained_n": pos_r.height,
        "fn_n": pos_fn.height,
        "spec_k": neg_ex.height, "spec_n": neg.height,
    }


# Attach v5 verdicts to each truth set
for ts_name, ts in [("Sahlmann", truth_sah), ("Combined", truth_comb)]:
    ts = ts.join(v5_cons, on="source_id", how="left").join(
        v5_aggr, on="source_id", how="left"
    )
    print(f"\n{'='*75}")
    print(f"BENCHMARK: {ts_name}")
    print(f"{'='*75}")
    bench(ts, "v5_cons_verdict", f"  v5-conservative on {ts_name}")
    bench(ts, "v5_aggr_verdict", f"  v5-aggressive+stage1 on {ts_name}")


# Verify our 9 candidates aren't affected
print(f"\n{'='*75}")
print("HEADLINE CANDIDATE VERDICT CHECK")
print(f"{'='*75}")
candidates = pl.read_csv(f"{REPO}/novelty_candidates.csv").select([
    pl.col("gaia_dr3_source_id").cast(pl.Int64).alias("source_id"),
    "name",
])
cand_v5c = candidates.join(v5_cons, on="source_id", how="left").join(
    v5_aggr, on="source_id", how="left"
)
print("Our 9 substellar candidates — v5 verdicts (should all retain):")
print(cand_v5c.select(["name", "v5_cons_verdict", "v5_aggr_verdict"]))
