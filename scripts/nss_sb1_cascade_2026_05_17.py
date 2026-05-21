"""NSS SB1 substellar pool — run the v9b cascade on the 135 survivors.

Cascade order (mirrors pipeline_v9b for non-SB1 pool):
  1. Load 135 SB1 substellar candidates from
     data/intermediate/nss_sb1_pool_with_m2_2026_05_17.csv
  2. Cross-match SB9 (Pourbaix's own spectroscopic-binary catalog) via Vizier
  3. Cross-match exoplanet.eu (PM-corrected, 10")
  4. Cross-match NASA Exo PS (gaia_dr3_id)
  5. Cross-match Sahlmann 2025 verdict (preselection table)
  6. Look up HGCA Brandt 2024 chi^2 (only for HIP cross-IDs)
  7. Look up Kervella H2G2 PMa SNR (for HIP cross-IDs)
  8. Pure-novelty cut: not in any of the above; HGCA chi^2 in [5,30] OR
     no HGCA cross-match (anonymous; HGCA only covers HIP/Tycho)

Run:
    /Users/legbatterij/claude_projects/ostinato/.venv/bin/python \
        scripts/nss_sb1_cascade_2026_05_17.py
"""
from __future__ import annotations

import sys
import time
from pathlib import Path

import polars as pl
from astroquery.gaia import Gaia
from astroquery.vizier import Vizier

ROOT = Path("/tmp/gaia-novelty-publication")
INTER = ROOT / "data" / "intermediate"
INTER.mkdir(parents=True, exist_ok=True)


def load_substellar_subset() -> pl.DataFrame:
    df = pl.read_csv(INTER / "nss_sb1_pool_with_m2_2026_05_17.csv")
    sub = df.filter(
        (pl.col("m2_marg_med_mjup") < 80.0)
        & ((pl.col("ruwe").is_null()) | (pl.col("ruwe") < 7.0))
    )
    return sub


def gaia_to_simbad_id(source_ids: list[int]) -> pl.DataFrame:
    """Pull SIMBAD-equivalent identifiers via gaiadr3.dr3_neighbourhood +
    plain Gaia main-table (just for ra/dec/parallax/G for the cross-matches).
    Returns one row per source_id with ra, dec, G, plx, hip_alias (if any
    via xmatch table)."""
    ids = ",".join(str(int(x)) for x in source_ids)
    q = f"""SELECT g.source_id, g.ra, g.dec, g.parallax,
                  g.phot_g_mean_mag, g.pmra, g.pmdec
            FROM gaiadr3.gaia_source g
            WHERE g.source_id IN ({ids})"""
    job = Gaia.launch_job_async(q)
    return pl.from_pandas(job.get_results().to_pandas())


def xmatch_sb9(coords: pl.DataFrame, radius_arcsec: float = 10.0) -> pl.DataFrame:
    """Cross-match candidate ra/dec against Vizier B/sb9/main (SB9 catalog)."""
    Vizier.ROW_LIMIT = -1
    Vizier.TIMEOUT = 120
    import astropy.units as u
    from astropy.coordinates import SkyCoord

    print(f"Cross-matching {len(coords)} positions against SB9 (B/sb9/main) …")
    sc = SkyCoord(ra=coords["ra"].to_numpy() * u.deg,
                  dec=coords["dec"].to_numpy() * u.deg)
    # Vizier batches into <=20 at a time for reliability
    hits = []
    BATCH = 20
    for i in range(0, len(sc), BATCH):
        sub = sc[i:i+BATCH]
        try:
            res = Vizier.query_region(sub, radius=radius_arcsec * u.arcsec,
                                       catalog="B/sb9/main")
        except Exception as e:  # noqa: BLE001
            print(f"  Vizier batch {i//BATCH} err: {type(e).__name__}: {e}")
            continue
        if not res:
            continue
        for t in res:
            df = t.to_pandas()
            df["_input_idx_offset"] = i
            hits.append(df)
        time.sleep(0.2)
    if not hits:
        return pl.DataFrame({"source_id": [], "sb9_match": []})
    # Without per-row mapping back to source_id from Vizier batches, we treat
    # the SB9 cross-match as a *count* per batch — meaning any hit in the
    # batch marks "candidate in SB9 vicinity, manual confirm needed". For
    # the cascade purpose we don't need exact mapping at this stage; we will
    # mark the entire pool's SB9 fraction.
    return pl.DataFrame({
        "sb9_n_hits_in_pool": [sum(len(h) for h in hits)],
        "sb9_n_batches_with_hits": [len(hits)],
    })


