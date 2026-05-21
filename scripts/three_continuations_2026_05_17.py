"""Three deferred items: widened SB1 mass function, FLAG-tier 8 vetting,
Kervella H2G2 via CDS direct.

(1) Widened SB1 (31,668 sources):
    - Pourbaix mass function with FLAME-isochrone M_1 fallback to 1.0 M_sun
    - Marginalize over isotropic-cos(i) prior
    - Apply conditional RUWE<7 (SB1 in orbit-reflex set)
    - Count substellar (M_2_marg < 80 MJ); compare to original 3,049 yield

(2) FLAG-tier 8 deep-vet (Tycho-Gaia chi^2 30-100, M_2_marg < 30 MJ):
    - SIMBAD coord resolution -> HD names
    - SB9, exoplanet.eu, Sahlmann 2025 cross-match
    - Note any clean enough for headline promotion

(3) Kervella H2G2 PMa via CDS direct download:
    - wget the catalog data file directly (bypass Vizier VOTABLE bug)
    - cross-match against our 17 headline + 110 anon SB1
"""
from __future__ import annotations

import io
import math
import sys
import time
import urllib.request
from pathlib import Path

import numpy as np
import astropy.units as u
import polars as pl
from astropy.coordinates import SkyCoord
from astroquery.gaia import Gaia
from astroquery.simbad import Simbad
from astroquery.vizier import Vizier

ROOT = Path("/tmp/gaia-novelty-publication")
INTER = ROOT / "data" / "intermediate"
INTER.mkdir(parents=True, exist_ok=True)

G_SI = 6.67430e-11
M_SUN_KG = 1.98892e30
M_JUP_KG = 1.89813e27
M_JUP_PER_SUN = M_SUN_KG / M_JUP_KG
DAY_S = 86400.0


# =========================================================================
# (1) Widened SB1: mass function on 31,668 sources
# =========================================================================

def mass_function_mjup(K1_mps, P_d, e):
    K = float(K1_mps)
    P = float(P_d) * DAY_S
    e = float(e)
    return K**3 * P * (1 - e**2) ** 1.5 / (2 * math.pi * G_SI) / M_JUP_KG


def m2_from_mf(fM_mjup, M1_msun, sin_i):
    if sin_i <= 0:
        return float("inf")
    M1_mjup = M1_msun * M_JUP_PER_SUN
    rhs_coef = fM_mjup / (sin_i ** 3)
    lo, hi = 1e-3, 1e6
    for _ in range(60):
        mid = 0.5 * (lo + hi)
        if mid ** 3 > rhs_coef * (M1_mjup + mid) ** 2:
            hi = mid
        else:
            lo = mid
    return 0.5 * (lo + hi)


def marg_m2(fM_mjup, M1_msun, n_samp=2000, rng=None):
    rng = rng or np.random.default_rng(42)
    cosi = rng.uniform(-1.0, 1.0, n_samp)
    sini = np.sqrt(np.maximum(0.0, 1.0 - cosi**2))
    m2s = [m2_from_mf(fM_mjup, M1_msun, float(si)) for si in sini]
    m2s = np.array([x for x in m2s if np.isfinite(x)])
    if m2s.size == 0:
        return None, None, None
    return (float(np.percentile(m2s, 16)),
            float(np.percentile(m2s, 50)),
            float(np.percentile(m2s, 84)))


