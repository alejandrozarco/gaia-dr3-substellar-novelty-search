# Precovery Attempt — 2001 KJ76 (distant multi-opp TNO)

Date: 2026-07-07 | Work dir: /tmp/precovery_wave2/2001_KJ76/
Analyst: automated recovery run (Alexander Keur campaign). NO submission made — measurement + reporting only.

## OUTCOME: NULL_SEARCHED (clean, well-tested non-detection)

2001 KJ76 was searched at its SMIA-gate-passing windows across every epoch with real archival
coverage: the tightest/most-reliable epoch (2006-04-23 CFHT/MegaCam deep imaging, ~1 yr after the
last observation, 3-sigma ellipse SMIA 1.5" x SMAA 2.7") and all 14 DECam nights indexed by SSOIS
across 2013-2023 (NSC DR2 catalog). No credible detection emerged. The CFHT epoch is a deep
non-detection to i~23.0 (5-sigma), ~1.2 mag below the object's predicted brightness, confirmed by
forced photometry, an object-frame coadd, and a +/-40" digital-tracking scan along the ephemeris
uncertainty direction. The NSC search produced 3 single-night flags, all rejected on physical grounds
and consistent with the background contamination rate (negative control). No fake chain manufactured.

## TARGET & ARC
- 2001 KJ76: H=6.52, a=43.48 AU, distant multi-opp. 27 MPC observations, 4 oppositions
  (2001, 2002, 2003, 2005), last obs 2005-06-07 (Spacewatch 304). Obs codes 304/568/695/807.
- Gate best epoch 2005-07-01: V=22.88, SMIA_3s=1.16", SMAA_3s=1.51". Passes 4/4 grid epochs.
  SSOIS byname: 1668 footprints (CFHT 224, DECam 225, VISTA 513, PS1 130, Subaru 47, WISE 183, ...).
- Ephemeris independently re-derived (astroquery JPL Horizons, per-site obs codes; every multi-epoch
  call row-matched by datetime_jd). Reproduces the gate SMIA/SMAA/V exactly (2005-07-01 1.16"/1.51";
  2013-01-01 4.39"/25.67"). SSOIS predicted positions agree with my Horizons positions to ~0.3".

## THE KEY STRUCTURAL FACT
The tight 2005-07-01 gate ellipse sits just ~24 days after the last observation, so it is essentially
in-arc — but there is zero archival coverage in 2005 (earliest SSOIS-indexed image is 2006-04). The
tight epoch predates all deep imagery. Real searchable coverage begins 2006, where the propagated
uncertainty is still small (2006: SMIA 1.5"/SMAA 2.7"; 2007: 2.0"/4.7") and balloons at the later
gate windows (2013: 4.4"/26"; 2017: 6.7"/57"; 2021: 7.9"/85"). Unlike wave-1 analog 2001 KN76
(DECam-only, all 2013+), KJ76 has heavy 2006-2007 CFHT/MegaCam + a deep 2007 Subaru run at a
genuinely tight box — so the highest-value channel here is 2006 CFHT pixel imaging, not the ballooned
NSC catalog era.

## CHANNEL 1 (primary): 2006-04-23 CFHT/MegaCam deep imaging — tightest, most reliable epoch
16 deep 400s exposures (8x I.MP9701, 8x R.MP9601) over a 2.1 h run; object predicted to move ~4.6"
(mostly westward) across the night at ~2.3"/hr, all within CCD ccd08. 3-sigma ellipse 1.54" x 2.68".

