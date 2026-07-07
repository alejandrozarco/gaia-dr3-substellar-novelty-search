# JOB 2 — Value of our 6 DECam points for (330836) Orius = 2009 HW77
Date: 2026-07-07

HEADLINE: Adding our 6 pixel-verified W84/DECam points shrinks the sky-plane
1-sigma ephemeris uncertainty ~3x at every epoch (2026/2030/2040) AND recenters
the predicted position by ~7-14" (~1.9 sigma of the arc-only error). All 6 points
retained with sub-arcsec residuals.

## Method
Tool: find_orb console `fo` (Project Pluto, ver 2026-05-26), build reused from
/tmp/precovery_verify/2001_KN76/build/find_orb/fo. Full N-body LSQ with planetary
perturbers. Covariance propagation = find_orb native ephemeris-uncertainty output
(EPHEM_OPTIONS bit 16); it forms a 1-sigma variant orbit from the 6x6 covariance
and integrates to each epoch, reporting the semi-major axis of the sky-plane
1-sigma error ellipse (" sig column), geocentric MPC code 500. No Monte-Carlo
needed (find_orb yields a defensible propagated covariance directly).
Obs: 85 MPC arc from get-obs API ADES_DF (2002-02-12..2012-05-19; USNOB1/UCAC2/
2MASS auto-weighted); our 6 from updated_astrometry.csv as ADES rows with measured
per-axis sigma 0.12-0.25", astCat Gaia2, stn W84. Arc-only ADES fit reproduces the
OBS80 fit exactly (validates ingestion).

## Solution (a) arc-only 2002-2012, 85 obs, epoch 2012-05-19
a=21.3982439 +/-0.000727  e=0.4178754 +/-1.8e-5  i=17.89894 +/-4.1e-5
q=12.4564441 +/-3.81e-5   node=50.42136  peri=140.39384  P=98.98 yr
82/85 used; mean resid 0.42"; MPC U=3.0

## Solution (b) joint incl our 6, 2002-2015, 91 obs, epoch 2015-04-27
a=21.4837160 +/-0.000304  e=0.4202285 +/-7.46e-6  i=17.87420 +/-2.9e-5
q=12.4556455 +/-1.7e-5    node=50.38835  peri=140.52977  P=99.58 yr
89/91 used; mean resid 0.44"; MPC U=2.5
Element sigmas tighten ~2-2.4x; arc 10.3->13.2 yr; U 3.0->2.5.

### Our 6 W84 points (all retained, residuals RA/Dec arcsec)
2013-03-02 tu2037227:  +0.00 +0.25
2013-03-02 tu2037424:  -0.10 +0.33
2014-06-27 c4d_140627_015128: -0.14 +0.04
2014-06-29 c4d_140629_021153: -0.10 -0.13
2015-04-27 c4d_150427_053222: +0.14 +0.00
2015-04-27 c4d_150427_053734: +0.23 +0.12
Max resid 0.33"; consistent with assigned sigmas. Sanity check PASSES.
(The 2 rejected obs in soln b are both old arc points, not ours.)

## Ephemeris impact (sky-plane 1-sigma, arcsec, geocentric 500)
epoch       arc-only   with-6pts  shrink   arc-vs-joint pred offset   offset/arc-sigma
2026-07-01    3.69       1.11      3.3x     6.9"                       1.88
2030-01-01    4.27       1.34      3.2x     8.1"                       1.89
2040-01-01    7.33       2.51      2.9x    14.1"                       1.92

Meaning: recovery box shrinks ~3x/axis (~10x area); arc-only prediction was
biased ~1.9 sigma (~7-14"), so a naive recovery at the arc-only position risked
being mis-centered. Occultation shadow-path cross-track uncertainty shrinks the
same ~3x (~1" vs ~4" at 21 AU in 2026) -> Orius becomes campaign-able for
occultations through the 2030s.

## Caveats
1. No JPL DE installed (find_orb used internal analytic series). Slightly degrades
   ABSOLUTE point prediction but not the RELATIVE result (identical model both
   solutions); regenerate absolute coords with DE440 before a real pointing.
2. Linearized variant-orbit covariance; valid for U=2.5-3.0 over 14-28 yr but can
   mildly understate non-linear spread far from arc -> true value of our points is
   if anything a touch larger than the linear ratio.
3. " sig is the semi-major (worst, ~along-track) axis = correct search-box width.

## Files (all /tmp/orius_deepdive/)
REPORT.md, ephemeris_uncertainty.csv, arc_only.psv, combined_all.psv,
elements_arc_only.txt, elements_combined.txt, residuals_combined.txt,
mpc_obs.txt, eph_arc_only.txt, eph_combined_all.txt
