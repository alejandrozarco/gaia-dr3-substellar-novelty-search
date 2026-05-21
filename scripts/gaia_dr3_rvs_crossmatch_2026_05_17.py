"""(A) Gaia DR3 RVS / per-transit RV cross-match for our pools.

Three Gaia DR3 RV-time-series tables exist:

  (1) gaiadr3.epoch_radial_velocity         — per-transit RVs for RV-standards
                                              (~~370 stars; the only place DR3
                                               publishes per-epoch RVs)
  (2) gaiadr3.vari_rad_vel_statistics       — per-source RV time-series summary
                                              statistics for ~~1,800 sources
                                              (mostly LPVs but some F/G/K too)
  (3) gaiadr3.rvs_mean_spectrum             — the mean RVS spectrum
                                              (~~1M sources, used by activity
                                              and Halpha studies)

Plus the FPR analogues:

  (4) gaiafpr.vari_epoch_radial_velocity    — ~~9.5k LPV per-transit RVs
  (5) gaiafpr.vari_rad_vel_statistics       — ~~9.5k LPV per-source summary

What we do:

  - Cross-match all 5 tables against our 14 headline candidates.
  - Cross-match all 5 tables against the 3,049 SB1 pool.
  - For any hit in (1), (2), (4), or (5), pull the per-epoch / summary data.

A hit in (1) for any of our candidates would be a true smoking-gun
result: independent Gaia time-series RV on Gaia's own wavelength scale.
"""
from __future__ import annotations

import sys
from pathlib import Path

import polars as pl
from astroquery.gaia import Gaia

ROOT = Path("/tmp/gaia-novelty-publication")
INTER = ROOT / "data" / "intermediate"
INTER.mkdir(parents=True, exist_ok=True)


def build_id_list() -> tuple[pl.DataFrame, pl.DataFrame]:
    """Return (headline_14, sb1_pool_3049)."""
    headline = pl.read_csv(ROOT / "novelty_candidates.csv").select(
        ["name", "gaia_dr3_source_id"]
    ).rename({"gaia_dr3_source_id": "source_id"}).drop_nulls("source_id")

    sb1 = pl.read_csv(INTER / "nss_sb1_pool_with_m2_2026_05_17.csv").select(
        ["source_id"]
    ).drop_nulls()
    return headline, sb1


def xmatch_table(table_name: str, source_ids: list[int],
                 desc: str, max_chunk: int = 3000):
    """Cross-match a list of source_ids against table_name.source_id."""
    chunks = []
    for i in range(0, len(source_ids), max_chunk):
        sub = source_ids[i:i+max_chunk]
        ids = ",".join(str(int(x)) for x in sub)
        q = f"SELECT source_id FROM {table_name} WHERE source_id IN ({ids})"
        try:
            res = Gaia.launch_job_async(q).get_results().to_pandas()
            chunks.append(res)
        except Exception as e:  # noqa: BLE001
            print(f"  {table_name} chunk {i//max_chunk} err: "
                  f"{type(e).__name__}: {e}")
            chunks.append(None)
    n_hit = sum(len(c) for c in chunks if c is not None)
    print(f"  {table_name}: {n_hit} hits / {len(source_ids)} probed  ({desc})")
    if n_hit > 0:
        import pandas as pd
        ok = [c for c in chunks if c is not None]
        merged = pl.from_pandas(pd.concat(ok, ignore_index=True))
        return n_hit, merged
    return n_hit, pl.DataFrame({"source_id": []})


def pull_epoch_rv_for_hits(table_name: str, hits: pl.DataFrame, label: str):
    """For sources that hit the time-series table, pull the actual epoch RV."""
    if hits.is_empty():
        return
    ids = ",".join(str(int(x)) for x in hits["source_id"].to_list())
    q = f"SELECT * FROM {table_name} WHERE source_id IN ({ids})"
    print(f"  pulling full RV time-series for {len(hits)} {label} hits…")
    try:
        df = pl.from_pandas(
            Gaia.launch_job_async(q).get_results().to_pandas()
        )
        out = INTER / f"rv_timeseries_{label.replace(' ', '_').lower()}.csv"
        df.write_csv(out)
        print(f"  -> {out}: {len(df)} rows")
    except Exception as e:  # noqa: BLE001
        print(f"  pull-failed: {type(e).__name__}: {e}")


def main():
    headline, sb1 = build_id_list()
    print(f"Headline candidates: {len(headline)}")
    print(f"SB1 pool size: {len(sb1)}")

    head_ids = [int(x) for x in headline["source_id"].to_list()]
    sb1_ids = [int(x) for x in sb1["source_id"].to_list()]

    tables = [
        ("gaiadr3.epoch_radial_velocity",
         "DR3 per-transit RVs (RV-standards subset, ~~370 stars)"),
        ("gaiadr3.vari_rad_vel_statistics",
         "DR3 per-source RV summary (~~1,800 sources)"),
        ("gaiafpr.vari_epoch_radial_velocity",
         "FPR LPV per-transit RVs (~~9,500 LPVs)"),
        ("gaiafpr.vari_rad_vel_statistics",
         "FPR LPV per-source RV summary"),
        ("gaiadr3.rvs_mean_spectrum",
         "DR3 mean RVS spectrum (~~1M sources)"),
    ]

    print("\n=== Headline candidates (14) ===")
    head_results = {}
    for tbl, desc in tables:
        n, hits = xmatch_table(tbl, head_ids, desc, max_chunk=500)
        head_results[tbl] = (n, hits)
        if n > 0 and "rvs_mean_spectrum" not in tbl:
            pull_epoch_rv_for_hits(tbl, hits, f"headline_{tbl.split('.')[-1]}")

    print("\n=== SB1 pool (3,049 sources) ===")
    sb1_results = {}
    for tbl, desc in tables:
        n, hits = xmatch_table(tbl, sb1_ids, desc, max_chunk=500)
        sb1_results[tbl] = (n, hits)
        if n > 0 and "rvs_mean_spectrum" not in tbl:
            pull_epoch_rv_for_hits(tbl, hits, f"sb1_{tbl.split('.')[-1]}")

    print("\n=== SUMMARY ===")
    rows = []
    for tbl, desc in tables:
        rows.append({
            "table": tbl,
            "description": desc,
            "headline_hits": head_results[tbl][0],
            "sb1_pool_hits": sb1_results[tbl][0],
        })
    pl.DataFrame(rows).write_csv(INTER / "gaia_dr3_rvs_summary_2026_05_17.csv")
    print(pl.DataFrame(rows))


if __name__ == "__main__":
    sys.exit(main() or 0)
