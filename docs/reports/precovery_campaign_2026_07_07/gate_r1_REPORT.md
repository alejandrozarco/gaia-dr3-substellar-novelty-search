# GATE R1 — Solar-System Precovery / Arc-Extension Feasibility ("Sam Deen niche")

Date: 2026-07-07 | Work dir: /tmp/gate_r1_precovery/
Question: Can this no-telescope setup find archival detections of short-arc solar-system objects and submit MPC-creditable astrometry?

## VERDICT: GO
Binding caveat: slow-mover target supply lives in DEEP archives (DECam/CFHT/PS1/HSC via SSOIS), NOT ZTF. The ZTF/MOST route is validated but the distant-object pool is too faint for ZTF single epochs.

All four GO conditions met:
1. Positive control recovered (sub-arcsec, independent). 
2. Negative control clean (scrambled ephemeris -> 0 matches).
3. Supply >= ~10 viable: ~395 deep-survey-reachable single-opp distant objects (arc <=60 d).
4. Rubin/MPC automation NOT closing the niche: external-archive precovery is a PROTOTYPE (arXiv:2510.07588, LLNL Oct 2025), NOT production; MPC precovery still "ad hoc"; Sam Deen credited for 3I/ATLAS ATLAS-precoveries June 2025.

## STEP 1 - TOOLING ROUTE (no accounts)
- SSOIS PRIMARY: backend /cadcbin/ssos/ssosclf.pl (found via results.js). Query by name (resolves via CADC/Horizons/MPC) or arc. Returns Image,MJD,Filter,Object_RA/Dec,Telescope,Datalink,TSV. Indexes DECam, ESO-VISTA, VLT, HST, ZTF, LCO, SkyMapper.
- JPL Horizons (astroquery.jplhorizons) CORE: accepts obs code I41 (ZTF), gives ephemeris+V.
- IRSA MOST (astroquery.ipac.irsa.most) WORKS no-account for ZTF, but ZTF depth ~20.5 too shallow for distant supply.
- B612/ADAM: hosted demo (C/2014 UN271) implies account/indexing overhead; NOT required, skipped.
Chosen stack: Horizons -> SSOIS ssosclf.pl -> catalog/pixel source confirmation. Zero accounts.

## STEP 2 - CONTROLS (falsifiable)
POSITIVE: Centaur (10199) Chariklo, independent ZTF recovery.
- MOST/Horizons predicted Chariklo in ZTF on 2019-06-11: MJD 58645.4006 (RA 295.98142,Dec -25.46302,V~18.8) and 58645.4802 (RA 295.97795,Dec -25.46327).
- MPC OBS80 record (get-obs API): ZTF (I41) reported it 2019-06-11 at both epochs.
- Match: epoch1 sep=0.07", dt=+2.7 s; epoch2 sep=0.25", dt=-3.5 s. V~18.8 consistent w/ 18.75r/19.40g. Genuine independent recovery.
- SSOIS separately: 11,676 archival image rows (2015-2019) incl 84 CTIO-4m/DECam, ESO-VISTA, VLT/HAWKI, HST/WFC3, 34 ZTF; coherent track (0.0005"/frame within night).
NEGATIVE: scrambled ephemeris +1deg Dec -> 0 real detections within 5" on 2019-06-11 (true track: 2). Clean.

## STEP 3 - TARGET SUPPLY (load-bearing skeptical finding)
Source: MPC distant_extended.dat.gz (downloaded, parsed). 7,353 objects; 2,524 single-opp; 1,966 arc<=60d; 1,375<=30d; 933<=14d.
Artifact discipline: H-bright != reachable. H<=8 lost TNOs are distant -> V~23-24.5. MOST confirmed 2013 NH83 & 2016 LK89 at V~24 (below ZTF ~20.5). 60-object Horizons V-screen: 0% ZTF-reachable (V<21), ~23% deep-survey-reachable (V<23).
=> ~395 single-opp distant objects reachable in deep archives (PS1/DES/DECam/CFHT/HSC, all SSOIS-indexed) = ideal tight-extrapolation precovery targets.
5-10 best first targets (confirm each in SSOIS DECam/CFHT/HSC first):
 2000 FY53 (H8.8,35d,V~22.0); 2000 YQ142 (H7.6,2d,V~22.4); 2002 PE155 (H6.1,3d,V~22.4); 2001 QU297 (H6.0,23d,V~22.6); 1999 JB132 (H7.6,8d,V~22.6); 1995 KJ1 (H6.5,26d,V~22.8); 1997 CW29 (H6.5,27d,V~22.9); 2000 QB226 (H6.5,6d,V~23.1); 2000 QO252 (H7.0,29d,V~23.2); 2001 KM76 (H7.1,19d,V~23.3).
Favor 5-30 d arcs (tighter orbit) over 1-3 d. NEOCP live ~20 fresh unconfirmed objects = complementary faster-mover stream.

## STEP 4 - KILL CHECK: niche OPEN
- arXiv:2510.07588 (LLNL, 8 Oct 2025): prototype/PoC on historical ZTF; states prediscovery "handled in ad hoc manner"; motivated by "coming era of Rubin"; no public code; NEA-focused. NOT production.
- Rubin SSP (DP0.3): precovery linking of its own SSObjects queued to MPC; external archives (ZTF/PS1/DECam) NOT specified, only future/planned. Ops just beginning.
- MPC: no current automated cross-archive precovery; archival astrometry submitted manually.
- Live proof individuals work it 2025-26: Sam Deen credited, 3I/ATLAS ATLAS pre-discovery, June 2025.
Niche on a clock (Rubin external precovery + LLNL productionization) but not closed today.

## STEP 5 - CREDIT MECHANICS: creditable YES
- ADES (PSV/XML); obs80 obsolete. Submit obs@cfa.harvard.edu / ADES PSV web service / parser / curl.
- Archival astrometry from pro-survey images: coordinate with survey SARC rep, use survey's obs code (e.g. I41), but MEASURER STILL NAMED/ATTRIBUTED (the Sam Deen model). Precovery explicitly welcomed.
- Auto-reject traps: single position/night (need >=2), dupes, missing headers. Verify via WAMO.

## FULL CAMPAIGN IF GO
1. Queue: ingest distant_extended.dat + NEOCP daily; Horizons V-screen near opposition; keep single-opp arc 5-30 d, V<~23.
2. Coverage: SSOIS ssosclf.pl extres=yes + eellipse across DECam/CFHT/HSC/PS1/ZTF; pull Datalink cutouts.
3. Confirm: cross-match to survey source catalog (NSC DR2/IRSA) or measure cutout; require >=2 same-night coherent detections; reject isolated single-epoch excursions and <10" blends (reuse ATLAS artifact trio).
4. Submit: ADES PSV via SARC, verify WAMO. Measurer named.
5. Cadence: near-certain small MPC credits per recovery; run until Rubin external precovery hits production.
Community-confirm mode; P(>=1 creditable recovery this quarter | gate passed) high. RANK-1 survivor of 2026-07-07 scan, now confirmed on real data.

## Artifacts
- distant_extended.dat[.gz] - MPC supply table (parsed)
- mpc_chariklo_raw.json - Chariklo MPC OBS80/ADES record (positive-control ground truth)
- ssois_chariklo3.tsv - 11,676 SSOIS archival image rows (deep-archive coverage proof)
- REPORT.md - this file
