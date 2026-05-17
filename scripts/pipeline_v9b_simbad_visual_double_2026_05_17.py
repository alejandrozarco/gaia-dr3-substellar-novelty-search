"""Pipeline v9b: SIMBAD object_type visual-binary check (2026-05-17).

Fix B (companion to v9): catches visually-resolved binaries.

The v9 cascade promoted HD 222805 to CORROBORATED_kervella_only via
Fix D (Kervella-substitute-for-HGCA on short-period orbits). But
HD 222805 is a known SIMBAD ``**`` (visual double) with WDS entry
``WDS J23444-7029AB`` — the 216 d Gaia NSS Orbital may be detecting
the inner stellar companion within this hierarchical system rather
than a substellar tertiary.

v9b approach: query SIMBAD for each v9 candidate-tier source (~34
sources at CORROBORATED + FLAG verdicts), parse:

  * ``obj_type``: SIMBAD object classification. ``**`` = visually
    resolved double (DEMOTE).
  * WDS identifier: ``WDS J####+/-####`` regex pattern in
    Identifiers section. Annotate but do NOT reject (the WDS pair
    may be wide enough that the NSS orbit is independent).
  * Visual-double discoverer designation: ``** WSI``, ``** HDS``,
    ``** HJ``, etc. Annotate.

Demotion rule:
  * v9 verdict = CORROBORATED_* AND SIMBAD obj_type = ``**``
    → v9b verdict = REJECTED_simbad_visual_double

Annotation:
  * Adds ``simbad_otype``, ``wds_id``, ``visual_double_id`` columns.

Caching: this script caches SIMBAD lookups to
``data/intermediate/simbad_otype_cache.csv`` to avoid redundant TAP
queries on subsequent runs.

A future v9c would extend this to a proper WDS catalog cross-match
with separation thresholds (sep < 1" = REJECT, 1-10" = FLAG, > 10"
= ANNOTATE), pulled from Vizier B/wds/wds.
"""
from __future__ import annotations

import re
import time
import urllib.parse
import urllib.request
from pathlib import Path

import polars as pl

SIMBAD_BASE = "https://simbad.cds.unistra.fr/simbad/sim-id"
WDS_RE = re.compile(r"WDS J\d{4,5}[+-]\d{4,5}", re.MULTILINE)
MSC_RE = re.compile(r"\bMSC J\d{4}[+-]\d{4}", re.MULTILINE)
VIS_DOUBLE_RE = re.compile(
    r"\*\* (?:WSI|IZA|JNN|SHJ|STF|STT|HJ|HU|BU|HEI|COU|MCA|TOK|HDS|FIN|RST|"
    r"JC|KUI|VBS|VYS|DON|ARG|MCY|H)\s+\S+",
    re.MULTILINE,
)
OTYPE_RE = re.compile(r"^Object[^\n]*?---\s*(\S+)\s*---", re.MULTILINE)


def query_simbad(source_id: int, timeout: int = 20) -> dict:
    """Pull SIMBAD ASCII page for a Gaia DR3 source_id."""
    url = f"{SIMBAD_BASE}?Ident=Gaia+DR3+{source_id}&output.format=ASCII"
    try:
        with urllib.request.urlopen(url, timeout=timeout) as r:
            text = r.read().decode(errors="ignore")
    except Exception as e:
        return {"source_id": source_id, "otype": None, "error": str(e)}

    if "Identifiers" not in text:
        return {"source_id": source_id, "otype": None, "error": "not found"}

    otype_m = OTYPE_RE.search(text)
    otype = otype_m.group(1) if otype_m else None

    ids_section = text.split("Identifiers")[1]
    ids_section = ids_section.split("Bibcodes")[0] if "Bibcodes" in ids_section else ids_section

    wds = WDS_RE.findall(ids_section)
    msc = MSC_RE.findall(ids_section)
    vis = VIS_DOUBLE_RE.findall(ids_section)

    return {
        "source_id": source_id,
        "otype": otype,
        "wds_id": wds[0] if wds else None,
        "msc_id": msc[0] if msc else None,
        "visual_double_id": vis[0] if vis else None,
        "error": None,
    }


