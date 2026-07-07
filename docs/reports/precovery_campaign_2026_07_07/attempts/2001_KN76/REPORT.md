# Precovery Attempt — 2001 KN76 (distant multi-opp TNO)

Date: 2026-07-07 | Work dir: /tmp/precovery_recut/attempts/2001_KN76/
Analyst: automated recovery run (Alexander Keur campaign). NO submission made — measurement + reporting only.

## OUTCOME: CANDIDATE_CHAIN (two-epoch; credible but with ONE honest tension) — hold for USER review.

A pair of DECam single-night sources, one on 2013-03-11 and one on 2015-07-15, each sit within 0.3 sigma
(cross-track) of the JPL-propagated discovery orbit of 2001 KN76, on the exact DECam images SSOIS predicts
the object to fall on. Joint chance-coincidence ~ 8e-4. Both pass stationary-source rejection and the +1deg
negative control. HOWEVER, a 5-night 2015-05 DECam run of comparable depth at the predicted position detected
nothing, which is a real (not fatal) tension. This is a report-for-review candidate, NOT a confirmed recovery,
and NOT for submission without image-level (cutout) confirmation and an orbit-refit that ingests these points.

## TARGET & GATE
- 2001 KN76: H=6.38, a=43.54 AU, single-opp discovery arc, last obs 2008, V~22.6.
- Gate best epoch 2005-07-01: SMIA_3s=0.53", SMAA_3s=1.28". SSOIS: 830 deep footprints, 366 DECam. GATE PASS.
- Reality: SSOIS DECam footprints span 2013-2023; the 2005 tight-ellipse epoch PRE-DATES all deep coverage,
  so searchable epochs are 2013+ where SMIA grew to ~2-4". Ellipse is highly elongated: SMIA(cross) 2.0-2.6"
  at 2013-2015, SMAA(along) 9-13".

## METHOD (validated zero-account stack)
1. Horizons (astroquery.jplhorizons, obs 807=CTIO): ephemeris + 3-sigma error ellipse (qty 1,9,36,37) at every
   DECam night SSOIS lists (24 nights).
