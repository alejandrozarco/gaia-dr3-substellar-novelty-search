# (88268) = 2001 KK76 — HST precovery measurement: fit-validation + ADES draft
Date: 2026-07-07 | workdir /tmp/kk76_refit/ | zero telescope, NO submission (draft only).
Tooling: existing find_orb console build /tmp/precovery_verify/2001_KN76/build/find_orb/fo
(N-body, perturbers on, no JPL DE); MPC get-obs API; JPL Horizons (HST body -48).

## VERDICT: STRENGTHENED — the 4 HST points co-fit the ground arc cleanly and sharply
## improve the future ephemeris. No point rejected; no >2-sigma tension. One caveat (a/e shift).

## STEP 1 — MPC ground record (get-obs API; getobs_kk76.json / arc_kk76.obs)
- 41 observations, 2001-05-24 -> 2004-05-28 (last obs) — arc end CONFIRMED as stated.
- Codes: 304 (Las Campanas x25), 568 (Maunakea x6), 807 (CTIO x5), 950 (La Palma x3), 695 (KPNO x2).
- JPL SBDB cross-check: same 41-obs / 1100-day arc, a=42.303, e=0.01447, i=1.888 -> the cataloged
  orbit is genuinely ground-only through 2004; the 2006 HST epoch is NEW (~2-yr, first space-based).

## STEP 2 — HST -> find_orb (OBS80 satellite records, hst4.obs; ADES draft separately)
- 4 ACS/HRC CLEAR frames, 2006-05-02 08:34-08:50 UTC, obscode 250.
- obsTime = UTC (referee fix: CSV jd_tdb_mid actually holds UTC JD; verified vs obsTime_UTC).
- Per-axis sigmas 0.16"(RA)/0.10"(Dec) imposed via find_orb "#Sigmas 0.16x0.10" directive.
- HST is a spacecraft -> each obs written as an MPC satellite pair (S + s offset lines); the
  geocentric equatorial-J2000 HST position (km) at each mid-exposure UTC pulled from JPL Horizons
  (body -48, CENTER=500@399, REF_PLANE=FRAME). |r|~6960 km (consistent with 569-km HST altitude).

## STEP 3 — FITS (same fo settings both runs; N-body, perturbers on)
### (a) Ground-arc-only 2001-2004 (41 obs)   fit_arc/elements.txt
  a=42.5151+/-0.0055  e=0.014661+/-0.000492  i=1.88589+/-0.0006  node=86.9685+/-0.006
  peri=224.852+/-1.2  q=41.8918+/-0.0225  M=301.407+/-1.1  Tp=2049-07-10+/-333d
  mean residual 0.22"  U=4.6  (4 oppositions)
### (b) Joint 2001-2006 (45 obs incl. 4 HST)  fit_joint/elements.txt
  a=42.7066+/-0.0057  e=0.018766+/-0.000141  i=1.88308+/-0.00025  node=86.9931+/-0.0019
  peri=216.161+/-0.48  q=41.9052+/-0.0073  M=312.775+/-0.46  Tp=2042-12-11+/-129d
  mean residual 0.26"  U=4.2  (5 oppositions)
### HST points in the joint fit — ALL 4 RETAINED, sub-arcsec, no rejection
  frame       dRA(")   dDec(")  pull(sigma)
  J9FW91HPQ  -0.0443  +0.0595   0.66
  J9FW91HQQ  -0.0675  +0.0274   0.50
  J9FW91HRQ  +0.0691  -0.0035   0.43
  J9FW91HSQ  +0.0787  -0.0321   0.59
  RMS residual RA=0.066", Dec=0.037" (well inside 0.16"/0.10"); mean pull 0.55 sigma, max 0.66.
  Satellite parallax verified REAL: dropping the offset lines makes obscode 250 unusable
  (find_orb flags the 4 points "X"/excluded) -> the parallax is genuinely in the solution.

## STEP 4 — Covariance propagation to geocentric (500), without (arc) vs with (joint)
(fo ephemeris uncertainty; sky-plane 1-sigma = semimajor axis of the error ellipse, arcsec)
  epoch        sig_without  sig_with  shrink  pred.offset  offset/sig_without
  2026-07-01     11.2"       0.855"   13.1x    36.0"        3.22 sigma
  2030-01-01     13.7"       0.834"   16.4x    44.9"        3.28 sigma
  2040-01-01     24.0"       0.312"   76.9x    82.1"        3.42 sigma
  (ephemeris_uncertainty.csv) The HST anchor shrinks the sky-plane 1-sigma by 13-77x and moves the
  predicted position by ~3.2-3.4x the arc-only sigma — i.e. the arc-only forecast was biased at ~3
  sigma and the HST epoch corrects it. This is the Orius-style bias-detection metric.

## HONEST CAVEAT — osculating (a,e) shift beyond formal sigmas
Adding the HST epoch shifts a by +0.19 AU (~35x the arc-only formal a-sigma) and e by +0.0041
(~8 sigma). This is NOT a data conflict: the 4 HST points fit the joint orbit at 0.05", pulls
<0.7 sigma. It reflects the short-arc pathology — the 4-opposition, distant (q~42 AU, low-e) arc's
formal linear covariance UNDERESTIMATES the true (a,e) uncertainty (JPL's own arc-only a=42.30
already differs from fo's 42.52 by ~0.2 AU under different weighting/DE). The joint fit is better
conditioned (every element sigma shrinks 3-4x; U 4.6->4.2; 4->5 opps). Read the ~3 sigma ephemeris
offset and the a-shift as "the arc-only covariance was optimistic," not "the HST points discrepant."

## CONSISTENCY SUMMARY
Clean co-fit: 4/4 retained, residuals 0.04-0.08" (< the 0.16"/0.10" floor), mean pull 0.55 sigma,
no >2 sigma point, no rejection; ground-arc mean residual essentially unchanged (0.22"->0.26").
The only flag is the formal-sigma (a,e) shift, attributable to arc-only covariance optimism, not
to the HST data.

## ARTIFACTS (/tmp/kk76_refit/)
getobs_kk76.json, arc_kk76.obs/arc.obs; hst_vectors.txt (Horizons HST), make_hst_obs.py, hst4.obs,
joint.obs; fit_arc/ fit_joint/ (elements.txt, covar.json, resid.txt); eph_*.txt (6 ephemerides);
ephemeris_uncertainty.csv; resid_joint.txt / resid_geo.txt (parallax verification);
ades_draft_88268_2001kk76.psv (DRAFT — SARC-gated, user submits); sbdb_kk76.json (JPL cross-check).
