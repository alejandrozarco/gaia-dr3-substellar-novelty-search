# PIXEL-VERIFY + ORBIT-REFIT — 2001 KN76 (=(160147)) marginal precovery chain
Date: 2026-07-07 | /tmp/precovery_verify/2001_KN76/ | zero accounts, no submission.

## VERDICT: WEAKENED  (pixels PASS, refit INCONCLUSIVE)
Both epochs are REAL sources at the predicted positions — pixel test actively REJECTED the two
chain-killing hypotheses (2015 cosmic-ray/artifact; stationary background contaminant). Joint
orbit refit neither rejects (all 4 pts retained, sub-arcsec) nor cleanly confirms (new-pt
residuals 0.9-1.0" = worst in fit, ~3sigma at realistic errors; a shifts ~11sigma; orbit-wide
constraint barely improves). Strengthened CANDIDATE, not a confirmation.

## PART A — PIXELS (12 DECam InstCal frames, NOIRLab retrieve; WCS->CCD; photutils; LS-DR10 coadds)
2013-03-11 pair (133189_17045), CCD S10, two 150s r exposures:
  tu2088892: aper SNR 8.5, remeas FWHM 1.05" (seeing 1.13"), recentroid 0.154" from catalog
  tu2092162: aper SNR 9.0, remeas FWHM 1.27" (seeing 1.24"), recentroid 0.090"
  Two independent SNR~9 PSF sources at predicted pixel; deep LS-DR10 coadd BLANK in r,i,z
  (SNR -0.3/-0.9/-0.6) -> real MOVER, not stationary. STRONG.
2015-07-15 pair (133703_14601), CCD S1, two 50s r exposures (EXTRA scrutiny on 012616 fwhm_cat 0.77"):
  1) Artifact hyp REJECTED: 012616 remeasures to FWHM 1.15" = frame seeing 1.23", NOT sub-PSF.
     Catalog 0.77" was a SExtractor quirk on a marginal source; both frames PSF-width.
  2) Both-frames test marginal PASS: 012457 DAO-detected (recentroid 0.019"); 012616 forced
     aper SNR ~3.5 at same posn; catalog posns agree 0.15". Each frame only 2.6-4.6 sigma.
  3) Persistence: flux present in ALL 4 consecutive r-frames incl. the 2 NSC didn't catalog
     (012341/012457/012616/012733 aper SNR 4.6/2.6/3.5/4.1) -> real, not a one-frame blip.
  4) Stationary hyp REJECTED (decisive): i-band(2017) & z-band(2019) LS-DR10 coadds (NO
     2015-07-15 data) are BLANK (SNR -0.2/-2.2). A stationary r=23.5 object would be solid in
     deep i/z. Absence proves the r/g coadd signal is KN76's own 2015 flux, not a background src.
  Net: real, non-stationary, PSF-like but genuinely MARGINAL (~5sigma combined) detection.

## PART B — JOINT REFIT (find_orb console fo built from source; MPC 2001-2008 arc + 4 new W84 obs)
  arc-only 2001-2008: a=43.9309+/-0.0096, e=0.0931, mean resid 0.38", perih sigma 17.2d, U 4.1 (39/40)
  joint    2001-2015: a=43.8366+/-0.0086, e=0.0904, mean resid 0.48", perih sigma 13.1d, U 4.0 (43/44)
  - All 4 new points RETAINED. Joint residuals 2013 0.99/1.00", 2015 0.74/0.89" (RMS 0.91");
    worst in fit; ~1-1.8sigma at fo 0.5" default, ~3sigma at realistic 0.3"; coherent ~-0.7" Dec.
  - Along-track uncertainty SHRINKS ~4x (MC covariance propagation, 3000 draws):
    2013 0.90"->0.23"; 2015 1.54"->0.39"; cross-track unchanged (0.14/0.19"). Criterion met.
  - BUT orbit-wide barely improves: U 4.1->4.0, perih sigma 17->13d despite 2x baseline; a shifts
    0.094 AU = ~11sigma (either fit), perih time moves ~340d. Not a clean-recovery collapse.
  - Consistency w/ arc prediction: all 4 pts within <0.35sigma of arc 3-sigma ellipse
    (2013 along+0.65"/cross+0.2"; 2015 along+1.05"/cross-0.2").
  Part B = INCONCLUSIVE: retains pts + tightens along-track 4x (favorable), but no
  residuals-at-precision / orbit-wide collapse; exposes 11sigma a-shift.

## SYNTHESIS
Pixel test (load-bearing) FAVORABLE: 2015 not an artifact, not stationary; 2013 unambiguous mover.
Chain not spurious in either possible way. Refit keeps it alive but cannot certify (2015 ~5sigma
marginal; residuals/a-shift short of clean recovery). => WEAKENED.

## TO CLINCH (user; no submission)
1) THIRD epoch on the joint orbit (2013-2015 along-track now pinned ~0.4"): re-search 2016-2019
   DECam/HSC at refit ephemeris. 2) Refit with realistic 0.3" sigmas + full covariance weighting;
   escalate only if 4 pts survive <2sigma with sigma_a collapsing. 3) Only then prepare ADES.

## ARTIFACTS (/tmp/precovery_verify/2001_KN76/)
updated_astrometry.csv; analyze.py analyze2.py stationary_test.py mc_uncert.py make_obs.py;
new4.obs joint.obs arc.obs; fit_arc/ fit_joint/ (elements.txt covar.json total.json);
stamp_*.png ls_coadd_2013.png ls_coadd_2015.png; frames/ frames0515/ ls/.
