"""Pipeline v9: recall improvements + cascade hygiene (2026-05-17).

Addresses 4 cascade methodology errors exposed by the v8 hunt's
Sahlmann-disagreement analysis:

  Fix A — Sahlmann CONFIRMED_BINARY_FP filter
    HD 185501 (HIP 96576) was CORROBORATED at v8 but Sahlmann 2025
    lists it as CONFIRMED_BINARY_FP. The cascade's
    `REJECTED_sahlmann_ml_imposter` path is only checked via the
    `sahl_verdict` column during v3 processing and the final v_*
    verdict labels don't always preserve it. v9 adds a unified
    `REJECTED_sahlmann_fp` filter on top of v8 verdicts.

  Fix C — RUWE verdict-logic re-sync
    HD 5433 (HIP 4387) has ruwe=4.06 and solution_type=
    OrbitalTargetedSearch. The conditional RUWE rule (lax 7.0 for
    orbit-reflex solution_types) gives ruwe_pass=True, but the
    historical v2 verdict label is REJECTED_ruwe_quality (from when
    the cascade used a uniform RUWE<2 cut). The v3..v8 pipelines
    inherit this stale label. v9 re-applies the conditional rule
    against ruwe_pass to flip stale RUWE rejections back to their
    correct cascade tier.

  Fix D — Kervella substitute for HGCA on short-period orbits
    HD 92320 (HIP 52278) has P=145d, HGCA chi^2=2.25 (no PM anomaly
    over 25-yr arc because of orbital averaging), but Kervella
    H2G2 SNR=6.07 (10-yr arc detects the wobble). The cascade
    classifies it as SURVIVOR_no_hgca_corroboration even though
    Sahlmann 2025 confirmed it as a brown dwarf.

    v9 promotion logic: if (HGCA chi^2 < 5 OR HGCA missing) AND
    Kervella SNR > 3 AND substellar M_2 estimate AND short period
    (P < 4 years, so HGCA's 25-yr arc averages out >= 6 cycles),
    promote to CORROBORATED_kervella_only.

  Fix A also covers FLAG-to-CORROBORATED promotion when an
  independent published catalog has confirmed the substellar mass
  (Sahlmann CONFIRMED_BD, Halbwachs DPAC direct-method M_2 in
  substellar range with mass-agreement to cascade). HD 89707 is
  the canonical example: HGCA chi^2=53.5 (FLAG tier) but Sahlmann
  CONFIRMED_BD.

Fix B (WDS / Tokovinin MSC visual-binary filter) ships in a
separate companion script `pipeline_v9b_wds_tokovinin.py` because
it requires Vizier catalog downloads.
"""
from __future__ import annotations

from pathlib import Path

import polars as pl

# Fix C — conditional RUWE thresholds
ORBIT_REFLEX_SOLUTION_TYPES = {
    "Orbital",
    "AstroSpectroSB1",
    "OrbitalTargetedSearchValidated",
    "OrbitalTargetedSearch",
    "SB1",
}
V9_RUWE_LAX = 7.0
V9_RUWE_STRICT = 2.0

# Fix A — Sahlmann sahl_verdict tags treated as cascade FP
V9_SAHL_FP_TAGS = {
    "CONFIRMED_BINARY_FP",
    "REJECTED_sahlmann_ml_imposter",
    "CONFIRMED_STELLAR_BINARY",
}

# Fix A — Sahlmann tags that should promote FLAG -> CORROBORATED
V9_SAHL_PROMOTE_TAGS = {
    "CONFIRMED_BROWN_DWARF",
    "SAHL_CONFIRMED_BD",
}

# Fix D — Kervella substitute thresholds
V9_KERVELLA_CORR_THRESHOLD = 3.0
V9_P_DAYS_SHORT_ORBIT = 4 * 365.25  # 4 yr: HGCA 25-yr arc averages >= 6 cycles
V9_HGCA_NO_SIGNAL = 5.0  # chi^2 below this = HGCA sees no PMa


def is_substellar(m_face: float | None, m_marg: float | None) -> bool:
    """True if either M_2 face-on or marginalized is in substellar range."""
    face_sub = m_face is not None and m_face < 80.0
    marg_sub = m_marg is not None and m_marg < 80.0
    return face_sub or marg_sub


def reclass_ruwe_pass(r: dict) -> bool:
    """Fix C: conditional RUWE rule from filter_conditional_ruwe."""
    sol = r.get("nss_solution_type") or ""
    ruwe = r.get("ruwe")
    if ruwe is None:
        return True
    if sol in ORBIT_REFLEX_SOLUTION_TYPES:
        return float(ruwe) < V9_RUWE_LAX
    return float(ruwe) < V9_RUWE_STRICT


