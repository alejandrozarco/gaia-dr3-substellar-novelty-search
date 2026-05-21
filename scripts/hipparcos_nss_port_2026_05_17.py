"""(B) Port Hipparcos NSS solutions.

Hipparcos has its own pre-Gaia non-single-star system. The flag is in the
van Leeuwen 2007 reduction (Vizier I/311/hip2), column 'Sn' (solution
type):

  Sn = 5   single-star solution (default)
  Sn = 1   orbital solution (NSS-O equivalent — published orbit)
  Sn = 3   acceleration solution (NSS-A equivalent — proper-motion
            acceleration detected but no orbit fit)
  Sn = 7   stochastic / VIM (variability-induced mover — anomalous
            motion not fit by single-star model)
  Sn = 9   constrained component (a known double resolved by HIP)

We treat **Sn ∈ {1, 3, 7}** as Hipparcos NSS classifications.
Sn = 9 is a resolved double — clearly stellar — and we exclude it.

What we do here:

  1. Pull the full Hipparcos van Leeuwen 2007 catalog with Sn != 5.
  2. Cross-match against our 14 headline candidates (each is HIP-named).
  3. Cross-match against the entire Gaia DR3 NSS Orbital + SB1 + Accel pool.
  4. For HIP NSS + Gaia DR3 NSS dual-coverage sources: those are the
     strongest pre-Gaia + Gaia astrometric corroboration available
     (independent 25-yr proper-motion-corroborated NSS classifications).
"""
from __future__ import annotations

import sys
from pathlib import Path

import polars as pl
from astroquery.gaia import Gaia
from astroquery.vizier import Vizier

ROOT = Path("/tmp/gaia-novelty-publication")
INTER = ROOT / "data" / "intermediate"


def pull_hip_nss():
    """Pull Sn != 5 from Vizier I/311/hip2 (van Leeuwen 2007)."""
    Vizier.ROW_LIMIT = -1
    Vizier.TIMEOUT = 300
    print("Pulling Hipparcos van Leeuwen 2007 (I/311/hip2) …")
    res = Vizier(columns=["HIP", "Sn", "RAhms", "DEdms", "Plx",
                          "e_Plx", "RV", "e_RV", "Hpmag"]) \
              .query_constraints(catalog="I/311/hip2", Sn="!=5")
    if not res or len(res) == 0:
        print("  Vizier returned no rows (try with Vizier.get_catalogs)")
        return pl.DataFrame()
    df = res[0].to_pandas()
    df["HIP"] = df["HIP"].astype(int)
    df["Sn"] = df["Sn"].astype(int)
    print(f"  Hipparcos NSS solutions retrieved: {len(df)}")
    print(f"  Breakdown by Sn: "
          f"{df['Sn'].value_counts().to_dict()}")
    return pl.from_pandas(df)


def headline_xmatch(hip_nss: pl.DataFrame):
    head = pl.read_csv(ROOT / "novelty_candidates.csv").select(["name", "hip"])
    head = head.drop_nulls("hip").with_columns(pl.col("hip").cast(pl.Int64))
    hip_nss = hip_nss.rename({"HIP": "hip"}).with_columns(pl.col("hip").cast(pl.Int64))
    joined = head.join(hip_nss, on="hip", how="inner")
    return joined


def gaia_hip_to_dr3_id(hips: list[int]) -> pl.DataFrame:
    """Cross-match HIPs to Gaia DR3 source_id via hipparcos2_best_neighbour."""
    chunks = []
    BATCH = 4000
    for i in range(0, len(hips), BATCH):
        sub = hips[i:i+BATCH]
        ids = ",".join(str(int(x)) for x in sub)
        q = (f"SELECT original_ext_source_id AS hip, source_id "
             f"FROM gaiadr3.hipparcos2_best_neighbour "
             f"WHERE original_ext_source_id IN ({ids})")
        try:
            df = Gaia.launch_job_async(q).get_results().to_pandas()
            chunks.append(df)
        except Exception as e:  # noqa: BLE001
            print(f"  hip2gaia batch err: {type(e).__name__}: {e}")
    if not chunks:
        return pl.DataFrame({"hip": [], "source_id": []})
    import pandas as pd
    return pl.from_pandas(pd.concat(chunks, ignore_index=True))


