# Precovery attempt — 2001 KP76 (= (189067), packed K01K76P, perm# B9067)

Date: 2026-07-07 | Work dir: /tmp/precovery_wave2/2001_KP76/
Analyst: automated recovery agent (wave-2, USER review; NOTHING submitted to MPC or any service)

## OUTCOME: NULL_SEARCHED (clean, well-tested null)
No credible archival precovery. The post-discovery-arc gate-passing epochs were searched across two
independent no-account catalog channels (NSC DR2 DECam + PS1 DR2). Every in-ellipse detection is a
catalogued stationary star; no coherent moving source at the predicted track survives the chain
discipline; the negative control is not cleaner than the real field. Honest caveat: at V~22.7, diving
into the Galactic bulge, the object sits at/below reliable single-epoch catalog-inclusion limits, so a
real detection may exist in PIXELS but not in the extracted source catalogs.

## TARGET & WHY IT PASSED THE GATE
- 2001 KP76: distant multi-opp TNO. H=6.33, a=43.36 AU. Discovery arc 2001-05-23 -> 2007-05-08
  (6 oppositions, 26 astrometric obs via MPC get-obs OBS80). Now numbered (189067).
- Gate row (rank 13, score 0.5608): best epoch 2005-07-01, V=22.79, SMIA_3s=0.79", SMAA_3s=1.85",
  deep footprints ~4808 (DECam 3817, PS1 140, CFHT 193, HSC 13, VLT/VISTA 624).
- Re-derived ephemeris (JPL Horizons, obs W84, quantities 1,3,9,36,37) reproduces the gate log EXACTLY
  at all 4 epochs (SMAA 1.85/13.91/33.40/55.76"; SMIA 0.79/3.22/5.07/6.12"; V 22.79/22.71/22.52/22.54).
  Built one-epoch-per-call with per-night datetime_jd assertion |dJD|<1e-3 (STANDING RULE 1); per-night
  predictions cross-check the SSOIS byname positions to 0.26".

## KILLER CONTEXT (load-bearing)
Galactic latitude COLLAPSES across the passing window:
  2005-07-01 l=351.3 b=+18.9 (cleanest, but INSIDE arc + pre-NSC);
  2013-01-01 l=356.4 b=+9.3  (post-arc; NSC DR2 DECam);
  2017-07-01 l=358.3 b=+4.5  (very crowded);
  2021-01-01 l=0.9   b=-0.5  (Galactic-center; extreme crowding).
The tight NEW-astrometry epochs (post-arc; arc ends 2007-05) are exactly the ones buried in dense bulge
fields. PS1 cones hold 300-2460 detections; NSC DECam boxes hold tens-hundreds of stationary sources.

## COVERAGE (CADC SSOIS ssosclf.pl byname/Horizons)
2720 footprint rows 2004-2022. Deep-optical: DECam 2013(24)/2014(24)/2017(116)/2019(195)/2022(1192);
CFHT/MegaCam 2006(21)/2019(9)/2022(32); Subaru/HSC 2017(13); + IR (VISTA/NACO/HAWKI/NIRI) and shallow
PS1/WISE/Skymapper/LCO. Searchable deep-optical post-arc set = DECam 2013/2014/2017 + PS1 2010-2012.

## SEARCH EXECUTED (per-night log in search_log.csv)
Each channel re-centers on the Horizons position at EACH night's MJD and gates inside the 3-sigma error
ELLIPSE (SMAA/SMIA/Theta), propagating the 2.9-4.1"/hr intra-night motion.
1. NSC DR2 meas (Astro Data Lab TAP, anon): 13 DECam nights MJD 56361-58690 (2013.2-2019.5),
   SMAA 16-48", 599 raw in-ellipse total.
2. PS1 DR2 detections (MAST): 35 nights MJD 55250-56068 (2010.1-2012.3), SMAA 15-23", 77 raw in-ellipse.
Tightest post-arc constraint = 2013 pair MJD56361/56362 (consecutive nights, 12 DECam r-frames each):
8 in-ellipse on 56361, 0 on 56362 -> no cross-night track possible at catalog level.

## CHAIN DISCIPLINE — every candidate rejected
- STATIONARY REJECTION (decisive, rule 3): all 216 distinct NSC in-ellipse objectids resolved in
  nsc_dr2.object. 212/216 are multi-detection, multi-year mean objects (stationary stars) -> reject.
- 4 SURVIVORS all fail: 144501_24584 (single ndet=1, no motion, g=21.4); 144501_57595 (2 det same
  night 57863, z~20); 144501_57472 (2 det same night 57864, class_star=0.0006 = extended);
  144501_55159 (ndet=4 within ~1 d, z~20.4). All >1 mag BRIGHTER than V~22.6 (rule 4) and NONE forms a
  coherent ~70-90"/day track across nights (rule 2). No chain survives.
- PS1: scattered 0-15/night, no cross-night coherence; depth ~21.5-22 at/below V~22.7.

## NEGATIVE CONTROL (+1 deg Dec offset, identical pipeline, rule 5)
- NSC DECam: real in-ellipse 599 vs offset 328. Real higher = survey-pointing bias (SSOIS selects
  DECam fields pointed at the nominal track; offset lands in adjacent sky) — same artifact as wave-1
  2001 QT322. Decisive fact: 212/216 real sources are catalogued stationary stars; no track exists.
- PS1: real 77 vs offset 91 — real LOWER than control. Clean.
A genuine detection = one source moving at the predicted rate AND an excess over control. Neither
channel produced that. => NULL confirmed.

## EPOCHS SEARCHED / NOT SEARCHED (honesty)
- 2013/2017(+2019) post-arc DECam: SEARCHED (NSC DR2), null.
- 2010-2012 PS1: SEARCHED (PS1 DR2), null.
- 2005-07-01 pinpoint (SMIA 0.79"): NOT catalog-searched — pre-NSC(~2012) AND INSIDE the 2001-2007 arc
  (recovery there densifies an already-observed apparition = low novelty). Deep-optical there = CFHT/
  MegaCam 2006 (21 frames) via CADC Datalink = pixel-level EV only, deferred.
- 2021 epoch: SMAA 55.8" at b=-0.5 (Galactic center); gate deep-optical frames are 2022 (past window)/IR.
  Not catalog-tractable.

## REMAINING EV (not done; needs pixels)
Datalink FITS cutouts + PSF/forced photometry on 56361/56362 (SMAA 16") with locally Gaia-DR3-anchored
WCS could in principle recover a sub-catalog-threshold detection, but extreme bulge crowding makes a
clean measurement unlikely. No catalog-level chain survives.

## FILES
mpc_getobs_raw.json; gate_epoch_ephem.json; ssois_byname.tsv (2720 rows); eph_decam.json (JD-asserted);
nsc_real.json/nsc_neg.json; objectid_stats.json (216 ids, 212 stationary); eph_ps1.json/ps1_real.json/
ps1_neg.json; search_log.csv (48 nights + 2005 note); tallies.json.

## SUBMISSION: NONE. Nothing submitted to MPC or any external service (per rules). USER review only.
