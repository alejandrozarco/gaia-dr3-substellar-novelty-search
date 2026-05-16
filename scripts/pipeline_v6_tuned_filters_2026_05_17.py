"""Pipeline v6: + FluxRatio + Trifonov filters (2026-05-17).

Two new filters layered on top of v5 (which had Halbwachs binary_masses
direct-method M_2 cross-match):

  Filter #35 — Halbwachs FluxRatio > 0.1 (photometric SB2 indicator)
    Halbwachs/Gaia DR3 binary_masses provides a photometric flux ratio
    L_2 / L_1 for sources where DPAC's joint fit could decompose the
    photometry. FluxRatio > 0.1 means the secondary is luminous enough
    to be detected — strong SB2 indicator.
    Empirical separation on combined truth set:
      - POSITIVES: 0/16 with FluxRatio > 0.1
      - NEGATIVES: 13/20 with FluxRatio > 0.1
    Clean separator — independent of mass-ratio physics.

  Filter #36 — Trifonov 2025 HIRES RV-variability (≥ 1000 m/s scatter)
    For HIP-named sources in Trifonov+ 2025 HIRES Levy DR1 survey,
    the per-target RV scatter (rvc_std_mps) is measured to ~10 m/s
    precision. rvc_std > 1000 m/s indicates strong RV variability
    consistent with stellar-mass companion.
    Only ~20 v2 pool sources overlap with Trifonov coverage (HIP-named
    only); modest impact but clean signal where applicable.

Both filters only affect weak-tier (SURVIVOR / FLAG) verdicts —
CORROBORATED and explicit REJECTED verdicts are preserved.
"""
from __future__ import annotations

from pathlib import Path

import polars as pl

# Filter thresholds
V6_FLUXRATIO_MAX = 0.1
V6_TRIFONOV_RVC_STD_THRESH = 1000.0  # m/s


def reclassify_pool_to_v6(
    v5_pool: pl.DataFrame,
    halbwachs: pl.DataFrame,
    trifonov: pl.DataFrame | None = None,
) -> pl.DataFrame:
    """Apply v6 filters on top of v5 verdicts."""
    # Halbwachs FluxRatio
    hb = halbwachs.select([
        pl.col("Source").cast(pl.Int64).alias("source_id"),
        pl.col("FluxRatio").alias("hb_flux_ratio"),
    ])
    pool = v5_pool.with_columns(pl.col("source_id").cast(pl.Int64))
    pool = pool.join(hb, on="source_id", how="left")

    # Trifonov RV-variability
    if trifonov is not None:
        tr = trifonov.select([
            "source_id",
            pl.col("trif_rvc_std_mps").alias("trif_rv_scatter_mps"),
        ]).with_columns(pl.col("source_id").cast(pl.Int64))
        pool = pool.join(tr, on="source_id", how="left")
    else:
        pool = pool.with_columns(pl.lit(None).alias("trif_rv_scatter_mps"))

    # Apply v6 reclassification
    def reclass(r: dict) -> str:
        v5v = r.get("v5_verdict")
        # Only modify weak-tier verdicts
        if v5v not in {
            "SURVIVOR_no_hgca_corroboration",
            "FLAG_hgca_mass_ambiguous",
        }:
            return v5v
        # Filter #35: FluxRatio > 0.1
        fr = r.get("hb_flux_ratio")
        if fr is not None and fr > V6_FLUXRATIO_MAX:
            return "REJECTED_halbwachs_sb2_photometric"
        # Filter #36: Trifonov RV variability
        rvc = r.get("trif_rv_scatter_mps")
        if rvc is not None and rvc > V6_TRIFONOV_RVC_STD_THRESH:
            return "REJECTED_trifonov_rv_variable"
        return v5v

    pool = pool.with_columns(
        pl.struct(pool.columns).map_elements(
            reclass, return_dtype=pl.Utf8
        ).alias("v6_verdict")
    )
    return pool


if __name__ == "__main__":
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument("--v5-pool", required=True)
    p.add_argument("--halbwachs", required=True)
    p.add_argument("--trifonov", default=None,
                   help="Optional Trifonov 2025 HIRES cross-match CSV")
    p.add_argument("--out", required=True)
    args = p.parse_args()

    v5 = pl.read_csv(args.v5_pool)
    hb = pl.read_csv(args.halbwachs, schema_overrides={"Source": pl.Int64})
    hb = hb.with_columns(pl.col("Method").str.strip_chars())

    tr = None
    if args.trifonov:
        tr = pl.read_csv(args.trifonov)
        if "Gaia" in tr.columns:
            tr = tr.rename({"Gaia": "source_id"})
        tr = tr.with_columns(pl.col("source_id").cast(pl.Int64, strict=False))

    v6 = reclassify_pool_to_v6(v5, hb, tr)
    v6.write_csv(args.out)

    n_changed = v6.filter(pl.col("v5_verdict") != pl.col("v6_verdict")).height
    print(f"Wrote {args.out} ({v6.height} rows; {n_changed} reclassified vs v5)")
    print(f"\nv5 → v6 transitions:")
    print(v6.filter(pl.col("v5_verdict") != pl.col("v6_verdict")).group_by(
        ["v5_verdict", "v6_verdict"]
    ).agg(pl.len().alias("n")).sort("n", descending=True))
