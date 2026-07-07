# Precovery attempt — 2006 JG57 (Centaur, H=12.4, a=9.65 AU)

Date: 2026-07-07 | Work dir: /tmp/precovery_wave2/2006_JG57/
Analyst: automated recovery agent (Wave 2). USER review only. NOTHING submitted to MPC or any service.

## OUTCOME: NO_ARCHIVAL_COVERAGE
The single SMIA-gate-passing epoch (the 2005 apparition) has no archival image that contains the
object. Deep science archives (SSOIS index) have zero coverage before 2010-05; the one sky survey
that did image this region in 2005 (SDSS) scanned it ~5 months / ~30 deg away from where the object
actually was. There is nothing at the passing epoch to detect. Clean coverage null, not a detection
null — no candidate, no chain, no submission.

## TARGET / GATE ROW
campaign_targets.csv rank 6: 2006 JG57, inner-system, H=12.4, a=9.65, nopp=3, lastobs=2007,
best_epoch=2005-07-01, best_V=20.1, best_SMIA=0.94, best_SMAA=1.36, n_pass_epochs=1.
SMIA/SMAA are in arcsec (3-sigma) — confirmed by re-deriving from Horizons (SMAA_3sigma=1.36" at
2005-07-01). The gate footprint columns (decam=1481, vvs=535, ztf=147, "cfht"=31 -> actually ESO-VST
OmegaCam) are whole-arc SSOIS counts, NOT epoch-2005: every one of those 3,014 SSOIS images is dated
2010-2022 (DECam 2013-2021, VISTA 2016+, ZTF 2018+, WISE 2010+). None bears on the 2005 gate.

## MPC ARC (get-obs, OBS80) — re-pulled
48 observations, 2005-04-16 -> 2007-07-08, 3 oppositions:
- 2005-04-16 (obs 699 LONEOS): 4 obs, RA~14h51m, Dec +51.7, V~19.6  <- the entire 2005 opposition
- 2006-05-14 -> 2006-07-21 (644/703/704/699/147/204/J95/809/G96): dense main opposition, Dec +9->+1
- 2007-07-08 (D35): 3 obs, Dec -38.6
The 2005-07-01 gate epoch sits ~2.5 months after the real 2005-04-16 detections, which is why the
back-propagated uncertainty is tiny (~1"). A 2005 precovery would only densify opposition 1 (LONEOS
already holds 2005-04-16); modest value, but pursued per campaign discipline.

## RE-DERIVED EPHEMERIS (standing rule 1: one epoch per row, datetime_jd-keyed)
Horizons (astroquery), geocentric + daily over 2005-04-01..2005-10-15. The 2005 apparition track runs
RA 211-226, Dec +51.7 (Apr) -> +24 (late Sep), V 19.97-20.18, with the plane-of-sky 3-sigma error
ellipse ~1.0" x 1.2" across the ENTIRE apparition (not just the single gate-sampled date). So the whole
2005 window is a near-pinpoint search — searched it all, not just 2005-07-01.
Files: horizons_2005_geo.csv, horizons_2005_daily.csv.

## CHANNEL 1 — SSOIS deep-archive index: ZERO 2005 coverage
ssosclf.pl by-name (resolvers bynameall, bynameHorizons, bynameMPC), 2003-2022. Full-arc query returns
3,014 image rows but the earliest is WISE MJD 55339 = 2010-05-08. By-year: 2010:232, 2013:139, 2014:141,
2015:125, 2016:1675, 2017:44, 2018:152, 2019:67, 2020:13, 2021:424. 2003-2009: 0 rows. No CFHT/MegaCam,
no CTIO, no ESO, no Subaru, no HST, no Gemini image covers the object in 2005.
(Artifacts: ssois_full.tsv, ssois_bynameall_pre2010.tsv, ssois_bynameHorizons_pre2010.tsv.)

## CHANNEL 2 — SDSS DR16 (the only survey imaging this sky in 2005): temporally disjoint
Standing rule 4 route for pre-2012 windows. Two independent tests:
- Footprint probe (SDSS.query_region, r=2.9', 40 points along track): 40/40 return photoObj — the whole
  track lies inside the SDSS DR16 imaging footprint. But those detections come from SDSS runs in OTHER years.
- Space-time coincidence (decisive): SDSS Field table, RA 210-227 / Dec 19-53, restricted to 2005
  (mjd_r 53455-53665) -> 1,002 fields, all from 4 scan dates: 2005-04-19, 2005-04-26, 2005-05-26,
  2005-05-27, and ALL at Dec 19-24. On those four dates the object was at Dec ~51. Object interpolated to
  each field's mjd_r vs field center: minimum separation 1,773 arcmin (~30 deg). The object only descends
  into the Dec 19-24 band SDSS scanned by late-September 2005 — a ~5-month temporal miss. The object was
  NEVER inside a 2005 SDSS frame. (Artifact: sdss_fields_2005.csv.)

## NEGATIVE CONTROL
Track shifted +/-1 deg in Dec, identical field-match pipeline: min separation +1deg = 1,830', -1deg =
1,716' — statistically identical to the real 1,773'. The real field is indistinguishable from an offset
control because there is no spatial-temporal overlap in either case. A genuine chain would need the real
track to intersect a 2005 frame while the control does not; neither does. Null is symmetric and clean.

## CHAIN DISCIPLINE
Not reached: no image contains the object, so there is no in-3-sigma detection to test for motion,
stationarity, magnitude, or coadd-blankness. Zero candidates surfaced. Correctly no candidate_astrometry.csv.

## RESIDUAL (un-searched, not credible) EV
LONEOS (obs 699) demonstrably imaged the object 2005-04-16, and NEAT/Palomar-QUEST-era survey frames may
exist near the track — but these legacy survey archives are (a) not SSOIS-indexed, (b) not served as
queryable source catalogs, and (c) shallow (~V20 limiting, marginal for a V=20.1 target). No credible,
catalog-backed channel remains for the 2005 epoch. Real remaining EV for this object is post-2010 imaging
(3,014 SSOIS frames) — but those epochs FAIL the SMIA gate (SMAA blows up to 24"-75" by 2013-2021), so
they are search-space-lost and out of scope for a credible precovery.

## FILES
- mpc_getobs_raw.json          — full 48-obs OBS80 arc (get-obs API)
- horizons_2005_geo.csv        — 2005 window ephemeris + SMAA/SMIA_3sigma
- horizons_2005_daily.csv      — daily ephemeris (RA/DEC/V + per-axis 3-sigma)
- ssois_full.tsv               — 3,014 SSOIS image rows (all 2010-2022; proves no pre-2010 coverage)
- ssois_bynameall_pre2010.tsv, ssois_bynameHorizons_pre2010.tsv — resolver cross-checks (first row 2010-05)
- sdss_fields_2005.csv         — 1,002 SDSS 2005 fields in bbox (all Dec 19-24, Apr-May 2005)
- search_log.csv               — per-channel log (SSOIS x3 resolvers, SDSS real + neg control)

## SUBMISSION: NONE. Nothing submitted to MPC or any external service (per rules). USER review only.
