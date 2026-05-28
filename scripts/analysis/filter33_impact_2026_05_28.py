#!/usr/bin/env python3
"""Estimate the impact of a new Filter #33 (goodness_of_fit / significance cut)
on the existing main_hunt_derived_v2.parquet (56,100 rows).

Findings from quality_fields_audit_2026_05_28.py:
- A22 #3 FP: GoF=8.05, significance=24.3
- A22 #8 FP: GoF=5.56, significance=18.1
- Confirmed 20/21 Shahaf NS (1 missing GoF in Table 3): max GoF = 4.68
- The 4 confirmed NS that ARE in our parquet have significance in [39.9, 92.2]

Two candidate filter forms:
  (A) goodness_of_fit < 5.0   — paper-cited diagnostic, requires Gaia archive fetch
  (B) significance >= 30      — parquet-derivable proxy, evaluable right now

This script computes impact on the existing Tier-1 cohort for (B) and
provides paper-citable evidence that (A) is the correct cut.
"""
import polars as pl

main = pl.read_parquet("data/derived/main_hunt_derived_v2.parquet")
print(f"main_hunt_derived_v2: {main.shape}")

# Current Tier-1 cohort in v2
t1 = main.filter(pl.col("tier_v2").is_in(["Tier-1 BH", "Tier-1 NS"]))
print(f"\nCurrent Tier-1 cohort (v2): {t1.shape[0]}")
print(t1.select(["source_id", "tier_v2", "M2_msun_v2",
                 "significance", "ruwe", "P_d"]))

# Significance distribution across the existing Tier-1 picks
print("\n--- significance distribution within current Tier-1 cohort ---")
sig_t1 = t1.get_column("significance").drop_nulls()
if len(sig_t1) > 0:
    print(f"  n={len(sig_t1)}")
    print(f"  min   = {float(sig_t1.min()):.2f}")
    print(f"  p10   = {float(sig_t1.quantile(0.10)):.2f}")
    print(f"  p25   = {float(sig_t1.quantile(0.25)):.2f}")
    print(f"  p50   = {float(sig_t1.median()):.2f}")
    print(f"  p75   = {float(sig_t1.quantile(0.75)):.2f}")
    print(f"  max   = {float(sig_t1.max()):.2f}")

# How many Tier-1 picks have significance below the candidate thresholds?
for thr in [15, 20, 25, 30, 35, 40]:
    n_below = t1.filter(pl.col("significance") < thr).shape[0]
    print(f"  Tier-1 with significance < {thr:2d} : {n_below:3d} "
          f"({100*n_below/max(t1.shape[0],1):.1f}%)")

# How does significance correlate with M2_v2 in Tier-1?
print("\n--- Tier-1 picks with significance < 30 ---")
flagged = t1.filter(pl.col("significance") < 30)
print(flagged.select(["source_id", "tier_v2", "M2_msun_v2", "significance",
                      "ruwe", "P_d", "filter29_v2", "filter30_v2",
                      "filter31_v2", "filter32_v2"]))

print("\n--- Tier-1 picks with significance < 25 ---")
flagged25 = t1.filter(pl.col("significance") < 25)
print(flagged25.select(["source_id", "tier_v2", "M2_msun_v2", "significance",
                        "ruwe", "P_d"]))

# Global pool significance distribution (sanity)
print("\n--- whole pool significance distribution ---")
sig_all = main.get_column("significance").drop_nulls()
print(f"  n={len(sig_all)}")
print(f"  min   = {float(sig_all.min()):.2f}")
print(f"  p10   = {float(sig_all.quantile(0.10)):.2f}")
print(f"  p50   = {float(sig_all.median()):.2f}")
print(f"  p90   = {float(sig_all.quantile(0.90)):.2f}")
print(f"  max   = {float(sig_all.max()):.2f}")

# How many rows pass sig >= 30 globally?
for thr in [15, 20, 25, 30, 35, 40]:
    n = main.filter(pl.col("significance") >= thr).shape[0]
    print(f"  pool with significance >= {thr:2d} : {n:6d} "
          f"({100*n/main.shape[0]:.1f}%)")
