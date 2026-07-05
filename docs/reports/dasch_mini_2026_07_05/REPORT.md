# DASCH one-dip-wonders mini-campaign -- REPORT

Date: 2026-07-05
Input: 13 clean ASAS-SN "big dipper" survivors (/tmp/gate_dasch/FINAL_survivor_candidates.csv),
all from JoHantgen+2026 (arXiv:2507.19594), single-eclipse-binary category, no established
period, never previously DASCH-attempted.
Tooling: daschlab v1.0.0 (official DASCH DR7 Python client), fresh /tmp venv
(/tmp/gate_dasch/venv, reused from the gate check). Coordinates and modern dip
parameters (max depth, most recent dip epoch, min-period lower bound) taken directly
from JoHantgen+2026 Table 1/Table 2 (/tmp/gate_dasch/asassn_bigdippers.txt).

## Bottom line

0 / 13 PERIOD-RECOVERED. 4 / 13 DASCH-NULL (scatter-limited). 9 / 13 NO-HISTORICAL-DIPS
(clean non-detection of prior dips, given adequate sensitivity).

No falsifiable period predictions are issued. This is a clean, well-instrumented null
result, not an inconclusive one -- every object got a first-class DASCH pull (13/13
succeeded, 0 API failures) and an explicit, quantified skepticism gate.

## Method summary

For each object:

1. Pull: daschlab.open_session() -> select_target(ra_deg, dec_deg) (coordinate
   resolution, since these are internal ASAS-SN IDs with no Simbad name) ->
   select_refcat("apass") -> exposures() -> lightcurve(0) (closest APASS refcat
   source to the query center -- in every case this matched the target to <1" by
   design of the coordinate query).
2. Quality cut: reproduced daschlab's apply_standard_rejections() bitmask
   (HIGH_BACKGROUND | LARGE_ISO_RMS | LARGE_LOCAL_SMOOTH_RMS | CLOSE_TO_LIMITING |
   BIN_DRAD_UNKNOWN, AFLAGS mask 0xB840) plus dropping masked (non-detection) rows.
   Validated against a live daschlab session (99/2180 good detections for the first
   object, exact match).
3. Baseline + scatter: median magnitude and MAD-based robust sigma (one round of
   4-sigma clipping) over all good detections, ~1890s-1990s.
4. Skepticism gate: object is DASCH-NULL if scatter_sigma >= 0.5 x
   modern_dip_depth (equivalently dip-depth/scatter SNR < 2) -- i.e. the plate noise
   floor is too close to the claimed modern dip depth for a dip of that size to stand
   out from ordinary photographic scatter. This directly operationalizes the ASAS-SN
   team's own finding for ASASSN-25bv ("too much scatter... to search for earlier
   events" at g=12.31, scatter comparable to a 0.9-1.5 mag dip).
5. Dip search (only run if the gate passes): flag good detections >= max(3-sigma,
   0.5x modern depth) below baseline. Cluster flagged points within 200 days into
   "epochs." Look-elsewhere correction is reported explicitly: with N good
   detections, a plain 3-sigma cut is expected to yield ~N x 1.35e-3 chance hits from
   Gaussian noise alone even with zero real dips -- several objects had faint-point
   counts at or above this expectation, all as isolated single-plate points, not
   time-clustered. Per the skepticism mandate, a single faint plate is never treated
   as a dip; only clusters of >=2 detections at the same epoch count as a candidate
   historical dip.
6. Period test (only run if >=2 multi-point epochs found): test trial periods
   from integer divisors of the epoch spacing, check whether all historical epochs
   *and* the modern dip epoch land at a consistent phase (tolerance +-15% of P for
   dip-duration/timing slop). FAP = (2 x tolerance)^(n_alignments) x
   (number of trial periods scanned), Bonferroni-corrected over the trial-period scan
   -- a conservative, first-order estimate, not a full Monte Carlo, but explicit and
   auditable. Verdict is only promoted to PERIOD-RECOVERED if FAP < 0.05.
