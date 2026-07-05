#!/usr/bin/env python3
"""Ingest the bulk-downloaded full VSX table into the known_objects store,
closing the Phase-1-documented VSX gap (store had 0 VSX rows) for ALL future
hunts, not just this one.

Deliberately tagged `catalog="vsx_full"` -- DISTINCT from the registry's
existing `vsx_cataclysmic` CatalogSpec key (scripts/known_objects/
reference_catalogs.py), which is a cataclysmic/eruptive-only VizieR column-
filtered subset intended for CV-focused lanes. This ingest is the FULL table
(all VSX variable-star types: eclipsing binaries, RR Lyrae, rotational
variables, etc.) because that's what closes the gap for a general
RV-variability hunt like this one -- a future CV-only build.py run using
`vsx_cataclysmic` remains valid and complementary, not superseded.

Uses KnownObjectStore.append() (the store's own documented dedup-on-append
mechanism: same catalog + ~0.5" position + source_id) then .save(), i.e. the
exact "feeding it back" recipe documented in scripts/known_objects/README.md.

This is a data-store rebuild (parquet cache under data/external_catalogs/),
explicitly permitted by the task brief as an exception to the
docs/ no-edit rule (it is not a docs/ edit).
"""
from __future__ import annotations

import argparse
import sys
import time

import pandas as pd

sys.path.insert(0, "/Users/legbatterij/claude_projects/gaia-recovered-2026-05-27/scripts/known_objects")
from store import KnownObjectStore  # noqa: E402

NOW = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--vsx", default="/tmp/desi_p2a/checkpoints/vsx_raw.parquet")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    vsx = pd.read_parquet(args.vsx)
    print(f"Bulk VSX table: {len(vsx)} rows")

    # Build store-schema rows: source_id (from "Gaia DR3 <id>" Name strings,
    # where present -- VSX increasingly names Gaia-sourced entries this way),
    # ra/dec (RAJ2000/DEJ2000), name, otype (Type), catalog, pulled_utc.
    rows = pd.DataFrame({
        "ra": pd.to_numeric(vsx["RAJ2000"], errors="coerce"),
        "dec": pd.to_numeric(vsx["DEJ2000"], errors="coerce"),
        "name": vsx["Name"].astype(str),
        "otype": vsx["Type"].astype(str) if "Type" in vsx.columns else "",
    })
    # extract Gaia DR3 source_id when the VSX Name is literally "Gaia DR3 <id>"
    is_gaia_name = rows["name"].str.match(r"^Gaia DR3 \d+$", na=False)
    rows["source_id"] = pd.NA
    rows.loc[is_gaia_name, "source_id"] = rows.loc[is_gaia_name, "name"].str.replace(
        "Gaia DR3 ", "", regex=False)
    print(f"Rows with a Gaia DR3 source_id extractable from Name: {int(is_gaia_name.sum())} / {len(rows)}")

    rows = rows.dropna(subset=["ra", "dec"]).reset_index(drop=True)
    rows["catalog"] = "vsx_full"
    rows["pulled_utc"] = NOW

    store = KnownObjectStore()
    print(f"\nStore before ingest: {len(store.df)} rows")
    print(store.summary().to_string())

    if args.dry_run:
        print(f"\n[DRY RUN] would append {len(rows)} vsx_full rows -- not written")
        return

    n_added = store.append(rows, catalog="vsx_full", pulled_utc=NOW)
    p = store.save()
    print(f"\n+{n_added} rows added (post-dedup) -> saved {len(store.df)} total rows -> {p}")
    print("\nStore after ingest, by catalogue:")
    print(store.summary().to_string())


if __name__ == "__main__":
    main()
