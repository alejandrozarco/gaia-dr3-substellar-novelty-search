"""Pipeline v11: Filter #29 — Gaia SB2/SB2C double-lined rejection.

Motivation (the independent negative-control set, 2026-05-17):
  An out-of-sample negative control of 24 leak-free stellar imposters
  (18 with Gaia DR3 SB2/SB2C solutions + 6 APOGEE SB2) measured the
  cascade's specificity at only 0.33 (Gaia-SB2 tier) / 0.25 (combined).
  Of 18 escapes, every single one is an SB2 stellar binary — the cascade
  had NO filter on the Gaia spectroscopic-binary channel. One escape,
  HD 76078, had reached the headline candidate list as a false positive.

Filter #29 closes this blind spot.

Rule:
  Reject any pool source that ALSO carries a Gaia DR3 `nss_two_body_orbit`
  solution of type SB2 or SB2C. A double-lined solution publishes both K1
  AND K2 (the secondary's RV reflex), which is only measurable if the
  secondary is luminous — i.e. a star, not a substellar (brown-dwarf /
  planetary) companion. A measured K2 is therefore a direct stellar-secondary
  detection, independent of the astrometric photocentre mass estimate the
  cascade mines.

Why this is a legitimate categorical filter, not a tuned threshold:
  It is motivated by physics (double-lined ⇒ luminous secondary ⇒ stellar),
  not fit to the control set's statistics. No threshold is tuned. However,
  per the negative-control protocol, once Filter #29 is added the existing
  negative set is "spent" as a design input — re-measuring specificity needs
  a fresh independent negative set (or Gaia DR4 epoch RVs). Filter #29's
  effect on the existing set is deterministic: it rejects all 18 Gaia-SB2
  negatives by construction.

Independence note:
  The Gaia SB2 channel is NOT on the cascade's FILTER_BLOCKLIST and was never
  consulted by any prior filter or RV-joint-fit step. Adding it as a filter is
  consistent: the channel is now a filter input, so it can no longer be used
  to *label* future negatives — future negative sets must use APOGEE-SB2 /
  literature-SB2 / resolved-companion labels (Tiers A1/B/C), or DR4.
"""
from __future__ import annotations

import sys
from pathlib import Path

import polars as pl

ROOT = Path("/tmp/gaia-novelty-publication")

# Solution types that constitute a double-lined (luminous-secondary) detection.
SB2_SOLUTION_TYPES = {"SB2", "SB2C"}


def has_gaia_sb2(source_id: int, sb2_source_ids: set[int]) -> bool:
    """True if the source carries a Gaia DR3 SB2/SB2C solution."""
    return int(source_id) in sb2_source_ids


def filter29_sb2_rejection(row: dict, sb2_source_ids: set[int]) -> bool:
    """Filter #29: return True if the row PASSES (i.e. is NOT an SB2 binary).

    A source that carries a Gaia SB2/SB2C solution FAILS this filter
    (returns False) — it is a double-lined stellar binary, not a substellar
    candidate.
    """
    return not has_gaia_sb2(row.get("source_id"), sb2_source_ids)


def load_sb2_source_ids() -> set[int]:
    """Load the set of pool source_ids with Gaia SB2/SB2C solutions.

    Built by scripts/build_negative_control_2026_05_17.py (Tier A2). For a
    full-pipeline run this would be a live ADQL query:
        SELECT source_id FROM gaiadr3.nss_two_body_orbit
        WHERE nss_solution_type IN ('SB2','SB2C')
    """
    p = ROOT / "data" / "intermediate" / "tierA2_gaia_sb2_in_pool.csv"
    if not p.exists():
        return set()
    df = pl.read_csv(p)
    return set(int(x) for x in df["source_id"].to_list())


def apply_filter29_to_pool() -> dict:
    """Apply Filter #29 across the v2 pool; report how many it rejects and
    whether any headline candidates are affected."""
    sb2_ids = load_sb2_source_ids()
    pool = pl.read_csv(ROOT / "v2_scan_full_pool.csv", infer_schema_length=20000)

    flagged = pool.filter(pl.col("source_id").is_in(list(sb2_ids)))
    n_flagged = len(flagged)

    # How many of these were SURVIVOR/CORROBORATED/FLAG (i.e. would have leaked)?
    leaked = flagged.filter(~pl.col("v2_verdict").str.starts_with("REJECTED"))

    return {
        "n_sb2_in_pool": n_flagged,
        "n_would_have_leaked": len(leaked),
        "leaked_source_ids": leaked["source_id"].to_list(),
    }


def main():
    sb2_ids = load_sb2_source_ids()
    print(f"Filter #29 (Gaia SB2/SB2C rejection)")
    print(f"  SB2/SB2C source_ids loaded: {len(sb2_ids)}")

    res = apply_filter29_to_pool()
    print(f"  SB2 sources in v2 pool: {res['n_sb2_in_pool']}")
    print(f"  Of those, would have leaked (not already rejected): "
          f"{res['n_would_have_leaked']}")
    print(f"  Filter #29 newly rejects these source_ids:")
    for sid in res["leaked_source_ids"]:
        print(f"    {sid}")

    # Confirm HD 76078 is now rejected
    hd76078 = 1017645329162554752
    print(f"\n  HD 76078 (Gaia {hd76078}) rejected by Filter #29: "
          f"{has_gaia_sb2(hd76078, sb2_ids)}")


if __name__ == "__main__":
    sys.exit(main() or 0)
