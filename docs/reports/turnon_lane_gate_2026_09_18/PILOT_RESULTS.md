# Turn-on lane — pilot results and close-out (2026-09-18)

**Verdict: 13 candidates surfaced, 0 survive. All 13 are instrumental artifacts,
in three distinct and now-characterised channels.** The lane as specified does not
work, and the reason is structural rather than bad luck — see "Why the selection
is artifact-dominated".

Companion docs: `GATE_AND_PILOT_SCOPE.md` (gate zero, build notes).
Scripts: scratchpad `turnon_pilot.py`, `turnon_vet.py` (v1, defective),
`turnon_vet2.py` (v2, used for these verdicts), `measure_dropout.py`.

## 1. What the pilot produced

4,403 NSC DR2 positions (r 22–24, class_star>0.5, g−r<0.6, pre-MJD-58119, 7 tiles,
10.1 deg²) assessed against ZTF:

| status | n |
|---|---|
| NO_ZTF | 4,161 |
| ZTF_SPARSE | 120 |
| NO_TURNON | 109 |
| **CANDIDATE** | **13** |

## 2. The v1 vetting was worthless — and failed toward "reject"

`turnon_vet.py` returned **identical values on all four checks for all 13 objects**:
`isolated: true`, `bright_neighbour_3as: 0`, `SIMBAD: 1`, `gaia: null`,
`morph: "NO_DATA"`. Four independent tests agreeing perfectly across 13 unrelated
objects is a silent-failure signature, not a result.

Cause: every check called `curl()`, which returns `''` on any transport failure, and
each check treated `''` as a *finding* rather than an error:

- `hits["SIMBAD"] = 0 if (...) else 1` — an empty response fell to `else 1`, i.e.
  **a failed query was scored as "this object is already catalogued."** This alone
  set `uncatalogued: false` on all 13 and produced zero survivors.
- the NSC isolation query returned nothing → `bright_neighbour_3as: 0` → "isolated".
- the Gaia query returned nothing → `gaia: null` ("no counterpart").
- `morphology()` got nothing → `NO_DATA`.

All four queries succeed when re-run by hand; they were being rate-limited during the
run because the pilot had just issued 4,403 IRSA queries on 12 threads.

**Rule (new): a check that cannot distinguish "no result" from "no answer" is not a
check. Every query must retry and return an explicit error sentinel; no default value
may double as a finding.** `turnon_vet2.py` implements this — it recorded 0 errors on
the re-run, because it retries rather than because failures stopped happening.

## 3. The decisive test: ZTF tells you which star it measured

Better than counting neighbours: **the ZTF light curve carries a per-epoch centroid.**
Comparing the median bright-state centroid to the target position identifies blends
directly, with no assumptions about the neighbourhood.

| RA | Dec | amp | ZTF offset | duty | verdict | ZTF centroid sits on | that source's r |
|---|---|---|---|---|---|---|---|
| 117.75853 | +10.28674 | 6.87 | 0.97″ | 0.20 | ON_TARGET | 80807_1921 (target) | 22.94 |
| 118.73208 | +10.46179 | 4.20 | 2.41″ | 1.00 | BLEND | 80297_2382 | 22.29 |
| 118.47328 | +9.93255 | 3.94 | 2.61″ | 1.00 | BLEND | 80808_2042 | 19.20 |
| 118.73847 | +10.58810 | 3.70 | 1.53″ | 0.20 | AMBIGUOUS | 80297_8940 (target) | 23.12 |
| 118.12253 | +10.20091 | 3.62 | 2.89″ | 1.00 | BLEND | 80807_5662 | 19.53 |
| 118.50915 | +10.38057 | 3.35 | 1.45″ | 0.80 | AMBIGUOUS | 80808_8766 (target) | 22.85 |
| 118.26818 | +10.03518 | 3.04 | 2.24″ | 1.00 | BLEND | 81320_2511 | 20.29 |
| 118.52231 | +10.81402 | 2.98 | 3.24″ | 0.66 | BLEND | 79784_3158 | 21.94 |
| 118.11811 | +10.44334 | 2.92 | 1.24″ | 0.33 | AMBIGUOUS | 80296_6037 (target) | 22.82 |
| 118.65423 | +10.00158 | 2.80 | 3.18″ | 0.94 | BLEND | 81321_2491 | 21.22 |
| 118.33822 | +10.03366 | 2.76 | 2.42″ | 1.00 | BLEND | 80808_1821 | 19.86 |
| 118.19684 | +10.39440 | 2.61 | 2.49″ | 0.99 | BLEND | 80296_3713 | 19.65 |
| 118.50030 | +10.24046 | 2.56 | 2.68″ | 1.00 | BLEND | 80808_8491 | 20.82 |

