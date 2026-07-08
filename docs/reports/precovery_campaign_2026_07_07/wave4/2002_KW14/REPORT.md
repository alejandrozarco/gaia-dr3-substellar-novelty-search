# Precovery / Recovery Attempt — 2002 KW14 (307251) — wave-4

Work dir: /tmp/precovery_wave4/2002_KW14/  |  Date: 2026-07-08  |  Rules 1-8 applied.
Target (referee-gated): TNO 307251 (2002 KW14), a=46.5 au, e=0.20, i=9.78, H=5.51.
Gate: 16 DECam frames within +/-45 d of 2017-07-01, gate SMIA 0.21"/SMAA 0.54", V~21.8, gal b=+12.8.
Referee CORRECTED arc-end to ~2015 (not 2009) -> nominal leverage ~+2 yr.

## OUTCOME: NULL_SEARCHED
Genuine post-arc window, properly searched. No candidate chain, and none possible in principle:
the 16 "DECam frames" are 4 Y-band exposures in a single ~8-min sequence on ONE night
(2017-05-17, MJD 57890, at the -45 d edge). On 3 of the 4 exposures the target falls OFF the DECam
array; on the 1 usable exposure the NSC DR2 catalog shows a clean NON-DETECTION at the predicted
position despite depth ~1.5-2.5 mag fainter than the target. Negative control clean; bycatch clean
(0 unknown candidates).

## Rule 7 — Fresh MPC get-obs parse (run-time, not cached CSV)
POST https://data.minorplanetcenter.net/api/get-obs {"desigs":["2002 KW14"],"output_format":["OBS80"]}
-> 200, 67 optical OBS80 lines parsed fresh at run time (mpc_getobs_raw.json, obs_parsed_fresh.json).
- Parsed ARC START: 2002-05-17.261 (stn 675 = Palomar; discovery Trujillo/Brown)
- Parsed ARC END: 2015-05-15.515 (stn F51 = Pan-STARRS1)
- Stations: F51x26, 675x12, 809x12, 644x4, 688x4, 250x4, G96x3, 304x2. Years 2002-06,09,11,13,14,15.
- ZERO observations in 2016, 2017, or 2018. W84 (CTIO/DECam) contributes NOTHING to the arc.
- JPL SBDB cross-check: first_obs 2002-05-17, last_obs 2015-05-15, n_obs 90, arc 4746 d,
  condition_code 3, rms 0.51". Referee "arc-end ~2015" CONFIRMED (not 2009).

## Rule 8 — Self-arc test on the 2017-07 DECam window
SSOIS-confirmed DECam frames all fall on ONE night, 2017-05-17 (MJD 57890), at the -45 d edge.
- The fresh MPC record ends 2015-05-15 and contains NO 2017 observation (2.0 yr gap before window).
- W84 (CTIO/DECam) never contributed to the arc at any epoch.
- Verdict: NOT a self-arc. Genuinely post-arc, searchable. SELF_ARC_SKIP = NO.

## Coverage reality (Rule 4 — per-epoch SSOIS at the search epoch)
SSOIS bynameHorizons, 2017-05-01..2017-08-20 -> ssois_2017.tsv. In the +/-45 d window:
- CTIO-4m/DECam: 16 rows = 4 Y-band exposures, single night MJD 57890 (2017-05-17), spanning
  0.13 h (~8 min). (16 = 4 exposures x 4 pipeline products ori/oki/ooi/opi.)
- Also present but out of scope (not DECam): VISTA/VIRCAM H 2 nights (57894, 57903), NTT/EFOSC
  2 nights, Skymapper 1 frame — all shallow/near-IR, no DECam second night exists.
=> Maximum obtainable from the gated DECam data is a single ~8-min tracklet, NOT a multi-epoch chain.

