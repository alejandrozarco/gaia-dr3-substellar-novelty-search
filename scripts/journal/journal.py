#!/usr/bin/env python3
"""Object-journal helper — scaffold and append to per-object research journals.

Stdlib-only (no venv needed). The journal system is documented in
docs/object_journals/README.md and CLAUDE.md. The point: every cross-check is
recorded in a dated, sourced ledger so an object's known/novel status is READ,
never reconstructed from memory.

Usage:
  python scripts/journal/journal.py new <source_id> --name "WDJ060042" \
      --klass "DA WD + dark companion" --status CANDIDATE --dossier docs/dossiers/X.md \
      --candidates "table; framing note" --prereg yes

  python scripts/journal/journal.py ledger <source_id> \
      --catalog "Shahaf+2023 (J/MNRAS/518/2991)" --query "by source_id + 5\" cone" \
      --result "NOT IN" --provenance "CANDIDATES.md:212; dossier 8"

  python scripts/journal/journal.py entry <source_id> --title "Novelty cross-check" \
      --did "queried SIMBAD + Shahaf + Marcussen" --found "novel; 0 prior binary refs" \
      --provenance "task #46; dossier 8" [--status CANDIDATE --reason "novelty confirmed"]

  python scripts/journal/journal.py index      # rebuild INDEX.md from all journals
"""
from __future__ import annotations

import argparse
import csv
import datetime
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
JDIR = ROOT / "docs" / "object_journals"
RESERVED = {"README.md", "TEMPLATE.md", "INDEX.md"}
REGISTER = JDIR / "findings_register.csv"
REGISTER_COLS = ["date", "source_id", "name", "lane", "classification",
                 "novelty", "disposition", "journal", "provenance"]


def today() -> str:
    return datetime.date.today().isoformat()


def jpath(sid: str) -> Path:
    return JDIR / f"{sid}.md"


def _scaffold(sid, name, klass, status, dossier, candidates, prereg, date) -> str:
    return f"""# Object journal — Gaia DR3 {sid}

| field | value |
|---|---|
| Canonical key | **Gaia DR3 {sid}** |
| Aliases / names | {name or "—"} |
| Current class | {klass or "—"} |
| Current status | **{status or "CANDIDATE"}** (as of {date}) |
| Dossier | {dossier or "—"} |
| CANDIDATES.md | {candidates or "—"} |
| In DR4 pre-registration | {prereg or "—"} |

## Cross-check ledger
*Append-only. The anti-confabulation table — read this before asserting any prior result.*

| date | catalog / method | query | result | provenance |
|---|---|---|---|---|

## Status timeline
*Append-only.*

| date | status | reason | by |
|---|---|---|---|
| {date} | {status or "CANDIDATE"} | journal created | journal.py new |

## Entry log
*Append-only, chronological.*
"""


def _section_bounds(lines, heading):
    start = None
    for i, ln in enumerate(lines):
        if ln.strip() == heading:
            start = i
            break
    if start is None:
        raise SystemExit(f"section {heading!r} not found")
    end = len(lines)
    for j in range(start + 1, len(lines)):
        if lines[j].startswith("## "):
            end = j
            break
    return start, end


def _insert_table_row(lines, heading, row):
    start, end = _section_bounds(lines, heading)
    last_tbl = None
    for k in range(start, end):
        if lines[k].lstrip().startswith("|"):
            last_tbl = k
    if last_tbl is None:
        raise SystemExit(f"no table found under {heading!r}")
    lines.insert(last_tbl + 1, row)
    return lines


def _read(sid):
    p = jpath(sid)
    if not p.exists():
        raise SystemExit(f"no journal for {sid} — run: journal.py new {sid} ...")
    return p, p.read_text().splitlines()


def cmd_new(a):
    p = jpath(a.source_id)
    if p.exists():
        raise SystemExit(f"journal already exists: {p}")
    JDIR.mkdir(parents=True, exist_ok=True)
    p.write_text(_scaffold(a.source_id, a.name, a.klass, a.status, a.dossier,
                           a.candidates, a.prereg, a.date or today()))
    print(f"created {p}")
    _rebuild_index()


def cmd_ledger(a):
    p, lines = _read(a.source_id)
    row = f"| {a.date or today()} | {a.catalog} | {a.query or '—'} | **{a.result}** | {a.provenance or '—'} |"
    _insert_table_row(lines, "## Cross-check ledger", row)
    p.write_text("\n".join(lines) + "\n")
    print(f"ledger += {a.catalog} -> {a.result}")


