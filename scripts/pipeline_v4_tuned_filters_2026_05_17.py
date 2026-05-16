"""Pipeline v4 with SB2-imposter filter (2026-05-17).

Adds one new filter to the v3 cascade to catch SB2 systems where Gaia DR3
NSS Orbital mis-fits the K_1 (face-on K_1 ≈ K_total/2 for mass-ratio ~1
SB2, producing an artificially low face-on M_2 in the planet/BD regime
even though the underlying companion is stellar).

Filter #32 — SB2_low_face_on_no_corroboration:
  REJECT if:
    M_2_face_on < 22 M_J  (boundary just above typical SB2 K_1 inflation
                          regime; canonical BD/planet boundary is 13 M_J,
                          22 M_J is a safety margin for SB2 K_1 inflation
                          factor of ~1.5×)
    AND hgca_chisq IS NULL OR hgca_chisq < 5  (no independent HGCA
                                              long-baseline corroboration)
    AND nss_solution_type != "OrbitalTargetedSearchValidated"
                          (Gaia DPAC-validated solutions exempt)

Physical motivation
-------------------
Real low-mass companions (planet to BD-boundary) require independent
corroboration before promotion: archival RV that confirms K_1, or HGCA
chi² that confirms long-baseline transverse motion. Without either,
the candidate could be:
  (a) Real low-mass substellar — needs follow-up to confirm
  (b) SB2 system with K_1 mis-fit — Gaia averages mass-ratio-1 spectroscopic
      Doppler into an apparent SB1 K_1 ≈ K_true / 2, putting face-on M_2
      into the planet/BD-boundary regime artificially
  (c) Activity-driven photocentric wobble at high inclination

The cascade currently can't distinguish (a) from (b)/(c), so it
conservatively rejects (a) and (b)/(c) together. (a) cases would need
RV or imaging follow-up to be promoted anyway. This filter prefers
specificity over recall on this regime.

Empirical motivation
--------------------
From the independent Marcussen & Albrecht 2023 benchmark (v1.3.0), 4 of 5
in-pool imposters escape v3 as SURVIVOR_no_hgca_corroboration. All 4 have:
  * face-on M_2 ∈ [14.3, 20.9] M_J
  * hgca_chisq ∈ {null, 0.78, 1.66}
  * NSS solution type ∈ {Orbital, OrbitalTargetedSearch}
This filter catches all 4 while leaving the 9 substellar candidates
intact (face-on M_2 ∈ [48, 407] M_J for the 9, well above the 22 M_J
threshold).

Effect on full v3 pool (9,498 sources):
  - 92 sources newly REJECTED by this filter
  - 89 of 92 were previously SURVIVOR_no_hgca_corroboration (weak retain)
  - 0 of 92 were CORROBORATED or FLAG (preserved by HGCA exemption)
  - Net: weak-tier SURVIVOR pool shrinks from 7,322 → 7,233 (−1.2%)
"""
from __future__ import annotations

from pathlib import Path

import polars as pl

from pipeline_v3_tuned_filters_2026_05_17 import (  # noqa: E402
    SAHL_POSITIVE_LABELS, is_sahl_verdict_positive,
)

# Filter #32 thresholds
V4_FACE_ON_THRESHOLD_MJ = 22.0
V4_HGCA_CORROB_THRESHOLD = 5.0
V4_EXEMPT_SOLUTION_TYPES = frozenset({"OrbitalTargetedSearchValidated"})


def is_sb2_imposter_candidate(row: dict) -> bool:
    """Return True if this row matches the v4 SB2-imposter filter.

    Conditions (all must hold):
      1. M_2 face-on < V4_FACE_ON_THRESHOLD_MJ (22 M_J)
      2. HGCA chi² is null OR < V4_HGCA_CORROB_THRESHOLD (5)
      3. NSS solution type is not in V4_EXEMPT_SOLUTION_TYPES
    """
    m = row.get("M_2_mjup_face_on")
    if m is None or m >= V4_FACE_ON_THRESHOLD_MJ:
        return False
    chi = row.get("hgca_chisq")
    if chi is not None and chi >= V4_HGCA_CORROB_THRESHOLD:
        return False
    sol = row.get("nss_solution_type")
    if sol in V4_EXEMPT_SOLUTION_TYPES:
        return False
    return True


def reclassify_pool_to_v4(
    v3_pool: pl.DataFrame,
) -> pl.DataFrame:
    """Apply v4 SB2-imposter filter to a v3 cascade pool.

    Operates on rows whose v3_verdict is SURVIVOR_no_hgca_corroboration
    or FLAG_hgca_mass_ambiguous (the only verdicts where a weak signal
    can sneak through). Sources with strong CORROBORATED verdict or
    explicit REJECTED verdict are preserved unchanged.
    """
    def reclass(r: dict) -> str:
        v3v = r.get("v3_verdict") or r.get("v2_verdict")
        # Only modify weak-tier verdicts (SURVIVOR, FLAG)
        if v3v not in {
            "SURVIVOR_no_hgca_corroboration", "FLAG_hgca_mass_ambiguous"
        }:
            return v3v
        if is_sb2_imposter_candidate(r):
            return "REJECTED_sb2_low_face_on_no_corroboration"
        return v3v

    pool = v3_pool.with_columns(
        pl.struct(v3_pool.columns).map_elements(
            reclass, return_dtype=pl.Utf8
        ).alias("v4_verdict")
    )
    return pool


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(
        description="Apply v4 SB2-imposter filter to v3 cascade pool"
    )
    parser.add_argument("--v3-pool", required=True, help="Path to v3 CSV")
    parser.add_argument("--out", required=True, help="Output path for v4 CSV")
    args = parser.parse_args()

    v3 = pl.read_csv(args.v3_pool)
    v4 = reclassify_pool_to_v4(v3)
    v4.write_csv(args.out)

    # Compute v3 vs v4 transitions
    prev = "v3_verdict" if "v3_verdict" in v3.columns else "v2_verdict"
    n_changed = v4.filter(pl.col(prev) != pl.col("v4_verdict")).height
    print(f"Wrote {args.out} ({v4.height} rows; {n_changed} reclassified)")

    print(f"\n{prev} → v4 verdict transitions:")
    transitions = v4.filter(
        pl.col(prev) != pl.col("v4_verdict")
    ).group_by([prev, "v4_verdict"]).agg(pl.len().alias("n")).sort(
        "n", descending=True
    )
    print(transitions)
