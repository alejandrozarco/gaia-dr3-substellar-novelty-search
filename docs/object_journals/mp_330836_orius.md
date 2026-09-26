# (330836) Orius = 2009 HW77 — object journal

**Class:** Centaur (JPL CEN; T_J=3.746) — a=21.36 AU, e=0.418, i=17.88°, q=12.42 AU, Q=30.30 AU,
P≈98.7 yr, perihelion 2007-01. "Diffusing" Centaur, dynamical half-life ~4.5–5 Myr, ~27% of clones
temporarily captured as Jupiter-Family Comets (Wlodarczyk+2011, 2024) — a comet-in-waiting.
**Physical:** H=9.73±0.34 (only measured quantity); D≈26–79 km (albedo-assumed, ~30–65 km nominal);
colour class, rotation, spectrum, thermal size: all unmeasured.
**Discovery:** 2009-04-25, K. Černis & I. Eglītis, Baldone Observatory (Latvia); numbered 2012-06;
named 2013-01 (mythological centaur killed by Heracles stealing Pholus's wine).

**Status:** 6 pixel-verified DECam precovery detections (2013–2015), verified; ADES draft prepared;
MPC submission not yet filed (as of 2026-07-07).

## Status timeline

| date | status | note |
|---|---|---|
| 2026-07-07 | CANDIDATE_CHAIN | wave-1 recovery attempt: 6 NSC-DR2 DECam detections, 4 epochs 2013–2015, residuals 0.03–0.41″ vs the 2002–2012 arc orbit |
| 2026-07-07 | PIXEL-CONFIRMED / SUBMISSION-READY | all 6 detections verified on InstCal frames (PSF-like, moving-object tests pass all 4 epochs); independently reproduced from raw pixels; updated_astrometry.csv authoritative |
| 2026-07-07 | DEEP-DIVE COMPLETE | literature/physical/occultation/ephemeris-impact dossier, independently verified (one photometry-epoch bug caught + corrected) |
| 2026-09-22 | FILING ON HOLD | not detected in 2019 DECam frames to i > 24.70 (5 sigma) while the catalogued H predicts V = 22.45; controls of comparable brightness detected in the same frames; identity of the 2013-2015 detections not established |

## Cross-check ledger

| date | catalog / method | result |
|---|---|---|
| 2026-07-07 | MPC record (get-obs) | arc 2002-02-12 → 2012-05-19, 84 obs, 7 oppositions, U=3; **no observations after 2012** — the 2013–2015 detections are absent from the record |
| 2026-07-07 | JPL SBDB | elements + H=9.73 (ref MPO697732); orbit class CEN; no phys_par beyond H |
| 2026-07-07 | ADS/arXiv literature sweep (independently reproduced) | **only 3 refereed papers, all Baldone/OrbFit group** (Wlodarczyk+2011 MNRAS 418,2330 dynamics; Černis+2016 discovery-data; Wlodarczyk+2024 Open Astr. 33 dynamics update). Zero independent-team follow-up; zero physical characterization |
| 2026-07-07 | Population catalogs (source tables checked) | absent from TNOs-are-Cool XI (no thermal size), MBOSS (no colours), LCDB (no rotation), Johnston diameters, all 4 DES TNO/Centaur catalogs incl. the Y6 photometry paper — a physical blank |
| 2026-07-07 | Occultation campaigns | on both Lucky Star (Hv=9.9) and RECON target lists; RECON attempted the 2018-07-06 event with 576 s / 2141 km 1σ errors; today's arc-only 3σ sky error ~14″ ≈ 230,000 km = effectively unpredictable |
| 2026-07-07 | DECam astrometry (NSC DR2, pixel-verified) | 6 detections, 4 epochs 2013-03-02 → 2015-04-27, r/VR 21.53–21.83, per-axis σ 0.12–0.25″, obscode W84; +2.9 yr (+35% relative) arc extension on the post-perihelion outbound leg |
| 2026-07-07 | Photometry vs H (corrected epochs) | consistent with catalog H at the ~1σ faint edge (H≈9.9–10.1, matching the Hv=9.9 the occultation campaigns already adopt); no defensible variability (n=6, mixed bands, geometry accounts for most spread) |
| 2026-07-07 | find_orb joint refit (85+6 obs; independently reproduced) | all 6 points retained, max residual 0.33″; U 3.0→2.5; element σ's tighten 2–2.4×; **sky-plane 1σ ephemeris uncertainty: 2026 3.69″→1.11″, 2030 4.27″→1.34″, 2040 7.33″→2.51″ (~3× per axis, ~10× in area) AND the arc-only track is recentered by ~1.9σ (6.9–14.1″)** |
| 2026-09-22 | DECam archive, 2019-05-16 (6 x 180 s i, programme CrA-F1) | **not detected at the predicted position.** Motion-aligned stack: -0.6 sigma; 5-sigma limit i > 24.70; predicted V = 22.45 (JPL, H = 9.73), i ~ 21.6-22.2. Controls in the same frames: 2016 WZ80 (V = 22.9) 5.7 sigma, 2008 GV40 (V = 20.9) 13.4 sigma. Positions: JPL 3-sigma 6.45" x 0.61"; the combined fit agrees with JPL to 0.97"; stamps cover +/-20"; six different CCDs; nearest source static to 0.02" over 17 min (a star). |
| 2026-09-22 | DECam archive coverage 2015-06 .. 2019-05 | No frames >= 60 s on the path. Frames exist 2021 (z), 2022 (i, z), 2023 (g, r, i, z); being measured in a separate project. |

## Entries

### 2026-07-07 — Recovery, pixel confirmation, deep-dive (precovery campaign wave 1)
Found via the SMIA-gated re-cut. Six NSC-DR2 catalog detections at the
Horizons-predicted positions across 4 epochs; negative controls clean; all six re-opened as FITS
cutouts: PSF-like, unblended (2013 epoch decontaminated from a static star 1″ SW), and moving —
present on detection nights, absent at those positions in every other epoch. Ephemerides were
independently re-derived (6-decimal agreement) and controls re-run from raw catalogs/pixels.

Deep-dive verdict: the object is a physical blank studied only by its discoverers' group, yet it
sits on both major stellar-occultation target lists — the one technique that could measure its size
and search for rings — and its ephemeris had degraded to unusable (14 yr extrapolation, ~1.9σ bias).
These 6 points shrink the recovery box by ~10× in area, recenter the track, and improve U from 3.0
to 2.5. Filing the ADES astrometry (user action) directly enables future Lucky Star / RECON
shadow-track predictions; Rubin/LSST (Dec −34° footprint, V~23.5 now) is the dataset that will
eventually make the orbit occultation-grade and measure first colours/rotation.

The deep-dive's photometry check initially compared against the wrong dates (epoch-substitution);
this was caught and the corrected numbers stand.

Provenance: docs/reports/precovery_campaign_2026_07_07/{verify/2009_HW77/, orius_deepdive/};
ADES draft verify/2009_HW77/ades_draft_330836_orius.psv.

### 2026-09-22 — Measurement in 2019 archival DECam frames
- **Data:** six 180-s i-band DECam frames of 2019-05-16 covering the predicted position, on six CCDs; Gaia DR3 ties (57-103 stars per frame); SkyBoT controls from the same frames.
- **Result:** no source at the predicted position. Motion-aligned stack: -0.6 sigma; 5-sigma limit i > 24.70. Predicted brightness V = 22.45 (JPL, catalogued H = 9.73), i ~ 21.6-22.2.
- **Controls (same frames):** 2016 WZ80, V = 22.9, detected at 5.7 sigma, 1.1" from its predicted position; 2008 GV40, V = 20.9, at 13.4 sigma.
- **Position checks:** JPL 3-sigma 6.45" x 0.61"; combined fit within 0.97" of the JPL ephemeris; stamps cover +/-20"; nearest source static to 0.02" over 17 minutes (a star, not in Gaia).
- **Status:** the 2013-2015 detections behind the ADES draft are r/VR 21.5-21.8. Their identity is not established by these frames; filing on hold pending measurements at 2021-2023 epochs.
- **Provenance:** a separate project (measurements, figures, code).

### 2026-09-22 — 2019 non-detection withdrawn; candidate signals, unconfirmed; records moved to sso-recovery
- **Did:** Re-derived the 2019 DECam measurement in a separate project with reference subtraction, per-pixel outlier rejection, a look-elsewhere-correct search of the 3-sigma ellipse, injection-recovery depth, Gaia DR3 zeropoints and SkyBoT controls; validated blind on catalogued asteroids in the same frames (2016 WZ80 0.26", 2008 GV40 0.00" from Horizons). Re-measured the 2013-2015 campaign frames with the same pipeline.
- **Found:** The 2026-09-22 entry above (i > 24.70, not detected, filing on hold) is withdrawn: that limit was an analytic-noise artefact (per-pixel MAD x sqrt(N) on bilinearly resampled stamps). The ellipse search reaches i ~ 23.0-23.4 and contains candidate signals at the predicted position: 2019-05-15 i ~ 22.6, 2019-05-16 i ~ 22.8 (six frames), 2019-06-07 g ~ 23.35, each 0.5-1.1" from JPL's prediction; positions fit one orbit with the 2002-2012 arc at <= 0.3". Campaign nights 2013-03-02, 2014-06-27, 2014-06-29 re-measured with signals within 0.37" of JPL (2015-04-27 not testable). All unconfirmed: internal tests only, no independent review. The earlier reason for the hold no longer applies; the filing decision remains the user's. Still open before filing: a Gaia-tie check of the 2013-2015 positions (per-frame re-measurement).
- **Provenance:** recorded in the separate project noted above (RESEARCH_LOG.md and this object's journal there are now canonical for Orius).
