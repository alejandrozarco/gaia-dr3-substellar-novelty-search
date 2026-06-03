# Object journals — per-target documented history

An **append-only history** of everything we've researched about each object of
interest: every cross-check (*including the ones that came back null*), every
status change, every iteration and sidestep. The point is that a fact like
*"is it in Shahaf+2023?"* is **always answered from a logged, dated, sourced
ledger entry — never reconstructed from memory**.

> Memory drifts. On 2026-06-03 a context compaction silently turned UCAC4 313
> into a "Shahaf recovery" — it is not in Shahaf at all. This system exists so
> that a single `grep` of the ledger overrules any half-remembered claim.

## How this relates to the other docs

| Doc | Role |
|---|---|
| `docs/dossiers/<name>.md` | **Current** deep snapshot — best present understanding (carries superseding banners). |
| `docs/object_journals/<source_id>.md` | **History** — append-only ledger of how we got there + everything checked. |
| `docs/CANDIDATES.md` | Authoritative current roster + verdicts. |
| `docs/RESEARCH_LOG.md` | Project-level lab notebook (lanes, sidesteps, iterations, lessons). |

The dossier answers *"what do we believe now?"*. The journal answers *"what have
we actually done and checked, and when?"* — so we never repeat a sidestep or
re-confabulate a cross-check.

## Canonical key = Gaia DR3 source_id

Files are named `<source_id>.md` (19-digit Gaia DR3 id, as a string). Names are
ambiguous (UCAC4 313 ≠ its Gaia id; aliases collide); the source_id is stable
and matches the known-object store. `INDEX.md` maps source_id ↔ names ↔ status.

## The rule (mirrored in `CLAUDE.md`)

1. **Before asserting an object's known/novel status, mass, or any prior
   result, READ its journal ledger.** Do not reconstruct from memory or a
   conversation summary.
2. **After any investigation of an object** (a query, a cross-check, an
   analysis, a dossier edit, a workflow run), **append**: a cross-check ledger
   row for every catalog/method touched (with the result, *including null*) and
   a dated entry describing what was done, what was found, and the provenance.
3. **On any status change**, add a status-timeline row with the reason.
4. **Append-only.** Never delete history; supersede a wrong value with a new
   dated entry that says what it supersedes and why.

## Tooling

`scripts/journal/journal.py` makes this mechanical (scaffold a journal, append an
entry, append a ledger row, keep `INDEX.md` in sync) — stdlib-only, runs under
any python. The deep-dive workflows (`ns-candidate-deep-dive`, `wd-binary-sed-vet`,
`substellar-vet`) emit a `journal_entry` + `ledger_rows` in their synthesis
output for the main thread to append. See `.claude/workflows/README.md`.

## Format

See `TEMPLATE.md`. Each journal: identity header → cross-check ledger
(append-only table) → status timeline → chronological entry log.
