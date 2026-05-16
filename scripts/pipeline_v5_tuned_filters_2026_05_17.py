"""Pipeline v5 — additional independent-data filters (2026-05-17).

Three new filters tested against the combined Halbwachs + Marcussen
independent truth set:

  Filter #33-conservative: Halbwachs direct-method published companion
    REJECT if source is in I/360/binmass with one of:
      {SB2+M1, AstroSpectroSB1+M1, EclipsingSpectro+M1,
       Orbital+SB2, Eclipsing+SB1+M1, Eclipsing+SB2,
       EclipsingSpectro(SB2)}
    AND M2 >= 0.0764 Msun (>80 MJ — stellar)
    These methods use direct spectroscopic mass-ratio + M_1 prior
    (independent of our cascade's astrometric mass estimation).

  Filter #33-aggressive: Halbwachs ALL methods published companion
    REJECT if source is in I/360/binmass with any method AND M2 >= 0.0764.
    Includes indirect methods (Orbital+M1, SB1+M1) which use the same
    physics as our cascade — partly circular but DPAC has better M_1
    priors and quality flags. Marked as v5+aggressive for explicit
    opt-in.

  Filter #34: Trifonov 2025 HIRES RV-variable flag
    For HIP-named sources in Trifonov 2025 HIRES Levy survey, the K_1
    has been independently measured to ~10 m/s precision. If their K_1
    indicates stellar M_2 (>= 80 MJ) at face-on, REJECT.
    Catches sources where archival HIRES caught the SB1/SB2 nature
    independently of NSS.

  Stage 1 retightening (parametric):
    Stricter face-on M_2 pool entry cut. Currently any source with
    face_on_M_2 < ~1500 MJ enters the pool. Tightening to face_on < 200
    AND marginalized < 1000 should keep all of our 9 candidates but
    catch most of the Halbwachs-stellar SURVIVOR escapes.
    The 4 BD+ / HD multi-body candidates have face_on_M_2 < 200,
    so they survive.
"""
from __future__ import annotations

from pathlib import Path

import polars as pl

# ============================================================
# Filter #33 thresholds
# ============================================================

HALBWACHS_DIRECT_METHODS = frozenset({
    "SB2+M1",
    "AstroSpectroSB1+M1",
    "EclipsingSpectro+M1",
    "Orbital+SB2",
    "Eclipsing+SB1+M1",
    "Eclipsing+SB2",
    "EclipsingSpectro(SB2)",
})

# All Halbwachs methods (for aggressive variant)
HALBWACHS_ALL_METHODS_WITH_M2 = frozenset({
    "Orbital+M1",
    "SB1+M1",
    "AstroSpectroSB1+M1",
    "SB2+M1",
    "Orbital+SB1+M1",
    "Eclipsing+SB1+M1",
    "EclipsingSpectro+M1",
    "Eclipsing+SB2",
    "Orbital+SB2",
    "EclipsingSpectro(SB2)",
})

# Substellar threshold in solar masses
M_SUBSTELLAR_MAX = 0.0764  # = 80 MJ

# Stage 1 retightening thresholds (parametric — make conservative
# enough that our 9 substellar candidates survive)
V5_STAGE1_FACE_ON_MAX_MJ = 200.0
V5_STAGE1_MARGINALIZED_MAX_MJ = 1000.0


