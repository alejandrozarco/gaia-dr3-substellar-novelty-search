"""Pipeline v8: Filter #28 coord-match bug-fix (2026-05-17).

Fixes a silent failure in v2's `filter_exoplanet_eu_coord` filter. The
v2 implementation was conditionally guarded:

    if "ra" in pool.columns and "dec" in pool.columns:
        pool = filter_exoplanet_eu_coord(pool, radius_arcsec=5.0)
    else:
        pool = pool.with_columns(pl.lit(False).alias("exoeu_match"))

The production v2 candidate pool never propagated ra/dec from the
underlying Gaia DR3 tables, so the else-branch always fired and the
coord-match was a no-op for every source. As a result, the v2 → v7
cascade missed six exoplanet.eu-published companions that should have
been rejected at Filter #28:

  +--------------+----------+----------------+----------------+-------------+
  | Name         | HIP      | exo_mass_MJ    | exo_period_d   | raw sep ″   |
  +--------------+----------+----------------+----------------+-------------+
  | HD 33636     | 24205    | 15.4           | 2828.0         | 9.73        |
  | BD+05 5218   | 117179   | 44.20          | 247.98         | 0.42        |
  | HD 68638     | 40497    | 35.10          | 240.70         | 6.18        |
  | HD 30246     | 22203    | 42.18          | 990.08         | 1.45        |
  | L 194-115    | 60321    | 68.26          | 530.17         | 3.89        |
  | G 239-52     | 75202    | 69.00          | 591.46         | 3.29        |
  +--------------+----------+----------------+----------------+-------------+

After PM-correcting Gaia DR3 (epoch J2016.0) coords back to J2000.0,
all six fall within ~7″ of their exoplanet.eu coords. A 10″ radius
catches all six robustly and stays well below the typical proper-
motion-induced offset for the next-most-extreme cases (HD 33636's
pm = 178 mas/yr in RA gives 2.85″ of drift over 16 yr).

v8 contributions:

  Filter #28 v2 — `filter_exoplanet_eu_coord_pm_corrected`
    * Auto-fetches ra, dec, pmra, pmdec from Gaia DR3 gaia_source
      when missing from the input pool.
    * PM-projects Gaia DR3 J2016.0 coords back to J2000.0 epoch for
      the exoplanet.eu cross-match (catalog rows are at J2000).
    * Default radius: 10 arcsec (broadened from v2's 5 arcsec).
    * Matches on min(sep_pm_corrected, sep_uncorrected) so catalog
      entries with their own epoch ambiguity are still caught.

This file's `reclassify_pool_to_v8` operates on the v7 pool:
it re-runs the corrected Filter #28 on v7 verdicts and demotes any
previously CORROBORATED / FLAG / SURVIVOR verdict to
`REJECTED_published_exoplanet_eu` when the coord-match now hits.
"""
from __future__ import annotations

import io
import math
import time
import urllib.parse
import urllib.request
from pathlib import Path

import polars as pl

GAIA_TAP = "https://gea.esac.esa.int/tap-server/tap/sync"

# Filter #28 v2 parameters
V8_COORD_MATCH_RADIUS_ARCSEC = 10.0
V8_GAIA_EPOCH = 2016.0
V8_EXOEU_EPOCH = 2000.0


def ang_sep_arcsec(ra1: float, dec1: float, ra2: float, dec2: float) -> float:
    """Approximate angular separation (good for sub-arcmin scales)."""
    dra = (ra1 - ra2) * math.cos(math.radians((dec1 + dec2) / 2))
    return math.sqrt(dra * dra + (dec1 - dec2) ** 2) * 3600


def project_to_epoch(
    ra: float, dec: float, pmra_masyr: float, pmdec_masyr: float, dt_yr: float
) -> tuple[float, float]:
    """Linear PM projection (good enough for ~16 yr at the scales we care about)."""
    cosd = math.cos(math.radians(dec))
    ra_out = ra + (pmra_masyr * dt_yr / 3_600_000.0) / max(cosd, 1e-6)
    dec_out = dec + (pmdec_masyr * dt_yr / 3_600_000.0)
    return ra_out, dec_out


def fetch_gaia_coords(source_ids: list[int], batch_size: int = 200) -> pl.DataFrame:
    """Bulk-fetch ra, dec, pmra, pmdec from Gaia DR3 for a list of source_ids."""
    out = []
    for i in range(0, len(source_ids), batch_size):
        batch = source_ids[i : i + batch_size]
        sid_list = ",".join(str(s) for s in batch)
        q = (
            "SELECT source_id, ra, dec, pmra, pmdec "
            "FROM gaiadr3.gaia_source "
            f"WHERE source_id IN ({sid_list})"
        )
        url = (
            GAIA_TAP
            + "?REQUEST=doQuery&LANG=ADQL&FORMAT=csv&QUERY="
            + urllib.parse.quote(q)
        )
        with urllib.request.urlopen(url, timeout=180) as resp:
            data = resp.read().decode(errors="ignore")
        df = pl.read_csv(
            io.StringIO(data),
            schema_overrides={"source_id": pl.Int64},
            infer_schema_length=2000,
            ignore_errors=True,
        )
        out.append(df)
        time.sleep(0.5)  # be polite to ESA
    return pl.concat(out, how="vertical_relaxed").unique(
        subset=["source_id"], keep="first"
    )


