"""Pipeline v2 with tuned filters (2026-05-13).

Implements three high-value filter cascade updates:
  #1 Conditional RUWE: skip RUWE cut for NSS solution types where
     orbital reflex itself drives RUWE up (Orbital, AstroSpectroSB1,
     OrbitalTargetedSearchValidated)
  #3 exoplanet.eu coord cross-match at 5 arcsec (catches published
     systems NASA Exo PS misses)
  #4 HGCA Brandt 2024 chi^2 tier filter for HIP-named candidates:
     - chi^2 > 100 -> REJECT stellar imposter
     - chi^2 30-100 -> FLAG mass-ambiguous
     - chi^2 5-30 -> CORROBORATED real companion
     - chi^2 < 5 -> isolated (no outer-body anomaly)

This is the v2 standardized library function for any candidate vetting.
"""

from __future__ import annotations

import io
import math
import os
import urllib.parse
import urllib.request
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import polars as pl
from astropy.io import fits

DATA_ROOT = Path(
    os.environ.get(
        "GAIA_NOVELTY_DATA_ROOT",
        str(Path(__file__).resolve().parent.parent),
    )
)

GAIA_TAP = "https://gea.esac.esa.int/tap-server/tap/sync"
HGCA_FILE = "/Users/legbatterij/.cache/uv/git-v0/checkouts/f25841311b3ccd24/6634926/HGCA_vEDR3.fits"
EXOEU_CSV = DATA_ROOT / "data" / "external_catalogs" / "exoplanet_eu" / "exoplanet_eu_catalog.csv"
NASA_HOSTS_CSV = (
    DATA_ROOT / "data" / "candidate_dossiers"
    / "harps_rich_blind_xmatch_2026_05_13" / "nasa_exo_ps_hosts.csv"
)

DOCUMENTED_NSS_FPS = {
    "4698424845771339520": "WD 0141-675",
    "5765846127180770432": "HIP 64690",
    "522135261462534528": "* 54 Cas",
    "1712614124767394816": "HIP 66074",
}

# Solution types that have a real orbit and are EXPECTED to have elevated RUWE
# (do NOT apply RUWE < 2 cut to these)
ORBIT_REFLEX_SOLUTION_TYPES = {
    "Orbital",
    "AstroSpectroSB1",
    "OrbitalTargetedSearchValidated",
    "OrbitalTargetedSearch",
    "SB1",
}


def adql(q: str, tap_url: str = GAIA_TAP, timeout: int = 120) -> pl.DataFrame | None:
    url = tap_url + "?request=doQuery&lang=ADQL&format=csv&query=" + urllib.parse.quote(q)
    try:
        with urllib.request.urlopen(url, timeout=timeout) as resp:
            raw = resp.read().decode()
        return pl.read_csv(io.StringIO(raw), infer_schema_length=10_000, ignore_errors=True)
    except Exception:
        return None


def ang_sep_arcsec(ra1, dec1, ra2, dec2):
    dra = (ra1 - ra2) * math.cos(math.radians((dec1 + dec2) / 2))
    return math.sqrt(dra * dra + (dec1 - dec2) ** 2) * 3600


def filter_documented_fp(pool: pl.DataFrame, sid_col: str = "source_id") -> pl.DataFrame:
    """#27 Filter out the 4 Gaia DR3 NSS documented false-positive source_ids."""
    return pool.with_columns(
        pl.col(sid_col).cast(pl.Utf8).is_in(list(DOCUMENTED_NSS_FPS.keys())).alias("documented_fp")
    )


def filter_conditional_ruwe(
    pool: pl.DataFrame,
    soltype_col: str = "nss_solution_type",
    ruwe_col: str = "ruwe",
    ruwe_strict: float = 2.0,
    ruwe_lax: float = 7.0,
) -> pl.DataFrame:
    """#1 Conditional RUWE: skip strict cut for orbit-reflex solution types.

    Adds 'ruwe_pass' boolean column.
    """
    return pool.with_columns(
        pl.when(pl.col(soltype_col).is_in(list(ORBIT_REFLEX_SOLUTION_TYPES)))
        .then(pl.col(ruwe_col).fill_null(0) < ruwe_lax)
        .otherwise(pl.col(ruwe_col).fill_null(0) < ruwe_strict)
        .alias("ruwe_pass")
    )


def filter_nasa_exo(pool: pl.DataFrame, sid_col: str = "source_id") -> pl.DataFrame:
    """Stage 3a: NASA Exo PS gaia_dr3_id cross-match."""
    if not NASA_HOSTS_CSV.exists():
        return pool.with_columns(pl.lit(False).alias("nasa_exo_match"))
    nasa = pl.read_csv(NASA_HOSTS_CSV, infer_schema_length=10_000)
    known: set[str] = set()
    for r in nasa.iter_rows(named=True):
        g = r.get("gaia_dr3_id")
        if g is not None:
            s = str(g).replace("Gaia DR3", "").strip()
            if s.isdigit():
                known.add(s)
    return pool.with_columns(
        pl.col(sid_col).cast(pl.Utf8).is_in(list(known)).alias("nasa_exo_match")
    )