2. NOIRLab Astro Data Lab TAP (anonymous), NSC DR2:
   - nsc_dr2.object cone (fast, indexed) at each predicted position, radius = 1.3*SMAA (>=15").
   - single-night sources: deltamjd<3d AND detection MJD on that night (a mover the survey cannot link across
     its multi-year baseline shows up as a single-night object).
   - per-detection nsc_dr2.meas pulled BY objectid (indexed) for exact positions/times/mags.
   NOTE: bare meas cone / MJD-range / IN(exposure) queries 504-timeout; object-cone + meas-by-objectid works.

## CHAIN DISCIPLINE RESULTS

1. Search box = gated 3-sigma ellipse — YES, per-epoch Horizons ellipse (bounded, SMIA 2-4").

2. Motion consistency
   Multi-epoch co-fit (load-bearing test): two independent DECam nights 2.3 yr apart land on ONE propagated
   discovery orbit:
     2013-03-11  id 133189_17045  sep 0.66-0.71"  along +0.63..0.67"(+0.2s)  cross +0.19..0.23"(+0.3s)  r 23.06,23.32
     2015-07-15  id 133703_14601  sep 1.07"       along +1.04..1.06"(+0.2s)  cross -0.14..-0.27"(-0.3s)  r 23.12,23.31
   Both bullseye (<0.3s) on the tightly-constrained cross-track axis; small along-track residuals share sign
   -> consistent with a single ~1" orbit correction.
   Intra-night motion NOT measurable: each night's two detections are only 2-3 min apart (pred ~1.2"/hr ->
   ~0.05-0.1" motion, below centroid precision). Same-night motion neither confirms nor rejects; the chain
   rests on the two-epoch positional coincidence.
   Image-level cross-match (independent corroboration): NSC meas exposure IDs match SSOIS DECam footprint
   filenames EXACTLY -- 2013: tu2088892, tu2092162 (in SSOIS list, r, 150s, depth95 23.74-23.81);
   2015: c4d_150715_012457_ooi_r_ls9, c4d_150715_012616_ooi_r_ls9 (SSOIS c4d_150715_*_ooi_r_ls9). Two
   independent pipelines (SSOIS ephemeris footprint vs NSC catalog) agree on both image and position.

3. Stationary-source rejection — PASS. Within 3" of each candidate the only NSC mean object is the candidate
   itself (deltamjd~0, single-night). No static source underneath -> not a star.

4. Magnitude sanity — PASS (note). Pred V~22.4-22.6; measured r~23.06-23.32 (mean ~23.2). Dr~+0.6 fainter
   than V; for a red TNO (V-r~0.5-0.6) intrinsic r~22.0 expected, so ~1.2 mag fainter in r than a naive
   red-TNO prediction -- within +-1.5 window but on the faint side (bluer/fainter object or near-limit bias).

5. Negative control (+1deg Dec offset) — PASS.
     2013-03-11: TRUE box on-night-single-in-ellipse = 1 (candidate); +1deg OFFSET = 0
     2015-07-15: TRUE = 1 (candidate); +1deg OFFSET = 0
   True track cleaner than offset background on both nights.

6. Chance-coincidence: density of single-night faint (r in [22.5,23.7]) NSC sources in a 300" field ->
   expected number in the 3-sigma ellipse = 0.0155 (2013), 0.052 (2015). Joint (independent) ~ 8e-4, before
   crediting that both fell at ~0.2-0.3 sigma (bullseye), which lowers it further.

Full epoch log: search_log.csv (24 DECam nights + 2 neg-control rows), honest nulls included. Two other
flagged rows REJECTED: 2014-06-29 (single ndet=1, no same-night companion) and 2017-01-28 (r=99.99 invalid
photometry). All 2015-05 run nights, all 2017-2023 nights: clean NULL.

## THE ONE HONEST TENSION (why candidate, not confirmation)
The 2015-05-20..24 DECam run (19 VR exposures over 5 nights, depth95 ~ 23.0-23.5) covered the predicted
positions and detected NOTHING. For an object at V~22.4 (VR brighter still) this is a genuine non-detection
where a detection was plausible. Mitigations: (a) these pointings are ~50' from the detection fields
(different sky; possible chip-gap/edge or depth variation at the exact predicted pixel); (b) depth95 is 95%
completeness -- a red object at r~23.2 in a broad VR filter sits near the limit; (c) the 2015-07-15
r-detection is itself below depth95 (2 of 6 r-frames), i.e. genuinely marginal. Only the 2013-03-11
detection (0.5 mag above a 23.8 limit) is photometrically robust. A skeptic should read the pair as "one
solid + one marginal detection on the orbit, plus a non-detection run needing explanation" -> report for
review, do not submit.

## USER NEXT STEPS (not done here — no accounts / no submission)
1. Pull DECam cutouts (SSOIS Datalink / NOIRLab cutout) for tu2088892, tu2092162,
   c4d_150715_012457/012616_ooi_r_ls9; eyeball source at predicted pixel; confirm PSF-like, un-blended,
   and absent from a deep stack (i.e. it moved).
2. Feed the two positions (astrometry_for_review.csv) into an orbit fit WITH the 2001-2008 discovery arc
   (Find_Orb/OpenOrb). Real recovery drops chi2 sanely and shrinks along-track uncertainty; a coincidence
   pair will not co-fit at sub-arcsec residuals.
3. Only if both survive: prepare ADES via the DECam/NSC survey obs code, measurer attributed. NOT before.

## ASTROMETRY (measured, for USER review — see astrometry_for_review.csv)
4 detections (2 epochs x 2 frames). NSC DR2 meas RA/Dec (Gaia-DR2-referenced; per-detection est. sigma
~0.1-0.2" at this SNR). Times are exact frame MJD -> UTC.
  id            utc                    ra_deg        dec_deg       r     +-    exposure
  133189_17045  2013-03-11T06:22:11.8  228.8012394  -20.8267605  23.32  0.12  tu2088892
  133189_17045  2013-03-11T06:25:11.0  228.8012123  -20.8267731  23.06  0.14  tu2092162
  133703_14601  2015-07-15T01:23:18.3  229.7975286  -21.0925339  23.12  0.21  c4d_150715_012457_ooi_r_ls9
  133703_14601  2015-07-15T01:24:35.5  229.7974849  -21.0925470  23.31  0.20  c4d_150715_012616_ooi_r_ls9

## Artifacts
horizons_ephem.csv; full_epoch_scan.json; search_log.csv; nsc_movers.json;
meas_133189_17045.json; meas_133703_14601.json; precise_resid.json; astrometry_for_review.csv; REPORT.md
