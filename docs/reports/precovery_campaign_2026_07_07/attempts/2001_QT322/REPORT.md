# Precovery attempt — 2001 QT322

Date: 2026-07-07 | Work dir: /tmp/precovery_recut/attempts/2001_QT322/
Analyst: automated recovery agent (for USER review; NOTHING submitted)

## OUTCOME: NULL_SEARCHED (clean, well-tested null)
No credible archival precovery. The target's gate-passing tight uncertainty ellipse was
genuinely searchable (unlike the pilot's sky-spanning failures); the search was executed across
50 deep-survey nights; every candidate was rejected by the chain discipline (stationary-source
rejection + motion consistency). No coherent moving track exists in the archival catalogs within
the 3-sigma region. A properly-tested absence, NOT an un-searchable region.

## TARGET & WHY IT PASSED THE GATE
- 2001 QT322: distant (multi-opp) TNO. H=6.09, a=37.17 AU. Discovery arc 2001-08-21 -> 2008-08-29
  (6 oppositions, 19 obs). MPC packed desig K01QW2T, perm# D5182.
- Gate row (rank 3, score 0.5976): best epoch 2005-07-01, V=21.95, SMIA_3s=0.52", SMAA_3s=1.47".
- DISTINCTION vs pilot: pilot targets (2001 QU297, 1999 JB132) had sky-spanning 3-sigma regions
  (SMIA thousands of arcsec, along-track wrapped) => un-attributable. QT322's 6-opposition orbit
  keeps a TIGHT ellipse across the whole archival window (SMAA 1.2"-18.6", 2003-2018). SEARCHABLE.
- Discovery arc ENDS 2008-08-29 -> PS1 (2009-2014) and DECam (2014-2018) era is UN-linked; any
  coherent recovery there is genuinely new astrometry. The intended tight-extrapolation case.

## EPHEMERIS / UNCERTAINTY (JPL Horizons; quantities 1,3,9,36,37)
  epoch        RA(deg)   Dec(deg)  V      SMAA_3s   SMIA_3s
  2005-07-01   358.2779   0.7303   21.96   1.47"     0.52"
  2013-01-01     6.6157   4.0098   21.98   4.37"     1.25"
  2017-07-01    16.1431   7.8034   22.00  14.07"     1.99"
  2021-01-01    18.5416   8.6104   21.99  20.31"     2.58"
Per-footprint values in eph_by_jd.json; gate epochs in horizons_uncertainty.csv.

## COVERAGE ASSEMBLED
SSOIS (CADC ssosclf.pl): 1303 footprints (DECam 200, PS1 174, CFHT 53, HSC 19, VLT/FORS2 36,
NTT/EFOSC 41, + shallow ZTF/WISE/SDSS). Per-footprint Horizons uncertainty (8 batched calls).
504 DEEP footprints have SMAA_3sig < 30" (region fits one deep field = ATTRIBUTABLE): DECam 184,
PS1 174, CFHT 52, NTT 41, VLT/FORS2 36, HSC 17. SMAA range 1.23-18.57".

## SEARCH EXECUTED (50 nights; per-night log in search_log.csv)
Two independent no-account catalog channels, each following the object's motion (cone re-centered
on the predicted position at EACH night, not a fixed cone):
1. PS1 DR2 detection table (MAST): 38 nights, 2009.7-2014.9, tightest SMAA 1.23". 26 raw
   in-3sigma detections across 6 nights.
2. NSC DR2 meas (NOIRLab Astro Data Lab TAP, anon): 12 tightest DECam nights, 2014.8-2017.7,
   SMAA 7-14". 32 raw in-3sigma detections. DECam reaches ~23-24 (deep enough for V~22).

## CHAIN DISCIPLINE — how every candidate was rejected
A (stationary rejection, PS1): full multi-epoch history of each matched PS1 objID pulled. 9/17
  matched objIDs are STATIONARY STARS (>=2 nights, fixed position span <2"). 8 survivors are all
  single-detection objIDs (one exposure) => cannot establish motion.
B (motion consistency, PS1): every same-night detection pair tested vs predicted motion
  (2.5-3.4"/hr). NO pair matched (best resid 2.17" @MJD55501, 6.01" @MJD56913; threshold 1.5").
  Apparent "pairs" were unrelated single sources scattered in the box, not a track.
C (stationary rejection, NSC/DECam): in-3sigma detections clustered by fixed sky position. EVERY
  multi-exposure cluster is a stationary star. Decisive: MJD57193 source held fixed (<0.1" span)
  over a 23.4h baseline where the TNO would have moved 80.5". Single-exposure detections
  (baseline=0) carry no motion info = field noise in the wide (43-59") DECam 3-sigma box.
D (magnitude sanity): predicted V~21.8-22.0. Bright "matches" (mag 17-20) auto-fail; faint ones
  survive on brightness but fail motion/stationarity.
E (NEGATIVE CONTROL, +1 deg Dec offset, identical pipeline):
  - PS1: real 26 in-3sig vs offset 32 -> real NOT cleaner (field-star density, not the object).
  - NSC/DECam: real 32 vs offset 13 -> real higher only from survey-pointing bias (SSOIS selects
    footprints pointing at the nominal ephemeris track; offset lands in sparser sky). NOT an object:
    none of the 32 real-box detections form a track (A-D).
A genuine chain = one source moving at the predicted rate AND cleaner than control. Neither
channel produced that. => NULL confirmed.

## WHY NULL DESPITE TIGHT UNCERTAINTY (honest)
Region fully searchable; catalogs contain no moving source at the predicted track. Likely: (a) at
V~22 the object is at/below reliable single-epoch catalog-inclusion limits (PS1 3pi ~21.5-22; near
it for NSC/DECam) so a real detection may exist in PIXELS but not in source catalogs; (b) deep
frames reaching it may lack >=2 resolving exposures at the exact along-track position on one night.
NEXT STEP (not done; needs pixels): Datalink FITS cutouts + PSF photometry on the tightest nights
(PS1 MJD55088/55089 @SMAA 1.2"; DECam MJD56951 g/r/i @SMAA 7.2") could recover a sub-catalog-
threshold detection. No catalog-level chain survives.

## NEGATIVE CONTROL SUMMARY (CHAIN rule 5)
PS1: real in-3sig=26, +1deg offset=32. NSC: real=32, offset=13 (survey-pointing bias; 0 coherent
tracks either way). Logged in nsc_negcontrol.log, negcontrol_hits.json.

## FILES
search_log.csv (50 nights); horizons_uncertainty.csv; attributable_footprints.json (504);
deep_footprints.json; eph_by_jd.json; ps1_3sig_matches.json; objid_stationarity.json;
nsc_decam_results.json; nsc_search.log; nsc_negcontrol.log; negcontrol_hits.json;
mpc_getobs_raw.json (OBS80 discovery arc 2001-2008).

## SUBMISSION: NONE. Nothing submitted to MPC or any service (per rules). USER review only.
