# GATE — Blind-Novelty Lane: CANFind-style tracklet mining of NSC for NEW (undesignated) SSOs

Date: 2026-07-07 | Work dir: /tmp/novelty_gate/gate/
Question: Can a solo, no-telescope, catalog-only effort blind-mine the NOIRLab Source
Catalog (NSC) for NEW undesignated solar-system objects — especially SLOW movers
(TNOs / Centaurs / distant comets) — and get MPC designations/credit?

## VERDICT: NO-GO
Binding reason: the exact lane has already been executed end-to-end at FULL-catalog
scale by a funded team using a strictly superior algorithm. The Asteroid Institute
(B612) ran ADAM::THOR over the ENTIRETY of NSC DR2 (all 412,116 images, Oct 2012–Oct
2019, ~1.7B point sources) -> ~27,500 new asteroid candidates incl. ~150 NEAs, 100s
Jupiter Trojans, 100s Centaurs, 10s TNOs, submitted to the MPC. THOR is tracklet-LESS
and cadence-independent — it links single detections across nights by heliocentric orbit
hypothesis, dominating same-night 2-point tracklet pairing. CANFind (the catalog-tracklet
method named in the task) is superseded, and for the specific slow-mover target the
catalog is depth-walled (NSC single-visit ~23 mag vs TNO V~23–27, so new TNOs sit BELOW
catalog inclusion and require image-domain shift-and-stack — DES / DEEP / YOSO, also
already worked). The live pilot independently reproduces the combinatorial false-positive
wall. No credible undesignated-object surface remains for a solo catalog-only redo.

## 1. PRIOR ART / SCOOP (decisive)
- CANFind Paper I — Fasbender & Nidever 2021, arXiv:2109.00088 (AJ 162:244). NSC DR1,
  527,055 tracklets to ~24 mag over 29,971 sq deg = 19% of sky. Code public
  (github.com/katiefasbender/CANFind). "Paper I of a series; DR2 = future work." Mostly
  Main-Belt / Trojans / bright KBOs.
- CANFind DR2 successor — Fasbender, AAS 241 (2023), abstract 2023AAS...24113603F,
  "A comprehensive search for solar system objects in the NSC." Announces the DR2 run.
  NO Paper II and no public DR2 tracklet catalog appeared 2023–2026 — original team's DR2
  effort appears stalled/unpublished. An OPENING in name only (next bullet fills it).
- DECISIVE SCOOP — Asteroid Institute / B612 ADAM::THOR on NSC DR2. THOR (Tracklet-less
  Heliocentric Orbit Recovery; Moeyens, Juric et al. 2021, arXiv:2105.01056, AJ 162:143)
  run on all of NSC DR2 (412,116 images, Oct 2012–Oct 2019). First demo 104 asteroids (May
  2022); full run ~27,500 new candidates announced 2024 (with Google Cloud): ~150 NEAs,
  100s Trojans, 100s Centaurs, 10s TNOs, submitted to MPC. Source: b612.ai/thor-nsc,
  B612/PR-Newswire/SpaceNews/Google Cloud (2022, 2024). Exactly the blind-novelty lane, at
  100% of DR2, by a superior method, MPC-designated — including the slow-mover regime.
