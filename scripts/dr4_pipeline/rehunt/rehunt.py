"""rehunt.py — run the v2 dormant-compact cascade on an (adapted) NSS table.

Day-one DR4 driver. It does NOT fork the science: it imports
``consumer_v2.derive_row_v2`` (the exact production cascade — Corrections A/B/C +
F#29/F#31/F#32/F#33 + the M_1-aware mass-function inversion) and applies it row
by row to a table that ``adapter.py`` has mapped into the canonical schema. The
result is a tiered candidate frame with the same ``tier_v2`` / ``class_v2`` /
``M2_msun_v2`` / filter columns as ``data/derived/main_hunt_derived_v2.parquet``,
so it is directly comparable (see ``diff.py``).

Typical use the morning DR4 lands::

    # 1) export the DR4 nss_two_body_orbit table (joined to gaia_source +
    #    astrophysical_parameters[_supp]) to a parquet, then:
    python rehunt.py --table /path/to/dr4_nss.parquet --profile dr4 \
        --out /tmp/dr4_rehunt.parquet
    # 2) diff vs the committed DR3 roster:
    python diff.py --baseline data/derived/main_hunt_derived_v2.parquet \
        --new /tmp/dr4_rehunt.parquet --out /tmp/dr4_diff.md

To reproduce today's DR3 roster as a regression check, point --profile dr3_raw at
the raw chunks with --supp the supplementary cache (see test_rehunt.py).

stdlib + pandas/numpy; polars only to write parquet (optional).
"""
from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path
from typing import Any

import pandas as pd

THIS = Path(__file__).resolve().parent
if str(THIS) not in sys.path:
    sys.path.insert(0, str(THIS))

# The production cascade — imported, never re-implemented.
_V2_DIR = THIS.parents[1] / "streaming" / "v2_corrected"
if str(_V2_DIR) not in sys.path:
    sys.path.insert(0, str(_V2_DIR))
from consumer_v2 import derive_row_v2  # noqa: E402

import adapter as adapter_mod  # noqa: E402

ROOT = Path("/Users/legbatterij/claude_projects/gaia-recovered-2026-05-27")

# The v2-derived output columns we surface for each source (mirrors the keys
# derive_row_v2 returns, plus source_id). Kept explicit so an ERROR row still
# emits a uniform schema.
_V2_OUT_KEYS = (
    "a_phot_mas", "plx_used", "plx_source", "a_phot_AU_v2", "P_yr_v2", "e_v2",
    "M1_msun_v2", "M1_source_v2", "fM_msun_v2", "M2_msun_v2", "class_v2",
    "logg_used", "logg_source", "cbias_risk_v2",
    "filter29_v2", "filter30_v2", "filter30_reason_v2", "filter31_v2",
    "filter32_v2", "filter33_v2", "flags", "nss_period_nonsignificant",
    "sini_implied_v2", "K_pred_i90_v2", "tier_v2",
)

TIER1_LABELS = ("Tier-1 NS", "Tier-1 BH")


def run_cascade(adapted_rows: list[dict[str, Any]], m1_prior: float = 1.5) -> pd.DataFrame:
    """Apply derive_row_v2 to each adapted row -> a tiered candidate DataFrame.

    Error rows (missing parallax/period/a_phot) are kept with tier_v2='ERROR'
    so nothing silently vanishes — the diff treats them as non-candidates.
    """
    out_rows: list[dict[str, Any]] = []
    n_err = 0
    for row in adapted_rows:
        res = derive_row_v2(row, M1_prior=m1_prior)
        if "error" in res:
            n_err += 1
            rec = {k: None for k in _V2_OUT_KEYS}
            rec["tier_v2"] = "ERROR"
            rec["_error"] = res["error"]
        else:
            rec = {k: res.get(k) for k in _V2_OUT_KEYS}
        rec["source_id"] = row.get("source_id")
        # Carry a few raw descriptors through for readable reports / diffing.
        rec["nss_solution_type"] = row.get("nss_solution_type")
        rec["period"] = row.get("period")
        out_rows.append(rec)
    df = pd.DataFrame(out_rows)
    # source_id stays an exact integer; de-dup defensively.
    if "source_id" in df.columns:
        df["source_id"] = df["source_id"].astype("int64")
        df = df.drop_duplicates(subset=["source_id"], keep="first").reset_index(drop=True)
    df.attrs["n_error"] = n_err
    return df


def tier_counts(df: pd.DataFrame) -> pd.DataFrame:
    return (df.groupby("tier_v2", dropna=False).size()
              .sort_values(ascending=False)
              .rename("n").reset_index())


