#!/usr/bin/env python3
"""Ingest the published Gaia-XP mining catalogues into the known-object
front-filter, so a future XP-at-scale hunt flags these sources as KNOWN
(closing the same novelty blind-spot the binary_masses ingest closed for
compact candidates — task #103).

Catalogues ingested (each pulled fresh from VizieR; Gaia DR3 source_id kept as
a STRING; rows with null ra/dec dropped; store.append dedupes on
catalog+source_id+rounded-position):

  1. Garcia-Zamora et al. 2023 (A&A 679, A127) — Gaia DR3 XP-spectra white-dwarf
     spectral classification.  VizieR table  J/A+A/679/A127/catalog  (table 3,
     "predicted spectral type for all objects in the 100pc sample").
     SPPred = predicted spectral type.  We split it into two provenance tags:
       - DZ-containing SPPred (metal-polluted WDs)  -> garciazamora2023_xp_dz
       - all other WD spectral types                -> garciazamora2023_xp_wd
     NOTE on counts: the *paper* discusses ~79,000 XP WD candidates incl. ~785
     DZ; the *publicly-tabulated* VizieR table 3 is the 100-pc spectral-class
     sample = 12,351 WDs, of which 257 have a DZ-containing SPPred.  We ingest
     what VizieR actually serves (the operative front-filter test is exact
     source_id / position, so the 100-pc table is the high-value, well-curated
     subset to gate on).

  2. Gaia-XP carbon stars.  The ~43,574-object catalogue named in the task is
     Roulston, Leonhardes-Barboza, Green & Portnoi 2025 (ApJ 982, 184;
     2025ApJ...982..184R; arXiv:2501.18763) — but as of 2026-06-04 its VizieR
     entry J/ApJ/982/184 returns "Catalogue is not found or not available …
     could be in preparation (or removed from public access)", and it is absent
     from TAP_SCHEMA, so it CANNOT be pulled from VizieR today.  Likewise
     Sanders & Matsunaga 2023 (J/MNRAS/521/2745) exposes no positional data
     table in VizieR (online spectra only).  The Gaia-XP carbon-star catalogue
     that IS VizieR-queryable is Ye et al. 2025 (A&A 697, A107; deep-learning
     carbon-star identification from Gaia DR3 XP spectra): public table
       J/A+A/697/A107/tableb1  = 451 highest-confidence C-star candidates
     (the larger full-candidate list is not in the public VizieR release).
     We ingest those 451 under tag  xp_carbon_stars .
     --> ROULSTON_VIZIER below is the hook to flip on the moment J/ApJ/982/184
         (the ~43k catalogue) is ingested into VizieR; re-run this script then.

Offline-friendly (VizieR only; no Gaia ESA TAP).  Re-runnable (store.append
dedupes).  Mirrors scripts/known_objects/ingest_binary_masses.py.

Run:  /Users/legbatterij/claude_projects/ostinato/.venv/bin/python \
        scripts/known_objects/ingest_xp_catalogs.py
"""
import re
import sys
import warnings
from pathlib import Path

import pandas as pd

warnings.filterwarnings("ignore")

BASE = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(BASE / "scripts" / "known_objects"))
from store import KnownObjectStore  # noqa: E402

PULLED = "2026-06-04"

# --- VizieR table IDs (the load-bearing identifiers) -------------------------
GZ_VIZIER = "J/A+A/679/A127/catalog"     # Garcia-Zamora+ 2023 XP WD spectral class (table 3)
YE_VIZIER = "J/A+A/697/A107/tableb1"     # Ye+ 2025 Gaia-XP carbon-star candidates
# Roulston+ 2025 (~43,574 C stars) — NOT in VizieR as of 2026-06-04.
# When CDS ingests it, set this to the real table id (e.g. "J/ApJ/982/184/tableN")
# and re-run; the carbon-star block will pick it up automatically.
ROULSTON_VIZIER = None

_ID_RE = re.compile(r"^\d{5,}$")  # a plausible Gaia DR3 source_id (digits only)


def _vizier_fetch(table, columns):
    """Pull an entire VizieR table as a pandas DataFrame (no row cap)."""
    from astroquery.vizier import Vizier
    v = Vizier(catalog=table, columns=columns)
    v.ROW_LIMIT = -1
    v.TIMEOUT = 120
    cats = v.get_catalogs(table)
    if len(cats) == 0:
        raise RuntimeError(f"VizieR returned no table for {table} "
                           f"(catalogue absent / in preparation / mirror degraded)")
    return cats[0].to_pandas()


def _clean(df, id_col, ra_col, dec_col):
    """Coerce source_id to a clean string and drop rows with null id/ra/dec."""
    out = df.copy()
    out[id_col] = out[id_col].astype(str).str.strip()
    out = out.dropna(subset=[ra_col, dec_col])
    out = out[out[id_col].str.match(_ID_RE)]
    return out


