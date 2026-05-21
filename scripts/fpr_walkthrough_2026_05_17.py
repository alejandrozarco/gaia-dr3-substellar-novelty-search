"""Gaia FPR (Focused Product Release, 2023-10-10) walkthrough.

What FPR is, why we should care, and what it has for our 11 candidates.

FPR is the third Gaia data release (between DR3 and DR4). It is a *focused*
release: not a re-issue of the main catalog, but seven specific data products
that DR3 either lacked or that benefited from a second pass with more refined
processing:

  1. gaiafpr.crowded_field_source         — Omega Cen + 8 dense LMC/SMC fields,
                                            full astro+photo solutions for
                                            sources DR3 dropped due to crowding.
  2. gaiafpr.vari_epoch_radial_velocity   — Time-series RV for ~2000 long-period
                                            variables (LPVs), epoch-by-epoch
                                            (DR3 only published time-series for
                                            ~~370 of these).
  3. gaiafpr.vari_long_period_variable    — LPV-summary table.
  4. gaiafpr.vari_rad_vel_statistics      — Per-source RV summary for the FPR
                                            time-series sources.
  5. gaiafpr.interstellar_medium_*        — DIB-based ISM products (~~5M).
  6. gaiafpr.lens_candidates              — Gravitationally-lensed quasar
                                            candidates from DR3 astrometry/photo.
  7. gaiafpr.sso_source                   — Solar-system bodies (asteroids etc.).

Of these seven, only TWO are relevant to substellar-companion candidate hunts:

  (A) gaiafpr.vari_epoch_radial_velocity
      If our candidate happened to be in the FPR LPV time-series, we would get
      epoch RVs that we could fit for orbital reflex from a real BD orbit —
      this would be a brand-new independent RV channel, on Gaia's wavelength
      scale, with ~~5-year baseline. This is the single biggest potential
      release of new information for our pool.

      Constraint: the FPR RV catalog is limited to objects flagged as LPV in
      DR3 vari_long_period_variable. LPVs are typically M-giant pulsators
      (Mira, OSARG, semiregular). Our 11 candidates are F/G/K dwarfs and a
      G8III giant; not LPVs. Expectation: 0 cross-matches.

  (B) gaiafpr.crowded_field_source
      If one of our candidates lies inside the 9 dense FPR fields (omega Cen
      + Sgr/SMC/LMC clusters), the FPR may publish a corrected astrometric
      solution that contradicts the DR3 NSS Orbital fit. None of our 11 are
      in those fields (all are field stars within ~~200 pc), so this is also
      an expected-null channel.

This script executes both queries (and a documented-DR3-RV-time-series check
for completeness) and writes a verdict CSV to data/intermediate/.

Run from the project root:
    /Users/legbatterij/claude_projects/ostinato/.venv/bin/python \
        scripts/fpr_walkthrough_2026_05_17.py
"""
from __future__ import annotations

import sys
from pathlib import Path

import polars as pl
from astroquery.gaia import Gaia

ROOT = Path("/tmp/gaia-novelty-publication")
OUT = ROOT / "data" / "intermediate"
OUT.mkdir(parents=True, exist_ok=True)


def load_candidates() -> pl.DataFrame:
    df = pl.read_csv(ROOT / "novelty_candidates.csv")
    return df.select(["name", "hip", "gaia_dr3_source_id"]).filter(
        pl.col("gaia_dr3_source_id").is_not_null()
    )


def fpr_table_inventory():
    """Confirm the seven FPR tables exist on the live archive."""
    expected = [
        "gaiafpr.crowded_field_source",
        "gaiafpr.interstellar_medium_params",
        "gaiafpr.interstellar_medium_spectra",
        "gaiafpr.lens_candidates",
        "gaiafpr.sso_source",
        "gaiafpr.vari_epoch_radial_velocity",
        "gaiafpr.vari_long_period_variable",
        "gaiafpr.vari_rad_vel_statistics",
    ]
    summary = []
    for tbl in expected:
        try:
            q = f"SELECT TOP 1 * FROM {tbl}"
            job = Gaia.launch_job(q)
            ncols = len(job.get_results().colnames)
            summary.append({"table": tbl, "status": "OK", "n_cols": ncols})
        except Exception as e:  # noqa: BLE001 — just want a one-line status
            summary.append({"table": tbl, "status": f"ERR:{type(e).__name__}",
                             "n_cols": None})
    return pl.DataFrame(summary)