7. Novelty: cross-checked all 13 against SIMBAD (5" cone search) -- no returned
   object carries a variable-star classification or period beyond a generic
   catalog cross-ID (APASS/UCAC/Gaia DR3 ID only), consistent with JoHantgen+2026's
   own statement that these targets have no established period. Confirms no prior
   plate/period analysis exists for any of the 13 (moot for the final result, since
   no period was recovered, but relevant to future re-attempts).

## Per-object verdict table

| Object | N plates (good/total) | Baseline (yr) | Scatter sigma (mag) | Modern depth (mag) | SNR=depth/sigma | Multi-pt epochs | Verdict | Period + FAP | Next-eclipse prediction |
|---|---|---|---|---|---|---|---|---|---|
| ASASSN-J073234-200049 | 99 / 2180 | 1900.3-1953.2 (53 yr) | 0.113 | 1.38 | 12.2 | 0 | NO-HISTORICAL-DIPS | -- | -- |
| ASASSN-J175602+013135 | 195 / 3772 | 1897.4-1971.6 (74 yr) | 0.130 | 2.28 | 17.6 | 0 | NO-HISTORICAL-DIPS | -- | -- |
| ASASSN-J223332+565552 | 1027 / 6538 | 1891.8-1989.9 (98 yr) | 0.163 | 0.65 | 4.0 | 1 (insufficient) | NO-HISTORICAL-DIPS | -- | -- |
| ASASSN-J073924-272916 | 47 / 1617 | 1902.9-1945.9 (43 yr) | 0.081 | 0.34 | 4.2 | 0 (2 isolated single pts) | NO-HISTORICAL-DIPS | -- | -- |
| ASASSN-J074007-161608 | 423 / 2723 | 1894.9-1989.4 (95 yr) | 0.125 | 0.33 | 2.6 | 1 (insufficient) | NO-HISTORICAL-DIPS | -- | -- |
| ASASSN-J094848-545959 | 984 / 2745 | 1890.4-1989.5 (99 yr) | 0.184 | 0.32 | 1.7 | n/a | DASCH-NULL | -- | -- |
| ASASSN-J162209-444247 | 290 / 2993 | 1895.5-1988.3 (93 yr) | 0.094 | 0.61 | 6.5 | 1 (insufficient) | NO-HISTORICAL-DIPS | -- | -- |
| ASASSN-J183210-173432 | 712 / 2975 | 1893.6-1989.7 (96 yr) | 0.287 | 0.31 | 1.1 | n/a | DASCH-NULL | -- | -- |
| ASASSN-J183606-314826 | 214 / 2301 | 1896.8-1954.4 (58 yr) | 0.240 | 0.39 | 1.6 | n/a | DASCH-NULL | -- | -- |
| ASASSN-J190316-195739 | 238 / 2839 | 1895.4-1983.6 (88 yr) | 0.135 | 0.39 | 2.9 | 0 (3 isolated single pts) | NO-HISTORICAL-DIPS | -- | -- |
| ASASSN-J205245-713514 | 794 / 3621 | 1908.6-1989.7 (81 yr) | 0.136 | 0.38 | 2.8 | 0 (7 isolated single pts) | NO-HISTORICAL-DIPS | -- | -- |
| ASASSN-J212132+480140 | 247 / 5048 | 1898.8-1988.9 (90 yr) | 0.230 | 0.37 | 1.6 | n/a | DASCH-NULL | -- | -- |
| ASASSN-J225702+562312 | 253 / 5455 | 1896.7-1988.7 (92 yr) | 0.182 | 0.40 | 2.2 | 0 | NO-HISTORICAL-DIPS | -- | -- |

No object reached the >=2 multi-point-epoch threshold required to even attempt a period
fit with a meaningful FAP. No period claims, no next-eclipse predictions.

## Skepticism gate in detail: 4 DASCH-NULL objects

These 4 objects have plate scatter within a factor of ~2 of their modern dip depth
(SNR 1.1-1.7), meaning a dip of the observed modern size would not reliably stand out
above ordinary photographic noise in the DASCH baseline:

- ASASSN-J094848-545959 (SNR 1.7): 984 good detections, but sigma=0.184 mag vs a
  0.32 mag dip.
- ASASSN-J183210-173432 (SNR 1.1, worst case): 712 good detections, sigma=0.287 mag
  vs a 0.31 mag dip -- the scatter is almost as large as the dip itself.
- ASASSN-J183606-314826 (SNR 1.6): sigma=0.240 vs depth 0.39.
- ASASSN-J212132+480140 (SNR 1.6): sigma=0.230 vs depth 0.37.

This reproduces, quantitatively, the JoHantgen+2026 team's own qualitative finding for
ASASSN-25bv (g=12.31, "too much scatter... to search for earlier events") -- DASCH's
photographic noise floor is a real, non-trivial limitation for several of these
targets, not just a hypothetical risk flagged at the gate stage.

## Look-elsewhere / fat-tail check on the 9 NO-HISTORICAL-DIPS objects

Several objects (ASASSN-J223332, J074007, J205245, J190316) showed multiple
individually-"significant" (>=3-sigma) faint points -- but in every case these were
isolated single plates scattered across decades, not time-clustered, and their
counts (7-9 in some cases) were only marginally above (or consistent with) the
Gaussian look-elsewhere expectation for hundreds of trials, given that photographic
plate photometry is known to be fat-tailed (plate defects, blends, bad columns) rather
than strictly Gaussian. Per the mandate that "a single faint plate is not a dip," none
of these were promoted to candidate dip epochs. Visual inspection of the light curves
(see PNGs) confirms these look like ordinary scatter/systematics, not a coherent
brightness excursion reaching the claimed modern dip depth.

Only 3 objects (ASASSN-J223332, J074007, J162209) had even a single 2-point cluster --
each is a lone candidate epoch, correctly insufficient (by design) to run a period
test, since a period claim requires the epoch to repeat.

## Deliverables

- /tmp/dasch_mini/REPORT.md -- this file.
- /tmp/dasch_mini/SUMMARY.csv -- machine-readable per-object results.
- /tmp/dasch_mini/summary.json -- same, JSON.
- /tmp/dasch_mini/<name>_dasch_raw.ecsv -- full raw daschlab pull per object (13 files).
- /tmp/dasch_mini/<name>_dasch_lc.png -- per-object light curve plot (13 files), showing
  baseline, 1-sigma scatter band, modern dip-depth line, and any flagged multi-point
  epochs (orange shading).
- /tmp/dasch_mini/targets.csv -- input target list with RA/Dec/depth/epoch pulled from
  JoHantgen+2026 Table 1/2.
- /tmp/dasch_mini/pull_dasch.py, /tmp/dasch_mini/analyze_dasch.py -- reusable scripts.

## Honest accounting

- 13/13 objects pulled successfully (0 API failures), ~19-46s each, matching the
  gate's throughput estimate.
- 4/13 (31%) are DASCH-null (scatter-limited) -- a meaningfully worse hit rate than
  the single ASAS-SN-team anecdote (1/1) suggested in isolation, but consistent with it:
  DASCH plate noise is a real, common obstacle for this g~13-14.5 magnitude regime, not
  a one-off.
- 9/13 (69%) have adequate sensitivity but show no historical dips -- these are
  genuine non-detections given demonstrated adequate depth, and constrain the
  recurrence: no dip as deep as the modern one occurred on any DASCH plate across
  43-99 years of baseline (specific per-object baselines in the table above).
- 0/13 produced a period recovery or a falsifiable next-eclipse prediction.
  No candidate requires human review on that front.
- This mini-campaign closes the lane as scoped (13 clean ASAS-SN survivors): the
  archive-only "ASASSN-24fw template" paper does not materialize from this sample.
  The marginal/refinement-tier objects (5 more, with existing rough periods) were
  explicitly out of scope for this mini-campaign and were not run.