def _rows(df, id_col, ra_col, dec_col, otype, catalog):
    return pd.DataFrame({
        "source_id": df[id_col].astype(str),
        "ra": pd.to_numeric(df[ra_col], errors="coerce").astype(float),
        "dec": pd.to_numeric(df[dec_col], errors="coerce").astype(float),
        "name": df[id_col].map(lambda s: f"Gaia DR3 {s}"),
        "otype": otype,
        "catalog": catalog,
        "pulled_utc": PULLED,
    }).dropna(subset=["ra", "dec"])


def ingest_garcia_zamora(store):
    print("=" * 64)
    print(f"Garcia-Zamora+ 2023 WD  [{GZ_VIZIER}]")
    gz = _vizier_fetch(GZ_VIZIER, ["GaiaDR3", "RA_ICRS", "DE_ICRS", "SPPred"])
    print(f"  rows fetched: {len(gz)}")
    gz = _clean(gz, "GaiaDR3", "RA_ICRS", "DE_ICRS")
    print(f"  rows with valid source_id + ra/dec: {len(gz)}")

    sp = gz["SPPred"].astype(str).str.strip()
    is_dz = sp.str.upper().str.contains("DZ", na=False)
    gz_dz = gz[is_dz].copy()
    gz_wd = gz[~is_dz].copy()
    print(f"  DZ (metal-polluted): {len(gz_dz)}   |   other WD: {len(gz_wd)}")

    dz_rows = _rows(gz_dz, "GaiaDR3", "RA_ICRS", "DE_ICRS",
                    otype="DZ WD", catalog="garciazamora2023_xp_dz")
    # carry the exact predicted subtype into otype for the DZ rows
    dz_rows["otype"] = [f"{t} WD (XP, Garcia-Zamora 2023)"
                        for t in gz_dz["SPPred"].astype(str).str.strip()]
    wd_rows = _rows(gz_wd, "GaiaDR3", "RA_ICRS", "DE_ICRS",
                    otype="WD (XP, Garcia-Zamora 2023)",
                    catalog="garciazamora2023_xp_wd")

    added_wd = store.append(wd_rows)
    added_dz = store.append(dz_rows)
    print(f"  +{added_wd} garciazamora2023_xp_wd   +{added_dz} garciazamora2023_xp_dz")
    return {"garciazamora2023_xp_wd": added_wd, "garciazamora2023_xp_dz": added_dz}


def ingest_carbon_stars(store):
    print("=" * 64)
    counts = {}
    # Prefer the ~43k Roulston catalogue if/when it is in VizieR; else Ye+2025.
    if ROULSTON_VIZIER:
        print(f"Gaia-XP carbon stars  [{ROULSTON_VIZIER}]  (Roulston+ 2025, ~43k)")
        cs = _vizier_fetch(ROULSTON_VIZIER, ["**"])
        # Column names are guesses until the table exists; adjust on ingest day.
        id_col = next(c for c in cs.columns if c.lower() in ("gaiadr3", "source", "source_id"))
        ra_col = next(c for c in cs.columns if c.upper() in ("RA_ICRS", "RAJ2000", "RA"))
        dec_col = next(c for c in cs.columns if c.upper() in ("DE_ICRS", "DEJ2000", "DE", "DEC"))
        cs = _clean(cs, id_col, ra_col, dec_col)
        rows = _rows(cs, id_col, ra_col, dec_col,
                     otype="carbon star (XP)", catalog="xp_carbon_stars")
        added = store.append(rows)
        print(f"  rows valid: {len(cs)}   +{added} xp_carbon_stars")
        counts["xp_carbon_stars"] = added
        return counts

    print(f"Gaia-XP carbon stars  [{YE_VIZIER}]  (Ye+ 2025; "
          f"Roulston ~43k J/ApJ/982/184 not in VizieR as of {PULLED})")
    cs = _vizier_fetch(YE_VIZIER, ["GaiaDR3", "RA_ICRS", "DE_ICRS", "MainType", "Confidence"])
    print(f"  rows fetched: {len(cs)}")
    cs = _clean(cs, "GaiaDR3", "RA_ICRS", "DE_ICRS")
    print(f"  rows with valid source_id + ra/dec: {len(cs)}")
    rows = _rows(cs, "GaiaDR3", "RA_ICRS", "DE_ICRS",
                 otype="carbon star (XP)", catalog="xp_carbon_stars")
    added = store.append(rows)
    print(f"  +{added} xp_carbon_stars")
    counts["xp_carbon_stars"] = added
    return counts


def main():
    store = KnownObjectStore()
    before = len(store.df)
    print(f"store BEFORE: {before} rows  ({store.path})")

    added = {}
    added.update(ingest_garcia_zamora(store))
    added.update(ingest_carbon_stars(store))

    store.save()
    after = len(store.df)
    print("=" * 64)
    print("per-catalogue rows added (net of dedupe):")
    for k, v in added.items():
        print(f"  {k:32s} +{v}")
    print(f"store AFTER:  {after} rows   (net +{after - before})")
    print("--- store catalog breakdown ---")
    print(store.summary().to_string())


if __name__ == "__main__":
    main()
