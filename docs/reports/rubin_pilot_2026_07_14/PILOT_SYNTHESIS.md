# Rubin pilot synthesis — rank 1 (Lasair-LSST watchlists) + rank 2 (unadopted-tail forensics)

Run 2026-07-14 → 2026-07-15 (workflow wf_021e692e-c83, 13 agents, ~1.37M tokens;
survived two session-limit interruptions via resume-from-cache). All five forensics
dossiers independently refereed; **all five verdicts stand**. Referee-mandated package
corrections applied main-thread 2026-07-15 (see per-package notes below).

## Verdicts

- **Gate 1 (year-1 artifact ratio): PASS** — measured, not assumed. 772 flags/6 nights
  (MJD 61228–61235); stratified vetted n=40 → 37.5% artifact overall, but strongly
  channel-dependent: hostless/ELEPHANT 0/10 artifact, bright lt20mag 0/10 artifact
  (7/10 non-transient — 5 AGN + 2 variables — but real; corrected 2026-07-15 from
  "6/10" during RNAAS drafting, per flags_sample.csv), faint extragalactic_new 15/20
  artifact (year-1 incremental-template residuals). Condition: restrict lane to the
  pure channels until DR1 templates.
- **Gate 2 (demonstrated consumer): PREPARED, mechanisms live-verified** — four
  referee-audited consumer packages on disk; actual ingestion = USER filing (project
  guardrail). In-sample proof the loop works: same-night Rubin hostless object became
  SN 2026uid only after FLEET filed to TNS. If the user does not file within the useful
  window, next re-run treats gate 2 as untested.
- **Lane recommendation: PROCEED** (conditions: pure channels only; gate-2 completion
  requires an actual filing; rank-1 watchlists user-gated on Lasair registration).
- Kill-rule check: the week's bottleneck was vetting/refereeing labor, not telescope
  access — satisfied by direct experience.

## Per-candidate (all referee: stands)

| diaObjectId | verdict | one-line |
|---|---|---|
| 170587105461272950 | INTERESTING | Unreported SN-like transient (=ZTF26abfwqfp, 0.12″), fell between Fink-hostless + ALeRCE-"bogus" heuristics; TNS AT draft ready; near peak i~20.75 — TIME-SENSITIVE |
| 170635519425249637 | INTERESTING | Still-active unreported SN II-plateau candidate; ZFPS recovers it 22 d before Rubin's first alert; TNS AT draft ready — TIME-SENSITIVE |
| 170591519677875016 | INTERESTING | Month-long blue transient, ATLAS pre-discovery ≥16 d; Rubin template reveals r=23.96 sub-archival counterpart → ELEPHANT "hostless" is depth-limited; Fink-feedback + AstroNote drafts ready |
| 170587115976392822 | INTERESTING | =ZTF19abxfaon: uncatalogued 8-yr ~5.2-mag state-cycling variable, best read CV (ALeRCE ZTF FP classifiers CV/Nova 0.95–0.97); AstroNote + VSX drafts ready (time-axis corrections APPLIED 2026-07-15) |
| 170591507978387512 | MUNDANE | Real SN near peak on faint compact counterpart; CV/precursor hypothesis killed at pixel level (PS1 "precursors" = masked-pixel artifacts, rule 10 ported to PS1) |

## Referee-mandated corrections applied (2026-07-15, main thread)

- **-950:** atlas_fp.csv regenerated in consumer_package/ from completed ATLAS task
  4542361 (4,525 epochs; 0/1,023 pre-event nightly stacks ≥4σ with chi/N≤4 cut; the two
  raw >5σ single epochs are rule-10 non-reproducing artifacts). Stale task-ids fixed in
  atlas_task_url.txt + ANNOTATION.txt; TNS remarks now cite the real file.
- **-822:** three time-axis errors fixed in astronote_draft.md + vsx_draft.md (peak
  zr=17.976 at MJD 59218.078 = 2021-01-04, NOT ~59470; first bright detection
  zr=21.24±0.26 at 58285.400, not 20.5; season-conflation wording); ALeRCE CV/Nova
  0.95–0.97 strengthener added. FILING UNBLOCKED.
- **-637:** "atlas_precursor_mjd" mislabel → "atlas_pre_rubin_confirmation_mjd";
  ZTF-r-vs-Rubin-r ~0.4 mag calibration caution + stacks-vs-single-exposures label
  caution appended to TNS draft.
- **-016:** template-epoch caveat appended to annotation.txt + tns_astronote_draft.md
  (quiescent-counterpart interpretation assumes templates predate onset — unverified).

## Rank 1 (watchlists)

Both CSVs built + provenance-tracked (watchlists/): ao-dormant-co-2026.csv (13 rows,
PM-propagated to J2026.5, per-row radii) + ao-known-objects-2026.csv (19,168 rows from
11 curated catalogs; VSX/Milliquas bulk correctly excluded). Creation is web-UI-only
(no REST endpoint) and user-gated. **Token gate RESOLVED downstream of rank-1:** live
LSST instance = lasair.lsst.ac.uk (lasair-lsst.lsst.ac.uk serves mismatched TLS); the
ZTF-era token returns **401 Invalid token** there while still valid on lasair-ztf —
the community-scan "token does not transfer" prediction is now measured. Solar-system
movers deliberately excluded (static cones cannot track them; SSP handles SSOs).

## USER actions (in priority order)

TIME-SENSITIVE (days):
1. File TNS AT for 170587105461272950 (consumer_package/TNS_AT_REPORT_DRAFT.md;
   package corrected, file-ready; sandbox first). Object near peak.
2. File TNS AT for 170635519425249637 (consumer_package/TNS_AT_report_draft.md;
   corrected). Still active.

STANDARD:
3. 170587115976392822: file TNS AstroNote + VSX entry (drafts corrected; VSX needs
   your AAVSO account — community-scan lane #3 action).
4. 170591519677875016: email Fink the template-flux feedback (annotation.txt; literal
   contact@fink-broker.org unverified — use portal/Slack if it bounces); optional TNS
   draft (caveat added).

LASAIR (unlocks rank 1 + annotation consumer path):
5. Register personally on lasair.lsst.ac.uk; save new token to ~/.config/lasair/token
   (mode 600).
6. Create watchlists ao-dormant-co-2026 + ao-known-objects-2026 from watchlists/
   (UI upload; email Lasair team on Gateway Timeout); tick active.
7. Request an annotator topic (needs Lasair-team approval).

NOTE: ZFPS is bound to the TU Delft email; results also arrive as browser downloads
(all six 2026-07-14/15 light curves preserved + analyzed in zfps/).

All filings carry the adopted disclosure: algorithm-found / human-refereed / user-filed.

## Learnings (banked)

1. Lasair topology measured: live instance lasair.lsst.ac.uk; token does NOT transfer;
   watchlist creation UI-only.
2. Year-1 artifact rate is a CHANNEL property, not a stream property — lane viability
   comes from channel selection.
3. Unadopted-tail hypothesis validated mechanistically: real transients fall between
   broker heuristics; TNS adoption is literally "someone files."
4. Year-1 stamp classifiers are the weakest link (ALeRCE "bogus"/"asteroid"/"AGN"
   miscalls on all four interesting objects); multi-night persistence + forced
   photometry beat stamps.
5. ZTF/ATLAS forced photometry is the decisive archival lever (recovered events 16–22 d
   before Rubin; killed every false precursor). ZFPS procstatus 56/57 are warnings, not
   failures (parsing lesson in zfps/ZFPS_ANALYSIS.md).
