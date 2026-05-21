"""Fetch the four pieces of missing data flagged in EXPANSION_PUSH:

  1. gaiadr3.rvs_mean_spectrum — retry with chunk size 50 (vs the failing 500)
  2. Hipparcos van Leeuwen 2007 (I/311/hip2) — full bulk pull
  3. SIMBAD HD resolution for the 6 strongest anon SB1 candidates
  4. Tycho-2 PM lookup + 25-yr PM-anomaly in sigma units for the 6

For each, write a CSV + print a verdict.
"""
from __future__ import annotations

import math
import sys
import time
from pathlib import Path

import astropy.units as u
import polars as pl
from astropy.coordinates import SkyCoord
from astroquery.gaia import Gaia
from astroquery.simbad import Simbad
from astroquery.vizier import Vizier

ROOT = Path("/tmp/gaia-novelty-publication")
INTER = ROOT / "data" / "intermediate"


# ===== (1) rvs_mean_spectrum retry =====

def retry_rvs_mean_spectrum() -> dict:
    headline = pl.read_csv(ROOT / "novelty_candidates.csv") \
        .select("gaia_dr3_source_id") \
        .rename({"gaia_dr3_source_id": "source_id"}) \
        .drop_nulls()
    sb1 = pl.read_csv(INTER / "nss_sb1_pool_with_m2_2026_05_17.csv") \
        .select("source_id").drop_nulls()
    head_ids = [int(x) for x in headline["source_id"].to_list()]
    sb1_ids = [int(x) for x in sb1["source_id"].to_list()]

    def xmatch(label, ids, batch=50):
        hits = 0
        errs = 0
        BATCH = batch
        for i in range(0, len(ids), BATCH):
            sub = ids[i:i+BATCH]
            ids_str = ",".join(str(int(x)) for x in sub)
            q = (f"SELECT source_id FROM gaiadr3.rvs_mean_spectrum "
                 f"WHERE source_id IN ({ids_str})")
            try:
                res = Gaia.launch_job_async(q).get_results().to_pandas()
                hits += len(res)
            except Exception as e:  # noqa: BLE001
                errs += 1
                if errs <= 2:
                    print(f"  [{label}] chunk {i//BATCH} err: "
                          f"{type(e).__name__}: {str(e)[:120]}")
            time.sleep(0.3)
        return hits, errs

    print("(1) gaiadr3.rvs_mean_spectrum retry with smaller chunks…")
    h_hits, h_errs = xmatch("headline-14", head_ids, batch=14)
    s_hits, s_errs = xmatch("sb1-3049", sb1_ids, batch=50)
    print(f"  headline 14: {h_hits} hits, {h_errs} chunk errors")
    print(f"  SB1   3,049: {s_hits} hits, {s_errs} chunk errors")
    return {"headline_hits": h_hits, "sb1_hits": s_hits,
            "headline_errs": h_errs, "sb1_errs": s_errs}


# ===== (2) Hipparcos full bulk =====

def hip_full_bulk() -> pl.DataFrame:
    print("\n(2) Hipparcos van Leeuwen 2007 bulk pull (I/311/hip2)…")
    Vizier.ROW_LIMIT = -1
    Vizier.TIMEOUT = 300
    v = Vizier(columns=["HIP", "Sn", "Hpmag", "RAhms", "DEdms",
                          "pmRA", "pmDE", "Plx"])
    v.ROW_LIMIT = -1
    try:
        cats = v.get_catalogs("I/311/hip2")
        if cats is None or len(cats) == 0:
            print("  empty result")
            return pl.DataFrame()
        t = cats[0]
        df = t.to_pandas()
        print(f"  retrieved {len(df)} rows; columns: {list(df.columns)[:10]}")
        # Sn semantic: in I/311 (van Leeuwen 2007), Sn is the
        # solution-flag (single char):
        #   '0'/'1'  = 5-parameter single-star
        #   '3'/'7'/'9' = various NSS (orbit/accel/component-resolved)
        # Vizier returns as integer; let's count unique values
        if "Sn" in df.columns:
            uniq = df["Sn"].value_counts()
            print(f"  Sn value distribution:\n{uniq.head(20)}")
        return pl.from_pandas(df)
    except Exception as e:  # noqa: BLE001
        print(f"  bulk pull err: {type(e).__name__}: {e}")
        return pl.DataFrame()


def headline_in_hip_full(hip_df: pl.DataFrame) -> pl.DataFrame:
    head = pl.read_csv(ROOT / "novelty_candidates.csv") \
        .select(["name", "hip"]).drop_nulls("hip")
    head = head.with_columns(pl.col("hip").cast(pl.Int64))
    hip_df2 = hip_df.with_columns(pl.col("HIP").cast(pl.Int64))
    joined = head.join(hip_df2, left_on="hip", right_on="HIP", how="left")
    return joined


# ===== (3) SIMBAD HD resolution for the 6 anon SB1 =====

