"""Assemble the frozen independent negative control set + score specificity.

Per the spec (Independent Negative Control Set):
  - Tier A2: Gaia DR3 SB2/SB2C solutions for pool sources (K1+K2 measured ->
    luminous secondary). Disjoint from cascade filters. independence=within_gaia_distinct_method.
  - Tier A1: APOGEE SB2 (Kounkel 2021 J/AJ/162/184) ∩ pool. APOGEE is on the
    RV-input blocklist but the SB2 *detection* (two line sets) is independent
    of APOGEE RV joint-fitting. independence=apogee_sb2_detection.

  FILTER_BLOCKLIST enforced per row. Frozen to negative_control.csv with
  provenance columns. Then the FROZEN cascade verdict (v2_verdict from
  v2_scan_full_pool.csv) is read off — no tuning — and specificity is
  computed with a Wilson 95% interval.
"""
from __future__ import annotations

import math
import sys
from pathlib import Path

import polars as pl

ROOT = Path("/tmp/gaia-novelty-publication")
INTER = ROOT / "data" / "intermediate"

FILTER_BLOCKLIST = {
    "sahlmann2025", "hgca_brandt2024", "kervella2022_pma", "wds", "orb6",
    "sb9", "tokovinin_msc", "galah", "trifonov2025", "halbwachs2023_masses",
    "halbwachs_holl2024", "nasa_exo", "exoplanet_eu", "simbad",
    "harps", "hires", "apogee", "carmenes", "lamost", "tess_rot", "gaia_var",
}
# label_source values we WILL use (these are NOT in the blocklist):
#   gaia_dr3_sb2  -> the Gaia NSS SB2/SB2C spectroscopic channel (cascade
#                    never filters on it; distinct from the astrometric pool)
#   apogee_sb2_detection -> the FACT of two line sets in APOGEE, not the RVs.
#                    Documented exception (see spec 3a/8). NB: this is the
#                    SB2-detection label, deliberately tagged so it can be
#                    dropped for a maximally-pure run.


def wilson_ci(k, n, z=1.96):
    if n == 0:
        return (float("nan"), float("nan"), float("nan"))
    p = k / n
    denom = 1 + z**2 / n
    centre = (p + z**2 / (2 * n)) / denom
    half = (z * math.sqrt(p * (1 - p) / n + z**2 / (4 * n**2))) / denom
    return (p, centre - half, centre + half)


