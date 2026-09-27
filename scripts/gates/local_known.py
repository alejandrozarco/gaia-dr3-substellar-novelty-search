"""Local first-pass novelty gate against the May-2026 ostinato catalogue store
(~/claude_projects/ostinato/data/external_catalogs/known_objects/known_objects.parquet; 11.3M rows: full VSX, Milliquas,
Ritter & Kolb, Downes CVs, eRASS1 CV catalogues, Akras symbiotics, Garcia-Zamora XP WDs/DZs, Halbwachs AMRF binaries).
The store was pulled in May 2026 (per-row pulled_utc): a hit is authoritative, a miss still needs the live catalogues.

match(df, ra_col, dec_col, radius_arcsec) -> DataFrame with one row per (input row, store match) within the radius:
input index, catalog, name, otype, sep_arcsec. Positions are matched as-is (store positions are catalogue-epoch; use a
generous radius for high-proper-motion objects).
"""
import os
import numpy as np
import pandas as pd

STORE = os.path.expanduser("~/claude_projects/ostinato/data/external_catalogs/known_objects/known_objects.parquet")
_cache = {}


def _load():
    if "df" not in _cache:
        d = pd.read_parquet(STORE, columns=["ra", "dec", "name", "otype", "catalog"])
        d = d[np.isfinite(d.ra) & np.isfinite(d.dec)]
        _cache["df"] = d.sort_values("dec").reset_index(drop=True)
        _cache["dec"] = _cache["df"].dec.values
    return _cache["df"], _cache["dec"]


def match(df, ra_col="RA", dec_col="Dec", radius_arcsec=5.0):
    store, sdec = _load(); r = radius_arcsec / 3600.0; out = []
    for i, (ra, dec) in enumerate(zip(df[ra_col].values, df[dec_col].values)):
        lo, hi = np.searchsorted(sdec, [dec - r, dec + r])
        if hi <= lo:
            continue
        cand = store.iloc[lo:hi]
        sep = np.hypot((cand.ra.values - ra) * np.cos(np.radians(dec)), cand.dec.values - dec) * 3600.0
        for j in np.where(sep <= radius_arcsec)[0]:
            row = cand.iloc[j]
            out.append(dict(idx=df.index[i], catalog=row.catalog, name=row["name"], otype=row.otype, sep_arcsec=round(float(sep[j]), 2)))
    return pd.DataFrame(out)
