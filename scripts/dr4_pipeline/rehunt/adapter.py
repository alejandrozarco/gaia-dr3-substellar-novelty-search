"""adapter.py — load an NSS table into the canonical schema the v2 cascade expects.

The v2 dormant-compact cascade (``scripts/streaming/v2_corrected/consumer_v2.py::
derive_row_v2``) consumes a *row dict* with a fixed set of canonical keys:

    a_phot_mas, parallax, nss_parallax,
    period (P_d), eccentricity (e),
    mass_flame, mass_flame_spec,
    bp_rp, logg_gspphot, logg_gspspec_ann, logg_gspspec,
    teff_gspphot, teff_gspspec_ann,
    rv_amplitude_robust, rv_chisq_pvalue,
    in_sb2 (bool), nss_solution_type (str), flags (int NSS bitmask).

Different on-disk NSS tables name those fields differently:

  * the DR3 *producer* output (``data/raw_chunks/main_RA*.parquet``) names them
    ``period``, ``eccentricity``, ``phot_g_mean_mag``, ``mass_flame``,
    ``teff_gspphot``/``logg_gspphot`` (and stores the Thiele-Innes coefficients
    ``a_thiele_innes`` … rather than a pre-computed ``a_phot_mas``); it does NOT
    carry ``nss_parallax`` / ``logg_gspspec`` / ``logg_gspspec_ann`` —
    those came from a supplementary Gaia lookup;
  * the DR3 *derived* parquet (``data/derived/main_hunt_derived_v2.parquet``)
    renames them ``P_d``, ``e``, ``G``, ``Teff``, ``logg`` and already carries a
    pre-computed ``a_phot_mas`` + ``nss_parallax`` + the gspspec variants;
  * **DR4** (2 Dec 2026) will ship an expanded ``nss_two_body_orbit`` with — per
    the #116 shared assumptions — refined parallax / a_phot / errors, more
    Orbital/AstroSpectroSB1/Acceleration rows, and *possibly new column names or
    solution types*. We do not yet know the exact DR4 datamodel.

So this module is a thin **column-mapping adapter**: a per-profile dict mapping
canonical-key -> source-column-name(s), plus the small amount of derivation the
cascade needs but the raw table doesn't store (a_phot from Thiele-Innes; an
``in_sb2`` default). Pointing the harness at DR4 == adding/adjusting one profile
here (see ``PROFILES['dr4']`` — a stub to fill once the DR4 datamodel is public).

No science logic lives here. The mass-function inversion, the M_1 selection and
all five filters stay in ``consumer_v2`` — this only renames/derives inputs.

stdlib + pandas/numpy; optional polars (used only to read parquet if present).
"""
from __future__ import annotations

import dataclasses
import math
from pathlib import Path
from typing import Any, Iterable

import numpy as np
import pandas as pd

# Reuse the *exact* production a_phot formula — do not re-implement it here.
# (The cascade's photocentric_a_mas has dtype-safe NaN guards we must inherit.)
import sys as _sys

_V2_DIR = (
    Path(__file__).resolve().parents[2] / "streaming" / "v2_corrected"
)
if str(_V2_DIR) not in _sys.path:
    _sys.path.insert(0, str(_V2_DIR))
from consumer_v2 import photocentric_a_mas  # noqa: E402


# ---------------------------------------------------------------------------
# Column-mapping profiles
# ---------------------------------------------------------------------------
#
# A profile maps each *canonical* cascade key to a list of candidate source
# column names, tried in order (first present + non-null wins). Listing several
# names lets one profile span small schema variants (e.g. a derived parquet that
# renamed `period`->`P_d`). The canonical keys are exactly what derive_row_v2
# reads via row.get(...).
#
# `a_phot_mas` is special: if no source column supplies it directly, the adapter
# computes it from the Thiele-Innes coefficients named under `_thiele_innes_*`.

# Canonical keys the cascade consumes (documented for validation / DR4 mapping).
CANONICAL_KEYS = (
    "source_id",
    "a_phot_mas",
    "parallax",        # gaia_source single-star parallax (biased for binaries)
    "nss_parallax",    # orbit-fit parallax (Correction A prefers this)
    "period",          # days
    "eccentricity",
    "mass_flame",      # primary mass -> select_m1
    "mass_flame_spec",
    "bp_rp",
    "logg_gspphot",
    "logg_gspspec_ann",
    "logg_gspspec",
    "teff_gspphot",
    "teff_gspspec_ann",
    "rv_amplitude_robust",
    "rv_chisq_pvalue",
    "in_sb2",
    "nss_solution_type",
    "flags",           # NSS bitmask; F#33 reads bit 13 (8192)
)

