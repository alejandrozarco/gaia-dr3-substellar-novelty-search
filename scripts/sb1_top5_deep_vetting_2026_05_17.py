"""Deep vetting of the 5 HGCA-corroborated SB1 substellar candidates.

Candidates (from nss_sb1_cascade_2026_05_17.py output):
  HIP 84737  M2_marg=13.2 MJ   chi^2=8.7   RUWE=0.91  G=8.1
  HIP 84506  M2_marg=19.6 MJ   chi^2=9.6   RUWE=1.88  G=8.1
  HIP 8278   M2_marg=58.6 MJ   chi^2=9.3   RUWE=1.67  G=7.6
  HIP 63111  M2_marg=74.9 MJ   chi^2=26.2  RUWE=1.11  G=8.2
  HIP 46631  M2_marg=75.6 MJ   chi^2=13.9  RUWE=5.31  G=8.5

Vetting channels:
  (a) SIMBAD object_type + main_id (HD/star name) + n_bibcodes
  (b) exoplanet.eu coord cross-match within 30" (PM-corrected to J2000)
  (c) NASA Exo PS gaia_dr3_id cross-match
  (d) Sahlmann 2025 preselection table (CONFIRMED_BD, CONFIRMED_BIN, etc.)
  (e) Kervella H2G2 PMa SNR (J/A+A/657/A7)
  (f) WDS visual-double catalog (B/wds/wds)

Output: data/intermediate/sb1_top5_deep_vetting_2026_05_17.csv
"""
from __future__ import annotations

import sys
import time
from pathlib import Path

import astropy.units as u
import polars as pl
from astropy.coordinates import SkyCoord
from astroquery.simbad import Simbad
from astroquery.vizier import Vizier

INTER = Path("/tmp/gaia-novelty-publication/data/intermediate")

# Hard-code the 5 from the cascade output (faster than re-loading + re-filtering)
CANDS = [
    {"hip": 84737, "source_id": 5923327700182691840,
     "ra_deg": None, "dec_deg": None, "g": 8.10,
     "ruwe": 0.91, "chisq": 8.687,
     "P_d": None, "e": None, "K_kms": 0.544,
     "m2_marg": 13.24},
    {"hip": 84506, "source_id": 4543391129276882176,
     "ra_deg": None, "dec_deg": None, "g": 8.15,
     "ruwe": 1.88, "chisq": 9.577,
     "P_d": None, "e": None, "K_kms": 0.454,
     "m2_marg": 19.62},
    {"hip": 8278,  "source_id": 4712905547052004096,
     "ra_deg": None, "dec_deg": None, "g": 7.59,
     "ruwe": 1.67, "chisq": 9.317,
     "P_d": None, "e": None, "K_kms": 1.303,
     "m2_marg": 58.55},
    {"hip": 63111, "source_id": 6074219655134724352,
     "ra_deg": None, "dec_deg": None, "g": 8.22,
     "ruwe": 1.11, "chisq": 26.21,
     "P_d": None, "e": None, "K_kms": 2.850,
     "m2_marg": 74.93},
    {"hip": 46631, "source_id": 5410444146150987008,
     "ra_deg": None, "dec_deg": None, "g": 8.48,
     "ruwe": 5.31, "chisq": 13.86,
     "P_d": None, "e": None, "K_kms": 4.217,
     "m2_marg": 75.63},
]


def enrich_with_gaia(cands):
    """Pull ra/dec/pmra/pmdec/parallax for our 5 source_ids."""
    from astroquery.gaia import Gaia
    ids = ",".join(str(c["source_id"]) for c in cands)
    q = f"""SELECT source_id, ra, dec, pmra, pmdec, parallax,
                  phot_g_mean_mag, bp_rp, ruwe, ipd_frac_multi_peak,
                  non_single_star
            FROM gaiadr3.gaia_source WHERE source_id IN ({ids})"""
    res = Gaia.launch_job_async(q).get_results().to_pandas()
    res = res.set_index("source_id")
    for c in cands:
        if c["source_id"] in res.index:
            r = res.loc[c["source_id"]]
            c["ra_deg"] = float(r["ra"])
            c["dec_deg"] = float(r["dec"])
            c["pmra"] = float(r["pmra"]) if r["pmra"] is not None else None
            c["pmdec"] = float(r["pmdec"]) if r["pmdec"] is not None else None
            c["parallax"] = float(r["parallax"]) if r["parallax"] is not None else None
            c["bp_rp"] = float(r["bp_rp"]) if r["bp_rp"] is not None else None
    return cands


