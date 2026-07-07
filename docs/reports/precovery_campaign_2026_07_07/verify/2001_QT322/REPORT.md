# Bug-fixed deep re-run — 2001 QT322 (NSC DR2 / DECam precovery)

Date: 2026-07-07 | Work dir: /tmp/precovery_verify/2001_QT322/
Analyst: automated recovery agent (USER review only; NOTHING submitted to MPC or any service)

## OUTCOME: NULL_SEARCHED (clean, well-tested null — CONFIRMED after bug fix)
The prior NSC/DECam null for 2001 QT322 stands, but for the first time it is based on correctly
centered search boxes. The epoch-shuffle bug that voided the previous run is fixed; the corrected
boxes — now genuinely centered on the object's predicted track — still contain no coherent moving
source. Every in-3sigma detection is an independently catalogued stationary star; the negative
control is no cleaner than the real field.

## THE BUG (confirmed and quantified)
nsc_search.py built per-night predictions with astroquery Horizons called on a LIST of JDs
(epochs=jds) then read them back by POSITION: for i,mjd in enumerate(target_nights): row=eph[i].
astroquery returns ephemeris rows sorted by time, but target_nights was ordered by SMAA (tightness),
not by time -> row i did not correspond to night i. Measured mis-centering of the 12 buggy DECam
boxes vs the correct per-JD ephemeris (box_center_offset_vs_buggy_as in search_log.csv):

    MJD      offset       MJD      offset
    56951    1718.8"      57295    3362.3"
    56959     212.4"      57324    5466.8"
    57192     528.8"      57384    7834.7"
    57193    3138.7"      57611       0.1"  (accidentally correct)
    57199    5683.0"      58016      76.0"
    57210    8351.4"      58017      76.1"

11/12 boxes mis-centered by 76" to 8351" (2.3 deg) — only one buggy DECam box actually covered the
object. The buggy run ALSO mis-selected nights: it queried 58016/58017 (not in the true tightest-12)
and missed the two tightest nights entirely (56962, 56976, SMAA 7.2").

Fix (STANDING RULE): ephemeris recomputed one epoch per night, with a per-night assertion
abs(datetime_jd - requested_jd) < 1e-3 — positional indexing is structurally impossible. Recomputed
centers agree with the preserved per-footprint predictions (eph_by_jd.json, keyed by JD) to <0.02".

## CORRECTED SEARCH (12 tightest deep DECam nights, 2014-2018)
NSC DR2 meas table via NOIRLab Astro Data Lab TAP (anonymous). Box = 3*SMAA + intra-night motion
pad; each detection tested against the prediction interpolated to its own MJD (follows the
2.2-3.4"/hr motion within the night). Full per-night log: search_log.csv.

Nights SMAA 7.17-12.08". Raw in-3sigma detections: 21 total across 5 nights (56959:6, 57192:3,
57199:5, 57295:6, 57384:1). The two tightest nights the buggy run had missed (56962, 56976) were
searched here: 0 in-3sigma.

## CHAIN DISCIPLINE — every candidate rejected
- Stationary-source rejection (decisive). Each in-3sigma detection's objectid was resolved in
  nsc_dr2.object. EVERY one is a multi-detection mean object: ndet 5-22, baseline deltamjd
  984-1417 days, proper motions of only tens of mas/yr — i.e. stationary stars. Example
  (MJD57295): objectid 87313_1208 = 22 detections over 1204.7 d, position span 0.17"/0.12";
  objectid 87313_1211 = 21 detections over 1204.7 d, span 0.50"/0.33". A real TNO would appear in
  ONE opposition, not as a 3.3-year fixed source.
- Motion consistency. Only one night (MJD57295) produced an apparent motion-consistent pair
  (resid 0.09"). It is spurious: the "pair" is two exposures of the SAME stationary star
  (objectid 87313_1208) taken ~10 min apart, over which the predicted TNO displacement (~0.1-0.6")
  is small enough to be mimicked by measurement scatter of a fixed source. No cross-object track
  exists. Within-night, each stationary objectid appears in a single exposure (except that one
  star) -> no genuine intra-night motion baseline.
- Magnitude sanity. Predicted V~21.8-22.0. In-3sigma detections run mag 18.2-22.1, mostly
  0.1-3.8 mag BRIGHTER than predicted (dmag_vs_pred: -0.1 to -3.8) — consistent with field stars,
  not a V~22 TNO.

## NEGATIVE CONTROL (+1 deg Dec offset, identical pipeline)
Real total in-3sigma = 21; control total = 18 (control nights 57193:3, 57199:4, 57384:11). The
control even produced its own spurious "motion-consistent" pair (MJD57384, resid 0.04") — same
stationary-star short-baseline artifact. The real field is NOT cleaner than the offset control;
both are dominated by catalogued stationary stars. A genuine detection would be one source moving at
the predicted rate AND an excess over control. Neither exists. => NULL confirmed.

## PS1 COMPLETENESS RE-CHECK (nearest the depth limit)
The PS1 DR2 channel used a separately-keyed per-night prediction file (ps1_pred_by_night.json,
correctly keyed by MJD) and was not affected by the shuffle bug. Independent MAST PS1 DR2
detection-table cone queries on the three tightest PS1 nights reconfirm the null:
- MJD55088 (SMAA 1.23", the single tightest constraint): 0 in-night detections in a 14.4" cone.
- MJD55089 (SMAA 1.24"): 0 in-night detections.
- MJD55103 (SMAA 1.35"): 2 detections, both at sep 12.6" (OUTSIDE the 4" 3-sigma), stationary
  (two exposures of one source), AB~19.5 (~2.3 mag too bright).
Where the uncertainty ellipse is a near-pinpoint (~1.2"), the PS1 source catalog holds nothing at the
predicted position — consistent with V~21.8 sitting at/below PS1 3pi single-epoch inclusion (~21.5-22).

## HONEST INTERPRETATION
The bug fix did NOT change the conclusion, but it converts a void search into a valid one:
the object's tight, genuinely-attributable ellipse was correctly searched across 12 deep DECam nights
(+ reconfirmed PS1), and no moving source is present in the DR2 source catalogs. Most likely the
object at V~22 is at/below reliable single-epoch catalog-inclusion limits (a real detection may exist
in PIXELS but not in the extracted catalogs). Remaining, un-done EV = Datalink FITS cutouts + PSF/
forced photometry on the tightest nights (DECam 56951/56962/56976 g/r/i @SMAA 7.2"; PS1 55088/55089
@SMAA 1.2"). No catalog-level chain survives.

## FILES
- search_log.csv          — 12 corrected DECam nights (pred, box offset vs buggy, in-3sigma, negctrl, chain result)
- predn_corrected.json    — per-night ephemeris (one-epoch-per-night, datetime_jd-asserted)
- nsc_real_results.json   — full in-3sigma detections + objectid + motion pairs (real boxes)
- nsc_neg_results.json    — negative control (+1 deg Dec)
- tallies.json            — real vs control counts, mis-centering table
- nsc_corrected.py, build_outputs.py — reproducible pipeline

## SUBMISSION: NONE. Nothing submitted to MPC or any external service (per rules). USER review only.