**9/13 BLEND, 3/13 AMBIGUOUS, 1/13 ON_TARGET.**

Worked example (118.12253 +10.20091): NSC resolves two sources 2.87″ apart — our
target at r=22.88 and a neighbour at r=19.53. The ZTF centroid sits 0.65″ from the
neighbour and 3.0″ from the target; Gaia DR3 finds G=19.47, ϖ=1.41 mas on the
neighbour. ZTF measured the bright star for 7.5 years. Note the perfect diagnostic
correlation: **every duty_cycle ≈ 1.0 object is a blend** — a "turn-on" that is
simply constant in ZTF is a constant star seen through a coarser PSF.

## 4. The one on-target candidate: refuted by ATLAS (rule 10)

RA 117.75853 Dec +10.28674, claimed r=22.94 → zr=16.07, amp 6.87. **Dead.**

Its ZTF metadata condemns it without any external data — it is the only epoch of six
with non-zero `catflags`, and its PSF diagnostics are off-scale against its own siblings:

| MJD | mag | catflags | chi | sharp | limitmag |
|---|---|---|---|---|---|
| **58432.5074** | **16.067** | **1** | **5.20** | **+0.378** | 20.88 |
| 58802.4950 | 20.286 | 0 | 0.99 | −0.410 | 20.33 |
| 58802.4963 | 20.759 | 0 | 0.39 | +0.036 | 20.54 |
| 59484.4927 | 20.617 | 0 | 0.69 | −0.142 | 20.64 |
| 59518.5049 | 21.523 | 0 | 0.62 | −0.236 | 21.55 |
| 60671.3787 | 20.915 | 0 | 0.28 | −0.040 | 20.91 |

ATLAS forced photometry (task 5006731, 4,037 epochs MJD 58021–61000, 4,023 passing
chi/N<4) settles it independently: ATLAS observed **the same night, 3.5 h after the
ZTF exposure** (MJD 58432.6539) and measured **36 ± 24 µJy = 1.5σ**. A mag-16.07
source is 1,359 µJy — a **57σ** detection in that single exposure. Across the full
8-year ATLAS baseline there is exactly one ≥5σ single epoch (MJD 58152, 10.3σ,
mag 17.87) and its own 8-exposure nightly stack dilutes to mag 20.07 at 4.1σ, i.e.
1 exposure of 8 spiked and 7 saw nothing — a second, independent rule-10 artifact.

Cosmic ray / hot pixel. The commit message on 05f4659 ("uncatalogued 6.9-mag outburst
source") is superseded by this finding.

## 5. The three "ambiguous" objects: sub-threshold noise

For #4 (118.73847) and #9 (118.11811), **every detection is fainter than that frame's
own 5σ limiting magnitude** — by definition sub-threshold noise excursions, not
measurements. The apparent amplitude is manufactured by night-to-night depth
variation: #4's "bright" 19.42 epoch sits on a frame with `limitmag 18.93` (the
shallowest of its six), while its faint epochs come from frames reaching 22.2. The
source did not change; the noise floor did.

#6 (118.50915) has genuine above-limit detections but only 5 marginal zg epochs, with
the centroid wandering to 2.99″ and `sharp` reaching +0.53. Not a detection of anything.

## 6. Why the selection is artifact-dominated (the structural result)

The lane compares **a deep, high-resolution survey (NSC, ~0.9″, r→24) against a
shallow, low-resolution one (ZTF, ~2″, r→20.5)** and selects objects that are faint in
the first and bright in the second. That selection is *definitionally* satisfied by:

1. **blending** — any faint NSC source within ~3″ of a brighter star (ZTF cannot
   separate them);
2. **sub-threshold noise** — a faint target plus a shallow frame yields a spurious
   "bright" detection, with amplitude set by frame depth;
3. **single-epoch artifacts** — cosmic rays land preferentially on the faint targets
   because that is where a fixed flux implies a huge amplitude.

All three scale with the depth gap, so they dominate precisely where the intended
signal is largest. A real sustained turn-on is not distinguishable from channel 1 by
photometry alone — **only astrometry separates them.**

## 7. The pilot searched ~25% of what it claimed (the biggest defect)