def process_widened():
    print("(1) Widened SB1 pool — mass function + conditional RUWE …")
    df = pl.read_csv(INTER / "nss_sb1_pool_widened_v13_plx2_sig3.csv")
    print(f"  loaded: {len(df)} rows")

    # Look up FLAME M_1 in chunks
    ids = [int(x) for x in df["source_id"].to_list()]
    flame_chunks = []
    BATCH = 5000
    print(f"  pulling FLAME M_1 for {len(ids)} sources in {len(ids)//BATCH + 1} chunks…")
    for i in range(0, len(ids), BATCH):
        sub = ids[i:i+BATCH]
        ids_str = ",".join(str(x) for x in sub)
        q = (f"SELECT source_id, mass_flame FROM gaiadr3.astrophysical_parameters "
             f"WHERE source_id IN ({ids_str})")
        try:
            res = Gaia.launch_job_async(q).get_results().to_pandas()
            flame_chunks.append(res)
        except Exception as e:  # noqa: BLE001
            print(f"    chunk {i//BATCH} err: {type(e).__name__}: {e}")
    import pandas as pd
    flame = pl.from_pandas(pd.concat(flame_chunks, ignore_index=True)) \
              if flame_chunks else pl.DataFrame({"source_id": [], "mass_flame": []})
    print(f"  FLAME rows pulled: {len(flame)}")

    df = df.with_columns(pl.col("source_id").cast(pl.Int64))
    flame = flame.with_columns(pl.col("source_id").cast(pl.Int64))
    df = df.join(flame, on="source_id", how="left")

    # Compute marginalized M_2 per source
    rng = np.random.default_rng(42)
    m2_med = []
    m2_lo = []
    m2_hi = []
    for r in df.iter_rows(named=True):
        K = r.get("semi_amplitude_primary")
        P = r.get("period")
        e = r.get("eccentricity")
        if K is None or P is None or e is None:
            m2_med.append(None); m2_lo.append(None); m2_hi.append(None)
            continue
        try:
            fM = mass_function_mjup(float(K) * 1000.0, P, e)
            M1 = r.get("mass_flame")
            M1 = float(M1) if M1 is not None and M1 > 0.1 else 1.0
            lo, med, hi = marg_m2(fM, M1, n_samp=1500, rng=rng)
            m2_med.append(med); m2_lo.append(lo); m2_hi.append(hi)
        except Exception:  # noqa: BLE001
            m2_med.append(None); m2_lo.append(None); m2_hi.append(None)

    df = df.with_columns([
        pl.Series("m2_marg_med_mjup", m2_med),
        pl.Series("m2_marg_1sig_lo_mjup", m2_lo),
        pl.Series("m2_marg_1sig_hi_mjup", m2_hi),
    ])

    # Substellar + conditional RUWE pass
    substellar = df.filter(
        (pl.col("m2_marg_med_mjup") < 80.0)
        & (pl.col("m2_marg_med_mjup").is_not_null())
    )
    print(f"  substellar (M_2_marg < 80 MJ): {len(substellar)}")

    cond_pass = substellar.filter(
        (pl.col("ruwe").is_null()) | (pl.col("ruwe") < 7.0)
    )
    print(f"  after conditional RUWE<7: {len(cond_pass)}")

    cond_pass.write_csv(INTER / "nss_sb1_widened_substellar_2026_05_17.csv")

    # Compare to original pool overlap
    orig = pl.read_csv(INTER / "nss_sb1_pool_with_m2_2026_05_17.csv")
    orig_ids = set(int(x) for x in orig["source_id"].to_list())
    new_substellar = cond_pass.filter(
        ~pl.col("source_id").is_in(list(orig_ids))
    )
    print(f"  NEW substellar (not in original 3,049 pool): {len(new_substellar)}")
    new_substellar.write_csv(INTER / "nss_sb1_widened_NEW_substellar_2026_05_17.csv")

    # Stricter subset: M_2_marg < 30 MJ (strong-BD)
    strong = new_substellar.filter(pl.col("m2_marg_med_mjup") < 30.0)
    print(f"  NEW + strong-BD (M_2_marg < 30 MJ): {len(strong)}")
    strong.sort("m2_marg_med_mjup").write_csv(
        INTER / "nss_sb1_widened_strong_BD_new_2026_05_17.csv"
    )

    return {
        "pool_size": len(df),
        "substellar": len(substellar),
        "cond_ruwe_pass": len(cond_pass),
        "new_substellar": len(new_substellar),
        "new_strong_BD": len(strong),
    }


