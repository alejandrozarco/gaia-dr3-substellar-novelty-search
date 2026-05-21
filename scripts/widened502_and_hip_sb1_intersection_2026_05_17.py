"""(A) Cascade the 502 remaining widened-pool substellar candidates.
(B) HIP NSS Sn={1,3,7} intersect Gaia DR3 SB1 — maximally corroborated pool.

(A) The widened SB1 pool (V<13, plx>2, sig>=3) had 568 NEW substellar
    (not in original 3,049). 66 of those were strong-BD (M_2_marg<30 MJ)
    and got the full cascade. The remaining 502 (M_2_marg 30-80 MJ) had
    only the mass-function step. This script applies the full cascade to
    them:
      - Skip slow SIMBAD per-source (use Gaia coord ID resolution instead)
      - Tycho-2 PM via Vizier I/259/tyc2 (per-source)
      - SB9 cross-match
      - exoplanet.eu (vectorized 30" coord match)
      - Sahlmann 2025 (vectorized source_id lookup)
      - HIP cross-match via gaiadr3.hipparcos2_best_neighbour

(B) HIP NSS Sn in {1,3,7} that ALSO have a Gaia DR3 SB1 entry. These
    sources have:
      - Pre-Gaia (1991) Hipparcos detection of non-single-star solution
      - Gaia DR3 SB1 spectroscopic-binary fit
    Both channels independently flag a companion. Strongest possible
    pre-Gaia+Gaia evidence. Apply mass function + tiered classification.
"""
from __future__ import annotations

import io
import math
import sys
import time
import urllib.request
from pathlib import Path

import astropy.units as u
import numpy as np
import polars as pl
from astropy.coordinates import SkyCoord
from astroquery.gaia import Gaia
from astroquery.vizier import Vizier

ROOT = Path("/tmp/gaia-novelty-publication")
INTER = ROOT / "data" / "intermediate"

G_SI = 6.67430e-11
M_SUN_KG = 1.98892e30
M_JUP_KG = 1.89813e27
M_JUP_PER_SUN = M_SUN_KG / M_JUP_KG
DAY_S = 86400.0


# =========================================================================
# (A) Cascade 502 remaining substellar from widened pool
# =========================================================================