`ztf_at()` runs `curl -s` with no retry and returns `''` on transport failure without
raising, so the `except Exception` guard never fires and the position is filed as
`NO_ZTF`. The tell: **zero `ZTF_ERROR` statuses across 4,403 threaded queries** to a
public archive — not a credible transport record.

Measured by re-querying 60 random `NO_ZTF` positions with retries:
**20/60 (33.3%) actually have ZTF data. 0 hard errors** — i.e. with retries the
archive answers every time.

Binning the assessment file by completion order exposes the mechanism — a cliff, not
a decline:

| queries completed | has ZTF | dominant tile |
|---|---|---|
| 0–400 | 15.2% | 118.3_10.4 |
| 400–800 | 22.8% | 118.3_10.4 |
| 800–1200 | 22.5% | 119.3_6.1 |
| 1200–1600 | **0.0%** | 119.3_6.1 |
| 1600–2000 | **0.0%** | 119.3_6.1 |
| 2000–2400 | **0.0%** | 119.3_6.1 |
| 2400–2800 | **0.0%** | 120.0_8.0 |
| 2800–4403 | **0.0%** | 118.5_0.0 |

IRSA cut the 12-thread client off after ~1,100 requests; every query after that
returned empty and was recorded as `NO_ZTF`. **Effective coverage was ~1,100 of 4,403
positions (~2.5 deg², not the claimed 10.1 deg²).**

This also fully explains the candidate clustering. All 13 candidates fell in tile
118.3_10.4 — which looked like a tile-specific systematic worth investigating, and
is nothing of the kind: that tile was simply processed first, before the cutoff. The
apparent sky structure was an artifact of processing order.

No verdict in §3–§5 changes (a dropped query can only hide a candidate, never invent
one), but the lane's null was a null over a quarter of the intended footprint.

## 8. If the lane is re-run, the selection must include

1. ZTF centroid within ~1″ of the NSC target (the blend killer — would have removed
   9/13 before any human looked);
2. no NSC source brighter than the target within 4″;
3. detections above the frame `limitmag` by ≥0.3 mag (kills the noise channel);
4. `catflags == 0`, `|sharp| < 0.3`, `chi < 2` (kills the cosmic-ray channel);
5. ≥2 independent nights reproducing the bright state (rule 10);
6. duty cycle < 0.9 (a constant ZTF source is a blend, not a turn-on);
7. independent-survey confirmation (ATLAS forced photometry) before any claim;
8. retries with explicit error status on every query — no silent `NO_ZTF`.

Filters 1, 3, 4 and 6 together reject all 13 of the present candidates
automatically, which is the correct outcome and the cheapest possible referee.

**Re-run launched 2026-09-18 16:39 UTC** (`turnon_pilot2.py`): all eight filters
applied in-pipeline, 4 threads throttled to ~2.2 req/s with adaptive backoff and an
explicit `ZTF_ERROR` status, covering all 4,403 positions including the ~3,300 the
first pass never actually queried. Output: `ztf_assess2.jsonl`,
`turnon_candidates2.json`.

## 9. Self-recovery test (standing rule) — filters validated, selection NOT

Standing rule: a template-driven search must recover its own template before any
absence claim. Targets = the 3 catalogued dwarf novae inside the pilot's own tiles
(VSX), pushed through the **identical** v2 epoch filters and classifier.

| object | NSC r | ZTF offset | amp | duty | bright nights | verdict |
|---|---|---|---|---|---|---|
| CSS 140121:075258−000709 | 20.79 | 0.06″ | 3.00 | 0.58 | 11 | **RECOVERED** |
| ASASSN-15tr | 20.10 | 0.03″ | 3.45 | 0.17 | 5 | **RECOVERED** |
| SDSS J075117.00+100016.2 | 18.44 | 0.09″ | 0.45 | 1.00 | 302 | REJECTED: CONSTANT |

**2/3 recovered; the third rejection is correct** — in the ZTF era that object sits at
r≈18.0 with duty 1.00 and amp 0.45, i.e. it is genuinely not a turn-on on this baseline.

The specific worry that the `mag ≤ limitmag − 0.3` cut would reject genuine
modest-amplitude events is **not** borne out: CSS 140121 lost 58% of its epochs to the
quality filters and still passed comfortably, because a real outburst yields many good
epochs. Aggressive per-epoch filtering is affordable when the signal is real.