def cmd_entry(a):
    p, lines = _read(a.source_id)
    d = a.date or today()
    if a.status:
        row = f"| {d} | {a.status} | {a.reason or '—'} | {a.by or 'journal.py'} |"
        _insert_table_row(lines, "## Status timeline", row)
        for i, ln in enumerate(lines):
            if ln.startswith("| Current status |"):
                lines[i] = f"| Current status | **{a.status}** (as of {d}) |"
                break
    block = [f"\n### {d} — {a.title}"]
    if a.did:
        block.append(f"- **Did:** {a.did}")
    if a.found:
        block.append(f"- **Found:** {a.found}")
    if a.provenance:
        block.append(f"- **Provenance:** {a.provenance}")
    text = "\n".join(lines).rstrip() + "\n" + "\n".join(block) + "\n"
    p.write_text(text)
    print(f"entry += {a.title}" + (f" (status -> {a.status})" if a.status else ""))
    if a.status:
        _rebuild_index()


def _field(lines, label):
    for ln in lines:
        m = re.match(rf"\|\s*{re.escape(label)}\s*\|\s*(.*?)\s*\|", ln)
        if m:
            return m.group(1).replace("**", "").strip()
    return "—"


def _rebuild_index():
    rows = []
    for p in sorted(JDIR.glob("*.md")):
        if p.name in RESERVED:
            continue
        lines = p.read_text().splitlines()
        sid = p.stem
        rows.append((sid, _field(lines, "Aliases / names"),
                     _field(lines, "Current class"),
                     _field(lines, "Current status"),
                     f"`{p.relative_to(ROOT)}`"))
    out = ["# Object-journal index",
           "",
           "Source_id ↔ names ↔ status. Rebuilt by `journal.py index`. "
           "Read the per-object ledger before asserting any prior result.",
           "",
           "| Gaia DR3 source_id | aliases | class | status | journal |",
           "|---|---|---|---|---|"]
    for r in rows:
        out.append(f"| {r[0]} | {r[1]} | {r[2]} | {r[3]} | {r[4]} |")
    (JDIR / "INDEX.md").write_text("\n".join(out) + "\n")
    print(f"INDEX.md rebuilt ({len(rows)} journals)")


def cmd_index(a):
    _rebuild_index()


def cmd_register(a):
    """Append a row to findings_register.csv — the lightweight log for ANY object a
    search surfaces (validation recoveries + bulk uncatalogued). Novel/candidate
    objects ALSO get a full journal via `new`."""
    REGISTER.parent.mkdir(parents=True, exist_ok=True)
    fresh = not REGISTER.exists()
    with REGISTER.open("a", newline="") as f:
        w = csv.DictWriter(f, fieldnames=REGISTER_COLS)
        if fresh:
            w.writeheader()
        w.writerow({"date": a.date or today(), "source_id": str(a.source_id),
                    "name": a.name, "lane": a.lane, "classification": a.classification,
                    "novelty": a.novelty, "disposition": a.disposition,
                    "journal": a.journal or "no", "provenance": a.provenance})
    print(f"register += {a.source_id} ({a.novelty or '?'})")


def main():
    ap = argparse.ArgumentParser(description="Object-journal helper")
    sub = ap.add_subparsers(dest="cmd", required=True)

    n = sub.add_parser("new")
    n.add_argument("source_id")
    for f in ("name", "klass", "status", "dossier", "candidates", "prereg", "date"):
        n.add_argument(f"--{f}", default="")
    n.set_defaults(func=cmd_new)

    L = sub.add_parser("ledger")
    L.add_argument("source_id")
    L.add_argument("--catalog", required=True)
    L.add_argument("--result", required=True)
    L.add_argument("--query", default="")
    L.add_argument("--provenance", default="")
    L.add_argument("--date", default="")
    L.set_defaults(func=cmd_ledger)

    e = sub.add_parser("entry")
    e.add_argument("source_id")
    e.add_argument("--title", required=True)
    e.add_argument("--did", default="")
    e.add_argument("--found", default="")
    e.add_argument("--provenance", default="")
    e.add_argument("--status", default="")
    e.add_argument("--reason", default="")
    e.add_argument("--by", default="")
    e.add_argument("--date", default="")
    e.set_defaults(func=cmd_entry)

    i = sub.add_parser("index")
    i.set_defaults(func=cmd_index)

    g = sub.add_parser("register")
    g.add_argument("source_id")
    for f in ("name", "lane", "classification", "novelty", "disposition", "journal", "provenance", "date"):
        g.add_argument(f"--{f}", default="")
    g.set_defaults(func=cmd_register)

    a = ap.parse_args()
    a.func(a)


if __name__ == "__main__":
    main()