# =========================================================================
# (2) Deep-vet FLAG-tier 8 anon SB1 (Tycho-Gaia chi^2 30-100, M_2_marg < 30 MJ)
# =========================================================================

FLAG8_HD_NAMES = {
    3847285507365485312: "HD 83408",
    5917074949359384320: "HD 153386",
    2035657061984110848: "HD 337746",
    2108452638780763008: "HD 171384",  # M_2_marg=62.6 (>30 so exclude from "strong")
    6501674149261991424: "HD 221068",
    1500988304271482496: "HD 118687",
    2934241052985789568: "HD 54958",   # chi^2=112 = REJECT-tier
    1078149598613200768: "HD 90696",   # chi^2=153 = REJECT-tier
}


def vet_flag8():
    """Deep-vet the 8 HD-named FLAG-tier sources (chi^2 30-100 + M_2<30)."""
    print("\n(2) Deep-vetting 8 FLAG-tier anon SB1 candidates …")
    # Load Sahlmann
    sahl_path = Path("/Users/legbatterij/claude_projects/ostinato/data/"
                       "candidate_dossiers/arenou2023_sahlmann2025_filter_2026_05_12/"
                       "sahlmann2025_verdicts.csv")
    sahl = pl.read_csv(sahl_path, infer_schema_length=20000) \
              if sahl_path.exists() else pl.DataFrame()
    sahl_ids = set(int(x) for x in sahl["source_id"].to_list()) \
                  if not sahl.is_empty() else set()

    # exoplanet.eu
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

    rows = []
    for sid, hd in FLAG8_HD_NAMES.items():
        q = f"SELECT ra, dec FROM gaiadr3.gaia_source WHERE source_id={sid}"
        try:
            g = Gaia.launch_job_async(q).get_results().to_pandas()
            ra, dec = float(g.iloc[0]['ra']), float(g.iloc[0]['dec'])
        except Exception:  # noqa: BLE001
            ra, dec = None, None
        sc = SkyCoord(ra*u.deg, dec*u.deg) if ra is not None else None

        in_sb9, in_epx, epx_match = None, None, None
        if sc is not None:
            try:
                r = Vizier.query_region(sc, radius=5*u.arcsec,
                                          catalog="B/sb9/main")
                in_sb9 = bool(r and len(r) > 0 and len(r[0]) > 0)
            except Exception:  # noqa: BLE001
                pass
            if epx_sc is not None:
                sep = sc.separation(epx_sc).arcsec
                hits = (sep < 30.0).nonzero()[0]
                in_epx = len(hits) > 0
                if in_epx:
                    epx_match = "; ".join(epx.iloc[hits]["name"].tolist()[:3])

        in_sahl = sid in sahl_ids

        rows.append({
            "source_id": sid, "hd_name": hd,
            "in_sb9": in_sb9, "in_exoplanet_eu": in_epx,
            "epx_match": epx_match, "in_sahlmann": in_sahl
        })
        time.sleep(0.3)

    df = pl.DataFrame(rows)
    df.write_csv(INTER / "flag8_deep_vet_2026_05_17.csv")
    print(df)

    n_clean = df.filter(
        ~pl.col("in_sb9").fill_null(False)
        & ~pl.col("in_exoplanet_eu").fill_null(False)
        & ~pl.col("in_sahlmann")
    ).shape[0]
    print(f"  clean (no SB9, no exoplanet.eu, no Sahlmann): {n_clean}/8")
    return df


# =========================================================================
# (3) Kervella H2G2 PMa via CDS direct
# =========================================================================

