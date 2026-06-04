#!/usr/bin/env python3
"""Ingest the published Gaia DR3 binary_masses AMRFClassIII compact-companion
candidates (Halbwachs+ 2023) into the known-object front-filter.

Closes the novelty blind-spot found by the 2026-06-03 re-vet: the front-filter
held only CV / eRASS1 / symbiotic catalogs, so "absent from the front-filter"
never established novelty for a compact (NS/BH/WD) candidate. AMRFClassIII is
the Shahaf compact-companion class — a candidate that matches one is NOT novel
and carries a published independent M2.

binary_masses provides Source (Gaia DR3 id) + masses + Flag, but no ra/dec, so
ra/dec are joined from the local derived NSS parquets (source_id-keyed). The
front-filter's exact source_id match is the operative test for these; the
coordinates also enable positional matching. AMRFClassIII objects outside our
derived pool can't be coordinate-resolved offline (no full NSS table cached) —
they are reported but not ingested (they are outside our hunt pool anyway).

Offline; stdlib + pandas (ostinato venv). Re-runnable (store.append dedupes).
Run:  /Users/legbatterij/claude_projects/ostinato/.venv/bin/python \
        scripts/known_objects/ingest_binary_masses.py
"""
import glob
import os
import sys
from pathlib import Path

import pandas as pd

BASE = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(BASE / "scripts" / "known_objects"))
from store import KnownObjectStore  # noqa: E402

CSV = BASE / "data" / "external_catalogs" / "gaia_dr3_binary_masses_full.csv"
CATALOG = "halbwachs2023_binary_masses_amrf3"
PULLED = "2026-06-03"


def main():
    bm = pd.read_csv(CSV, usecols=["Source", "M2", "FluxRatio", "Flag"])
    a3 = bm[bm["Flag"] == "AMRFClassIII"].copy()
    a3["Source"] = a3["Source"].astype("int64")
    print(f"AMRFClassIII in binary_masses: {len(a3)}")

    # source_id -> (ra,dec) from the union of local derived parquets
    radec = {}
    import pyarrow.parquet as pq
    for p in sorted(glob.glob(str(BASE / "data" / "derived" / "*.parquet"))):
        cols = [f.name for f in pq.ParquetFile(p).schema_arrow]
        if not ({"source_id", "ra", "dec"} <= set(cols)):
            continue
        d = pd.read_parquet(p, columns=["source_id", "ra", "dec"]).dropna(subset=["ra", "dec"])
        for sid, ra, dec in zip(d["source_id"].astype("int64"), d["ra"], d["dec"]):
            radec.setdefault(int(sid), (float(ra), float(dec)))
    print(f"source_id->ra/dec map (union of derived parquets): {len(radec)}")

    a3["ra"] = a3["Source"].map(lambda s: radec.get(int(s), (None, None))[0])
    a3["dec"] = a3["Source"].map(lambda s: radec.get(int(s), (None, None))[1])
    resolved = a3.dropna(subset=["ra", "dec"]).copy()
    print(f"AMRFClassIII resolved to ra/dec locally: {len(resolved)} / {len(a3)}")
    print(f"  unresolved {len(a3) - len(resolved)} are outside our derived pool "
          f"(reported, not ingested)")

    rows = pd.DataFrame({
        "source_id": resolved["Source"].astype(str),
        "ra": resolved["ra"].astype(float),
        "dec": resolved["dec"].astype(float),
        "name": resolved["Source"].map(lambda s: f"Gaia DR3 {s}"),
        "otype": "AMRFClassIII (compact-companion candidate)",
        "catalog": CATALOG,
        "pulled_utc": PULLED,
    })

    store = KnownObjectStore()
    before = len(store.df)
    added = store.append(rows)
    store.save()
    print(f"store: {before} -> {len(store.df)} (+{added})")

    # spot-check our journaled / known compact objects against the full AMRFClassIII set
    checks = {
        "3378588057203660160": "HD 264291 (RV-confirmed heavy NS, Shahaf)",
        "5858574810404752256": "5858574 (triple-favored, on boundary)",
        "2909342818326298112": "WDJ060042",
        "332248057157474176": "WDJ020915",
        "6092654861665006592": "WG 26",
        "5612039087715504640": "UCAC4 313",
        "6021285355771958528": "TYC 7350-249-1 (orphan SB1 BH-cand)",
    }
    a3ids = set(a3["Source"].astype(str))
    print("--- spot-check: is it AMRFClassIII (i.e. a known compact candidate)? ---")
    for sid, lbl in checks.items():
        print(f"  {sid} {lbl}: AMRFClassIII={'YES' if sid in a3ids else 'no'}")


if __name__ == "__main__":
    main()
