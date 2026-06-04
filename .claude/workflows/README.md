# Gaia DR3 dormant-companion search — reusable workflows

Multi-agent Workflow-tool scripts that codify this project's recurring tasks, with the
rigor learned the hard way baked in. Invoke with the Workflow tool by name, e.g.:

```
Workflow({ name: "ns-candidate-deep-dive", args: { source_id: "3378588057203660160" } })
```

**Gaia source_ids are 19 digits — always pass them as STRINGS** (a JS number truncates them).
Each workflow spawns several `general-purpose` subagents (they run astroquery/lightkurve via
the ostinato venv) and finishes with a skeptical synthesis. They run in the background.

## The four

| Workflow | args | What it does |
|---|---|---|
| `ns-candidate-deep-dive` | `{source_id}` | NSS mass derivation ∥ archival-RV Keplerian ∥ Gaia quality ∥ **AMRF triple-vs-compact** ∥ novelty → adversarial verdict |
| `pool-second-method-triage` | `{source_ids:[...]}` | Per-candidate RV census + NSS-locked Keplerian → classify, with an adversarial **verify pass on every CORROBORATED** (clustered/one-phase epochs get downgraded) |
| `photometric-revet` | `{source_id, claimed_period_min}` | ZTF (outburst-masked LS/BLS + permutation FAP) ∥ TESS (real SPOC, permutation/refined-null FAP) → real-vs-artifact verdict |
| `catalog-consistency-sweep` | `{query}` or `{audit:true}` | **Read-only** blast-radius sweep across CANDIDATES.md / dossiers / README / CITATION / releases → a precise correction checklist (apply+commit+push stay manual) |

## Lessons encoded (from the 2026-05 re-vetting)

- **Compact ≠ what the cascade says.** The astrometric mass function can't tell a single dark
  companion from a hierarchical triple — every deep-dive defers to the **Shahaf AMRF P(compact)**.
- **No sin-i inflation.** For a dark companion, M₂ comes straight from the photocentric mass
  function; never multiply up with `rv_amplitude_robust/2` (that error invented "mass-gap BHs").
- **Single-phase ≠ corroboration.** RV epochs clustered in one MJD window are one phase; low
  χ²/dof on few points is not a detection. The triage verify-pass exists to catch exactly this.
- **Photometry false positives.** Outburst-contaminated folds + minimum-of-noise depths at
  per-cadence S/N<1 manufacture fake periods/eclipses — hence masked periodograms + permutation FAPs.
- **Known ⇒ not novel.** Always cross-check Shahaf+2023 / Müller-Horn+2026 / Halbwachs+2023.
- **Trust but verify.** Each workflow ends with an adversarial synthesis that defaults to the
  less-exciting interpretation.
- **Write it down.** Cross-checks live in `docs/object_journals/<source_id>.md`, not memory —
  every per-object deep-dive emits a `journal_entry` + `ledger_rows` for the main thread to append
  (the 2026-06 UCAC4/Shahaf drift, where a compaction invented a "Shahaf recovery", is why).

## Journaling (mandatory)

Every per-object workflow's synthesis returns two extra fields for the **main thread** to append
to that object's journal via `scripts/journal/journal.py`:

- `journal_entry` — a dated entry body: what was done / what was found (incl. nulls) / provenance.
- `ledger_rows` — one per catalog/method checked: `{catalog, query, result, provenance}`.

Agents never write to `docs/` themselves (single-writer rule — see `CLAUDE.md`); they **return**
the content and the main thread appends it:

```
python scripts/journal/journal.py ledger <sid> --catalog "Shahaf+2023 (J/MNRAS/518/2991)" \
    --query "by source_id" --result "NOT IN" --provenance "task #NN"
python scripts/journal/journal.py entry  <sid> --title "..." --did "..." --found "..." \
    --provenance "..." [--status CANDIDATE --reason "..."]
```

Before asserting any prior result about an object (is it known? in catalog X? what mass?),
**read its ledger** — don't reconstruct from memory.

**Log every surfaced object, not just survivors.** A hunt should `journal.py register` each
object it surfaces into `findings_register.csv` — validation recoveries (a recovered *known*
object proves the pipeline works) *and* uncatalogued finds — and promote any novel/uncatalogued
one to a full journal. Full spec: `docs/object_journals/README.md`.

## Additional workflows (built — same `.claude/workflows/` dir)

- `wd-binary-sed-vet` — Pile E: SED 2-component fit, exclude M-dwarf / hot-WD companions,
  Type-Ia-progenitor (M_tot vs Chandrasekhar) check.
- `substellar-vet` — Pile B: NSS planet/BD mass + inclination prior + TESS dark-companion
  photometric limit (rules out a stellar companion across all i).
- `cascade-regression` — run the v2 cascade against the frozen known-BH/NS positives + known-SB2
  negatives; report recall/specificity (guards against pipeline regressions).
- `pre-release-audit` — whole-catalog `catalog-consistency-sweep({audit:true})` + a test-suite run
  before cutting any release ("is anything left to retract?", automated).
- `new-data-reingest` — on a new Gaia/archive release: re-run producer + v2 cascade + M₁ correction,
  diff the candidate tiers, and flag movers.
- `archival-rv-monitor` — periodically re-check the top candidates (HD 264291, Pile B, ...) for
  newly-published archival RV epochs that could confirm/refute them.
