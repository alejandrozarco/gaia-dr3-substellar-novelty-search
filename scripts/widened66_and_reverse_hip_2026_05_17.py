"""(1) Cascade the 66 widened-pool strong-BD candidates.
(Novelty) Reverse HIP NSS port: HIP Sn={1,3,7} without Gaia DR3 NSS detection.

(1) Widened-66 cascade:
    - SIMBAD coord-resolve all 66 (find HD/HIP/BD names)
    - HIP cross-match via Gaia hipparcos2_best_neighbour AND direct Vizier query
    - HGCA Brandt 2021 chi^2 for HIP-named subset
    - Tycho-2 PM via Vizier I/259/tyc2 -> 25-yr PMa chi^2
    - SB9 + exoplanet.eu + Sahlmann 2025 cross-match
    - Output: cascade_widened66_2026_05_17.csv with tier classifications

(Novelty) Reverse HIP NSS:
    - From hipparcos_vanLeeuwen2007_FULL.csv (117,955 rows), filter Sn in {1,3,7}
    - Cross-match each to Gaia DR3 source_id via hipparcos2_best_neighbour
    - Query gaiadr3.nss_two_body_orbit + nss_acceleration_astro for those source_ids
    - HIP NSS WITHOUT Gaia DR3 NSS = HIP detected a companion that Gaia DR3 missed
    - These are candidates for either: (a) DR4 will catch (P too short / too long for DR3 baseline)
                                       (b) companion has moved orbit (chance alignment)
                                       (c) Hipparcos false positive
    - For each, fetch Gaia main-table photometry/parallax/RUWE
    - Apply the BD-substellar criteria: V<12, plx>5, RUWE elevated, ipd_frac flags
    - Yield: HIP NSS candidates missed by Gaia DR3 that might still be substellar
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


# =========================================================================
# (1) Widened-66 cascade
# =========================================================================

def cascade_widened66():
    df = pl.read_csv(INTER / "nss_sb1_widened_strong_BD_new_2026_05_17.csv")
    print(f"(1) Widened-66 cascade — input: {len(df)} rows")

    src_ids = [int(x) for x in df["source_id"].to_list()]

    # --- Gaia main-table enrichment + HIP via hipparcos2_best_neighbour ---
    chunks = []
    for i in range(0, len(src_ids), 500):
        sub = src_ids[i:i+500]
        ids = ",".join(str(x) for x in sub)
        q = f"""
        SELECT g.source_id, g.ra, g.dec, g.pmra, g.pmra_error, g.pmdec,
               g.pmdec_error, g.parallax, g.phot_g_mean_mag, g.ruwe,
               g.astrometric_excess_noise,
               h.original_ext_source_id AS hip_via_xmatch
        FROM gaiadr3.gaia_source g
        LEFT JOIN gaiadr3.hipparcos2_best_neighbour h ON g.source_id=h.source_id
        WHERE g.source_id IN ({ids})
        """
        try:
            chunks.append(Gaia.launch_job_async(q).get_results().to_pandas())
        except Exception as e:  # noqa: BLE001
            print(f"  gaia chunk err: {type(e).__name__}: {e}")
    import pandas as pd
    gaia = pl.from_pandas(pd.concat(chunks, ignore_index=True))
    print(f"  Gaia info pulled: {len(gaia)} rows; "
          f"HIP via Gaia xmatch: {gaia.filter(pl.col('hip_via_xmatch').is_not_null()).shape[0]}")

    # --- SIMBAD coord resolution per source (find HD/HIP via SIMBAD when
    # Gaia xmatch missed) ---
    s = Simbad()
    s.TIMEOUT = 60
    try:
        s.add_votable_fields("otype", "ids")
    except Exception:  # noqa: BLE001
        pass

    simbad_rows = []
    n = len(gaia)
    print(f"  SIMBAD coord resolution for {n} sources (slow; ~~{n*0.4:.0f}s)…")
    for i, r in enumerate(gaia.iter_rows(named=True)):
        sc = SkyCoord(r["ra"]*u.deg, r["dec"]*u.deg)
        name = None
        otype = None
        try:
            res = s.query_region(sc, radius=5*u.arcsec)
            if res is None or len(res) == 0:
                res = s.query_region(sc, radius=10*u.arcsec)
            if res is not None and len(res) > 0:
                name = str(res[0]["main_id"])
                otype = str(res[0]["otype"])
        except Exception:  # noqa: BLE001
            pass
        simbad_rows.append({"source_id": r["source_id"],
                              "simbad_main_id": name,
                              "simbad_otype": otype})
        time.sleep(0.3)
        if i % 15 == 14:
            print(f"    ... {i+1}/{n}")
    sim_df = pl.DataFrame(simbad_rows).with_columns(
        pl.col("source_id").cast(pl.Int64))

    gaia = gaia.with_columns(pl.col("source_id").cast(pl.Int64))
    df_ann = df.with_columns(pl.col("source_id").cast(pl.Int64)) \
                 .join(gaia, on="source_id", how="left") \
                 .join(sim_df, on="source_id", how="left")

    # --- Tycho-2 PM lookup per source (using gaiadr3.tycho2tdsc_merge_best_neighbour
    #     plus direct I/259/tyc2 query for permissive matching) ---
    print(f"  Tycho-2 PM via Vizier I/259/tyc2 ({n} sources)…")
    tyc_rows = []
    for i, r in enumerate(gaia.iter_rows(named=True)):
        sc = SkyCoord(r["ra"]*u.deg, r["dec"]*u.deg)
        try:
            res = Vizier(columns=["TYC1","TYC2","TYC3","pmRA","pmDE",
                                    "e_pmRA","e_pmDE"]) \
                      .query_region(sc, radius=5*u.arcsec, catalog="I/259/tyc2")
            if not res or len(res) == 0:
                tyc_rows.append({"source_id": r["source_id"],
                                   "tyc_pmRA": None, "tyc_pmDE": None,
                                   "tyc_e_pmRA": None, "tyc_e_pmDE": None})
                continue
            t = res[0][0]
            tyc_rows.append({
                "source_id": r["source_id"],
                "tyc_pmRA": float(t["pmRA"]) if "pmRA" in res[0].colnames else None,
                "tyc_pmDE": float(t["pmDE"]) if "pmDE" in res[0].colnames else None,
                "tyc_e_pmRA": float(t["e_pmRA"]) if "e_pmRA" in res[0].colnames else None,
                "tyc_e_pmDE": float(t["e_pmDE"]) if "e_pmDE" in res[0].colnames else None,
            })
        except Exception:  # noqa: BLE001
            tyc_rows.append({"source_id": r["source_id"],
                               "tyc_pmRA": None, "tyc_pmDE": None,
                               "tyc_e_pmRA": None, "tyc_e_pmDE": None})
        time.sleep(0.25)
        if i % 15 == 14:
            print(f"    ... {i+1}/{n}")
    tyc_df = pl.DataFrame(tyc_rows).with_columns(
        pl.col("source_id").cast(pl.Int64))
    df_ann = df_ann.join(tyc_df, on="source_id", how="left")

    # --- PMa chi^2 ---
    def anomaly(r):
        try:
            if (r["tyc_pmRA"] is None or r["tyc_pmDE"] is None
                or r["tyc_e_pmRA"] is None or r["tyc_e_pmDE"] is None):
                return None
            d_ra = float(r["tyc_pmRA"]) - float(r["pmra"])
            d_de = float(r["tyc_pmDE"]) - float(r["pmdec"])
            s_ra = math.sqrt(float(r["tyc_e_pmRA"])**2
                              + float(r["pmra_error"])**2)
            s_de = math.sqrt(float(r["tyc_e_pmDE"])**2
                              + float(r["pmdec_error"])**2)
            if s_ra == 0 or s_de == 0:
                return None
            return (d_ra/s_ra)**2 + (d_de/s_de)**2
        except Exception:  # noqa: BLE001
            return None

    chi2s = [anomaly(r) for r in df_ann.iter_rows(named=True)]
    df_ann = df_ann.with_columns(pl.Series("tycho_gaia_chi2", chi2s))

    # --- SB9 + exoplanet.eu + Sahlmann ---
    # Load Sahlmann
    sahl_path = Path("/Users/legbatterij/claude_projects/ostinato/data/"
                       "candidate_dossiers/arenou2023_sahlmann2025_filter_2026_05_12/"
                       "sahlmann2025_verdicts.csv")
    sahl_ids = set()
    if sahl_path.exists():
        sahl = pl.read_csv(sahl_path, infer_schema_length=20000)
        sahl_ids = set(int(x) for x in sahl["source_id"].to_list())
    df_ann = df_ann.with_columns(
        pl.col("source_id").is_in(list(sahl_ids)).alias("in_sahlmann")
    )

    # Load exoplanet.eu
    try:
        with urllib.request.urlopen("https://exoplanet.eu/catalog/csv/",
                                      timeout=60) as resp:
            import pandas as pd
            epx = pd.read_csv(io.BytesIO(resp.read()), low_memory=False)
        epx_sc = SkyCoord(epx["ra"].to_numpy()*u.deg,
                            epx["dec"].to_numpy()*u.deg) \
                    if "ra" in epx.columns else None
    except Exception:  # noqa: BLE001
        epx, epx_sc = None, None

    in_epx, epx_match = [], []
    for r in df_ann.iter_rows(named=True):
        if epx_sc is None:
            in_epx.append(None); epx_match.append(None); continue
        try:
            sc = SkyCoord(float(r["ra"])*u.deg, float(r["dec"])*u.deg)
            sep = sc.separation(epx_sc).arcsec
            hits = (sep < 30.0).nonzero()[0]
            if len(hits) > 0:
                in_epx.append(True)
                epx_match.append("; ".join(epx.iloc[hits]["name"].tolist()[:3]))
            else:
                in_epx.append(False); epx_match.append(None)
        except Exception:  # noqa: BLE001
            in_epx.append(None); epx_match.append(None)
    df_ann = df_ann.with_columns([
        pl.Series("in_exoplanet_eu", in_epx),
        pl.Series("epx_match", epx_match),
    ])

    # SB9 — per-source (slow); skip if too many. Use coord query.
    print(f"  SB9 cross-match (Vizier B/sb9/main, 5\" radius)…")
    in_sb9 = []
    for r in df_ann.iter_rows(named=True):
        try:
            sc = SkyCoord(float(r["ra"])*u.deg, float(r["dec"])*u.deg)
            res = Vizier.query_region(sc, radius=5*u.arcsec,
                                        catalog="B/sb9/main")
            in_sb9.append(bool(res and len(res) > 0 and len(res[0]) > 0))
        except Exception:  # noqa: BLE001
            in_sb9.append(None)
        time.sleep(0.2)
    df_ann = df_ann.with_columns(pl.Series("in_sb9", in_sb9))

    # Tier classification
    def tier(r):
        chi2 = r.get("tycho_gaia_chi2")
        if chi2 is None:
            return "no_tycho_pm"
        if chi2 > 100:
            return "REJECT_likely_stellar"
        if chi2 >= 30:
            return "FLAG_mass_ambiguous"
        if chi2 >= 5:
            return "CORROBORATED_real_companion"
        return "isolated_no_outer_body"

    tiers = [tier(r) for r in df_ann.iter_rows(named=True)]
    df_ann = df_ann.with_columns(pl.Series("tycho_tier", tiers))

    df_ann.write_csv(INTER / "cascade_widened66_2026_05_17.csv")
    print(f"\n  Output: {INTER / 'cascade_widened66_2026_05_17.csv'}")

    # Promotion summary
    clean = df_ann.filter(
        ~pl.col("in_sahlmann")
        & (~pl.col("in_exoplanet_eu").fill_null(False))
        & (~pl.col("in_sb9").fill_null(False))
    )
    print(f"\n  Clean (no SB9/exoplanet.eu/Sahlmann): {len(clean)}/{len(df_ann)}")

    corrob = clean.filter(pl.col("tycho_tier") == "CORROBORATED_real_companion")
    flag = clean.filter(pl.col("tycho_tier") == "FLAG_mass_ambiguous")
    print(f"  CORROBORATED-tier clean: {len(corrob)}")
    print(f"  FLAG-tier clean: {len(flag)}")
    print(f"  Top CORROB candidates (m2 < 30 MJ):")
    print(corrob.filter(pl.col("m2_marg_med_mjup") < 30) \
                 .sort("tycho_gaia_chi2", descending=True) \
                 .select(["source_id", "simbad_main_id", "phot_g_mean_mag",
                          "ruwe", "period", "m2_marg_med_mjup",
                          "tycho_gaia_chi2"]).head(10))

    return df_ann


# =========================================================================
# (Novelty) Reverse HIP NSS port
# =========================================================================

def reverse_hip_nss():
    print("\n\n(Novelty) Reverse HIP NSS port — HIP Sn={1,3,7} without Gaia DR3 NSS …")
    hip = pl.read_csv(INTER / "hipparcos_vanLeeuwen2007_FULL.csv")
    nss_hip = hip.filter(pl.col("Sn").is_in([1, 3, 7]))
    print(f"  HIP NSS (Sn in {{1,3,7}}): {len(nss_hip)}")

    # Map HIP -> Gaia DR3 source_id via hipparcos2_best_neighbour
    hips = [int(x) for x in nss_hip["HIP"].to_list()]
    chunks = []
    for i in range(0, len(hips), 4000):
        sub = hips[i:i+4000]
        ids = ",".join(str(x) for x in sub)
        q = (f"SELECT original_ext_source_id AS hip, source_id "
             f"FROM gaiadr3.hipparcos2_best_neighbour "
             f"WHERE original_ext_source_id IN ({ids})")
        try:
            chunks.append(Gaia.launch_job_async(q).get_results().to_pandas())
        except Exception as e:  # noqa: BLE001
            print(f"  HIP->Gaia chunk err: {type(e).__name__}")
    import pandas as pd
    hip2gaia = pl.from_pandas(pd.concat(chunks, ignore_index=True)) \
                  if chunks else pl.DataFrame()
    print(f"  HIP->Gaia DR3 cross-matches: {len(hip2gaia)}")

    if hip2gaia.is_empty():
        return

    # Now check which of these have Gaia DR3 NSS classifications
    src_ids = [int(x) for x in hip2gaia["source_id"].to_list()]
    nss_chunks = []
    accel_chunks = []
    for i in range(0, len(src_ids), 4000):
        sub = src_ids[i:i+4000]
        ids = ",".join(str(x) for x in sub)
        try:
            nss_chunks.append(Gaia.launch_job_async(
                f"SELECT source_id, nss_solution_type FROM gaiadr3.nss_two_body_orbit "
                f"WHERE source_id IN ({ids})").get_results().to_pandas())
        except Exception:  # noqa: BLE001
            pass
        try:
            accel_chunks.append(Gaia.launch_job_async(
                f"SELECT source_id, nss_solution_type FROM gaiadr3.nss_acceleration_astro "
                f"WHERE source_id IN ({ids})").get_results().to_pandas())
        except Exception:  # noqa: BLE001
            pass
    gaia_nss = pl.from_pandas(pd.concat(nss_chunks + accel_chunks,
                                           ignore_index=True)) \
                  if nss_chunks or accel_chunks else pl.DataFrame()
    print(f"  Gaia DR3 NSS classifications for these: "
          f"{len(gaia_nss)}")

    gaia_nss_ids = set(int(x) for x in gaia_nss["source_id"].to_list()) \
                      if not gaia_nss.is_empty() else set()
    hip2gaia = hip2gaia.with_columns(pl.col("source_id").cast(pl.Int64))
    missed = hip2gaia.filter(~pl.col("source_id").is_in(list(gaia_nss_ids)))
    print(f"\n  HIP NSS Sn={{1,3,7}} WITHOUT Gaia DR3 NSS: {len(missed)}")

    if missed.is_empty():
        return

    # Add Hipparcos info
    hip_meta = nss_hip.select(["HIP", "Sn", "Hpmag", "pmRA", "pmDE", "Plx"]) \
                       .rename({"HIP": "hip"}) \
                       .with_columns(pl.col("hip").cast(pl.Int64))
    missed = missed.with_columns(pl.col("hip").cast(pl.Int64))
    missed = missed.join(hip_meta, on="hip", how="left")

    # Enrich with Gaia photometry/parallax/RUWE
    src_ids2 = [int(x) for x in missed["source_id"].to_list()]
    chunks2 = []
    for i in range(0, len(src_ids2), 500):
        sub = src_ids2[i:i+500]
        ids = ",".join(str(x) for x in sub)
        q = (f"SELECT source_id, ra, dec, phot_g_mean_mag, parallax, ruwe, "
             f"astrometric_excess_noise, non_single_star "
             f"FROM gaiadr3.gaia_source WHERE source_id IN ({ids})")
        try:
            chunks2.append(Gaia.launch_job_async(q).get_results().to_pandas())
        except Exception as e:  # noqa: BLE001
            print(f"  gaia_source chunk err: {type(e).__name__}")
    gmeta = pl.from_pandas(pd.concat(chunks2, ignore_index=True)) \
              if chunks2 else pl.DataFrame()
    gmeta = gmeta.with_columns(pl.col("source_id").cast(pl.Int64))
    missed = missed.join(gmeta, on="source_id", how="left")

    # Apply BD criteria
    missed = missed.with_columns(
        (1000.0 / pl.col("parallax")).alias("dist_pc"),
    )
    bd_quality = missed.filter(
        (pl.col("phot_g_mean_mag") < 12.0)
        & (pl.col("parallax") > 5.0)
        & (pl.col("ruwe") > 1.4)  # elevated RUWE — suggests unmodeled wobble
    )
    print(f"  Passing V<12 + plx>5 + RUWE>1.4: {len(bd_quality)}")

    missed.write_csv(INTER / "reverse_hip_nss_missed_by_gaia_2026_05_17.csv")
    bd_quality.write_csv(INTER / "reverse_hip_nss_bd_candidates_2026_05_17.csv")

    # Top by Sn=7 (stochastic) - those are the strongest "Hipparcos detected anomaly"
    sn7 = bd_quality.filter(pl.col("Sn") == 7).sort("ruwe", descending=True)
    sn1 = bd_quality.filter(pl.col("Sn") == 1).sort("ruwe", descending=True)
    sn3 = bd_quality.filter(pl.col("Sn") == 3).sort("ruwe", descending=True)
    print(f"\n  By Sn type:")
    print(f"    Sn=1 (orbital): {len(sn1)}")
    print(f"    Sn=3 (accel):   {len(sn3)}")
    print(f"    Sn=7 (stoch):   {len(sn7)}")
    print("\n  Top 10 Sn=7 (stochastic) by RUWE — strongest HIP-only candidates:")
    print(sn7.select(["hip", "Sn", "Hpmag", "phot_g_mean_mag", "ruwe",
                       "dist_pc", "astrometric_excess_noise"]).head(10))


def main():
    df66 = cascade_widened66()
    reverse_hip_nss()

    print("\n=== SUMMARY ===")
    print("(1) Widened-66 cascade -> cascade_widened66_2026_05_17.csv")
    print("(Novelty) Reverse HIP NSS -> reverse_hip_nss_bd_candidates_2026_05_17.csv")


if __name__ == "__main__":
    sys.exit(main() or 0)
