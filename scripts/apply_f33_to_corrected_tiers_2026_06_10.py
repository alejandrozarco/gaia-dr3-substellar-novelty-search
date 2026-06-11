#!/usr/bin/env python
"""Propagate the F#33 down-tier into the M1-corrected tiers (2026-06-10).

F#33 (2026-05-31) down-tiers AstroSpectroSB1 solutions whose Gaia NSS period is
flagged non-significant (flags bit 13) — but the re-derivation only wrote the
down-tier into the raw-M1 `tier_v2` column, never into `tier_v2_corrected`.
The 2026-06-10 project review (docs/reports/project_review_2026_06_10.json)
found 41 main + 4 relaxed corrected-Tier-1 NS carrying filter33_v2 == 'FLAG'.

This script adds a `tier_v2_corrected_f33` column to both _M1corrected
parquets: identical to tier_v2_corrected except that corrected-Tier-1 rows
with filter33_v2 == 'FLAG' become 'Tier-2 (NSS period non-significant —
needs corroboration)'. Original columns are left untouched (audit trail).
The DR4 rehunt diff baseline should use this column.
"""
import pandas as pd

DOWNTIER = "Tier-2 (NSS period non-significant — needs corroboration)"
FILES = [
    "data/derived/main_hunt_derived_v2_M1corrected.parquet",
    "data/derived/main_hunt_derived_v2_relaxed_M1corrected.parquet",
]

for path in FILES:
    df = pd.read_parquet(path)
    is_t1 = df["tier_v2_corrected"].astype(str).str.startswith("Tier-1")
    flagged = is_t1 & (df["filter33_v2"].astype(str) == "FLAG")
    df["tier_v2_corrected_f33"] = df["tier_v2_corrected"].where(~flagged, DOWNTIER)
    df.to_parquet(path, index=False)
    before = df.loc[is_t1, "tier_v2_corrected"].value_counts().to_dict()
    after = df[df["tier_v2_corrected_f33"].astype(str).str.startswith("Tier-1")][
        "tier_v2_corrected_f33"
    ].value_counts().to_dict()
    print(f"{path}\n  down-tiered: {int(flagged.sum())}\n  Tier-1 before: {before}\n  Tier-1 after:  {after}")
