"""Build/refresh the known-object store from the reference catalogues.

    python scripts/known_objects/build.py                 # all registered catalogues + session seed
    python scripts/known_objects/build.py --classes cv     # only CV/accretor catalogues
    python scripts/known_objects/build.py --no-vsx --no-gaia-tap   # skip the heavy/finicky pulls
    python scripts/known_objects/build.py --dry-run        # report what would be pulled

Per-catalogue failures are logged and skipped (never abort the whole build).
Data is written to the catalogue cache (CATALOG_DEPENDENCIES.md), NOT the repo.
"""
from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
from reference_catalogs import CATALOGS, specs_for  # noqa: E402
from store import KnownObjectStore  # noqa: E402

NOW = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())

# This session's deflated objects — caught at the BACK; seed them so they're
# caught at the FRONT next time. (Gaia DR3 id, ra, dec, name, otype, tag)
SESSION_SEED = [
    ("6048007439673413760", 250.55517, -23.22049, "ASASSN-14gb", "CV:UGSU", "session_deflated"),
    ("3051038565433012480", 103.14978, -7.98960, "ATO J103.1497-07.9895", "CV:UG", "session_deflated"),
    ("1682129610835350400", 190.17895, 67.17622, "GaiaDR3 1682129610835350400", "WD:DBZ_halo", "session_deflated"),
]


def _find(cols, hints):
    low = {str(c).lower(): c for c in cols}
    for h in hints:
        if h.lower() in low:
            return low[h.lower()]
    for c in cols:                       # substring fallback
        for h in hints:
            if h.lower() in str(c).lower():
                return c
    return None


def _vizier_tables(spec):
    from astroquery.vizier import Vizier
    # '**' = all native columns; '_RAJ2000'/'_DEJ2000' = VizieR computed DECIMAL
    # coords, so catalogues that store only sexagesimal RA/DE strings still work.
    kw = dict(columns=["**", "_RAJ2000", "_DEJ2000"], row_limit=-1)
    if spec.column_filters:
        kw["column_filters"] = dict(spec.column_filters)
    return Vizier(**kw).get_catalogs(spec.ident)


def _rows_from_table(t, spec):
    cols = t.colnames
    ra = _find(cols, spec.ra_hints); dec = _find(cols, spec.dec_hints)
    if not (ra and dec):
        return None
    df = t.to_pandas()
    out = pd.DataFrame({"ra": pd.to_numeric(df[ra], errors="coerce"),
                        "dec": pd.to_numeric(df[dec], errors="coerce")})
    nm = _find(cols, spec.name_hints); ty = _find(cols, spec.type_hints)
    sid = _find(cols, spec.sourceid_hints)
    out["name"] = df[nm].astype(str) if nm else ""
    out["otype"] = df[ty].astype(str) if ty else ""
    out["source_id"] = df[sid].astype(str) if sid else pd.NA
    out["catalog"] = spec.key
    out["pulled_utc"] = NOW
    return out.dropna(subset=["ra", "dec"])


def pull_vizier(spec, store, dry):
    try:
        tables = _vizier_tables(spec)
    except Exception as e:
        print(f"  [{spec.key}] VizieR pull FAILED: {repr(e)[:140]}"); return 0
    if tables is None or len(tables) == 0:
        print(f"  [{spec.key}] no tables returned"); return 0
    total = 0
    for t in tables:
        rows = _rows_from_table(t, spec)
        if rows is None or len(rows) == 0:
            continue
        if dry:
            print(f"  [{spec.key}] would add {len(rows)} rows from a {spec.ident} table")
            total += len(rows); continue
        total += store.append(rows)
    print(f"  [{spec.key}] +{total} rows")
    return total


def pull_gaia_tap(spec, store, dry):
    try:
        from astroquery.gaia import Gaia
        q = (f"SELECT v.source_id, s.ra, s.dec, v.best_class_name "
             f"FROM {spec.ident} v JOIN gaiadr3.gaia_source s USING (source_id) "
             f"WHERE v.best_class_name='CV'")
        job = Gaia.launch_job_async(q)
        df = job.get_results().to_pandas()
    except Exception as e:
        print(f"  [{spec.key}] Gaia TAP pull FAILED: {repr(e)[:140]}"); return 0
    if not len(df):
        print(f"  [{spec.key}] 0 rows"); return 0
    rows = pd.DataFrame({"source_id": df["source_id"].astype(str),
                         "ra": pd.to_numeric(df["ra"], errors="coerce"),
                         "dec": pd.to_numeric(df["dec"], errors="coerce"),
                         "name": "GaiaDR3 " + df["source_id"].astype(str),
                         "otype": df["best_class_name"].astype(str),
                         "catalog": spec.key, "pulled_utc": NOW})
    if dry:
        print(f"  [{spec.key}] would add {len(rows)} rows"); return len(rows)
    n = store.append(rows)
    print(f"  [{spec.key}] +{n} rows")
    return n


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--classes", nargs="*", default=None, help="lane classes to seed (default all)")
    ap.add_argument("--out", default=None, help="store path override")
    ap.add_argument("--no-vsx", action="store_true", help="skip the big/finicky VSX pull")
    ap.add_argument("--no-gaia-tap", action="store_true", help="skip Gaia-TAP pulls")
    ap.add_argument("--no-session-seed", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    store = KnownObjectStore(path=args.out)
    print(f"store: {store.path}  (starting rows: {len(store.df)})")

    specs = specs_for(args.classes)
    for spec in specs:
        if args.no_vsx and spec.key == "vsx_cataclysmic":
            print(f"  [{spec.key}] skipped (--no-vsx)"); continue
        if spec.source == "gaia_tap":
            if args.no_gaia_tap:
                print(f"  [{spec.key}] skipped (--no-gaia-tap)"); continue
            pull_gaia_tap(spec, store, args.dry_run)
        else:
            pull_vizier(spec, store, args.dry_run)

    if not args.no_session_seed and not args.dry_run:
        seed = pd.DataFrame(SESSION_SEED, columns=["source_id", "ra", "dec", "name", "otype", "catalog"])
        seed["pulled_utc"] = NOW
        n = store.append(seed)
        print(f"  [session_seed] +{n} rows")

    if not args.dry_run:
        p = store.save()
        print(f"\nsaved {len(store.df)} known objects -> {p}")
        print("by catalogue:"); print(store.summary().to_string())
    else:
        print("\n(dry run — nothing written)")


if __name__ == "__main__":
    main()