def annotate_simbad_visual_doubles(
    v9_pool: pl.DataFrame,
    cache_path: str = "/tmp/gaia-novelty-publication/data/intermediate/simbad_otype_cache.csv",
    rate_limit_sec: float = 0.3,
) -> pl.DataFrame:
    """Query SIMBAD for v9 candidate-tier sources; add visual-double columns."""
    candidates = v9_pool.filter(
        pl.col("v9_verdict").is_in([
            "CORROBORATED_real_companion",
            "CORROBORATED_kervella_only",
            "FLAG_hgca_mass_ambiguous",
        ])
    )
    target_sids = candidates["source_id"].to_list()

    # Load cache
    cache_file = Path(cache_path)
    if cache_file.exists():
        cache = pl.read_csv(cache_file, schema_overrides={"source_id": pl.Int64})
        cached_sids = set(cache["source_id"].to_list())
    else:
        cache = pl.DataFrame(
            schema={
                "source_id": pl.Int64,
                "otype": pl.Utf8,
                "wds_id": pl.Utf8,
                "msc_id": pl.Utf8,
                "visual_double_id": pl.Utf8,
                "error": pl.Utf8,
            }
        )
        cached_sids = set()
        cache_file.parent.mkdir(parents=True, exist_ok=True)

    missing = [s for s in target_sids if s not in cached_sids]
    print(f"v9 candidate-tier sources: {len(target_sids)}; cached: {len(target_sids)-len(missing)}; to fetch: {len(missing)}")

    new_rows = []
    for i, sid in enumerate(missing):
        res = query_simbad(sid)
        new_rows.append(res)
        if (i + 1) % 10 == 0:
            print(f"  fetched {i+1}/{len(missing)}")
        time.sleep(rate_limit_sec)

    if new_rows:
        new_df = pl.DataFrame(new_rows)
        cache = pl.concat([cache, new_df], how="diagonal_relaxed").unique(
            subset=["source_id"], keep="last"
        )
        cache.write_csv(cache_file)

    # Join cache columns into the v9 pool
    out = v9_pool.with_columns(pl.col("source_id").cast(pl.Int64))
    out = out.join(
        cache.select(["source_id", "otype", "wds_id", "msc_id", "visual_double_id"]),
        on="source_id",
        how="left",
    )
    out = out.rename({"otype": "simbad_otype"})
    return out


def reclass_to_v9b(r: dict) -> str:
    """Demote CORROBORATED to REJECTED_simbad_visual_double when obj_type='**'."""
    v9v = r.get("v9_verdict") or ""
    otype = r.get("simbad_otype")
    if otype == "**" and v9v.startswith("CORROBORATED"):
        return "REJECTED_simbad_visual_double"
    return v9v


def reclassify_pool_to_v9b(v9_pool: pl.DataFrame) -> pl.DataFrame:
    """Annotate + reclassify v9 pool with SIMBAD visual-double rejection."""
    annotated = annotate_simbad_visual_doubles(v9_pool)
    out = annotated.with_columns(
        pl.struct(annotated.columns)
        .map_elements(reclass_to_v9b, return_dtype=pl.Utf8)
        .alias("v9b_verdict")
    )
    return out


if __name__ == "__main__":
    import argparse

    p = argparse.ArgumentParser()
    p.add_argument("--v9-pool", required=True)
    p.add_argument("--out", required=True)
    args = p.parse_args()

    v9 = pl.read_csv(args.v9_pool, schema_overrides={"source_id": pl.Int64}).unique(
        subset=["source_id"], keep="first"
    )
    v9b = reclassify_pool_to_v9b(v9)
    v9b = v9b.unique(subset=["source_id"], keep="first")
    v9b.write_csv(args.out)

    n_changed = v9b.filter(pl.col("v9_verdict") != pl.col("v9b_verdict")).height
    print(f"\nWrote {args.out} ({v9b.height} rows; {n_changed} reclassified vs v9)")

    print("\nv9 → v9b transitions:")
    print(
        v9b.filter(pl.col("v9_verdict") != pl.col("v9b_verdict"))
        .group_by(["v9_verdict", "v9b_verdict"])
        .agg(pl.len().alias("n"))
        .sort("n", descending=True)
    )

    print("\nNewly REJECTED_simbad_visual_double:")
    print(
        v9b.filter(pl.col("v9b_verdict") == "REJECTED_simbad_visual_double")
        .select(["source_id", "Name", "HIP", "simbad_otype", "wds_id", "visual_double_id"])
    )

    print("\nv9 candidate-tier sources with WDS membership (annotated but not rejected):")
    print(
        v9b.filter(
            pl.col("v9_verdict").is_in([
                "CORROBORATED_real_companion",
                "CORROBORATED_kervella_only",
                "FLAG_hgca_mass_ambiguous",
            ])
            & (pl.col("wds_id").is_not_null() | pl.col("visual_double_id").is_not_null())
        )
        .select(["source_id", "Name", "HIP", "v9_verdict", "v9b_verdict",
                 "simbad_otype", "wds_id", "visual_double_id"])
    )