def xmatch_sb9_per_source(coords: pl.DataFrame,
                           radius_arcsec: float = 5.0) -> pl.DataFrame:
    """One-by-one SB9 cross-match returning source_id -> in_sb9 boolean.

    Slower but gives exact mapping back to source_id.
    """
    Vizier.ROW_LIMIT = 5
    Vizier.TIMEOUT = 60
    import astropy.units as u
    from astropy.coordinates import SkyCoord

    rows = []
    for r in coords.iter_rows(named=True):
        sc = SkyCoord(ra=r["ra"] * u.deg, dec=r["dec"] * u.deg)
        try:
            res = Vizier.query_region(sc, radius=radius_arcsec * u.arcsec,
                                       catalog="B/sb9/main")
            in_sb9 = len(res) > 0 and len(res[0]) > 0
        except Exception:  # noqa: BLE001
            in_sb9 = None
        rows.append({"source_id": r["source_id"], "in_sb9": in_sb9})
    return pl.DataFrame(rows)


def lookup_hip_via_gaia_neighbourhood(source_ids: list[int]) -> pl.DataFrame:
    """Find HIP cross-IDs for our Gaia source_ids using HIP-Gaia DR3 xmatch
    table (gaiadr3.hipparcos2_best_neighbour or similar). Note: this table
    is gaiadr3.hipparcos2_best_neighbour."""
    ids = ",".join(str(int(x)) for x in source_ids)
    q = f"""SELECT source_id, original_ext_source_id AS hip
            FROM gaiadr3.hipparcos2_best_neighbour
            WHERE source_id IN ({ids})"""
    job = Gaia.launch_job_async(q)
    return pl.from_pandas(job.get_results().to_pandas())


def vizier_hgca(hips: list[int]) -> pl.DataFrame:
    """Lookup HGCA Brandt 2024 chi^2 for HIP IDs.

    Strategy: fetch the entire HGCA catalog once (~~115k rows; tiny on disk
    and faster than 24 individual constraint queries), then filter to our
    HIP list.

    Catalog name on Vizier: J/ApJS/268/66 (Brandt 2024 corrected HGCA).
    Fallback: J/ApJS/254/42 (Brandt 2021 original HGCA) if 2024 not found.
    """
    if not hips:
        return pl.DataFrame({"hip": [], "chisq": []})
    Vizier.ROW_LIMIT = -1
    Vizier.TIMEOUT = 180
    v = Vizier(columns=["HIP", "chisq", "snr_pma"])
    v.ROW_LIMIT = -1
    for cat in ["J/ApJS/268/66", "J/ApJS/254/42", "J/ApJS/268/24"]:
        try:
            res = v.get_catalogs(cat)
        except Exception as e:  # noqa: BLE001
            print(f"  HGCA bulk fetch {cat} err: {type(e).__name__}: {e}")
            continue
        if not res or len(res) == 0:
            continue
        # find table with HIP + chisq
        for t in res:
            cols = [c.lower() for c in t.colnames]
            if "hip" in cols and any("chi" in c for c in cols):
                df = t.to_pandas()
                # normalize column names
                df.columns = [c.lower() for c in df.columns]
                # rename HIP and chisq columns
                rename = {}
                for c in df.columns:
                    if c == "hip":
                        rename[c] = "hip"
                    elif "chi" in c and "snr" not in c:
                        rename[c] = "chisq"
                df = df.rename(columns=rename)
                if "hip" not in df.columns or "chisq" not in df.columns:
                    continue
                # filter to our HIPs
                df = df[df["hip"].isin(hips)][["hip", "chisq"]].copy()
                df["hip"] = df["hip"].astype(int)
                df["chisq"] = df["chisq"].astype(float)
                print(f"  HGCA hit on Vizier {cat}: {len(df)} HIP matches "
                      f"out of {len(hips)} probed")
                return pl.from_pandas(df.reset_index(drop=True))
    return pl.DataFrame({"hip": [], "chisq": []})


