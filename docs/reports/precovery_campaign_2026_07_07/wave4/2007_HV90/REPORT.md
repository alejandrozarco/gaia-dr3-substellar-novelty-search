# Precovery / Recovery Attempt — 2007 HV90 (wave-4)

Work dir: /tmp/precovery_wave4/2007_HV90/  |  Date: 2026-07-07  |  Rules 1-8 applied.
Target (referee-gated): distant-multiopp TNO; H=6.6, a=43.84 au; gate window 2017-07-01 +/-45 d,
28 DECam frames, V~22.9, gal b=+15.7, gate SMIA 0.30"/SMAA 0.58".

## OUTCOME: NULL_SEARCHED
Genuinely post-arc window, properly searched with a tight re-derived per-frame ephemeris.
No usable candidate chain: NSC DR2 catalog non-detection at the predicted position on all 8
DECam Y exposures; nearest source is a confirmed stationary field object (rejected); negative
control clean; bycatch clean (0 unknowns). Structurally the window is single-night only, so no
multi-epoch motion-consistent chain is possible even in principle.

## Rule 7 — Fresh MPC get-obs parse (run-time, not cached CSV)
GET https://data.minorplanetcenter.net/api/get-obs (POST 405s; GET works) -> 32 OBS80 lines.
- Parsed ARC START: 2007-04-21.234 (stn 807)
- Parsed ARC END:   2016-06-13.417 (stn F51 = Pan-STARRS1)
- Stations: F51x23, W84x4 (all 2015-05), G37x2, 807x3. Years 2007,2011,2013,2014,2015,2016.
- JPL SBDB cross-check: first 2007-04-21, last 2016-06-13, n_obs 31, arc 3341 d, U=4, rms 0.65".
  Referee "arc-end ~2016" CONFIRMED.

## Rule 8 — Self-arc test on the 2017-07 DECam window
SSOIS-confirmed DECam frames all fall on ONE night, 2017-05-17 (MJD 57890), at the -45 d edge.
- Zero observations anywhere in 2017 in the fresh MPC record (arc ends 2016-06-13, ~11.2 mo prior).
- W84 (CTIO/DECam) contributed to the arc only 2015-05-20..24 — a different epoch. The 2017-05-17
  frames add genuinely new astrometry.
- Verdict: NOT a self-arc. Genuinely post-arc, searchable. SELF_ARC_SKIP = NO.

## Coverage reality
Gate "28 decam frames" = 7-8 DECam exposures on a SINGLE night (2017-05-17), all Y-band, ~1.5 h
(28 = 7 exposures x 4 product types; NSC has 8 exposures). No 2nd night in +/-45 d => max
obtainable is a single-night tracklet, not a multi-epoch chain.

## Rule 1/3 — Re-derived per-frame ephemeris + boxes (Horizons, obscode W84)
- Horizons vs SSOIS predicted positions agree to <0.16" on every frame (time-axis aligned).
- V = 22.83; 3-sigma ellipse SMAA = 0.622", SMIA = 0.296" (matches gate 0.58"/0.30"). Tight box.
- Intra-night motion ~0.8" total (~0.5"/hr; near-stationary within the night).

## NSC DR2 catalog search, re-centered per night (rule 3,6)
- No catalog source within the 3-sigma ellipse (0.62"), nor within 2.7", of the predicted moving
  position on ANY of the 8 exposures.
- Nearest on-night source = obj 134244_29995 at 2.75-3.1". Stationary test: RA/Dec scatter
  0.021"/0.018" over 193 epochs / 1932 d (2014-2019), i/Y/VR/g, mag ~20-21 -> static. REJECTED.
- Depth: NSC per-exposure Y faint end ~21.5-21.7; red TNO at V=22.83 has Y~21.3-21.6 (at/below
  threshold) -> catalog non-detection is expected; not by itself proof of absence.

## _ooi_ cutout inspection (rule 2) — attempted, service-limited
svc/cutout?siaRef=<ooi>&POS&SIZE returns a fixed CCD (S29, pointing centre 0.5 deg off), not a
positional cutout; SIA voimg returned only a COUNT. 6 full _ooi_ CCDs pulled but none cover the
target pixel; a true positional cutout needs the 326 MB MEF / datalink route. Does NOT change the
outcome (single-night + at/below Y depth => a pixel blob is uncorroborable and cannot chain).

## Rule 6 — Chain discipline + negative control
- Chain: none possible. Single night; intra-night motion (~0.5"/hr) below astrometric resolution
  and below bycatch stationary floor -> cannot demonstrate motion, cannot chain.
- +1 deg negative control (Dec+1.0, same night): 37 night detections in-box; nearest to shifted
  predicted position = 9.84" (nothing in the ellipse). Clean.

## Rule 5 — Mandatory bycatch pass
run_bycatch(night_detections=120, static_sources=nsc_dr2.object[65], identify=True)
-> 0 tracklets survived (stationary_rate 186, too_fast 3150, on_static 2788, not_same_night 1016).
n_unknown_candidate = 0. No referee leads. (A real slow TNO lands in stationary_rate on a single
night — reinforcing the no-chain finding.)

## Files
mpc_obs80.txt, mpc_getobs_raw.json, sbdb.json (rule 7); horizons_ephem_W84.json (ephem+boxes);
nsc_meas_box20.json, search_log.csv (catalog search); nsc_object_static.json (bycatch static in);
nsc_negctrl_p1deg.json (neg control); bycatch_summary.json, bycatch_tracklets.csv (rule 5);
night_exposures.json, cutouts/ (cutout attempt). No candidate_astrometry.csv (no chain).
