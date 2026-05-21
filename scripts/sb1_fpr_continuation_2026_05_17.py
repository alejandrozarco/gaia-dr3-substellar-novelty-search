"""Continuation push: deeper SB1 + Tycho-Gaia + Tier-2 candidate vetting.

Five tasks in one script:

  1. Re-resolve the missing 6th anon SB1 (Gaia DR3 9794874309557736960).
  2. Compute Tycho-Gaia 25-yr PMa for all 110 anonymous SB1 candidates
     (not just the 6 high-AEN). Output sorted by chi^2.
  3. Deep-vet HD 104289 + CD-70 5 (the two Tier-2-tier candidates from
     the previous turn: chi^2 = 10.7 and 9.6 respectively).
  4. Widen the NSS SB1 pool: V<13, plx>2, significance>=3, P 10-10000 d
     -> see how many extra substellar candidates surface.
  5. FPR crowded-field cross-check: download crowded_field_source CDN
     shards and verify 0 overlap with our anon SB1 pool. Only relevant
     for sources possibly within the 9 FPR dense fields (omega Cen,
     LMC/SMC clusters).
"""
from __future__ import annotations

import io
import math
import sys
import time
import urllib.request
from pathlib import Path

import astropy.units as u
import polars as pl
from astropy.coordinates import SkyCoord
from astroquery.gaia import Gaia
from astroquery.simbad import Simbad
from astroquery.vizier import Vizier

ROOT = Path("/tmp/gaia-novelty-publication")
INTER = ROOT / "data" / "intermediate"
INTER.mkdir(parents=True, exist_ok=True)


# =========================================================================
# 1 + 2: Tycho-Gaia PMa for the full anon SB1 pool
# =========================================================================

def fetch_anon_full(source_ids: list[int]) -> pl.DataFrame:
    """Pull ra/dec/PM/parallax for all 110 anon source_ids."""
    chunks = []
    BATCH = 200
    for i in range(0, len(source_ids), BATCH):
        sub = source_ids[i:i+BATCH]
        ids = ",".join(str(int(x)) for x in sub)
        q = (f"SELECT source_id, ra, dec, pmra, pmra_error, pmdec, pmdec_error, "
             f"parallax, parallax_error, phot_g_mean_mag, ruwe, "
             f"astrometric_excess_noise "
             f"FROM gaiadr3.gaia_source WHERE source_id IN ({ids})")
        try:
            res = Gaia.launch_job_async(q).get_results().to_pandas()
            chunks.append(res)
        except Exception as e:  # noqa: BLE001
            print(f"  anon batch {i//BATCH} err: {type(e).__name__}: {e}")
    if not chunks:
        return pl.DataFrame()
    import pandas as pd
    return pl.from_pandas(pd.concat(chunks, ignore_index=True))


def tycho2_pm_per_source(coords: pl.DataFrame) -> list[dict]:
    """Per-source Vizier coordinate query against Tycho-2 (I/259/tyc2)."""
    Vizier.ROW_LIMIT = 3
    Vizier.TIMEOUT = 60
    rows = []
    n = len(coords)
    for i, r in enumerate(coords.iter_rows(named=True)):
        try:
            sc = SkyCoord(r["ra"] * u.deg, r["dec"] * u.deg)
            res = Vizier(columns=["TYC1", "TYC2", "TYC3",
                                    "pmRA", "pmDE",
                                    "e_pmRA", "e_pmDE",
                                    "BTmag", "VTmag"]) \
                      .query_region(sc, radius=5 * u.arcsec,
                                     catalog="I/259/tyc2")
            if not res or len(res) == 0:
                rows.append({"source_id": r["source_id"],
                             "tyc_pmRA": None, "tyc_pmDE": None,
                             "tyc_e_pmRA": None, "tyc_e_pmDE": None,
                             "tyc_VTmag": None, "tyc_status": "no_match"})
                continue
            t = res[0]
            row = t[0]
            rows.append({
                "source_id": r["source_id"],
                "tyc_pmRA": float(row["pmRA"]) if "pmRA" in t.colnames else None,
                "tyc_pmDE": float(row["pmDE"]) if "pmDE" in t.colnames else None,
                "tyc_e_pmRA": float(row["e_pmRA"]) if "e_pmRA" in t.colnames else None,
                "tyc_e_pmDE": float(row["e_pmDE"]) if "e_pmDE" in t.colnames else None,
                "tyc_VTmag": float(row["VTmag"]) if "VTmag" in t.colnames else None,
                "tyc_status": "ok"})
        except Exception as e:  # noqa: BLE001
            rows.append({"source_id": r["source_id"],
                          "tyc_pmRA": None, "tyc_pmDE": None,
                          "tyc_e_pmRA": None, "tyc_e_pmDE": None,
                          "tyc_VTmag": None,
                          "tyc_status": f"ERR:{type(e).__name__}"})
        time.sleep(0.25)
        if i % 25 == 24:
            print(f"  ... {i+1}/{n} processed")
    return rows


