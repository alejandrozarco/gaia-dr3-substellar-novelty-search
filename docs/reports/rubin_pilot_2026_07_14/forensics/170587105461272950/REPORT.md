# Archival forensics: Rubin diaObject 170587105461272950 (= ZTF26abfwqfp)

Rank-2 pilot, stage 2 — 2026-07-14. Position (Rubin diaObject): RA 334.2496225,
Dec -18.2079475 (J2000; 22:16:59.909 -18:12:28.611). Gal. l=38.75, b=-53.43.
E(B-V)_SFD = 0.027 (IRSA dust service) — extinction negligible.

## VERDICT: INTERESTING — real, live, UNREPORTED SN-like transient; TNS AT package drafted.

## 1. The trigger
Fink/LSST flagged it hostless_candidate (ELEPHANT); 7 alert epochs over 4 nights
(MJD/TAI 61217-61235), reliability 1.0; no xm_tns at any epoch; live TNS 10" cone
negative (orchestrator, 2026-07-14; independently reproduced via TNS public CSV
search, 0 rows). Same alert-night family as SN 2026uid (Rubin diaObjectId
170587114058023168, SLSN-I z=0.936, reported to TNS by FLEET) — that one got
adopted, this one did not.

## 2. What the archival stack found

### 2a. The transient is real and two-survey confirmed
- Rubin diaSources (Fink api.lsst.fink-portal.org, live endpoint verified; the
  old api.fink-portal.org host times out): 7 epochs, SNR 13.6-82.6, reliability
  0.9987-1.0000, extendedness <= 0.40, isDipole/isNegative False, all
  pixelFlags (bad/CR/streak/saturated/edge/injected) clean. i: 22.07+/-0.04
  (61217.393) -> 20.75 (61228.398) -> 20.56 (61232.357, peak) -> 20.75 (61235.329);
  z: 22.30 -> 21.26 -> 21.30. Fink Rubin forced photometry (/api/v1/fp, 6 epochs)
  matches diaSource mags to <0.02 mag.
- ZTF public alerts (ALeRCE cone 30"): **ZTF26abfwqfp at 0.12" — the same
  transient, independently detected**. 7 detections MJD 61228.439-61232.372:
  r 20.46 -> 20.20, g 20.42, 20.39; g-r ~ 0 (blue/hot photosphere). 37
  non-detections MJD 61201-61231 (g,r,i 5-sigma limits 18.6-20.5): no precursor
  in the 2 weeks pre-discovery to ~20. ALeRCE stamp-classifier top class:
  "bogus" 0.65 (marginal 20.4-mag ZTF stamps, rb 0.35-0.74) — overruled by the
  Rubin SNR-80 detections; this plus the ELEPHANT hostless flag explains
  non-adoption on both broker sides.
- Astrometry: Rubin and ZTF positions agree to 0.12"; source stationary across
  18 days (not a mover; ssObjectId empty).

### 2b. Light curve shape
~15-day i-band rise (1.5 mag), rollover at MJD ~61232, then -0.2 mag/3 d decline.
CATS broad classifier on later epochs: class 11 = SN-like, score up to 0.993;
SNN SN-vs-others 0.72-0.83. Rise rate ~0.1 mag/d is normal-SN-like, too fast for
a typical SLSN-I unless significantly time-dilated (z >~ 0.35).

### 2c. Host association — "hostless" is a near-miss
- Legacy Survey DR10 tractor (Data Lab TAP): REX galaxy at **1.01"**
  (ra 334.249416, dec -18.207745), g=22.88, r undetected, i=22.29, z=22.62,
  W1=22.85(forced), shape_r=0.72" -> transient offset ~1.4 Re. Two more faint
  REX at 5.9" and 8.8". LS DR10 photo-z: -99 (unavailable) for all three.
  LS viewer cutouts (data vs model) confirm a marginal diffuse detection.
- Lasair Sherlock by position (lasair-ztf API): classification "SN", possible
  association with NED UV source GALEX ASC J221659.77-181227.3 at 2.38"
  (classificationReliability 3 — weak, but a UV-bright faint host is consistent
  with a star-forming dwarf).
- So: genuinely faint host (near LS DR10 limit), not genuinely hostless.

### 2d. Progenitor / precursor / counterpart searches (all negative)
- Gaia DR3: no source within 15".
- PS1 DR2 mean objects: nearest 4.99" (single-detection marginals only); nothing
  < 2". No prior variability info at position.
- CatWISE2020, unWISE: no source within 10" -> no IR counterpart, disfavors
  dusty AGN.
- VLASS QL (J/ApJS/255/30): no radio source 15". Milliquas (VII/294): none 15".
- NSC DR2 (Data Lab): zero objects within 12". Field IS covered: single DECam
  i epoch MJD 58705.209 (2019-08-10), 26 objects in 2'x2', median depth i=22.2,
  faintest 22.9 -> one archival non-detection epoch; host at i=22.3 sits at that
  limit, uninformative for variability.
- ATLAS forced photometry (queued 19:26Z, task 4542361): full 2015-2026 o/c
  history at the position — see Section 2e / atlas_fp.csv.
- DASCH: skipped by rule — object never plausibly V<15 (peak i=20.56, host g=22.9).
- ZFPS (dec -18.2 > -31, in footprint): full-survey request (JD 2458194.5-
  2461236.5) submitted and accepted 2026-07-14 under the user's registered
  account; today's queue latency ~2-5 h, results by email/queue — landing after
  this session. Purpose: deep pre-2026 stacked limits + any sub-threshold
  precursor. (First submit bounced: registered ZFPS email is the TU Delft
  address, not gmail.)

### 2e. ATLAS result
PENDING AT REPORT TIME: ATLAS FP task 4542361 (queued 2026-07-14 19:26Z at the
exact position, mjd_min=57000) was still in the per-user serial queue when this
report was finalized (status at close: None None). Retrieval command is banked in
atlas_fp.py (poll https://fallingstar-data.com/forcedphot/queue/4542361/, then
save result_url payload to atlas_fp.csv). Expected value: precursor-outburst
constraint at o/c ~ 19.5 depth 2015-2026. Note the transient peak (i=20.56) is
BELOW single-epoch ATLAS depth, so ATLAS adds history, not confirmation —
confirmation is already two-survey (Rubin + ZTF).

## 3. Classification assessment
- ARTIFACT: excluded. Two independent surveys, clean Rubin pixel flags,
  stationary, point-source, 18-day coherent evolution.
- Moving object: excluded (stationary over 18 d; no ssObjectId).
- AGN flare: strongly disfavored — 1.01" from host center (~1.4 Re, non-nuclear),
  no WISE/radio/X-ray/Milliquas counterpart, no ATLAS/ZTF/NSC variability
  2015-2026.
- CV / stellar flare: disfavored — no quiescent point source to i~23 (LS DR10) at
  the position; 15-d rise is wrong timescale.
- SN (II or Ia, z ~ 0.1-0.3): favored. g-r ~ 0 near peak, ~15 d rise, faint
  (dwarf) host. M_i ~ -16.2 (z=0.05), -17.8 (z=0.1), -19.4 (z=0.2), -20.4 (z=0.3).
- SLSN-I (the phenotype the channel was fishing for, cf. SN 2026uid): not
  excluded, but requires z >~ 0.35 (M_i < -21 and rest-frame rise stretched);
  host then M_g < -18.6. Spectroscopy decides; the object is i ~ 20.75 today
  and still spectroscopable.

## 4. Why it was unadopted (diagnosis for gate 2 of the lane)
Fink: ELEPHANT hostless flag (host below its catalog threshold) and no
xm_tns; main_label_crossmatch = "Fail". ALeRCE: stamp classifier bogus 0.65 on
marginal ZTF stamps. Human filter chains (FLEET etc.) pull from TNS, and nothing
put it on TNS. A real transient fell between two broker heuristics — exactly the
unadopted-tail failure mode this lane hypothesized.

## 5. Consumer package
consumer_package/TNS_AT_REPORT_DRAFT.md — form-ready TNS AT (PSN) report with
photometry table + remarks; consumer_package/ANNOTATION.txt — concise annotation.
Ingestion path (concrete): USER files a TNS AT report via their personal TNS
account ("Report new AT"); spectroscopic classifiers (FLEET/ePESSTO+/SCAT) consume
TNS. Secondary path (Lasair-LSST annotator) is BLOCKED today: gate test shows the
ZTF-era Lasair token gets 401 Invalid token on https://lasair.lsst.ac.uk (and
lasair-lsst.lsst.ac.uk serves a mismatched TLS cert) — user re-registration needed.
VSX/MPC/AstroNote: not applicable (see draft).

