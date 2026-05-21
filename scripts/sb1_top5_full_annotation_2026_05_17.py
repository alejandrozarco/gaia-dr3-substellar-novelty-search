"""Build the full annotation row for the 5 SB1 HGCA-corroborated candidates.

Pulls:
  - Period, eccentricity, K_1, K_1_error, significance, t_periastron from the
    SB1 pool CSV (nss_sb1_pool_with_m2_2026_05_17.csv)
  - HGCA chi^2 + main_id from the cascade CSV
  - Kervella H2G2 PMa SNR via the proper table J/A+A/657/A7/tableb2 (HIP+G3)
  - Distance from parallax (1000/plx)
  - Final tentative-class assignment

Output: data/intermediate/sb1_top5_full_2026_05_17.csv (one row per candidate
with all columns the headline novelty_candidates.csv uses).
"""
from __future__ import annotations

import sys
from pathlib import Path

import polars as pl
from astroquery.vizier import Vizier

ROOT = Path("/tmp/gaia-novelty-publication")
INTER = ROOT / "data" / "intermediate"

TOP5_HIPS = [84737, 84506, 8278, 63111, 46631]
TOP5_NAMES = {84737: "HD 156239", 84506: "HD 156342",
              8278: "HD 11042",  63111: "HD 112243",
              46631: "HD 82455"}


def kervella_pma_proper(hips: list[int]) -> pl.DataFrame:
    """Kervella+2022 H2G2 PMa: J/A+A/657/A7.
    Table b1 = HIP+DR3, table b2 = HIP+DR3 corrected.
    """
    Vizier.ROW_LIMIT = -1
    Vizier.TIMEOUT = 180

    for cat in ["J/A+A/657/A7"]:
        try:
            tables = Vizier.get_catalogs(cat)
        except Exception as e:  # noqa: BLE001
            print(f"  Kervella {cat} err: {type(e).__name__}: {e}")
            continue
        for ti, t in enumerate(tables):
            cols_lower = {c.lower(): c for c in t.colnames}
            if "hip" not in cols_lower:
                continue
            print(f"  Kervella table[{ti}] cols: {t.colnames[:20]}…")
            df = t.to_pandas()
            df = df.rename(columns={cols_lower["hip"]: "hip"})
            # parse HIP safely
            df["hip"] = (df["hip"]
                          .astype(str)
                          .str.extract(r"(\d+)")[0]
                          .fillna("0").astype(int))
            df = df[df["hip"].isin(hips)].copy()
            if df.empty:
                continue
            # find PMa SNR column
            for cand in ["snrG3", "SNRG3", "snrPMaG3", "snrPMa", "SNR_PMa"]:
                if cand in df.columns:
                    df["kerv_pma_snr"] = df[cand]
                    break
            if "kerv_pma_snr" not in df.columns:
                # fallback: any column containing 'snr'
                for c in df.columns:
                    if "snr" in c.lower():
                        df["kerv_pma_snr"] = df[c]
                        print(f"  using fallback PMa SNR column '{c}'")
                        break
            sub = df[["hip"]].copy()
            sub["kerv_pma_snr"] = df.get("kerv_pma_snr", None)
            return pl.from_pandas(sub.reset_index(drop=True))
    return pl.DataFrame({"hip": [], "kerv_pma_snr": []})


def main():
    pool = pl.read_csv(INTER / "nss_sb1_pool_with_m2_2026_05_17.csv")
    annot = pl.read_csv(INTER / "nss_sb1_cascade_annotated_2026_05_17.csv")

    sub = (annot.filter(pl.col("hip").is_in(TOP5_HIPS))
                .select(["source_id", "hip", "ra", "dec",
                         "phot_g_mean_mag", "bp_rp",
                         "parallax", "parallax_error",
                         "ruwe", "non_single_star", "ipd_frac_multi_peak",
                         "period", "eccentricity",
                         "semi_amplitude_primary",
                         "semi_amplitude_primary_error",
                         "significance",
                         "mass_flame",
                         "f_M_mjup",
                         "m2_face_mjup",
                         "m2_marg_1sig_lo_mjup",
                         "m2_marg_med_mjup",
                         "m2_marg_1sig_hi_mjup",
                         "chisq", "hgca_tier", "in_sb9"]))

    # Kervella PMa
    print("Fetching Kervella H2G2 PMa for top-5 HIPs …")
    kerv = kervella_pma_proper(TOP5_HIPS)
    print(kerv)
    sub = sub.join(kerv, on="hip", how="left")

    # Distance
    sub = sub.with_columns(
        (1000.0 / pl.col("parallax")).alias("dist_pc_naive")
    )

    # Name
    sub = sub.with_columns(
        pl.col("hip").map_elements(lambda h: TOP5_NAMES.get(int(h), f"HIP {int(h)}"),
                                    return_dtype=pl.Utf8).alias("name")
    )

    # Tier
    def tier(r):
        m2 = r.get("m2_marg_med_mjup")
        ruwe = r.get("ruwe")
        chi = r.get("chisq")
        if m2 is None:
            return "UNCLASSIFIED"
        if m2 < 30 and (ruwe is None or ruwe < 2.5) and chi < 30:
            return "STRONG_BD"
        if m2 < 65 and chi < 30:
            return "SOLID_BD_CANDIDATE"
        if m2 < 80:
            return "BORDERLINE_BD"
        return "STELLAR"

    sub = sub.with_columns(
        pl.struct(["m2_marg_med_mjup", "ruwe", "chisq"])
          .map_elements(lambda r: tier(r), return_dtype=pl.Utf8)
          .alias("class")
    )

    sub.write_csv(INTER / "sb1_top5_full_2026_05_17.csv")
    print(f"\nFull annotation -> {INTER / 'sb1_top5_full_2026_05_17.csv'}")
    print(sub.sort("m2_marg_med_mjup"))


if __name__ == "__main__":
    sys.exit(main() or 0)
