"""Comprehensive v2 scan v2 (faster) — use cached metadata where available;
only query Gaia TAP for the ~150 missing fields needed.

Pools combined (all already in cached marginalized CSVs):
  - NSS Orbital substellar (2,673 with parallax, RUWE, snrPMa, etc.)
  - NSS Acceleration substellar (6,825 same)
  - NSS SB1+Kervella (already cached with most metadata)

For each, the only data we still need from Gaia TAP is the Thiele-Innes
parameters (for orbital pool only, ~2,673 sources). Other quality flags
(rv_amplitude_robust, rv_chisq_pvalue, ipd_frac) are nice-to-have but not
required for the v2 cascade — we can defer those to the top-100 follow-up.
"""

from __future__ import annotations

import io
import math
import os
import sys
import time
import urllib.parse
import urllib.request
from pathlib import Path

import polars as pl
import scipy.optimize as opt
from astropy.io import fits

sys.path.insert(0, str(Path(__file__).resolve().parent))
from pipeline_v2_tuned_filters_2026_05_13 import (
    DOCUMENTED_NSS_FPS, hgca_chisq_lookup,
)

DATA_ROOT = Path(
    os.environ.get(
        "GAIA_NOVELTY_DATA_ROOT",
        str(Path(__file__).resolve().parent.parent),
    )
)
DOSSIER = DATA_ROOT / "data" / "candidate_dossiers" / "comprehensive_v2_scan_2026_05_13"
DOSSIER.mkdir(parents=True, exist_ok=True)

GAIA_TAP = "https://gea.esac.esa.int/tap-server/tap/sync"

ORBIT_REFLEX_SOLUTION_TYPES = {
    "Orbital", "AstroSpectroSB1", "OrbitalTargetedSearchValidated",
    "OrbitalTargetedSearch", "SB1",
}


