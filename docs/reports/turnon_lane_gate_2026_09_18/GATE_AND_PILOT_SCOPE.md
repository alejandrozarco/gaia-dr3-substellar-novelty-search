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
