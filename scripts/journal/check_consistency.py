#!/usr/bin/env python3
"""Journal consistency checker — pre-release hygiene for the object-journal system.

Asserts:
  1. COVERAGE   — every dossier in docs/dossiers/ has a docs/object_journals/<sid>.md
  2. WELL-FORMED — every journal has the 4 sections, a parseable Current status,
                   and at least one cross-check ledger data row
  3. INDEX SYNC — every journal appears in INDEX.md (run `journal.py index` to fix)

Soft/info (does not fail): journals with no dossier (e.g. recovered orphans).

Exit 0 if clean, 1 if any HARD failure. Stdlib-only.
Run:  /usr/bin/env python3 scripts/journal/check_consistency.py
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DOSS = ROOT / "docs" / "dossiers"
JDIR = ROOT / "docs" / "object_journals"
RESERVED = {"README.md", "TEMPLATE.md", "INDEX.md"}
SECTIONS = ["## Cross-check ledger", "## Status timeline", "## Entry log"]


def dossier_sid(path: Path):
    """Resolve a dossier's Gaia DR3 source_id (filename prefix, else file content)."""
    m = re.match(r"(\d{17,19})_", path.stem)
    if m:
        return m.group(1)
    txt = path.read_text(errors="ignore")
    for pat in (r"(?i)source[ _]?id\D{0,30}?(\d{17,19})",
                r"Gaia DR3\D{0,5}(\d{17,19})",
                r"\b(\d{18,19})\b"):
        m = re.search(pat, txt)
        if m:
            return m.group(1)
    return None


def ledger_rows(lines):
    """Count data rows under '## Cross-check ledger' (exclude header + separator)."""
    try:
        start = next(i for i, l in enumerate(lines) if l.strip() == "## Cross-check ledger")
    except StopIteration:
        return 0
    end = len(lines)
    for j in range(start + 1, len(lines)):
        if lines[j].startswith("## "):
            end = j
            break
    n = 0
    for l in lines[start:end]:
        s = l.lstrip()
        if s.startswith("|") and not s.startswith("|---") and "| date " not in s and not s.startswith("| date"):
            n += 1
    return n


def main():
    hard, soft = [], []

    journals = {p.stem: p for p in JDIR.glob("*.md") if p.name not in RESERVED}
    index_txt = (JDIR / "INDEX.md").read_text() if (JDIR / "INDEX.md").exists() else ""

    # 1. coverage
    dossiers = sorted(DOSS.glob("*.md"))
    for d in dossiers:
        sid = dossier_sid(d)
        if sid is None:
            hard.append(f"COVERAGE: cannot resolve source_id for dossier {d.name}")
        elif sid not in journals:
            hard.append(f"COVERAGE: dossier {d.name} (sid {sid}) has NO journal")

    # 2. well-formed
    for sid, p in sorted(journals.items()):
        lines = p.read_text().splitlines()
        for sec in SECTIONS:
            if not any(l.strip() == sec for l in lines):
                hard.append(f"WELL-FORMED: {sid}.md missing section '{sec}'")
        if not any(l.startswith("| Current status |") for l in lines):
            hard.append(f"WELL-FORMED: {sid}.md missing parseable 'Current status' header row")
        if ledger_rows(lines) == 0:
            hard.append(f"WELL-FORMED: {sid}.md has an EMPTY cross-check ledger")
        # 3. index sync
        if sid not in index_txt:
            hard.append(f"INDEX SYNC: {sid} not in INDEX.md (run journal.py index)")

    # soft: journals with no dossier
    dsids = {dossier_sid(d) for d in dossiers}
    for sid in sorted(journals):
        if sid not in dsids:
            soft.append(f"info: journal {sid} has no dossier (orphan/standalone — OK)")

    print(f"dossiers: {len(dossiers)} | journals: {len(journals)} | "
          f"hard failures: {len(hard)} | info: {len(soft)}")
    for s in soft:
        print("  " + s)
    for h in hard:
        print("  [FAIL] " + h)
    if hard:
        print(f"\n{len(hard)} HARD failure(s).")
        sys.exit(1)
    print("\nAll journals consistent.")
    sys.exit(0)


if __name__ == "__main__":
    main()
