# DESI DR1 dark-companion hunt — Phase 1 (RV-variability screen)

Date: 2026-07-05. Gate: PASSED GO (docs/reports/gates_2026_07_05/desi_gate.md).
Status: COMPLETE.

## 1. Route + access

- **Route chosen: bulk per-healpix `rvtab_spectra` FITS download**, streamed
  (download -> extract per-epoch rows -> append to CSV checkpoint -> delete
  FITS immediately). This is the ONLY route with genuine per-epoch
  VRAD/VRAD_ERR/MJD.
- **Astro Data Lab TAP was tested and rejected for this purpose.** Measured
  directly: `desi_dr1.mws` (6,372,607 rows) is COADD-only -- a known
  multi-epoch TARGETID returns exactly 1 row. `desi_dr1.ztile` is per-TILE
  coadd (2 rows for the same test target) but carries no VRAD/VRAD_ERR columns
  at all -- those live only in the RVTAB extension of the per-healpix FITS
  files. TAP is useful for coadd-level science but not this lane.
- **Full pixel enumeration** (not sampled, all 3 main-survey programs):
  main/bright 13,851 pixels, main/dark 13,348, main/backup 4,726 = **31,925
  healpix leaf directories**. Measured avg file size ~500KB(bright)/
  226KB(dark)/598KB(backup) -> ~14.8 GB total raw FITS -- never held on disk
  at once (stream-process-delete), because only ~26-27GB was free in /tmp.
- 24 parallel workers per program (72 total), all 3 programs run concurrently.
  Completed in ~23 minutes wall-clock. Failure rate: 24/31,925 pixel downloads
  (0.075%) hit a transient HTTP 503 after 3 retries -- negligible pixel loss.
- **Result: 5,840,078 good (SUCCESS & epoch-level) rows extracted** across
  bright (3,034,129) + dark (675,303) + backup (2,130,646).

## 2. Funnel

