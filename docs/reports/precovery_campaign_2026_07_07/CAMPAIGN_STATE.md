# Precovery campaign — state snapshot (2026-07-07, late)

Written as a crash-safe checkpoint. **Read this + RESEARCH_LOG.md (entries 2026-07-07) before
resuming campaign work in any session.** All results below are LOCAL (unpushed) per push policy.

## Scoreboard

| object | state | astrometry | user action |
|---|---|---|---|
| ★ (330836) Orius = 2009 HW77 | **pixel-CONFIRMED, submission-ready** (6 DECam det., 4 epochs 2013–15, +2.9 yr arc) | `verify/2009_HW77/updated_astrometry.csv` (authoritative); **ADES draft: `verify/2009_HW77/ades_draft_330836_orius.psv`** | **task #141: contact SARC → review → file to obs@cfa → WAMO.** Deep-dive: our points cut its recovery box ~10× in area + recenter a ~1.9σ-biased track — re-enables Lucky Star/RECON occultation prediction. Journal: `docs/object_journals/mp_330836_orius.md` |
| ★ (88268) = 2001 KK76 | **REFIT REFEREE-CONFIRMED, submission-ready** (2026-07-08): joint fo fit retains all 4 HST points (max pull 0.66σ); sky-plane 1σ 2026/2030/2040 = 11.2″→0.86″ / 13.7″→0.83″ / 24″→0.31″ (13–77×) + ~3.2–3.4σ bias correction; referee independently re-ran both fits + proved satellite parallax genuine. Caveats: fo no-JPL-DE (arc-only covariance optimistic — the point); astCat Gaia3 = confirm with SARC. 2010 WFC3 = bounded non-detection | `wave3/hst_kk76/candidate_astrometry.csv` (NOTE: `jd_tdb_mid` column actually holds UTC JD — use `obsTime_UTC`); **ADES draft: `kk76_refit/ades_draft_88268_2001kk76.psv`**; full fit artifacts `kk76_refit/` | **task #141: same SARC → obs@cfa → WAMO path as Orius** |
| 2001 KN76 | PARKED — real mover (pixels passed) but joint refit inconclusive | `verify/2001_KN76/updated_astrometry.csv` | do NOT submit; needs 3rd epoch + DE-ephemeris refit |
| 2001 QT322 | valid catalog-level null (after epoch-shuffle bug fix) | — | none (optional pixel-level pass unspent) |
| 2001 KJ76 | strongest null (pixel-level CFHT ±40″ tracking scan) | — | none |
| 2001 KP76 | two-channel catalog null | — | none |
| 2001 KK76 blind-DECam / 2006 JG57 / 2004 YH32 | soft null / NO_COVERAGE ×2 (see wave2/) | — | none |
| 2007 HV90 / 2002 KW14 / 2010 JK124 (wave 4) | **3/3 NULL_SEARCHED, referee-confirmed 2026-07-08.** HV90 + KW14 = honest single-night/single-sequence nulls (2017-05-17 windows can never chain a slow TNO). **JK124: agent's 3-epoch CANDIDATE_CHAIN OVERTURNED by referee** — 2 of 3 detections were ndet=1 and absent from same-night equal-depth partner frames minutes later (a real SNR~17–19 TNO must reappear); only the 2015-06-20 ndet=2 epoch was real, and one epoch ≠ chain. Bycatch 3/3 clean (0 unknowns). | — (JK124 `wave4/2010_JK124/candidate_astrometry.csv` = REFUTED, do not use) | none — file nothing for wave 4 |

## In flight (background workflows; resume with the run IDs below if a session limit killed them)

**NOTHING in flight (2026-07-08).** #147 KK76 refit + #148 wave 4 both COMPLETED and banked
(`kk76_refit/`, `wave4/`). The only open task is **#141 (USER): MPC filing for Orius + KK76.**

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
10. **Chain members must reproduce in a same-night, equal-depth partner exposure** — reject ndet=1
    detections as chain members (wave-4 JK124 overturn: 2/3 claimed epochs were single-exposure
    spurious; a real SNR~17–19 TNO moves <0.1″ in minutes and MUST reappear).
11. **Pre-gate requires ≥2 distinct post-arc imaging nights spanning real baseline (months)** —
    never dispatch single-night/single-sequence windows; they are guaranteed nulls for slow TNOs
    and burn a full referee cycle for no information (wave-4 HV90/KW14).

## Closed lanes (do not reopen without new data)

- Blind NSC novelty mining: NO-GO — ADAM::THOR ran 100% of NSC DR2 (~27.5k candidates); CANFind DR2 ~600k SSOs; faint slow movers are image-domain (DES/DEEP/YOSO) + Rubin. `novelty_gate/REPORT.md`.
- DASCH dippers (R2): supply collapse; trigger = future bright V≲13.5 long-eclipse event.
- Short single-opp distant arcs (<~40 d at >30 AU): dynamically lost (pilot); SMIA pre-gate mandatory.
- Stellar/compact-object archival frame: frozen for Gaia DR4 (2 Dec 2026) — see RESEARCH_LOG 2026-07-05.

## Queue after in-flight work

- Wave 4 DONE (3/3 null). Next pool (optional, user decides): repaired full re-cut over the
  remaining ~90 gate passers with rules 7+8 AND the new rules 10+11 baked into the cut itself
  (require ≥2 post-arc imaging nights with baseline before a target is even dispatched).
- KK76 pointed-HST 2010 WFC3 field: revisit with the 2006-refined orbit (bounded non-detection could become a localization).
