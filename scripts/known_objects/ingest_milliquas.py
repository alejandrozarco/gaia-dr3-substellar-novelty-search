#!/usr/bin/env python3
"""Ingest the Milliquas (Million Quasars) catalogue into the known-object
front-filter, so AGN / quasars can be gated POSITIONALLY.

Why (gap surfaced 2026-06-05, lanes #126 / #127): the store held only Galactic
compact-object catalogues (CV / WD / symbiotic / binary_masses / Gaia-XP), so
"absent from the store" was NOT evidence of novelty in extragalactic-prone lanes
— an X-ray-loud blue source could be a quasar and the store could not say so.
The Object-B AGN-misflag recovery, the "absence-as-selection" isolated-NS lane
(#126), and the "mine-the-rejects" QSOC lane (#127) all need an AGN gate.
Milliquas (Flesch, the all-sky Million Quasars compilation) is the standard one.

Milliquas rows are ingested with source_id = <NA> (the catalogue is positional;
most entries carry no Gaia DR3 id), so the store's POSITIONAL cone match (3") is
what flags a candidate as a known quasar. catalog tag = 'milliquas'.

Version-agnostic: the exact VizieR id has changed across Milliquas releases
(VII/258 → VII/280 → VII/290 → …), so we resolve it at run time via
Vizier.find_catalogs and prefer the newest VII/NNN, with --table to override.
Re-runnable (store.append dedupes on catalog+source_id+rounded-position).
VizieR-only; the catalogue is large (~1.5M rows) — allow a long timeout.

Run:
  .../ostinato/.venv/bin/python scripts/known_objects/ingest_milliquas.py            # full ingest
  .../ostinato/.venv/bin/python scripts/known_objects/ingest_milliquas.py --limit 5 --dry-run   # validate
"""
import argparse
import sys
import warnings
from pathlib import Path

import pandas as pd

warnings.filterwarnings("ignore")

BASE = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(BASE / "scripts" / "known_objects"))
from store import KnownObjectStore  # noqa: E402

PULLED = "2026-06-05"


def resolve_tables(explicit=None):
    """Return candidate VizieR table ids for Milliquas, newest VII/NNN first."""
    if explicit:
        return [explicit]
    from astroquery.vizier import Vizier
    found = Vizier.find_catalogs("Milliquas Million Quasars")
    keys = list(found.keys())
    vii = sorted([k for k in keys if k.upper().startswith("VII/")], reverse=True)
    # de-dup while preserving order; fall back to any keys if no VII/ match
    ordered = vii + [k for k in keys if k not in vii]
    return ordered or ["VII/294", "VII/290", "VII/280"]


def fetch(table, limit=None):
    from astroquery.vizier import Vizier
    v = Vizier(catalog=table, columns=["**"])
    v.ROW_LIMIT = (limit if limit else -1)
    v.TIMEOUT = 600
    cats = v.get_catalogs(table)
    if not len(cats):
        raise RuntimeError("VizieR returned no table")
    return cats[0].to_pandas()


def pick(cols, *cands):
    low = {c.lower(): c for c in cols}
    for cand in cands:
        if cand.lower() in low:
            return low[cand.lower()]
    return None


def to_rows(df):
    ra = pick(df.columns, "RAJ2000", "RA_ICRS", "_RAJ2000", "RAdeg", "RA", "_RA.icrs")
    dec = pick(df.columns, "DEJ2000", "DE_ICRS", "_DEJ2000", "DEdeg", "DE", "DEC", "_DE.icrs")
    name = pick(df.columns, "Name", "QSO", "Milliquas", "ID", "recno")
    typ = pick(df.columns, "Type", "Cl", "Class", "Qpct")
    gid = pick(df.columns, "GaiaDR3", "Gaia", "DR3Name", "DR3")
    if not (ra and dec):
        raise SystemExit("could not find RA/DEC columns in %s" % list(df.columns))
    print("  cols -> ra=%s dec=%s name=%s type=%s gaia=%s" % (ra, dec, name, typ, gid))
    sid = (df[gid].astype(str).str.extract(r"(\d{5,})")[0] if gid else pd.Series(pd.NA, index=df.index))
    otype = (("Milliquas " + df[typ].astype(str)).str.strip() if typ else "QSO/AGN (Milliquas)")
    return pd.DataFrame({
        "source_id": sid,
        "ra": pd.to_numeric(df[ra], errors="coerce"),
        "dec": pd.to_numeric(df[dec], errors="coerce"),
        "name": (df[name].astype(str) if name else "Milliquas source"),
        "otype": otype,
        "catalog": "milliquas",
        "pulled_utc": PULLED,
    }).dropna(subset=["ra", "dec"])


def main():
    ap = argparse.ArgumentParser(description="Ingest Milliquas (AGN/QSO) into the known-object store.")
    ap.add_argument("--limit", type=int, default=None, help="row cap (for validation; default = all)")
    ap.add_argument("--table", default=None, help="force a VizieR table id (else auto-resolve)")
    ap.add_argument("--dry-run", action="store_true", help="fetch + report columns, do NOT append/save")
    args = ap.parse_args()

    tables = resolve_tables(args.table)
    print("candidate Milliquas tables:", tables)
    df = used = None
    for t in tables:
        try:
            df = fetch(t, args.limit)
            used = t
            break
        except Exception as ex:  # noqa: BLE001 -- try the next candidate id
            print("  %s: %s" % (t, ex))
    if df is None:
        raise SystemExit("could not fetch any Milliquas table from VizieR")
    print("using %s; fetched %d rows" % (used, len(df)))

    rows = to_rows(df)
    print("valid rows (ra/dec finite): %d" % len(rows))
    if args.dry_run:
        print("DRY RUN — not appending. sample:")
        print(rows.head(5).to_string())
        return

    store = KnownObjectStore()
    before = len(store.df)
    added = store.append(rows)
    store.save()
    print("store %d -> %d  (+%d milliquas)" % (before, len(store.df), added))
    print("--- store catalog breakdown ---")
    print(store.summary().to_string())


if __name__ == "__main__":
    main()