# Thiele-Innes element keys used to reconstruct a_phot when not pre-computed.
_TI_KEYS = ("a_thiele_innes", "b_thiele_innes", "f_thiele_innes", "g_thiele_innes")


@dataclasses.dataclass(frozen=True)
class Profile:
    """A named column-mapping profile.

    `mapping[canonical_key] = [src_col, src_col, ...]` (first present wins).
    `thiele_innes` names the A,B,F,G columns used to derive a_phot when no
    direct a_phot column is mapped.
    `notes` is free text shown by ``describe()``.
    """

    name: str
    mapping: dict[str, list[str]]
    thiele_innes: tuple[str, str, str, str] = _TI_KEYS
    notes: str = ""


# --- DR3 "raw" producer output (data/raw_chunks/main_RA*.parquet) ----------
# This is the canonical DR3 NSS table: gaiadr3.nss_two_body_orbit JOIN
# gaiadr3.gaia_source, with the producer.py main-mode column names. a_phot is
# NOT stored (derive it from Thiele-Innes); nss_parallax / gspspec* are absent
# (supply them via a supplementary frame — see load_nss_table(..., supp=...)).
DR3_RAW = Profile(
    name="dr3_raw",
    mapping={
        "source_id": ["source_id"],
        # a_phot_mas omitted -> computed from Thiele-Innes
        "parallax": ["parallax"],
        "nss_parallax": ["nss_parallax"],            # only if merged from supp
        "period": ["period"],
        "eccentricity": ["eccentricity"],
        "mass_flame": ["mass_flame"],
        "mass_flame_spec": ["mass_flame_spec"],
        "bp_rp": ["bp_rp"],
        "logg_gspphot": ["logg_gspphot"],
        "logg_gspspec_ann": ["logg_gspspec_ann"],    # from supp
        "logg_gspspec": ["logg_gspspec"],            # from supp
        "teff_gspphot": ["teff_gspphot"],
        "teff_gspspec_ann": ["teff_gspspec_ann"],    # from supp
        "rv_amplitude_robust": ["rv_amplitude_robust"],
        "rv_chisq_pvalue": ["rv_chisq_pvalue"],
        "in_sb2": ["in_sb2"],
        "nss_solution_type": ["nss_solution_type"],
        "flags": ["flags"],
    },
    notes="DR3 producer.py main-mode output (raw_chunks). a_phot from "
          "Thiele-Innes; nss_parallax/gspspec* via supplementary frame.",
)

# --- DR3 "derived" parquet (data/derived/main_hunt_derived_v2.parquet) -----
# Already carries a_phot_mas, nss_parallax and the gspspec variants, but renamed
# several base columns. Useful as an alternate stand-in input and to show how a
# renamed schema maps. (Note: this parquet already contains v2 outputs too; the
# adapter only reads the *input* columns.)
DR3_DERIVED = Profile(
    name="dr3_derived",
    mapping={
        "source_id": ["source_id"],
        "a_phot_mas": ["a_phot_mas"],
        "parallax": ["parallax"],
        "nss_parallax": ["nss_parallax"],
        "period": ["P_d", "period"],
        "eccentricity": ["e", "eccentricity"],
        "mass_flame": ["mass_flame", "M1_msun"],
        "mass_flame_spec": ["mass_flame_spec"],
        "bp_rp": ["bp_rp"],
        "logg_gspphot": ["logg_gspphot", "logg"],
        "logg_gspspec_ann": ["logg_gspspec_ann"],
        "logg_gspspec": ["logg_gspspec"],
        "teff_gspphot": ["teff_gspphot", "Teff"],
        "teff_gspspec_ann": ["teff_gspspec_ann"],
        "rv_amplitude_robust": ["rv_amplitude_robust"],
        "rv_chisq_pvalue": ["rv_chisq_pvalue"],
        "in_sb2": ["in_sb2"],
        "nss_solution_type": ["nss_solution_type"],
        "flags": ["flags"],
    },
    notes="DR3 derived parquet (main_hunt_derived_v2). a_phot_mas pre-computed; "
          "base columns renamed (P_d/e/G/Teff/logg).",
)