## 6. Files
- photometry_master.csv — jd+mjd-keyed combined photometry (Rubin diaSource +
  Rubin forced + ZTF det/limits + NSC epoch + ATLAS), asserts enforced.
- atlas_fp.csv / atlas_fp_raw.txt — ATLAS forced photometry full history.
- fink_diasources.csv, fink_forcedphot.csv, fink_obj.json — Rubin/Fink data.
- alerce_cone.json, alerce_ztf26_lc.json, alerce_probs.json — ZTF/ALeRCE data.
- ls_dr10_tractor.csv, ls_dr10_photoz.csv, nsc_dr2_object.csv,
  nsc_dr2_field2arcmin.csv, ps1_mean.csv, gaia_dr3_cone.csv — catalogs.
- sherlock_position.json — Lasair Sherlock position result.
- ls_dr10_zoom.jpg / ls_dr10_model.jpg / ls_dr10_cutout.jpg — host cutouts.
- lightcurve.png — combined LC figure.

## 7. Checkable URLs
- Fink LSST API: https://api.lsst.fink-portal.org (objects, /fp, conesearch)
- ALeRCE: https://api.alerce.online/alerts/v1/objects/?ra=334.24962&dec=-18.20795&radius=30
- ALeRCE LC: https://api.alerce.online/alerts/v1/objects/ZTF26abfwqfp/lightcurve
- TNS cone (public): https://www.wis-tns.org/search?&ra=334.24962&decl=-18.20795&radius=10&coords_unit=arcsec&format=csv
- SN 2026uid: https://www.wis-tns.org/search?&name=2026uid&format=csv
- LS viewer: https://www.legacysurvey.org/viewer?ra=334.24962&dec=-18.20795&layer=ls-dr10&zoom=16
- Data Lab TAP: https://datalab.noirlab.edu/tap/sync (ls_dr10.tractor, nsc_dr2.object)
- PS1: https://catalogs.mast.stsci.edu/api/v0.1/panstarrs/dr2/mean.csv
- IRSA dust: https://irsa.ipac.caltech.edu/cgi-bin/DUST/nph-dust?locstr=334.24962+-18.20795+equ+j2000
- ATLAS FP: https://fallingstar-data.com/forcedphot/ (task 4542361)
