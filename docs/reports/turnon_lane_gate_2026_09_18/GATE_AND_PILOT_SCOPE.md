# Prior-art gate + pilot scope — "turn-on" CV search by deep-archive × ZTF cross-match
Date 2026-09-18. Trigger: can we find more objects like ZTF19abxfaon (4 yr at r≈23.2 →
permanent 5.5-mag turn-on)? The closed state-cycler lane searched ZTF ALERTS at high |b|
and returned a null; this proposes the inverted, catalogue-level selection at low |b|.

## 1. Prior-art gate — QUALIFIED PASS (not a clean pass; read the caveats)

Repo screen (`scripts/litcheck/prior_art.py`, strict AND): **0 matches** for the specific
method string. Broad screen + targeted web search establishes the real picture:

**The field is crowded at the component level:**
- **Duffy et al. 2024** (arXiv:2411.07744) — high/low accretion states in VY Scl CVs with ZTF+TESS. (Already our ideation-scan control sample.)
- **Bernhard et al. 2025** (arXiv:2502.00736) — *new* possible VY Scl found from survey data (2005→present). The amateur-expert network (Bernhard, Kato, Denisenko, MGAB) actively discovers VY Scl systems from public surveys.
- **Szkody et al. 2020, 2021** — annual catalogues of CVs found in ZTF (VizieR J/AJ/159/198, J/AJ/162/94).
- **ML CV discovery in the ZTF alert stream** (MNRAS 527, 8633) and the **ZTF Source Classification Project** variable-source catalogues (arXiv:2312.00143).
- **VSX already holds >15,300 objects classified as CV**, of which ~5,683 crossmatch to ZTF alerts.
- **NSC DR2 itself ships 8 variability indices and flags ~23 M variable objects** — archival-variability selection is built into the catalogue we would mine.
- Using deeper archives (PS1/LS) to pin *quiescence* is standard practice — e.g. new dwarf novae with quiescent PS1 counterparts and ≳4 mag outburst amplitudes.

**What is NOT found published:** using the deep archival catalogue as the *selection* step
— i.e. r≈23 pre-2018 detections cross-matched against ZTF bright-state detections — to
recover turn-ons that never alert because quiescence is below the alert threshold.

**Verdict per CLAUDE.md prior-art rule:** method-level prior art EXISTS. Frame the lane as
**supply-limited selection inside a crowded field, not a novel method.** Mandatory:
front-filter every candidate against the *published lists* above, not just SIMBAD/VSX.
Absence from the strict arXiv screen is weak evidence and must not be quoted as novelty.

## 2. Pilot scope (cheap, kill-gated)

**Gate zero — footprint reality check (do FIRST, ~1 h).** The method needs deep pre-2018
DECam/LS coverage AND ZTF coverage at low |b|. NSC DR2 is DECam-based (dec ≲ +36) and the
Legacy Surveys historically avoid the plane; ZTF needs dec ≳ −31. **Measure the actual
overlap area at |b| = 5–20° before choosing a field** — if usable overlap is <50 deg², the
lane dies here on footprint, not on astrophysics.

**Field:** the largest contiguous overlap found by gate zero, target ~100–300 deg²,
|b| 5–20° (CV density rises toward the plane; our null covered |b| 35–60° only),
avoiding the inner bulge (crowding) and E(B−V) > 1.

**Selection:**
1. Deep archival (NSC DR2 / LS DR10, epoch < 2018): point-like sources with r > 22.
2. Cross-match (1.5″) to ZTF DR detections with r < 20.5 on ≥2 distinct nights.
3. Require Δmag > 2.5 between archival quiescence and ZTF bright state.
4. Require the bright state to be *sustained* (detections spanning > 30 d) — this is the
   discriminator against dwarf-nova outbursts, which are days-long.

**Mandatory rejections:** VSX (all 15,300 CV entries + full catalogue), Szkody ZTF CV
catalogues, ZTF SCP variable catalogue, GCVS, Milliquas + WISE W1−W2 > 0.7 (AGN),
SIMBAD; asteroids via the ≥2-distinct-nights requirement plus ecliptic-latitude flagging
(ZTF19abxfaon itself is at β = −0.12° and picked up two asteroid contaminants).

**Verification of survivors:** full ZTF DR + forced photometry, state structure (sustained
states vs outbursts), colour, and the same manual-grade VSX package standard used for
ZTF18abxnwmb.

**Kill criteria (pre-registered):**
- Footprint overlap < 50 deg² → CLOSE (gate zero).
- >90% of raw candidates already in the published CV/variable catalogues → CLOSE (scooped in practice).
- 0 survivors after full verification in the pilot field → report a density limit and close, as the state-cycler lane did.
**Success:** ≥1 verified uncatalogued sustained turn-on → lane lives, and each find is a
VSX-fileable object of exactly the ZTF19abxfaon class.

**Cost:** gate zero ~1 h; full pilot ~1 day of agent time. No new accounts, no telescope.

---

# GATE ZERO RESULT (2026-09-18) — **PASS, decisively**

Measured, not assumed, from `nsc_dr2.exposure` (NOIRLab Data Lab TAP) — the deep-archive
side — plus live ZTF spot-checks.