def cascade_502():
    print("(A) Cascading the 502 remaining widened-pool substellar …")

    # Load the widened pool + the strong-BD subset (already done)
    new_sub = pl.read_csv(INTER / "nss_sb1_widened_NEW_substellar_2026_05_17.csv")
    strong_done = pl.read_csv(INTER / "cascade_widened66_2026_05_17.csv")
    done_ids = set(int(x) for x in strong_done["source_id"].to_list())
    rest = new_sub.filter(~pl.col("source_id").is_in(list(done_ids)))
    print(f"  Total widened-pool NEW substellar: {len(new_sub)}")
    print(f"  Already cascaded (strong-BD): {len(done_ids)}")
    print(f"  Remaining to cascade: {len(rest)}")

    src_ids = [int(x) for x in rest["source_id"].to_list()]

    # Gaia main-table enrichment + HIP cross-match
    chunks = []
    for i in range(0, len(src_ids), 500):
        sub = src_ids[i:i+500]
        ids = ",".join(str(x) for x in sub)
        q = f"""
        SELECT g.source_id, g.ra, g.dec, g.pmra, g.pmra_error,
               g.pmdec, g.pmdec_error, g.parallax, g.phot_g_mean_mag,
               g.ruwe, g.astrometric_excess_noise,
               h.original_ext_source_id AS hip_via_xmatch
        FROM gaiadr3.gaia_source g
        LEFT JOIN gaiadr3.hipparcos2_best_neighbour h ON g.source_id=h.source_id
        WHERE g.source_id IN ({ids})
        """
        try:
            chunks.append(Gaia.launch_job_async(q).get_results().to_pandas())
        except Exception as e:  # noqa: BLE001
            print(f"  gaia chunk err: {type(e).__name__}")
    import pandas as pd
    gaia = pl.from_pandas(pd.concat(chunks, ignore_index=True))
    print(f"  Gaia info pulled: {len(gaia)} rows; "
          f"HIP via Gaia xmatch: {gaia.filter(pl.col('hip_via_xmatch').is_not_null()).shape[0]}")

    # Tycho-2 PM per source via Vizier I/259/tyc2
    print(f"  Tycho-2 PM lookup ({len(gaia)} sources)…")
    tyc_rows = []
    for i, r in enumerate(gaia.iter_rows(named=True)):
        try:
            sc = SkyCoord(r["ra"]*u.deg, r["dec"]*u.deg)
            res = Vizier(columns=["pmRA","pmDE","e_pmRA","e_pmDE"]) \
                      .query_region(sc, radius=5*u.arcsec, catalog="I/259/tyc2")
            if not res or len(res) == 0:
                tyc_rows.append({"source_id": r["source_id"],
                                   "tyc_pmRA": None, "tyc_pmDE": None,
                                   "tyc_e_pmRA": None, "tyc_e_pmDE": None})
            else:
                t = res[0][0]
                cols = res[0].colnames
                tyc_rows.append({
                    "source_id": r["source_id"],
                    "tyc_pmRA": float(t["pmRA"]) if "pmRA" in cols else None,
                    "tyc_pmDE": float(t["pmDE"]) if "pmDE" in cols else None,
                    "tyc_e_pmRA": float(t["e_pmRA"]) if "e_pmRA" in cols else None,
                    "tyc_e_pmDE": float(t["e_pmDE"]) if "e_pmDE" in cols else None,
                })
        except Exception:  # noqa: BLE001
            tyc_rows.append({"source_id": r["source_id"],
                               "tyc_pmRA": None, "tyc_pmDE": None,
                               "tyc_e_pmRA": None, "tyc_e_pmDE": None})
        time.sleep(0.2)
        if i % 50 == 49:
            print(f"    Tyc ... {i+1}/{len(gaia)}")

    tyc_df = pl.DataFrame(tyc_rows).with_columns(
        pl.col("source_id").cast(pl.Int64))
    gaia = gaia.with_columns(pl.col("source_id").cast(pl.Int64))
    df_ann = rest.with_columns(pl.col("source_id").cast(pl.Int64)) \
                  .join(gaia, on="source_id", how="left") \
                  .join(tyc_df, on="source_id", how="left")

    # PMa chi^2
    def anomaly(r):
        try:
            if (r["tyc_pmRA"] is None or r["tyc_pmDE"] is None
                or r["tyc_e_pmRA"] is None or r["tyc_e_pmDE"] is None):
                return None
            d_ra = float(r["tyc_pmRA"]) - float(r["pmra"])
            d_de = float(r["tyc_pmDE"]) - float(r["pmdec"])
            s_ra = math.sqrt(float(r["tyc_e_pmRA"])**2 + float(r["pmra_error"])**2)
            s_de = math.sqrt(float(r["tyc_e_pmDE"])**2 + float(r["pmdec_error"])**2)
            if s_ra == 0 or s_de == 0: return None
            return (d_ra/s_ra)**2 + (d_de/s_de)**2
        except Exception:  # noqa: BLE001
            return None

    chi2s = [anomaly(r) for r in df_ann.iter_rows(named=True)]
    df_ann = df_ann.with_columns(pl.Series("tycho_gaia_chi2", chi2s))

    # SB9 per-source
    print(f"  SB9 cross-match ({len(df_ann)} sources)…")
    in_sb9 = []
    for i, r in enumerate(df_ann.iter_rows(named=True)):
        try:
            sc = SkyCoord(float(r["ra"])*u.deg, float(r["dec"])*u.deg)
            res = Vizier.query_region(sc, radius=5*u.arcsec, catalog="B/sb9/main")
            in_sb9.append(bool(res and len(res) > 0 and len(res[0]) > 0))
        except Exception:  # noqa: BLE001
            in_sb9.append(None)
        time.sleep(0.2)
        if i % 50 == 49:
            print(f"    SB9 ... {i+1}/{len(df_ann)}")
    df_ann = df_ann.with_columns(pl.Series("in_sb9", in_sb9))

    # exoplanet.eu vectorized
    try:
        with urllib.request.urlopen("https://exoplanet.eu/catalog/csv/",
                                      timeout=60) as resp:
            import pandas as pd
            epx = pd.read_csv(io.BytesIO(resp.read()), low_memory=False)
        epx_sc = SkyCoord(epx["ra"].to_numpy()*u.deg,
                            epx["dec"].to_numpy()*u.deg) \
                    if "ra" in epx.columns else None
    except Exception:  # noqa: BLE001
        epx, epx_sc = None, None

    in_epx, epx_match = [], []
    for r in df_ann.iter_rows(named=True):
        if epx_sc is None:
            in_epx.append(None); epx_match.append(None); continue
        try:
            sc = SkyCoord(float(r["ra"])*u.deg, float(r["dec"])*u.deg)
            sep = sc.separation(epx_sc).arcsec
            hits = (sep < 30.0).nonzero()[0]
            if len(hits) > 0:
                in_epx.append(True)
                epx_match.append("; ".join(epx.iloc[hits]["name"].tolist()[:3]))
            else:
                in_epx.append(False); epx_match.append(None)
        except Exception:  # noqa: BLE001
            in_epx.append(None); epx_match.append(None)
    df_ann = df_ann.with_columns([
        pl.Series("in_exoplanet_eu", in_epx),
        pl.Series("epx_match", epx_match),
    ])

    # Sahlmann 2025
    sahl_path = Path("/Users/legbatterij/claude_projects/ostinato/data/"
                       "candidate_dossiers/arenou2023_sahlmann2025_filter_2026_05_12/"
                       "sahlmann2025_verdicts.csv")
    sahl_ids = set()
    if sahl_path.exists():
        sahl = pl.read_csv(sahl_path, infer_schema_length=20000)
        sahl_ids = set(int(x) for x in sahl["source_id"].to_list())
    df_ann = df_ann.with_columns(
        pl.col("source_id").is_in(list(sahl_ids)).alias("in_sahlmann")
    )

    # Tier
    def tier(c):
        if c is None: return "no_tycho_pm"
        if c > 100: return "REJECT_likely_stellar"
        if c >= 30: return "FLAG_mass_ambiguous"
        if c >= 5:  return "CORROBORATED_real_companion"
        return "isolated_no_outer_body"

    df_ann = df_ann.with_columns(
        pl.col("tycho_gaia_chi2").map_elements(tier, return_dtype=pl.Utf8) \
            .alias("tycho_tier")
    )

    df_ann.write_csv(INTER / "cascade_widened502_2026_05_17.csv")
    print(f"\n  Output: {INTER / 'cascade_widened502_2026_05_17.csv'}")

    # Promotion candidates: CORROB tier + clean vetting + RUWE<2 + M_2<40 MJ
    clean = df_ann.filter(
        ~pl.col("in_sahlmann")
        & ~pl.col("in_exoplanet_eu").fill_null(False)
        & ~pl.col("in_sb9").fill_null(False)
        & (pl.col("ruwe") < 2.0)
        & (pl.col("m2_marg_med_mjup") < 40.0)
        & (pl.col("tycho_tier") == "CORROBORATED_real_companion")
    )
    print(f"\n  Clean + CORROB + RUWE<2 + M_2<40 MJ: {len(clean)}")
    if len(clean) > 0:
        print(clean.select(["source_id", "ra", "dec", "phot_g_mean_mag",
                             "ruwe", "period", "m2_marg_med_mjup",
                             "tycho_gaia_chi2"]).sort("tycho_gaia_chi2", descending=True).head(20))
    return df_ann