**Honest limitation — the selection is NOT validated end-to-end.** All three templates
have NSC r = 18.4–20.8, *outside* the pilot's 22–24 selection window. There is no known
object of the target class at the target faintness anywhere in this footprint to
recover. So this test validates the **filters**, not the **selection**; the lane hunts a
regime where no confirmed template exists, and that must be stated with any null.

### Faint-end sensitivity (measured, 963 real zr frames in-field)

Frame depth: median limitmag 20.50 (10th pct 19.89, 90th pct 21.30). Fraction of
frames on which a turn-on of a given brightness clears `mag ≤ limitmag − 0.3`:

| turn-on reaches | frames usable | amp from r=23 |
|---|---|---|
| r = 18.0 | 100.0% | 5.0 mag |
| r = 19.0 | 98.2% | 4.0 mag |
| r = 19.5 | 91.4% | 3.5 mag |
| r = 20.0 | 70.7% | 3.0 mag |
| r = 20.3 | 44.7% | 2.7 mag |
| r = 20.5 | 34.3% | 2.5 mag |
| r = 21.0 | 9.6% | 2.0 mag |

**CORRECTED 2026-09-18 (see §10).** The table above is *per-frame* efficiency, which is
NOT completeness. An earlier version of this section concluded "near-full sensitivity only
for turn-ons reaching r ≲ 19.5" — that was wrong: with hundreds of epochs, even a 34%
per-frame rate yields abundant detections. End-to-end injection gives **100% recovery of
sustained turn-ons down to r = 20.5**. Quote §10, not this table, for completeness.

### The bug class bit the referee too

The first pass of this recovery test reported 2/3 REJECTED: BLEND with offsets
~1.3″ and 2.8″. Both were artifacts of the test, not the pipeline:
(a) **VSX catalogue positions are 1.25–1.35″ off** the true source here (NSC and Gaia
agree with each other to 0.03″), so anchoring on VSX manufactured a fake offset; and
(b) a hardcoded anchor for ASASSN-15tr was wrong, and the re-resolution query — a 2″
box centred on that wrong position — **returned empty and the code kept the bad
value**. Anchored correctly on the NSC source at the ZTF centroid, the offsets are
0.03″ and 0.06″.

That is the same silent-empty-result failure this whole report is about, occurring
inside the tool written to referee it. It is not a rare bug; it is the default
behaviour of any query whose empty return is a plausible value.

## 9. Lessons banked

- **A default value must never double as a finding.** v1's `else 1` converted network
  failure into "already catalogued" and silently rejected the entire candidate list.
- **Identical output across independent checks on unrelated objects is a bug signature.**
  Suspect the harness before believing the astronomy.
- **Per-epoch astrometry is a first-class vetting tool.** ZTF publishes a centroid on
  every detection; it identifies blends directly and needs no external catalogue.
- **`limitmag` is the honest reference for a detection, not the magnitude.** Comparing
  mag to the frame's own limit exposes depth-driven pseudo-variability that any
  amplitude cut will otherwise pass.
- **The referee needs the same rigour as the pipeline.** The self-recovery test
  initially "failed" 2/3 purely through its own coordinate bugs — including one empty
  query whose result was silently kept. Validate the validator.
- **Catalogue positions are not truth.** VSX positions here are 1.25–1.35″ off sources
  where NSC and Gaia agree to 0.03″; anchor astrometric tests on survey catalogues,
  never on variable-star catalogue coordinates.
- **A cross-survey depth gap is a systematic generator**, not just a discovery lever;
  a search built on one must budget for all three artifact channels up front.
- **Apparent sky structure in a result can be processing-order structure.** The 13
  candidates clustering in one tile looked astrophysical and was purely an artifact of
  which positions were queried before the archive cut us off. Before interpreting any
  spatial pattern, check it against completion order.
- **Rate limits present as data, not as errors.** A throttled archive returns empty
  200s, so an unthrottled scraper does not crash — it quietly manufactures a null.
  Any bulk archive job needs a request-rate budget and a positive-control check that
  the last query still returns data (bin the outcome by completion order).


---

## 10. END-TO-END LANE TEST — injected turn-ons in real ZTF cadences

External review (gpt-6-astra, 2026-09-18) made the fair objection that recovering two
bright dwarf novae validates the filters on two examples and says nothing about
completeness across amplitude or turn-on date. Measured properly here: synthetic sources
injected into **real ZTF observing dates with real per-frame limiting magnitudes**, passed
through the **identical classifier** from `turnon_pilot2.py` (script:
`lane_injection_test.py`; 3 real cadences, 442–1,146 zr epochs each, median limitmag
20.45–20.80; 60 trials per cell).