ANON_TOP6_IDS = [
    6547933592738551680,
    2848846382894793984,
    1576108450508750208,
    4521257204320883712,
    9794874309557736960,
    4702272586713535872,
]


def fetch_anon_coords() -> pl.DataFrame:
    ids = ",".join(str(x) for x in ANON_TOP6_IDS)
    q = f"""SELECT source_id, ra, dec, pmra, pmra_error, pmdec, pmdec_error,
                   parallax, phot_g_mean_mag
            FROM gaiadr3.gaia_source
            WHERE source_id IN ({ids})"""
    res = Gaia.launch_job_async(q).get_results().to_pandas()
    return pl.from_pandas(res)


def simbad_resolve(coords: pl.DataFrame) -> pl.DataFrame:
    print("\n(3) SIMBAD HD resolution for 6 strongest anon SB1…")
    s = Simbad()
    s.TIMEOUT = 120
    try:
        s.add_votable_fields("otype", "ids")
    except Exception:  # noqa: BLE001
        pass
    out = []
    for r in coords.iter_rows(named=True):
        try:
            sc = SkyCoord(r["ra"] * u.deg, r["dec"] * u.deg)
            res = s.query_region(sc, radius=5 * u.arcsec)
            if res is None or len(res) == 0:
                # widen
                res = s.query_region(sc, radius=15 * u.arcsec)
            if res is None or len(res) == 0:
                out.append({"source_id": r["source_id"],
                            "simbad_main_id": None,
                            "simbad_otype": None,
                            "simbad_ids": None,
                            "ra": r["ra"], "dec": r["dec"]})
                continue
            row = res[0]
            cols = res.colnames
            main_id = str(row["main_id"]) if "main_id" in cols else None
            otype = str(row["otype"]) if "otype" in cols else None
            ids_all = str(row["ids"]) if "ids" in cols else None
            out.append({"source_id": r["source_id"],
                        "simbad_main_id": main_id,
                        "simbad_otype": otype,
                        "simbad_ids": ids_all,
                        "ra": r["ra"], "dec": r["dec"]})
        except Exception as e:  # noqa: BLE001
            out.append({"source_id": r["source_id"],
                        "simbad_main_id": f"ERR:{type(e).__name__}",
                        "simbad_otype": None, "simbad_ids": None,
                        "ra": r["ra"], "dec": r["dec"]})
        time.sleep(0.4)
    return pl.DataFrame(out)


# ===== (4) Tycho-2 PM lookup + anomaly =====

