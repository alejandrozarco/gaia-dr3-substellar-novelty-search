"""Simpler annotation: drop the Vizier bulk Kervella fetch, just combine the
existing cascade + deep-vetting outputs into one row-per-candidate CSV.

Output: data/intermediate/sb1_top5_full_2026_05_17.csv
"""
from __future__ import annotations

import sys
from pathlib import Path

import polars as pl

INTER = Path("/tmp/gaia-novelty-publication/data/intermediate")

TOP5_HIPS = [84737, 84506, 8278, 63111, 46631]
TOP5_NAMES = {84737: "HD 156239", 84506: "HD 156342",
              8278: "HD 11042",  63111: "HD 112243",
              46631: "HD 82455"}


def main():
    annot = pl.read_csv(INTER / "nss_sb1_cascade_annotated_2026_05_17.csv")
    vet = pl.read_csv(INTER / "sb1_top5_deep_vetting_2026_05_17.csv")

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

    vet_sub = vet.select([
        "hip", "simbad_main_id", "simbad_otype",
        "in_exoplanet_eu", "match_planet"
    ])
    sub = sub.join(vet_sub, on="hip", how="left")

    sub = sub.with_columns(
        (1000.0 / pl.col("parallax")).alias("dist_pc_naive")
    )
    sub = sub.with_columns(
        pl.col("hip").map_elements(lambda h: TOP5_NAMES.get(int(h), f"HIP {int(h)}"),
                                     return_dtype=pl.Utf8).alias("name")
    )

    def tier(r):
        m2 = r["m2_marg_med_mjup"]
        ruwe = r["ruwe"]
        chi = r["chisq"]
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
          .map_elements(tier, return_dtype=pl.Utf8)
          .alias("class")
    )

    out_path = INTER / "sb1_top5_full_2026_05_17.csv"
    sub.write_csv(out_path)
    print(f"Wrote {out_path}")
    print(sub.sort("m2_marg_med_mjup").select([
        "name", "hip", "source_id",
        "phot_g_mean_mag", "ruwe", "period", "eccentricity",
        "semi_amplitude_primary",
        "m2_face_mjup", "m2_marg_med_mjup",
        "m2_marg_1sig_lo_mjup", "m2_marg_1sig_hi_mjup",
        "chisq", "hgca_tier", "in_sb9", "in_exoplanet_eu",
        "simbad_main_id", "simbad_otype", "dist_pc_naive", "class",
    ]))


if __name__ == "__main__":
    sys.exit(main() or 0)
