# Precovery / Arc-Extension Attempt — 2009 HW77

Date: 2026-07-07 | Work dir: /tmp/precovery_recut/attempts/2009_HW77/
Stack: JPL Horizons (astroquery.jplhorizons, ellipse q=1,9,36,37) -> CADC SSOIS byname footprints
-> NOIRLab Astro Data Lab NSC DR2 meas/object (anonymous TAP) -> MAST PS1 DR2 detection.
Zero accounts. Measurement/reporting ONLY. Nothing submitted anywhere. Submission is the user's action.

## OUTCOME: CANDIDATE_CHAIN
A 4-epoch, post-discovery-arc precovery chain in CTIO-4m/DECam archival imagery (via NSC DR2),
each epoch an independently-confirmed single-night transient matching the JPL orbit (derived from
the 2002-2012 MPC arc) to 0.03-0.41 arcsec at the predicted magnitude. Negative control clean.
Recommended for USER review toward ADES astrometry (arc extension 2012 -> 2015, +2.9 yr).

## TARGET CONTEXT
- 2009 HW77: inner-system (Hungaria-region), H=9.73, a~1.9 AU, 7 oppositions, MPC arc 2002-02-12 -> 2012-05-19 (85 obs).
- Gate row (campaign_targets.csv rank 7): best epoch 2013-01-01 V=21.6 SMIA=0.25" SMAA=0.57", passes 4/4 gate epochs; 845 deep footprints (DECam 403, PS1 113, CFHT 37, VLT/VISTA/Subaru 257).
- Antithesis of the pilot's UNUSABLE case (2001 QU297, sky-spanning region): here the 3-sigma error
  ellipse stays SMIA<0.5", SMAA<7" at EVERY archive epoch 2005-2021 — pinpoint-recoverable.

## POSITIVE CONTROL (pipeline validation)
Horizons reproduces KNOWN MPC positions at arc endpoints: 2012-05-19.412 (F51) sep=0.07";
2005-06-05.203 (645) sep=0.18". Pipeline validated to <0.2".

## CHAIN-DISCIPLINE AUDIT
1. SEARCH BOX = gated 3-sigma region: YES. SMAA 0.8-2.3", SMIA 0.27-0.38".
2. MOTION CONSISTENCY: 2013-03-02 and 2015-04-27 each have >=2 same-night detections; all 4 epochs
   co-fit the single 2002-2012 orbit to sub-arcsec; 2014-06-27 object present in 01:49 exposure but
   absent at its moved (+29" at 6.8"/hr) position in the +4.28h exposure — excludes a static star.
3. STATIONARY-SOURCE REJECTION: PASSED. Each match is an NSC object with ndet=1-2, deltamjd 0-5 min
   (single-night transient), NOT the multi-year (deltamjd 1400-2000 d) static stars 1-5" away.
   2013 explicitly disambiguated: transient (246.12949,-26.25183) ndet=2/deltamjd=2.1min r=21.59,
   separate from red static star (246.12925,-26.25197) ndet=23/deltamjd=1451d i=21.6/y=20.8 (~1.0" off).
4. MAGNITUDE SANITY: PASSED. 21.5-21.8 (r/VR) vs predicted V 21.5-21.8.
5. NEGATIVE CONTROL (+1 deg Dec, same nights, same box): CLEAN. Offset boxes comparably populated
   (250-1877 rows) but ZERO same-night detections within 1.2" at any mag. Coincidence excluded.
6. LOGGING: all epochs (candidate + null) in search_log.csv.

## MEASURED ASTROMETRY (for USER review — NOT submitted)  [full: FINAL_astrometry.csv]
CTIO-4m/DECam, NOIRLab community pipeline; NSC DR2 meas per-det astrom err ~0.13-0.21"/axis.

night(UT)   MJD(UTC)      RA(J2000)    Dec(J2000)    mag   filt  resid  3sig(SMAA/SMIA)
2013-03-02  56353.32383   16 24 31.08  -26 15 06.6   21.63 r     0.41"  0.82"/0.27"
2013-03-02  56353.32533   16 24 31.08  -26 15 06.6   21.57 r     0.33"  0.82"/0.27"
2014-06-27  56835.07565   16 37 59.66  -29 56 21.1   21.83 VR    0.09"  1.20"/0.34"
2014-06-29  56837.08979   16 37 35.12  -29 55 49.3   21.60 VR    0.14"  1.19"/0.34"
2015-04-27  57139.22940   17 21 13.68  -32 22 44.9   21.53 VR    0.15"  2.29"/0.37"
2015-04-27  57139.23297   17 21 13.65  -32 22 44.9   21.66 VR    0.03"  2.29"/0.37"

Est. per-det uncertainty for ADES: sigma_RA ~ sigma_Dec ~ 0.15-0.2". Obscode CTIO-4m/DECam = W84.
Archival-astrometry ADES submission coordinated with survey/SARC, measurer named (GATE-R1 mechanics).

## SUPPORTING (sub-threshold, not counted in chain)
- 2013-06-25 (MJD 56427.489) Pan-STARRS1 DR2: single g=21.73 detection 0.34" from F51 prediction,
  non-stationary (objID 75902441251563620 = 1 detection ever). Right mag/place/motion but single-band
  single-epoch -> corroborating context only. Independent survey+epoch raises confidence.

## NULLS (honest)
- 2015-05-20 / 2015-05-21 DECam: no clean sub-arcsec transient (nearest 2.9-4.3" out, multi-night objs).
- 2013-06-25 NSC DECam box: 0 on-night detections.
- 2010-2011 PS1 opposition: positions already in arc; PS1 single izy visits too shallow at V~21.
- NSC DR2 TAP meas had a ~40-min 504 degradation mid-run; recovered; final queries used RA/Dec
  bounding-box + tight q3c radius (~5 s each).

## RECOMMENDATION
Four post-arc DECam epochs (2013-03-02, 2014-06-27, 2014-06-29, 2015-04-27) form a credible precovery
chain extending 2009 HW77's arc 2012 -> 2015 (+2.9 yr). USER should: (a) pull DECam FITS cutouts
(Datalink/NOIRLab) at these frames/positions to visually confirm and re-centroid; (b) coordinate ADES
PSV via survey SARC, obscode W84, measurer named; (c) verify via WAMO. Do NOT submit without
image-level confirmation. This report is measurement only.

## ARTIFACTS
FINAL_astrometry.csv; candidate_astrometry.csv; search_log.csv; ephem_nights.csv; ephem_uncertainty.csv;
nsc_2013.csv..nsc_2015c.csv, nsc_2013jun.csv; obj_m*.csv; neg_*.csv; ps1_det_2013.csv, ps1det_p*.csv,
hist_*.csv; err_2013.csv, err_2014a.csv; mpc_getobs.json.