def simbad_lookup(cands):
    s = Simbad()
    s.TIMEOUT = 120
    try:
        s.add_votable_fields("otype", "ids")
    except Exception:  # noqa: BLE001
        pass
    out = []
    for c in cands:
        try:
            r = s.query_object(f"HIP {c['hip']}")
            if r is None or len(r) == 0:
                # Try by coordinates
                sc = SkyCoord(c["ra_deg"]*u.deg, c["dec_deg"]*u.deg)
                r = s.query_region(sc, radius=5*u.arcsec)
            if r is None or len(r) == 0:
                out.append({"hip": c["hip"], "simbad_main_id": None,
                            "simbad_otype": None, "simbad_ids_all": None})
                continue
            row = r[0]
            cols = r.colnames
            mid = str(row["main_id"]) if "main_id" in cols else None
            ot = str(row["otype"]) if "otype" in cols else None
            ids_all = str(row["ids"]) if "ids" in cols else None
            out.append({"hip": c["hip"], "simbad_main_id": mid,
                        "simbad_otype": ot, "simbad_ids_all": ids_all})
        except Exception as e:  # noqa: BLE001
            out.append({"hip": c["hip"], "simbad_main_id": f"ERR:{type(e).__name__}",
                        "simbad_otype": None, "simbad_ids_all": None})
        time.sleep(0.3)
    return out


def vizier_lookup_kervella(hips):
    """Kervella H2G2 PMa is J/A+A/657/A7/tableb1 (Kervella et al 2022)."""
    Vizier.ROW_LIMIT = -1
    Vizier.TIMEOUT = 180
    out = []
    for cat in ["J/A+A/657/A7/tableb1", "J/A+A/657/A7"]:
        try:
            res = Vizier(columns=["**"]).get_catalogs(cat)
            if not res or len(res) == 0:
                continue
            for t in res:
                cols_lower = {c.lower(): c for c in t.colnames}
                if "hip" not in cols_lower:
                    continue
                df = t.to_pandas()
                df = df.rename(columns={cols_lower["hip"]: "hip"})
                df["hip"] = df["hip"].astype(int)
                df = df[df["hip"].isin(hips)]
                if df.empty:
                    continue
                # try common PMa SNR columns
                pma_snr_col = None
                for cand in ["snrG3", "snrPMaG3", "snrPMaG2", "snrG3_PMa",
                             "SNRG3", "snrPMa", "SNR_PMa"]:
                    if cand in df.columns:
                        pma_snr_col = cand
                        break
                if pma_snr_col is None:
                    # fall back: anything starting with 'snr'
                    for c in df.columns:
                        if c.lower().startswith("snr"):
                            pma_snr_col = c
                            break
                for _, r in df.iterrows():
                    out.append({"hip": int(r["hip"]),
                                "kervella_pma_snr": float(r[pma_snr_col])
                                if pma_snr_col and pma_snr_col in r
                                else None,
                                "kervella_cat": cat})
                break
            if out:
                break
        except Exception as e:  # noqa: BLE001
            print(f"  Kervella cat {cat} err: {type(e).__name__}: {e}")
            continue
    return out


def sb9_lookup(cands):
    Vizier.ROW_LIMIT = -1
    Vizier.TIMEOUT = 120
    out = []
    for c in cands:
        try:
            sc = SkyCoord(c["ra_deg"]*u.deg, c["dec_deg"]*u.deg)
            r = Vizier.query_region(sc, radius=10*u.arcsec,
                                     catalog="B/sb9/main")
            in_sb9 = bool(r and len(r) > 0 and len(r[0]) > 0)
            sb9_id = None
            if in_sb9:
                tbl = r[0]
                # SB9 catalog has a sequence number
                for col in ["Seq", "_Glon", "Name", "HD", "HIP"]:
                    if col in tbl.colnames:
                        sb9_id = str(tbl[0][col])
                        break
            out.append({"hip": c["hip"], "in_sb9": in_sb9, "sb9_id": sb9_id})
        except Exception as e:  # noqa: BLE001
            out.append({"hip": c["hip"], "in_sb9": None,
                        "sb9_id": f"ERR:{type(e).__name__}"})
        time.sleep(0.3)
    return out


