"""Unit tests for the pure data layer (no streamlit). Run with the ostinato python.

    python test_hunt_data.py

Asserts each public function works on the ingested hunt B, exercises a triage
round-trip on a REAL B id, and checks graceful degradation on missing/half-written
files. Prints a PASS/FAIL line per check and exits non-zero on any failure.
"""
from __future__ import annotations

import os
import sys
import time
import tempfile
from pathlib import Path

import hunt_data as hd

B = "ir_nova_2026_06_01"
PLATE_BLANK_ID = "3152p454_b0-000375"  # the lone PLATE_BLANK survivor (has a plot)

_failures = 0


def check(name: str, cond: bool, detail: str = "") -> None:
    global _failures
    mark = "PASS" if cond else "FAIL"
    if not cond:
        _failures += 1
    print(f"[{mark}] {name}" + (f"  — {detail}" if detail else ""))


def main() -> int:
    print(f"runs_dir = {hd.runs_dir()}\n")

    # --- list_runs --------------------------------------------------------
    runs = hd.list_runs()
    check("list_runs finds the ingested B run", B in runs, f"runs={runs}")
    check("list_runs finds the synthetic live run", "demo_live_running" in runs)

    # --- read_manifest ----------------------------------------------------
    man = hd.read_manifest(B)
    check("read_manifest status == done", man.get("status") == "done", man.get("status"))
    check("read_manifest lane == ir_nova", man.get("lane") == "ir_nova")
    check("read_manifest preserves extra 'headline' key", bool(man.get("headline")))

    # --- read_progress ----------------------------------------------------
    prog = hd.read_progress(B)
    check("read_progress processed == 97", (prog or {}).get("processed") == 97, str(prog))
    check("read_progress total == 97", (prog or {}).get("total") == 97)

    # --- read_candidates --------------------------------------------------
    df = hd.read_candidates(B)
    check("read_candidates returns 97 rows", len(df) == 97, f"len={len(df)}")
    for col in hd.REQUIRED_CANDIDATE_COLS:
        check(f"read_candidates has required col '{col}'", col in df.columns)
    check("read_candidates id column dtype is object/str",
          df["id"].map(type).eq(str).all(), "ids must stay strings")
    check("read_candidates score is numeric",
          str(df["score"].dtype).startswith(("float", "int")), str(df["score"].dtype))
    check("PLATE_BLANK id present in candidates",
          PLATE_BLANK_ID in set(df["id"]), PLATE_BLANK_ID)

    # --- candidate_row ----------------------------------------------------
    row = hd.candidate_row(B, PLATE_BLANK_ID)
    check("candidate_row returns the PLATE_BLANK row", row is not None and row["id"] == PLATE_BLANK_ID)
    check("candidate_row verdict is PLATE_BLANK_NO_CATALOG",
          "PLATE_BLANK_NO_CATALOG" in str((row or {}).get("verdict")), str((row or {}).get("verdict")))

    # --- findings + plots -------------------------------------------------
    f = hd.read_findings(B, PLATE_BLANK_ID)
    check("read_findings returns a dict for the plotted target", isinstance(f, dict))
    check("findings has key_values + classification + flags",
          all(k in (f or {}) for k in ("key_values", "classification", "flags")))
    plots = hd.list_target_plots(B, PLATE_BLANK_ID)
    check("list_target_plots finds the copied PNG", len(plots) == 1 and plots[0].endswith(".png"),
          str(plots))
    twf = hd.list_targets_with_findings(B)
    check("list_targets_with_findings includes the plotted id", PLATE_BLANK_ID in twf, str(twf))

    # --- cross_hunt_search on a REAL B id ---------------------------------
    hits = hd.cross_hunt_search(PLATE_BLANK_ID)
    check("cross_hunt_search finds the real B id", len(hits) >= 1, f"{len(hits)} hit(s)")
    if hits:
        hk, hrow = hits[0]
        check("cross_hunt_search hit reports the right hunt", hk == B, hk)
        check("cross_hunt_search row carries _hunt + _triage keys",
              "_hunt" in hrow and "_triage" in hrow)
    check("cross_hunt_search of a bogus id returns []",
          hd.cross_hunt_search("does_not_exist_zzz") == [])

    # --- triage round-trip (write then read) on a REAL B id ---------------
    # clean slate for this id
    hd.write_triage(B, PLATE_BLANK_ID, "clear")
    check("triage starts cleared", hd.get_triage_verdict(B, PLATE_BLANK_ID) is None)

    hd.write_triage(B, PLATE_BLANK_ID, "promote", note="queue for RV follow-up")
    v = hd.get_triage_verdict(B, PLATE_BLANK_ID)
    check("triage round-trip: write promote -> read promote", v == "promote", f"read={v}")
    full = hd.read_triage(B)
    check("triage entry stores the note",
          full.get(PLATE_BLANK_ID, {}).get("note") == "queue for RV follow-up")
    check("triage_counts reflects the promote", hd.triage_counts(B).get("promote", 0) >= 1)

    # candidates.csv must NOT have been mutated by triage
    df2 = hd.read_candidates(B)
    check("candidates.csv unchanged by triage (no 'triage' col added)",
          "triage" not in df2.columns and len(df2) == 97)

    # change verdict, then clear
    hd.write_triage(B, PLATE_BLANK_ID, "reject")
    check("triage update: promote -> reject", hd.get_triage_verdict(B, PLATE_BLANK_ID) == "reject")
    hd.write_triage(B, PLATE_BLANK_ID, "clear")
    check("triage clear removes the entry", hd.get_triage_verdict(B, PLATE_BLANK_ID) is None)

    # invalid verdict rejected
    try:
        hd.write_triage(B, PLATE_BLANK_ID, "banana")
        check("write_triage rejects an invalid verdict", False, "no exception raised")
    except ValueError:
        check("write_triage rejects an invalid verdict", True)

    # --- staleness / graded-health logic ----------------------------------
    # Construct heartbeats explicitly so the test does not depend on the demo
    # run's on-disk ts (which ages between ingest runs — the old flakiness).
    live_man = {"status": "running"}
    fresh = {"ts": time.time(), "processed": 10, "total": 100}
    quiet = {"ts": time.time() - 300}     # 300s: QUIET(180) < age <= STALE(600)
    dead = {"ts": time.time() - 999}      # 999s: > STALE(600)
    check("a running run with a fresh heartbeat is NOT stale",
          not hd.is_stale(live_man, fresh))
    check("a running run with a 999s-old heartbeat IS stale",
          hd.is_stale(live_man, dead))
    check("a 'done' run is never stale even with no heartbeat",
          not hd.is_stale({"status": "done"}, None))
    # graded health: live / quiet (mid long query) / stale / starting / done
    check("run_health: fresh running -> live",
          hd.run_health(live_man, fresh) == "live")
    check("run_health: 300s-quiet running -> quiet (NOT a dead worker)",
          hd.run_health(live_man, quiet) == "quiet")
    check("run_health: 999s-silent running -> stale",
          hd.run_health(live_man, dead) == "stale")
    check("run_health: running with no heartbeat yet -> starting",
          hd.run_health(live_man, None) == "starting")
    check("run_health: done run -> done",
          hd.run_health({"status": "done"}, None) == "done")

    # --- graceful degradation on missing / half-written files -------------
    with tempfile.TemporaryDirectory() as tmp:
        empty = Path(tmp) / "empty_run"
        empty.mkdir()
        (empty / "manifest.json").write_text("")          # empty file
        (empty / "candidates.csv").write_text("")          # empty csv
        (empty / "progress.json").write_text('{"ts": 1, "proc')  # truncated JSON
        check("read_manifest on empty file returns dict with defaults",
              isinstance(hd.read_manifest("empty_run", base=tmp), dict))
        check("read_candidates on empty csv returns empty df with required cols",
              list(hd.read_candidates("empty_run", base=tmp).columns) == hd.REQUIRED_CANDIDATE_COLS
              and len(hd.read_candidates("empty_run", base=tmp)) == 0)
        check("read_progress on truncated JSON returns None (not a crash)",
              hd.read_progress("empty_run", base=tmp) is None)
        check("read_findings on a totally missing target returns None",
              hd.read_findings("empty_run", "nope", base=tmp) is None)
        check("list_runs on a dir with only empty files still lists the run",
              "empty_run" in hd.list_runs(base=tmp))

    print()
    if _failures:
        print(f"==== {_failures} FAILURE(S) ====")
        return 1
    print("==== ALL DATA-LAYER CHECKS PASSED ====")
    return 0


if __name__ == "__main__":
    sys.exit(main())
