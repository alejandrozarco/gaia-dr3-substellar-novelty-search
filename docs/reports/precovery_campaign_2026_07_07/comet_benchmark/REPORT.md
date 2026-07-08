# Comet benchmark — C/2014 UN271 (Bernardinelli–Bernstein), 2026-07-08

**Purpose:** positive-control benchmark of the precovery astrometry pipeline on a second object
class (comet) with professional same-frame ground truth + a gold-standard orbit. Pre-registered
pass criteria. The campaign's self-arc rule is DELIBERATELY INVERTED here (re-measuring frames
already in the arc is the point of a measurement-vs-measurement benchmark). NOTHING submitted —
these positions are already in the MPC record; duplicates would be harmful.

**Verdict: PASS on all three criteria.** Refereed (checks 1/4/5 by the referee agent — all
reproduce to the digit; checks 2/3/6 completed main-thread after the referee hit a session limit).

## Setup

- 10 DES/DECam epochs, 10 distinct nights, 2014-10-20 → 2018-11-08 (r_helio 29.0 → 23.7 AU),
  all with published W84 astrometry from the same exposures (Bernardinelli & Bernstein DES work).
- Blind re-measurement: NSC DR2 `meas` at the Horizons-predicted position (code-verified: search
  center = prediction, "never using the published RA/Dec"); 10/10 detected at sep 0.02–0.39″;
  2 epochs independently re-centroided on the raw `_ooi_` pixels (agree ≤0.07″/axis).
- Frame-midpoint vs MPC obstime: |Δt| < 1 s on all 10 (referee: fresh Horizons per-epoch calls
  reproduce stored predictions to 4–14 mas and stored PsAng exactly on 4 spot-checked epochs).
- Packed designation gotcha: C/2014 UN271 = `CK14UR1N` (not `CK14U27N`); get-obs via GET
  data.minorplanetcenter.net/api/get-obs with JSON body `{"desigs":["C/2014 UN271"]}`.

## Results (N=10, arcsec)

| comparison | dRA·cosδ mean / RMS | dDec mean / RMS |
|---|---|---|
| OURS − PUBLISHED (same frame) | −0.007 / **0.029** | −0.005 / **0.043** |
| OURS − JPL (O−C) | −0.024 / 0.080 | −0.107 / 0.203 |
| PUBLISHED − JPL (O−C) | −0.018 / 0.072 | −0.102 / 0.186 |

- **(i) Same-frame: PASS (strong).** Two independent pipelines (DESDM vs NSC/ours) on identical
  pixels agree to 0.03–0.04″ RMS — at the catalog noise floor.
- **(ii) O−C vs JPL: PASS.** The −0.107″ Dec systematic is mirrored in the published data →
  intrinsic to the object, not the reduction (see photocenter below).
- **(iii) Orbit-level: PASS (relative).** Swapping our 10 positions for the published ones:
  every element changes <0.1σ; 2030 geocentric prediction shifts 0.0003″ (the epochs' total
  leverage being 0.036″) — our points carry the professional points' information to <1%.
  Known limitation: the local fo build runs without a JPL DE planetary ephemeris → a shared
  ~3.6″@2030 absolute offset vs JPL common to full/minus/joint; cancels in all comparisons.

## Photocenter finding (the comet-specific physics)

Offset of measured photocenters w.r.t. the current JPL orbit, projected on the sunward direction
(sunward PA = Horizons PsAng+180°; convention independently re-derived, matches to 1 mas):
mildly ANTI-sunward (−0.10″) at 28–29 AU → **+0.28–0.35″ SUNWARD by 23–25 AU**; Pearson
r(sunward, r_helio) = −0.873 over all 32 epochs (robust to dropping the 2 largest offsets and to
per-night averaging); perpendicular component ~0 while the sunward axis rotates on-sky with the
observing geometry (PA 277°→72°) — a heliocentric-geometry effect, not WCS scatter. Identical in
our and the published measurements.

**Interpretation (literature-anchored, deliberately left two-way):** published comet-astrometry
work models photocenter bias as TAILWARD with aperture (C/2013 A1, arXiv:1507.01980), and the
Rubin 3I/ATLAS paper (arXiv:2507.13409) reports exactly our signature — accurate measurements
sitting consistently SUNWARD of a JPL orbit because the orbit absorbs tailward-biased astrometry
from elsewhere in the arc. Our sunward-growing offset is therefore either (a) a sunward
inner-coma fan (common in distant CO-driven comets) or (b) the JPL solution being dragged by
later, more-active-era astrometry. Both are activity physics; neither indicts the pipeline.
**Operational rule derived: comet astrometry from this pipeline requires either a quiescence
requirement or an activity-dependent photocenter caveat before any submission.**

## Bottom line

The pipeline is validated end-to-end on a second object class against professional ground truth:
astrometric accuracy at the catalog noise floor, orbit-level information content equal to the
professional measurements, and the known comet systematic (photocenter offset) detected,
quantified, and correctly attributed rather than absorbed.