def main():
    pool = pl.read_csv(ROOT / "v2_scan_full_pool.csv", infer_schema_length=20000)

    # --- Tier A2: Gaia SB2/SB2C ---
    a2 = pl.read_csv(INTER / "tierA2_gaia_sb2_in_pool.csv")
    a2 = a2.with_columns([
        pl.lit("gaia_dr3_sb2").alias("label_source"),
        pl.lit("gaia_nss").alias("instrument"),
        pl.lit("within_gaia_distinct_method").alias("independence"),
        pl.col("nss_solution_type").alias("M2_method_detail"),
    ]).select([
        pl.col("source_id").alias("gaia_dr3_id"),
        "label_source", "instrument", "independence",
        pl.lit("SB2_K1K2_both_measured").alias("M2_method"),
        pl.col("semi_amplitude_primary").alias("K1_kms"),
        pl.col("semi_amplitude_secondary").alias("K2_kms"),
        pl.col("period").alias("sb2_period_d"),
    ])

    # --- Tier A1: APOGEE SB2 ---
    a1 = pl.read_csv(INTER / "tierA1_apogee_sb2_in_pool.csv")
    a1 = a1.select([
        pl.col("source_id").alias("gaia_dr3_id"),
        pl.lit("apogee_sb2_detection").alias("label_source"),
        pl.lit("apogee").alias("instrument"),
        pl.lit("apogee_sb2_detection").alias("independence"),
        pl.lit("SB2_two_line_sets_SBn>=2").alias("M2_method"),
        pl.lit(None, dtype=pl.Float64).alias("K1_kms"),
        pl.lit(None, dtype=pl.Float64).alias("K2_kms"),
        pl.col("Per").alias("sb2_period_d"),
        pl.col("qW").alias("apogee_qW"),
        pl.col("SBn").alias("apogee_SBn"),
    ])

    # Combine; A2 takes priority where a source is in both (strictly-disjoint
    # label preferred over the asterisked APOGEE one)
    a2_ids = set(a2["gaia_dr3_id"].to_list())
    a1_only = a1.filter(~pl.col("gaia_dr3_id").is_in(list(a2_ids)))
    overlap_count = a1.filter(pl.col("gaia_dr3_id").is_in(list(a2_ids))).height
    print(f"Tier A2 (Gaia SB2): {len(a2)}")
    print(f"Tier A1 (APOGEE SB2): {len(a1)}  (of which {overlap_count} also in A2)")

    # Harmonize columns
    a2 = a2.with_columns([
        pl.lit(None, dtype=pl.Float64).alias("apogee_qW"),
        pl.lit(None, dtype=pl.Int64).alias("apogee_SBn"),
    ])
    a1_only = a1_only.with_columns([
        pl.col("apogee_SBn").cast(pl.Int64),
        pl.col("sb2_period_d").cast(pl.Float64, strict=False),
    ])
    a2 = a2.with_columns(pl.col("sb2_period_d").cast(pl.Float64, strict=False))
    neg = pl.concat([a2, a1_only], how="diagonal")

    # Enforce FILTER_BLOCKLIST
    bad = neg.filter(pl.col("label_source").is_in(list(FILTER_BLOCKLIST)))
    assert bad.is_empty(), f"BLOCKLIST VIOLATION: {bad['gaia_dr3_id'].to_list()}"
    print(f"\nBlocklist check passed. Combined unique negatives: {len(neg)}")

    # Mark in_pool (all are, by construction) + attach pool fields + verdict
    poolsel = pool.select([
        "source_id", "nss_solution_type", "period_d",
        "M_2_mjup_marginalized", "M_2_2sigma_hi", "Name", "HIP",
        "v2_verdict",
    ]).rename({"source_id": "gaia_dr3_id",
                "nss_solution_type": "pool_solution_type",
                "period_d": "pool_period_d"})
    # Strict in-pool assertion: drop coordinate-match artifacts whose
    # recorded source_id is not actually a pool source_id. (APOGEE 2MASS
    # epoch-2000 positions vs Gaia epoch-2016 without PM correction produce
    # some spurious 2" matches; the official 2MASSxGaia PM-aware xmatch would
    # recover these, documented as a limitation of the APOGEE tier.)
    pool_id_set = set(int(x) for x in pool["source_id"].to_list())
    before = len(neg)
    neg = neg.filter(pl.col("gaia_dr3_id").is_in(list(pool_id_set)))
    dropped = before - len(neg)
    print(f"Dropped {dropped} coordinate-match artifacts not in pool "
          f"(all APOGEE tier). Clean in-pool negatives: {len(neg)}")
    neg = neg.join(poolsel, on="gaia_dr3_id", how="left")
    neg = neg.with_columns(pl.lit(True).alias("in_pool"))

    # fp_tier: SB2 with K2 measured (Gaia) = unambiguous stellar.
    #          APOGEE SB2 detection = stellar. None are mass_ambiguous because
    #          the SB2 detection itself (two luminous components) is the label,
    #          independent of the astrometric mass estimate.
    neg = neg.with_columns(pl.lit("stellar_sb2_unambiguous").alias("fp_tier"))

    # Freeze
    out_cols = ["gaia_dr3_id", "in_pool", "Name", "HIP",
                 "pool_solution_type", "pool_period_d",
                 "M_2_mjup_marginalized", "M_2_2sigma_hi",
                 "label_source", "instrument", "independence", "M2_method",
                 "K1_kms", "K2_kms", "sb2_period_d", "apogee_qW", "apogee_SBn",
                 "fp_tier", "v2_verdict"]
    neg = neg.select([c for c in out_cols if c in neg.columns])
    neg.write_csv(ROOT / "negative_control.csv")
    print(f"Frozen -> negative_control.csv ({len(neg)} rows)")

    # ===== SCORING (frozen cascade verdict, no tuning) =====
    def score(subset, label):
        rej = subset.filter(pl.col("v2_verdict").str.starts_with("REJECTED")).height
        nn = len(subset)
        p, lo, hi = wilson_ci(rej, nn)
        print(f"\n[{label}] n={nn}, rejected={rej}, "
              f"specificity={p:.3f} (Wilson 95% CI {lo:.3f}-{hi:.3f}, "
              f"±{(hi-lo)/2*100:.0f} pp)")
        return p, lo, hi

    print("\n=== SPECIFICITY (out-of-sample, leak-free negatives) ===")
    # Strictly-disjoint headline tier: Gaia SB2 only
    gaia_sb2 = neg.filter(pl.col("label_source") == "gaia_dr3_sb2")
    score(gaia_sb2, "Gaia-SB2 (strictly disjoint) — HEADLINE")
    score(neg, "Combined (Gaia-SB2 + APOGEE-SB2 asterisked)")

    rejected = neg.filter(pl.col("v2_verdict").str.starts_with("REJECTED"))
    escaped = neg.filter(~pl.col("v2_verdict").str.starts_with("REJECTED"))

    print("\n--- Per-filter credit (which reject reason caught each) ---")
    print(rejected.group_by("v2_verdict").len().sort("len", descending=True).to_pandas().to_string())

    print(f"\n--- ESCAPES ({len(escaped)}): leak-free negatives the cascade FAILED to reject ---")
    print(escaped.select(["gaia_dr3_id", "Name", "pool_solution_type",
                            "M_2_mjup_marginalized", "label_source",
                            "K1_kms", "K2_kms", "v2_verdict"]).to_pandas().to_string())

    # Highlight: escapes that are in the headline list
    head = pl.read_csv(ROOT / "novelty_candidates.csv")
    head_ids = set(int(x) for x in head["gaia_dr3_source_id"].drop_nulls().to_list())
    esc_head = escaped.filter(pl.col("gaia_dr3_id").is_in(list(head_ids)))
    if not esc_head.is_empty():
        print(f"\n*** {len(esc_head)} ESCAPE(S) ARE IN THE HEADLINE LIST — false positives: ***")
        for r in esc_head.iter_rows(named=True):
            print(f"    {r['Name']} (Gaia {r['gaia_dr3_id']}): "
                  f"Gaia SB2 K1={r['K1_kms']}, K2={r['K2_kms']} -> stellar")


if __name__ == "__main__":
    sys.exit(main() or 0)