### Sustained turn-on, archival NSC r = 23.0

| reaches | amp | pre-ZTF | 2019 | 2021 | 2023 |
|---|---|---|---|---|---|
| r = 18.5 | 4.5 | 100% | 100% | 100% | 100% |
| r = 19.5 | 3.5 | 100% | 100% | 100% | 100% |
| r = 20.0 | 3.0 | 100% | 100% | 100% | 100% |
| r = 20.5 | 2.5 | 100% | 100% | 100% | 100% |
| r = 21.0 | 2.0 | 0% | 0% | 0% | 2% |

**Recovery is complete down to r = 20.5 and independent of when the turn-on happened.**
The cliff at r = 21.0 is the `amp > 2.5` CUT, not a sensitivity limit — at NSC r = 23.0 a
source reaching r = 21.0 has amp = 2.0 and is rejected by construction.

**This overturns §9's earlier conclusion.** Per-frame efficiency (34% of frames at r = 20.5)
is not completeness: hundreds of epochs over 8 years convert a modest per-frame rate into
certain detection. The lane is considerably more sensitive than the frame-level table
implied, and the null is correspondingly stronger for sustained events.

### Outburst (dwarf-nova-like), 30-day events

| reaches | 1 outburst | 2 | 4 | 8 |
|---|---|---|---|---|
| r = 18.0 | 58% | 72% | 97% | 100% |
| r = 19.0 | 57% | 75% | 100% | 100% |
| r = 19.5 | 55% | 80% | 93% | 100% |
| r = 20.0 | 50% | 77% | 93% | 100% |

**This is where the lane actually leaks.** A single 30-day outburst is recovered only
~50–58% of the time, driven by the ≥2-bright-nights requirement against seasonal gaps.
Rare-outburst systems (WZ Sge-like) are the class most likely to be missed, and any
statement about their absence must carry ~55% completeness for single events.

### Scope limits of this test (stated, not glossed)

- **Catalogue-level, not image-level.** It tests the cadence, the depth model and the
  classifier. It does NOT test source extraction, deblending or association, so it cannot
  measure losses from crowding or from absence in ZTF's reference catalogue.
- ZTF light curves are seeded from reference-catalogue sources, so a target missing from
  or misassociated with that reference escapes the lookup entirely and is invisible to
  both the pilot and this test.
- Noise is modelled as growing toward the frame limit; real photometry has correlated
  systematics this does not reproduce.

---

## 11. LANE CLOSE-OUT — full footprint, corrected pipeline (2026-09-19)

The rebuilt pilot (`turnon_pilot2.py`, randomised order, retries, explicit error status,
eight artifact filters in-pipeline, duty veto removed) completed **all 4,403 positions**
over 10.1 deg².

| status | n | % |
|---|---|---|
| NO_ZTF | 3,182 | 72.3% |
| ZTF_SPARSE | 1,154 | 26.2% |
| BLEND | 59 | 1.3% |
| NO_TURNON | 6 | 0.1% |
| SINGLE_NIGHT | 1 | — |
| ZTF_ERROR | 1 | 0.02% |
| **CANDIDATE** | **0** | — |

**One hard query failure in 4,403**, recorded as `ZTF_ERROR` rather than silently filed as
`NO_ZTF`. Contrast v1, whose *zero* errors across a 12-thread run were the tell that it was
manufacturing nulls; here the single error is a genuine, reported failure after 4 retries.

### The null, quantified

`NO_ZTF` is an informative non-detection, not an unsearched position: a source that turned
on to r ≤ 20.5 **would** appear in ZTF, and injection shows it would be recovered with 100%
efficiency. So the searched sample is 4,402 (excluding the one error).

- **0 sustained turn-ons** among 4,402 faint (r 22–24) archival sources.
- 95% upper limit on recoverable discovery probability: **3/4,402 ≈ 6.8 × 10⁻⁴ per target**.
- Surface-density limit for this selection: **< 0.30 deg⁻² (95%)** over 10.1 deg².
- Valid at **100% completeness for sustained events reaching r ≤ 20.5**, and only
  **~55% for single 30-day outbursts** (see §10) — rare-outburst systems are NOT
  constrained at the same level.

### Caveats that bound the null

- **Reference-catalogue seeding.** ZTF DR light curves are built around reference-catalogue
  seed sources. A target absent from, or misassociated with, that reference escapes the
  lookup entirely — invisible to both the pilot and the injection test. This is the largest
  unquantified hole in the null.
