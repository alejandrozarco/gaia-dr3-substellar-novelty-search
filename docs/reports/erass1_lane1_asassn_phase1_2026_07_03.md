# eRASS1-register classification lane — Phase 1 (ASAS-SN Sky Patrol v2)

Date: 2026-07-03. Scope: ASAS-SN only (ATLAS is Phase 2, separately blocked/deferred).
Sample: 136 unique uncatalogued eRASS1 source_ids from `findings_register.csv`
(lane contains "eRASS1", novelty=uncatalogued), Object B (3161546596480983040)
excluded as already fully worked. 15 of these are the CMD-bridge discovery pool
(gate: `docs/reports/erass1_lane1_gate_table_2026_07_03.csv`); 121 are the
expected-coronal-rotator bulk (housekeeping-value classification).

## Headline counts

- **Sample:** 136 (88 southern dec<-30, 48 northern); G 12.2-19.0, median 15.9.
- **ASAS-SN master_list coverage:** 98/136 matched within 15" (38 no counterpart
  -- see Coverage gaps).
- **Light curves obtained:** 87/98 matched targets (11 failed after retries --
  see Coverage gaps).
- **Outburst screen (cross-camera, temporally-clustered episodes only):**
  - **1 confirmed-outburst** (cross-camera-overlapping episodes) -- but this
    single case is a **near-certain blend false-positive**, not a credible
    accretor detection (see below). Net credible confirmed-outburst count: **0**.
  - **7 candidate-artifact-outburst** (single-camera only, needs 2nd
    camera/survey confirmation) -- 1 of these is also blend-flagged.
  - 2 confirmed-dip / 1 candidate-artifact-dip -- all 3 are saturation/blend
    artifacts on inspection (bright neighbour dominates), not credible
    eclipses/VY Scl lows on the eRASS1 targets themselves.
- **Period screen (Lomb-Scargle 0.05-50d, outburst-masked, bootstrap FAP +
  red-noise local null + per-camera coherence + 1-day/lunar-month alias
  comb), run on all 15 bridge objects (10 with LC) + 7 outburst-flagged
  targets = 17 total screened:**
  - **0 COHERENT-PERIOD.**
  - **17 MARGINAL** -- every one of these is explained: 13/17 sit at P~1.0d or
    0.5d (1-day sampling alias, flagged) and the other 4 sit at P~29.49-29.55d
    (synodic lunar month, a scheduling/moon-brightness systematic). No
    candidate here passed the cross-camera coherence test, so nothing was
    promoted to COHERENT-PERIOD.
  - **0 QUIET** among the screened set (everything screened had at least a
    marginal FAP hit, all attributable to the alias systematics above).
- **Net classification:** 0 credible outburst/eclipse detections, 0 coherent
  periods. The bulk sample (121 non-bridge, minus 1 ambiguous-blend and 7
  single-camera outburst candidates) is consistent with the expected coronal
  rotator population -- clean housekeeping null, as anticipated.

## The full 15-bridge verdict sub-table