Pipeline (standing rule 4): CADC SODA whole-extension cutouts (pixel-range SODA cuts return
header-only on this deployment; whole-CCD SUB=[9] works). WCS re-anchored locally against Gaia DR3 —
required: the Elixir header carries a full-focal-plane TAN solution (CRPIX ~9500 px outside the
extracted CCD), giving position-dependent errors of ~13" that no global shift fixes; a local
Gaia-star grid-search + median-offset anchor near the object registers each frame to rms 0.1-0.5 px
(0.02-0.09").

Tests, all negative:
- Forced aperture photometry at the corrected predicted pixel in each of the 16 frames: no consistent
  source (SNR scatters -9 to +7 = background fluctuation, not a repeating source). The one strong
  nearby detection (SNR 10.4, r~23.3) is 4.78" away (outside the ellipse), a field source, and does
  not track the predicted motion.
- Object-frame sigma-clipped coadd (registers each frame on the moving predicted pixel, concentrating
  a real object to a point over 3200 s): predicted position net negative, SNR -1.7 (I) / -6.1 (R);
  40 blank-sky apertures max 1.6-sigma. No point source.
- Depth / sensitivity proof (star-registered coadd): Gaia control stars g=18.0->SNR 185,
  g~20.3-20.6 -> SNR 17-26; 5-sigma limiting mag i~23.0, r~22.8. Detects sources 1+ mag fainter than
  the object's predicted brightness.
- Digital-tracking scan (coadd at the predicted rate over along-track offsets -40..+40"): no source
  above 3-sigma anywhere (max SNR 3.0 at -30", i.e. noise; predicted position SNR -1.7). Doubles as
  the negative control — every offset is as blank as the true position; a real object would spike at 0.

Interpretation: predicted V=22.83 -> i~21.8 for a red TNO -> a real object would be an obvious
SNR ~15-20 single-frame detection and a very high-SNR coadd point. It is absent to i~23. Clean
non-detection at the epoch where both the ephemeris (1 yr post-arc, 4-opp) and imaging depth are
strongest. The 2006-04-24/25 CFHT nights (same apparition, ephemeris essentially identical) are
redundant with this result and were not separately reduced.

## CHANNEL 2: NSC DR2 catalog search — 14 DECam nights, 2013-2023
Per-night Horizons ellipse (obs 807); NSC DR2 object-cone (radius 1.35xSMAA, >=15"); single-night
sources (deltamjd<3 on the night) tested against the 3-sigma ellipse. Reuses the validated wave-1
(KN76) stack. All 14 nights: 0 credible in-ellipse sources. Three flags, all rejected:
- 2017-04-28 id 142966_190802, r=21.48, cross +2.4"/along -23.9": a single measurement in 1 of the
  night's 8 exposures, single r-band, not re-detected on the deep griz nights 2017-04-29/04-30/05-04
  bracketing it, and 1.35 mag brighter than predicted. Spurious / main-belt asteroid. Negative
  control: TRUE in-ellipse=1 vs +1deg-Dec offset=0 and +0.7RA/-0.5Dec offset=0 — a lone Poisson count
  in a 57"-long ellipse, not an excess.
- 2019-05-02 id 143994_110160 (r=19.28, class_star 0.91 = star, 3.5 mag too bright) and id
  143994_87070 (g=16.8, class_star 0.0003 = galaxy, 6 mag too bright). Rejected on magnitude +
  morphology. Negative control: TRUE=2 vs offset 1-2 = background density, no excess.

## CHANNELS NOT PURSUED (and why)
- Pan-STARRS1 (39 nights 2009-2014): object at V~22.8 below PS1 single-epoch depth (~21.5); no useful
  single-epoch constraint.
- 2007-03 CFHT + 2007-06-20 Subaru/SuprimeCam (deep, tight box, different apparition): would only add
  value to probe a >3-sigma ephemeris systematic. The 2006 tight-ellipse non-detection plus the
  +/-40" along-track digital-tracking scan already cover the plausible systematic range for a 4-opp
  orbit. Natural next step for a second independent apparition (both SSOIS-indexed; Subaru via SMOKA).
- 2018/2022 CFHT, VISTA, later DECam: along-track uncertainty >50-100"; low attribution power.

## CHAIN DISCIPLINE ACCOUNTING
1. Searched only the gate-passing windows (2005 = no coverage; 2006 near-arc; 2013/2017/2021 via
   DECam). Epoch-fragile discipline respected.
2. Motion consistency: no >=2 same-night coherent detections and no multi-epoch source to co-fit —
   nothing to test; correctly NULL.
3. Stationary-source rejection: n/a (no candidate).
4. Magnitude sanity: the only non-trivial flag (2017-04-28) was 1.35 mag bright and single-exposure.
5. Negative control: performed and clean — CFHT along-track offset scan (all offsets blank); NSC
   +1deg-Dec and RA/Dec offset boxes (flag counts = background).
6. Every epoch logged in search_log.csv with honest outcome.

## OUTCOME BUCKET: NULL_SEARCHED
15 epochs/nights searched with real coverage (1 deep CFHT night + 14 DECam nights); 1 gate window
(2005) has NO_ARCHIVAL_COVERAGE. No credible precovery. A genuine, deep, well-controlled null — the
object is absent from its predicted position at the tightest reliable epoch down to ~1.2 mag below
prediction. NO submission (there is nothing to submit).

## ARTIFACTS
- mpc_obs_raw.json           — 27-line MPC observation record (arc 2001-2005)
- ssois_byname.tsv           — 1668 SSOIS footprints
- horizons_scan.json / decam_ephem.json — re-derived ephemerides + 3-sigma ellipses (gate-validated)
- frames_20060423.json       — 16 CFHT deep frames + per-frame predicted positions
- ccds/*.fits                — 16 CFHT ccd08 cutouts (CADC SODA)
- gaia_refs.csv              — Gaia DR3 astrometric anchor stars
- cfht_measure_20060423.json — per-frame forced/local photometry
- coadd_I.npy / coadd_R.npy   — object-frame coadds
- cfht_track.py               — along-track digital-tracking scan (negative control)
- decam_nsc_candidates.json   — 3 NSC flags (all rejected)
- search_log.csv              — 16-row epoch log, honest outcomes
