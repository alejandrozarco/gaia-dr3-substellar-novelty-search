# Precovery attempt — 2004 YH32 (wave 2)

Date: 2026-07-07 | Work dir: /tmp/precovery_wave2/2004_YH32/
Outcome: **NO_ARCHIVAL_COVERAGE** (honest null; no submission)

## Target / gate row
- 2004 YH32, inner-system Centaur, H=13.11, a=8.14 AU, nopp=3, arc 2004-12 -> 2007-01.
- Gate (campaign_targets.csv): rank 1; best_epoch 2005-07-01; best_V 19.68; SMIA 0.19"/SMAA 0.42"; n_pass_epochs = 1.
- EPOCH-FRAGILE: only the 2005 near-perihelion sample passes brightness; 2013/2017/2021 samples V~24.
- Per chain-discipline rule 1, searched ONLY the 2005 passing window.

## Ephemeris (self-derived, JPL Horizons, geocentric 500)
Orbit is superbly determined across the whole 2005 window (3-opp arc): SMAA ~0.42", SMIA ~0.19".
Gate epoch 2005-07-01 = JD 2453551.5, RA 57.408, Dec +3.416, V 19.68.
V stays ~19.6-19.8 from Apr through Sep 2005 (near perihelion, r~3.5 AU).

## Decisive geometry (why the gate is optimistic)
The SMIA gate scored brightness+uncertainty only, NOT observability geometry. Across the entire
pre-August 2005 window the object sits at LOW SOLAR ELONGATION:
  2005-06-10 elong 33 deg; 2005-07-01 elong 45.6 deg; 2005-07-25 elong 63 deg; 2005-08-03 elong 70 deg.
Deep-survey telescopes do not image at ~33-46 deg elongation (near solar conjunction). This is
the same reason the object's own MPC astrometric arc has a hard GAP from 2005-03 to 2005-08:
observations resume 2005-08 precisely when elongation clears ~70 deg. The gate-passing epoch
2005-07-01 lands inside that unobservable, un-imaged gap.

## Channels searched (full log: search_log.csv)
1. SSOIS (CADC ssosclf.pl, byname, extres=yes) — authoritative multi-archive image index
   (DECam, CFHT/MegaCam, Subaru SuprimeCam+HSC, ESO-VISTA/VST, Pan-STARRS1, KPNO-4m, HST, WISE, ZTF, LCO):
   - 2005-04-01..2005-10-01: **0 footprints**
   - 2005 full calendar year: **0 footprints**
   - 2004..2022 (resolver sanity): 1,407 footprints -> object resolves and IS well covered,
     but EARLIEST footprint is 2006-08-02; ALL coverage is 2006+, where V~24 (fails brightness gate).
     (DECam 546, WISE 377, ESO-VISTA 173, PS1 123, Subaru 50, etc. — every deep archive postdates the
     bright 2005 window; DECam/PS1/ZTF did not exist in 2005.)
2. SDSS DR16 imaging (NOT indexed by SSOIS — independent channel), 4 track positions:
   - 2005-06-10 (Dec +0.10, grazes Stripe 82): in footprint (4961 objs) but imaging MJDs 1998-2007,
     NONE near 2005-06; and elong 33 deg = SDSS would not image there regardless.
   - 2005-07-01 / 07-25 / 08-03 (Dec +3.4 / +6.9 / +8.2): 0 SDSS objects -> outside imaging footprint.

## Chain discipline
- Rule 1 (passing epochs only): satisfied — searched the single 2005 window; did not wander to 2006+.
- Rules 2-4 (motion/stationary/magnitude): N/A — zero candidate detections (no images to search).
- Rule 5 (negative control): degenerate/moot — with zero images in the passing window there is no
  background for a +1 deg offset box to be compared against; the control is trivially satisfied.
- Rule 6 (log every epoch): done (search_log.csv).

## Verdict
Real archival coverage of 2004 YH32 exists in abundance, but ALL of it is 2006 or later, when the
object is V~24 (below the gate). The single 2005 gate-passing epoch is un-imaged because the object
was near solar conjunction (elong 45 deg). No precovery is possible from existing archives; none is
physically expected. This is a clean NO_ARCHIVAL_COVERAGE null. No candidate chain; nothing submitted.

Lesson for the campaign: the SMIA gate should carry a solar-elongation cut (e.g. require elong >
~60-70 deg at the passing epoch). Bright-but-near-sun perihelion samples pass on V+uncertainty yet
have no archival imagery by construction. 2004 YH32 is the archetype: bright, tiny error ellipse,
zero coverage.