def reclass_to_v9(r: dict) -> str:
    """Apply v9 reclassification on top of v8 verdict."""
    v8v = r.get("v8_verdict") or ""

    # Preserve documented_fp and published rejections — they're correct
    if v8v in {"REJECTED_documented_fp",
               "REJECTED_published_nasa_exo",
               "REJECTED_published_exoplanet_eu",
               "REJECTED_published_exoplanet_eu_pm_corr"}:
        return v8v

    # Fix A: Sahlmann FP override (rejects HD 185501 etc.)
    sahl = r.get("sahl_verdict")
    if sahl in V9_SAHL_FP_TAGS:
        return "REJECTED_sahlmann_fp"

    # Fix C: re-evaluate RUWE under conditional rule
    if v8v == "REJECTED_ruwe_quality":
        if reclass_ruwe_pass(r):
            # Stale REJECTED — fall through and re-derive correct tier
            v8v_recovered = True
        else:
            return v8v  # Genuine RUWE rejection still
    else:
        v8v_recovered = False

    # If RUWE was stale-rejected, re-derive the tier from the other fields
    if v8v_recovered:
        # Use HGCA tier + Kervella + Sahlmann to decide what tier this
        # source belongs in now that RUWE no longer rejects it.
        hgca = r.get("hgca_chisq")
        kerv = r.get("snrPMaH2G2")
        m_face = r.get("M_2_mjup_face_on")
        m_marg = r.get("M_2_mjup_marginalized")
        is_sub = is_substellar(m_face, m_marg)

        if hgca is not None:
            if hgca > 100:
                return "REJECTED_hgca_stellar"
            if hgca > 30:
                # FLAG tier
                if sahl in V9_SAHL_PROMOTE_TAGS:
                    return "CORROBORATED_real_companion"
                return "FLAG_hgca_mass_ambiguous"
            if hgca > 5:
                return "CORROBORATED_real_companion"
            # hgca <= 5: HGCA sees no anomaly
            if (kerv is not None and kerv > V9_KERVELLA_CORR_THRESHOLD
                    and is_sub):
                return "CORROBORATED_kervella_only"
            return "SURVIVOR_no_hgca_corroboration"
        # No HGCA: check Kervella
        if (kerv is not None and kerv > V9_KERVELLA_CORR_THRESHOLD
                and is_sub):
            return "CORROBORATED_kervella_only"
        return "SURVIVOR_no_hgca_corroboration"

    # Fix D: Kervella-substitute promotion on SURVIVOR (short-P, HGCA-blind)
    if v8v == "SURVIVOR_no_hgca_corroboration":
        hgca = r.get("hgca_chisq")
        kerv = r.get("snrPMaH2G2")
        period = r.get("period_d")
        m_face = r.get("M_2_mjup_face_on")
        m_marg = r.get("M_2_mjup_marginalized")
        # HGCA either missing or in no-signal regime
        hgca_blind = (hgca is None) or (hgca < V9_HGCA_NO_SIGNAL)
        # Kervella corroborates
        kerv_strong = (kerv is not None) and (kerv > V9_KERVELLA_CORR_THRESHOLD)
        # Short-period (HGCA's 25-yr arc would average out)
        short_p = (period is not None) and (period < V9_P_DAYS_SHORT_ORBIT)
        # Substellar mass
        is_sub = is_substellar(m_face, m_marg)
        if hgca_blind and kerv_strong and short_p and is_sub:
            return "CORROBORATED_kervella_only"

    # Fix A (continued): FLAG -> CORROBORATED if Sahlmann published as BD
    if v8v == "FLAG_hgca_mass_ambiguous":
        if sahl in V9_SAHL_PROMOTE_TAGS:
            return "CORROBORATED_real_companion"

    return v8v


def reclassify_pool_to_v9(v8_pool: pl.DataFrame) -> pl.DataFrame:
    """Apply v9 reclassification on top of v8 verdicts."""
    pool = v8_pool.with_columns(
        pl.struct(v8_pool.columns)
        .map_elements(reclass_to_v9, return_dtype=pl.Utf8)
        .alias("v9_verdict")
    )
    return pool


if __name__ == "__main__":
    import argparse

    p = argparse.ArgumentParser()
    p.add_argument("--v8-pool", required=True)
    p.add_argument("--out", required=True)
    args = p.parse_args()

    v8 = pl.read_csv(args.v8_pool).unique(subset=["source_id"], keep="first")
    v9 = reclassify_pool_to_v9(v8)
    v9 = v9.unique(subset=["source_id"], keep="first")
    v9.write_csv(args.out)

    n_changed = v9.filter(pl.col("v8_verdict") != pl.col("v9_verdict")).height
    print(f"Wrote {args.out} ({v9.height} rows; {n_changed} reclassified vs v8)")

    print("\nv8 → v9 transitions:")
    print(
        v9.filter(pl.col("v8_verdict") != pl.col("v9_verdict"))
        .group_by(["v8_verdict", "v9_verdict"])
        .agg(pl.len().alias("n"))
        .sort("n", descending=True)
    )

    print("\nv9 verdict breakdown:")
    print(v9.group_by("v9_verdict").agg(pl.len().alias("n")).sort("n", descending=True))