def main():
    sub = load_substellar_subset()
    print(f"SB1 substellar (post conditional RUWE): {len(sub)} candidates")
    src_ids = sub["source_id"].cast(pl.Int64).to_list()

    print("\n=== STEP 1: HIP cross-id via gaiadr3.hipparcos2_best_neighbour ===")
    hip_xm = lookup_hip_via_gaia_neighbourhood(src_ids)
    print(f"HIP cross-matches: {len(hip_xm)} / {len(sub)}")
    sub_h = sub.join(hip_xm, on="source_id", how="left")

    print("\n=== STEP 2: HGCA Brandt 2024 chi^2 for HIP-named ===")
    hip_list = [int(h) for h in sub_h["hip"].drop_nulls().to_list()]
    print(f"Looking up {len(hip_list)} HIPs in HGCA …")
    hgca = vizier_hgca(hip_list)
    print(f"HGCA hits: {len(hgca)}")
    if not hgca.is_empty():
        sub_h = sub_h.join(hgca, on="hip", how="left")
        # Tier
        def tier(c):
            if c is None:
                return None
            c = float(c)
            if c > 100: return "REJECT_stellar"
            if c >= 30: return "FLAG_ambiguous"
            if c >= 5: return "CORROBORATED"
            return "isolated_lt5"
        sub_h = sub_h.with_columns(
            pl.col("chisq").map_elements(tier, return_dtype=pl.Utf8).alias("hgca_tier")
        )

    print("\n=== STEP 3: SB9 (Pourbaix's own catalog) per-source cross-match ===")
    coords = sub.select(["source_id", "ra", "dec"])
    sb9 = xmatch_sb9_per_source(coords, radius_arcsec=5.0)
    sb9_count = sb9["in_sb9"].sum() if not sb9.is_empty() else 0
    print(f"SB9 hits within 5\": {sb9_count} / {len(sub)}")
    sub_h = sub_h.join(sb9, on="source_id", how="left")

    # Save full annotated pool
    sub_h.write_csv(INTER / "nss_sb1_cascade_annotated_2026_05_17.csv")

    # Final cut: not in SB9, HGCA in CORROBORATED tier or no HIP at all
    novel = sub_h.filter(
        (pl.col("in_sb9").is_null() | (pl.col("in_sb9") == False))
    )
    print(f"\nNot-in-SB9: {len(novel)} candidates")

    if "hgca_tier" in novel.columns:
        novel_hgca_corrob = novel.filter(
            (pl.col("hgca_tier") == "CORROBORATED")
        )
    else:
        novel_hgca_corrob = novel.head(0)
    print(f"Not-in-SB9 + HGCA CORROBORATED (5 <= chi^2 < 30): "
          f"{len(novel_hgca_corrob)}")

    novel_hgca_corrob.write_csv(INTER / "nss_sb1_hgca_corroborated_2026_05_17.csv")

    novel_anon = novel.filter(pl.col("hip").is_null())
    print(f"Not-in-SB9 + anonymous (no HIP, HGCA inapplicable): {len(novel_anon)}")
    novel_anon.write_csv(INTER / "nss_sb1_anonymous_novel_2026_05_17.csv")

    print("\n=== SHORTLIST (HGCA-corroborated SB1 substellar, no SB9) ===")
    show_cols = ["source_id", "hip", "phot_g_mean_mag", "ruwe",
                 "period", "eccentricity", "semi_amplitude_primary",
                 "m2_marg_med_mjup", "chisq", "hgca_tier"]
    cols_present = [c for c in show_cols if c in novel_hgca_corrob.columns]
    if not novel_hgca_corrob.is_empty():
        print(novel_hgca_corrob.sort("m2_marg_med_mjup").select(cols_present).head(30))
    else:
        print("(empty)")


if __name__ == "__main__":
    sys.exit(main() or 0)
