"""diff.py — diff a rehunt candidate roster against a baseline, keyed by source_id.

Compares two cascade outputs (each a frame carrying at least ``source_id`` +
``tier_v2``, and ideally ``M2_msun_v2`` / ``sini_implied_v2`` / period) and
classifies every source into:

  * NEW       — source present only in the *new* run (a DR4-only source, or one
                that was an ERROR/absent in the baseline) and now in a real tier.
  * VANISHED  — present (in a real tier) in the baseline but gone/ERROR in the new.
  * PROMOTED  — moved UP the tier ladder (e.g. Tier-2 -> Tier-1 NS, or
                Characterized -> Tier-1).
  * DEMOTED   — moved DOWN the tier ladder (e.g. Tier-1 NS -> Demoted/Tier-2).
  * MASS_MOVER   — same tier but |ΔM2| above a threshold.
  * PERIOD_MOVER — same tier but fractional |ΔP| above a threshold.
  * SAME      — same tier and within thresholds.

The tier ladder is an ordinal ranking (higher = stronger compact-object
candidate). PROMOTED/DEMOTED are defined by rank change, so a re-run that flips a
source between, say, "Tier-2 (RV inconclusive)" and "Tier-1 NS" is captured even
when the exact label strings differ.

Designed for the DR4 day-one diff: baseline = the committed DR3 v2 roster
(``data/derived/main_hunt_derived_v2.parquet``), new = a ``rehunt.py`` run on the
DR4 table. Also used by ``test_rehunt.py`` to confirm a DR3->DR3 re-run is ~empty.

Emits a readable Markdown report (or prints it). stdlib + pandas.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Any

import pandas as pd

# Tier ladder: higher rank == stronger candidate. Labels not listed get rank 0
# (with a substring fallback so minor label-text drift still ranks sensibly).
TIER_RANK = {
    "Tier-1 BH": 100,
    "Tier-1 NS": 90,
    "Tier-2 (RV inconclusive — needs follow-up)": 60,
    "Tier-2 (NSS period non-significant — needs corroboration)": 55,
    "Tier-2 (unexpected combination)": 50,
    "Characterized — sub-Ch WD or low-mass-star companion "
    "(0.5 ≤ M_2 < 1.2; ambiguous from astrometry alone)": 30,
    "Characterized — M-dwarf companion (0.08 ≤ M_2 < 0.5)": 25,
    "Characterized — brown-dwarf companion (0.013 ≤ M_2 < 0.08)": 22,
    "Characterized — planet-mass companion (M_2 < 0.013)": 20,
    "Demoted (failed F#29 SB2)": 10,
    "Demoted (failed F#33 NSS period non-significant)": 10,
    "Demoted (failed F#30 K-giant chromatic)": 10,
    "Demoted (failed F#32 joint K_obs/K_pred)": 10,
    "Demoted (failed F#31 phantom RV)": 10,
    "ERROR": -1,
}

# Sources at or above this rank are "real candidates" for NEW/VANISHED purposes.
# (>=20 == characterized-or-better; ERROR(-1) and absence are non-candidates.)
CANDIDATE_RANK_FLOOR = 20

TIER1_LABELS = ("Tier-1 NS", "Tier-1 BH")


def tier_rank(label: Any) -> int:
    if label is None or (isinstance(label, float) and pd.isna(label)):
        return -1
    s = str(label)
    if s in TIER_RANK:
        return TIER_RANK[s]
    # Substring fallback for label-text drift.
    if s.startswith("Tier-1 BH"):
        return 100
    if s.startswith("Tier-1 NS"):
        return 90
    if s.startswith("Tier-2"):
        return 55
    if s.startswith("Characterized"):
        return 25
    if s.startswith("Demoted"):
        return 10
    if s == "ERROR":
        return -1
    return 0


def _load(path: str | Path) -> pd.DataFrame:
    """Load a candidate frame; require source_id + tier_v2."""
    path = Path(path)
    if path.suffix in (".parquet", ".pq"):
        try:
            import polars as pl
            df = pl.read_parquet(path).to_pandas()
        except Exception:
            df = pd.read_parquet(path)
    else:
        df = pd.read_csv(path)
    if "source_id" not in df.columns or "tier_v2" not in df.columns:
        raise ValueError(f"{path} lacks source_id/tier_v2 columns "
                         f"(have: {list(df.columns)[:12]}...)")
    df = df.copy()
    df["source_id"] = df["source_id"].astype("int64")
    df = df.drop_duplicates(subset=["source_id"], keep="first")
    return df


def diff_rosters(baseline: pd.DataFrame, new: pd.DataFrame,
                 mass_thresh: float = 0.05, period_frac_thresh: float = 0.02
                 ) -> pd.DataFrame:
    """Return a per-source diff frame keyed by source_id.

    Columns: source_id, change, tier_base, tier_new, rank_base, rank_new,
    M2_base, M2_new, dM2, P_base, P_new, dP_frac.
    `change` in {NEW, VANISHED, PROMOTED, DEMOTED, MASS_MOVER, PERIOD_MOVER, SAME}.
    """
    b = baseline.set_index("source_id")
    n = new.set_index("source_id")
    all_ids = sorted(set(b.index) | set(n.index))

    def _f(frame, sid, col):
        if sid in frame.index and col in frame.columns:
            v = frame.at[sid, col]
            return v if not (isinstance(v, float) and pd.isna(v)) else None
        return None

    recs = []
    for sid in all_ids:
        tb = _f(b, sid, "tier_v2")
        tn = _f(n, sid, "tier_v2")
        rb, rn = tier_rank(tb), tier_rank(tn)
        m2b, m2n = _f(b, sid, "M2_msun_v2"), _f(n, sid, "M2_msun_v2")
        # period column may be named period or P_d depending on source frame.
        pb = _f(b, sid, "P_d")
        if pb is None:
            pb = _f(b, sid, "period")
        pn = _f(n, sid, "P_d")
        if pn is None:
            pn = _f(n, sid, "period")

        # "present" == the source_id is in the frame AND landed in a real tier
        # (rank >= 0, i.e. not ERROR and not an absent/NaN tier). NEW/VANISHED are
        # reserved for genuine appearance/disappearance from the catalog; a
        # source that merely fell to a "Demoted ..." tier is still present and is
        # reported as DEMOTED (rank dropped), not VANISHED. The CANDIDATE_RANK_FLOOR
        # is retained only for the report's "candidate" headline counts.
        present_b = sid in b.index and rb >= 0
        present_n = sid in n.index and rn >= 0

        dM2 = (m2n - m2b) if (m2b is not None and m2n is not None) else None
        dPf = (abs(pn - pb) / pb) if (pb not in (None, 0) and pn is not None) else None

        if present_n and not present_b:
            change = "NEW"
        elif present_b and not present_n:
            change = "VANISHED"
        elif rn > rb:
            change = "PROMOTED"
        elif rn < rb:
            change = "DEMOTED"
        elif dM2 is not None and abs(dM2) >= mass_thresh:
            change = "MASS_MOVER"
        elif dPf is not None and dPf >= period_frac_thresh:
            change = "PERIOD_MOVER"
        else:
            change = "SAME"

        recs.append(dict(
            source_id=sid, change=change,
            tier_base=tb, tier_new=tn, rank_base=rb, rank_new=rn,
            M2_base=m2b, M2_new=m2n, dM2=dM2,
            P_base=pb, P_new=pn, dP_frac=dPf,
        ))
    return pd.DataFrame(recs)


def render_report(diff: pd.DataFrame, baseline_name: str, new_name: str,
                  max_rows: int = 60) -> str:
    """Render a Markdown diff report."""
    order = ["NEW", "PROMOTED", "DEMOTED", "VANISHED", "MASS_MOVER", "PERIOD_MOVER"]
    counts = diff["change"].value_counts().to_dict()
    n_same = counts.get("SAME", 0)

    L = []
    L.append(f"# Rehunt diff — `{new_name}` vs baseline `{baseline_name}`")
    L.append("")
    L.append(f"- baseline sources: {(diff['rank_base'] >= 0).sum()}  |  "
             f"new sources: {(diff['rank_new'] >= 0).sum()}  |  "
             f"compared: {len(diff)}")
    L.append("")
    L.append("## Summary")
    L.append("")
    L.append("| change | count |")
    L.append("|---|---:|")
    for c in order:
        L.append(f"| {c} | {counts.get(c, 0)} |")
    L.append(f"| SAME | {n_same} |")
    L.append("")

    # Tier-1 movement is the headline for a compact-object hunt.
    base_t1 = set(diff.loc[diff["tier_base"].isin(TIER1_LABELS), "source_id"])
    new_t1 = set(diff.loc[diff["tier_new"].isin(TIER1_LABELS), "source_id"])
    L.append("## Tier-1 NS+BH delta")
    L.append("")
    L.append(f"- baseline Tier-1: {len(base_t1)}  |  new Tier-1: {len(new_t1)}")
    L.append(f"- Tier-1 gained: {len(new_t1 - base_t1)}  |  "
             f"Tier-1 lost: {len(base_t1 - new_t1)}  |  "
             f"retained: {len(base_t1 & new_t1)}")
    L.append("")

    def _section(title, sub):
        L.append(f"## {title} ({len(sub)})")
        L.append("")
        if sub.empty:
            L.append("_none_")
            L.append("")
            return
        L.append("| source_id | tier_base | tier_new | M2_base | M2_new | dM2 | dP_frac |")
        L.append("|---|---|---|---:|---:|---:|---:|")
        for _, r in sub.head(max_rows).iterrows():
            def fmt(v, p=3):
                return f"{v:.{p}f}" if isinstance(v, (int, float)) and pd.notna(v) else "—"
            L.append(
                f"| {int(r['source_id'])} | {r['tier_base'] or '—'} | "
                f"{r['tier_new'] or '—'} | {fmt(r['M2_base'])} | {fmt(r['M2_new'])} | "
                f"{fmt(r['dM2'])} | {fmt(r['dP_frac'])} |"
            )
        if len(sub) > max_rows:
            L.append(f"| … {len(sub) - max_rows} more … | | | | | | |")
        L.append("")

    # Order each section by candidate strength (new rank desc, then |dM2|).
    for c in order:
        sub = diff[diff["change"] == c].copy()
        sort_cols = [col for col in ["rank_new", "rank_base"] if col in sub.columns]
        if sort_cols:
            sub = sub.sort_values(sort_cols, ascending=False)
        _section(c, sub)

    if not any(counts.get(c, 0) for c in order):
        L.append("## Verdict")
        L.append("")
        L.append("**No tier movement** — the new run reproduces the baseline "
                 "roster (regression-clean).")
        L.append("")
    return "\n".join(L)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--baseline", required=True, help="baseline candidate frame")
    ap.add_argument("--new", required=True, help="new candidate frame (rehunt output)")
    ap.add_argument("--out", default=None, help="write Markdown report here")
    ap.add_argument("--out-csv", default=None, help="write the per-source diff CSV here")
    ap.add_argument("--mass-thresh", type=float, default=0.05,
                    help="|ΔM2| (M_sun) to flag a MASS_MOVER (default 0.05)")
    ap.add_argument("--period-frac-thresh", type=float, default=0.02,
                    help="fractional |ΔP| to flag a PERIOD_MOVER (default 0.02)")
    args = ap.parse_args(argv)

    base = _load(args.baseline)
    new = _load(args.new)
    d = diff_rosters(base, new, mass_thresh=args.mass_thresh,
                     period_frac_thresh=args.period_frac_thresh)
    report = render_report(d, Path(args.baseline).name, Path(args.new).name)

    if args.out_csv:
        d.to_csv(args.out_csv, index=False)
    if args.out:
        Path(args.out).write_text(report)
        print(f"wrote {args.out}")
    else:
        print(report)
    # Exit code: 0 if regression-clean (no movement), 1 if there is movement —
    # lets the test / a CI gate detect drift.
    moved = d["change"].isin(
        ["NEW", "PROMOTED", "DEMOTED", "VANISHED", "MASS_MOVER", "PERIOD_MOVER"]
    ).any()
    return 1 if moved else 0


if __name__ == "__main__":
    sys.exit(main())
