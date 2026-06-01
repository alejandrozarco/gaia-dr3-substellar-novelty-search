"""Known-object store + front-of-pipeline filter.

A hunt calls this BEFORE vetting to drop/flag candidates that are already
catalogued, so deep-vet effort is spent only on genuinely-uncatalogued sources
(the lesson from re-vetting ASASSN-14gb / ATO J103.1497-07.9895 at the *back*).

Store schema (one row per known object), persisted as parquet in the catalogue
cache (NOT committed — rebuildable via build.py):
    source_id : str | <NA>   Gaia DR3 source_id where the catalogue provides it
    ra, dec   : float (deg, ICRS)   required
    name      : str          catalogue designation
    otype     : str          object/variable type as the catalogue records it
    catalog   : str          provenance tag (CatalogSpec.key, or a hunt id for ingested knowns)
    pulled_utc: str          ISO timestamp the row entered the store

Matching is positional (cone, default 3") via astropy, plus exact Gaia
source_id where both sides have one. `annotate` is vectorised for whole
candidate tables.
"""
from __future__ import annotations

import os
from pathlib import Path

import numpy as np
import pandas as pd

STORE_COLUMNS = ["source_id", "ra", "dec", "name", "otype", "catalog", "pulled_utc"]


def default_store_path() -> Path:
    """Cache location, consistent with CATALOG_DEPENDENCIES.md (GAIA_NOVELTY_DATA_ROOT)."""
    root = os.environ.get("GAIA_NOVELTY_DATA_ROOT")
    base = Path(root) if root else Path(__file__).resolve().parents[2]
    return base / "data" / "external_catalogs" / "known_objects" / "known_objects.parquet"


def _empty() -> pd.DataFrame:
    df = pd.DataFrame(columns=STORE_COLUMNS)
    return df.astype({"source_id": "string", "ra": "float64", "dec": "float64",
                      "name": "string", "otype": "string", "catalog": "string",
                      "pulled_utc": "string"})