def filter_exoplanet_eu_coord_pm_corrected(
    pool: pl.DataFrame,
    exoeu_csv: str,
    radius_arcsec: float = V8_COORD_MATCH_RADIUS_ARCSEC,
    auto_fetch_coords: bool = True,
) -> pl.DataFrame:
    """v8 Filter #28: PM-corrected coord cross-match against exoplanet.eu.

    Adds boolean ``exoeu_match_v8`` column and also ``exoeu_match_name`` /
    ``exoeu_match_sep_arcsec`` debug columns.
    """
    pool = pool.with_columns(pl.col("source_id").cast(pl.Int64))

    # Auto-fetch coords if missing
    missing_coords = (
        ("ra" not in pool.columns)
        or ("dec" not in pool.columns)
        or ("pmra" not in pool.columns)
        or ("pmdec" not in pool.columns)
    )
    if missing_coords and auto_fetch_coords:
        ids = pool["source_id"].to_list()
        coords = fetch_gaia_coords(ids)
        pool = pool.join(coords, on="source_id", how="left")

    # Load exoplanet.eu rows with valid coords
    exo = pl.read_csv(exoeu_csv, infer_schema_length=20_000, ignore_errors=True)
    exo = exo.filter(pl.col("ra").is_not_null() & pl.col("dec").is_not_null())
    exo_rows = exo.select(["name", "star_name", "ra", "dec"]).to_dicts()

    dt = V8_EXOEU_EPOCH - V8_GAIA_EPOCH  # -16 yr (project Gaia back to J2000)

    matches_sid: set[int] = set()
    match_meta: dict[int, dict] = {}

    for r in pool.iter_rows(named=True):
        ra = r.get("ra")
        dec = r.get("dec")
        if ra is None or dec is None:
            continue
        pmra = r.get("pmra") or 0.0
        pmdec = r.get("pmdec") or 0.0
        ra_j2000, dec_j2000 = project_to_epoch(ra, dec, pmra, pmdec, dt)

        best = None
        for e in exo_rows:
            s_pm = ang_sep_arcsec(ra_j2000, dec_j2000, e["ra"], e["dec"])
            s_raw = ang_sep_arcsec(ra, dec, e["ra"], e["dec"])
            s = min(s_pm, s_raw)
            if s < radius_arcsec:
                if best is None or s < best["sep"]:
                    best = {
                        "name": e["name"],
                        "star_name": e["star_name"],
                        "sep": s,
                        "sep_pm": s_pm,
                        "sep_raw": s_raw,
                    }
        if best is not None:
            matches_sid.add(int(r["source_id"]))
            match_meta[int(r["source_id"])] = best

    pool = pool.with_columns(
        pl.col("source_id").is_in(list(matches_sid)).alias("exoeu_match_v8"),
        pl.col("source_id")
        .map_elements(
            lambda s: match_meta.get(int(s), {}).get("name"),
            return_dtype=pl.Utf8,
        )
        .alias("exoeu_match_name"),
        pl.col("source_id")
        .map_elements(
            lambda s: match_meta.get(int(s), {}).get("sep"),
            return_dtype=pl.Float64,
        )
        .alias("exoeu_match_sep_arcsec"),
    )
    return pool


def reclassify_pool_to_v8(
    v7_pool: pl.DataFrame,
    exoeu_csv: str,
    radius_arcsec: float = V8_COORD_MATCH_RADIUS_ARCSEC,
) -> pl.DataFrame:
    """Apply v8 Filter #28 to v7 verdicts.

    Only modifies verdicts that did not already trigger the existing
    REJECTED_published_nasa_exo or REJECTED_documented_fp filters.
    """
    pool = filter_exoplanet_eu_coord_pm_corrected(
        v7_pool, exoeu_csv=exoeu_csv, radius_arcsec=radius_arcsec
    )

    def reclass(r: dict) -> str:
        v7v = r.get("v7_verdict")
        # Preserve documented_fp and nasa_exo hits
        if v7v in {"REJECTED_documented_fp", "REJECTED_published_nasa_exo"}:
            return v7v
        if r.get("exoeu_match_v8"):
            return "REJECTED_published_exoplanet_eu_pm_corr"
        return v7v

    pool = pool.with_columns(
        pl.struct(pool.columns)
        .map_elements(reclass, return_dtype=pl.Utf8)
        .alias("v8_verdict")
    )
    return pool


if __name__ == "__main__":
    import argparse

    p = argparse.ArgumentParser()
    p.add_argument("--v7-pool", required=True)
    p.add_argument("--exoeu-csv", required=True)
    p.add_argument("--out", required=True)
    p.add_argument("--radius-arcsec", type=float, default=V8_COORD_MATCH_RADIUS_ARCSEC)
    args = p.parse_args()

    v7 = pl.read_csv(args.v7_pool).unique(subset=["source_id"], keep="first")
    v8 = reclassify_pool_to_v8(v7, exoeu_csv=args.exoeu_csv, radius_arcsec=args.radius_arcsec)
    v8 = v8.unique(subset=["source_id"], keep="first")
    v8.write_csv(args.out)

    n_changed = v8.filter(pl.col("v7_verdict") != pl.col("v8_verdict")).height
    print(f"Wrote {args.out} ({v8.height} rows; {n_changed} reclassified vs v7)")
    print("\nv7 → v8 transitions:")
    print(
        v8.filter(pl.col("v7_verdict") != pl.col("v8_verdict"))
        .group_by(["v7_verdict", "v8_verdict"])
        .agg(pl.len().alias("n"))
        .sort("n", descending=True)
    )
    print("\nNewly rejected exoplanet.eu publications:")
    print(
        v8.filter(pl.col("v8_verdict") == "REJECTED_published_exoplanet_eu_pm_corr")
        .select(
            ["source_id", "Name", "HIP", "v7_verdict",
             "exoeu_match_name", "exoeu_match_sep_arcsec"]
        )
    )