## Rule 1/3 — Re-derived per-exposure ephemeris + boxes (Horizons, obscode W84)
Horizons OBSERVER, CENTER='W84', TLIST = the 4 SSOIS exposure MJDs (horizons_w84_4exp.txt):
- 03:19:01 UT  RA 252.079046  Dec -24.789008   |  03:20:45  252.079021 -24.789007
- 03:23:45 UT  RA 252.078978  Dec -24.789004   |  03:26:42  252.078935 -24.789001
- APmag V = 21.78; 3-sigma ellipse SMAA 0.442" / SMIA 0.201" (theta -16.4 deg) — matches gate.
- Time-axis alignment asserted (Rule 1): predicted positions computed AT the SSOIS MJDs;
  cross-checked vs NSC exposure-table MJDs (agree <2 min -> <0.1" of on-sky motion). My Horizons
  RA/Dec also agree with SSOIS's own Horizons prediction to ~0.1". Intra-sequence motion ~0.4" total.

## NSC DR2 catalog search, re-centered per exposure (Rules 3,4,6) — search_log.csv
All 4 DECam exposures are ingested in NSC DR2 (nsc_dr2.exposure). Pointing centers are dithered by
up to 0.3 deg; the target (252.079/-24.789) sits 0.83-1.08 deg from each center — at/near the DECam
field edge:
- 031953 & 032252: target ~1.04-1.08 deg from center -> OFF the DECam array (0 detections within
  72" of the predicted position). No search possible.
- 032551: target in a chip-gap / array edge on this dither (0 src within 72"; nearest 78").
- 032849 (ONLY usable exposure): target lands squarely on a working, densely-populated CCD
  (377 detections within 72"). Exposure reaches Y_faint = 22.65 (456k sources) — i.e. ~1.5-2.5 mag
  DEEPER than the target's expected Y ~ 20-21 (red TNO, V-Y ~ 0.8-1.7 vs V_pred 21.78).
  Nearest catalog source to the predicted position = 1.73", i.e. ~4x the SMAA and ~9x the SMIA
  of the 3-sigma ellipse -> OUTSIDE the box. The three nearest sources are all confirmed STATIONARY
  field objects (nsc_dr2.object): 139366_91157 (1.73", ndet 33 / 1106 d), 139366_77340 (2.08",
  bright star ndet 40 / 2300 d), 139366_77339 (2.99", ndet 41 / 2300 d) — many detections at fixed
  positions over 3-6.3 yr; none can be the one-night moving TNO. => clean catalog non-detection.

The non-detection here is NOT a depth artifact (unlike wave-4 sibling 2007 HV90, where V~22.9 sat at
the Y limit): the target is well above threshold, so a real source would have been catalogued within
the 0.44" ellipse if present. Its absence is a genuine non-detection on the single usable exposure.

## _ooi_ cutout inspection (Rule 2) — attempted, service-limited, not needed
astroarchive svc/cutout -> 404; SIA voimg -> VOTABLE with 0 rows; positional cutout requires the
full 326 MB MEF / datalink route (same limitation documented for 2007 HV90). Not pursued: the
catalog result is already conclusive (target 1.5-2.5 mag above depth, on-array, nearest source a
confirmed static star), and a single-exposure pixel blob could not be chained or confirmed moving
regardless (target off-array on the other 3 exposures).

## Rule 6 — Chain discipline + negative control
- Chain: NONE possible. One usable exposure only; the 4-exposure sequence spans ~8 min, over which a
  46-au TNO moves ~0.4" (below astrometric resolution). Cannot demonstrate motion, cannot chain.
- Stationary-source rejection: the 3 nearest sources on 032849 are all multi-year static objects
  (rejected). No transient/one-night source anywhere in the ellipse.
- +1 deg negative control (Dec +1.0, exposure 032849): 278 sources in the 72" box (region on-array),
  nearest 2.64", ZERO inside the 0.44" ellipse — matching the on-target result. Clean (negctrl_p1deg.json).

## Rule 5 — Mandatory bycatch pass
PYTHONPATH=<repo>/scripts/precovery, bycatch.run_bycatch(detections, static_sources=NSC mean-object
catalog, identify=True). Ran over the central region covered by all 4 dithers (multi-exposure overlap,
where tracklets are geometrically possible): 6792 detections, 5310 NSC static sources.
-> n_tracklets 0, n_unknown_candidate 0. Rejections: too_fast 16.57M (the ~8-min baseline makes any
cross-source pairing look absurdly fast), not_same_night 6.47M, on_static 24919, stationary_rate 1756.
A genuine slow TNO on a single 8-min sequence necessarily lands in stationary_rate — reinforcing the
no-chain finding. No referee leads. (bycatch_summary.json, bycatch_tracklets.csv)

## Files (all under /tmp/precovery_wave4/2002_KW14/)
mpc_getobs_raw.json, obs_parsed_fresh.json, mpc_obs80.txt, sbdb.json (Rule 7);
ssois_2017.tsv (Rule 4 coverage); horizons_w84_4exp.txt (Rule 1/3 ephemeris+boxes);
nsc_meas_byexp_box.json, nsc_meas_cone*.json (catalog search, stationarity);
search_log.csv (per-exposure); negctrl_p1deg.json (negative control);
bycatch_dets.json, bycatch_static.json, bycatch_summary.json, bycatch_tracklets.csv (Rule 5).
No candidate_astrometry.csv (no chain — correct).
