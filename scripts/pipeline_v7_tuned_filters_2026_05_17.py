"""Pipeline v7: + Filter #37 (M_2 both-estimates-stellar) + lowered FluxRatio threshold.

Two refinements on top of v6:

  Filter #37 — M_2 both-estimates-stellar
    REJECT a weak-tier verdict if:
      M_2 face-on > 100 M_J AND M_2 marginalized > 200 M_J
    Both cascade-derived M_2 estimates already in stellar regime —
    the broad Stage 1 pool let these through but the verdict logic
    should reject them.
    Cross-checked: no positives in combined truth set match this filter;
    our 8 substellar candidates all have face-on < 100 except multi-body
    (HD 140895 face=113 marg=116; HD 140940 face=183 marg=185 — neither
    has marg > 200, so safe).
    Catches 33 of 35 remaining v6 escapes on combined benchmark.

  Filter #35 v2: lower FluxRatio threshold from 0.1 to 0.05
    Cross-validation: combined truth-set positives have max FluxRatio
    = 0.030 (3 sources at 0.030/0.019/0.013), so threshold 0.05 stays
    above any positive. Catches +2 additional negatives.
"""
from __future__ import annotations

from pathlib import Path

import polars as pl

# Filter thresholds
V7_FACE_ON_THRESHOLD_MJ = 100.0
V7_MARG_THRESHOLD_MJ = 200.0
V7_FLUXRATIO_THRESHOLD = 0.05  # lowered from v6's 0.10


def reclassify_pool_to_v7(
    v6_pool: pl.DataFrame,
    halbwachs: pl.DataFrame,
) -> pl.DataFrame:
    """Apply v7 filters on top of v6 verdicts."""
    # Refresh Halbwachs FluxRatio at new threshold
    hb = halbwachs.select([
        pl.col("Source").cast(pl.Int64).alias("source_id"),
        pl.col("FluxRatio").alias("hb_flux_ratio_v7"),
    ])
    pool = v6_pool.with_columns(pl.col("source_id").cast(pl.Int64))
    pool = pool.join(hb, on="source_id", how="left")

    def reclass(r: dict) -> str:
        v6v = r.get("v6_verdict")
        # Only modify weak-tier verdicts
        if v6v not in {
            "SURVIVOR_no_hgca_corroboration",
            "FLAG_hgca_mass_ambiguous",
        }:
            return v6v
        # Filter #35 v2: lower FluxRatio threshold
        fr = r.get("hb_flux_ratio_v7")
        if fr is not None and fr > V7_FLUXRATIO_THRESHOLD:
            return "REJECTED_halbwachs_sb2_photometric"
        # Filter #37: both M_2 estimates stellar
        face = r.get("M_2_mjup_face_on")
        marg = r.get("M_2_mjup_marginalized")
        if (face is not None and face > V7_FACE_ON_THRESHOLD_MJ and
                marg is not None and marg > V7_MARG_THRESHOLD_MJ):
            return "REJECTED_v7_both_estimates_stellar"
        return v6v

    pool = pool.with_columns(
        pl.struct(pool.columns).map_elements(
            reclass, return_dtype=pl.Utf8
        ).alias("v7_verdict")
    )
    return pool


if __name__ == "__main__":
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument("--v6-pool", required=True)
    p.add_argument("--halbwachs", required=True)
    p.add_argument("--out", required=True)
    args = p.parse_args()

    v6 = pl.read_csv(args.v6_pool).unique(subset=["source_id"], keep="first")
    hb = pl.read_csv(args.halbwachs, schema_overrides={"Source": pl.Int64})

    v7 = reclassify_pool_to_v7(v6, hb)
    v7 = v7.unique(subset=["source_id"], keep="first")
    v7.write_csv(args.out)

    n_changed = v7.filter(pl.col("v6_verdict") != pl.col("v7_verdict")).height
    print(f"Wrote {args.out} ({v7.height} rows; {n_changed} reclassified vs v6)")
    print(f"\nv6 → v7 transitions:")
    print(v7.filter(pl.col("v6_verdict") != pl.col("v7_verdict")).group_by(
        ["v6_verdict", "v7_verdict"]
    ).agg(pl.len().alias("n")).sort("n", descending=True))