# --- DR4 stub ---------------------------------------------------------------
# PLACEHOLDER. Fill the source-column names once the Gaia DR4 nss_two_body_orbit
# datamodel is published (2 Dec 2026). It currently *inherits the DR3-raw names*
# so the harness runs end-to-end on a DR4 table that happens to keep DR3 names;
# adjust each list below to the real DR4 column names as they land. Things that
# may move in DR4 (per #116 shared assumptions): a refined parallax column, an
# orbit a_phot that may be reported directly (add it under "a_phot_mas" so the
# Thiele-Innes fallback is skipped), renamed/extra Thiele-Innes elements, new
# solution types in `nss_solution_type`, and a possibly-widened `flags` bitmask.
DR4 = Profile(
    name="dr4",
    mapping={
        "source_id": ["source_id"],
        # If DR4 reports a_phot directly, list its column here; else the
        # Thiele-Innes fallback below computes it (same as DR3).
        "a_phot_mas": ["a_phot_mas", "semi_major_axis_phot"],  # 2nd name is a guess
        "parallax": ["parallax"],
        "nss_parallax": ["nss_parallax"],
        "period": ["period", "P_d"],
        "eccentricity": ["eccentricity", "e"],
        "mass_flame": ["mass_flame", "mass_flame_dr4"],  # FLAME col may be renamed
        "mass_flame_spec": ["mass_flame_spec"],
        "bp_rp": ["bp_rp"],
        "logg_gspphot": ["logg_gspphot"],
        "logg_gspspec_ann": ["logg_gspspec_ann"],
        "logg_gspspec": ["logg_gspspec"],
        "teff_gspphot": ["teff_gspphot"],
        "teff_gspspec_ann": ["teff_gspspec_ann"],
        "rv_amplitude_robust": ["rv_amplitude_robust"],
        "rv_chisq_pvalue": ["rv_chisq_pvalue"],
        "in_sb2": ["in_sb2"],
        "nss_solution_type": ["nss_solution_type"],
        "flags": ["flags"],
    },
    # DR4 may rename Thiele-Innes; keep DR3 names as the default guess.
    thiele_innes=_TI_KEYS,
    notes="STUB — inherits DR3-raw names. Replace source-column names with the "
          "real Gaia DR4 nss_two_body_orbit datamodel once public (2 Dec 2026).",
)

PROFILES: dict[str, Profile] = {
    "dr3_raw": DR3_RAW,
    "dr3_derived": DR3_DERIVED,
    "dr4": DR4,
}


def get_profile(name: str) -> Profile:
    if name not in PROFILES:
        raise KeyError(
            f"unknown profile {name!r}; available: {sorted(PROFILES)}"
        )
    return PROFILES[name]


def describe(name: str | None = None) -> str:
    """Human-readable description of one or all profiles (for the CLI/README)."""
    names = [name] if name else list(PROFILES)
    out = []
    for nm in names:
        p = PROFILES[nm]
        out.append(f"profile {p.name!r}: {p.notes}")
        for k in CANONICAL_KEYS:
            srcs = p.mapping.get(k, [])
            out.append(f"    {k:22s} <- {srcs if srcs else '(derived/absent)'}")
        out.append(f"    [a_phot Thiele-Innes fallback: {p.thiele_innes}]")
    return "\n".join(out)


# ---------------------------------------------------------------------------
# Core adaptation
# ---------------------------------------------------------------------------

def _first_present(row: pd.Series, cols: Iterable[str]) -> Any:
    """First column in `cols` present in `row` with a non-null value."""
    for c in cols:
        if c in row.index:
            v = row[c]
            if v is not None and not _is_nan(v):
                return v
    return None


def _is_nan(v: Any) -> bool:
    try:
        return bool(pd.isna(v))
    except (TypeError, ValueError):
        return False


def _read_table(path: str | Path) -> pd.DataFrame:
    """Read a parquet/csv NSS table into a pandas DataFrame (source_id as Int64)."""
    path = Path(path)
    if path.suffix in (".parquet", ".pq"):
        try:
            import polars as pl
            df = pl.read_parquet(path).to_pandas()
        except Exception:
            df = pd.read_parquet(path)
    elif path.suffix in (".csv", ".tsv"):
        sep = "\t" if path.suffix == ".tsv" else ","
        # Keep source_id exact (19-digit) — read as string then to Int64.
        df = pd.read_csv(path, sep=sep, dtype={"source_id": "string"})
    else:
        raise ValueError(f"unsupported table format: {path.suffix}")
    return df


