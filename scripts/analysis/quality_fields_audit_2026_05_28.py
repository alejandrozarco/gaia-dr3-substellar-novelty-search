#!/usr/bin/env python3
"""Audit NSS/gaia_source quality fields for the 21 Shahaf NS + 2 Tier-1 FPs.

Goal: find a quality cut that demotes A22 #3 (sid 6281177228434199296,
goodness_of_fit=8.05) and A22 #8 (sid 3263804373319076480, goodness_of_fit=5.56)
without dropping any of the 21 confirmed NS (their max GoF in Shahaf+2024
Table 3 is ~4.7).

We do not have nss_two_body_orbit.goodness_of_fit in the parquet, so we
combine: (i) GoF values transcribed from Shahaf+2024 Table 3 (definitive
for these 23 sources), (ii) raw-chunk quality fields (significance, ruwe,
ipd_frac_multi_peak, parallax_over_error, astrometric_excess_noise_sig)
that ARE in the parquet, looking for any correlate of GoF that we already
have.
"""
import glob
import polars as pl

# --- 21 Shahaf NS + 2 FPs, with Table 3 GoF (where available) ---------------
# (source_id, name, G_mag, GoF_table3, ground_truth_class)
SOURCES = [
    # Group B confirmed NS (Shahaf+2024 Table 3, status="one of our candidates")
    (2995961897685517312, "J0553-1349",  13.00, -0.01, "NS"),
    (6481502062263141504, "J2057-4742",  13.58,  2.11, "NS"),
    (5820382041374661888, "J1553-6846",  14.19, -2.04, "NS"),
    (1871419337958702720, "J2102+3703",  13.70, -0.71, "NS"),
    (5530442371304582912, "J0742-4749",  14.60, -2.04, "NS"),
    (5136025521527939072, "J0152-2049",  12.05,  4.68, "NS"),
    (4922744974687373440, "J0003-5604",  14.48,  1.23, "NS"),
    (1434445448240677376, "J1733+5808",  13.65, -2.97, "NS"),
    (1694708646628402048, "J1449+6919",  13.20,  0.77, "NS"),
    (3494029910469026432, "J1150-2203",  12.66,  2.64, "NS"),
    (4637171465304969216, "J0217-7541",  14.01,  0.77, "NS"),
    (5580526947012630912, "J0639-3655",  13.36,  0.66, "NS"),
    (1350295047363872512, "J1739+4502",  13.52,  3.53, "NS"),
    (2426116249713980416, "J0036-0932",  13.02, -0.30, "NS"),
    (6328149636482597888, "J1432-1021",  13.34,  0.74, "NS"),
    (2397135910639986304, "J2244-2236",  13.35,  2.10, "NS"),
    (1058875159778407808, "J1048+6547",  14.52, -0.01, "NS"),
    (1801110822095134848, "J2145+2837",  13.19,  3.58, "NS"),
    (1028887114002082432, "J0824+5254",  13.59, -0.42, "NS"),
    (465093354131112960,  "J0230+5950",  13.10, -0.86, "NS"),
    (1007185297091149824, "J0634+6256",  None,  None,  "NS"),  # not extracted from PDF; will pull from raw

    # Group C false positives (Shahaf+2024 Table 3, status="ruled out by RV follow-up")
    (6281177228434199296, "A22 #3 (FP)", 11.26, 8.05, "FP_BH"),
    (3263804373319076480, "A22 #8 (FP)", 12.67, 5.56, "FP_NS"),
]

# Build polars Series for join.
target_df = pl.DataFrame({
    "source_id": [int(s[0]) for s in SOURCES],
    "name": [s[1] for s in SOURCES],
    "G_table3": [s[2] for s in SOURCES],
    "GoF_table3": [s[3] for s in SOURCES],
    "truth": [s[4] for s in SOURCES],
})

# --- Load raw chunks (have significance, ruwe, ipd_frac_multi_peak, etc.) ---
raw_paths = sorted(glob.glob("data/raw_chunks/main_RA*.parquet"))
raw = pl.concat([pl.read_parquet(p) for p in raw_paths], how="vertical_relaxed")
print(f"raw chunks: {raw.shape}")

# Pick relevant raw fields
raw_q = raw.select([
    pl.col("source_id"),
    pl.col("nss_solution_type"),
    pl.col("significance"),
    pl.col("ruwe"),
    pl.col("ipd_frac_multi_peak"),
    pl.col("astrometric_excess_noise_sig"),
    pl.col("parallax"),
    pl.col("parallax_error"),
    pl.col("phot_g_mean_mag").alias("G"),
])

joined = target_df.join(raw_q, on="source_id", how="left")

# Also pull derived M2_v2 from main parquet so we can label which subset
# of the 21 NS reach Tier-1 in our cascade.
derived = pl.read_parquet("data/derived/main_hunt_derived_v2.parquet").select([
    pl.col("source_id"),
    pl.col("M2_msun_v2"),
    pl.col("class_v2"),
    pl.col("tier_v2"),
    pl.col("filter29_v2"),
    pl.col("filter30_v2"),
    pl.col("filter31_v2"),
    pl.col("filter32_v2"),
    pl.col("nss_parallax"),
    pl.col("nss_parallax_error"),
])

joined = joined.join(derived, on="source_id", how="left")

joined = joined.with_columns([
    (pl.col("parallax") / pl.col("parallax_error")).alias("plx_over_err_gs"),
    (pl.col("nss_parallax") / pl.col("nss_parallax_error")).alias("plx_over_err_nss"),
])

# Print full audit
pl.Config.set_tbl_cols(25)
pl.Config.set_tbl_rows(30)
pl.Config.set_fmt_str_lengths(60)

print("\n=== AUDIT: 21 Shahaf NS + 2 FPs, quality fields ===")
print(joined.select([
    "name", "truth", "GoF_table3",
    "significance", "ruwe", "ipd_frac_multi_peak",
    "plx_over_err_nss",
    "M2_msun_v2", "tier_v2",
]).sort(by=["truth", "name"]))

# Summary stats: NS distribution vs FP separation
ns = joined.filter(pl.col("truth") == "NS")
fp = joined.filter(pl.col("truth").str.starts_with("FP"))

print("\n--- NS (n=21) distributions ---")
for col in ["GoF_table3", "significance", "ruwe", "ipd_frac_multi_peak",
            "plx_over_err_nss", "astrometric_excess_noise_sig"]:
    s = ns.get_column(col).drop_nulls()
    if len(s) == 0:
        continue
    print(f"  {col:30s}  min={float(s.min()):.3f}  p50={float(s.median()):.3f}  "
          f"p90={float(s.quantile(0.9)):.3f}  max={float(s.max()):.3f}  n={len(s)}")

print("\n--- FP (n=2) values ---")
print(fp.select(["name", "GoF_table3", "significance", "ruwe",
                 "ipd_frac_multi_peak", "plx_over_err_nss",
                 "astrometric_excess_noise_sig"]))