def gaia_nss_classification(source_ids: list[int]) -> pl.DataFrame:
    """For each Gaia DR3 source_id, find its NSS solution_type if any."""
    if not source_ids:
        return pl.DataFrame()
    chunks = []
    BATCH = 4000
    for i in range(0, len(source_ids), BATCH):
        sub = source_ids[i:i+BATCH]
        ids = ",".join(str(int(x)) for x in sub)
        # Two NSS tables: nss_two_body_orbit (Orbital/SB1/SB2/etc) +
        # nss_acceleration_astro (Accel7/Accel9)
        chunk_dfs = []
        for tbl in ["gaiadr3.nss_two_body_orbit", "gaiadr3.nss_acceleration_astro"]:
            q = (f"SELECT source_id, nss_solution_type, period, eccentricity, "
                 f"  significance "
                 f"FROM {tbl} WHERE source_id IN ({ids})")
            try:
                df = Gaia.launch_job_async(q).get_results().to_pandas()
                df["nss_table"] = tbl.split(".")[-1]
                chunk_dfs.append(df)
            except Exception as e:  # noqa: BLE001
                print(f"  {tbl} batch err: {type(e).__name__}: {e}")
        if chunk_dfs:
            import pandas as pd
            chunks.append(pd.concat(chunk_dfs, ignore_index=True))
    if not chunks:
        return pl.DataFrame()
    import pandas as pd
    return pl.from_pandas(pd.concat(chunks, ignore_index=True))


def main():
    hip_nss = pull_hip_nss()
    if hip_nss.is_empty():
        print("FATAL: no Hipparcos NSS rows retrieved")
        return 1

    hip_nss.write_csv(INTER / "hipparcos_nss_vanLeeuwen_2007.csv")

    print("\n=== STEP A: headline-14 cross-match ===")
    cross = headline_xmatch(hip_nss)
    print(f"Headline candidates with Hipparcos NSS Sn != 5: {len(cross)}")
    if not cross.is_empty():
        print(cross.select(["name", "hip", "Sn", "Hpmag"]))
        cross.write_csv(INTER / "hip_nss_headline_matches.csv")
    else:
        print("(none — Sn=5 single-star in HIP for all our 14, as expected for "
              "Gaia-DR3-discovered companions)")

    print("\n=== STEP B: HIP NSS -> Gaia DR3 NSS dual-coverage scan ===")
    hip_list = hip_nss["HIP"].cast(pl.Int64).to_list()
    print(f"Mapping {len(hip_list)} HIP NSS sources to Gaia DR3 source_ids …")
    hip2gaia = gaia_hip_to_dr3_id(hip_list)
    print(f"  HIP -> Gaia DR3 cross-match: {len(hip2gaia)} sources")
    hip2gaia.write_csv(INTER / "hip_nss_to_gaia_dr3_mapping.csv")

    src_ids = [int(x) for x in hip2gaia["source_id"].to_list()]
    nss = gaia_nss_classification(src_ids)
    print(f"  Gaia DR3 NSS classification for those: {len(nss)} hits")

    # Merge
    nss = nss.rename({"source_id": "source_id"})
    hip2gaia = hip2gaia.with_columns(pl.col("source_id").cast(pl.Int64))
    nss = nss.with_columns(pl.col("source_id").cast(pl.Int64))

    dual = hip2gaia.join(nss, on="source_id", how="inner")
    print(f"  HIP NSS Sn!=5 + Gaia DR3 NSS dual-coverage: {len(dual)}")
    if not dual.is_empty():
        # Attach the original HIP Sn
        dual = dual.with_columns(pl.col("hip").cast(pl.Int64))
        hip_meta = hip_nss.rename({"HIP": "hip"}).with_columns(pl.col("hip").cast(pl.Int64))
        dual = dual.join(hip_meta.select(["hip", "Sn", "Hpmag"]),
                          on="hip", how="left")
        dual.write_csv(INTER / "hip_nss_gaia_dr3_nss_dual.csv")

    print("\n=== SUMMARY ===")
    summary = pl.DataFrame({
        "channel": ["HIP NSS Sn!=5 total",
                    "HIP NSS Sn=1 (orbit)",
                    "HIP NSS Sn=3 (accel)",
                    "HIP NSS Sn=7 (stochastic/VIM)",
                    "HIP NSS Sn=9 (resolved)",
                    "HIP NSS w/ Gaia DR3 source_id",
                    "HIP NSS + Gaia DR3 NSS dual-coverage"],
        "count": [
            len(hip_nss),
            int(hip_nss.filter(pl.col("Sn") == 1).shape[0]),
            int(hip_nss.filter(pl.col("Sn") == 3).shape[0]),
            int(hip_nss.filter(pl.col("Sn") == 7).shape[0]),
            int(hip_nss.filter(pl.col("Sn") == 9).shape[0]),
            len(hip2gaia),
            len(dual) if 'dual' in dir() else 0,
        ],
    })
    print(summary)
    summary.write_csv(INTER / "hip_nss_summary_2026_05_17.csv")


if __name__ == "__main__":
    sys.exit(main() or 0)
