# Precovery campaign — state snapshot (2026-07-07, late)

Written as a crash-safe checkpoint. **Read this + RESEARCH_LOG.md (entries 2026-07-07) before
resuming campaign work in any session.** All results below are LOCAL (unpushed) per push policy.

## Scoreboard

| object | state | astrometry | user action |
|---|---|---|---|
| ★ (330836) Orius = 2009 HW77 | **pixel-CONFIRMED, submission-ready** (6 DECam det., 4 epochs 2013–15, +2.9 yr arc) | `verify/2009_HW77/updated_astrometry.csv` (authoritative); **ADES draft: `verify/2009_HW77/ades_draft_330836_orius.psv`** | **task #141: contact SARC → review → file to obs@cfa → WAMO.** Deep-dive: our points cut its recovery box ~10× in area + recenter a ~1.9σ-biased track — re-enables Lucky Star/RECON occultation prediction. Journal: `docs/object_journals/mp_330836_orius.md` |
| ★ (88268) = 2001 KK76 | **HST 4-point chain MEASURED, referee-clean** (2006-05-02 ACS/HRC, prog 10514/Noll, obscode 250, σ 0.16″/0.10″, +1.9 yr); 2010 WFC3 = bounded non-detection | `wave3/hst_kk76/candidate_astrometry.csv` (NOTE: `jd_tdb_mid` column actually holds UTC JD — use `obsTime_UTC`) | refit + ADES draft in flight (task #147); then same SARC/file path |
| 2001 KN76 | PARKED — real mover (pixels passed) but joint refit inconclusive | `verify/2001_KN76/updated_astrometry.csv` | do NOT submit; needs 3rd epoch + DE-ephemeris refit |
| 2001 QT322 | valid catalog-level null (after epoch-shuffle bug fix) | — | none (optional pixel-level pass unspent) |
| 2001 KJ76 | strongest null (pixel-level CFHT ±40″ tracking scan) | — | none |
| 2001 KP76 | two-channel catalog null | — | none |
| 2001 KK76 blind-DECam / 2006 JG57 / 2004 YH32 | soft null / NO_COVERAGE ×2 (see wave2/) | — | none |

## In flight (background workflows; resume with the run IDs below if a session limit killed them)

| task | workflow | runId (resumeFromRunId) | script (repo copy in `workflow_scripts/`) |
|---|---|---|---|
| #147 KK76/(88268) joint refit + ADES draft | wnmbzfu6s | `wf_16b7135e-77d` | `kk76_refit.mjs` |
| #148 wave 4: 2007 HV90, 2002 KW14, 2010 JK124 | w3ue4aqw0 | `wf_dcc746e5-6e3` | `precovery_wave4.mjs` |

Resume pattern: `Workflow({scriptPath: <scratchpad or repo copy>, resumeFromRunId: "<runId>"})` —
completed agents replay from cache. Scratchpad originals:
`/private/tmp/claude-501/-Users-legbatterij-claude-projects/5bae4473-7497-4a6b-8bf6-3ecc9abd4295/scratchpad/`.
Outputs land in `/tmp/kk76_refit/` and `/tmp/precovery_wave4/` → preserve into this dir on completion
(pattern: copy `*.md,*.csv,*.json,*.tsv,*.txt` <3M, exclude venv/FITS).

## Standing rules (all bought by documented failures — enforce in every wave)

1. datetime_jd-keyed ephemerides, per-epoch asserts (epoch-shuffle bug, QT322; 3rd occurrence caught in the Orius photometry check — time-axis asserts apply to EVERY comparison).
2. NOIRLab `/svc/cutout` needs the `_ooi_` science product.
3. Catalog PSF positions + honest per-axis σ; HST weights 0.16″/0.10″ (not internal tens-of-mas).
4. Rule v3/4: search only where a SMIA-passing epoch OVERLAPS confirmed per-epoch imaging (SSOIS at the epoch, never whole-arc footprint counts); prefer arc-end ≳2010 (wave-2 anti-correlation).
5. Bycatch pass mandatory (`scripts/precovery/bycatch.py`, 18/18 tests; static/mean-object catalog MANDATORY; unknowns = review leads, never claims).
6. Chain discipline: multi-detection motion-consistent chains; deep-coadd blank-test; mag sanity; +1° offset negative control; honest nulls.
7. Arc-ends from fresh MPC get-obs parse at run time (wave-3 recut failure).
8. Self-arc test before searching any window (wave-3 recut failure).
9. Prior-art gates MUST include web/press search, not arXiv-only (missed ADAM::THOR twice-class lesson).

## Closed lanes (do not reopen without new data)

- Blind NSC novelty mining: NO-GO — ADAM::THOR ran 100% of NSC DR2 (~27.5k candidates); CANFind DR2 ~600k SSOs; faint slow movers are image-domain (DES/DEEP/YOSO) + Rubin. `novelty_gate/REPORT.md`.
- DASCH dippers (R2): supply collapse; trigger = future bright V≲13.5 long-eclipse event.
- Short single-opp distant arcs (<~40 d at >30 AU): dynamically lost (pilot); SMIA pre-gate mandatory.
- Stellar/compact-object archival frame: frozen for Gaia DR4 (2 Dec 2026) — see RESEARCH_LOG 2026-07-05.

## Queue after in-flight work

- Wave-3 referee-salvaged trio = wave 4 (running). Next pool: repaired full rule-v3 re-cut over the remaining ~90 gate passers (repairs = rules 7+8 in the recut script) — optional, user decides.
- KK76 pointed-HST 2010 WFC3 field: revisit with the 2006-refined orbit (bounded non-detection could become a localization).