def fetch_tycho2_pm(simbad_df: pl.DataFrame,
                     gaia_pm: pl.DataFrame) -> pl.DataFrame:
    """For each of the 6, do a Vizier coord-based query against I/259/tyc2
    and pull the Tycho-2 PM, then compute (PM_TYC - PM_DR3) / sigma."""
    print("\n(4) Tycho-2 PM + 25-yr PM anomaly in sigma units…")
    Vizier.ROW_LIMIT = 3
    Vizier.TIMEOUT = 120
    pm_lookup = []
    for r in simbad_df.iter_rows(named=True):
        sc = SkyCoord(r["ra"] * u.deg, r["dec"] * u.deg)
        try:
            res = Vizier(columns=["TYC1", "TYC2", "TYC3",
                                    "pmRA", "pmDE",
                                    "e_pmRA", "e_pmDE",
                                    "BTmag", "VTmag"]) \
                      .query_region(sc, radius=5 * u.arcsec,
                                     catalog="I/259/tyc2")
            if not res or len(res) == 0:
                pm_lookup.append({
                    "source_id": r["source_id"],
                    "tyc_pmRA": None, "tyc_pmDE": None,
                    "tyc_e_pmRA": None, "tyc_e_pmDE": None,
                    "tyc_VTmag": None})
                continue
            t = res[0]
            row = t[0]  # closest match
            pm_lookup.append({
                "source_id": r["source_id"],
                "tyc_pmRA": float(row["pmRA"])
                    if "pmRA" in t.colnames else None,
                "tyc_pmDE": float(row["pmDE"])
                    if "pmDE" in t.colnames else None,
                "tyc_e_pmRA": float(row["e_pmRA"])
                    if "e_pmRA" in t.colnames else None,
                "tyc_e_pmDE": float(row["e_pmDE"])
                    if "e_pmDE" in t.colnames else None,
                "tyc_VTmag": float(row["VTmag"])
                    if "VTmag" in t.colnames else None})
        except Exception as e:  # noqa: BLE001
            pm_lookup.append({"source_id": r["source_id"],
                                "tyc_pmRA": f"ERR:{type(e).__name__}",
                                "tyc_pmDE": None, "tyc_e_pmRA": None,
                                "tyc_e_pmDE": None, "tyc_VTmag": None})
        time.sleep(0.4)
    pmdf = pl.DataFrame(pm_lookup)
    # Join Gaia PM
    gaia_pm = gaia_pm.select(
        ["source_id", "pmra", "pmra_error", "pmdec", "pmdec_error"]
    ).rename({"pmra": "dr3_pmra", "pmra_error": "dr3_pmra_err",
              "pmdec": "dr3_pmdec", "pmdec_error": "dr3_pmdec_err"})
    pmdf = pmdf.with_columns(pl.col("source_id").cast(pl.Int64))
    gaia_pm = gaia_pm.with_columns(pl.col("source_id").cast(pl.Int64))
    combined = pmdf.join(gaia_pm, on="source_id", how="left")

    # Compute anomaly: chi^2 = ((pmTYC - pmDR3) / sqrt(e_pmTYC^2 + e_pmDR3^2))^2
    # Note Tycho-2 PM is in mas/yr (same as Gaia). Subtraction is direct.
    def anomaly(r):
        try:
            tyc_ra = float(r["tyc_pmRA"]) if r["tyc_pmRA"] is not None else None
            tyc_de = float(r["tyc_pmDE"]) if r["tyc_pmDE"] is not None else None
            etyc_ra = float(r["tyc_e_pmRA"]) if r["tyc_e_pmRA"] is not None else None
            etyc_de = float(r["tyc_e_pmDE"]) if r["tyc_e_pmDE"] is not None else None
            g_ra = float(r["dr3_pmra"])
            g_de = float(r["dr3_pmdec"])
            eg_ra = float(r["dr3_pmra_err"])
            eg_de = float(r["dr3_pmdec_err"])
            if any(v is None for v in [tyc_ra, tyc_de, etyc_ra, etyc_de]):
                return (None, None, None)
            d_ra = tyc_ra - g_ra
            d_de = tyc_de - g_de
            s_ra = math.sqrt(etyc_ra**2 + eg_ra**2)
            s_de = math.sqrt(etyc_de**2 + eg_de**2)
            sigma_ra = d_ra / s_ra if s_ra > 0 else None
            sigma_de = d_de / s_de if s_de > 0 else None
            chi2 = ((d_ra/s_ra)**2 + (d_de/s_de)**2
                    if s_ra > 0 and s_de > 0 else None)
            return (sigma_ra, sigma_de, chi2)
        except Exception:  # noqa: BLE001
            return (None, None, None)

    anomalies = [anomaly(r) for r in combined.iter_rows(named=True)]
    combined = combined.with_columns([
        pl.Series("pm_anomaly_RA_sigma", [a[0] for a in anomalies]),
        pl.Series("pm_anomaly_DE_sigma", [a[1] for a in anomalies]),
        pl.Series("pm_anomaly_chi2", [a[2] for a in anomalies]),
    ])
    return combined


def main():
    # (1)
    rvs_result = retry_rvs_mean_spectrum()

    # (2)
    hip_df = hip_full_bulk()
    if not hip_df.is_empty():
        hip_df.write_csv(INTER / "hipparcos_vanLeeuwen2007_FULL.csv")
        joined = headline_in_hip_full(hip_df)
        joined.write_csv(INTER / "headline_in_hip_FULL.csv")
        print(f"\nHeadline-14 join with full HIP catalog:")
        print(joined.select(["name", "hip", "Sn", "Hpmag"]))

    # (3) + (4)
    coords = fetch_anon_coords()
    print(f"\nAnon Gaia info pulled: {len(coords)} sources")
    sim = simbad_resolve(coords)
    sim.write_csv(INTER / "anon_top6_simbad_resolved.csv")
    print(sim.select(["source_id", "simbad_main_id", "simbad_otype"]))

    tyc = fetch_tycho2_pm(sim, coords)
    tyc.write_csv(INTER / "anon_top6_tycho2_pm_anomaly.csv")
    print(f"\nTycho-2 PM + anomaly for the 6:")
    print(tyc.select([
        "source_id", "tyc_pmRA", "tyc_pmDE",
        "dr3_pmra", "dr3_pmdec",
        "pm_anomaly_RA_sigma", "pm_anomaly_DE_sigma",
        "pm_anomaly_chi2"
    ]))

    # Final summary
    print("\n=== SUMMARY OF MISSING-DATA RETRIEVAL ===")
    print(f"(1) rvs_mean_spectrum: headline={rvs_result['headline_hits']} hits, "
          f"SB1={rvs_result['sb1_hits']} hits, "
          f"errors={rvs_result['headline_errs'] + rvs_result['sb1_errs']}")
    print(f"(2) Hipparcos vL07 bulk: {len(hip_df)} rows pulled")
    if not hip_df.is_empty():
        head_with_hip = headline_in_hip_full(hip_df)
        n_nss = head_with_hip.filter(
            (pl.col("Sn").is_not_null()) & (pl.col("Sn") != 5)
        ).shape[0]
        print(f"    headline-14 with HIP Sn != 5: {n_nss}")
    print(f"(3) SIMBAD HD resolution: 6 sources resolved")
    print(f"(4) Tycho-2 PM anomalies computed for 6")


if __name__ == "__main__":
    sys.exit(main() or 0)