def adql_batch(sids: list[str], cols: str, table: str, batch: int = 80) -> list[dict]:
    rows: list[dict] = []
    for i in range(0, len(sids), batch):
        chunk = sids[i:i + batch]
        q = f"SELECT {cols} FROM {table} WHERE source_id IN ({','.join(chunk)})"
        url = GAIA_TAP + "?request=doQuery&lang=ADQL&format=csv&query=" + urllib.parse.quote(q)
        try:
            with urllib.request.urlopen(url, timeout=120) as resp:
                raw = resp.read().decode()
            df = pl.read_csv(io.StringIO(raw), infer_schema_length=10_000, ignore_errors=True)
            rows.extend(df.with_columns(pl.col("source_id").cast(pl.Utf8)).to_dicts())
        except Exception as e:
            print(f"  batch {i // batch} ERR: {e}")
        if (i // batch + 1) % 5 == 0:
            print(f"  ... fetched {i + batch}/{len(sids)}")
        time.sleep(0.05)
    return rows


def a_phot_from_TI(A, B, F, G):
    if any(x is None for x in [A, B, F, G]):
        return None
    sum1 = A**2 + B**2 + F**2 + G**2
    sum2 = (A**2 + B**2 - F**2 - G**2)**2 + 4 * (A*F + B*G)**2
    return math.sqrt((sum1 + math.sqrt(sum2)) / 2)


def m2_kepler(a_1_au, P_yr, M_1_msun):
    def fn(M2_mj):
        M2_sun = M2_mj / 1047.57
        a_tot = ((M_1_msun + M2_sun) * P_yr**2) ** (1/3)
        return a_1_au / a_tot - M2_sun / (M_1_msun + M2_sun)
    try:
        return opt.brentq(fn, 0.05, 5000)
    except ValueError:
        return None


def host_mass_pm(bp_rp, M_G):
    if bp_rp is None or M_G is None:
        return 1.0
    if M_G < 4.5 and bp_rp < 0.8: return 1.1
    if M_G < 5.5 and bp_rp < 1.0: return 1.0
    if M_G < 6.5 and bp_rp < 1.3: return 0.85
    if M_G < 7.5 and bp_rp < 1.6: return 0.7
    if M_G < 9.0 and bp_rp < 2.0: return 0.55
    if M_G < 11.0: return 0.4
    return 0.3


def main() -> int:
    # Load cached pools
    orb = pl.read_csv(
        DATA_ROOT / "data" / "candidate_dossiers"
        / "incl_marginalized_2026_05_12" / "nss_orbital_2678_marginalized.csv",
        infer_schema_length=20_000,
    )
    print(f"NSS Orbital substellar: {len(orb)}")
    acc = pl.read_csv(
        DATA_ROOT / "data" / "candidate_dossiers"
        / "incl_marginalized_2026_05_12" / "nss_accel_6825_marginalized.csv",
        infer_schema_length=20_000,
    )
    print(f"NSS Acceleration substellar: {len(acc)}")

    # Combined records using cached values - no Gaia TAP needed for these
    rows: list[dict] = []
    for r in orb.iter_rows(named=True):
        rows.append({
            "source_id": str(r["source_id"]),
            "source_pool": "orbital_pool",
            "nss_solution_type": r.get("nss_solution_type"),
            "period_d": r.get("period"),
            "eccentricity": r.get("eccentricity"),
            "significance": r.get("significance"),
            "ruwe": r.get("ruwe"),
            "parallax": r.get("parallax"),
            "phot_g_mean_mag": r.get("phot_g_mean_mag"),
            "bp_rp": r.get("bp_rp"),
            "distance_pc": r.get("distance_pc"),
            "M_2_mjup_face_on": r.get("M_2_mjup_ours"),
            "M_2_mjup_marginalized": r.get("M_2_median_true"),
            "M_2_2sigma_hi": r.get("M_2_2sigma_hi"),
            "HIP": r.get("HIP"),
            "Name": r.get("Name"),
            "Vmag": r.get("Vmag"),
            "SpType": r.get("SpType"),
            "snrPMaH2G2": r.get("snrPMaH2G2"),
            "M_host_msun_used": r.get("M_host_msun_used"),
            "sahl_confirmed": r.get("sahl_confirmed"),
            "tier_a": r.get("tier_a"),
            "in_stefansson": r.get("in_stefansson"),
        })
    for r in acc.iter_rows(named=True):
        rows.append({
            "source_id": str(r["source_id"]),
            "source_pool": "acceleration_pool",
            "nss_solution_type": r.get("nss_solution_type"),
            "period_d": None,
            "eccentricity": None,
            "significance": r.get("significance"),
            "ruwe": r.get("RUWE_combined"),
            "parallax": r.get("parallax"),
            "phot_g_mean_mag": r.get("G_combined"),
            "bp_rp": None,
            "distance_pc": r.get("distance_pc"),
            "M_2_mjup_face_on": None,
            "M_2_mjup_marginalized": r.get("M_2_median_true"),
            "M_2_2sigma_hi": r.get("M_2_2sigma_hi"),
            "HIP": r.get("HIP_hgca"),
            "Name": r.get("Name"),
            "Vmag": r.get("V_combined"),
            "SpType": r.get("SpType_combined"),
            "snrPMaH2G2": r.get("snrPMaH2EG3a"),
            "M_host_msun_used": r.get("M1"),
            "sahl_confirmed": None,
            "tier_a": None,
            "in_stefansson": None,
        })
    pool = pl.from_dicts(rows)
    # Dedupe (source can be in both, prefer orbital)
    pool = pool.unique(subset=["source_id"], keep="first", maintain_order=True)
    print(f"Combined pool (unique): {len(pool)}")

    # ----- Apply v2 cascade using cached fields -----
    print("\nApplying v2 cascade ...")
    # documented FP
    pool = pool.with_columns(
        pl.col("source_id").is_in(list(DOCUMENTED_NSS_FPS.keys())).alias("documented_fp")
    )
    # conditional RUWE
    pool = pool.with_columns(
        pl.when(pl.col("nss_solution_type").is_in(list(ORBIT_REFLEX_SOLUTION_TYPES)))
        .then(pl.col("ruwe").fill_null(0) < 7)
        .otherwise(pl.col("ruwe").fill_null(0) < 2)
        .alias("ruwe_pass")
    )
    # NASA Exo
    nasa = pl.read_csv(
        DATA_ROOT / "data" / "candidate_dossiers"
        / "harps_rich_blind_xmatch_2026_05_13" / "nasa_exo_ps_hosts.csv",
        infer_schema_length=10_000,
    )
    nasa_gaia: set[str] = set()
    for r in nasa.iter_rows(named=True):
        g = r.get("gaia_dr3_id")
        if g is not None:
            s = str(g).replace("Gaia DR3", "").strip()
            if s.isdigit():
                nasa_gaia.add(s)
    pool = pool.with_columns(
        pl.col("source_id").is_in(list(nasa_gaia)).alias("nasa_exo_match")
    )
    # HGCA chi^2 tier (HIP-named only)
    chi_map = hgca_chisq_lookup()
    def hgca_lookup(row):
        h = row.get("HIP")
        if h is None: return None
        try: return chi_map.get(int(float(h)))
        except (ValueError, TypeError): return None
    pool = pool.with_columns(
        pl.struct(pool.columns).map_elements(hgca_lookup, return_dtype=pl.Float64).alias("hgca_chisq")
    )
    def hgca_tier(chi):
        if chi is None: return None
        if chi > 100: return "REJECTED_likely_stellar"
        if chi > 30: return "FLAG_mass_ambiguous"
        if chi > 5: return "CORROBORATED_real_companion"
        return "isolated_no_outer_body"
    pool = pool.with_columns(
        pl.col("hgca_chisq").map_elements(hgca_tier, return_dtype=pl.Utf8).alias("hgca_tier")
    )
    # Verdict
    def verdict(r):
        if r.get("documented_fp"): return "REJECTED_documented_fp"
        if r.get("nasa_exo_match"): return "REJECTED_published_nasa_exo"
        if not r.get("ruwe_pass"): return "REJECTED_ruwe_quality"
        if r.get("sahl_confirmed") == 1: return "REJECTED_sahlmann_ml_imposter"
        t = r.get("hgca_tier")
        if t == "REJECTED_likely_stellar": return "REJECTED_hgca_stellar"
        if t == "FLAG_mass_ambiguous": return "FLAG_hgca_mass_ambiguous"
        if t == "CORROBORATED_real_companion": return "CORROBORATED_real_companion"
        return "SURVIVOR_no_hgca_corroboration"
    pool = pool.with_columns(
        pl.struct(pool.columns).map_elements(verdict, return_dtype=pl.Utf8).alias("v2_verdict")
    )
    print("Verdict breakdown:")
    print(pool.group_by("v2_verdict").len().sort("len", descending=True))

    # ----- Score for ranking -----
    print("\nComputing v2 score ...")
    def score(r):
        if r.get("v2_verdict", "").startswith("REJECTED"): return -10.0
        s = 0.0
        sig = r.get("significance") or 0
        s += min(sig / 10, 5)
        if r.get("v2_verdict") == "CORROBORATED_real_companion": s += 2
        elif r.get("v2_verdict") == "FLAG_hgca_mass_ambiguous": s += 0.5
        elif r.get("v2_verdict") == "SURVIVOR_no_hgca_corroboration":
            if r.get("hgca_chisq") is None: s += 0.3
        if r.get("nss_solution_type") == "AstroSpectroSB1": s += 1
        elif r.get("nss_solution_type") == "Orbital": s += 0.5
        elif r.get("nss_solution_type") in ("Acceleration7", "Acceleration9"): s += 0.5
        m2 = r.get("M_2_mjup_marginalized")
        if m2 is not None and 13 < m2 < 80: s += 1
        elif m2 is not None and m2 < 13: s += 0.7
        if r.get("HIP") is not None: s += 0.3
        return s
    pool = pool.with_columns(
        pl.struct(pool.columns).map_elements(score, return_dtype=pl.Float64).alias("v2_score")
    )

    pool.write_csv(DOSSIER / "combined_pool_with_v2_verdict.csv")
    print(f"\nWrote combined_pool_with_v2_verdict.csv ({len(pool)} rows)")

    # ----- Top 100 -----
    survivors = pool.filter(~pl.col("v2_verdict").str.starts_with("REJECTED"))
    top100 = survivors.sort("v2_score", descending=True).head(100)
    top100.write_csv(DOSSIER / "top_100_for_deep_dive.csv")
    print(f"Top 100 (survivors sorted by v2_score): {len(top100)} written")

    print()
    print("=== TOP 20 ===")
    cols = ["source_id", "HIP", "Name", "source_pool", "nss_solution_type",
            "Vmag", "period_d", "eccentricity", "M_2_mjup_marginalized",
            "ruwe", "significance", "hgca_chisq", "hgca_tier", "v2_verdict", "v2_score"]
    present = [c for c in cols if c in top100.columns]
    print(top100.select(present).head(20))

    print("\nVerdict breakdown of top 100:")
    print(top100.group_by("v2_verdict").len().sort("len", descending=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
