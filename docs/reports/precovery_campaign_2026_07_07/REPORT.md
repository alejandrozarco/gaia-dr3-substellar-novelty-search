# Recipe-v2 Gated Precovery Campaign — Target List

Date: 2026-07-07 | Work dir: /tmp/precovery_recut/
Built on the validated GATE-R1 stack (Horizons ellipse quantities 36/37 -> CADC SSOIS ssosclf.pl
byname -> deep-survey footprint count). Zero accounts. Measurement/reporting only.

## HEADLINE
Started from 7,353 MPC distant_extended objects. Two prioritized lanes -> 144-object SMIA pre-gate
budget -> **103 gate-passers**, ALL with >=3 deep-survey footprints. Ranked by
searchability x value. Materially smaller, genuinely searchable list. Quality over quantity.

## POOL CONSTRUCTION (two lanes)
Parsed distant_extended.dat (7,353 objs; 2,524 single-opp, 4,829 multi-opp).
Lane split by orbit: INNER-SYSTEM = a<30 AU or q<13 AU (Centaur/SPO, Chariklo regime); DISTANT = rest.
Faintness proxy vidx = H + 10*log10(a) used to pre-rank (H-bright != archive-reachable, the pilot
lesson); kept vidx<23.3.
  Candidate cuts (vidx<23.3): DISTANT multi-opp stale(last<=2018)=106; DISTANT single-opp arc>=60d=90;
  INNER single-opp arc 5-90d=22; INNER multi-opp stale=30.
  Gate budget selection (144): 55 distant-multi + 45 distant-single + 22 inner-single + 22 inner-multi.

## SMIA PRE-GATE (144 gated, one batched Horizons call/object, 4 archive epochs)
Epochs 2005-07-01 / 2013-01-01 / 2017-07-01 / 2021-01-01. PASS iff >=1 epoch has
SMIA_3sigma<10' AND SMAA_3sigma<60' AND V<23.3. 0 errors, 0 red flags (all returned ellipse cols).

  PASSED: 103/144.
  By lane/type (passed / gated):
    distant multi-opp:  43 / 55
    distant single-opp: 34 / 45
    inner  multi-opp:   22 / 22
    inner  single-opp:  4 / 22   <-- GUTTED

  HONEST LANE ACCOUNTING: the INNER single-opp lane is where the gate bites hardest — only
  4/22 survive. Short arcs (mostly 5-40 d,
  many just-discovered 2025-26 objects) have huge per-day leverage but the along-track (SMAA) and
  cross-track (SMIA) both blow past the box at 8-20 yr archive baselines. This is the pilot's
  Chariklo-control caveat inverted: leverage helps ONLY when the arc already pins the orbit.
  Failure-reason tally over 41 fails (best epoch): SMAA-blown=20, V-too-faint=22,
  SMIA-blown=8. The distant single-opp fails are almost all 2025-vintage objects whose
  archive-epoch positions are pre-discovery extrapolations (correctly rejected).

## PASSER QUALITY (searchability)
  best-SMIA min/median/max = 0.06 / 0.80 / 546.81 arcsec.
  Pinpoint (best SMIA<10"): 79/103.  Tight (<60"): 100/103.
  Passing at >=2 archive epochs (robust): 90/103.

## COVERAGE (CADC SSOIS byname, deep surveys)
All 103 passers queried; ALL have >=3 deep-survey footprints (DECam/PS1/CFHT-MegaCam/HSC/VLT/
VISTA/Subaru/ZTF). CAVEAT: SSOIS byname uses the FULL-orbit uncertainty, so footprint counts are a
broad UPPER BOUND on candidate frames (the large along-track SMAA sweeps many fields), NOT confirmed
on-chip detections. The small SMIA is what makes per-frame attribution tractable; deep_fp indicates
that indexed deep imagery exists to search, not that the object is in it. Confirmation (>=2 same-night
coherent detections, blend rejection) is the per-target campaign step, unchanged from GATE-R1.

## RANKING
score = searchability x value.
  searchability = 0.40*f(SMIA) + 0.25*f(V) + 0.20*f(deep_fp) + 0.15*f(n_pass_epochs)
  value: single-opp = 0.85 flat (a precovery MULTI-OPP-IFIES a 1-opposition orbit — highest structural gain);
         multi-opp = 0.6*type + 0.4*staleness (older last-obs = closer to lost = more valuable to re-anchor).

Lane mix of the 103: distant-multiopp=43, distant-longarc(single>=60d)=34, inner-system=26.