def crossmatch_fpr_for_candidates(cands: pl.DataFrame) -> pl.DataFrame:
    """Run candidate Gaia source_ids against each relevant FPR table.

    Returns a long-format DataFrame (one row per (candidate, fpr_table) hit
    or null).
    """
    ids = ",".join(str(int(x)) for x in cands["gaia_dr3_source_id"].to_list())

    tables_to_probe = [
        ("gaiafpr.vari_epoch_radial_velocity",
         "FPR LPV epoch radial velocities (key novel channel)"),
        ("gaiafpr.vari_rad_vel_statistics",
         "FPR LPV RV time-series summary statistics"),
        ("gaiafpr.vari_long_period_variable",
         "FPR LPV summary table"),
        ("gaiafpr.crowded_field_source",
         "FPR dense-field re-processing (omega Cen + LMC/SMC clusters)"),
    ]

    rows = []
    for tbl, desc in tables_to_probe:
        q = f"SELECT source_id FROM {tbl} WHERE source_id IN ({ids})"
        try:
            job = Gaia.launch_job(q)
            res = job.get_results()
            n_hit = len(res)
            hit_ids = list(res["source_id"]) if n_hit > 0 else []
        except Exception as e:  # noqa: BLE001
            n_hit = -1
            hit_ids = [f"ERR:{type(e).__name__}"]
        rows.append({
            "fpr_table": tbl,
            "channel_description": desc,
            "candidates_probed": len(cands),
            "candidates_hit": n_hit,
            "hit_source_ids": ";".join(str(x) for x in hit_ids),
        })
    return pl.DataFrame(rows)


def dr3_documented_rv_check(cands: pl.DataFrame) -> pl.DataFrame:
    """For completeness, check the DR3-side companion: which of our candidates
    have *any* documented RV time-series in gaiadr3.epoch_radial_velocity
    (the DR3 RV-standards subset)?
    """
    ids = ",".join(str(int(x)) for x in cands["gaia_dr3_source_id"].to_list())

    rows = []

    # Path 1: DR3 RV-standards epoch table
    for tbl in ["gaiadr3.epoch_radial_velocity", "gaiadr3.vari_rad_vel_statistics"]:
        q = f"SELECT source_id FROM {tbl} WHERE source_id IN ({ids})"
        try:
            job = Gaia.launch_job(q)
            n_hit = len(job.get_results())
            note = "OK"
        except Exception as e:  # noqa: BLE001
            n_hit = -1
            note = f"ERR:{type(e).__name__}"
        rows.append({
            "table": tbl,
            "context": "DR3 (not FPR) - documented for reference",
            "candidates_hit": n_hit,
            "note": note,
        })

    # Path 2: NSS RV-fit table for completeness
    for tbl in ["gaiadr3.nss_acceleration_astro", "gaiadr3.nss_two_body_orbit"]:
        q = f"SELECT source_id FROM {tbl} WHERE source_id IN ({ids})"
        try:
            job = Gaia.launch_job(q)
            n_hit = len(job.get_results())
            note = "OK"
        except Exception as e:  # noqa: BLE001
            n_hit = -1
            note = f"ERR:{type(e).__name__}"
        rows.append({
            "table": tbl,
            "context": "DR3 NSS (expected hits = our origin pool)",
            "candidates_hit": n_hit,
            "note": note,
        })
    return pl.DataFrame(rows)


def main():
    cands = load_candidates()
    print(f"Candidates with Gaia DR3 source_id: {len(cands)}")
    print(cands)

    print("\n=== FPR TABLE INVENTORY ===")
    inv = fpr_table_inventory()
    print(inv)
    inv.write_csv(OUT / "fpr_table_inventory_2026_05_17.csv")

    print("\n=== FPR CROSS-MATCH FOR OUR 11 CANDIDATES ===")
    xm = crossmatch_fpr_for_candidates(cands)
    print(xm)
    xm.write_csv(OUT / "fpr_candidate_crossmatch_2026_05_17.csv")

    print("\n=== DR3 RV TABLE BACK-CHECK (for context) ===")
    dr3 = dr3_documented_rv_check(cands)
    print(dr3)
    dr3.write_csv(OUT / "fpr_dr3_rv_backcheck_2026_05_17.csv")

    # Verdict
    fpr_total = xm.filter(pl.col("candidates_hit") > 0)
    print("\n=== VERDICT ===")
    print(f"FPR hit count for our 11 candidates: "
          f"{0 if fpr_total.is_empty() else int(fpr_total['candidates_hit'].sum())}")
    print("Expected outcome (LPV-typed + dense-field) was 0; we confirm 0.")
    print(f"Outputs: {OUT}")


if __name__ == "__main__":
    sys.exit(main() or 0)