def compute_pma_anomaly(tyc_rows: list[dict], gaia_df: pl.DataFrame) -> pl.DataFrame:
    tyc = pl.DataFrame(tyc_rows).with_columns(
        pl.col("source_id").cast(pl.Int64)
    )
    gaia = gaia_df.select([
        "source_id", "ra", "dec", "pmra", "pmra_error", "pmdec", "pmdec_error",
        "phot_g_mean_mag", "ruwe", "astrometric_excess_noise"
    ]).with_columns(pl.col("source_id").cast(pl.Int64))
    df = gaia.join(tyc, on="source_id", how="left")

    def anomaly(r):
        if r["tyc_pmRA"] is None or r["tyc_pmDE"] is None:
            return (None, None, None, None)
        try:
            d_ra = float(r["tyc_pmRA"]) - float(r["pmra"])
            d_de = float(r["tyc_pmDE"]) - float(r["pmdec"])
            etr = float(r["tyc_e_pmRA"]) or 0.0
            etd = float(r["tyc_e_pmDE"]) or 0.0
            egr = float(r["pmra_error"]) or 0.0
            egd = float(r["pmdec_error"]) or 0.0
            s_ra = math.sqrt(etr**2 + egr**2)
            s_de = math.sqrt(etd**2 + egd**2)
            sig_ra = d_ra / s_ra if s_ra > 0 else None
            sig_de = d_de / s_de if s_de > 0 else None
            chi2 = (sig_ra**2 + sig_de**2
                    if sig_ra is not None and sig_de is not None else None)
            sigma_max = max(abs(sig_ra or 0), abs(sig_de or 0))
            return (sig_ra, sig_de, chi2, sigma_max)
        except Exception:  # noqa: BLE001
            return (None, None, None, None)

    a = [anomaly(r) for r in df.iter_rows(named=True)]
    df = df.with_columns([
        pl.Series("pm_anomaly_RA_sigma", [x[0] for x in a]),
        pl.Series("pm_anomaly_DE_sigma", [x[1] for x in a]),
        pl.Series("pm_anomaly_chi2", [x[2] for x in a]),
        pl.Series("pm_anomaly_max_sigma", [x[3] for x in a]),
    ])
    return df


# =========================================================================
# 3: Deep-vet HD 104289 + CD-70 5
# =========================================================================

TIER2_CANDS = {
    "HD 104289": {"source_id": 1576108450508750208, "chi2_tg": 10.7,
                   "m2_marg": 47.6, "P": 886, "e": 0.27, "K": 0.87},
    "CD-70 5":   {"source_id": 4702272586713535872, "chi2_tg": 9.6,
                   "m2_marg": 58.8, "P": 76, "e": 0.25, "K": 2.22},
}


