# Ingestion paths for diaObject 170635519425249637 (drafts only — USER files everything)

Verdict: INTERESTING — real, still-active (last epoch 2026-07-14 08:50 UT), TNS-unreported
SN candidate with a 30-day three-survey forced-photometry light curve and archival nulls.

## Path 1 (primary): TNS AT discovery report — `TNS_AT_report_draft.md`
- WHO consumes it: spectroscopic classification programs (ePESSTO+, SGLF, ZTF-follow-up
  groups) pull targets from TNS; the object is i~21.5 and slowly fading — classifiable now,
  likely too faint in ~2-4 weeks. Time-sensitive.
- MECHANISM: user's own TNS account -> "Report new AT" web form (or sandbox first:
  https://sandbox.wis-tns.org). All required fields prefilled in the draft. No bot needed
  for a single manual report.
- CREDIT: named discovery/report credit on the TNS object page.

## Path 2: Lasair-LSST annotation — `lasair_annotation.txt`
- WHO consumes it: Lasair-LSST users filtering on annotator topics; annotations appear on
  the public object page and are queryable in Lasair filters.
- MECHANISM: register on https://lasair.lsst.ac.uk (GATE RESULT: the old lasair-ztf token
  returns 401 on the LSST instance — a fresh account/token IS required), create an
  annotator topic, then POST /api/annotate/ with the draft text.
- NOTE: this is exactly the "demonstrated consumer" test for the Rubin unadopted-tail lane.

## Path 3 (optional, after 1): TNS AstroNote
- Only if the object gets classified or the pre-discovery story proves useful to others; a
  standalone methods note is below the project's "no standalone incremental note" bar.

## NOT applicable
- VSX: not a periodic variable.
- MPC: stationary to <0.1" over 7 d — not solar-system.

## Duplicates / housekeeping
- ZFPS: two identical requests exist for this position (reqId 479165 = prior run, completed
  and used here; reqId 479183 = today's duplicate, was still queued — harmless, ignore its
  email when it arrives).
- ATLAS FP: prior run's job 4541122 (completed, used here); today's duplicate task 4542396
  was cancelled (HTTP 204) before running.