- Image-domain blind mining (covers the faint TNO discovery space THOR/CANFind can't):
  * DES: Bernardinelli et al. 2020/2022 — 800+ TNOs from 6-yr DES (y6 catalog, GitHub);
    C/2014 UN271 came from this archival search.
  * DEEP (DECam Ecliptic Exploration Project) — Trujillo/Bernardinelli et al., Papers I–VI
    (2023–2024). Digital tracking to VR~27; hundreds of new TNOs; Paper VI 105/110 new.
  * YOSO — arXiv:2605.06913 (7 May 2026), 18 authors. Deep-learning motion-filtered
    shift-and-stack on DEEP/DECam: 45/73 knowns + 11 new TNOs + 216 near-Solar objects.
    LSST-deployable. The DECam faint-mover space is under active, funded assault.
  * FindPOTATOs (Erasmus et al. 2024, PSJ) — open linking tool.
- prior_art.py (arXiv screen) returned only CANFind Paper I + NSC DR2 catalog papers; the
  THOR-on-NSC scoop lives in press/B612 (not arXiv) — the WebSearch-not-arXiv gap the tool
  itself warns about.

## 2. DATA REALITY
- NSC DR2 is the latest release — there is NO DR3. DR2 = 412,116 exposures (~98%
  DECam/CTIO-4m), 3.9B objects, 67.8B measurements, ~35,000 sq deg, single-visit depth ~23
  (stacks ~24), epochs Oct 2012–Oct 2019, 7 bands (ugrizY + VR).
- Astro Data Lab anonymous access WORKS at scale — verified live: anonymous UWS/TAP async
  (datalab.noirlab.edu/tap/async) accepted jobs without login and returned a 10k+ row
  orphan set in seconds (shared queue does back up — some jobs sat QUEUED minutes on
  2026-07-07). meas: measid/objectid/mjd/ra/dec/mag_auto/class_star/flags; object: ndet
  (orphans = ndet=1) + per-band mags. Sufficient for orphan + tracklet queries.
- Footprint vs competitors: DES box (~5000 sq deg) = Bernardinelli; DEEP ecliptic fields =
  DEEP/YOSO; CANFind DR1 = 19%; THOR = 100% of DR2. No catalog-scale gap left.

## 3. LIVE PILOT (counting, decisive)
Region OUTSIDE DES, low ecliptic latitude, multi-visit DECam night (from NSC exposure
table): RA 179.5–182.5, Dec +0.5–+3.5 (~9 sq deg), MJD 56769 (2014-04-02), ecliptic
lat +2°, 33 DECam exposures / 2.4 h, depth95≈24.2.
- ndet=1 orphan objects in field-night: 22,446 (mover + single-detection-noise pool).
- After mag(14–23.5)/fwhm/flag sanity: 10,342 clean orphans.
- Raw same-night orphan PAIRS in slow-mover window (0.5–10 arcsec/hr, dmag<1.5): 414
  => ~46 raw 2-point tracklet candidates / sq deg / night.
- FP diagnosis: rate histogram rises MONOTONICALLY toward the window edge
  {0.5–1"/hr:2, then 10,21,30,32,44,56,66,78,75 up to ~10"/hr} — pure chance-coincidence
  signature (pair count ∝ separation ∝ area), NOT a real mover population. Slow (TNO/
  Centaur) end 0.5–3"/hr holds only ~63 pairs over 9 sq deg, essentially all random
  coincidences of unrelated single-detection noise/edge artifacts.
- Yield reality: converting a 2-point pair into a real tracklet needs a 3rd coherent point
  + orbit-consistency + known-object subtraction — CANFind's ≥3-point rule and THOR's
  orbit-linking, already run over this catalog. Genuine NEW slow movers surviving that in a
  random 9 sq deg ecliptic field: ≈0 (bright ones designated; faint ones below catalog
  depth). No clean unknown tracklet fell out.

## 4. CREDIT MECHANICS (verified)
- Comet path CONFIRMED: C/2014 UN271 (Bernardinelli–Bernstein) found in archival DES
  images during a TNO search; MPC announced 19 June 2021; provisional 2014 UN271; comet
  designation C/2014 UN271 NAMED after the archival finders. Archival discoverer does get
  the comet name — but the find was image-domain (shift-and-stack), funded team, pixel
  access.
- Minor-planet path: provisional designation on accepted submission; formal discoverer
  credit at NUMBERING (multi-opposition, secured orbit). Archival/survey detections
  submitted under the survey obscode (DECam), linker/measurer attributed — the model
  THOR-on-NSC used for its ~27,500 MPC submissions. A solo catalog-only submitter re-derives
  objects already in B612's MPC pipeline.

## 5. RUBIN CLOCK
- Rubin DP1 released 30 June 2025 (ComCam commissioning Oct–Dec 2024; 1,792 exposures, 7
  fields; 431 SSOs incl. 93 new, reported to MPC). Full LSST ops ramping 2026.
- Rubin Solar System Processing links its own detections nightly and submits orbits to MPC
  daily; yearly DRs reprocess everything. Rubin will dominate new southern-sky SSO discovery
  (millions over 10 yr, ~24.5/visit) — renders a slow archival DECam BLIND-discovery redo
  irrelevant on a ~1–2 yr horizon.
- Conversely, Rubin's southern footprint overlaps the DECam-era archive, making archival
  DECam valuable for PRECOVERY / arc-extension of Rubin objects — the R1 lane (GATE-R1 =
  GO), NOT this blind-novelty lane.

## BOTTOM LINE
Blind catalog-tracklet mining of NSC for new SSOs is scooped at 100% of DR2 by ADAM::THOR
(superior method, MPC output, incl. Centaurs+TNOs); the faint slow-mover discovery space is
below catalog depth and contested in the image domain by DES/DEEP/YOSO; Rubin closes the
forward-looking value. The pilot confirms a chance-coincidence FP wall at the 2-point level.
NO-GO for blind novelty. The creditable no-telescope niche remains the R1 PRECOVERY lane
(arc-extension of known short-arc objects), not new-object discovery.

## Artifacts (all in /tmp/novelty_gate/gate/)
- pilot2.py / pilot2.out — live orphan+pair counting pilot (field RA181/Dec+2, MJD 56769)
- tapq2.py — multi-visit ecliptic DECam night finder (NSC exposure table)
- cols.py — verified meas/object schema
- REPORT.md — this file