def vet_tier2(cands: dict) -> pl.DataFrame:
    """For each Tier-2: SB9, exoplanet.eu, Sahlmann verdict cross-match."""
    rows = []

    # Load Sahlmann verdict table once
    sahl_path = Path("/Users/legbatterij/claude_projects/ostinato/data/"
                       "candidate_dossiers/arenou2023_sahlmann2025_filter_2026_05_12/"
                       "sahlmann2025_verdicts.csv")
    sahl = pl.read_csv(sahl_path, infer_schema_length=20000) \
              if sahl_path.exists() else pl.DataFrame()
    sahl_ids = set(int(x) for x in sahl["source_id"].to_list()) if not sahl.is_empty() else set()

    # Load exoplanet.eu once
    try:
        with urllib.request.urlopen("https://exoplanet.eu/catalog/csv/",
                                      timeout=60) as resp:
            import pandas as pd
            epx = pd.read_csv(io.BytesIO(resp.read()), low_memory=False)
        if "ra" in epx.columns and "dec" in epx.columns:
            epx_sc = SkyCoord(epx["ra"].to_numpy()*u.deg,
                                epx["dec"].to_numpy()*u.deg)
        else:
            epx_sc = None
    except Exception:  # noqa: BLE001
        epx, epx_sc = None, None

    # Fetch coords from Gaia
    src_ids = [v["source_id"] for v in cands.values()]
    ids = ",".join(str(x) for x in src_ids)
    q = (f"SELECT source_id, ra, dec FROM gaiadr3.gaia_source "
         f"WHERE source_id IN ({ids})")
    gco = Gaia.launch_job_async(q).get_results().to_pandas()
    gco = gco.set_index("source_id")

    for name, c in cands.items():
        sid = c["source_id"]
        ra, dec = float(gco.loc[sid]["ra"]), float(gco.loc[sid]["dec"])
        sc = SkyCoord(ra*u.deg, dec*u.deg)

        # SB9
        try:
            res = Vizier.query_region(sc, radius=5*u.arcsec,
                                        catalog="B/sb9/main")
            in_sb9 = bool(res and len(res) > 0 and len(res[0]) > 0)
        except Exception:  # noqa: BLE001
            in_sb9 = None

        # exoplanet.eu
        if epx_sc is not None:
            sep = sc.separation(epx_sc).arcsec
            hits = (sep < 30.0).nonzero()[0]
            in_epx = len(hits) > 0
            epx_match = "; ".join(epx.iloc[hits]["name"].tolist()[:3]) if in_epx else None
        else:
            in_epx, epx_match = None, None

        # Sahlmann
        in_sahl = sid in sahl_ids

        # SIMBAD
        try:
            s = Simbad()
            s.TIMEOUT = 60
            try:
                s.add_votable_fields("otype", "ids")
            except Exception:  # noqa: BLE001
                pass
            sim_res = s.query_region(sc, radius=5*u.arcsec)
            simbad_id = str(sim_res[0]["main_id"]) if sim_res is not None and len(sim_res) > 0 else None
            simbad_ot = str(sim_res[0]["otype"]) if sim_res is not None and len(sim_res) > 0 else None
        except Exception:  # noqa: BLE001
            simbad_id, simbad_ot = None, None

        rows.append({"name": name, "source_id": sid,
                       "tycho_gaia_chi2": c["chi2_tg"],
                       "m2_marg": c["m2_marg"],
                       "P_d": c["P"], "e": c["e"], "K_kms": c["K"],
                       "in_sb9": in_sb9, "in_exoplanet_eu": in_epx,
                       "epx_match_name": epx_match,
                       "in_sahlmann": in_sahl,
                       "simbad_main_id": simbad_id,
                       "simbad_otype": simbad_ot})
    return pl.DataFrame(rows)


# =========================================================================
# 4: Widen SB1 pool
# =========================================================================

def widen_sb1_pool() -> dict:
    """Drop V<12 cut and parallax>5 cut. Lower significance to 3."""
    q = """
    SELECT
        nss.source_id,
        nss.period, nss.eccentricity,
        nss.semi_amplitude_primary, nss.semi_amplitude_primary_error,
        nss.significance, nss.inclination,
        g.ra, g.dec, g.phot_g_mean_mag, g.parallax, g.parallax_error,
        g.ruwe, g.astrometric_excess_noise
    FROM gaiadr3.nss_two_body_orbit nss
    JOIN gaiadr3.gaia_source g ON g.source_id = nss.source_id
    WHERE nss.nss_solution_type = 'SB1'
      AND nss.eccentricity IS NOT NULL
      AND nss.semi_amplitude_primary IS NOT NULL
      AND nss.significance >= 3.0
      AND nss.period BETWEEN 10.0 AND 10000.0
      AND g.phot_g_mean_mag < 13.0
      AND g.parallax > 2.0
    """
    print("Widened SB1 query (V<13, plx>2, sig>=3, P 10-10000d)…")
    res = Gaia.launch_job_async(q).get_results().to_pandas()
    return {"pool_size": len(res), "df": pl.from_pandas(res)}


# =========================================================================
# Main
# =========================================================================