class KnownObjectStore:
    def __init__(self, path: str | os.PathLike | None = None, df: pd.DataFrame | None = None):
        self.path = Path(path) if path is not None else default_store_path()
        if df is not None:
            self.df = self._normalize(df)
        elif self.path.exists():
            self.df = self._normalize(pd.read_parquet(self.path))
        else:
            self.df = _empty()
        self._sc = None  # cached SkyCoord, built lazily

    # -- internals -----------------------------------------------------------
    @staticmethod
    def _normalize(df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()
        for c in STORE_COLUMNS:
            if c not in df.columns:
                df[c] = pd.NA
        df["source_id"] = df["source_id"].astype("string")
        df["ra"] = pd.to_numeric(df["ra"], errors="coerce")
        df["dec"] = pd.to_numeric(df["dec"], errors="coerce")
        for c in ("name", "otype", "catalog", "pulled_utc"):
            df[c] = df[c].astype("string")
        df = df.dropna(subset=["ra", "dec"]).reset_index(drop=True)
        return df[STORE_COLUMNS]

    def _skycoord(self):
        from astropy.coordinates import SkyCoord
        import astropy.units as u
        if self._sc is None or len(self._sc) != len(self.df):
            if len(self.df):
                self._sc = SkyCoord(self.df["ra"].to_numpy(float) * u.deg,
                                    self.df["dec"].to_numpy(float) * u.deg)
            else:
                self._sc = None
        return self._sc

    # -- query ---------------------------------------------------------------
    def match(self, ra: float, dec: float, source_id: str | None = None,
              radius_arcsec: float = 3.0) -> list[dict]:
        """All known-object rows matching one candidate (by source_id and/or cone)."""
        hits: list[dict] = []
        if source_id is not None and len(self.df):
            sid = str(source_id)
            m = self.df[self.df["source_id"].astype("string") == sid]
            hits.extend(m.to_dict("records"))
        sc = self._skycoord()
        if sc is not None:
            from astropy.coordinates import SkyCoord
            import astropy.units as u
            c = SkyCoord(float(ra) * u.deg, float(dec) * u.deg)
            sep = c.separation(sc).arcsec
            within = np.where(sep <= radius_arcsec)[0]
            for j in within:
                row = self.df.iloc[int(j)].to_dict()
                row["sep_arcsec"] = float(sep[j])
                hits.append(row)
        # dedupe by (catalog, name)
        seen, out = set(), []
        for h in hits:
            k = (h.get("catalog"), h.get("name"), h.get("source_id"))
            if k not in seen:
                seen.add(k); out.append(h)
        return out

    def annotate(self, cand: pd.DataFrame, ra_col: str = "ra", dec_col: str = "dec",
                 id_col: str | None = "id", radius_arcsec: float = 3.0) -> pd.DataFrame:
        """Add known/known_catalogs/known_name/known_otype/known_sep_arcsec columns
        to a candidate table. Vectorised; returns a copy."""
        out = cand.copy().reset_index(drop=True)
        n = len(out)
        known = np.zeros(n, bool)
        cats = [""] * n; names = [""] * n; otypes = [""] * n
        seps = np.full(n, np.nan)
        store = self.df
        if n == 0 or len(store) == 0:
            out["known"] = known if n else pd.Series([], dtype=bool)
            out["known_catalogs"] = cats; out["known_name"] = names
            out["known_otype"] = otypes; out["known_sep_arcsec"] = seps
            return out

        # 1) positional crossmatch (all matches within radius, multi-catalogue)
        from astropy.coordinates import SkyCoord
        import astropy.units as u
        cra = pd.to_numeric(out[ra_col], errors="coerce").to_numpy(float)
        cdec = pd.to_numeric(out[dec_col], errors="coerce").to_numpy(float)
        valid = np.isfinite(cra) & np.isfinite(cdec)
        if valid.any():
            cc = SkyCoord(cra[valid] * u.deg, cdec[valid] * u.deg)
            sc = self._skycoord()
            idx_c, idx_s, sep2d, _ = sc.search_around_sky(cc, radius_arcsec * u.arcsec)
            valid_pos = np.where(valid)[0]
            per: dict[int, list] = {}
            for ic, is_, s in zip(idx_c, idx_s, sep2d.arcsec):
                gi = int(valid_pos[ic])
                per.setdefault(gi, []).append((float(s), int(is_)))
            for gi, lst in per.items():
                lst.sort()
                known[gi] = True
                catset = []
                for s, is_ in lst:
                    r = store.iloc[is_]
                    tag = str(r["catalog"])
                    if tag not in catset:
                        catset.append(tag)
                cats[gi] = ";".join(catset)
                names[gi] = str(store.iloc[lst[0][1]]["name"])
                otypes[gi] = str(store.iloc[lst[0][1]]["otype"])
                seps[gi] = lst[0][0]

        # 2) exact Gaia source_id (catches high-PM stars a cone might miss)
        if id_col and id_col in out.columns and store["source_id"].notna().any():
            sstore = store.dropna(subset=["source_id"]).copy()
            sstore["source_id"] = sstore["source_id"].astype("string")
            by_sid = {sid: g for sid, g in sstore.groupby("source_id")}
            cand_ids = out[id_col].astype("string")
            for i in range(n):
                sid = cand_ids.iloc[i]
                if sid in by_sid:
                    g = by_sid[sid]
                    known[i] = True
                    extra = [t for t in g["catalog"].astype(str).tolist()]
                    merged = [c for c in (cats[i].split(";") if cats[i] else []) ]
                    for t in extra:
                        if t not in merged:
                            merged.append(t)
                    cats[i] = ";".join([c for c in merged if c])
                    if not names[i]:
                        names[i] = str(g.iloc[0]["name"])
                        otypes[i] = str(g.iloc[0]["otype"])

        out["known"] = known
        out["known_catalogs"] = cats
        out["known_name"] = names
        out["known_otype"] = otypes
        out["known_sep_arcsec"] = seps
        return out

    # -- mutate --------------------------------------------------------------
    def append(self, rows: pd.DataFrame, catalog: str | None = None,
               pulled_utc: str | None = None) -> int:
        """Add rows (any subset of STORE_COLUMNS; catalog/pulled_utc fill defaults),
        dedupe, keep in memory. Call save() to persist. Returns rows added."""
        add = rows.copy()
        if catalog is not None and "catalog" not in add.columns:
            add["catalog"] = catalog
        if pulled_utc is not None and "pulled_utc" not in add.columns:
            add["pulled_utc"] = pulled_utc
        add = self._normalize(add)
        before = len(self.df)
        self.df = pd.concat([self.df, add], ignore_index=True)
        # dedupe: same catalogue + ~same position (round to ~0.5") + same source_id
        self.df["_rkey"] = (self.df["catalog"].astype(str) + "|"
                            + self.df["source_id"].astype(str) + "|"
                            + (self.df["ra"] * 7200).round().astype("Int64").astype(str) + "|"
                            + (self.df["dec"] * 7200).round().astype("Int64").astype(str))
        self.df = self.df.drop_duplicates("_rkey").drop(columns="_rkey").reset_index(drop=True)
        self._sc = None
        return len(self.df) - before

    def save(self, path: str | os.PathLike | None = None) -> Path:
        p = Path(path) if path is not None else self.path
        p.parent.mkdir(parents=True, exist_ok=True)
        self.df.to_parquet(p, index=False)
        return p

    def summary(self) -> pd.Series:
        return self.df["catalog"].value_counts()