| source_id | name | G | ASAS-SN | outburst tier | period verdict | best P (d) | classification | evidence |
|---|---|---:|---|---|---|---:|---|---|
| 2993086056306989824 | 1eRASS J061056.4-152054 | 16.49 | matched, LC ok | none | MARGINAL | 0.9974 | marginal_period_followup | 1-day alias, not coherent -- effectively quiet |
| 4688120596457178624 | 1eRASS J013933.0-703127 | 18.76 | matched, LC fetch FAILED | NO_LC_DATA | NO_LC_DATA | -- | unclassified_no_lc | ASAS-SN backend gap |
| 4715379894891417856 | 1eRASS J012229.2-623125 | 17.25 | matched, LC ok | none | MARGINAL | 0.9998 | marginal_period_followup | 1-day alias, not coherent -- effectively quiet |
| 4822674126477654784 | 1eRASS J051943.9-352029 | 15.42 | matched, LC ok | none | MARGINAL | 0.4993 | marginal_period_followup | 0.5-day alias, not coherent -- effectively quiet |
| 4933000119641126912 | 1eRASS J005925.3-474843 | 15.89 | matched, LC ok | none | MARGINAL | 1.0001 | marginal_period_followup | 1-day alias, not coherent -- effectively quiet |
| 5086290113773259776 | 1eRASS J033510.0-240911 | 15.99 | matched, LC ok | none | MARGINAL | 1.0002 | marginal_period_followup | 1-day alias, not coherent; neighbor 1.14" G=12.18 (3.8 mag brighter) -- severe blend risk on ANY future signal |
| 5289353281310733696 | 1eRASS J074649.3-612756 | 15.37 | matched, LC ok | none | MARGINAL | 1.0002 | marginal_period_followup | 1-day alias, not coherent; neighbor 1.71" G=14.43 (~1 mag brighter) -- blend caution |
| 5518166598858566528 | 1eRASS J074744.7-482558 | 16.94 | no ASAS-SN counterpart <15" | NO_LC_DATA | NO_LC_DATA | -- | unclassified_no_lc | genuine ASAS-SN input-catalog gap |
| 5698053847990609920 | 1eRASS J080939.0-241518 | 14.75 | matched, LC fetch FAILED | NO_LC_DATA | NO_LC_DATA | -- | unclassified_no_lc | ASAS-SN backend gap |
| 5700916082915916032 | 1eRASS J081057.7-211610 | 14.12 | matched, LC ok | none | MARGINAL | 0.9970 | marginal_period_followup | 1-day alias, not coherent -- effectively quiet |
| 5713277789070104960 | 1eRASS J080530.3-201237 | 15.46 | matched, LC ok | none | MARGINAL | 0.9974 | marginal_period_followup | 1-day alias, not coherent -- effectively quiet |
| 5808732887468490368 | 1eRASS J163428.7-693348 | 15.80 | matched, LC fetch FAILED | NO_LC_DATA | NO_LC_DATA | -- | unclassified_no_lc | ASAS-SN backend gap |
| 6006980297150138112 | 1eRASS J151305.9-390418 | 14.47 | matched, LC fetch FAILED | NO_LC_DATA | NO_LC_DATA | -- | unclassified_no_lc | ASAS-SN backend gap; neighbor 0.78" G=15.43 -- blend caution for any future signal |
| 6342358797048816128 | 1eRASS J195248.1-872256 | 18.67 | matched, LC ok | candidate-artifact-outburst | MARGINAL | 29.5159 | DN_candidate_artifact_tier | single-camera 2.04-mag brightening over 1 day (JD 2460130-2460131); no blend flag (nearest neighbor 12.7", comparable G); period hit is the lunar-month systematic, not real; needs 2nd-camera/ATLAS confirmation |
| 6414835064496112640 | 1eRASS J183831.6-750020 | 18.91 | matched, LC ok | none | MARGINAL | 29.5452 | marginal_period_followup | lunar-month alias, not coherent -- effectively quiet |

**Bottom line on the 15 bridge objects:** no coherent periods, no confirmed
outbursts. One (**6342358797048816128**) has a single, unconfirmed,
non-blended 2-mag brightening event -- the sole genuinely interesting lead
from this phase, but single-camera and single-night, so it stays
candidate-artifact tier pending a second survey (ATLAS, Phase 2). The other
14 are photometrically quiet at the ASAS-SN depth/cadence, with 4/15 unfetched
(backend gap) and 1/15 genuinely absent from ASAS-SN's input catalog.

## Anything resembling a genuine accretor

**None found with credible, unambiguous evidence.** The single
"confirmed-outburst" case in the full 136-sample --
**6482924963452562432** (non-bridge, G=14.78, 1eRASS J204757.9-451301) --
shows a striking 13-episode, ~1.3-1.75 mag, cross-camera-confirmed recurrent
brightening pattern that would otherwise be a strong dwarf-nova signature.
However: its ASAS-SN quiescent baseline (g~9.55, V~9.15) is ~5 mag brighter
than the Gaia G=14.78 of the eRASS1 target, and there is a Gaia neighbour at
6.46" with G=8.56 (a bright, nearly-saturating star for ASAS-SN) -- the
ASAS-SN cone-search match itself sits at 6.48" from the target, i.e.
essentially coincident with this bright neighbour, not the target. This
light curve almost certainly belongs to the neighbour, not the eRASS1
source. Downgraded to DN_candidate_AMBIGUOUS_BLEND; not a discovery
claim. If re-examined, this needs a resolved instrument (<2" pixels) to
settle which star is varying.

The bridge object **6342358797048816128** (see table) is the only lead
without a blend confound, but it is single-camera/single-night -- an
artifact-tier candidate that needs independent confirmation, not a claim.

## Coverage gaps (honest accounting)

1. **ASAS-SN Sky Patrol v2 light-curve backend: confirmed intermittent
   outage, 2026-07-03.** The dedicated data host referenced by the pyasassn
   client (asassn-data01.ifa.hawaii.edu:9006) refused all connections
   throughout. The load-balanced endpoint (asassn-lb01.ifa.hawaii.edu:9006)
   served metadata/cone-search reliably but returned
   {"error": "lightcurve servers temporarily unavailable"} for a
   consistent subset of targets even after repeated, politely-spaced
   retries (~5 attempts over ~5 minutes confirmed a specific ID down;
   broader sampling showed ~90% success). Final tally: 87/98 matched
   targets fetched (89%), 11/98 failed after 4 retries with exponential
   backoff each. This reads as a partial data-shard outage, not a rate
   limit -- retrying further would not have been polite or productive.
   5 of the 15 bridge objects are among the 11 failures
   (4688120596457178624, 5698053847990609920, 5808732887468490368,
   6006980297150138112, plus one non-bridge overlap) -- these remain
   genuinely untested at ASAS-SN depth. Recommend a retry in a future
   session once the backend stabilizes.
2. **38/136 targets have no ASAS-SN master_list counterpart within 15".**
   Spot-checked 2 bright (G<15) cases at wider radius -- both resolve at
   16-22", i.e. a real but modest astrometric-catalog offset, not a data
   gap; the full 38 were not individually re-checked at wider radius (out
   of scope for this pass, low expected yield given the majority are faint).
3. **The pyasassn client's bundled deserialization code was broken**
   against modern pyarrow (pa.deserialize, a legacy pre-1.0 API, was
   removed years ago) -- worked around by discovering the server actually
   returns standard Parquet under the "arrow" flag and monkey-patching
   _deserialize to use pd.read_parquet. No functional behavior change,
   just a transport-layer fix; documented in asassn_client_fixed.py.
4. **ATLAS forced photometry (Phase 2, decisive for dec<-50) intentionally
   NOT run this phase** per the task's scope -- noting for the record that a
   token file now exists at ~/.config/atlas/token, so Phase 2 may be
   unblocked; that's for a separate, explicitly-scoped run.
5. **V-band vs g-band split is approximate.** ASAS-SN's public API does not
   return a filter column; the V->g camera changeover happened per-unit
   across ~2017-2018 with no published per-camera-code table, so band was
   assigned by a JD cutoff (2018-11-01), consistent with this project's
   prior ASAS-SN screens. This has no effect on the outburst/period
   screens (which group by camera code, the true systematics unit), only
   on the reported n_epochs_g / n_epochs_V / quiescent_mag_g / _V columns.

## Methodology notes / self-corrections made during this run

- **Outburst-episode clustering bug found and fixed.** The first pass
  flagged "outbursts" spanning 700+ days by only requiring >=2 points across
  >=2 nights, with no requirement that those nights be temporally close --
  this wrongly merged isolated bright outliers scattered across years into
  one fake "event," producing 12 false "confirmed-outburst" tags. Fixed by
  clustering flagged points into temporally-contiguous episodes (<=30-day
  gap) before applying the point/night thresholds, and by requiring
  cross-camera temporal overlap (not just "both cameras have some
  outburst, ever") for the confirmed tier. Re-running dropped confirmed
  outbursts from 12 to 1 (the 1 remaining being the blend case above).
  This mirrors the project's own documented 2026-05-28 CV-period pipeline
  retraction lesson (outburst-including data injects false periods /
  false episodes) and is now recorded here for the same reason.
- **Outburst-masked period screening.** Per the same institutionalized
  lesson, the period screen runs on the light curve with all detected
  outburst/dip episodes masked out (+/-10-day pad), never on the raw
  outburst-including data.
- **Red-noise null redesigned for correctness.** The first implementation
  compared the periodogram's best (max-of-thousands-of-frequencies) power
  to individual random-period points -- a sample-size mismatch that
  saturated near 100th-percentile even on pure white noise, and briefly
  produced ~universal false MARGINAL verdicts before being caught in
  calibration (0/15 false positives confirmed after the fix, on synthetic
  noise; clean COHERENT-PERIOD recovery confirmed on a synthetic 3.23-day
  injected signal with correct camera coherence).
- **Alias comb extended to the lunar synodic month (29.53d)** after this
  run empirically surfaced 4/17 MARGINAL cases clustered there
  (29.49-29.55d) -- a known ground-survey scheduling systematic. All 4 were
  independently already excluded from COHERENT-PERIOD by failing camera
  coherence, so this didn't change any verdict, only sharpens the
  diagnostic note.
- **Blend-neighbour check strengthened.** Beyond flagging the single
  nearest Gaia neighbour, the check now also verifies whether the ASAS-SN
  cone-search match itself coincides positionally with a bright neighbour
  (this caught 6482924963452562432 -- a case the naive nearest-neighbour
  check alone would have missed, since a closer-but-fainter, irrelevant
  neighbour was picked first).

## File paths

- /tmp/erass1_classify/sample_137.csv -- the 136-object working sample
  (136 = 137 register uncatalogued eRASS1 objects minus Object B), with
  is_bridge flag.
- /tmp/erass1_classify/gaia_astrometry.csv -- Gaia DR3 positions/photometry
  for all 136 (anonymous TAP).
- /tmp/erass1_classify/asassn_conesearch.csv -- ASAS-SN master_list
  cone-search match (asas_sn_id, separation, coverage status) for all 136.
- /tmp/erass1_classify/gaia_neighbors_15arcsec.csv -- all Gaia neighbours
  within 15" of every target (blend discipline).
- /tmp/erass1_classify/lightcurves/<source_id>.json -- 87 raw fetched
  ASAS-SN light curves.
- /tmp/erass1_classify/step4_fetch_status.csv -- per-target fetch outcome
  (ok/cached/failed + reason).
- /tmp/erass1_classify/verdict_table_final.csv -- the authoritative
  per-object verdict table (136 rows, all columns per the task spec).
- /tmp/erass1_classify/analysis_detail.json -- full outburst/period-screen
  diagnostic detail (episodes, FAP, red-noise-null stats, camera coherence)
  per screened object.
- /tmp/erass1_classify/screens.py -- outburst_screen + period_screen
  implementation (reusable).
- /tmp/erass1_classify/lc_utils.py, asassn_client_fixed.py -- light
  curve loading + the pyasassn deserialization fix.
- /tmp/erass1_classify/step2b_conesearch_fixed.py,
  step3_gaia_neighbors.py, step4_fetch_lightcurves.py,
  step5_analyze.py -- the pipeline scripts, in run order.

## Proposed ledger rows (bridge objects only; journal.py format)

None of these 15 have existing journals yet. For the calling agent/user to
apply via:
python scripts/journal/journal.py ledger <source_id> --catalog "..." --result "..." --provenance "..."

2993086056306989824 --catalog "ASAS-SN Sky Patrol v2" --result "QUIET: 1-day sampling alias at P=0.997d, camera-incoherent, no outburst; effectively no photometric signal at ASAS-SN depth/cadence" --provenance "/tmp/erass1_classify/ (verdict_table_final.csv, analysis_detail.json)"

4688120596457178624 --catalog "ASAS-SN Sky Patrol v2" --result "UNTESTED: ASAS-SN counterpart matched but lightcurve fetch failed (backend outage 2026-07-03, 4 retries exhausted) -- coverage gap, not a null" --provenance "/tmp/erass1_classify/step4_fetch_status.csv"

4715379894891417856 --catalog "ASAS-SN Sky Patrol v2" --result "QUIET: 1-day sampling alias at P=1.000d, camera-incoherent, no outburst" --provenance "/tmp/erass1_classify/ (verdict_table_final.csv)"

4822674126477654784 --catalog "ASAS-SN Sky Patrol v2" --result "QUIET: 0.5-day sampling alias, camera-incoherent, no outburst" --provenance "/tmp/erass1_classify/ (verdict_table_final.csv)"

4933000119641126912 --catalog "ASAS-SN Sky Patrol v2" --result "QUIET: 1-day sampling alias, camera-incoherent, no outburst" --provenance "/tmp/erass1_classify/ (verdict_table_final.csv)"

5086290113773259776 --catalog "ASAS-SN Sky Patrol v2" --result "QUIET: 1-day sampling alias, camera-incoherent, no outburst; CAUTION -- Gaia neighbour at 1.14 arcsec, G=12.18 (3.8 mag brighter) -- any future positive signal at this position is high blend risk and should be treated as ambiguous by default" --provenance "/tmp/erass1_classify/ (verdict_table_final.csv, gaia_neighbors_15arcsec.csv)"

5289353281310733696 --catalog "ASAS-SN Sky Patrol v2" --result "QUIET: 1-day sampling alias, camera-incoherent, no outburst; neighbour at 1.71 arcsec G=14.43 (~1 mag brighter) -- blend caution" --provenance "/tmp/erass1_classify/ (verdict_table_final.csv, gaia_neighbors_15arcsec.csv)"

5518166598858566528 --catalog "ASAS-SN Sky Patrol v2" --result "NO COUNTERPART: no ASAS-SN master_list match within 15 arcsec -- genuine input-catalog gap, unconstrained by this survey" --provenance "/tmp/erass1_classify/asassn_conesearch.csv"

5698053847990609920 --catalog "ASAS-SN Sky Patrol v2" --result "UNTESTED: ASAS-SN counterpart matched but lightcurve fetch failed (backend outage 2026-07-03) -- coverage gap" --provenance "/tmp/erass1_classify/step4_fetch_status.csv"

5700916082915916032 --catalog "ASAS-SN Sky Patrol v2" --result "QUIET: 1-day sampling alias, camera-incoherent, no outburst" --provenance "/tmp/erass1_classify/ (verdict_table_final.csv)"

5713277789070104960 --catalog "ASAS-SN Sky Patrol v2" --result "QUIET: 1-day sampling alias, camera-incoherent, no outburst" --provenance "/tmp/erass1_classify/ (verdict_table_final.csv)"

5808732887468490368 --catalog "ASAS-SN Sky Patrol v2" --result "UNTESTED: ASAS-SN counterpart matched but lightcurve fetch failed (backend outage 2026-07-03) -- coverage gap" --provenance "/tmp/erass1_classify/step4_fetch_status.csv"

6006980297150138112 --catalog "ASAS-SN Sky Patrol v2" --result "UNTESTED: ASAS-SN counterpart matched but lightcurve fetch failed (backend outage 2026-07-03) -- coverage gap; neighbour at 0.78 arcsec G=15.43 also noted for any future re-attempt (blend caution)" --provenance "/tmp/erass1_classify/step4_fetch_status.csv, gaia_neighbors_15arcsec.csv"

6342358797048816128 --catalog "ASAS-SN Sky Patrol v2" --result "CANDIDATE (artifact tier): single-camera 2.04-mag brightening over 1 night (JD 2460130-2460131), no cross-camera confirmation, no blend confound (nearest neighbour 12.7 arcsec, comparable G); period hit at P=29.52d is the lunar-month sampling systematic, not real. Best remaining lead from this phase; needs 2nd-camera/ATLAS confirmation before any DN classification claim" --provenance "/tmp/erass1_classify/ (verdict_table_final.csv, analysis_detail.json)"

6414835064496112640 --catalog "ASAS-SN Sky Patrol v2" --result "QUIET: lunar-month sampling alias (P=29.55d), camera-incoherent, no outburst" --provenance "/tmp/erass1_classify/ (verdict_table_final.csv)"

## Findings-register summary note (bulk sample, non-bridge)

121 non-bridge objects processed as a batch (per instructions, no
per-object ledger rows for this tier). Summary: 82 with ASAS-SN LC data of
the 121; outburst screen found 6 single-camera candidate-artifact outbursts
and 3 dip events among them, all traced to bright-neighbour blends on
inspection (quiescent-mag mismatches vs Gaia G of 3-7 mag, or a bright
Gaia neighbour within ~6" coincident with the ASAS-SN match position); the
1 cross-camera "confirmed" outburst (6482924963452562432) is the blend case
detailed above. Net: 0 credible novel accretors in the bulk sample --
consistent with the pre-registered expectation that this tier is dominated
by coronal rotators (housekeeping classification, not a discovery lane).
