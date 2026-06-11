# Gaia DR4 Pre-Registration + Day-One Re-Analysis Plan

**The 4 standing UNCONFIRMED novel candidates of the skepticism-first Gaia DR3 dormant-compact-object search**

- **Compiled:** 2026-06-01 (sub-agent analysis artifact — NOT a dossier edit; main thread integrates).
- **Purpose:** Pre-register *quantitative, falsifiable* Gaia DR4 predictions for each candidate **before the data drop**, so the day-one re-analysis is a confirm/refute test against thresholds fixed in advance — the rigor this project values over post-hoc rationalization.
- **Gaia DR4 release:** 2 December 2026. Baseline = **66 months / 5.5 yr** (25 Jul 2014 → 20 Jan 2020, the complete nominal mission) vs DR3's **34 months**. Reference epoch J2017.5. DR4 publishes, for **all** sources: the full **epoch (transit) astrometric time series**, epoch photometry (G + BP/RP), epoch RV + RVS spectra, a re-derived `nss_two_body_orbit` with the longer baseline, and an unresolved-binary / exoplanet catalogue. ([ESA Gaia DR4 content](https://www.cosmos.esa.int/web/gaia/dr4); [ESA release scenario](https://www.cosmos.esa.int/web/gaia/release))
- **Why DR4 is decisive for THIS sample:** DR3 NSS published only the *fitted* Thiele-Innes / Campbell parameters — never the underlying per-epoch positions. DR4 releases the **individual astrometric transits**, so for the first time we can (a) re-fit the photocentric orbit from the measurements directly, (b) measure the goodness-of-fit (F2) of a *single*-Keplerian model against the data and test for a non-Keplerian wobble (the triple signature), (c) tighten a_phot / i with ~2× the baseline (critical for the loose Thiele-Innes coefficients flagged below), and (d) break the inclination→M2 degeneracy that DR3 left open. The 1.6× longer baseline is especially decisive for the long-period systems (WDJ060042 P=935d, only ~1.0 cycle in DR3 → ~2.1 cycles in DR4; UCAC4 313 P=592d, ~1.7 → ~3.4 cycles).

> **Scope honesty (set up front).** DR4 epoch astrometry resolves the *dynamical* questions — orbit shape, a_phot, inclination, M2, and triple-vs-single. It does **NOT** resolve the *companion-class* question for the two massive-WD systems (cool-DWD vs dormant ~1.3 M⊙ NS): that degeneracy is photometric/spectroscopic (the companion is dark in every archival band, and K₁ is identical for a cool WD and a NS of the same mass), so it needs **HST/COS FUV** regardless of any astrometric improvement. This is flagged per-candidate in the "What STAYS undecided" column.

---

## Master parameter + prediction table

The "current params" are the authoritative full-Thiele-Innes-covariance re-analysis (`/tmp/wd_sed_mass_refinement_2026_05_31.md`, 2026-05-31) cross-checked against `data/derived/main_hunt_derived_v2_relaxed_M1corrected.parquet` and the per-candidate dossiers in `docs/dossiers/`. **Realistic budget** = a_phot ± a_phot/significance (the Gaia `significance` is the SNR of a_phot from the full covariance). **Conservative budget** = full-TI-marginal Monte-Carlo with the published 12×12 correlation matrix (exposes the loose-coefficient tail).