def main():
    # ----- Step 1: load anon pool -----
    anon = pl.read_csv(INTER / "nss_sb1_anonymous_novel_2026_05_17.csv")
    print(f"Anonymous SB1 pool: {len(anon)} sources")

    # Verify the 6th
    target6 = 9794874309557736960
    has6 = anon.filter(pl.col("source_id") == target6)
    print(f"6th candidate present in anon pool: {len(has6)} row")

    src_ids = [int(x) for x in anon["source_id"].to_list()]
    print(f"\n=== Step 1+2: Tycho-Gaia PMa for {len(src_ids)} anon sources ===")
    coords = fetch_anon_full(src_ids)
    print(f"  Gaia info fetched: {len(coords)} rows")

    print("  Querying Tycho-2 per-source (slow; ~~110 × 0.25s = 30s)…")
    tyc_rows = tycho2_pm_per_source(coords)
    pma = compute_pma_anomaly(tyc_rows, coords)

    n_with_tyc = pma.filter(pl.col("tyc_pmRA").is_not_null()).shape[0]
    n_high_chi2 = pma.filter(
        (pl.col("pm_anomaly_chi2").is_not_null())
        & (pl.col("pm_anomaly_chi2") >= 30.0)
    ).shape[0]
    n_corrob = pma.filter(
        (pl.col("pm_anomaly_chi2").is_not_null())
        & (pl.col("pm_anomaly_chi2") >= 5.0)
        & (pl.col("pm_anomaly_chi2") < 30.0)
    ).shape[0]
    print(f"  Tycho-2 cross-matches obtained: {n_with_tyc} / {len(pma)}")
    print(f"  PMa chi^2 >= 30 (FLAG/REJECT tier): {n_high_chi2}")
    print(f"  PMa chi^2 in [5, 30] (CORROBORATED tier): {n_corrob}")

    # Join in mass-marginalized info
    anon_min = anon.select(["source_id", "m2_marg_med_mjup",
                              "m2_marg_1sig_lo_mjup",
                              "m2_marg_1sig_hi_mjup",
                              "period", "eccentricity",
                              "semi_amplitude_primary"]) \
                    .with_columns(pl.col("source_id").cast(pl.Int64))
    pma_final = pma.join(anon_min, on="source_id", how="left")
    pma_final.write_csv(INTER / "anon_sb1_tycho_pma_FULL_110.csv")

    # Print sorted top
    top = pma_final.filter(pl.col("pm_anomaly_chi2").is_not_null()) \
                    .sort("pm_anomaly_chi2", descending=True).head(15)
    print("\nTop 15 anon SB1 by Tycho-Gaia PMa chi^2:")
    print(top.select(["source_id", "phot_g_mean_mag", "ruwe",
                       "period", "m2_marg_med_mjup",
                       "pm_anomaly_chi2", "pm_anomaly_max_sigma"]))

    # ----- Step 3: deep-vet Tier-2 -----
    print("\n=== Step 3: Deep-vet HD 104289 + CD-70 5 ===")
    tier2_vet = vet_tier2(TIER2_CANDS)
    tier2_vet.write_csv(INTER / "tier2_deep_vet_2026_05_17.csv")
    print(tier2_vet)

    # ----- Step 4: widen SB1 pool -----
    print("\n=== Step 4: Widened SB1 pool ===")
    wider = widen_sb1_pool()
    print(f"  Widened pool: {wider['pool_size']} sources")
    wider["df"].write_csv(INTER / "nss_sb1_pool_widened_v13_plx2_sig3.csv")

    # Summary
    print("\n=== SUMMARY ===")
    print(f"  Tycho-Gaia PMa for full anon SB1 pool: "
          f"{n_with_tyc}/110 with Tycho-2 match")
    print(f"  FLAG-tier (chi^2 >= 30): {n_high_chi2}")
    print(f"  CORROBORATED-tier (5 <= chi^2 < 30): {n_corrob}")
    print(f"  HD 104289 + CD-70 5 vetting: see tier2_deep_vet csv")
    print(f"  Widened SB1 pool: {wider['pool_size']} sources "
          f"(vs original 3,049)")
    print(f"  -> increase factor: "
          f"{wider['pool_size']/3049:.2f}×")


if __name__ == "__main__":
    sys.exit(main() or 0)