def _merge_supp(df: pd.DataFrame, supp: pd.DataFrame) -> pd.DataFrame:
    """Left-merge supplementary columns (NSS plx, gspspec variants) by source_id.

    Supplementary columns that are absent in `df` are added; columns already in
    `df` are NOT overwritten (the primary table wins). De-duplicates supp on
    source_id first (the Gaia LEFT JOIN can emit multiple rows per source).
    """
    if supp is None or len(supp) == 0:
        return df
    supp = supp.copy()
    supp["source_id"] = supp["source_id"].astype("int64")
    supp = supp.drop_duplicates(subset=["source_id"], keep="first")
    df = df.copy()
    df["source_id"] = df["source_id"].astype("int64")
    add_cols = [c for c in supp.columns
                if c != "source_id" and c not in df.columns]
    if not add_cols:
        return df
    return df.merge(supp[["source_id"] + add_cols], on="source_id", how="left")


def adapt_row(row: pd.Series, profile: Profile) -> dict[str, Any]:
    """Map one source-table row -> a canonical dict for derive_row_v2.

    Computes a_phot from the profile's Thiele-Innes columns when no a_phot
    column is mapped/present. Coerces source_id to int. Leaves numeric NaNs as
    None so the cascade's own guards see them consistently.
    """
    out: dict[str, Any] = {}
    for key in CANONICAL_KEYS:
        out[key] = _first_present(row, profile.mapping.get(key, []))

    # source_id: keep exact integer value (19-digit; never via float).
    sid = out.get("source_id")
    if sid is not None:
        out["source_id"] = int(sid)

    # a_phot fallback: derive from Thiele-Innes if not supplied directly.
    if out.get("a_phot_mas") is None:
        A, B, F, G = (_first_present(row, [c]) for c in profile.thiele_innes)
        out["a_phot_mas"] = photocentric_a_mas(A, B, F, G)

    # in_sb2 default + coercion to a plain bool.
    sb2 = out.get("in_sb2")
    out["in_sb2"] = bool(sb2) if sb2 is not None else False

    # flags: keep integer or None (cascade handles None / NaN).
    fl = out.get("flags")
    if fl is not None and not _is_nan(fl):
        try:
            out["flags"] = int(fl)
        except (TypeError, ValueError):
            out["flags"] = None
    else:
        out["flags"] = None

    return out


def load_nss_table(
    path: str | Path,
    profile: str | Profile = "dr3_raw",
    supp: str | Path | pd.DataFrame | None = None,
    limit: int | None = None,
) -> tuple[pd.DataFrame, list[dict[str, Any]]]:
    """Load an NSS table and return (raw_df, adapted_rows).

    Parameters
    ----------
    path     : parquet/csv NSS table (DR3 raw chunk, DR3 derived, or DR4 export).
    profile  : profile name or Profile object selecting the column mapping.
    supp     : optional supplementary table/path/DataFrame providing columns the
               primary table lacks (NSS parallax, logg_gspspec[_ann],
               teff_gspspec_ann). Merged by source_id; primary table wins.
    limit    : optional cap on number of rows (for smoke tests).

    Returns
    -------
    (raw_df, adapted_rows) where adapted_rows is a list of canonical dicts ready
    for ``consumer_v2.derive_row_v2``.
    """
    prof = profile if isinstance(profile, Profile) else get_profile(profile)
    df = _read_table(path)
    # De-dup the source table on source_id, preferring rows with a non-null NSS
    # parallax (mirrors run_v2's multi-NSS-row handling). If nss_parallax isn't a
    # column yet, just drop_duplicates.
    if "source_id" in df.columns:
        df["source_id"] = df["source_id"].astype("int64")
        if "nss_parallax" in df.columns:
            df = df.sort_values(["source_id", "nss_parallax"],
                                ascending=[True, False], na_position="last")
        df = df.drop_duplicates(subset=["source_id"], keep="first").reset_index(drop=True)

    if supp is not None:
        supp_df = supp if isinstance(supp, pd.DataFrame) else _read_table(supp)
        df = _merge_supp(df, supp_df)

    if limit:
        df = df.head(limit)

    adapted = [adapt_row(r, prof) for _, r in df.iterrows()]
    return df, adapted


if __name__ == "__main__":  # tiny self-describe entry point
    import argparse

    ap = argparse.ArgumentParser(description="Describe NSS adapter profiles.")
    ap.add_argument("--profile", default=None, help="profile to describe (default: all)")
    a = ap.parse_args()
    print(describe(a.profile))