| Stage | N |
|---|---|
| Total good epoch rows extracted | 5,840,078 |
| Distinct Gaia-matched source_ids | 3,723,579 |
| Unique physical stars, >=2 good epochs (merged across programs by Gaia source_id, or by targetid where no Gaia match) | **1,211,271** |
| + baseline >= 1 day (kills same-night pairs) | 931,803 |
| + G in [16, 18.5) | 458,898 |
| + dec > -30 (ZTF-followable) | 458,898 (no further loss -- backup program's Gaia-based footprint is already broad) |
| + p(const RV) < 1e-3 (significant RV variability) | 57,140 |
| + dRV_max >= 5-sigma above combined per-epoch error | 27,043 |
| + RR_SPECTYPE == STAR (drop QSO/GALAXY/blank Redrock coadd class) | 26,429 |
| Known (multi-catalogue front-filter: known_objects store) | 2 (both the same object, see below) |
| Smith (2026) object present in tail? | Yes, 1 (front-filtered out) |
| **NOVEL survivors (final candidates.csv)** | **26,427** |

The **~26,400-strong "novel" tail is NOT 26,400 dark-companion candidates** --
see Section 6. It is the RV-variability-significant, ZTF-followable, G=16-18.5,
single-lined(-ish) tail after the front-filter; the overwhelming majority are
expected to be ordinary stellar binaries, spotted/active stars, or residual
pipeline artifacts. Ranking (FoM) and quality flags below are how the top ~30
were selected for inline reporting and are the recommended starting point for
Phase 2, not a claim that everything below rank ~30 is uninteresting or that
everything above is real.

## 3. Novelty front-filter — what was actually checked, and an honest gap

- `scripts/known_objects` cached store: **1,041,012 rows** -- milliquas
  (1,021,800 QSOs, mostly irrelevant here), garciazamora2023_xp_wd (12,094),
  ritter_kolb (2,156 CVs), downes_cv (1,830), eRASS1/Rodriguez+2025 CV
  cross-matches (~1,700), xp_carbon_stars (451), akras2019_symbiotic (410),
  halbwachs2023_binary_masses_amrf3 (306, published astrometric binary mass
  functions -- directly relevant, checked). Only 2 rows in the whole 26,427-row
  tail matched this store (both the same physical object).
- **GAP, flagged honestly and CONFIRMED by direct testing this session**: the
  store's README documents a VSX cataclysmic subset as seeded, but the live
  store has **zero VSX rows** (`build.py --no-vsx`, documented as
  "big/finicky", was evidently used, or a VSX pull failed silently). A live
  VizieR `B/vsx` cone-search backstop was attempted as a substitute; it
  returned empty even for a known VSX object (Algol) tested directly, and
  independently timed out (60s) on 2/15 real candidates during the shortlist
  check -- **unreliable in this environment, dropped from the default run**.
  **This gap is not hypothetical**: the live SIMBAD backstop on the top 30
  candidates (below) directly caught **3 of the top 17** ranked candidates as
  already-known variable/binary stars with real designations (CRTS/ZTF survey
  IDs) that our front-filter store missed entirely because it has no VSX. Any
  "novel" tag from this pipeline should be read as **"not in our curated store
  + not in SIMBAD" -- NOT "not in VSX."** This is real, demonstrated
  contamination risk on ordinary stellar binaries, not a theoretical caveat.
- **Smith (2026) object**: Gaia DR3 3802130935635096832 front-filtered by
  exact source_id match (RNAAS 10, 25, "A High-amplitude Radial Velocity
  Variable in DESI DR1" -- single-object note, DeltaRV~146-151 km/s over
  38.9 days, itself flagged by its author as needing resolved follow-up to
  rule out a blended 0.688" neighbour rather than a genuine compact companion).
  It was present in the pre-front-filter tail and is now excluded.
- **Method-level prior art** (`scripts/litcheck/prior_art.py`, strict AND):
  zero hits; broad OR fallback surfaced only unrelated DESI cosmology
  (BAO/clustering) papers -- no systematic dark-companion survey paper. A plain
  WebSearch (2026-07-05) corroborated: only the Smith(2026) single-object note
  exists. Niche open; single competitor object already claimed and excluded.

## 4. SB1/SB2 handling

DESI RVS has **no dedicated double-lined-spectrum (SB2) flag** -- confirmed by
reading the Koposov+2026 stellar-catalogue text directly: `RVS_WARN`'s only
documented bit (bit 3, value 8) flags stellar-parameter grid-edge proximity,
not SB2. Used `VSINI > 30 km/s` as an indirect, DEPRIORITIZE-not-DROP proxy
(the paper's OWN quality-cut boundary; K24 recommends VSINI<30 for trusted RVS
use, and a blended/composite spectrum is one common cause of spuriously high
fitted vsini in a single-star template). **383/26,427 (1.4%) candidates
flagged.** This is a soft heuristic, not a real SB2 detector.

## 5. Data-quality reality check (the most important finding of this screen)

A first-pass ranking by raw chi2/significance put **QSO- and GALAXY-classified
Redrock spectra at rank #1-2** -- dropped by adding an explicit
`RR_SPECTYPE == STAR` cut (removed 614 rows).

After that fix, the top of the list was STILL dominated by objects with
**chi2_red in the tens-of-thousands to ~233,000** (for context: the FULL
multi-epoch population, before any RV-significance cut, has median
chi2_red=1.62 -- consistent with correctly-estimated errors). Investigated one
directly (rank 1, source_id 1572335888675471488): CHISQ_TOT/CHISQ_C_TOT
(single-star template fit quality) were 45,939-329,626 -- but this measure
turned out to scale strongly with source brightness across the WHOLE
population (median chisq_tot ~17,400 at G=16 vs ~8,300 at G=18.5), so an
absolute threshold is not meaningful. Built a **G-mag-relative** diagnostic
(`chisq_relative_max` = worst per-epoch CHISQ_TOT / population median CHISQ_TOT
in that 0.5-mag G bin) instead: population median 1.07, 99th-percentile 3.53.
**The current top-15 candidates by dRV sit at chisq_relative_max ~1.3-7x** --
elevated but not screaming "obviously broken" by this metric alone. Net
conclusion: **DESI RVTAB columns alone cannot cleanly separate "genuine
large-amplitude binary" from "bad fit / blended fiber" for the highest-dRV
tail.** This is exactly the CLAUDE.md lesson from the TESS/Kepler project
("chi2_red-scale trend sigmas") recurring in a new dataset. `chi2_implausible`
(chi2_red>200) and `rv_implausible` (|mean RV|>600 km/s) are recorded as
audit/deprioritization flags in candidates.csv, not hard cuts -- Phase 2 must
resolve this with independent data (ZTF light curve + period, ideally resolved
imaging/spectroscopy), not more DESI-internal statistics.

## 6. Top ~30 ranked candidates (see candidates.csv for the full 26,427)

Ranked by FoM = drv_max_sigma x log10(1+drv_max), halved for SB2-suspects,
x0.1 for chi2/RV-implausible-flagged (Phase-1 proxy for "interesting for
Phase-2 ZTF follow-up" -- NOT a mass function; that needs an orbital period).

**Live SIMBAD backstop run on the top 30** (VSX leg dropped as unreliable, see
Section 3): **8/30 (27%) already have a SIMBAD designation.** Three are
unambiguous known ordinary variables that our front-filter store missed:
- rank 7, Gaia DR3 1154769341272239616 = **CRTS J150219.2+031156, SIMBAD type
  EB\*** (eclipsing binary) -- ordinary stellar binary, not dark.
- rank 10, Gaia DR3 1058868906306003072 = **ZTF J104819.80+655559.4, SIMBAD
  type BY\*** (BY Draconis spotted/active variable) -- ordinary star.
- rank 17, Gaia DR3 1480681355298504960 = **CRTS J142114.7+352838, SIMBAD type
  BY\*** -- ordinary star.
Three more are Em\*/Pe\* (emission-line / peculiar star -- ambiguous, plausibly
Be star or CV, not obviously dark-companion) and two are unclassified generic
SIMBAD entries (uninformative). **22/30 have no SIMBAD match at all** -- true
absence of information, not confirmation of novelty (see Section 3's VSX gap).

## 7. Honest assessment

Per the skepticism-first prior (0-2 plausible dark-companion candidates in the
whole sample): **nothing in this Phase-1 screen should be read as a discovery
claim.** Concretely:
- At least 3 of the top-17-by-FoM are demonstrably ordinary stellar binaries
  or active stars once checked against SIMBAD (a check this pipeline's
  front-filter store, due to its VSX gap, did NOT catch on its own).
- The remaining un-flagged top candidates have chi2/fit-quality diagnostics
  that are elevated but not decisively artifact-like -- Phase 1 statistics
  alone cannot resolve real-vs-artifact for them.
- 383 candidates are SB2-suspect (VSINI>30) and 3,926 are chi2/RV-implausible
  -- both deprioritized in ranking, both still present in candidates.csv for
  audit.
- 0 candidates were confirmed novel-AND-dark-companion-plausible with the
  tools available in this screen; that determination requires Phase 2.

**What Phase 2 (ZTF period search) should target:**
1. Take the top ~20-30 candidates.csv rows (by FoM, excluding the 3 SIMBAD-
   confirmed known binaries above) and search ZTF light curves for a coherent
   period. A real binary (dark or luminous) should show ellipsoidal variation,
   reflection, or eclipses at a period consistent with the DESI-epoch RV
   swing; an artifact (blended fiber, bad fit) should show no credible
   photometric period at all.
2. Re-run the live SIMBAD/known-object check on the FULL candidate list (or at
   least top ~100-200), not just the top 30, before any further vetting effort
   is spent -- this screen only budgeted the top 30.
3. **Fix the known_objects store's VSX gap** (flagged, not fixed, in this
   session) before the next hunt reuses it as a front-filter -- it demonstrably
   let 3 known binaries through undetected in just a top-30 sample.
4. For survivors with both a photometric period AND a defensible DESI RV
   amplitude, compute the actual mass function f(M) (needs the period) and
   only then assess plausibility of a WD/NS/BH-boundary companion vs. a
   luminous low-mass stellar one.
5. Independently verify the highest-chi2_red objects (chi2_red>200,
   n=3,926) are not simply catastrophic fit failures before spending Phase-2
   telescope-adjacent effort on them -- resolved imaging (checking for a close
   luminous neighbour, as Smith 2026 had to do) or an independent RV source
   (e.g. a second spectroscopic survey) would settle this faster than ZTF alone
   for that specific subset.

## 8. Scripts (all in /tmp/desi_hunt/scripts/)

- `list_pixels.py` -- enumerate all healpix leaf dirs per program (cached JSON).
- `fetch_and_extract.py` -- stream download+extract+delete per pixel, checkpointed CSV.
- `compute_rv_stats.py` -- per-targetid (single-program) RV stats; superseded by merge_and_filter.py for final numbers, kept for reference.
- `merge_and_filter.py` -- merge across programs by Gaia source_id (vectorized pre-filter to multi-epoch keys before the expensive per-group loop -- a naive full groupby over 3.7M mostly-singleton groups was the first-pass bottleneck), apply cuts, novelty filter, rank, write candidates.csv.
- `add_chisq_diagnostic.py` -- G-mag-relative CHISQ_TOT badness score (chisq_relative_max), merged into candidates.csv.
- `live_backstop_check.py` -- SIMBAD (reliable) + best-effort VSX (unreliable, off by default) live check for a shortlist.

## 9. Addendum: a more credible starting shortlist for Phase 2

Because the raw-FoM top-15 (Section 6) are ALL chi2-flagged (Section 5),
a second, arguably more useful cut for Phase-2 triage is the **top-of-FoM
subset that is NOT flagged on chi2/RV-implausibility or SB2** (22,202 of the
26,427 candidates pass this; the top 30 of those are staged separately at
`/tmp/desi_hunt/checkpoints/top30_plausible_shortlist.csv`). These have:
- `chisq_relative_max` ~0.7-1.6 (i.e. fit quality is population-typical for
  their brightness, NOT anomalous) -- much more reassuring than the raw-FoM
  top-15's 1.3-7x.
- dRV_max_sigma still 19-27 (highly significant, just not the most extreme).
- dRV amplitude 44-113 km/s over baselines of 29-385 days, with 3-8 epochs
  each (more epochs per target than the 2-point pairs dominating the raw-FoM
  top-15, so less sensitive to a single bad exposure).
- Sky coverage spans dec -15 to +75 (both hemispheres of the dec>-30 cut).

**Recommendation**: Phase 2 should prioritize THIS chi2-clean shortlist over
the raw-FoM top-15, precisely because the raw-FoM top-15's extreme dRV is
degenerate with "extreme fit failure" in a way this list cannot resolve
in isolation.