Tooling gotchas banked: SSOIS CGI endpoints 404 (relocated) — use `nsc_dr2.exposure` MJD+exptime
directly; Datalab `/tap` timing out — use REST `/query/query`; `c4d_HHMMSS` exposure-name
timestamps off by up to ~140 s — never use as a time source; `/svc/cutout` ignores SIZE for these
frames (321 MB MEF — select CCD in memory).

Artifacts: benchmark_table.csv (10 rows, full three-way per epoch), raw/ (SBDB, MPC ADES+OBS80,
Horizons ephem+sunward, per-epoch meas, pixel_centroids.json), orbit/ (full/minus/joint .obs +
fo outputs; >1 MB fit dumps pruned, regenerable), scripts (nsc.py, process_epochs.py, analyze.py,
orbit_prep.py, pixel_centroid.py). Provenance: tasks a903f3e50163b489c (benchmark) +
acc03fc3b2a1cf10f (referee, checks 1/4/5) + main-thread checks 2/3/6 (2026-07-08).

## Referee addendum (independent completion, 2026-07-08 late) — SUPERSEDES parts of the above

The resumed referee re-derived ALL checks independently (instructed not to trust the main-thread
provisional numbers). **verdict_stands = TRUE; all three criteria PASS with 6–20× margins on its
own recomputation.** Everything deterministic reproduced exactly (headline table to the digit;
frame midpoints max |dt|=0.91 s from its OWN OBS80 parse + exposure query; stored Horizons rows
to ≤0.2 mas; OBS80 sexagesimal decode reproduces ra_pub/dec_pub to ≤1.6 mas; N=10 = 10 distinct
nights over 5 seasons; parent 32 exposures/21 nights matches MPEC 2021-M83 exactly; r=−0.8726
robust to outlier-drop [−0.8427] and per-night collapse [−0.8738]; orbit swap ≤0.0062σ / 0.263 mas
@2030; blindness procedurally verified at code level).

**Interpretive corrections (binding; none change pass/fail):**
1. **"≈0 at 28–29 AU" REFUTED:** the 8 early epochs are significantly ANTI-sunward, mean
   −0.163″±0.022 (SE); the trend is −0.16″ → +0.24″ with zero-crossing ≈27.7 AU. A real coma
   cannot displace the photocenter anti-sunward at 29 AU with no detectable coma → the early-epoch
   offset must be (at least partly) a JPL-solution reference-trajectory artifact.
2. **Single-mechanism claim overclaimed; frames are degenerate:** projecting the offsets onto the
   (nearly constant) anti-velocity axis correlates with r_helio equally well (r=−0.889 vs −0.873
   sunward) — the PA-"rotation-tracking" discriminant has little power (the extreme-PA epochs
   carry the smallest offsets). Adjudication: an ambiguous MIX of (a) real sunward photocenter
   displacement in the active 2016–18 epochs — literature-backed FOR THIS COMET (Farnham et al.
   2021 reported a sunward coma enhancement in UN271, slow large grains from the sunlit
   hemisphere) — and (b) JPL-orbit-arc absorption of activity-biased astrometry (mechanism
   documented in the Rubin 3I/ATLAS paper §4.4/4.6). Neither indicts the pipeline (ours≡published
   at 0.03–0.04″ throughout).
3. **Sign-paraphrase correction (of the main thread):** in the 3I/ATLAS paper the coma extension
   is SUNWARD and the Rubin residuals sit roughly ANTI-sunward of the dragged orbit — the earlier
   "sunward of a tailward-dragged orbit" paraphrase in this report had it backwards; the paper is
   the authority, and the mechanism (orbit dragged by coma-biased astrometry elsewhere in the
   arc) is what transfers, not the sign.
4. **e-"discrepancy" dissolved (STRENGTHENS the result):** fo's e=1.00417 vs SBDB 0.9991 is an
   osculating-EPOCH artifact — Horizons' own heliocentric osculating e at the fo epoch
   (2026-07-04) is 1.0041528; fo matches JPL same-epoch to 1.9×10⁻⁵. The no-DE limitation shows
   only in the shared 3.6″ 2030 offset.
5. **Blindness caveat:** procedurally blind confirmed (search centers = predictions; published
   positions touched only after selection; one candidate per frame → no selection freedom), but
   the 10-of-32 epoch subset was hard-coded without documented criteria — read "10/10" as "10/10
   of an undocumented subset." The referee's survivorship probe of a NON-selected epoch (idx 1)
   found a clean detection 0.255″ from prediction at matching mag → no evidence of forcing.

**Operational rule (refined):** comet astrometry from this pipeline is submission-grade only with
an explicit photocenter caveat; absence-of-precovery claims near a comet's ACTIVE phase must
budget a ~0.2–0.4″ systematic, not the 0.05″ TNO floor. Bottom line unchanged: (a) TNO/slow-mover
astrometry VALIDATED at the catalog noise floor with orbit-level interchangeability; (b) comet
astrometry validated AS MEASUREMENT, bounded AS INTERPRETATION.