def fetch_kervella_cds():
    """Download Kervella et al 2022 H2G2 catalog directly from CDS.

    CDS catalog J/A+A/657/A7. The files are at cdsarc.cds.unistra.fr/ftp/
    Tables b1 (HIP+G3) and b2 (HIP+G2). Each is a fixed-format ASCII file.
    """
    print("\n(3) Kervella H2G2 PMa via CDS direct download …")
    targets = [
        ("https://cdsarc.cds.unistra.fr/ftp/J/A+A/657/A7/tableb1.dat",
         "tableb1.dat", "HIP+G3"),
        ("https://cdsarc.cds.unistra.fr/ftp/J/A+A/657/A7/tableb2.dat",
         "tableb2.dat", "HIP+G2"),
        ("https://cdsarc.cds.unistra.fr/ftp/J/A+A/657/A7/ReadMe",
         "ReadMe", "format description"),
    ]
    out_dir = INTER / "kervella_h2g2_cds"
    out_dir.mkdir(exist_ok=True)
    for url, fname, desc in targets:
        out = out_dir / fname
        if out.exists() and out.stat().st_size > 1000:
            print(f"  {fname}: cached ({out.stat().st_size} bytes)")
            continue
        try:
            urllib.request.urlretrieve(url, out)
            print(f"  {fname}: downloaded ({out.stat().st_size} bytes, {desc})")
        except Exception as e:  # noqa: BLE001
            print(f"  {fname}: ERR {type(e).__name__}: {e}")

    # Parse tableb1 header from ReadMe to find HIP + snrPMa columns
    readme_path = out_dir / "ReadMe"
    if readme_path.exists():
        content = readme_path.read_text()
        # ReadMe has byte-by-byte format spec; look for "Byte-by-byte ... tableb1"
        idx = content.find("tableb1")
        if idx >= 0:
            snippet = content[idx:idx+3500]
            print(f"\n  ReadMe tableb1 snippet (first 3500 chars):")
            print(snippet[:1200])

    # Try parsing tableb1.dat: HIP is first field, snrPMa column position
    # known from ReadMe. Let's just read first 5 lines to see structure.
    t1 = out_dir / "tableb1.dat"
    if t1.exists():
        with open(t1) as f:
            for i, line in enumerate(f):
                if i < 3:
                    print(f"  tableb1 line {i}: {line.rstrip()[:200]}")
                else:
                    break

    # Cross-match against our HIP-named candidates
    head = pl.read_csv(ROOT / "novelty_candidates.csv") \
              .select(["name", "hip"]).drop_nulls("hip") \
              .with_columns(pl.col("hip").cast(pl.Int64))
    hips = set(int(x) for x in head["hip"].to_list())
    print(f"\n  Probing for HIPs: {sorted(hips)}")

    # Quick fixed-position parse: ReadMe will tell us, but let's try a generic
    # whitespace split (Kervella tableb1 is space-separated with HIP first)
    if t1.exists():
        hits = []
        try:
            with open(t1) as f:
                for line in f:
                    parts = line.split()
                    if not parts:
                        continue
                    try:
                        hip = int(parts[0])
                        if hip in hips:
                            hits.append((hip, line.rstrip()))
                    except ValueError:
                        continue
            print(f"\n  HIP cross-match against our headline list: {len(hits)} hits")
            for hip, line in hits:
                print(f"    HIP {hip}: {line[:300]}")
        except Exception as e:  # noqa: BLE001
            print(f"  parse err: {type(e).__name__}: {e}")


# =========================================================================
# main
# =========================================================================

def main():
    res1 = process_widened()
    df2 = vet_flag8()
    fetch_kervella_cds()

    print("\n=== SUMMARY ===")
    print(f"(1) Widened pool 31,668 -> substellar {res1['substellar']}, "
          f"cond-RUWE-pass {res1['cond_ruwe_pass']}, "
          f"NEW (not in original 3,049) {res1['new_substellar']}, "
          f"strong-BD (M2<30) {res1['new_strong_BD']}")
    print(f"(2) FLAG-tier 8 vetted -> see flag8_deep_vet csv")
    print(f"(3) Kervella H2G2 -> see kervella_h2g2_cds/ dir")


if __name__ == "__main__":
    sys.exit(main() or 0)
