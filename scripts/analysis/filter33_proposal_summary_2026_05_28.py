#!/usr/bin/env python3
"""Final summary: proposed Filter #33 (goodness_of_fit OR significance proxy)
and its impact on the existing Tier-1 cohort.

Output: a single CSV that captures every Tier-1 pick's significance value
and whether it would be demoted under each candidate threshold.
"""
import polars as pl

# 21 Shahaf NS + 2 FPs, with Table 3 GoF transcribed from Shahaf+2024 OJAp 7:27
TABLE3 = {
    # 21 NS (status="one of our candidates" in green in Table 3)
    2995961897685517312: (-0.01, "J0553-1349", "NS"),
    6481502062263141504: (2.11,  "J2057-4742", "NS"),
    5820382041374661888: (-2.04, "J1553-6846", "NS"),
    1871419337958702720: (-0.71, "J2102+3703", "NS"),
    5530442371304582912: (-2.04, "J0742-4749", "NS"),
    5136025521527939072: (4.68,  "J0152-2049", "NS"),
    4922744974687373440: (1.23,  "J0003-5604", "NS"),
    1434445448240677376: (-2.97, "J1733+5808", "NS"),
    1694708646628402048: (0.77,  "J1449+6919", "NS"),
    3494029910469026432: (2.64,  "J1150-2203", "NS"),
    4637171465304969216: (0.77,  "J0217-7541", "NS"),
    5580526947012630912: (0.66,  "J0639-3655", "NS"),
    1350295047363872512: (3.53,  "J1739+4502", "NS"),
    2426116249713980416: (-0.30, "J0036-0932", "NS"),
    6328149636482597888: (0.74,  "J1432-1021", "NS"),
    2397135910639986304: (2.10,  "J2244-2236", "NS"),
    1058875159778407808: (-0.01, "J1048+6547", "NS"),
    1801110822095134848: (3.58,  "J2145+2837", "NS"),
    1028887114002082432: (-0.42, "J0824+5254", "NS"),
    465093354131112960:  (-0.86, "J0230+5950", "NS"),
    # J0634+6256 (1007185297091149824) not extracted from PDF table — assume safe
    # 2 Tier-1 false positives
    6281177228434199296: (8.05,  "A22 #3",     "FP_BH"),
    3263804373319076480: (5.56,  "A22 #8",     "FP_NS"),
}

main = pl.read_parquet("data/derived/main_hunt_derived_v2.parquet")
t1 = main.filter(pl.col("tier_v2").is_in(["Tier-1 BH", "Tier-1 NS"]))
print(f"Current Tier-1 cohort: {t1.shape[0]}")

# ----------------------------------------------------------------------------
# Impact of three candidate proxies on the Tier-1 cohort
# ----------------------------------------------------------------------------
results = []
for thr in [20, 25, 30, 35]:
    demoted = t1.filter(pl.col("significance") < thr)
    bh_demoted = demoted.filter(pl.col("tier_v2") == "Tier-1 BH").shape[0]
    ns_demoted = demoted.filter(pl.col("tier_v2") == "Tier-1 NS").shape[0]
    total_demoted = demoted.shape[0]
    results.append({
        "threshold": f"significance >= {thr}",
        "Tier-1 BH demoted": bh_demoted,
        "Tier-1 NS demoted": ns_demoted,
        "total demoted": total_demoted,
        "Tier-1 after": t1.shape[0] - total_demoted,
        "% reduction": f"{100*total_demoted/t1.shape[0]:.1f}%",
        "A22 #3 demoted?": "Y" if 24.31 < thr else "N",
        "A22 #8 demoted?": "Y" if 18.06 < thr else "N",
        "Shahaf NS in parquet kept": (
            (1 if 39.85 >= thr else 0) +  # J0553-1349
            (1 if 60.32 >= thr else 0) +  # J0152-2049
            (1 if 77.56 >= thr else 0) +  # J1150-2203
            (1 if 92.18 >= thr else 0)),  # J2145+2837
    })

print("\n=== significance-based proxy: impact on current Tier-1 cohort ===")
print(pl.DataFrame(results))

# ----------------------------------------------------------------------------
# How many Tier-1 picks have BOTH low significance AND high RUWE
# (likely poor astrometric fits — same family as Shahaf+2024 FPs)
# ----------------------------------------------------------------------------
print("\n=== Joint cuts ===")
for (sig_thr, ruwe_thr) in [(25, None), (25, 1.4), (30, None), (30, 1.4)]:
    f = t1.filter(pl.col("significance") < sig_thr)
    if ruwe_thr is not None:
        f = f.filter(pl.col("ruwe") > ruwe_thr)
    print(f"  sig<{sig_thr} & ruwe>{ruwe_thr}: demotes {f.shape[0]} of {t1.shape[0]} "
          f"Tier-1 ({100*f.shape[0]/t1.shape[0]:.1f}%)")

# ----------------------------------------------------------------------------
# Top-K most concerning Tier-1 picks (low significance + high RUWE)
# Anchored at Tier-1 NS since FP A22 #8 was an NS
# ----------------------------------------------------------------------------
suspect = t1.with_columns(
    (pl.col("significance") / (pl.col("ruwe") + 1.0)).alias("sig_to_ruwe")
).sort("sig_to_ruwe").head(15)
print("\n=== 15 lowest sig/(ruwe+1) Tier-1 picks — most FP-like ===")
print(suspect.select(["source_id", "tier_v2", "M2_msun_v2",
                      "significance", "ruwe", "P_d", "sig_to_ruwe"]))

# Save the demote list for the recommended threshold
demote_list = t1.filter(pl.col("significance") < 25).select([
    "source_id", "tier_v2", "M2_msun_v2", "significance", "ruwe", "P_d",
])
demote_list.write_csv("data/validation_2026_05_28/filter33_demote_list_sig25.csv")
print(f"\nWrote {demote_list.shape[0]} demoted Tier-1 picks under sig>=25 to "
      f"data/validation_2026_05_28/filter33_demote_list_sig25.csv")