def filter_exoplanet_eu_coord(
    pool: pl.DataFrame,
    ra_col: str = "ra",
    dec_col: str = "dec",
    radius_arcsec: float = 5.0,
) -> pl.DataFrame:
    """#3 exoplanet.eu coord cross-match (5 arcsec radius)."""
    if not EXOEU_CSV.exists():
        return pool.with_columns(pl.lit(False).alias("exoeu_match"))
    exo = pl.read_csv(EXOEU_CSV, infer_schema_length=20_000, ignore_errors=True)
    exo = exo.filter(pl.col("ra").is_not_null() & pl.col("dec").is_not_null())
    exo_dicts = exo.select(["name", "star_name", "ra", "dec"]).to_dicts()
    matches: set[str] = set()
    for r in pool.iter_rows(named=True):
        ra0, dec0 = r.get(ra_col), r.get(dec_col)
        if ra0 is None or dec0 is None:
            continue
        for e in exo_dicts:
            if ang_sep_arcsec(ra0, dec0, e["ra"], e["dec"]) < radius_arcsec:
                matches.add(str(r["source_id"]))
                break
    return pool.with_columns(pl.col("source_id").cast(pl.Utf8).is_in(list(matches)).alias("exoeu_match"))


def hgca_chisq_lookup() -> dict[int, float]:
    """Load HGCA Brandt 2024 chi^2 by HIP for all 115K HIP stars."""
    if not os.path.exists(HGCA_FILE):
        return {}
    hdul = fits.open(HGCA_FILE)
    data = hdul[1].data
    return {int(r["hip_id"]): float(r["chisq"]) for r in data if r["chisq"] == r["chisq"]}


def filter_hgca_chisq_tier(
    pool: pl.DataFrame, hip_col: str = "HIP", chisq_lookup: dict | None = None
) -> pl.DataFrame:
    """#4 HGCA chi^2 tier filter for HIP-named candidates.

    Adds 'hgca_chisq' and 'hgca_tier' columns:
        chi^2 > 100  -> 'REJECTED_likely_stellar'
        chi^2 30-100 -> 'FLAG_mass_ambiguous'
        chi^2 5-30   -> 'CORROBORATED_real_companion'
        chi^2 < 5    -> 'isolated_no_outer_body'
        no HIP / no HGCA entry -> None
    """
    if chisq_lookup is None:
        chisq_lookup = hgca_chisq_lookup()

    def lookup(r):
        h = r.get(hip_col)
        if h is None:
            return None
        try:
            return chisq_lookup.get(int(float(h)))
        except (ValueError, TypeError):
            return None

    def tier(chi):
        if chi is None:
            return None
        if chi > 100:
            return "REJECTED_likely_stellar"
        if chi > 30:
            return "FLAG_mass_ambiguous"
        if chi > 5:
            return "CORROBORATED_real_companion"
        return "isolated_no_outer_body"

    pool = pool.with_columns(
        pl.struct(pool.columns).map_elements(lookup, return_dtype=pl.Float64).alias("hgca_chisq")
    )
    pool = pool.with_columns(
        pl.col("hgca_chisq").map_elements(tier, return_dtype=pl.Utf8).alias("hgca_tier")
    )
    return pool


def apply_tuned_cascade(
    pool: pl.DataFrame,
    sid_col: str = "source_id",
    hip_col: str = "HIP",
    soltype_col: str = "nss_solution_type",
    ruwe_col: str = "ruwe",
) -> pl.DataFrame:
    """Apply v2 tuned cascade (#1 + #3 + #4 + #27) to a candidate pool."""
    pool = filter_documented_fp(pool, sid_col=sid_col)
    pool = filter_conditional_ruwe(pool, soltype_col=soltype_col, ruwe_col=ruwe_col)
    pool = filter_nasa_exo(pool, sid_col=sid_col)
    if "ra" in pool.columns and "dec" in pool.columns:
        pool = filter_exoplanet_eu_coord(pool, radius_arcsec=5.0)
    else:
        pool = pool.with_columns(pl.lit(False).alias("exoeu_match"))
    pool = filter_hgca_chisq_tier(pool, hip_col=hip_col)
    # Combined verdict
    def verdict(r):
        if r.get("documented_fp"):
            return "REJECTED_documented_fp"
        if r.get("nasa_exo_match"):
            return "REJECTED_published_nasa_exo"
        if r.get("exoeu_match"):
            return "REJECTED_published_exoplanet_eu"
        if not r.get("ruwe_pass"):
            return "REJECTED_ruwe_quality"
        t = r.get("hgca_tier")
        if t == "REJECTED_likely_stellar":
            return "REJECTED_hgca_stellar"
        if t == "FLAG_mass_ambiguous":
            return "FLAG_hgca_mass_ambiguous"
        if t == "CORROBORATED_real_companion":
            return "CORROBORATED_real_companion"
        return "SURVIVOR_no_hgca_corroboration_yet"
    return pool.with_columns(
        pl.struct(pool.columns).map_elements(verdict, return_dtype=pl.Utf8).alias("v2_verdict")
    )


if __name__ == "__main__":
    # Quick self-test on the existing NSS Orbital substellar pool
    nss = pl.read_csv(
        DATA_ROOT / "data" / "candidate_dossiers"
        / "incl_marginalized_2026_05_12" / "nss_orbital_2678_marginalized.csv",
        infer_schema_length=10_000,
    )
    print(f"Input: {len(nss)} NSS Orbital substellar candidates")
    print(f"Pool needs ra/dec — fetching from Gaia TAP for first 50 ...")
    sids = nss["source_id"].cast(pl.Utf8).to_list()[:50]
    coord_q = f"SELECT source_id, ra, dec FROM gaiadr3.gaia_source WHERE source_id IN ({','.join(sids)})"
    coords = adql(coord_q)
    if coords is not None:
        coords = coords.with_columns(pl.col("source_id").cast(pl.Utf8))
        sub = nss.head(50).with_columns(pl.col("source_id").cast(pl.Utf8)).join(coords, on="source_id", how="left")
        out = apply_tuned_cascade(sub)
        print()
        print("Verdict breakdown (50-row sample):")
        print(out.group_by("v2_verdict").len().sort("len", descending=True))