def summarize(df: pd.DataFrame) -> str:
    """Readable run summary: tier counts + the Tier-1 NS/BH roster."""
    lines = []
    lines.append(f"rehunt: {len(df)} sources, {df.attrs.get('n_error', 0)} cascade errors")
    lines.append("")
    lines.append("tier_v2 counts:")
    for _, r in tier_counts(df).iterrows():
        lines.append(f"  {str(r['tier_v2']):<55s} {int(r['n']):>7d}")
    t1 = df[df["tier_v2"].isin(TIER1_LABELS)].copy()
    t1 = t1.sort_values("M2_msun_v2", ascending=False)
    lines.append("")
    lines.append(f"Tier-1 NS+BH roster (n={len(t1)}):")
    for _, r in t1.iterrows():
        sini = r.get("sini_implied_v2")
        sini_s = f"{sini:.3f}" if pd.notna(sini) else "n/a"
        lines.append(
            f"  {int(r['source_id']):<25d} {str(r['tier_v2']):<10s} "
            f"M2={r['M2_msun_v2']:.3f}  sini={sini_s}  "
            f"{r.get('nss_solution_type')}"
        )
    return "\n".join(lines)


def _maybe_backfill_supp(table_path: Path, profile_name: str, supp,
                         do_gaia: bool):
    """Optionally fetch missing NSS-plx / gspspec fields from Gaia DR3/DR4 ADQL.

    Only used when --gaia-backfill is passed AND no --supp file is given. This
    reuses the same lookup query shape as the v2 producer/run_v2. Returns a
    supplementary DataFrame (or None). Kept optional so the default path is
    fully offline (the DR3 dry-run + a DR4 export that already joined the AP
    tables both avoid network).
    """
    if supp is not None or not do_gaia:
        return supp
    # Defer import so the offline path never touches astroquery.
    try:
        from astroquery.gaia import Gaia
    except ImportError:
        print("WARNING: --gaia-backfill requested but astroquery unavailable; "
              "running offline.", flush=True)
        return None
    df = adapter_mod._read_table(table_path)
    ids = [int(s) for s in df["source_id"].astype("int64").tolist()]
    print(f"Gaia backfill: fetching supp fields for {len(ids)} source_ids", flush=True)
    chunks = []
    for i in range(0, len(ids), 100):
        batch = ",".join(str(s) for s in ids[i:i + 100])
        q = f"""
        SELECT g.source_id,
               n.parallax AS nss_parallax,
               ap.logg_gspphot, ap.logg_gspspec,
               ap.teff_gspphot, ap.teff_gspspec, ap.mass_flame,
               aps.logg_gspspec_ann, aps.teff_gspspec_ann
        FROM gaiadr3.gaia_source AS g
        LEFT JOIN gaiadr3.nss_two_body_orbit AS n USING (source_id)
        LEFT JOIN gaiadr3.astrophysical_parameters AS ap USING (source_id)
        LEFT JOIN gaiadr3.astrophysical_parameters_supp AS aps USING (source_id)
        WHERE g.source_id IN ({batch})
        """
        try:
            chunks.append(Gaia.launch_job_async(q, verbose=False).get_results().to_pandas())
        except Exception as exc:  # noqa: BLE001
            print(f"  backfill batch {i//100+1} ERR {type(exc).__name__}: "
                  f"{str(exc)[:100]}", flush=True)
    if not chunks:
        return None
    return pd.concat(chunks, ignore_index=True)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--table", required=True, help="NSS table (parquet/csv)")
    ap.add_argument("--profile", default="dr3_raw",
                    choices=sorted(adapter_mod.PROFILES),
                    help="column-mapping profile (default: dr3_raw)")
    ap.add_argument("--supp", default=None,
                    help="supplementary table (NSS plx + gspspec variants) to "
                         "merge by source_id when the main table lacks them")
    ap.add_argument("--out", default=None,
                    help="write the tiered candidate frame to this parquet/csv")
    ap.add_argument("--M1-prior", type=float, default=1.5,
                    help="fallback primary mass when no FLAME mass (default 1.5)")
    ap.add_argument("--limit", type=int, default=None, help="cap rows (smoke test)")
    ap.add_argument("--gaia-backfill", action="store_true",
                    help="if --supp absent, fetch missing NSS-plx/gspspec from "
                         "Gaia ADQL (network; off by default)")
    ap.add_argument("--quiet", action="store_true", help="suppress the summary")
    args = ap.parse_args(argv)

    t0 = time.time()
    table_path = Path(args.table)
    supp_arg = _maybe_backfill_supp(table_path, args.profile, args.supp,
                                    args.gaia_backfill)

    raw_df, adapted = adapter_mod.load_nss_table(
        table_path, profile=args.profile, supp=supp_arg, limit=args.limit)
    print(f"adapter: loaded {len(raw_df)} rows via profile {args.profile!r}",
          flush=True)

    out = run_cascade(adapted, m1_prior=args.M1_prior)
    print(f"cascade: derived {len(out)} rows in {time.time()-t0:.1f}s "
          f"({out.attrs.get('n_error', 0)} errors)", flush=True)

    if args.out:
        op = Path(args.out)
        if op.suffix in (".parquet", ".pq"):
            try:
                import polars as pl
                pl.from_pandas(out).write_parquet(op)
            except Exception:
                out.to_parquet(op, index=False)
        else:
            out.to_csv(op, index=False)
        print(f"wrote {op} ({len(out)} rows)", flush=True)

    if not args.quiet:
        print()
        print(summarize(out))
    return 0


if __name__ == "__main__":
    sys.exit(main())