def apply_v5_filters(
    v4_pool: pl.DataFrame,
    halbwachs: pl.DataFrame,
    halbwachs_aggressive: bool = False,
    apply_stage1_retighten: bool = False,
) -> pl.DataFrame:
    """Apply v5 filters on top of v4 verdicts.

    Returns v4 pool with a new `v5_verdict` column.
    """
    # Halbwachs cross-match
    methods_to_use = (
        HALBWACHS_ALL_METHODS_WITH_M2 if halbwachs_aggressive
        else HALBWACHS_DIRECT_METHODS
    )
    # Strip trailing whitespace from Method column (Vizier TSV padding)
    halbwachs = halbwachs.with_columns(
        pl.col("Method").str.strip_chars()
    )
    # Clean Halbwachs: keep only direct-method entries with stellar M_2
    hb = halbwachs.filter(
        pl.col("M2").is_not_null() &
        (pl.col("M2") >= M_SUBSTELLAR_MAX) &
        pl.col("Method").is_in(list(methods_to_use))
    ).select([
        pl.col("Source").cast(pl.Int64).alias("source_id"),
        pl.col("M2").alias("hb_M2_msun"),
        pl.col("Method").alias("hb_method"),
    ])

    print(f"  Halbwachs filter targets "
          f"({'aggressive' if halbwachs_aggressive else 'conservative'}): "
          f"{hb.height} sources with M_2 >= {M_SUBSTELLAR_MAX} Msun")

    # Join
    pool = v4_pool.with_columns(pl.col("source_id").cast(pl.Int64))
    pool = pool.join(hb, on="source_id", how="left")
    pool = pool.with_columns(
        pl.col("hb_M2_msun").is_not_null().alias("hb_stellar_match")
    )

    # Apply v5 verdict logic
    def reclass(r: dict) -> str:
        v4v = r.get("v4_verdict") or r.get("v3_verdict") or r.get("v2_verdict")
        # Filter #33: Halbwachs binary_masses cross-match
        if r.get("hb_stellar_match"):
            # Only override weak-tier verdicts (preserve REJECTED_published/_documented_fp)
            if v4v in {
                "SURVIVOR_no_hgca_corroboration",
                "FLAG_hgca_mass_ambiguous",
                "CORROBORATED_real_companion",  # also reject if DPAC says stellar
            }:
                return "REJECTED_halbwachs_dpac_stellar"
        # Filter #Stage1: tighter face-on M_2 cut (only on weak-tier)
        if apply_stage1_retighten and v4v in {
            "SURVIVOR_no_hgca_corroboration", "FLAG_hgca_mass_ambiguous"
        }:
            face = r.get("M_2_mjup_face_on")
            marg = r.get("M_2_mjup_marginalized")
            if (face is not None and face > V5_STAGE1_FACE_ON_MAX_MJ and
                    marg is not None and marg > V5_STAGE1_MARGINALIZED_MAX_MJ):
                return "REJECTED_v5_stage1_stellar_mass"
        return v4v

    pool = pool.with_columns(
        pl.struct(pool.columns).map_elements(
            reclass, return_dtype=pl.Utf8
        ).alias("v5_verdict")
    )
    return pool


if __name__ == "__main__":
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument("--v4-pool", required=True)
    p.add_argument("--halbwachs", required=True)
    p.add_argument("--out", required=True)
    p.add_argument("--aggressive", action="store_true",
                   help="Use Halbwachs ALL methods (incl. indirect)")
    p.add_argument("--stage1", action="store_true",
                   help="Apply Stage 1 retightening")
    args = p.parse_args()

    v4 = pl.read_csv(args.v4_pool)
    hb = pl.read_csv(args.halbwachs, schema_overrides={"Source": pl.Int64})
    for c in ["M1", "e_M1", "E_M1", "M2", "e_M2", "E_M2", "FluxRatio"]:
        if c in hb.columns and hb[c].dtype == pl.Utf8:
            hb = hb.with_columns(pl.col(c).str.strip_chars().cast(pl.Float64, strict=False))

    v5 = apply_v5_filters(v4, hb, args.aggressive, args.stage1)
    v5.write_csv(args.out)

    prev = "v4_verdict"
    n_changed = v5.filter(pl.col(prev) != pl.col("v5_verdict")).height
    print(f"\nWrote {args.out} ({v5.height} rows; {n_changed} reclassified)")
    print(f"\n{prev} → v5 transitions:")
    print(v5.filter(pl.col(prev) != pl.col("v5_verdict")).group_by(
        [prev, "v5_verdict"]
    ).agg(pl.len().alias("n")).sort("n", descending=True))
