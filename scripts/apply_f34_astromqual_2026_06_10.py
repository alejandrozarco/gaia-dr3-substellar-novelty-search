#!/usr/bin/env python
"""Apply the F#34 astrometric-quality caution flag to the M1-corrected parquets
(2026-06-10; the CANDIDATES.md 'no global RUWE gate' tracked follow-up).

Merges the freshly fetched NSS goodness_of_fit (F2) + ipd_frac_multi_peak
(/tmp/f2_ipd_fetch_2026_06_10.csv — 1,251 candidate-tier sources, archived to
docs/reports/f2_ipd_fetch_2026_06_10.csv) into the three _M1corrected parquets
as `nss_gof_f2` / `ipd_frac_multi_peak`, then writes `filter34_v2` +
`filter34_reason_v2` via consumer_v2.filter34_astromqual. A caution flag only —
no tier changes. Non-candidate rows lack F2/ipd and get the flag from RUWE
alone or 'NO_DATA' (loud, per the #117 lesson).
"""
import sys
import pandas as pd

sys.path.insert(0, "scripts/streaming/v2_corrected")
from consumer_v2 import filter34_astromqual

fetch = pd.read_csv("docs/reports/f2_ipd_fetch_2026_06_10.csv",
                    dtype={"source_id": "int64"})
fetch = fetch.rename(columns={"goodness_of_fit": "nss_gof_f2"})

FILES = [
    "data/derived/main_hunt_derived_v2_M1corrected.parquet",
    "data/derived/main_hunt_derived_v2_relaxed_M1corrected.parquet",
    "data/derived/main_hunt_derived_v2_alt_M1corrected.parquet",
]

for path in FILES:
    df = pd.read_parquet(path)
    df = df.drop(columns=[c for c in ("nss_gof_f2", "ipd_frac_multi_peak",
                                      "filter34_v2", "filter34_reason_v2")
                          if c in df.columns])
    key = ["source_id", "nss_solution_type"]
    sub = fetch[key + ["nss_gof_f2", "ipd_frac_multi_peak"]].drop_duplicates(key)
    df = df.merge(sub, on=key, how="left")
    res = df.apply(lambda r: filter34_astromqual(
        gof_f2=r.get("nss_gof_f2"),
        ipd_frac_multi_peak=r.get("ipd_frac_multi_peak"),
        ruwe=r.get("ruwe")), axis=1)
    df["filter34_v2"] = [v for v, _ in res]
    df["filter34_reason_v2"] = [why for _, why in res]
    df.to_parquet(path, index=False)

    tiers = df.get("tier_v2_corrected_f33", df["tier_v2_corrected"]).astype(str)
    t1 = df[tiers.str.startswith("Tier-1")]
    print(f"{path}")
    print(f"  pool F#34: {df['filter34_v2'].value_counts().to_dict()}")
    print(f"  Tier-1 F#34: {t1['filter34_v2'].value_counts().to_dict()}")
    fl = t1[t1["filter34_v2"] == "FLAG"]
    for _, r in fl.iterrows():
        print(f"    FLAG Tier-1: {r['source_id']}  {r['filter34_reason_v2']}"
              f"  (F2={r['nss_gof_f2']}, ruwe={r['ruwe']:.2f})")