| Candidate (Gaia DR3 source_id) | Headline hypothesis | DR3 orbit (P, e, a_phot, i, sig, **F2**, RUWE) | M₁ (source) | f(M) | M₂ (realistic) / [conservative] | **Competing hypotheses** | DR4 IF compact/headline TRUE | DR4 IF alternative TRUE | **CONFIRM / REFUTE thresholds (pre-registered)** | What STAYS undecided after DR4 |
|---|---|---|---|---|---|---|---|---|---|---|
| **WG 26** — 6092654861665006592 | Sub-Chandra **double-WD** (DA WD + ~0.65 M⊙ cool WD), d=56.4 pc | P=175.94±0.29 d; e=0.064±0.026; a_phot=5.40±0.08 mas; **i=77.1°** (measured); sig=68.8; **F2=−1.11 (clean)**; RUWE=5.01 | 0.62±0.02 (Sahu 2023 HST/COS; GF21-phot 0.528) | 0.170±0.007 | **M₂=0.649 [0.63–0.67]**; M_tot=1.27±0.03 | (A) unresolved 176-d DWD **[favored]**; (B) hierarchical triple (inner 176-d pair + outer P≫DR3 baseline) — IPD harmonic 0.063 hints at extra structure; (C) M-dwarf companion (already SED-excluded ~2000σ) | Single-Keplerian epoch fit stays clean: **F2 stays ≲ +2**; a_phot=5.40 mas and **i≈77°** reproduce to ≪1σ; no residual long-period acceleration; parallax tightens to ~56 pc; **M₂ stays 0.60–0.70 M⊙** | Triple → DR4 epoch series shows a **non-Keplerian residual / a 2nd long-period (P₃≳5–8 yr) acceleration term** on top of the 176-d ellipse; or a_phot shrinks (luminous-3rd-body photocentre dilution) and M₂ drops | **CONFIRM (clean DWD):** F2(DR4 single-Kepler) ≤ +2 AND a_phot within 3σ of 5.40 mas AND no significant acceleration/2nd-period term. **REFUTE→triple:** DR4 acceleration or 2nd-period term significant at >5σ, OR F2>+5 for the single-Kepler model. (M₂ already too low for a NS — compact-NS hypothesis is N/A here; the "compact" question for WG 26 is moot, the science is *is it a clean DWD or a triple*.) | **Nothing dynamical** — but the cool-WD-vs-other-degenerate class detail and the systemic γ / sin-i-cross-check still want 1 RV epoch (K₁≈21 km/s predicted). DR4 fully settles the triple question. |
| **WDJ020915** — 332248057157474176 | Long-P **M_tot>M_Ch DWD or WD+NS** (DA WD + ~1.32 M⊙ dark companion), d=84 pc | P=274.52±0.67 d; e=0.024±0.031; a_phot=7.73±0.12 mas; i=65.8° (**loose** — A,G unconstrained); sig=67.3; **F2=+8.39 (WEAK fit)**; RUWE=**8.79** | 0.718±0.053 (GF21 DA; He-fit 0.694) | 0.556 [0.53–0.585] | **M₂=1.322 [1.27–1.38]**; M_tot=2.04±0.10; **[conservative a_phot 95% CI 7.7–22.6 mas → M₂ 1.29–15.2]** | (A) M_tot>M_Ch DWD/WD+NS at i≈66°, M₂≈1.3 **[realistic favored]**; (B) **non-Keplerian / unmodelled acceleration inflating F2=+8.4** (a 3rd body — the conservative MC's huge M₂ upper tail is driven by this); (C) under-estimated per-epoch errors (F2 high but a_phot unbiased) | **The headline test of the whole sample.** DR4 single-Keplerian epoch fit **collapses F2 from +8.4 to ≲+2**, A & G become well-constrained (errors ≪ value), a_phot tightens to ±2–3% and stays ≈7.7 mas → **M₂ pins to 1.3±0.1 with i≈66° confirmed**; no 2nd-period term; the orbit is a single clean Keplerian. | (B) triple/acceleration → DR4 reveals a **2nd astrometric period or a significant acceleration** term; the 176→274-d ellipse rides on a longer wobble; a_phot of the *inner* orbit shrinks → M₂ drops below the NS floor (<1.2 M⊙) and the "M_tot>M_Ch" claim collapses. (C) noise-only → F2 falls AND a_phot ≈ unchanged (M₂ holds) — i.e. distinguishes (B) from (C). | **CONFIRM (real M_tot>M_Ch single-companion):** DR4 F2 ≤ +2 for a single Keplerian AND a_phot within 3σ of 7.73 mas (M₂ ≥ 1.2 M⊙) AND **no** significant 2nd-period/acceleration term. **REFUTE:** any of — DR4 2nd-period or acceleration term >5σ (→ triple, M_tot>M_Ch claim void); OR refined a_phot drops M₂ below 1.2 M⊙ (→ ordinary sub-Ch DWD); OR DR4 still F2>+5 with the longer baseline (→ orbit unreliable, candidate parked). | **WD-vs-NS companion class** (M₂≈1.3 is consistent with *both* a cool ONe WD and a dormant low-mass NS; K₁ identical). DR4 cannot break this — needs **HST/COS FUV** (detects a WD photosphere to T₂≈25 kK). No usable archival GALEX (single shallow off-axis NUV leg). |
| **WDJ060042** — 2909342818326298112 | Long-P **M_tot>M_Ch DWD or WD+NS** (DA WD + ~1.37 M⊙ dark companion), d=98 pc — **strongest Chandra-straddle** | P=935.14±31.5 d; e=0.038±0.023; a_phot=19.62±0.95 mas; i=66.4° (**loose** — F unconstrained); sig=20.6; **F2=+0.79 (clean)**; RUWE=6.13; π tension 2.8σ (GS 10.24 vs NSS 12.08 mas) | 0.612±0.05 (GF21 DA; He-fit 0.554) | 0.653 [0.55–0.77] | **M₂=1.367 [1.23–1.52]**; M_tot=1.98±0.17; **P(M₂>1.40)=41%**; [conservative a_phot 19.0–44.2 → M₂ 1.31–8.6] | (A) M_tot>M_Ch DWD/WD+NS, companion **genuinely straddling Chandra** (M₂≈1.37; near-Ch ONe WD *or* low-mass NS) **[favored, clean orbit]**; (B) hierarchical triple (less likely — F2 already clean); (C) a_phot loose tail (F unconstrained) inflating M₂ | DR4's **1.6× longer baseline covers ~2.1 full cycles** (vs ~1.0 in DR3) → P refines from ±31 d to ~±5 d, **F unconstrained→constrained**, a_phot tightens to ±2–3%, **i confirmed ≈66°**, the GS-vs-NSS parallax tension **resolves to a single ~83-pc value**, **M₂ pins to ±0.05** → a clean verdict on whether M₂ exceeds 1.40. Single-Keplerian F2 stays clean (≲+2). | (B) triple → 2nd-period/acceleration term appears with the longer baseline; (C) loose-tail → refined a_phot lands lower in [1.23–1.52], M₂ settles ~1.3 (sub-Ch DWD, no longer a Chandra straddle) | **CONFIRM (M_tot>M_Ch single-companion, possibly super-Ch companion):** DR4 F2 ≤ +2 single-Kepler AND a_phot within 3σ of 19.62 mas AND no 2nd-period/accel term; **super-Ch companion confirmed IF refined M₂(±0.05) > 1.40** at the joint M₁ posterior. **REFUTE / down-grade:** M₂ refines below 1.33 (NS-floor) → ordinary sub-Ch DWD; OR 2nd-period/accel >5σ → triple. | **WD-vs-NS companion class** — DR4 cannot break it (same K₁; SED-degenerate below T₂≈10–11.5 kK even *with* the GALEX NUV). Needs **HST/COS FUV**. The M₂≈1.37 value makes the dormant-NS reading physically live (≥ NS minimum), so this is the candidate where the class question matters most. |
| **UCAC4 313-025977** — 5612039087715504640 | **~13–15 M_J brown-dwarf / planet-borderline** companion to an M4–5V dwarf, d=32.4 pc | P=592.32±3.29 d; e=0.214±0.026; a_phot=1.32±0.12 mas; i **undetermined** (degenerate); sig=55.0; RUWE=4.72; AEN_sig=355σ | 0.23±0.04 (Kervella 2022 / TIC); M_G→M4V | ≈6.0×10⁻⁶ M⊙ | **M₂≈13 M_J face-on** (i=90°); ∝1/sin i → 17 M_J at i≈60°, ≳25 M_J at i≲45° | (A) substellar BD/planet-borderline at i≈90° (~13 M_J); (B) **inclination-inflated** — a moderate/low i lifts M₂ into the **stellar** regime (M-dwarf secondary, e.g. i≈30° → ~25–40 M_J→0.04 M⊙+); (C) higher M₁ than 0.23 also raises M₂ | DR4 epoch astrometry **measures i directly** from the Thiele-Innes shape (a_phot=1.32 mas wobble well-sampled over ~3.4 cycles). IF substellar: **i resolves near 90°** (edge-on/high) → **M₂ stays 12–15 M_J**; clean single-Keplerian; a_phot confirmed ≈1.32 mas. Predicted RV K₁≈860 m/s at i=90° (DR4 epoch RV at G=13.9, σ≈1–3 km/s, is marginal — ground RV is the cleaner amplitude test). | (B) low-i → DR4 measures **i≲45–50°** → M₂ ≥ 20–25 M_J (high-mass BD) or, at i≲30°, into the low-mass-**star** regime; the "planet-borderline" headline collapses. (C) triple/blend → non-Keplerian residual (none expected; field is clean, IPD single-peak). | **CONFIRM (substellar):** DR4-measured **sin i ≥ 0.85 (i ≥ 58°)** at M₁=0.23 → M₂ ≤ ~15 M_J (BD, near D-burning line). **REFUTE (stellar/high-mass BD):** DR4 **i ≤ 45°** → M₂ ≥ 20 M_J; **fully refuted as substellar if M₂ ≥ 0.075 M⊙** (78.5 M_J, the H-burning limit) i.e. i low enough to make it an M-dwarf secondary. **Exact M₂(sin i) curve pre-registered in the per-candidate section.** | **Atmospheric class of the companion IF it lands at the BD/star boundary** — astrometry gives the dynamical mass; a spectrum (CARMENES/NIRPS) would type a luminous low-mass-star secondary if present. But DR4 i alone is decisive for the substellar-vs-stellar headline. |

---

## Per-candidate detail (quantitative predictions + decision trees)

### 1. WG 26 / Gaia DR3 6092654861665006592 — clean-DWD-vs-triple test

**Current state (DR3).** A hot DA WD primary (T_eff=21,705 K, log g=7.99, M₁=0.62 M⊙, cooling age 42 Myr; Sahu 2023 HST/COS) with a **clean** NSS Orbital photocentric ellipse: P=175.94 d, a_phot=5.40±0.08 mas, **i=77.1° (a measurement, not a floor)**, F2=−1.11 (excellent Keplerian fit), sig=68.8. The companion is dynamically M₂=0.649 [0.63–0.67] M⊙, M_total=1.27 M⊙ — **sub-Chandrasekhar by 0.13 M⊙**, SED-favored to be a cool CO/He double-degenerate (M-dwarf of that mass excluded ~2000σ; hot-WD companion excluded by SkyMapper u−v). The companion is too light to be a NS (0.65 ≪ ~1.2 M⊙ NS floor), so for WG 26 the open dynamical question is **not** compact-vs-not but **clean-binary-vs-hierarchical-triple** (the IPD harmonic-amplitude 0.063 and the high RUWE=5.01/AEN_sig=731 leave a third-body window open; RUWE is fully explained by the 5.4-mas wobble, but a long-P outer body would not yet have shown up in the 34-month DR3 baseline).

**DR4 prediction IF clean DWD (headline).** With the 5.5-yr epoch series:
- The single-Keplerian fit to the transits stays clean: **F2 ≲ +2**.
- a_phot reproduces at 5.40 mas (±3σ) and **i at 77°**; M₂ holds at 0.60–0.70 M⊙.
- **No** significant acceleration or 2nd-period term; parallax tightens around 56 pc.

**DR4 prediction IF hierarchical triple.** The 176-d ellipse rides on a longer-period wobble:
- DR4 epoch astrometry shows a **statistically significant acceleration term or a 2nd period P₃ ≳ 5–8 yr** (now within the 5.5-yr baseline) on top of the inner ellipse.
- Alternatively a_phot of the inner orbit shrinks (luminous third body pulling the photocentre) and the inferred inner-pair M₂ drifts.

**Decision thresholds (pre-registered).**
- **CONFIRM clean DWD:** DR4 single-Keplerian F2 ≤ +2 **AND** a_phot within 3σ of 5.40 mas **AND** no acceleration/2nd-period term > 5σ.
- **REFUTE → triple:** DR4 acceleration or 2nd-period term significant at > 5σ, **OR** single-Keplerian F2 > +5 with the longer baseline.
- (No compact/NS branch — M₂=0.65 is below the NS minimum; settled already.)

**What stays undecided after DR4.** Nothing dynamical. A single RV epoch (K₁≈21 km/s predicted; gravitational-redshift-corrected γ≈−93 km/s) would still be nice for the sin-i cross-check and to nail the companion as a quiescent DWD, but DR4 fully settles the triple question that DR3 cannot.

---

### 2. WDJ020915.51+380425.92 / Gaia DR3 332248057157474176 — the F2=+8.4 stress case (the single most DR4-dependent candidate)

**Current state (DR3).** DA WD primary (T_eff=14,958 K, log g=8.17, M₁=0.718 M⊙). NSS Orbital: P=274.52 d, a_phot=7.73 mas, i=65.8°, sig=67.3 — **but F2=+8.39 (a poor 8.4σ Keplerian fit) and RUWE=8.79.** The binary is unambiguously real (AEN_sig=807, ipd_frac_multi_peak=0, no blend), but the *orbit solution* is the weakest of the set. The realistic-budget companion mass is M₂=1.322 [1.27–1.38] M⊙ (M_total=2.04, P(M₂>1.40)=8.6% — **not** robustly super-Chandra), but the **conservative full-TI MC explodes to a_phot 7.7–22.6 mas → M₂ 1.29–15.2 M⊙, P(M₂>1.40)=85%**, because the Thiele-Innes A=−0.42±5.32 and G=+3.81±7.43 are *unconstrained* (error ≫ value). The two physical readings of F2=+8.4 are (B) a genuine non-Keplerian perturbation = a 3rd body, or (C) merely under-estimated per-epoch errors (G=16.2) inflating F2 without biasing a_phot.

**DR4 prediction IF real M_tot>M_Ch single-companion (headline).**
- The 5.5-yr epoch series **collapses F2 from +8.4 to ≲ +2** for a single Keplerian (the longer baseline + per-epoch errors now correctly weighted).
- A and G become well-determined (errors ≪ value) → a_phot tightens from the [7.7–22.6] conservative band to ±2–3% around ≈7.7 mas → **M₂ pins to 1.3 ± 0.1 M⊙ with i≈66° confirmed.**
- **No** 2nd-period/acceleration term.

**DR4 prediction IF triple/acceleration (alternative B).**
- DR4 reveals a **2nd astrometric period or a significant acceleration** term: the inner ~274-d ellipse rides on a longer wobble. Re-fitting the *inner* orbit alone shrinks its a_phot → **M₂ drops below the NS floor (<1.2 M⊙)** and the "M_tot>M_Ch" claim collapses to an ordinary sub-Ch DWD + a third body.

**DR4 prediction IF noise-only (alternative C).**
- F2 falls to ≲+2 **and** a_phot stays ≈7.7 mas (M₂ holds at ~1.3). This is how DR4 *distinguishes* (B) from (C): both lower F2, but only (B) moves a_phot/adds a period.

**Decision thresholds (pre-registered).**
- **CONFIRM real M_tot>M_Ch single-companion:** DR4 single-Keplerian F2 ≤ +2 **AND** a_phot within 3σ of 7.73 mas (M₂ ≥ 1.2 M⊙) **AND** no 2nd-period/acceleration term > 5σ.
- **REFUTE:** any of — (i) DR4 2nd-period/acceleration term > 5σ → triple, M_tot>M_Ch void; (ii) refined a_phot drops M₂ < 1.2 M⊙ → ordinary sub-Ch DWD; (iii) DR4 *still* F2 > +5 with the longer baseline → orbit unreliable, **park the candidate**.

**What stays undecided after DR4.** **WD-vs-NS companion class.** M₂≈1.3 is consistent with both a cool ONe WD and a dormant low-mass NS, and K₁ is identical for both → an RV epoch (K₁≈25 km/s, feasible at G=16.2) gives M₂ but **not** the class. Only **HST/COS FUV** breaks it. No usable archival GALEX (a single shallow off-axis NUV leg, not in GUVcat). **This is the candidate whose headline most depends on DR4: a clean DR4 orbit promotes it; a 2nd period demotes it.**

---

### 3. WDJ060042.75-293041.36 / Gaia DR3 2909342818326298112 — the strongest Chandra-straddle; long-P baseline win

**Current state (DR3).** Cool DA WD primary (T_eff=7,121 K, M₁=0.612 M⊙, cooling age ~1 Gyr). NSS Orbital: P=935.14±31.5 d, a_phot=19.62±0.95 mas, i=66.4°, sig=20.6, **F2=+0.79 (a clean Keplerian fit)** despite RUWE=6.13. Companion M₂=1.367 [1.23–1.52] M⊙, M_total=1.98 — **P(M₂>1.40)=41%, a genuine Chandrasekhar straddle.** Two caveats: (i) the Thiele-Innes F=+2.96±17.07 is unconstrained (loosens i and the a_phot upper tail; conservative MC → M₂ up to 8.6 M⊙), and (ii) a **2.8σ parallax tension** (gaia_source 10.24 vs NSS-internal 12.08 mas) — the textbook orbital-wobble-absorbed-into-single-star signature, but it means the distance (and hence the absolute scale) is not yet pinned. The orbit covered only **~1.0 full cycle** in the 34-month DR3 window.

**DR4 prediction IF real M_tot>M_Ch single-companion (headline).** This is the candidate where the **1.6× longer baseline matters most**: 5.5 yr covers **~2.1 full P=935-d cycles** (vs ~1.0):
- P refines from ±31 d to ~±5 d; the **unconstrained F coefficient becomes constrained**; a_phot tightens to ±2–3%; **i confirmed ≈66°.**
- The gaia_source-vs-NSS **parallax tension resolves to a single ~83-pc value** (DR4 fits astrometry + orbit jointly from the transits).
- **M₂ pins to ±0.05 M⊙** → a clean verdict on whether the companion exceeds 1.40 M⊙.
- Single-Keplerian F2 stays clean (≲+2).

**DR4 prediction IF alternative.** (B) triple → a 2nd-period/acceleration term emerges with the longer baseline (less likely — F2 is already clean at +0.8). (C) loose-F tail → refined a_phot lands lower in [1.23–1.52] and M₂ settles near 1.3 (a sub-Ch DWD, no longer a straddle).

**Decision thresholds (pre-registered).**
- **CONFIRM M_tot>M_Ch single-companion:** DR4 single-Keplerian F2 ≤ +2 **AND** a_phot within 3σ of 19.62 mas **AND** no 2nd-period/acceleration term > 5σ.
- **Super-Chandra *companion* confirmed** additionally **IF** the refined M₂ (now ±0.05) **> 1.40 M⊙** at the joint M₁ posterior.
- **REFUTE / down-grade:** refined M₂ < 1.33 M⊙ (NS-floor) → ordinary sub-Ch DWD; **OR** 2nd-period/acceleration > 5σ → triple.

**What stays undecided after DR4.** **WD-vs-NS companion class.** Even with the GALEX NUV in hand, the SED is degenerate below T₂≈10–11.5 kK; a ~1.3 M⊙ WD cooled past ~1–2 Gyr is photometrically identical to a dark NS, and K₁ is the same. Because M₂≈1.37 sits *at* the NS-mass range, the dormant-NS reading is physically live here — making the class question scientifically sharpest for this object. Needs **HST/COS FUV**. (RV at G=18.4 is hard: K₁≈17 km/s, σ_K≈1.5 km/s/epoch, ~6 epochs over 2.5 yr for ~28σ — but RV still won't give the class.)

---

### 4. UCAC4 313-025977 / Gaia DR3 5612039087715504640 — inclination is the whole ballgame

**Current state (DR3).** Nearby M4–5V dwarf (M₁=0.23±0.04 M⊙, d=32.4 pc). NSS Orbital: P=592.32 d, e=0.214 (the most eccentric of the four — a more informative orbit), a_phot=1.32±0.12 mas, sig=55.0, RUWE=4.72, AEN_sig=355σ. The companion's dynamical mass is **purely inclination-degenerate**: M₂≈13 M_J *only* at face-on (i=90°), scaling as M₂∝1/sin i. DR3 gives no inclination, so the substellar headline is unproven — a moderate inclination lifts M₂ into the high-mass-BD or even low-mass-stellar regime. The field is clean (Gaia single source within 5″, IPD single-peak), so a blend/triple is disfavored a priori.

**Pre-registered M₂(sin i) curve** (M₁=0.23 M⊙, from the dossier f(M) inversion):

| i (sin i) | M₂ | Regime |
|---:|---:|---|
| 90° (1.00) | ~13 M_J | planet/BD borderline (≈ D-burning 13 M_J) |
| 72° (0.95) | ~14 M_J | BD |
| 58° (0.85) | ~15–16 M_J | BD |
| 45° (0.71) | ~18 M_J | BD |
| 30° (0.50) | ~25 M_J | high-mass BD |
| ~10° (0.17) | ~75–80 M_J ≈ 0.075 M⊙ | **H-burning limit → low-mass star** |

**DR4 prediction.** The epoch astrometry **directly measures i** from the Thiele-Innes shape — the a_phot=1.32 mas wobble is sampled over **~3.4 cycles** in the 5.5-yr baseline (vs ~1.7 in DR3), so the Campbell elements (i, ω, Ω) become well-determined.
- **IF substellar (headline):** DR4 resolves **i near edge-on/high (sin i ≥ 0.85)** → **M₂ stays 12–15 M_J**; clean single-Keplerian; a_phot confirmed ≈1.32 mas. (DR4 epoch RV at G=13.9 gives ~10 epochs at σ≈1–3 km/s vs the predicted K₁≈860 m/s at i=90° — marginal; ground RV HARPS/NIRPS, K₁ 435–860 m/s, is the cleaner amplitude check, but **DR4 i alone is decisive for the substellar verdict**.)
- **IF inclination-inflated (alternative):** DR4 measures a **low i** → M₂ rises into high-mass-BD or stellar.

**Decision thresholds (pre-registered).**
- **CONFIRM substellar:** DR4-measured **sin i ≥ 0.85 (i ≥ 58°)** at M₁=0.23 → M₂ ≤ ~15 M_J (BD, near the D-burning line). A genuinely planetary mass (< 13 M_J) requires i ≳ 80°.
- **REFUTE as substellar:** DR4 **i ≤ 45°** → M₂ ≥ ~18–20 M_J (high-mass BD, headline weakens); **fully refuted** (it is a **star**) if the DR4 mass reaches M₂ ≥ 0.075 M⊙ (78.5 M_J), i.e. i low enough (≲10–15°) to put it on the H-burning side.
- **Caveat on M₁:** the mass scale also depends on M₁=0.23 M⊙ — DR4's improved parallax + (if released) astrophysical parameters tighten M₁; a higher M₁ shifts the whole curve up. Re-evaluate M₂ at the DR4 M₁.

**What stays undecided after DR4.** If DR4 lands the companion at the BD/star boundary, a spectrum (CARMENES/NIRPS) would *type* a luminous low-mass-star secondary if one is present (SB2 / spectral cross-correlation). But for the substellar-vs-stellar headline, **DR4 inclination is by itself decisive** — this is the candidate DR4 most cleanly resolves, because there is only one degeneracy (i) and no companion-class FUV problem (the secondary is not a degenerate remnant).

---

## Cross-candidate summary: what DR4 settles vs what it cannot

| Question | WG 26 | WDJ020915 | WDJ060042 | UCAC4 313 |
|---|---|---|---|---|
| Orbit shape / single-Keplerian F2 | DR4 ✔ (confirm clean) | **DR4 ✔ (the F2=+8.4 test — most decisive)** | DR4 ✔ (long-P baseline win) | DR4 ✔ |
| a_phot / inclination → M₂ | i already 77°; DR4 confirms | DR4 tightens A,G → M₂±0.1 | DR4 tightens F + π → M₂±0.05 | **DR4 measures i (the whole question)** |
| Hierarchical-triple vs single | **DR4 ✔ (2nd-period/accel test)** | DR4 ✔ | DR4 ✔ | DR4 ✔ (a_phot residual) |
| Parallax / distance scale | minor | minor | **DR4 resolves 2.8σ tension** | DR4 tightens |
| **Companion class (WD vs NS)** | N/A (M₂ too low) | **✘ DR4 cannot — needs HST/COS FUV** | **✘ DR4 cannot — needs HST/COS FUV** | N/A (luminous secondary; spectrum if needed) |
| Substellar vs stellar | N/A | N/A | N/A | **DR4 ✔ (via i)** |

**The single highest-information DR4 outcome** is WDJ020915's F2: it either collapses (promoting a clean M_tot>M_Ch single-companion orbit) or reveals a 2nd period (demoting it to a triple). WDJ060042 is the candidate most likely to *survive and sharpen* (clean F2 already; DR4 pins whether the companion is truly super-Chandra). UCAC4 313 is the cleanest DR4-decidable case (one degeneracy, i). WG 26 is essentially confirmed as a DWD; DR4 only forecloses the residual triple possibility.

---

## DAY-ONE DR4 PIPELINE (run the day DR4 drops, 2 Dec 2026)

> Env: `/Users/legbatterij/claude_projects/ostinato/.venv/bin/python` (no pip-install). Write to /tmp only; do not edit dossiers/CANDIDATES.md. source_ids as strings. The four targets:
> `6092654861665006592` (WG 26), `332248057157474176` (WDJ020915), `2909342818326298112` (WDJ060042), `5612039087715504640` (UCAC4 313).

### Step 0 — Confirm DR4 schema + access (first 30 min)
1. Check the DR4 TAP endpoint is live (`gaiadr4.*` tables in the Gaia archive TAP). Pull the DR4 datamodel for the new epoch/transit tables — names not yet final as of pre-registration; expect something like `gaiadr4.astrometric_epoch` (per-transit AL/AC positions), `gaiadr4.epoch_photometry`, `gaiadr4.epoch_rv` / RVS, and the re-derived `gaiadr4.nss_two_body_orbit`. Record the exact table + column names into `/tmp/dr4_schema_2026_12_02.md`.
2. Verify the 12×12 correlation-vector ordering for DR4 NSS (DR3 was `[ra,dec,plx,pmra,pmdec,A,B,F,G,e,P,T0]`); the parsing helper from the 2026-05-31 refinement must be re-validated against DR4.

### Step 1 — Pull the per-candidate DR4 tables (cascade input)
For each of the 4 source_ids, pull and cache to `/tmp/dr4_<name>_2026_12_02.json`:
- `gaiadr4.gaia_source` (updated single-star astrometry, RUWE, AEN, parallax, RV, G/BP/RP).
- `gaiadr4.nss_two_body_orbit` (re-derived **P, e, Thiele-Innes A/B/F/G + full errors + 12×12 corr matrix, significance, F2/goodness_of_fit, inclination if populated**).
- **`gaiadr4` epoch astrometry** (the per-transit time series — the headline new product).
- `gaiadr4` epoch photometry (G + BP/RP) and epoch RV / RVS (esp. for UCAC4 313 at G=13.9 and WDJ020915 at G=16.2).
- The DR4 unresolved-binary / exoplanet catalogue rows if any of the four appear.

### Step 2 — Re-run the v2 cascade on the DR4 NSS rows
- Re-derive a_phot, f(M), M₂(M₁), tier, class through `scripts/streaming/v2_corrected/` (consumer_v2) using the **DR4** NSS row — applying the project's standing corrections: NSS-parallax preference (METHODOLOGY Correction A), K_obs=rv_amplitude_robust/2 (B), F#30 logg fallback, and **F#33 NSS-period-significance** (pull `flags` bit 13). Use the **real M₁** (FLAME/GF21/TIC per source), not the 1.5 default.
- Re-run the **full-TI-covariance Monte-Carlo** (the 2026-05-31 method) on the DR4 correlation matrix → realistic + conservative M₂ budgets. The headline test: **does the conservative budget collapse toward the realistic one** (i.e. do A,G [020915] / F [060042] become constrained)?

### Step 3 — The decisive new analysis: fit the epoch astrometry directly
This is what DR3 could not do. For each candidate:
1. **Single-Keplerian fit** to the DR4 per-transit positions → measure **F2 (goodness-of-fit)**, a_phot, i, P, e, and residual RMS. Compare F2 to the pre-registered threshold.
2. **Non-Keplerian / triple test:** fit (a) single Keplerian, (b) Keplerian + linear+quadratic acceleration, (c) double-Keplerian (inner + outer). Model-select by ΔBIC / F-test. A significant acceleration or 2nd period (>5σ) = the triple signature.
3. **Inclination extraction** (UCAC4 313 especially): solve i from the DR4 Thiele-Innes → M₂(sin i) against the pre-registered curve.
4. **Parallax reconciliation** (WDJ060042): confirm the DR4 joint astrometry+orbit fit resolves the 10.24-vs-12.08-mas tension to one value; re-scale M₂.

### Step 4 — Per-candidate decision tree (apply the pre-registered thresholds)

```
WG 26 (6092654861665006592):
  DR4 single-Kepler F2 ≤ +2  AND a_phot ≈ 5.40 mas (±3σ) AND no accel/2nd-period >5σ
    → CONFIRM clean sub-Chandra DWD (M2≈0.65). [Residual: 1 RV epoch for γ/sin-i — optional.]
  else (accel or 2nd period >5σ, OR F2 > +5)
    → REFUTE → hierarchical triple. Re-classify; drop from DWD list.

WDJ020915 (332248057157474176):   ← highest-information node
  DR4 F2 collapses to ≤ +2  AND a_phot ≈ 7.73 mas (M2 ≥ 1.2) AND no 2nd-period/accel >5σ
    → CONFIRM real M_tot>M_Ch single-companion (M2≈1.3 ±0.1).
       → then companion CLASS (WD vs NS) still open → queue HST/COS FUV.
  elif DR4 2nd-period/accel >5σ
    → REFUTE → triple; M_tot>M_Ch claim void.
  elif refined a_phot drops M2 < 1.2
    → DOWNGRADE → ordinary sub-Ch DWD.
  elif DR4 still F2 > +5 (longer baseline didn't help)
    → PARK (orbit unreliable).

WDJ060042 (2909342818326298112):
  DR4 F2 ≤ +2 AND a_phot ≈ 19.62 mas (±3σ) AND π tension resolved AND no 2nd-period/accel >5σ
    → CONFIRM M_tot>M_Ch single-companion.
       IF refined M2 (±0.05) > 1.40 → super-Chandra COMPANION confirmed.
       IF 1.33 ≤ M2 ≤ 1.40 → Chandra-straddle holds; class (near-Ch ONe WD vs low-mass NS) → HST/COS FUV.
  elif refined M2 < 1.33
    → DOWNGRADE → ordinary sub-Ch DWD.
  elif 2nd-period/accel >5σ
    → REFUTE → triple.

UCAC4 313-025977 (5612039087715504640):
  DR4 measures i:
    sin i ≥ 0.85 (i ≥ 58°)  → CONFIRM substellar (M2 ≤ ~15 M_J BD; planetary if i ≳ 80° → M2 < 13 M_J).
    45° ≤ i < 58°           → BD but heavier (~16–18 M_J); headline holds as "wide-orbit BD".
    i ≤ 45°                 → REFUTE substellar headline → high-mass BD (M2 ≥ ~18–20 M_J).
    i so low that M2 ≥ 0.075 M⊙ → it is a LOW-MASS STAR (fully refuted).
  (Re-evaluate the whole M2 curve at the DR4-refined M1.)
```

### Step 5 — Integrate + record
- Write `/tmp/dr4_reanalysis_<name>_2026_12_02.md` per candidate (DR3 prediction vs DR4 measurement vs threshold → verdict), and a one-page roll-up `/tmp/dr4_reanalysis_summary_2026_12_02.md`.
- Hand to the main thread for CANDIDATES.md / dossier integration (this sub-agent does not edit those).
- For any candidate whose dynamical verdict is CONFIRM but whose **companion class remains open** (WDJ020915, WDJ060042): the action item is **HST/COS FUV**, not more astrometry — flag explicitly so the post-DR4 plan does not chase a degeneracy DR4 structurally cannot break.

### Pre-registration audit hooks (so the test is honestly falsifiable)
- The thresholds above (F2 ≤ +2 confirm / > +5 refute; a_phot within 3σ; 2nd-period/accel > 5σ; sin i ≥ 0.85 substellar / i ≤ 45° refute; M₂ < 1.33 NS-floor downgrade; M₂ > 1.40 super-Chandra companion) are **fixed as of 2026-06-01** and must not be moved after seeing DR4.
- The DR3 anchor values to beat: WG 26 (a_phot 5.40, i 77.1°, F2 −1.11); WDJ020915 (a_phot 7.73, F2 +8.39, RUWE 8.79); WDJ060042 (a_phot 19.62, i 66.4°, F2 +0.79, π 10.24 vs 12.08); UCAC4 313 (a_phot 1.32, e 0.214, i undetermined).
- Provenance: `docs/dossiers/{WG26,WDJ020915+380425,WDJ060042-293041,UCAC4_313-025977}_DOSSIER_2026_05_28.md`; `/tmp/wd_sed_mass_refinement_2026_05_31.md` (purged from /tmp — **regenerated and REPRODUCED 2026-06-10**: `docs/reports/wd_ti_mc_regen_2026_06_10.md`); `data/derived/main_hunt_derived_v2_relaxed_M1corrected.parquet`. DR4 content: [ESA Gaia DR4](https://www.cosmos.esa.int/web/gaia/dr4), [ESA release scenario](https://www.cosmos.esa.int/web/gaia/release).

---

## Addendum B (2026-06-10) — conventions clarification + mass-MC provenance (frozen thresholds untouched)

1. **NS-floor convention.** The 2026-06-01 thresholds use *per-candidate* floors — WDJ020915 downgrades at M₂ < 1.2 M⊙, WDJ060042 at M₂ < 1.33 M⊙. These are intentional (set by each candidate's posterior position vs the NS mass range), remain frozen, and the difference is hereby recorded as a convention, not an error. Any DR4-day verdict must quote the candidate's own floor.
2. **WDJ020915 knife-edge procedure (mandatory).** The 2026-06-05 refit-engine finding (RESEARCH_LOG #116): the bare f(M) at the pre-reg anchors gives M₂ = 1.223, ON the 1.2 floor — ~1-in-7 noise realisations land on DOWNGRADE even with a perfect orbit. **On DR4 day, run the full-Thiele-Innes-covariance MC, never the bare inversion**, for this candidate.
3. **Mass-anchor provenance restored.** The 2026-05-31 full-TI-covariance MC artifact this document cites was purged from /tmp. Re-derived 2026-06-10 from `gaiadr3.nss_two_body_orbit` + `corr_vec` (200k draws, the vetted `refit/model.py` chain): WDJ020915 M₂ = 1.322 [1.267–1.379], P(M₂>1.4) = 8.7% (anchor 8.6%); WDJ060042 M₂ = 1.368 [1.229–1.521], P(M₂>1.4) = 41.4% (anchor 41%) — **both REPRODUCED**. Committed artifact: `docs/reports/wd_ti_mc_regen_2026_06_10.md` (+ `.csv`).

## Addendum A (2026-06-10) — pre-registered thresholds for the remaining roster objects

> **Dated addendum, fixed before the DR4 drop.** The 2026-06-01 thresholds for the 4 original candidates are **untouched and remain frozen**. This section extends the same discipline to the 5 remaining roster objects (closing the coverage gap found by the 2026-06-10 project review — which also found RESEARCH_LOG #122 calling the HD 157033 DR4 play "pre-registered" when it was not; it is, as of this addendum). Same engine and statistics throughout: `scripts/dr4_pipeline/refit` (ΔBIC > +10 strong / accel-SNR > 5σ significant; F2 ≤ +2 clean / > +5 unreliable), the full-TI-covariance MC, the F#33 period-significance flag. DR4 baseline 66 months ≈ 2008 d.
>
> **Threshold provenance:** anchor values below are taken from the journals/dossiers; thresholds marked **[new 06-10]** are proposals first registered today (not derived from a prior doc) — still frozen as of this addendum date.

### A.1 Gaia DR3 3155543945892767232 — the period-reality test (bit-13)

Anchors (journal/dossier): AstroSpectroSB1 P=543.27±4.56 d, e=0.089±0.045, sig=40.74, a_phot=0.980 mas (MC 0.90/1.16/1.48), K₁≈15.47 km/s, γ=37.38±0.91 km/s, M₂≈1.26–1.6; **NSS flags bit 13 set** — so the first DR4 question is *is the 543-d period real*. External corroboration only 2 LAMOST phases / 2.66σ (re-confirmed current 2026-06-10: no new public epochs; LAMOST DR12 login-gated). DR4 covers ~3.7 cycles.

- **CONFIRM period + orbit:** DR4 NSS (or epoch-astrometry re-fit) returns P within 3σ of 543.27±4.56 d **with a significant period** (DR4 analogue of bit 13 NOT set) AND F2 ≤ +2 AND a_phot within 3σ of 0.980 mas AND no accel/2nd-period > 5σ. **CONFIRM NS-mass band** additionally if DR4 epoch RVs (G=12.3, well inside RVS) give K₁ = 13–18 km/s with γ within 3σ (bands repurposed from the dossier's ground-RV outcome table **[new 06-10 as DR4-RV thresholds]**).
- **REFUTE:** no significant DR4 period / P shifts > 5σ / F2 > +5 → period-search artifact, park. **DOWNGRADE → WD:** K₁ = 8–13 km/s; falsified if K₁ < 5. Accel/2nd-period > 5σ → triple.
- **DR4 cannot decide:** WD-vs-NS class at M₂≈1.3 (K₁ identical for both) — FUV/telescope-gated.

### A.2 Gaia DR3 5858574810404752256 — triple-vs-compact at the calibrated boundary

Anchors: Orbital P=506.14±2.80 d, e=0.542±0.047, sig=20.02, a_phot=0.5265 mas, π_NSS=0.5918±0.0129, f(M)=0.3667, M₂=1.48 [1.34–1.74] at adopted M₁=1.5±0.3 (StarHorse 1.80); Shahaf-calibrated P(compact|A,M₁)=0.21–0.35 — **TRIPLE for M₁ ≥ 1.55**; RUWE 1.96; no archival RV; WATCH-LIST (triple-favored).

- **REFUTE → hierarchical triple:** DR4 epoch astrometry prefers accel/2-body at ΔBIC > +10 or accel-SNR > 5σ.
- **CONFIRM compact-channel:** DR4 single-Keplerian F2 ≤ +2 AND a_phot within 3σ of 0.5265 mas AND no accel/2nd-period > 5σ, AND recomputed P(compact|A,M₁) at the DR4 values ≥ 0.5 **[new 06-10: the 0.5 line is the Shahaf-convention complement of the anchored 0.35 boundary]**. P(compact) ≤ 0.35 at DR4 M₁ → triple-favored verdict STANDS; 0.35–0.5 → still ambiguous. M₁ is the lever.
- **Auxiliary:** SB2/SB3 signature in DR4 RVS epochs, or K₁ inconsistent with the DR4 inclination, → triple.
- **DR4 cannot decide:** a *tight* inner MS pair gives the same single outer Keplerian — if clean AND P(compact) lands 0.35–0.5, the split stays spectrum/RV-gated. WD-vs-NS likewise.

### A.3 Gaia DR3 1593152388271709824 — the GoF stress case + predictive RV orbit

Anchors: Orbital P=597.36±3.61 d, e=0.404±0.027, sig=104.54 (highest of roster), **GoF F2=+9.70 (stress case)**, a_phot=1.952 mas, π_NSS=2.1307±0.0160 (vs gaia_source +4.05σ), RUWE 5.44, M₂=1.27±0.04 at M₁=1.40; archival 4-epoch NSS-locked K₁=17.49±5.93 (only ~3σ), γ=−22.80±2.89; MSC luminous-pair demotion risk (logposterior 684.8). Next periastron (predicted ~30 km/s swing) MJD 61658 = 2027-09-09 — **outside the DR4 data window (ends 2020)**. DR4 covers ~3.4 cycles.

- **CONFIRM:** DR4 single-Keplerian **F2 collapses from +9.7 to ≤ +2** AND a_phot within 3σ of 1.952 mas AND no accel/2nd-period > 5σ → M₂=1.27±0.04 stands. **CONFIRM 2-channel** additionally if DR4 epoch RVs (G=11.30; DR3 has_rvs=False — DR4's fainter RVS limit expected to add epochs) detect K₁ at > 3σ within 2σ of 17.49±5.93, γ within 3σ.
- **REFUTE → triple:** accel/2nd-period > 5σ. **PARK:** DR4 still F2 > +5. **DOWNGRADE → MSC luminous pair:** DR4 epoch RVs give K₁ < 6 km/s at > 3σ **[new 06-10: ≈2σ below central K₁]**, or DR4 RVS shows line-doubling.
- **DR4 cannot decide:** WD-vs-NS at M₂≈1.27; the definitive periastron K₁ (2027-09-09) stays a ground-RV epoch.

### A.4 HD 157033 / Gaia DR3 4111149395881722496 — the partial-arc acceleration prediction (no DR3 NSS)

Anchors: A9/F0 (M₁=1.60±0.20, d=293.4 pc), no DR3 NSS row (P≈5–20 yr, nominal 10), RUWE=0.849; HGCA χ²=1583 (|ΔPM|=2.350±0.085 mas/yr), Kervella snrPMa=14.85 (dVt=3.15±0.13 km/s, PA 303.2°±1.5°, face-value M₂_5AU=0.45), rv_amplitude_robust=16.305 km/s (≈2K₁, not clean). Mass AMBIGUOUS 0.4–6 M⊙. ESO raw archive: **zero archival spectra (verified 2026-06-10 with positive control)**. At P≈10 yr the 66-month DR4 window is a ~55% arc → **the pre-registered prediction is curvature (acceleration), not a closed orbit**.

- **CONFIRM companion (astrometric):** DR4 publishes an acceleration (7/9-param) or long-period Orbital NSS solution at > 5σ — equivalently refit accel-SNR > 5 on DR4 epoch astrometry — with the acceleration PA consistent with the Kervella PMa (303.2°±1.5°). Corollary: DR3 RUWE=0.849 must rise with the longer baseline if the PMa is orbital.
- **Mass branch (only if DR4 epoch RVs deliver; G=9.95):** K₁ ≥ 15 km/s → BH-class candidate; 5–10 → NS/massive-WD band; 2–5 → **DOWNGRADE to M-dwarf** (Kervella face value); peak-to-peak < ~2 km/s over the DR4 span → rv_amplitude_robust spurious **[new 06-10: the <3σ refute floor and 2 km/s flatness line]**.
- **REFUTE:** no DR4 acceleration (accel-SNR < 3) AND flat DR4 epoch RVs → the PMa interpretation fails for P ≤ ~20 yr; park.
- **DR4 cannot decide:** if P ≈ 10–20 yr the arc does not close — P, e, M₂ stay degenerate (acceleration gives M₂(P) only); M-dwarf-vs-BH likely still needs one clean ground RV + the DR5 baseline. A hierarchical-triple reading is not excluded by an acceleration alone.

### A.5 Object B / Gaia DR3 3161546596480983040 — astrometry testable, subtype not

Anchors: plx=1.166±0.218 (5.34σ), pmdec=−8.176±0.225 (36σ), RUWE 1.159, M_G=8.75 [8.32–9.17], G=18.62, d_BJ≈944 pc; eRASS1 favoured ID (P≈0.8), Lx≈3.6e31; blended with the 4.76″ G=13.8 neighbour (ZTF cannot isolate it, #113); **subtype spectrum-gated**. 2026-06-10 sweep: GALEX = coverage gap; XMM/Chandra never pointed here; DASCH 1889–1989 = no nova-scale outburst (blend floor hides dwarf-nova-scale).

- **CONFIRM Galactic + distance scale:** DR4 parallax within 3σ of 1.166±0.218 AND still > 5σ; pmdec within 3σ; RUWE stays < 1.4 **[new 06-10: conventional cut]**. This locks the subluminous-blue gap locus.
- **REFUTE (re-open extragalactic/artefact):** DR4 parallax consistent with 0 at < 3σ, or the solution degrades (RUWE > 1.4 with AEN_sig ≫ 2 without an NSS solution → blend/systematic suspect).
- **Support channels (pre-registered as support, NOT confirmation):** DR4 epoch photometry (first un-blended light curve of the blue star): outburst ≥ 1 mag, eclipses, or a period at permutation-FAP < 1% → accretor/close-binary support; a null is inconclusive at G=18.6 **[new 06-10]**. has_xp_continuous flipping True → XP continuum Teff for the WD-vs-composite split. A DR4 NSS/epoch-RV entry (unexpected at this G) would be decisive for binarity.
- **Honesty clause:** the subtype (CV / pre-CV / WD+dM / ELM) **remains telescope-gated** — DR4 can *refute* (kill the parallax) but can only *strengthen, never confirm*, the accretor claim. The ~20% X-ray-ID ambiguity closes only with Chandra/XMM or a spectrum.