- The injection test is **catalogue-level**: it validates cadence, depth model and
  classifier, not source extraction, deblending or association.
- 26% of positions returned ZTF data too sparse to classify after quality cuts; those are
  weaker non-detections than the `NO_ZTF` majority.

### What the lane produced

**One object, and only via a bug fix.** J075308.47+003535.6 sits at amp 2.44 against the
2.5 threshold — it was rejected outright until external review showed the `duty > 0.9` veto
was discarding the lane's primary target class. It is a real ~1.9 mag sustained brightening,
**unconfirmed as to nature** (see `docs/object_journals/nsc_97192_2072.md`, REVISION 2).

That is the honest yield: **0 formal candidates, 1 sub-threshold object of uncertain class,
from 4,403 positions over 10.1 deg².**

### Verdict

The selection works as specified and is now completeness-characterised, but its yield at
this depth and footprint is consistent with zero. External review independently recommended
abandoning `NSC r=22–24 → bright ZTF counterpart` as a primary discovery programme and
moving to selections with a *temporal* reason to query (NSC `meas` time series rather than
object averages), a brighter window (r ≈ 18.5–21.5), and bulk access via IRSA's HATS/S3
endpoint rather than per-position API calls. **Lane status: CLOSED as a primary programme**;
the tooling and the artifact catalogue carry forward.


---

## 12. SELECTION CORRECTED (2026-09-19) — the null covered 45% of its own target population

The selection used `nsc_dr2.object` with `mjd + deltamjd/2 < 58119` to require a pre-ZTF
archival epoch. **Both columns are aggregates over ALL bands**, so the cut used a multi-band
epoch aggregate to test a single-band temporal condition: an object whose r-band history is
entirely pre-2018 was excluded if it happened to have, say, a z-band measurement in 2019.

**v2 states the condition directly on dated r-band `meas` rows** (script:
`turnon_select_v2.py`):

```sql
JOIN nsc_dr2.meas m ON m.objectid = o.id
WHERE m.filter = 'r' AND m.mjd < 58119
GROUP BY o.id HAVING COUNT(m.mjd) >= 2 AND AVG(m.mag_auto) BETWEEN 22 AND 24
```

### What the flaw actually did — incompleteness, not contamination

Decomposed on a 0.2×0.2° test box:

| cut | surviving |
|---|---|
| base (rmag 22–24, class_star > 0.5, g−r < 0.6) | 122 |
| + `ndetr >= 2` | 97 |
| + `ndetg >= 1` | 97 (no further loss) |
| **+ `mjd + deltamjd/2 < 58119`** | **41** |
| dated `meas` selection | **96** |

**Zero objects selected by v1 fail the dated test** — the cut produced no false positives.
It discarded **58%** of otherwise-valid objects on that box.

### Full-footprint impact

| tile | v2 (dated) | v1 (object) | ratio |
|---|---|---|---|
| 118.3_10.4 | 2,835 | 959 | 2.96 |
| 119.3_6.1 | 2,603 | 1,287 | 2.02 |
| 120.0_8.0 | 1,906 | 434 | 4.39 |
| 118.5_0.0 | 1,857 | 1,672 | 1.11 |
| **116.0_12.0** | **520** | **26** | **20.00** |
| 84.0_0.1 | 10 | 9 | 1.11 |
| 83.0_-3.9 | 14 | 16 | 0.88 |
| **TOTAL** | **9,745** | **4,403** | **2.21** |

### CORRECTED NULL

The lane assessed 4,403 positions of the **9,745** meeting its own stated criteria — a
completeness of **45%** with respect to its target population. The per-searched-target limit
is unchanged (0 detections in 4,402 → 95% UL 6.8 × 10⁻⁴), but the population statement is not:

- **Surface-density limit corrected from < 0.30 deg⁻² to < 0.66 deg⁻² (95%)**, i.e. a factor
  2.2 weaker, scaling 3 detections to the full population (3 × 9745/4403 ÷ 10.1 deg²).
- The null remains valid and the artifact analysis is unaffected — the missing 55% were never
  looked at, so they can only have hidden candidates, not created them.

**LESSON: never use a multi-band aggregate column to test a single-band condition.** The
object-table `mjd`/`deltamjd` pair describes the whole record; a statement about r-band
history has to be made on r-band rows. This is the same class of error as the earlier
epoch-shuffle and "average vs dated" problems — a summary column silently standing in for
the measurement it summarises.