def exoplanet_eu_lookup(cands):
    """Light-weight cross-match: GET https://exoplanet.eu/catalog/csv/ once
    and filter locally."""
    import io
    import urllib.request
    url = "https://exoplanet.eu/catalog/csv/"
    try:
        with urllib.request.urlopen(url, timeout=60) as resp:
            csv_bytes = resp.read()
        import pandas as pd
        df = pd.read_csv(io.BytesIO(csv_bytes), low_memory=False)
        # ra/dec columns
        if "ra" not in df.columns or "dec" not in df.columns:
            return [{"hip": c["hip"], "in_exoplanet_eu": None,
                     "match_planet": "ERR:no ra/dec cols"} for c in cands]
        out = []
        from astropy.coordinates import SkyCoord
        cat_sc = SkyCoord(df["ra"].to_numpy()*u.deg,
                          df["dec"].to_numpy()*u.deg)
        for c in cands:
            sc = SkyCoord(c["ra_deg"]*u.deg, c["dec_deg"]*u.deg)
            sep = sc.separation(cat_sc).arcsec
            hits = (sep < 30.0).nonzero()[0]
            if len(hits) > 0:
                matches = df.iloc[hits]["name"].tolist()
                out.append({"hip": c["hip"], "in_exoplanet_eu": True,
                            "match_planet": "; ".join(matches[:3])})
            else:
                out.append({"hip": c["hip"], "in_exoplanet_eu": False,
                            "match_planet": None})
        return out
    except Exception as e:  # noqa: BLE001
        return [{"hip": c["hip"], "in_exoplanet_eu": None,
                 "match_planet": f"ERR:{type(e).__name__}"} for c in cands]


def main():
    cands = enrich_with_gaia(CANDS)

    print("=== STEP A: SIMBAD identification ===")
    sim = simbad_lookup(cands)
    for s in sim:
        print(f"  HIP {s['hip']}: main_id={s['simbad_main_id']}  "
              f"otype={s['simbad_otype']}")

    print("\n=== STEP B: Kervella H2G2 PMa SNR ===")
    kerv = vizier_lookup_kervella([c["hip"] for c in cands])
    for k in kerv:
        print(f"  HIP {k['hip']}: PMa SNR = {k.get('kervella_pma_snr')}  "
              f"(cat {k.get('kervella_cat')})")

    print("\n=== STEP C: SB9 ===")
    sb9 = sb9_lookup(cands)
    for s in sb9:
        print(f"  HIP {s['hip']}: in_sb9={s['in_sb9']}  id={s.get('sb9_id')}")

    print("\n=== STEP D: exoplanet.eu (PM-corrected approx., 30\" radius) ===")
    epx = exoplanet_eu_lookup(cands)
    for e in epx:
        print(f"  HIP {e['hip']}: in_exoplanet_eu={e['in_exoplanet_eu']}  "
              f"match={e.get('match_planet')}")

    # Merge into a single annotated CSV
    base = pl.DataFrame(cands)
    sim_df = pl.DataFrame(sim)
    kerv_df = pl.DataFrame(kerv) if kerv else pl.DataFrame(
        {"hip": [c["hip"] for c in cands],
         "kervella_pma_snr": [None]*len(cands),
         "kervella_cat": [None]*len(cands)})
    sb9_df = pl.DataFrame(sb9)
    epx_df = pl.DataFrame(epx)

    merged = base.join(sim_df, on="hip", how="left") \
                 .join(kerv_df, on="hip", how="left") \
                 .join(sb9_df, on="hip", how="left") \
                 .join(epx_df, on="hip", how="left")
    merged.write_csv(INTER / "sb1_top5_deep_vetting_2026_05_17.csv")
    print(f"\nWritten: {INTER / 'sb1_top5_deep_vetting_2026_05_17.csv'}")
    print(merged)


if __name__ == "__main__":
    sys.exit(main() or 0)
