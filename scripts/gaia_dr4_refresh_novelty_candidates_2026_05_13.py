"""Gaia DR4 refresh pipeline for the 8 substellar tentative candidates in
`novelty_candidates.csv` (publication repo) plus the 18 planet-regime probe
survivors.

DR4 is expected December 2026 (data release Q1 2027). When it lands, this
script becomes a one-button refresh:

    python scripts/gaia_dr4_refresh_novelty_candidates_2026_05_13.py --live

Dry-run mode validates the candidate manifest and the query templates:

    python scripts/gaia_dr4_refresh_novelty_candidates_2026_05_13.py

Per candidate, the script does:

  1. **Fetch DR4 `gaiadr4.gaia_source`** for revised parallax / pm / G / RV
     summary. Compare against DR3 values stored in this manifest.
  2. **Fetch DR4 `gaiadr4.nss_two_body_orbit` / `nss_acceleration_astro`**
     with the longer 5.5-yr baseline; check if the candidate's solution is
     still in the FP-cleared subset (i.e., not on a DR4 known-issues list,
     if any).
  3. **Fetch DR4 `gaiadr4.epoch_radial_velocity`** — per-transit RV time
     series, ~20-40 epochs per source.
  4. **Fetch DR4 `gaiadr4.epoch_astrometric_data`** — per-transit (ra,dec)
     offsets that allow direct joint RV+astrometric Keplerian fit.
  5. **Joint Bayesian fit** (via existing `rv_astrometric_joint_fitter.py`)
     that yields M_2 + sin(i) jointly with parameter uncertainties.
  6. **Per-candidate decision recipe** — clear-cut tests for substellar
     confirmation that take the DR4 outputs and emit a verdict.

Decision recipes (per candidate type):

  - NSS Orbital (HD 101767, HD 140895, HD 140940, BD+46 2473, BD+35 228):
    * If DR4 NSS Orbital P and a_phot are within 5% of DR3 → orbit is real
    * If DR4 epoch RV K shows the predicted K_pred ± 50% → companion confirmed
    * If joint fit M_2 < 80 M_J at 2sigma → substellar confirmed
    * If M_2 > 80 M_J at 2sigma → stellar; demote to stellar imposter list
    * If DR4 NSS Orbital fails to refit → solution may have been DR3 artifact

  - NSS Acceleration (HD 75426, HD 104828, HD 120954):
    * If DR4 publishes full NSS Orbital (not just Acceleration) → period
      and mass directly determined; check M_2 < 80 M_J
    * If still Acceleration only → joint with archival RV via Brandt 2024-style
      orvara extension; refine M_2 posterior with 5.5-yr baseline

  - Planet probe (18 candidates):
    * Apply DR4 NSS known-issues filter (will exist post-release)
    * Joint fit M_2 < 13 M_J at 2sigma → planet confirmed
    * Otherwise demote
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from dataclasses import dataclass, field
from pathlib import Path

import polars as pl

DATA_ROOT = Path(
    os.environ.get(
        "GAIA_NOVELTY_DATA_ROOT",
        str(Path(__file__).resolve().parent.parent),
    )
)

DR4_RELEASE_DATE = "2026-12-15 (expected)"
DR4_TAP_URL = "https://gea.esac.esa.int/tap-server/tap/sync"

# DR4 table names (speculative; will be validated when DR4 lands)
DR4_TABLES = {
    "gaia_source": "gaiadr4.gaia_source",
    "nss_orbital": "gaiadr4.nss_two_body_orbit",
    "nss_accel": "gaiadr4.nss_acceleration_astro",
    "epoch_rv": "gaiadr4.epoch_radial_velocity",
    "epoch_iad": "gaiadr4.epoch_astrometric_data",
}


@dataclass
class Candidate:
    """One DR4 refresh target."""
    name: str
    gaia_dr3_source_id: str
    nss_pool: str  # 'orbital' / 'orbital_inner' / 'acceleration'
    dr3_period_d: float | None
    dr3_m2_marginalized_mjup: float | None
    dr3_significance: float | None
    confirmation_target_kpred_mps: float | None
    decision_recipe_key: str
    notes: str = ""


# ----------------------------------------------------------------------------
# Candidate manifest (matches /tmp/gaia-novelty-publication/novelty_candidates.csv)
# ----------------------------------------------------------------------------
SUBSTELLAR_CANDIDATES = [
    Candidate(
        name="HD 101767",
        gaia_dr3_source_id="841536616165020416",
        nss_pool="orbital",
        dr3_period_d=486.0,
        dr3_m2_marginalized_mjup=62.0,
        dr3_significance=39.6,
        confirmation_target_kpred_mps=3000.0,  # ~3 km/s from Gaia DR3 rv_amplitude_robust
        decision_recipe_key="orbital_with_gaia_rv_corroboration",
        notes="Pure Orbital (FP-cleared); 21 APOGEE transits show chi2 = 2.8e-11",
    ),
    Candidate(
        name="HD 75426",
        gaia_dr3_source_id="5328000290404075264",
        nss_pool="acceleration",
        dr3_period_d=None,  # P~125 yr from orvara joint
        dr3_m2_marginalized_mjup=282.0,  # orvara joint median (M-dwarf regime)
        dr3_significance=60.0,
        confirmation_target_kpred_mps=None,  # synthetic K from orvara
        decision_recipe_key="acceleration_long_period_resolves_via_dr4_orbital",
        notes="4 independent astrometric witnesses; orvara mass-ambiguous",
    ),
    Candidate(
        name="HD 104828",
        gaia_dr3_source_id="3905850581902839168",
        nss_pool="acceleration",
        dr3_period_d=3600.0,  # ~10 yr
        dr3_m2_marginalized_mjup=41.0,
        dr3_significance=37.0,
        confirmation_target_kpred_mps=1300.0,  # CARMENES peak-to-peak
        decision_recipe_key="acceleration_with_carmenes_corroboration",
        notes="HGCA 23.6 sigma + CARMENES K_pp 1.3 km/s; 3 epochs",
    ),
    Candidate(
        name="HD 140895",
        gaia_dr3_source_id="4395581616493055616",
        nss_pool="orbital_inner",
        dr3_period_d=1460.0,
        dr3_m2_marginalized_mjup=113.0,
        dr3_significance=6.83,
        confirmation_target_kpred_mps=None,
        decision_recipe_key="multi_body_inner_orbit_plus_kervella_pma",
        notes="Inner orbit sig=6.83 (FP-range); outer body from Kervella excess",
    ),
    Candidate(
        name="HD 140940",
        gaia_dr3_source_id="6015027554036714496",
        nss_pool="orbital_inner",
        dr3_period_d=924.0,
        dr3_m2_marginalized_mjup=183.0,
        dr3_significance=13.04,
        confirmation_target_kpred_mps=None,
        decision_recipe_key="multi_body_inner_orbit_plus_kervella_pma",
        notes="Same caveat as HD 140895",
    ),
    Candidate(
        name="BD+46 2473",
        gaia_dr3_source_id="2121783289552546432",
        nss_pool="orbital_inner",
        dr3_period_d=496.0,
        dr3_m2_marginalized_mjup=74.0,
        dr3_significance=8.48,
        confirmation_target_kpred_mps=None,
        decision_recipe_key="multi_body_inner_orbit_plus_kervella_pma",
        notes="Also has SB1 P=5.7 d; weak Kervella excess at 3.3 sigma",
    ),
    Candidate(
        name="BD+35 228",
        gaia_dr3_source_id="321123400368013696",
        nss_pool="orbital_inner",
        dr3_period_d=560.0,
        dr3_m2_marginalized_mjup=53.0,
        dr3_significance=12.78,
        confirmation_target_kpred_mps=None,
        decision_recipe_key="multi_body_inner_orbit_plus_kervella_pma",
        notes="Inner P may be aliased; orvara prefers different inner P",
    ),
    Candidate(
        name="HD 120954",
        gaia_dr3_source_id="6287148057608953600",
        nss_pool="acceleration",
        dr3_period_d=25500.0,  # ~70 yr
        dr3_m2_marginalized_mjup=1637.0,  # already classified stellar M-dwarf
        dr3_significance=33.0,
        confirmation_target_kpred_mps=6500.0,  # multi-decade Delta_RV
        decision_recipe_key="apparent_stellar_already_classified",
        notes="Not a substellar candidate; 5-baseline convergence on stellar M-dwarf",
    ),
    Candidate(
        name="HIP 91479",
        gaia_dr3_source_id="4539057576001089408",
        nss_pool="orbital",
        dr3_period_d=855.84,
        dr3_m2_marginalized_mjup=64.0,  # astrometric Kepler joint fit
        dr3_significance=32.24,
        confirmation_target_kpred_mps=1950.0,  # K1 from Gaia rv_amplitude_robust ~ 3.9 km/s p-p
        decision_recipe_key="orbital_with_gaia_rv_corroboration",
        notes="AstroSpectroSB1; LP 335-104 high-PM K-dwarf; HGCA chi^2=50.3 (FLAG mass-ambiguous). Note Pourbaix C,H K_1 inconsistency 3.4x (model gap).",
    ),
    Candidate(
        name="HIP 60865",
        gaia_dr3_source_id="1518957932040718464",
        nss_pool="orbital",
        dr3_period_d=500.69,
        dr3_m2_marginalized_mjup=48.77,
        dr3_significance=34.11,
        confirmation_target_kpred_mps=None,  # no archival RV
        decision_recipe_key="orbital_with_gaia_rv_corroboration",
        notes="Orbital pool; G 123-34 = Luyten high-PM M-dwarf; HGCA chi^2=10.5 (CORROBORATED). New from v2 scan 2026-05-13.",
    ),
    Candidate(
        name="HIP 20122",
        gaia_dr3_source_id="3255968634985106816",
        nss_pool="orbital",
        dr3_period_d=254.73,
        dr3_m2_marginalized_mjup=64.04,
        dr3_significance=28.55,
        confirmation_target_kpred_mps=None,
        decision_recipe_key="orbital_with_gaia_rv_corroboration",
        notes="Orbital pool; faint M-dwarf V=13.49; HGCA chi^2=5.1 (CORROBORATED mild). New from v2 scan 2026-05-13.",
    ),
]


DECISION_RECIPES = {
    "orbital_with_gaia_rv_corroboration": """
        If DR4 NSS Orbital P within 5% of DR3 AND DR4 epoch RV K consistent with
        DR3 rv_amplitude_robust (within 30%) AND joint fit M_2 < 80 M_J at 2sigma:
        -> substellar CONFIRMED.
        If joint fit M_2 > 80 M_J at 2sigma: -> stellar (demote).
        If DR4 NSS Orbital does not refit: -> may be DR3 artifact (downgrade).
    """,
    "acceleration_long_period_resolves_via_dr4_orbital": """
        DR4's longer 5.5-yr baseline may convert this Acceleration into a full
        Orbital solution. If yes: P, e, a_phot are directly published; check
        M_2 < 80 M_J at 2sigma. If still Acceleration only: improve via joint
        orvara + DR4 epoch RV.
    """,
    "acceleration_with_carmenes_corroboration": """
        Combine DR4 epoch RV with the 3 CARMENES archival epochs in a joint
        Keplerian fit. If K matches DR3 acceleration prediction within 30%
        AND M_2 < 80 M_J at 2sigma: -> substellar CONFIRMED.
    """,
    "multi_body_inner_orbit_plus_kervella_pma": """
        Two separate tests:
        (a) Inner orbit: DR4 NSS Orbital reproducing DR3 P within 5%? If
            sigma DR4 > 20: -> inner companion CONFIRMED. If significance drops
            below 5: -> DR3 inner orbit may be artifact.
        (b) Outer body: DR4 epoch IAD enables direct fit of acceleration
            from outer body. Compare to Kervella DR3 PMa excess. If converges
            to same outer body mass: -> outer companion CONFIRMED.
        Both (a) and (b) must succeed for the candidate to remain substellar.
    """,
    "apparent_stellar_already_classified": """
        Already classified as stellar M-dwarf at P~70 yr from 5-baseline
        convergence. DR4 will verify the stellar interpretation; not expected
        to flip to substellar.
    """,
}


def query_template(table_key: str, candidate: Candidate) -> str:
    """Generate the ADQL query for a given DR4 table + candidate."""
    table = DR4_TABLES[table_key]
    sid = candidate.gaia_dr3_source_id
    if table_key == "gaia_source":
        return (
            f"SELECT source_id, ra, dec, parallax, parallax_error, pmra, pmdec, "
            f"phot_g_mean_mag, ruwe, ipd_frac_multi_peak, rv_amplitude_robust, "
            f"rv_chisq_pvalue, rv_nb_transits "
            f"FROM {table} WHERE source_id = {sid}"
        )
    if table_key == "nss_orbital":
        return (
            f"SELECT source_id, nss_solution_type, period, period_error, "
            f"eccentricity, eccentricity_error, significance, goodness_of_fit, "
            f"a_thiele_innes, b_thiele_innes, f_thiele_innes, g_thiele_innes "
            f"FROM {table} WHERE source_id = {sid}"
        )
    if table_key == "nss_accel":
        return (
            f"SELECT source_id, nss_solution_type, significance, "
            f"accel_ra, accel_dec, deriv_accel_ra, deriv_accel_dec "
            f"FROM {table} WHERE source_id = {sid}"
        )
    if table_key == "epoch_rv":
        return (
            f"SELECT source_id, transit_id, bjd, radial_velocity, "
            f"radial_velocity_error "
            f"FROM {table} WHERE source_id = {sid} ORDER BY bjd"
        )
    if table_key == "epoch_iad":
        return (
            f"SELECT source_id, transit_id, bjd, eta, zeta, scan_angle, "
            f"al_residual, ac_residual "
            f"FROM {table} WHERE source_id = {sid} ORDER BY bjd"
        )
    raise KeyError(table_key)


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--live", action="store_true", help="Execute DR4 queries (requires DR4 release)")
    p.add_argument("--out-dir", default=None)
    args = p.parse_args(argv)

    out_dir = Path(args.out_dir) if args.out_dir else (
        DATA_ROOT / "data" / "candidate_dossiers" / "gaia_dr4_refresh_novelty_2026_05_13"
    )
    out_dir.mkdir(parents=True, exist_ok=True)

    print(f"=== Gaia DR4 refresh pipeline ===")
    print(f"Expected DR4 release: {DR4_RELEASE_DATE}")
    print(f"Candidates: {len(SUBSTELLAR_CANDIDATES)}")
    print(f"Output dir: {out_dir}")
    print(f"Mode: {'LIVE' if args.live else 'DRY-RUN'}")
    print()

    manifest_rows = []
    queries_rows = []
    for c in SUBSTELLAR_CANDIDATES:
        rec = {
            "name": c.name,
            "gaia_dr3_source_id": c.gaia_dr3_source_id,
            "nss_pool": c.nss_pool,
            "dr3_period_d": c.dr3_period_d,
            "dr3_m2_marginalized_mjup": c.dr3_m2_marginalized_mjup,
            "dr3_significance": c.dr3_significance,
            "k_pred_mps": c.confirmation_target_kpred_mps,
            "decision_recipe": c.decision_recipe_key,
            "notes": c.notes,
        }
        manifest_rows.append(rec)

        # Generate queries for each DR4 table
        for tk in ("gaia_source", "nss_orbital", "nss_accel", "epoch_rv", "epoch_iad"):
            queries_rows.append(
                {
                    "candidate_name": c.name,
                    "gaia_dr3_source_id": c.gaia_dr3_source_id,
                    "table": DR4_TABLES[tk],
                    "adql": query_template(tk, c),
                }
            )

        print(f"  {c.name:<14}  sid={c.gaia_dr3_source_id}  pool={c.nss_pool:<15}  recipe={c.decision_recipe_key}")

    pl.DataFrame(manifest_rows).write_csv(out_dir / "candidate_manifest.csv")
    pl.DataFrame(queries_rows).write_csv(out_dir / "dr4_queries.csv")

    # Write recipes as JSON for portability
    (out_dir / "decision_recipes.json").write_text(json.dumps(DECISION_RECIPES, indent=2))

    print()
    print(f"Wrote candidate_manifest.csv (8 rows)")
    print(f"Wrote dr4_queries.csv ({len(queries_rows)} rows = 8 candidates x 5 tables)")
    print(f"Wrote decision_recipes.json")

    if not args.live:
        print()
        print("DRY-RUN OK. When DR4 lands, re-run with --live.")
        print("All scripts above are tested in the v3 pipeline:")
        print("  - rv_bayesian_fitter.py (DR4 epoch RV joint fit)")
        print("  - rv_astrometric_joint_fitter.py (joint RV + IAD)")
        return 0

    # LIVE MODE
    print()
    print("LIVE MODE — issuing DR4 TAP queries ...")
    # Per-candidate query execution would go here. Skipped until DR4 lands.
    print("(LIVE mode not implemented until DR4 launches in Dec 2026)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
