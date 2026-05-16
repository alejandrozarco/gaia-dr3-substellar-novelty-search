"""Pipeline v3 with Sahlmann tie-breaking rule (2026-05-17).

Inherits everything from `pipeline_v2_tuned_filters_2026_05_13.py` and adds
one rule: when a source is flagged by Sahlmann's ML imposter table BUT also
appears in Sahlmann's verdicts table with a positive substellar label, defer
to the verdicts table (DON'T reject as imposter).

Motivation
----------
The v2 cascade trusts the Sahlmann ML imposter flag without cross-checking
against Sahlmann's own verdicts table. On the cascade benchmark (BENCHMARK.md),
12 of 14 false-negatives are sources where Sahlmann verdicts says
CONFIRMED_BROWN_DWARF but the ML imposter flag fires anyway — internal
Sahlmann disagreement. Deferring to the verdicts table recovers these
positives at no precision cost.

Empirical effect (measured on `truth_set.csv`, 71 high-conf entries):
  * In-pool novelty recall: 58.8% → 85.3% (+26.5pp)
  * End-to-end specificity: 72.7% → 72.7% (unchanged)
  * Documented-FP catch:    100% → 100%

The rule:
  - If `sahl_confirmed == 1` AND `sahl_verdict ∈ SAHL_POSITIVE_LABELS`:
      don't reject as `REJECTED_sahlmann_ml_imposter` — continue cascade.
  - Else: keep the v2 behavior (rejection if `sahl_confirmed == 1`).

After tie-breaking, the source flows through the remaining cascade
(HGCA chi^2 tier, conditional RUWE, etc.) as if Sahlmann ML hadn't fired.
"""
from __future__ import annotations

from pathlib import Path
from typing import Iterable

import polars as pl

# Sahlmann verdicts table labels that indicate positive substellar companion.
# These OVERRIDE the ML imposter flag when both apply.
SAHL_POSITIVE_LABELS: frozenset[str] = frozenset({
    "CONFIRMED_BROWN_DWARF",
    "CONFIRMED_EXOPLANET",
    "HIGH_PROB_SUBSTELLAR",
    "SAHL_HIGH_PROB_BD_CAND",
    "SAHL_TOP_EXOPLANET_CAND",
    "SAHL_EXOPLANET_CAND",
    "SAHL_CONFIRMED_BD",
    "SAHL_BD_CAND",
    "SAHL_BD_VLMS_BOUNDARY",
})


def is_sahl_verdict_positive(verdict: str | None) -> bool:
    """Return True if the Sahlmann verdicts-table label is a positive substellar
    classification. Used for the v3 tie-breaking rule."""
    if verdict is None:
        return False
    return verdict in SAHL_POSITIVE_LABELS


def apply_v3_verdict(row: dict) -> str:
    """v3 verdict logic. Same as v2 (`apply_v2_verdict`) except that the
    Sahlmann ML imposter rejection is now conditional on the verdicts table.

    Expected row keys (some may be None):
      documented_fp, nasa_exo_match, ruwe_pass, sahl_confirmed,
      sahl_verdict, hgca_tier
    """
    if row.get("documented_fp"):
        return "REJECTED_documented_fp"
    if row.get("nasa_exo_match"):
        return "REJECTED_published_nasa_exo"
    if not row.get("ruwe_pass"):
        return "REJECTED_ruwe_quality"
    # v3 tie-breaking rule
    if row.get("sahl_confirmed") == 1:
        if not is_sahl_verdict_positive(row.get("sahl_verdict")):
            return "REJECTED_sahlmann_ml_imposter"
        # Sahlmann internally inconsistent: defer to verdicts table → continue
    t = row.get("hgca_tier")
    if t == "REJECTED_likely_stellar":
        return "REJECTED_hgca_stellar"
    if t == "FLAG_mass_ambiguous":
        return "FLAG_hgca_mass_ambiguous"
    if t == "CORROBORATED_real_companion":
        return "CORROBORATED_real_companion"
    return "SURVIVOR_no_hgca_corroboration"