## TOP 12
 1. 2004 YH32    (144908)     [inner-system] score=0.671
     best epoch 2005-07-01: V=19.7, SMIA=0.19" (SMAA=0"), passes 1/4 epochs
     deep footprints=995 (DECam 554, PS1 123, CFHT 12, HSC 1, VLT/VISTA/Subaru 224); 3-opp, last obs 2007
 2. 2017 FP50                 [inner-system] score=0.610
     best epoch 2017-07-01: V=21.8, SMIA=2.04" (SMAA=12"), passes 2/4 epochs
     deep footprints=452 (DECam 219, PS1 159, CFHT 5, HSC 9, VLT/VISTA/Subaru 64); single-opp 75d arc
 3. 2001 QT322   (135182)     [distant-multiopp] score=0.598
     best epoch 2005-07-01: V=22.0, SMIA=0.52" (SMAA=1"), passes 4/4 epochs
     deep footprints=891 (DECam 200, PS1 174, CFHT 53, HSC 19, VLT/VISTA/Subaru 55); 6-opp, last obs 2008
 4. 2001 KK76                 [distant-multiopp] score=0.594
     best epoch 2005-07-01: V=22.6, SMIA=1.14" (SMAA=2"), passes 4/4 epochs
     deep footprints=1283 (DECam 142, PS1 104, CFHT 123, HSC 0, VLT/VISTA/Subaru 492); 4-opp, last obs 2004
 5. 2025 LU2                  [distant-longarc] score=0.587
     best epoch 2021-01-01: V=22.5, SMIA=5.43" (SMAA=329"), passes 4/4 epochs
     deep footprints=584 (DECam 230, PS1 168, CFHT 3, HSC 38, VLT/VISTA/Subaru 64); single-opp 109d arc
 6. 2006 JG57                 [inner-system] score=0.584
     best epoch 2005-07-01: V=20.1, SMIA=0.94" (SMAA=1"), passes 1/4 epochs
     deep footprints=2212 (DECam 1481, PS1 0, CFHT 31, HSC 0, VLT/VISTA/Subaru 535); 3-opp, last obs 2007
 7. 2009 HW77                 [inner-system] score=0.575
     best epoch 2013-01-01: V=21.6, SMIA=0.25" (SMAA=1"), passes 4/4 epochs
     deep footprints=845 (DECam 403, PS1 113, CFHT 37, HSC 0, VLT/VISTA/Subaru 257); 7-opp, last obs 2012
 8. 2025 NB192                [distant-longarc] score=0.574
     best epoch 2021-01-01: V=22.9, SMIA=4.78" (SMAA=97"), passes 4/4 epochs
     deep footprints=559 (DECam 181, PS1 139, CFHT 26, HSC 0, VLT/VISTA/Subaru 0); single-opp 143d arc
 9. 2001 KN76                 [distant-multiopp] score=0.571
     best epoch 2005-07-01: V=22.6, SMIA=0.53" (SMAA=1"), passes 4/4 epochs
     deep footprints=830 (DECam 366, PS1 123, CFHT 179, HSC 1, VLT/VISTA/Subaru 84); 8-opp, last obs 2008
10. 2025 NO193                [distant-longarc] score=0.570
     best epoch 2021-01-01: V=22.7, SMIA=6.14" (SMAA=127"), passes 4/4 epochs
     deep footprints=611 (DECam 133, PS1 141, CFHT 18, HSC 57, VLT/VISTA/Subaru 117); single-opp 137d arc
11. 2001 KJ76                 [distant-multiopp] score=0.568
     best epoch 2005-07-01: V=22.9, SMIA=1.16" (SMAA=2"), passes 4/4 epochs
     deep footprints=1195 (DECam 225, PS1 130, CFHT 233, HSC 14, VLT/VISTA/Subaru 560); 4-opp, last obs 2005
12. 2025 LW3                  [distant-longarc] score=0.566
     best epoch 2021-01-01: V=23.0, SMIA=5.21" (SMAA=217"), passes 4/4 epochs
     deep footprints=517 (DECam 105, PS1 173, CFHT 16, HSC 29, VLT/VISTA/Subaru 107); single-opp 109d arc

## ARTIFACTS
- campaign_targets.csv  — all 103 passers, ranked, with SMIA/SMAA/V/footprint columns
- smia_gate_log.csv     — per-object per-epoch gate decisions (144 objs x 4 epochs)
- coverage_log.csv      — per-passer deep-survey footprint breakdown
- gate_pool.json / gate_results.json / coverage_results.json / scored.json — intermediate state
- ssois/*.tsv           — raw SSOIS byname results per passer

## NEXT ACTION (per target, unchanged from GATE-R1 GO recipe)
For a chosen target: re-pull SSOIS at the passing epoch with tight eellipse; for frames whose center
falls within the SMIA box, pull Datalink cutout / cross-match NSC DR2 or PS1 DR2 detections; require
>=2 same-night coherent detections; reject <10" blends and single-epoch excursions; measure ADES PSV;
submit via survey SARC (measurer named). Verify WAMO. Submission is the user's action.