## Deep pre-2018 coverage in the ZTF-overlapping low-latitude band
Query: mjd < 58119 (pre-2018), exptime ≥ 60 s, filter ∈ griz, |b| = 5–20°, −30° < dec < +32°.

- 214,009 deep pre-2018 griz exposures all-sky → **4,046 in the band**, of which
  **3,023 reach depth95 > 22** (c4d/DECam 2,931 · ksb 67 · k4m 25); 1,729 are r-band.
- Sky area covered (per-instrument FOV radii: DECam 1.1°, Bok 0.6°, Mosaic 0.3°;
  0.15°-grid, 192,432 cells over a 4,330 deg² band):
  - **any deep griz: 1,458 deg²**
  - **deep r-band: 1,190 deg²**
- **Kill threshold was <50 deg². Actual is 1,190 deg² — passes by ~24×.**

## Depth is sufficient for the selection
r-band depth95: median **23.09**, quartiles 22.72 / 23.45, max 25.22; **58% of exposures
reach deeper than 23.0**. The method needs r ≈ 23 quiescence detections — this is exactly
that depth, and it is the same DECam/NSC data that measured ZTF19abxfaon at r = 23.05–23.44.

## Where the coverage is (deg² by galactic longitude)
| l bin | deg² | note |
|---|---|---|
| 200–220 | 273.9 | **anticentre** |
| 0–20 | 259.0 | inner Galaxy — high extinction/crowding, southern dec |
| 180–200 | 244.9 | **anticentre** |
| 220–240 | 155.3 | **anticentre** |
| 340–360 | 142.0 | inner Galaxy |
| 40–60 | 137.9 | |
| 240–260 | 136.7 | |

## ZTF side verified live
Five random deep-exposure centres in l = 195–235 queried against ZTF DR (30″ cones):
13–42 ZTF objects each, median **16–73 epochs per object**, baselines **2,609–2,764 days**
(7.1–7.6 yr). ZTF coverage is not a constraint in this region.

## RECOMMENDED PILOT FIELD
**Galactic anticentre, l = 195–235°** — 1,163 deep exposures, median depth95 23.03,
dec −22° to +23.5°, ~400–500 deg² of deep coverage inside the l = 180–240 block (674 deg²).
Chosen over the l = 0–20 / 340–360 inner-Galaxy blocks because those sit at southern
declinations at the edge of ZTF's range and carry far worse extinction and crowding, which
would both hide quiescent counterparts and inflate the false-match rate.

**Gate zero is cleared. The remaining pre-registered kills stand:** >90% of raw candidates
already in the published CV/variable catalogues → close; 0 verified survivors → density
limit and close.

---

# PILOT BUILD NOTES (2026-09-18) — feasibility findings that change the design

**1. No server-side join exists.** Data Lab hosts NSC DR2 (object/meas/exposure/variable) and
~60 pre-computed 1.5″ crossmatch tables — but **none to ZTF** (only user `mydb` entries).
IRSA hosts the ZTF object tables (`ztf_objects_dr20…dr24`, 70 columns: ra, dec, fid,
medianmag, minmag, maxmag, magrms, chisq, con, ngoodobsrel, refmag, lineartrend …).
So the cross-match must be **pulled from two services and joined locally** → the pilot must
be area-bounded. IRSA TAP counts on the ZTF object tables are slow (a COUNT over 4 deg²
exceeded 500 s), so the ZTF side should be pulled per small tile, not per large region.

**2. Population sizing** (2×2° anticentre test box, RA 117.3–119.3, Dec +9.4–11.4):
NSC DR2 objects 284,874 total → **107,789 with 22 < r < 24** → **66,304 of those stellar
(class_star > 0.5)**, i.e. **~16,500 faint stellar archival sources per deg²**. A 25 deg²
pilot therefore pulls ~400 k archival rows — fine locally, but it means the join is
dominated by chance alignments unless isolation is enforced (see 4).

**3. `nsc_dr2.object` carries what the selection needs:** per-band mags (u,g,r,i,z,y),
`mjd` + `deltamjd` (so "all epochs pre-2018" is expressible at object level),
`class_star`, `ndet`/`ndetr`, and a full variability block (`rmsvar, madvar, chivar,
etavar, nsigvar, variable10sig`).

**4. Dominant false-positive mode = BLENDING, not astrophysics.** ZTF pixels are 1.0″ with
~2″ effective resolution; NSC/DECam resolves ~0.9″. A faint NSC source 1–2″ from a bright
star will "match" a bright ZTF object and mimic a turn-on. **Mandatory cut: the faint NSC
source must be isolated — no NSC source brighter than r = 21 within 3″** — plus a check
that the ZTF position centroid is closer to the faint source than to any neighbour.

**5. DESIGN REFINEMENT (raises the lane's novelty value).** Objects that turned on *before*
ZTF began and have stayed on are **photometrically ordinary inside ZTF** — ZTF sees a
constant star. They are therefore invisible to every ZTF-internal variability search
(SNAD, ZTF SCP, Szkody's CV catalogues, the alert-stream ML classifiers) and can only be
found by comparison with the deeper pre-ZTF archive. **Select `magrms` LOW as well as
`medianmag` bright** — that subset is the genuinely unscooped part of the parameter space,
and it is the complement of the state-cycler lane we already closed (which required
variability *within* ZTF).