# =========================================================================
# (B) HIP NSS ∩ Gaia SB1 intersection — maximally corroborated
# =========================================================================

def hip_nss_sb1_intersection():
    print("\n\n(B) HIP NSS Sn={1,3,7} ∩ Gaia DR3 SB1 intersection …")

    # Load HIP NSS pool (already filtered Sn != 5; we want subset {1,3,7})
    hip_full = pl.read_csv(INTER / "hipparcos_vanLeeuwen2007_FULL.csv")
    hip_nss = hip_full.filter(pl.col("Sn").is_in([1, 3, 7]))
    print(f"  HIP NSS Sn={{1,3,7}}: {len(hip_nss)}")

    # Map HIP -> Gaia DR3 source_id
    hips = [int(x) for x in hip_nss["HIP"].to_list()]
    chunks = []
    for i in range(0, len(hips), 4000):
        sub = hips[i:i+4000]
        ids = ",".join(str(x) for x in sub)
        q = (f"SELECT original_ext_source_id AS hip, source_id "
             f"FROM gaiadr3.hipparcos2_best_neighbour "
             f"WHERE original_ext_source_id IN ({ids})")
        try:
            chunks.append(Gaia.launch_job_async(q).get_results().to_pandas())
        except Exception as e:  # noqa: BLE001
            print(f"  HIP->Gaia chunk err: {type(e).__name__}")
    import pandas as pd
    hip2gaia = pl.from_pandas(pd.concat(chunks, ignore_index=True)) \
                  if chunks else pl.DataFrame()
    print(f"  HIP -> Gaia DR3 cross-match: {len(hip2gaia)}")
    if hip2gaia.is_empty():
        return

    # Now check intersection with Gaia DR3 SB1
    src_ids = [int(x) for x in hip2gaia["source_id"].to_list()]
    sb1_chunks = []
    for i in range(0, len(src_ids), 4000):
        sub = src_ids[i:i+4000]
        ids = ",".join(str(x) for x in sub)
        q = (f"SELECT nss.source_id, nss.nss_solution_type, nss.period, "
             f"nss.eccentricity, nss.semi_amplitude_primary, nss.significance "
             f"FROM gaiadr3.nss_two_body_orbit nss "
             f"WHERE nss.source_id IN ({ids}) "
             f"AND nss.nss_solution_type = 'SB1'")
        try:
            sb1_chunks.append(Gaia.launch_job_async(q).get_results().to_pandas())
        except Exception:  # noqa: BLE001
            pass
    sb1 = pl.from_pandas(pd.concat(sb1_chunks, ignore_index=True)) \
              if sb1_chunks else pl.DataFrame()
    print(f"  HIP NSS ∩ Gaia DR3 SB1: {len(sb1)} sources")

    if sb1.is_empty():
        print("  Empty intersection — no dual-detection candidates")
        return

    # Join HIP Sn back
    hip_meta = hip_nss.select(["HIP", "Sn", "Hpmag"]).rename({"HIP": "hip"}) \
                       .with_columns(pl.col("hip").cast(pl.Int64))
    hip2gaia = hip2gaia.with_columns([pl.col("hip").cast(pl.Int64),
                                         pl.col("source_id").cast(pl.Int64)])
    sb1 = sb1.with_columns(pl.col("source_id").cast(pl.Int64))
    inter = sb1.join(hip2gaia, on="source_id", how="left") \
                 .join(hip_meta, on="hip", how="left")

    # Gaia main-table
    ids2 = [int(x) for x in inter["source_id"].to_list()]
    if len(ids2) > 0:
        ids_str = ",".join(str(x) for x in ids2)
        q = (f"SELECT source_id, ra, dec, phot_g_mean_mag, parallax, "
             f"ruwe, astrometric_excess_noise "
             f"FROM gaiadr3.gaia_source WHERE source_id IN ({ids_str})")
        gmeta = pl.from_pandas(Gaia.launch_job_async(q).get_results().to_pandas())
        gmeta = gmeta.with_columns(pl.col("source_id").cast(pl.Int64))
        inter = inter.join(gmeta, on="source_id", how="left")

    # Pourbaix mass function with M_1 = 1.0 fallback
    def m2_from_mf(fM_mjup, M1_msun, sin_i):
        if sin_i <= 0: return float("inf")
        M1_mjup = M1_msun * M_JUP_PER_SUN
        rhs_coef = fM_mjup / (sin_i**3)
        lo, hi = 1e-3, 1e6
        for _ in range(60):
            mid = 0.5*(lo+hi)
            if mid**3 > rhs_coef*(M1_mjup+mid)**2:
                hi = mid
            else:
                lo = mid
        return 0.5*(lo+hi)

    rng = np.random.default_rng(42)
    m2_med = []
    for r in inter.iter_rows(named=True):
        K = r.get("semi_amplitude_primary")
        P = r.get("period")
        e = r.get("eccentricity")
        if K is None or P is None or e is None:
            m2_med.append(None); continue
        try:
            fM = (float(K)*1000.0)**3 * float(P)*DAY_S \
                  * (1-float(e)**2)**1.5 / (2*math.pi*G_SI) / M_JUP_KG
            cosi = rng.uniform(-1, 1, 1500)
            sini = np.sqrt(np.maximum(0, 1 - cosi**2))
            m2s = np.array([m2_from_mf(fM, 1.0, float(s)) for s in sini])
            m2s = m2s[np.isfinite(m2s)]
            m2_med.append(float(np.percentile(m2s, 50)) if m2s.size > 0 else None)
        except Exception:  # noqa: BLE001
            m2_med.append(None)
    inter = inter.with_columns(pl.Series("m2_marg_med_mjup", m2_med))

    inter.write_csv(INTER / "hip_nss_x_gaia_sb1_intersection_2026_05_17.csv")
    print(f"\n  Output: {INTER / 'hip_nss_x_gaia_sb1_intersection_2026_05_17.csv'}")
    print(f"  Sources: {len(inter)}")
    print(f"  By Sn:")
    for s in [1, 3, 7]:
        sub = inter.filter(pl.col("Sn") == s)
        print(f"    Sn={s}: {len(sub)}")
    print(f"  Substellar (M_2_marg < 80 MJ): "
          f"{inter.filter(pl.col('m2_marg_med_mjup') < 80).shape[0]}")
    sub_clean = inter.filter(pl.col("m2_marg_med_mjup") < 80)
    print(sub_clean.select(["source_id", "hip", "Sn", "Hpmag",
                              "phot_g_mean_mag", "ruwe", "period",
                              "semi_amplitude_primary", "m2_marg_med_mjup"]) \
                    .sort("m2_marg_med_mjup").head(10))


def main():
    df502 = cascade_502()
    hip_nss_sb1_intersection()


if __name__ == "__main__":
    sys.exit(main() or 0)