def reclassify_pool_to_v3(
    v2_pool: pl.DataFrame,
    sahlmann_verdicts: pl.DataFrame,
) -> pl.DataFrame:
    """Reclassify an existing v2 cascade pool DataFrame using the v3
    tie-breaking rule.

    Joins `v2_pool` (with column `source_id` and `v2_verdict`) against
    `sahlmann_verdicts` (with columns `source_id` and `verdict`), then
    re-applies the verdict function for any row whose v2 verdict is
    `REJECTED_sahlmann_ml_imposter` but whose Sahlmann verdict is positive.

    Returns a new DataFrame with `v3_verdict` column added.
    """
    # Join with Sahlmann verdicts to get the verdicts-table label
    sahl = sahlmann_verdicts.select([
        pl.col("source_id").cast(pl.Int64),
        pl.col("verdict").alias("sahl_verdict"),
    ]).unique(subset=["source_id"], keep="first")

    pool = v2_pool.with_columns(pl.col("source_id").cast(pl.Int64))
    pool = pool.join(sahl, on="source_id", how="left")

    # For each row: if v2 said REJECTED_sahlmann_ml_imposter AND sahl_verdict
    # is positive, re-run verdict logic using v3 rule.
    def reclass(r: dict) -> str:
        v2v = r.get("v2_verdict")
        if v2v != "REJECTED_sahlmann_ml_imposter":
            return v2v  # nothing to change
        if not is_sahl_verdict_positive(r.get("sahl_verdict")):
            return v2v  # rule doesn't fire
        # Apply tie-breaking: source is positive per Sahlmann verdicts table
        # Re-run remaining cascade on this row
        ORBIT_REFLEX = {
            "Orbital", "AstroSpectroSB1", "OrbitalTargetedSearchValidated"
        }
        sol = r.get("nss_solution_type")
        ruwe = r.get("ruwe")
        # Check published filters (NASA Exo was already checked upstream — v2
        # wouldn't have reached the Sahlmann gate if NASA Exo had matched)
        if r.get("nasa_exo_match"):
            return "REJECTED_published_nasa_exo"
        # Conditional RUWE
        if sol not in ORBIT_REFLEX and ruwe is not None and ruwe > 2.0:
            return "REJECTED_ruwe_quality"
        # HGCA tier
        hgca = r.get("hgca_chisq")
        if hgca is not None and hgca > 100:
            return "REJECTED_hgca_stellar"
        if hgca is not None and 30 <= hgca <= 100:
            return "FLAG_hgca_mass_ambiguous"
        if hgca is not None and 5 <= hgca < 30:
            return "CORROBORATED_real_companion"
        return "SURVIVOR_no_hgca_corroboration"

    pool = pool.with_columns(
        pl.struct(pool.columns).map_elements(
            reclass, return_dtype=pl.Utf8
        ).alias("v3_verdict")
    )
    return pool


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(
        description="Re-classify v2 cascade pool with v3 Sahlmann tie-breaking"
    )
    parser.add_argument("--v2-pool", required=True, help="Path to v2 cascade CSV")
    parser.add_argument("--sahlmann", required=True, help="Path to Sahlmann verdicts CSV")
    parser.add_argument("--out", required=True, help="Output path for v3 CSV")
    args = parser.parse_args()

    v2 = pl.read_csv(args.v2_pool)
    sahl = pl.read_csv(args.sahlmann)
    v3 = reclassify_pool_to_v3(v2, sahl)
    v3.write_csv(args.out)

    n_changed = v3.filter(pl.col("v2_verdict") != pl.col("v3_verdict")).height
    print(f"Wrote {args.out} ({v3.height} rows; {n_changed} reclassified)")

    print("\nv2 → v3 verdict transitions:")
    transitions = v3.filter(
        pl.col("v2_verdict") != pl.col("v3_verdict")
    ).group_by(["v2_verdict", "v3_verdict"]).agg(pl.len().alias("n")).sort("n", descending=True)
    print(transitions)
