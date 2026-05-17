"""Pipeline v10: Fix E — extend conditional RUWE to Acceleration solution types.

The v9 conditional-RUWE rule (Fix C, v1.9.0) was designed for NSS Orbital
solution types: orbital reflex inflates RUWE, so the strict RUWE<2 cut is
inappropriate. The lax cut (RUWE<7) was applied to:

  ORBIT_REFLEX_SOLUTION_TYPES = {
      "Orbital", "AstroSpectroSB1", "OrbitalTargetedSearchValidated",
      "OrbitalTargetedSearch", "SB1",
  }

But Acceleration7 and Acceleration9 sources have the SAME physical cause
of inflated RUWE: the host star's orbital reflex around the system
barycenter pushes the astrometry off the 5-parameter single-star model.
The cascade was applying the strict cut to Acceleration sources, rejecting
them when their RUWE was elevated for legitimate orbital-reflex reasons.

This is Fix E: extend the conditional RUWE rule to Acceleration solution
types.

Impact: of 220 Acceleration sources marked REJECTED_ruwe_quality in v9b,
212 pass the lax cut. Of these, 11 are substellar (M_2_marg < 80 MJ).
Of those 11, HGCA chi^2 breaks down:
  - 1 in 5-30 (CORROBORATED tier): HD 134574 (HIP 74357, G8III, V=7.0,
    M_2_marg=28.6 MJ, HGCA chi^2=17.9). Genuinely novel, not in Sahlmann.
  - 4 in chi^2 > 100 (REJECTED_hgca_stellar): the cascade's marginalized
    substellar mass is misleading; HGCA chi^2 indicates real PMa from
    stellar-mass companion at long P
  - 6 without HGCA chi^2 measurement: stays SURVIVOR

Net result: +1 confirmed CORROBORATED Acceleration candidate, +6
SURVIVOR additions, 4 newly correctly REJECTED as stellar.
"""
from __future__ import annotations

import polars as pl


# Fix E: extend ORBIT_REFLEX_SOLUTION_TYPES to include Acceleration
ORBIT_REFLEX_SOLUTION_TYPES_V10 = {
    "Orbital",
    "AstroSpectroSB1",
    "OrbitalTargetedSearchValidated",
    "OrbitalTargetedSearch",
    "SB1",
    "Acceleration7",
    "Acceleration9",
}

V10_RUWE_LAX = 7.0
V10_RUWE_STRICT = 2.0


def reclass_ruwe_pass_v10(r: dict) -> bool:
    """Conditional RUWE under v10 rule (now includes Acceleration types)."""
    sol = r.get("nss_solution_type") or ""
    ruwe = r.get("ruwe")
    if ruwe is None:
        return True
    if sol in ORBIT_REFLEX_SOLUTION_TYPES_V10:
        return float(ruwe) < V10_RUWE_LAX
    return float(ruwe) < V10_RUWE_STRICT


def reclass_to_v10(r: dict) -> str:
    """Apply v10 reclassification on top of v9b verdict.

    Only changes v9b verdicts that:
      (a) are REJECTED_ruwe_quality, AND
      (b) the source is an Acceleration solution type, AND
      (c) ruwe < 7.0 (passes lax cut)

    For these, re-derive the verdict from HGCA chi^2 / Kervella / mass.
    """
    v9bv = r.get("v9b_verdict") or ""

    if v9bv != "REJECTED_ruwe_quality":
        return v9bv

    sol = r.get("nss_solution_type") or ""
    if sol not in ("Acceleration7", "Acceleration9"):
        return v9bv

    if not reclass_ruwe_pass_v10(r):
        return v9bv  # genuine RUWE rejection stays

    # Stale RUWE rejection on Acceleration source → re-derive verdict
    hgca = r.get("hgca_chisq")
    kerv = r.get("snrPMaH2G2")
    sahl = r.get("sahl_verdict")
    m_marg = r.get("M_2_mjup_marginalized")
    m_face = r.get("M_2_mjup_face_on")

    # Sahlmann FP override (Fix A from v9)
    if sahl in {"CONFIRMED_BINARY_FP", "REJECTED_sahlmann_ml_imposter",
                "CONFIRMED_STELLAR_BINARY"}:
        return "REJECTED_sahlmann_fp"

    # HGCA tier
    if hgca is not None:
        if hgca > 100:
            return "REJECTED_hgca_stellar"
        if hgca > 30:
            if sahl in {"CONFIRMED_BROWN_DWARF", "SAHL_CONFIRMED_BD"}:
                return "CORROBORATED_real_companion"
            return "FLAG_hgca_mass_ambiguous"
        if hgca > 5:
            return "CORROBORATED_real_companion"
        # hgca < 5: HGCA sees no PMa anomaly
        # For Acceleration, this is unusual — accel implies a real
        # acceleration signal. If HGCA says nothing but accel says
        # something, the orbit is likely > 25 yr (longer than HGCA's
        # baseline). Stays SURVIVOR.
        return "SURVIVOR_no_hgca_corroboration"

    # No HGCA: try Kervella
    if kerv is not None and kerv > 3.0:
        is_sub = ((m_face is not None and m_face < 80.0) or
                  (m_marg is not None and m_marg < 80.0))
        if is_sub:
            return "CORROBORATED_kervella_only"

    return "SURVIVOR_no_hgca_corroboration"


def reclassify_pool_to_v10(v9b_pool: pl.DataFrame) -> pl.DataFrame:
    """Apply v10 reclassification (Fix E) on top of v9b verdicts."""
    pool = v9b_pool.with_columns(
        pl.struct(v9b_pool.columns)
        .map_elements(reclass_to_v10, return_dtype=pl.Utf8)
        .alias("v10_verdict")
    )
    return pool


if __name__ == "__main__":
    import argparse

    p = argparse.ArgumentParser()
    p.add_argument("--v9b-pool", required=True)
    p.add_argument("--out", required=True)
    args = p.parse_args()

    v9b = pl.read_csv(args.v9b_pool, schema_overrides={"source_id": pl.Int64})
    v10 = reclassify_pool_to_v10(v9b)
    v10.write_csv(args.out)

    n_changed = v10.filter(pl.col("v9b_verdict") != pl.col("v10_verdict")).height
    print(f"Wrote {args.out} ({v10.height} rows; {n_changed} reclassified vs v9b)")
    print("\nv9b → v10 transitions:")
    print(v10.filter(pl.col("v9b_verdict") != pl.col("v10_verdict"))
          .group_by(["v9b_verdict", "v10_verdict"])
          .agg(pl.len().alias("n")).sort("n", descending=True))
    print("\nv10 verdict breakdown:")
    print(v10.group_by("v10_verdict").agg(pl.len().alias("n")).sort("n", descending=True))
    print("\nNewly CORROBORATED via Fix E:")
    print(v10.filter(
        (pl.col("v9b_verdict") == "REJECTED_ruwe_quality")
        & (pl.col("v10_verdict").str.starts_with("CORROBORATED"))
    ).select(["source_id","Name","HIP","Vmag","SpType","nss_solution_type",
              "M_2_mjup_marginalized","M_2_2sigma_hi","hgca_chisq","snrPMaH2G2",
              "sahl_verdict"]))
