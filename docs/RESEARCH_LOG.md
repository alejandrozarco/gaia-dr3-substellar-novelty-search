# Research log — project lab notebook

A chronological record of **lanes explored, sidesteps, iterations, and lessons**
across the whole project — so we never silently repeat a dead lane, lose an
"insight catalog," or forget a previous iteration. Per-*object* history lives in
`docs/object_journals/<source_id>.md`; this file is the per-*project* history.

> Context: solo, AI-assisted hobby project, begun ~mid-May 2026. This is the
> notebook for the search campaign, not a claim of a long program.

**Append-only.** Add an entry whenever a lane is opened, advanced, iterated, or
closed. Newest at the bottom of each section. Status tags: `OPEN` /
`PROMISING` / `PARKED` / `NULL` / `SUPERSEDED` / `INFRA`.

---

## Lane & iteration index

| date(s) | lane / activity | outcome | detail |
|---|---|---|---|
| ~05-12 → 05-27 | Gaia DR3 NSS dormant-compact cascade (v1) + repo | built | README, `scripts/streaming/` |
| 05-27 | repo recovery + v1.17.0 | done | — |
| 05-28 | v1 → **v2 cascade corrections** (NSS parallax, K_obs/2, F#30 logg) | SUPERSEDED v1 | `docs/METHODOLOGY.md` |
| 05-28 | **Retractions** (CRTS J051419 CV period/eclipse; mass-gap-BH sin-i inflation) | NULL/corrected | release v2.1.0; CANDIDATES.md retraction table |
| 05-28 | Per-target dossiers (17) | built | `docs/dossiers/` |
| 05-28 | **Triple-vs-compact** realisation — Shahaf AMRF | insight | most Tier-1 NS are hierarchical triples, not single compact objects |
| 05-29 | HD 264291 — independent RV confirmation (heavy NS M₂≈1.94) | known (Shahaf) | the one compact-favoured survivor; not novel |
| 05-30 | Substellar novelty cross-check | corrected | UCAC4 313 = novel; APMPM J0710 / SCR J1441 = already published |
| 05-31 | **Inclination Thiele-Innes cos i sqrt bug** fixed (6 sites/3 scripts) | corrected | biased spectroscopic M₂ high; pre-fix outputs stale |
| 05-31 | WD-binary **framing correction** (NOT super-Ch WD / NOT Type-Ia progenitor) | corrected | WDJ020915/060042: M_tot>M_Ch split between two bodies |
| 05-31 | Self-lensing search | PARKED | — |
| 05-31 | eRASS1 v1 → **v2** (multi-catalogue gate, high-PM J2000 propagation) | NULL | 671 known / 137 uncatalogued / 0 outburst-confirmed-new |
| 06-01 | **Fresh-lane sweep**: XP-pilot, hyper-v WD, eRASS1, bulge-symbiotic, spectral-diff, IR-nova | all NULL | 0 confirmed novel across every archival lane |
| 06-01 | **XP-at-scale** feasibility milestone | NO-GO | artifact-swamped, structurally blind, crowded field |
| 06-01 | **DR4 pre-registration** (falsifiable confirm/refute thresholds) | built | `docs/dr4_preregistration_2026_06_01.md` |
| 06-01 | **Occurrence upper limit** (Poisson rule-of-3) | result | f < 5.7×10⁻⁵ (95% CL) in the searched regime; `/tmp/occurrence_limit_2026_06_01.md` |
| 06-01 | Known-object **front-filter** (6104 objects, source_id-keyed) | built | `scripts/known_objects/` |
| ~06-01 | Hunt console (live dashboard + dossier viewer) | built | `scripts/web_tool/hunt_console/` |
| 06-03 | **Object-journal + research-log system** | built | this file + `docs/object_journals/` |
| 06-03 | UCAC4 313 "Shahaf recovery" claim | corrected | compaction error; it is NOT in Shahaf — see its journal ledger |
| 06-03 | **Project-wide re-vet** (5 agents, all files+history) | audit — null robust | 1 orphan (TYC 7350-249-1); front-filter blind-spot closed (#109, 26 pool objs = published AMRFClassIII); #101/#102 = INFRA-NULLS (untested); 5858574 soft demotion |
| 06-05 | **Field-status / prior-art screen** (cross-survey lanes vs the literature) | lesson + tool | multi-survey fusion is the field's dominant paradigm; #114/#115 + SN-runaway + anomaly ideas are all published 2024–26 (Rodriguez+25 eRASS1×Gaia×ZTF; COBIPLANE & ZTF×4FGL spiders; high-v X-ray 2026; SNAD). Built `scripts/litcheck/prior_art.py` + prior-art gate (CLAUDE.md) |
| 06-05 | **Cross-survey quiescent-XRB lane** (Gaia NSS dark-companion pool × eRASS1-DE), widened from #34 | NULL → park | 6468-source pool, 110 eRASS1 matches (1.70%); all coronal (log fx/fopt ≤ −2.09; max Lx 8.2e30); 0 compact accretor; `/tmp/gaia_xray_quiescent_2026_06_05.md` |
| 06-05 | **DR4 day-one: blind re-hunt harness** (#117) | built | `scripts/dr4_pipeline/rehunt/`; science imported not forked; DR3 dry-run reproduces roster exactly (0/56,100 tier mismatches); found input-staleness — raw chunks lack `flags`, committed v2 parquet is M1-stale → diff DR4 against `_M1corrected` baseline |
| 06-05 | **DR4 day-one: candidate re-fit engine** (#116) | built | `scripts/dr4_pipeline/refit/`; epoch-astrometry orbit fitter + 1-body-vs-multi-body (ΔBIC/F-test/accel-SNR/F2); pre-reg thresholds wired + doc-cross-checked; 8 synthetic tests pass (0% false-triple, 72% 2-body detection); **WDJ020915 knife-edge: bare f(M) M2=1.223 on the 1.2 floor → use full-TI MC on DR4 day** |
| 06-05 | **Odd-axis D: PMa × RV-trend** (#122) | NO-GO (duplicate) | already done in-repo both flavors — Pile-A HGCA (HD 157033 + 7 demoted) + acceleration_v3 (16,949 srcs, 6,828 dual-signal, 3,761 RV-demoted); inclination/period degeneracy + telescope-gated → DR4 play. arXiv gate 429 (flagged) |
| 06-05 | **Odd-axis F: IR-variability × astrometry** (#124) | NO-GO (structural null) | NSS G<13 cap vs dusty-symbiotic G~13-16 disjoint; 0/2,330 unsaturated red NSS giants W1−W2>0.2; 13 raw hits all WISE-saturation artifacts; adds ~nothing over IR-nova/bulge parks → DR4 (fainter) play. arXiv gate 429 (flagged) |
| 06-05 | **Odd-axis B: variability-phase × orbit-phase** (#120) | NO-GO discovery / GREEN self-audit | not novel (Holl+2023a/b + DPAC already filter spurious-period artifacts) AND inoperative — P_orb median 585d vs P_phot median 1.9d (disjoint, max ratio 0.22); BUT confirmed all 16 candidates photometrically quiet (0/16 VARIABLE) → clean self-audit. arXiv 429 → WebSearch |
| 06-05 | **Cross-survey Fermi-spider hunt** (#114; 4FGL-DR3 × eRASS1-DE × Gaia) | NULL → park (pipeline validated) | 2154 unassoc 4FGL → 733 in-ellipse eROSITA → 384 γ+X+optical pairs → 0 novel spiders; positive control PASSED (12 known PSR / 5 SpiderCat, incl. full J0639 redback triple); survivors all known CV/YSO/EB + chance alignments (count tracks stellar density); eastern Galactic plane uncovered → eROSITA-east. 2 CV recoveries → register |
| 06-05 | **Odd-axis G: Galactic kinematics × companion mass** (#125; demographics, no new object) | NULL/anti-signal → **GO as limits-paper box** | UVW+Toomre: 641 compact-favoured + 149 Tier-1 vs 53,659 stellar-companion NSS binaries (Sahlmann orbit parent, 87% real RV). Compact pool kinematically COLDER/thin-disk, NOT hotter: thick+halo 0.9% vs 3.8% (Fisher p=1.5e-5); survives dist/mag/colour matching (KS p=2e-6) → independent kinematic corroboration of the contamination/triple null → supports f<5.7e-5. arXiv gate 429. `/tmp/lane125_*` |
| 06-05 | **Odd-axis C: GALEX UV × astrometry** (#121) | NO-GO discovery / GO as vetting add-on | published (Makarov 2017; Shahaf+2023 Triage II; Garbutt/Parsons+2024). Candidate re-test: WDJ060042 UV excess +0.4σ → STAYS compact-compatible; WDJ205650 (known He+He DD) +9.2σ = positive control; WDJ020915 no detection. 0 novel → add a standing UV-excess screen to the deep-dive workflow |
| 06-05 | **Odd-axis H: "absence"-as-selection** (#126; eRASS1 → Gaia, no-binarity + faint/blue + high fx/fopt) | NO-GO (hard) | premise self-defeating (true INS are V≳25, below Gaia → an optical counterpart selects AGAINST INS; XDINS controls RX J1856/J0720 have no real Gaia source) + cut selects AGN (8/8 full-cut survivors PQSO=1.0; 50/67 X-ray-loud extragalactic) + published (Kurpas+2024, 33 XDINS cand). Store has no AGN catalog → can't gate novelty here. `/tmp/iso_compact_lane126_2026_06_05.md` |
| 06-05 | **Odd-axis I: mine the Gaia QSOC/DSC rejects** (#127; Object B generalized) | NO-GO | the rejects ARE the Gentile-Fusillo Gaia WD catalogue (97% already-known WDs, same plx/PM cut); Object B's interest was its eRASS1 X-ray not the reject status; defensible recipe collapses to the NULL #115 lane + a completeness-shrinking pre-filter; published both ways (CatNorth/Quaia purification; GF21 recovery). arXiv 429. `/tmp/lane127_*` |
| 06-05 | **Odd-axis E: asteroseismology × astrometry** (#123) | NO-GO / NULL (yield-starved) | seismic M1 IS new info (19 pool overlaps all had M1=default 1.5; median M_seis 1.59) but companions stay stellar — max min-M2=1.97 (already demoted), 0 compact; yield ceiling ~46 systems (Kepler×all-sky-NSS overlap tiny); established niche. Best residual use = consistency check on existing candidates. arXiv 429. `/tmp/seismic_nss_lane123_report.md` |
| 06-05 | **Odd-axis A: chemistry × astrometry** (#119; Ba/CH × Gaia NSS) | NO-GO / PARKED (feasible, not novel) | 437 Escorza Ba/CH → 60 with NSS orbits, 25 AMRF-derivable; companion masses 0.31-0.84 M⊙ (median 0.60 = textbook CO WD), nothing >1.0 → physically confirmatory but sample+objects+method all published (Escorza/Jorissen WD-mass dists of THIS sample; Shahaf AMRF); Gaia P matches literature → AMRF-pipeline validation. arXiv 429. `/tmp/lane119_FEASIBILITY_REPORT.md` |
| 06-05 | **Astrometric microlensing predictor** (#118) | BUILT + VALIDATED; candidate cross NULL | `scripts/microlensing/` (geometry/predict/validate/apply + 13 tests); reproduces LAWD 37 (θ_E 31.4 vs 32.8 mas, TCA exact, mass→0.61 M⊙; fixed a 2× parallax-factor bug); 12 candidates as lenses → NULL (low-PM distant); WD-lens flagging works. Method-validation + DR4-ready tool, NOT novel — isolated dark lenses are Rubin-monitoring-gated (can't pre-target the unseen) |
| 06-09→06-10 | **Full project review** (5 repo audits + 8 ideation lenses → 36 ideas → 12-lane shortlist → adversarial verify + second skeptic) | 4 GO lanes; debt list; NO-GO ledger | `docs/reports/project_review_2026_06_10.json` (full verdicts + prior-art refs); detailed entry below |
| 06-10 | **F#33 → corrected-tier propagation** (review debt item) | FIXED | 41 main + 4 relaxed corrected-Tier-1 NS carried bit-13 FLAG → new `tier_v2_corrected_f33` column: Tier-1 NS 148→**107** (main), 13→**9** (relaxed), roster = **116**; `scripts/apply_f33_to_corrected_tiers_2026_06_10.py`; DR4 rehunt must diff on this column |
| 06-10 | **WD full-TI-covariance MC regeneration** (deleted /tmp provenance restored) | REPRODUCED | WDJ020915 M₂=1.322 [1.267–1.379], P(>1.4)=8.7% (anchor 8.6); WDJ060042 1.368 [1.229–1.521], P(>1.4)=41.4% (anchor 41); corr_vec used; `docs/reports/wd_ti_mc_regen_2026_06_10.md` |
| 06-10 | **Phase-2 archival sweep** (eRASS1 / GALEX / 4XMM / CSC / 2SXPS / DASCH / LAMOST-DR11+DR12 / SDSS-V DR19 / ESO raw) on 6 roster objects | logged (14 ledger rows) | Object B: GALEX = **coverage gap** (UV unconstrained — dossier S3 superseded), XMM/Chandra = no-coverage, DASCH = no nova-scale outburst 1889–1989; WDJ060042+WG 26 eRASS1 NULL; no new RV epochs (1593152, 3155543; DR12 login-gated); HD 157033 ESO archive = zero spectra (positive control verified) → confirmed telescope-gated. `docs/reports/phase2_archival_checks_2026_06_10.md` |
| 06-10 | **DR4 prereg Addendum A+B** (5 remaining roster objects + floor convention + WDJ020915 MC mandate) | built — coverage now 9/9 | `docs/dr4_preregistration_2026_06_01.md` addenda; corrects #122's false "(pre-registered)" claim — HD 157033 is pre-registered only as of A.4 |
| 06-10 | **Register backfill** (#109 AMRFClassIII 25 rows; relaxed Tier-1 NS 13 rows incl. 8 never-logged) | done | `findings_register.csv` → 1,997 rows; per-object 2026-05-28 triage verdicts unrecoverable (/tmp purged) — logged as triaged-in-aggregate |
| 06-11 | **ATLAS forced photometry** — first-ever light curves for Object B + WDJ020915 (10.4 yr o+c) | WDJ020915 QUIET / Object B unmeasurable | WDJ020915: no outbursts, nothing at P_orb=274.5d or P/2 (perm-FAP 0.27–1.0), LS peaks = diurnal/seasonal aliases → variability does NOT explain the F2=+8.39 weak fit (orbit-reality strengthened pre-DR4). Object B: blend with the 4.76″ G=13.8 neighbour dominates the 4″ ATLAS PSF (σ_rob=740 µJy) → only sustained mag≲15 events excluded; discriminator now rests on ZTF ZFPS (user registration pending; probe confirmed email unregistered). LAMOST DR12 NADC validation pending. `docs/reports/atlas_forcedphot_2026_06_11.md` |
| 06-10 | **F#34 astrometric-quality caution flag** (the 05-30 "global RUWE gate" follow-up, retired) | built + gate PASS | `consumer_v2.filter34_astromqual` — flag never cut: F2>+5 / ipd≥4 / RUWE≥12.5. Key finding: Tier-1 RUWE 2.6–28.8 (median 6.1) = normal photocentric-binary signature → absolute-RUWE gate meaningless, orbit F2 is the axis. F2+ipd fetched for 1,251 candidate-tier srcs; 51/108 main + 3/9 relaxed Tier-1 flagged (incl. GALEX J145250 F2=+8.0, HD 75567, HD 264291 caution). Cascade-regression gate: **PASS (conditional)** — 0 behavioral regressions; conditions fixed same-day (stale BH1 + HD 207141 benchmark expectations corrected; HD 207141 journal created incl. a flagged 1.31-vs-1.75 M₂ reconciliation item; Shahaf 49-obj cross salvaged to `docs/reports/tier1_x_shahaf_t1_2026_06_10.csv`; 93% recall claim annotated unverified — truth set never committed). Shahaf gate stat: 9/49 Tier-1 with PIII≥0.5 (median 0.015) — quantitative re-confirmation of the triple-dominated insight |

---

## Net state (as of 2026-06-04)

**0 confirmed novel compact objects across every archival lane.** All methods
validated. Remaining expected value is **XP-at-scale** (a build, highest ceiling)
and **fresh data** (Gaia DR4, 2 Dec 2026; eROSITA-east; Rubin/LSST). Breadth on
existing data is exhausted. Active candidates (all unconfirmed, pending DR4): see
`docs/CANDIDATES.md` + the per-object journals.

**Online re-runs (2026-06-04) — all NULL, now PROPERLY tested** (the two big lanes were never genuinely tested before; the 2026-06-03 attempts were infra-nulls):
- **#101 ELM/sdB + NS/BH** — real test (66k hot subdwarfs × live Gaia NSS with no period floor; short-P ZTF/Gaia photometry; 3 positive controls pass) → **0 novel** sdB/ELM + dark compact companion. Gaia NSS is structurally blind to hours-period sdB orbits → that channel is telescope-gated (RV f(M) needed).
- **#102 ETV compact tertiary** — real test (Borkovits+2016 LTT + Gaia accel/RUWE; controls pass) → **0 novel** compact tertiaries (the "compact" cases drop to ~1–1.5 M⊙ at realistic inner mass); 3 partial-arc systems are DR4 targets.
- **#104 CPM** → NULL (no wide tertiary for WG 26 / WDJ020915 / WDJ060042). **#108** orphan TYC 7350-249-1 → REFUTED. **#110** 5858574 → ambiguous/watch-list (Orbital solution → the inclination bug never applied; NS-mass 1.48, not BH).
- **eRASS1 re-exam** of the 2 top uncatalogued leads → A (5526308…) deflated (reddening artifact); **B = Gaia DR3 3161546596480983040 — uncatalogued blue Galactic compact-object candidate** (Gaia QSOC "AGN" overturned by 5.3σ parallax + 36σ PM); full journal + deep-dive (#112), spectrum-gated + X-ray-ID-ambiguous.

Still pending: **#103** XP-catalogue ingest (network), **#111** bulk-import remaining hunt findings (offline), **#112** Object B deep-dive (running). *(Superseded 2026-06-10: #103/#111/#112 were all completed in commit 7b7c4a2 and #113 in the Object B journal — closure recorded in the 2026-06-10 detailed entry below.)*

**Offline-done 2026-06-03:** #109 front-filter novelty blind-spot closed — 306
in-pool Halbwachs+2023 `binary_masses` AMRFClassIII compact-candidates ingested
into the known-object store (`scripts/known_objects/ingest_binary_masses.py`);
**26 of our candidate pool (incl. 5 Tier-1 NS + 1 Tier-1 BH) are published
AMRFClassIII → not novel**.

---

## Catalogs & insights ledger ("don't lose the sidesteps")

**Catalogs in use** — authoritative list in `CATALOG_DEPENDENCIES.md`; known-object
front-filter contents in `scripts/known_objects/`. Notables: Gaia DR3 NSS
(Orbital / AstroSpectroSB1 / OrbitalAlternative / Acceleration), Shahaf+2023
Triage I (J/MNRAS/518/2991), Gentile Fusillo 2021 WDs, Brandt HGCA, Kervella
PMa, Ritter-Kolb + Downes CVs, Akras 2019 symbiotics, eRASS1-Gaia, LAMOST DR11
(V/162 MRS, V/164 LRS), APOGEE DR17, GALAH, RAVE.

**Insight catalog** (hard-won; the rules the workflows encode):
- **The no-telescope filter** — a lane only pays off if the public archive both
  *finds* AND *confirms*; otherwise it's telescope-gated and parked.
- **Compact ≠ what the cascade says** — the astrometric mass function can't
  separate a single dark companion from a hierarchical triple; defer to Shahaf AMRF.
- **No sin-i inflation** for dark companions — M₂ comes straight from the
  photocentric mass function (the `rv_amplitude_robust/2` error invented fake mass-gap BHs).
- **Single-phase ≠ corroboration** — RV epochs clustered in one MJD window are
  one phase; low χ²/dof on few points is not a detection.
- **Photometry false positives** — outburst-contaminated folds + minimum-of-noise
  depths at S/N<1 manufacture fake periods/eclipses → masked periodograms + permutation FAPs.
- **Known ⇒ not novel via a *multi-catalogue* gate** — never SIMBAD-only;
  cross-match by **source_id** and by **J2000-back-propagated** position (high-PM leak).
- **NSS parallax bias** — single-star parallax is biased low for binaries; prefer `nss_two_body_orbit.parallax`.
- **APOGEE DR17 ASPCAP not yet ingested** — the no-telescope bulge-confirmation route, still open.

---

## Detailed entries

*(Append longer narrative entries here as lanes are worked. Each: date, lane,
what was tried, outcome, lesson, links. Keep the index table above in sync.)*

### 2026-06-03 — Object-journal + research-log system stood up
- **Did:** built `docs/object_journals/` (README/TEMPLATE/INDEX + per-object
  ledgers), this research log, `scripts/journal/journal.py`, `CLAUDE.md`
  instructions, and wired journaling into `.claude/workflows/`.
- **Why:** a context compaction had silently mislabelled UCAC4 313 as a "Shahaf
  recovery" (it is not in Shahaf). Documented, dated, sourced ledgers make such
  claims grep-checkable instead of memory-dependent.
- **Provenance:** tasks #105–#107; session 2026-06-03.

### 2026-06-03 — Project-wide candidate re-vet (5 parallel offline agents)
- **Did:** swept all files + history — demoted/triple-favored pool, Tier-2 +
  uncatalogued objects, parked lanes, all 17 dossiers, and orphaned mentions —
  for any promising candidate dropped along the way.
- **Found (bottom line):** the campaign null is **robust** — no *novel* object
  was prematurely buried; every demotion runs on the bug-immune Shahaf-AMRF /
  RUWE / flux-ratio axes, not the corrected inclination/sin-i route. Four
  actionable items:
  1. **One orphan:** TYC 7350-249-1 (6021285355771958528), an M₂,min=3.36 M⊙
     SB1 BH-candidate computed 2026-05-31 but never logged into the roster.
     Likely deflates (SB1-only = the published-null lane; RUWE=6.99 may be an
     SB2 artifact). Journal created; re-vet queued (#108).
  2. **Front-filter novelty blind-spot — CLOSED (#109):** the known-object
     filter held only CV/symbiotic catalogs, so "absent from the filter" never
     proved novelty for a compact candidate. Ingested 306 in-pool Halbwachs+2023
     `binary_masses` AMRFClassIII compact-candidates; **26 of our candidate pool
     are published AMRFClassIII → not novel**, incl. Tier-1 NS 5446310318525312768,
     5788346533133183744, 4042401027000908928, 6453094358292937984,
     2208943221256515712 and Tier-1 BH 6281177228434199296 — their published M₂
     corroborates the cascade NS-masses. (Per-object ledger rows: with #107.)
  3. **#101/#102 are infra-nulls, not nulls:** the offline runs fell back to
     wrong-regime data (#101 a 100-d period floor vs a minutes–hours target;
     #102 only re-scored old Kepler EBs); the hypotheses were never tested and
     the 2026-06-03 re-attempts re-blocked. Need proper network runs.
  4. **5858574810404752256** — the one genuinely-novel former compact prospect;
     demotion sits on the triple/ambiguous boundary and used pre-bugfix math.
     Journal created; post-fix regeneration queued (#110).
- **Minor:** CANDIDATES.md:100 over-generalises "all triples" (false for ~12
  known Shahaf-PIII>0.5 objects, all known); HD 264291's M₂=1.94 rests on the
  bugfix but was regenerated by the fixed script (bias-direction safe).
- **Provenance:** session 2026-06-03; tasks #108–#110;
  `scripts/known_objects/ingest_binary_masses.py`.

### 2026-06-05 — Field status: multi-survey fusion is the dominant paradigm; prior-art gate added
- **Did:** after deciding to lean into "combine surveys to find what single surveys miss," ran a
  literature check (arXiv + web) on the cross-survey ideas in flight.
- **Found:** the thesis is correct — and *crowded*. Every cross-survey lane we queued/proposed maps
  onto a funded team's 2024–26 paper:
  - Gaia×eROSITA×ZTF accretors (our #115; the Object-B recipe) = Rodriguez et al. 2025, eRASS1
    (arXiv:2505.10478) — the identical 3-step selection.
  - SN-runaway + X-ray = "high-velocity X-ray sources in the Gaia era" (arXiv:2601.02287, Jan 2026).
  - Fermi-unassociated × multiwavelength → spiders (our #114) = COBIPLANE + ZTF×4FGL searches
    (e.g. PSR J1544−2555, arXiv:2509.09605); Fermi has enabled 62/84 of known spiders.
  - Multi-modal anomaly detection = SNAD/PineForest + AHA on the ZTF alert stream — and they hit our
    exact artifact wall (~68% non-astrophysical), confirming the XP-pilot NO-GO lesson.
  - Rubin/LSST is live (first alerts 24 Feb 2026, ~800k/night); the broker fleet (ALeRCE, ANTARES,
    Fink, …) *is* industrialized multi-survey fusion.
- **Lesson:** these lanes are **method-validation, not novel discovery** — benchmark any candidate
  against the published lists, not just SIMBAD. Solo novelty stays in the **occurrence limit** + the
  **self-auditing methodology**, not the object hunts.
- **Built:** `scripts/litcheck/prior_art.py` (stdlib arXiv prior-art screen) + a **prior-art gate**
  (CLAUDE.md / workflows README) — the method-level twin of the object-level "known ⇒ not novel"
  gate: run it before opening any new lane.
- **Provenance:** session 2026-06-05; refs above.

### 2026-06-05 — Cross-survey quiescent-XRB lane (#115) — NULL (widened from #34)
- **Did:** cross-matched the full Gaia NSS dark-companion pool (6468 non-demoted Tier-1/2 with
  M2_central>1 M⊙: 366 v2 robust-orbital + 6102 v3 acceleration) to eRASS1-DE (J/A+A/682/A34) at 5″,
  PM-propagated to 2019.96; coronal-saturation-ceiling test on every X-ray match.
- **Found:** **110 matches = 1.70% X-ray-detected fraction.** All 110 have log fx/fopt ≤ −2.09
  (textbook coronal; median −3.16); max Lx = 8.2e30 erg/s (below the 1e31–1e34 quiescent-XRB range).
  Only 3 nominally exceed Lx/Lbol=1e-3 (by ≤1.4×) and **none has a robust or compact mass floor** (all
  acceleration-channel, M2_min≈0.12). The 14 robust-orbital matches (incl. all Tier-1 NS) sit far below
  the ceiling. Known recovery: 3160943617433900672 = RX J0702.0+1257 (XB*, K0IV-Ve+DA — WD companion;
  high M2 is a period-degeneracy artifact). **NULL — no quiescent compact accretor.** New vs #34:
  overlap 1/110 → 109 newly X-ray-screened. Caveat: eRASS1-DE covers only the western Galactic
  hemisphere, and a *truly* dormant object is X-ray-silent — this lane tests only the faint-accretion
  hypothesis.
- **Logged:** 109 coronal-null matches → findings_register.csv (lane "eRASS1×NSS quiescent-XRB
  widened"). No source met the deep-dive bar.
- **Provenance:** task #115; `/tmp/gaia_xray_quiescent_2026_06_05.md`.

### 2026-06-05 — DR4 day-one blind re-hunt harness (#117) — built
- **Did:** built `scripts/dr4_pipeline/rehunt/` (adapter.py, rehunt.py, diff.py, test_rehunt.py, README.md) — a thin wrapper that re-runs the v2 cascade on a new NSS table and diffs candidate tiers vs a DR3 baseline by source_id. Science is IMPORTED from `scripts/streaming/v2_corrected/consumer_v2.py` (derive_row_v2 + all 5 filters), never forked; the harness only does column-mapping (DR3-raw / DR3-derived / DR4-stub profiles; a_phot from Thiele-Innes) + the tier diff (NEW/PROMOTED/DEMOTED/VANISHED/mass+period movers). Pointing at DR4 = fill `adapter.PROFILES['dr4']` with the real DR4 column names.
- **Found:** DR3 dry-run reproduces the roster EXACTLY — 0 tier mismatches / 56,100 rows, max|ΔM2|=0, Tier-1 NS+BH 199→199 (regression sanity PASS); repo suite still 50/50. Surfaced an INPUT-STALENESS nuance (not cascade bugs): (1) the raw producer chunks lack the NSS `flags` column (F#33 added 2026-05-31, after the 2026-05-27 chunks) → F#33 no-ops there and ~51 demoted sources spuriously re-surface as Tier-1; (2) the committed plain `main_hunt_derived_v2.parquet` was written with M1 fixed at 1.5 (predates select_m1/FLAME) → a faithful re-run re-tiers ~half the pool (~17.2k mass-movers); the M1-corrected roster is `main_hunt_derived_v2_M1corrected.parquet`. → For DR4: ensure the export carries `flags`, and diff against the `_M1corrected` baseline.
- **Provenance:** task #117; `scripts/dr4_pipeline/rehunt/`.

### 2026-06-05 — DR4 candidate re-fit engine (#116) — built
- **Did:** built `scripts/dr4_pipeline/refit/` (model/modelselect/prereg/synth/adapter/run + README; 8 files, stdlib+numpy/scipy/astropy). Re-fits a candidate's photocentric orbit directly from DR4 per-transit along-scan astrometry; 1-body vs multi-body (acceleration / double-Keplerian) via ΔBIC + nested F-test + accel-SNR + Gaia F2; pre-registered confirm/refute thresholds transcribed into PREREG with a doc cross-check asserted in tests. Reuses the vetted a_phot + **cos i=|AG−BF|/a² (no sqrt — the 2026-05-31 bugfix)** + f(M) chain. DR4 column names isolated to one adapter map (the only stub).
- **Found:** 8 synthetic tests pass — clean 1-body → 'single' (0% false-triple over 25 seeds); 2-body (274d inner + ~1300d outer) → 'multi' (ΔBIC≈+3850, accel-SNR~69σ, both periods recovered; 72% detection power). Per-candidate wiring verified on the 4 anchor orbits (CONFIRM in headline-true world; triple-injection → REFUTE; HST/COS-FUV auto-flagged for WD-vs-NS-degenerate cases). **Skeptical finding: WDJ020915 is a knife-edge — the bare f(M) at the pre-reg anchors gives M2=1.223, on the 1.2 M⊙ NS floor; ~1-in-7 noise realisations land on DOWNGRADE even with a perfect orbit → on DR4 day run the full-TI-covariance MC, not the bare inversion.**
- **Provenance:** task #116; `scripts/dr4_pipeline/refit/`.

### 2026-06-05 — Odd-axis D: PMa × RV-trend (#122) — NO-GO (duplicate of existing work)
- **Did:** feasibility + prior-art scout for "Hipparcos-Gaia PMa × long-term RV linear trend → massive dark companion at 5-50 AU." (arXiv prior-art gate FAILED — 2× timeout + 429 — FLAGGED could-not-run; verdict rests on the solid internal-duplication half.)
- **Found:** already executed in-repo in BOTH flavors. (A) Literal: the Pile-A HGCA BH-class family — HD 157033 (4111149395881722496, χ²=1583, Kervella snrPMa=14.85, P≈5-20 yr → AMBIGUOUS 0.4-6 M⊙) + 7 sibling demotion scripts (7/8 → luminous stellar); 0 confirmed compact. (B) Systematic: `acceleration_v3.parquet` (16,949 srcs) already computes joint acceleration+RV mass+inclination; 6,828 dual-signal; 3,761 RV-demoted; surviving high-M₂ are period-degenerate artifacts (i pegged 90°) → never promoted.
- **Verdict:** NO-GO — method-validation, already paid; binding walls = inclination/period degeneracy + telescope-gated confirmation. Carries forward only as a DR4 fresh-data play (pre-registered). Re-confirm arXiv crowdedness when reachable.
- **Provenance:** task #122; `/tmp/lane122_pma_x_rvtrend_scout_2026_06_05.md`.

### 2026-06-05 — Odd-axis F: IR-variability × astrometry (#124) — NO-GO (structural null)
- **Did:** tested the increment over the prior IR-nova / bulge-symbiotic (pure-IR) lanes: join a measured Gaia DR3 NSS orbit with a WISE W1−W2 excess + WISE var flag. Red NSS subsample bp_rp>1.4 (3,576) + 11 candidates → AllWISE XMatch @3″ (99%); saturation/quality scrutiny; Akras2019/store front-filter. (arXiv gate 429×2 — FLAGGED could-not-run.)
- **Found:** raw join = 13 sources (0 known) but **100% WISE-saturation artifacts** (NSS is Gaia-bright G≈6-11 → W1≈3-8 ≪ the W1≈8 saturation onset; K−W3≈0 → no dust). Among the 2,330 unsaturated red NSS giants, W1−W2 centres at −0.03 and **0 reach >0.2** — no symbiotic excess. No candidate shows excess.
- **Lesson:** the join INHERITS the bulge-symbiotic park — the DR3 NSS bright cap (G<13) and the dusty-symbiotic faint regime (G≈13-16) are essentially disjoint. Re-run on DR4 (fainter). Recipe must include a WISE W1≥8 & W2≥7 saturation cut before trusting any excess on bright NSS giants.
- **Provenance:** task #124; `/tmp/lane124_ir_variability_astrometry_2026_06_05.md`.

### 2026-06-05 — Odd-axis B: variability-phase × orbit-phase (#120) — NO-GO discovery / GREEN self-audit
- **Did:** scout the photocentric-artifact validator (P_phot ≈ P_orb harmonic ⇒ possible artifact; mismatch ⇒ real orbit). Gaia TAP: 16 candidates + 1,014 NSS-Orbital×vari-period pairs. (arXiv prior_art 429 on all 4 attempts → substituted WebSearch.)
- **Found:** (prior-art) NOT novel — Holl+2023a/b + Halbwachs+2023 + Bashi+2022 characterise it and DPAC pre-filters scan-angle spurious periods out of nss_two_body_orbit; `gaiadr3.vari_compact_companion` is the constructive flip-side. (feasibility) 0/16 candidates are VARIABLE / in vari_summary → no period to match → NO red flag for any candidate. Population red-flag rate 0.0% (control 0.0%) — STRUCTURAL: P_orb median 585d vs P_phot median 1.9d, max ratio 0.22, 0 pairs in the [0.3,3]×P_orb overlap → harmonic lock geometrically unreachable for our long-period orbits.
- **Verdict:** NO-GO as a discovery lane (not novel + inoperative in our regime); GREEN as a cheap no-telescope SELF-AUDIT — clean null that all 16 candidates carry no photocentric-variability period artifact. Only bites short-P NSS orbits (P≲tens d), which we barely populate.
- **Provenance:** task #120; `/tmp/lane120_report_2026_06_05.md`.

### 2026-06-05 — Cross-survey spider-MSP hunt (Fermi 4FGL-DR3 × eROSITA eRASS1-DE × Gaia DR3) (#114) — NULL (candidate-gated, parked)
- **Did:** pulled 4FGL-DR3 (IX/67; 2154 unassoc), cross-matched eROSITA eRASS1-m within each 95% γ-ellipse (1152 in the western-hemisphere footprint; 733 with an in-ellipse X-ray source), front-filtered ATNF (B/psr) + SpiderCat (J/ApJ/994/8), required a Gaia DR3 faint optical counterpart with significant Galactic PM (anti-blazar), then VSX/SIMBAD/store novelty.
- **Found:** 0 novel spiders. The 238-Fermi / 384-pair candidate set is dominated by chance star+X-ray alignments at low |b| (count tracks stellar density: 189 at |b|<5° → 41 at |b|>20°). The 5 distinctive survivors are all known/ordinary (2 VSX CVs incl. J1528.2-2448 = Gaia 6238744394658069376, 2 YSOs, EBs). POSITIVE CONTROL PASSED: recovered 12 known pulsars / 5 SpiderCat spiders, incl. full source-level recovery of the J0639.1-8009 redback triple (eROSITA J064100.6-801127 + Gaia 5207836863615934080).
- **Insight:** the anti-blazar discriminator that works on Gaia is *significant Galactic proper motion* on a faint counterpart (spider companions pm_snr≈5-36; blazar cores ≈0); a Gaia-variability or high-parallax *requirement* would wrongly reject real distant/faint spiders. Confirmation needs radio/γ pulsation timing → no-telescope filter → park. eRASS1-DE covers only l∈[180,360]; the eastern Galactic plane (best spider sky) is uncovered → re-run when eROSITA-east is public. Consistent with the standing 0-confirmed-novel result. 2 CV recoveries → findings_register.
- **Provenance:** task #114; `/tmp/fermi_spider_hunt_2026_06_05.md`.

### 2026-06-05 — Odd-axis G: Galactic kinematics × companion mass (#125) — NULL/anti-signal → GO as a limits-paper box
- **Did:** derived UVW + Toomre for 641 compact-favoured (NS+BH) + 149 Tier-1 vs 53,659 stellar-companion NSS binaries, from the local Sahlmann gaia_source_astrometric_orbits parquet (169k NSS, 87% real Gaia RV; 100% of our hunt present). galpy absent → velocity-space only. (arXiv prior-art gate could-not-run — 429 on all attempts incl. a direct fallback; flagged.)
- **Found:** the naive "compact-companion binaries are kinematically hotter/older (thick/halo, SN-kicked)" hypothesis is FALSIFIED in the OPPOSITE direction — the compact-favoured pool is kinematically COLDER / more thin-disk: thick+halo 0.9% [0.3-1.7%] vs 3.8% (Fisher p=1.5e-5, OR=0.24); σ(Vtot) 25.6 vs 31.7 (KS p=9e-8). Survives a distance/magnitude/colour-matched control (KS p=2e-6). All 4 named candidates with a Gaia RV are thin-disk. Honest reading: the ABSENCE of the high-velocity tail expected for genuine SN-kicked remnants is most parsimoniously a signature that the high-f(M) pool is contamination-dominated (unresolved triples / degeneracy-inflated f(M)) — an INDEPENDENT kinematic corroboration of the campaign null, complementary to the Shahaf AMRF axis.
- **Verdict:** GO — fold the demographics box into the limits/methods paper (a second, citable, no-telescope, no-new-object argument that the Tier-1 pool is contamination-dominated → supports f<5.7e-5, with a falsifiable DR4 prediction: real DR4 remnants should populate the high-Vtot tail). General method not novel; the modestly-novel piece is the differential "high-f(M) pool runs colder ⇒ contamination diagnostic" framing. Weight: methods-paper-supporting, modest, not standalone. arXiv gate unverified — re-run before relying on the novelty framing.
- **Provenance:** task #125; `/tmp/lane125_kinematics_companion_mass_2026_06_05.md`, `/tmp/lane125_uvw_table.csv`.

### 2026-06-05 — Odd-axis C: GALEX UV × astrometry (#121) — NO-GO discovery / GO as a candidate-vetting add-on
- **Did:** scout UV-excess companion-typing on the NSS pool + a direct re-test of our candidates (GALEX AIS II/335, 8" cone, photosphere-normalised UV-excess σ; the repo's hd*_pma SED machinery already implements the 2-component fit). (arXiv gate 429×3, succeeded on the 4th attempt.)
- **Found:** method is PUBLISHED — Makarov 2017 (arXiv:1705.01114), Shahaf+2023 Triage II (2309.15143, WD census on the SAME NSS pool), Garbutt/Parsons+2024 WD-pathways X (2403.07985, Gaia orbits for known UV-excess binaries) → the photometric twin of the Shahaf AMRF test, not novel. Candidate re-test (5/15 NUV-detected): **WDJ060042 (STRONG) excess +0.09 mag / +0.4σ → NO hot companion → stays compact-compatible** (GALEX does not deflate it; HST/COS still needed); WDJ205650 (confirmed He+He DD) +9.2σ NUV / +5.8σ FUV = POSITIVE CONTROL (statistic works); WDJ020915 no detection (AIS depth); 1593152 a −13.6σ "deficit" = single-T-BB artifact for cool primaries (caveat: use a real atmosphere for Teff≲6000 K).
- **Verdict:** NO-GO as a standalone hunt (covered; for compact candidates UV is only a NEGATIVE tool — no excess ⇒ stays compact). GO (cheap) as a standing GALEX-AIS UV-excess screen in the deep-dive workflow (reuse companion_excess_sigma; swap BB → model atmosphere / Makarov NUV envelope for cool primaries; flag NUV excess ≳+0.3 mag at ≥3σ + FUV corroboration).
- **Logged:** GALEX cross-check ledger rows added to the WDJ060042 + WDJ020915 journals.
- **Provenance:** task #121; `/tmp/lane121_galex_uv_astrometry_scout_2026_06_05.md`.

### 2026-06-05 — Odd-axis H: "absence" as a selection axis (isolated NS / quiescent compact) (#126) — NO-GO (hard)
- **Did:** complement of #34/#54/#115 — started FROM eRASS1-DE X-ray and selected on the ABSENCE of a binary signature (single + blue BP−RP<0.5 + RUWE<1.4 + log fx/fopt>−1). Recovered XDINS controls (RX J1856, RX J0720 — both in footprint, both soft); population test on a 161-source high-|b| cone + Gaia DSC class probs. (arXiv gate 429×2 → web substitute.)
- **Found:** (1) PHYSICS KILLS THE PREMISE — genuine isolated NS are V≈25-28 (RX J1856 V=25.6), 4.6-7.6 mag below Gaia G≈21, so "has a faint/blue Gaia counterpart" selects AGAINST INS; the controls themselves have NO real Gaia counterpart. (2) THE CUT IS QUASAR SELECTION — full isolated-compact cut → 8 survivors, ALL Gaia-DSC PQSO=1.000; 50/67 X-ray-loud counterparts extragalactic. (3) No parallax handle at G≈20.8 (the Object-B wall without Object-B's 5.3σ escape). (4) The one real discriminant (soft kT≈45-100 eV blackbody) is band-limited → needs photon-level spectral fitting + a V>25 non-detection → telescope-gated to both find and confirm.
- **Prior art:** published + actively worked by the eROSITA-DE team with a superior NWAY multi-survey + soft-spectral method — Kurpas/Schwope+2024 (arXiv:2405.12846; 33 new XDINS candidates, optical FU found nothing brighter than V≈25), Salvato+2025 (2509.02842).
- **Lesson + front-filter gap:** for isolated NS the discriminating "absence" is OPTICAL NON-DETECTION (Gaia gives it only as a null, never a selection); a blue Gaia source selects AGN. The known-object store holds only Galactic compact-object catalogues (no AGN/QSO) → "absent from store" is NOT novelty evidence in extragalactic-prone lanes — **add a QSO/AGN catalogue (Milliquas) to the front-filter** (also relevant to #127 / the Object-B recipe).
- **Provenance:** task #126; `/tmp/iso_compact_lane126_2026_06_05.md`.

### 2026-06-05 — Odd-axis I: mining the Gaia QSOC/DSC pipeline rejects (Object B generalized) (#127) — NO-GO
- **Did:** scouted "the Gaia pipeline's failures as a selection axis," anchored on Object B (3161546596480983040 — re-pulled its qso_candidates row: reproduces the journal exactly, plx 5.34σ / PM 36.3σ / crf=False / DSCq=0.505 / z=4.36). Sized the contaminant population: qso_candidates 6.65M, astrometric_selection_flag=False = 4.75M (71%); Object-B archetype (0.45<DSCq<0.6, z>2, asf=F) = 147k; a TOP-2000 significant-astrometry sample (plx_SNR>8) is 100% non-CRF, median PM_SNR≈62, 77% blue+subluminous (median M_G≈12.8 = hot-WD track). (arXiv gate 429 throughout → WebSearch+SIMBAD fallback.)
- **Found:** front-filter kills it — 58/60 blue-subluminous rejects already catalogued, 57 as WD/WD?: these rejects ARE the Gentile-Fusillo Gaia WD catalogue (GF21 uses the same plx/PM cut; Object B is already in it). Published both ways: QSO purification (CatNorth, Quaia, Apsis III) + WD recovery (GF21); the accretor subset = X-ray+colour = Rodriguez+2025 (already noted). Counter-case KUV 23182+1007 (suspected AM CVn → real quasar) shows "reject ⇒ compact object" is an unsafe prior.
- **Verdict:** NO-GO — ~97% already-catalogued WDs; Object B's interest was its eRASS1 X-ray (not the reject status); the only defensible recipe collapses to the already-NULL eRASS1×Gaia lane (#115) with a completeness-shrinking QSO pre-filter. No deep-dive dispatched. EV stays in fresh data.
- **Provenance:** task #127; `/tmp/lane127_qsoc_reject_mining_2026_06_05.md`.

### 2026-06-05 — Odd-axis E: asteroseismology × astrometry (seismic M1 on the NSS pool) (#123) — NO-GO / NULL (method-validated, yield-starved)
- **Did:** APOKASC-2 (J/ApJS/239/32) + Yu+2018 (J/ApJS/236/42) = 16,566 unique-KIC seismic giants × Gaia NSS (3″): 46 have a mass-function-yielding orbit (32 AstroSpectroSB1 + 14 Orbital), 19 survive our quality cut. Recomputed M2 with seismic M1 (project f(M) convention, no sin-i inflation). (Gaia upload-xmatch 500'd — archive "in evolution"; used a Kepler-box pull + local match. arXiv gate 429×3 → training-knowledge + VizieR backstop.)
- **Found:** premise HOLDS — all 19 pool overlaps had M1=DEFAULT_1.5, so seismic M1 is genuinely new info (median M_seis 1.59 vs 1.50, |ΔM1|≈0.43). But companions stay stellar: max min-M2 (sin i=1) = 1.97 (KIC 11502218 = Gaia 2132620694633811456, already F#30-demoted); 0 in compact/NS range, 0 mass-gap; seismic masses 0.95-2.48 (ordinary giants). SIMBAD: all survivors RG*/HB*/SB*.
- **Verdict:** NO-GO as discovery — established niche (APOGEE-Kepler seismic binaries; Gaia NSS × Kepler-seismic ~2022-24, not novel) AND yield-starved (ceiling ~46 systems; TESS too weak for P~0.6-4 yr orbits). Best residual use = a consistency cross-check (seismic M1 vs catalogue M1) on existing NSS candidates, not a discovery channel. arXiv gate unverified — manual re-run needed.
- **Provenance:** task #123; `/tmp/seismic_nss_lane123_report.md`.

### 2026-06-05 — Odd-axis A: chemistry × astrometry (Ba/CH × Gaia NSS) (#119) — NO-GO / PARKED (feasible, not novel)
- **Did:** Escorza+2017 (VizieR J/A+A/608/A100, 437 Ba/CH/dwarf-Ba/C stars) → 400/437 (92%) resolved to Gaia DR3 → 60 with an NSS orbit (~14%; SB1=35, AstroSpectroSB1=17, Orbital=7, OTS=1), 25 AMRF-derivable (reusing the Shahaf-validated AMRF-from-Thiele-Innes machinery in prime3_deepdive_2026_05_29.py). (Gaia tap_upload 500'd — archive "in evolution"; used per-star cones + batched source_id IN(...). arXiv gate 429×5 → domain-knowledge; NEEDS MANUAL RE-RUN.)
- **Found:** strongly feasible + physically confirmatory — AMRF photocentre masses 0.31-0.84 M⊙ (median 0.60 = textbook CO white dwarf), SB1 f(M) lower bounds 0.01-0.70 M⊙ = the WD range; **nothing anywhere >1.0 M⊙** (no compact/over-massive companion, as expected for AGB mass-transfer products). Gaia periods match decades-old literature (HD 50264 916 vs 910 d) — independent AMRF-pipeline validation. 0/60 in the known-object store (expected — these WDs sit below the Class-III compact bar); SIMBAD survivors are catalogued SB* with Ba/CH spectral types.
- **Verdict:** NO-GO as discovery — sample, objects, AND method all heavily published (McClure; Jorissen/Pourbaix; Escorza+2017/2019 + Jorissen+2019 = WD-companion mass distributions of THIS exact sample; Shahaf+2023/24 AMRF; Escorza/Shahaf Gaia-DR3 Ba-star astrometry 2023-24). Best residual use = a method-validation sanity check of our AMRF pipeline against a chemically-independent binary class (passed). arXiv gate unverified — manual re-run needed before any novelty claim.
- **Provenance:** task #119; `/tmp/lane119_FEASIBILITY_REPORT.md`.

### 2026-06-05 — Astrometric-microlensing event predictor (#118) — BUILT + VALIDATED; candidate cross NULL
- **Did:** built `scripts/microlensing/` — geometry.py (Einstein radius, A(u), dark-lens + luminous-blend centroid shift, PM+parallax closest-approach solver, mass-from-shift inversion), predict.py (Gaia DR3 high-μ lenses → background neighbours along the 2024-2030 track → ranked predicted-event table), validate.py, apply_candidates.py, README, 13 offline unit tests (all pass).
- **Validated:** reproduces the published LAWD 37 (Gaia DR3 5332606522595645952) event (Klüter+2018 prediction; McGill+2023 measurement): θ_E 31.4 vs 32.8±0.3 mas (4.4%, in-band); TCA J2019.860 exact; major-image shift 2.83 vs ~2.8 mas; mass inversion → 0.61 M⊙. (Fixed a 2× parallax-factor bug found in validation → astropy Earth ephemeris, <0.1 mas.)
- **Applied:** all 12 CANDIDATES.md source_ids cross-checked as lenses 2024-2030 → NULL (low PM 5-48 mas/yr ⇒ <0.3″ tracks ⇒ no background source swept). Predictor correctly flags 3 WD-locus lenses among top sample events (incl. LAWD 37 + two with ~30-47 µas predicted shifts — the "deflection weighs a WD mass" case).
- **Verdict:** method-validation + DR4-ready re-runnable tool, NOT a novel channel. Prior art semi-crowded (Klüter+2018 ×2, McGill+2018/19/20, Bramich 2018, Klüter+2024). HARD LIMIT (README): unseen isolated dark lenses CANNOT be pre-targeted (no Gaia entry) — those need Rubin-era monitoring; the predictor weighs KNOWN foreground objects. Solo edge = DR4-readiness (GAIA_TABLE→gaiadr4) + the candidate cross (null).
- **Provenance:** task #118; `scripts/microlensing/`, `tests/test_microlensing.py`.

### 2026-06-10 — Full project review (multi-agent) + Phase-1/2 of the resulting attack order
- **Did:** 5 repo audits (docs/infra/journals/data/candidates) + 8 ideation lenses → 36 lane ideas → 12-lane
  shortlist → per-lane adversarial verification (prior-art via WebSearch, duplicate-check vs this log,
  no-telescope test, feasibility probes) + a second skeptic on every GO + a completeness critic. Full
  machine-readable verdicts: `docs/reports/project_review_2026_06_10.json`.
- **Survivor lanes (GO, double-verified):** (1) **freeze the DR4 prereg as a citable product + AEN
  shadow-WD watch list** (EV 6.5; per-candidate registered-report practice absent in subfield; GF21 WDs with
  RUWE/AEN wobble but NO NSS solution = a day-one watch list the #117 rehunt is structurally blind to;
  condition: extend prereg coverage first — DONE today, Addendum A); (2) **RVS mean-spectrum SB2/second-light
  screen on the 23 Tier-1 NS with has_rvs** (EV 5; zero in-repo DataLink-RVS use; window closes at DR4;
  realistic sensitivity 15–30% flux ratio); (3) **M1-correction debt**: substellar bins still at default
  M1=1.5 (81/82 main, 113/115 relaxed) + acceleration_v3 100% default → re-tier + BD extraction + a
  near-unpopulated [Fe/H]<−1 astrometric-BD-host slice (EV 6; front-filter vs Stevenson+2023/DPAC/Wallace&Casey
  2026/GaiaPMEX; NOTE: the dossier ref "Bailer-Jones & Kreidberg 2026" could not be located by the verifier —
  re-check that citation); (4) **DR4 joint epoch-astrometry+epoch-RV fitter** (EV 6; third pipeline leg,
  genuinely absent in-repo; validate on the 854 FPR×SB1 overlap — the AstroSpectroSB1×FPR overlap is EMPTY).
- **Killed lanes (log so they are not re-tried):** occurrence-limit standalone paper **REFUTED** — El-Badry+2024
  (arXiv:2405.00089) already *measured* ~1e-6 for this population, ~50× below our f<5.7e-5 limit (the limit is
  non-constraining; #125 kinematics box survives only as a methods-paper element); Gomel
  vari_compact_companion × archival RV (Nagarajan & El-Badry 2023 refuted the best candidates; 17/6306 have NSS
  rows); FPR-LPV blind RV Keplerian hunt (Nagarajan+2024 = exactly this); eastern 4XMM/2SXPS/CSC screen
  (expected detections ~0); APOGEE-ASPCAP both-arms ingest (bright-cap mismatch + telescope-gated discriminants
  — closes the standing "highest-value missing data" item as a NO-GO); bug-catalog stress-test of published
  lists (Bashi+2022 = the bit-13 audit; Gomel join structurally empty; surviving kernel = pre-register DR4
  predictions for published lists, folded into lane 1); plus MARVELS / radio-quiescence / DASCH-as-survey /
  OGLE-ETV / self-lensing / CPM-age / TESS-BD-transit / dark-lens-π_E / e–P mining — reasons + refs in the JSON.
- **Review blind spots (critic):** ASAS-SN + ATLAS forced photometry never used as a modality anywhere —
  the pool is G≈6–13 where ZTF *saturates*; a pool-wide bright-star variability screen is an open cheap
  self-audit (queued). No standing scoop monitor on the 4 novel candidates (queued). No security red-team of
  the hunt console / web-ingest path. eROSITA-east is IKI-held with **no scheduled public release** — stop
  treating it as scheduled fresh data.
- **Phase-1 debt retired today:** F#33→corrected-tier propagation (roster 161→116, see index row); WD
  full-TI MC regenerated + REPRODUCED (prereg provenance restored, `docs/reports/wd_ti_mc_regen_2026_06_10.md`);
  prereg Addenda A+B (coverage 4/9→9/9; floor-convention + WDJ020915 MC mandate recorded); register backfill
  (25 AMRFClassIII + 13 relaxed Tier-1; → 1,997 rows); #121 GALEX ledger rows propagated to WDJ205650 + 1593152;
  `docs/reports/` created as the durable home for lane artifacts (**lesson: stop anchoring permanent docs to
  /tmp — three headline artifacts had already been purged**, incl. the prereg's mass-MC provenance).
- **Task closures:** #103 (XP ingest), #111 (register bulk-import), #112 (Object B deep-dive) completed in
  commit 7b7c4a2; #113 (Object B ZTF re-check → INCONCLUSIVE, unmeasurable: no ZTF source within 2″) integrated
  in the journal — Object B is **spectrum-gated**; CANDIDATES.md roster row updated accordingly. **Correction:**
  the #122 entry's claim that the HD 157033 PMa play was "(pre-registered)" was false at the time of writing —
  it is pre-registered only as of today's Addendum A.4.
- **Phase-2 archival sweep results:** see index row + `docs/reports/phase2_archival_checks_2026_06_10.md`;
  14 cross-check ledger rows appended. Notables: Object B's GALEX null is a **coverage gap** (dossier S3
  wording superseded — UV unconstrained); DASCH 1889–1989 excludes nova-scale outbursts of the blend (dwarf-nova
  scale hidden by the B≈13.7 blend floor); HD 157033 has zero ESO archival spectra ever (Proxima positive
  control) → its RV is genuinely telescope-gated; no new public RV epochs for 1593152/3155543 (LAMOST DR12 is
  login-gated — **watch item**: re-query on international release).
- **Unrecoverable details (recorded honestly):** per-object verdicts of the 2026-05-28 ns_pool_triage and the
  exact candidate membership of the #118/#120/#125 per-object nulls were only in purged /tmp files — register
  rows say "triaged-in-aggregate"; the per-object #118/#120/#125 ledger backfill is NOT possible from prose
  alone and was skipped rather than logged inaccurately.
- **Queued next (order of attack):** RUWE flag in consumer_v2 tiering (+ cascade-regression gate) before DR4;
  GALEX screen + store/Milliquas gate wiring into ns-candidate-deep-dive workflow; lanes 1–4 above; ASAS-SN/ATLAS
  bright-pool screen; scoop monitor; CITATION.cff/version reconciliation; unified-parquet regeneration.
- **Provenance:** session 2026-06-09→10; `docs/reports/project_review_2026_06_10.json`; workflow run wf_d27944e2.

### 2026-06-10 — F#34 astrometric-quality caution flag (RUWE follow-up retired) + cascade-regression gate
- **Did:** implemented `filter34_astromqual` in `consumer_v2.py` — the 2026-05-30 "global RUWE gate" tracked
  follow-up — as a **caution flag that never changes the tier**. Fetched the never-pulled NSS
  `goodness_of_fit` (F2) + `ipd_frac_multi_peak` for all 1,251 candidate-tier sources
  (`docs/reports/f2_ipd_fetch_2026_06_10.csv`), merged into the three `_M1corrected` parquets
  (`nss_gof_f2`, `ipd_frac_multi_peak`, `filter34_v2`, `filter34_reason_v2`;
  `scripts/apply_f34_astromqual_2026_06_10.py`), wired into `derive_row_v2` so the DR4 rehunt inherits it.
- **Design finding (corrects the original note's premise):** the corrected Tier-1 pool spans RUWE 2.6–28.8
  (median 6.1) — elevated single-star RUWE is the *normal* signature of a photocentric binary, so the
  originally envisioned absolute-RUWE gate would flag 52% of Tier-1 at >6 and discriminate nothing (both
  motivating offenders, 6.46/9.35, sit inside the bulk). Discriminating axes used instead: orbit-level
  **F2 > +5** (the frozen prereg "unreliable" convention), **ipd_frac_multi_peak ≥ 4** (resolved-double
  contamination), **RUWE ≥ 12.5** (Tier-1 P95, extreme even for wobble). Loud `NO_DATA` when all inputs
  missing (the #117 silent-no-op lesson).
- **Result:** 51/108 main + 3/9 relaxed Tier-1 NS flagged — incl. **GALEX J145250 (F2=+8.0)**, the exact case
  that motivated the follow-up, HD 75567 (triple-favored, F2=+6.3), and 2129927539681151872 (F2=+17.2).
  HD 264291 carries the caution too (F2=+6.8) — consistent with its documented marginal astrometry
  (sig 12.5); its independent RV confirmation is why this is a flag, not a cut.
- **Gate:** cascade-regression after the consumer change — **PASS (conditional)**: 63/63 pytest, BH2 fixture
  Tier-1 (1/1), 6/6 negative controls rejected, frozen production tiers reproduced exactly; the 3 live "misses"
  (BH1 F#31 NO_DATA, BH2 F#30, BH3 no-NSS) are documented design. Conditions, all closed same-day:
  (1) `benchmarks.json` stale BH1 expectation ("Tier-1 BH" → the by-design Tier-2 string) fixed;
  (2) HD 207141 stale "heaviest BH candidate M₂=7.57" benchmark entry corrected AND its missing journal
  created (`docs/object_journals/6811355413155399040.md`) with the Shahaf PIII=1e-5 triple verdict +
  a flagged **1.31-vs-1.75 M₂ reconciliation item** (demoted-table vs M1-corrected parquet — open);
  (3) the 49-object Tier-1×Shahaf cross salvaged to `docs/reports/tier1_x_shahaf_t1_2026_06_10.csv`
  (gate stat: 9/49 PIII≥0.5, median 0.015 — quantitative re-confirmation of the triple-dominated insight);
  (4) the "93% recall on 27 systems" claim annotated **unverified** in CANDIDATES.md (truth set never
  committed; CITATION.cff says 70) — re-commit the truth set or soften before release.
- **Provenance:** session 2026-06-10; gate run wf_30d426da; `scripts/apply_f34_astromqual_2026_06_10.py`.

### 2026-06-12 — Access lanes: ZTF ZFPS granted; LAMOST DR12 route host-gated (not CV-gated)
- **ZTF ZFPS:** account granted (IPAC, J. Castaneda Jaimes). Dual-position request staged
  (`scripts/ztf_zfps_objectB_request.sh`): Object B + the 4.76″ neighbour as contamination
  control; submission = user keystroke; results by email (queue can exceed 7 d).
- **LAMOST:** DR11 is public without registration (already swept 2026-06-10 — nothing new for
  1593152/3155543). The DR12+ external-collaborator application requires a **Chinese host
  institution + host researcher + recommendation letter** (form sections 5+7) — not viable solo;
  the correct plan stays the existing watch item (re-query on DR12 international release), or a
  host/collaborator if a confirmed result later motivates one.
- **Object B contamination audit (same session):** Gaia BP/RP blend diagnostics — Object B
  photometry CLEAN (C*=+0.056, 0% blended transits, ipd_mp=0); the neighbour is itself a close
  double (ipd_mp=91, RUWE 18.95) → coronal-ceiling argument weakens to ~1.3×; X-ray ID rests on
  the positional match (unaffected). Ledger row in the Object B journal.

### 2026-07-01 — Object B: PS1 DR2 = first resolved photometric signal (suggestive variability); ZFPS revoked -> DIY forced-photometry lane opened
- **ZFPS account revoked** (institutional-policy gate; creds rejected). Route replaced by (a) a DIY local forced-photometry lane on PUBLIC ZTF difference images (ztfquery/ztflc-class, anonymous-IBE feasibility spike dispatched) and (b) status email to the IPAC operator (user action).
- **PS1 DR2 (new lane, never checked): suggestive ~0.1-0.3 mag variability of Object B itself** — attribution-clean 15-epoch resolved photometry 2011.8-2014.3; scatter p89-p100 of a 37-star control; percentile-0 g-band bright-state offset (4/4 dets 0.24-0.38 mag above the concordant stack+forced time-average); NO outbursts; deblend-loss confound stated (evidence, not proof). Exactly the CV-flickering signature the classification predicts; confirmation = resolved ZTF light curve.
- **LSST alert lane opened but not closed** (Fink unreachable locally; ALeRCE/ANTARES ZTF-only; Lasair token-gated). Validated ZTF alert nulls at both positions through 2026-06 (no bright outburst 2018-2026).

### 2026-07-01 (late) — Object B PS1 variability claim REFUTED by adversarial referee; variability = UNTESTED, DR4-gated
- The same-day PS1 forced-warp "variability CONFIRMED" verdict was killed on re-verification: the correct control population (9 blend-geometry ANALOGUES — faint star 3-6as from a bright one) shows Object B's scatter is percentile ~67 = TYPICAL for its geometry; the signal is the neighbour's halo/wing systematic (seeing over-subtraction sign, chip-aliased "seasons", neighbour anticorrelation, error-model-inflated sigmas). The first agent's numbers reproduced exactly; its inference (isolated-star controls) was the flaw. **Lesson institutionalized: for blended targets, the control ensemble must MATCH THE BLEND GEOMETRY, not just the magnitude.**
- Net Object B ledger: photometric variability is UNTESTED across ALL archives (PS1 cannot decide at this geometry; ZTF floor 0.21-0.36 mag; ATLAS/DASCH blend-dead) except: not a dwarf nova (ZTF duty <5-9%, 2018-2025) and no bright outburst 1889-1989 (DASCH nova-scale) / 2018-2026 (alerts). Subtype remains SPECTRUM-GATED; the designated variability instrument is **Gaia DR4 epoch photometry (Dec 2)** — resolved, and the target is well within reach.
- Both verdicts + the refutation are ledgered same-day; status/dossier NOT upgraded at any point (the referee gate did its job before any status change).

### 2026-07-02 — PS1 forced-warp variability screen over the uncatalogued register (NEW lane; instrument built 2026-07-01)
- **Lane:** first-ever time-series test of the register's 155 uncatalogued objects via anonymous MAST PS1-DR2 forced-warp TAP + population-calibrated thresholds + blend-geometry gate (Object B auto-flagged UNRELIABLE by the gate — the 2026-07-01 analogue-control lesson is now structural, sanity check passed).
- **Result: properly-tested NEAR-NULL.** 149 Gaia-resolvable: 94 NOT-IN-PS1 (93 at Dec<-30 — the eRASS1 lane is SOUTH-HEAVY: the register's majority needs a southern instrument => LSST is the register's designated time-series instrument), 28 quiet, 11 saturated, 5 blend-flagged, 5 too-few-epochs, 3 seeing-systematics (demoted at deep-check), 1 photometry-integrity-broken (3851730042602531584: forced-vs-mean 2-mag discrepancy + RUWE 4.08 unresolved pair — image-level inspection needed if ever revisited).
- **2 CANDIDATE-VARIABLE (pending referee, both plausibly ORDINARY active M dwarfs, no compact-object signature):** 3137896273168859648 (1eRASS J073600.6+034909; time-coherent 0.2-0.6 mag, M dwarf + X-ray => activity plausible; beat 5/5 matched controls + systematics checks) and 6315134987927550592 (weaker, 92 mas/yr PM caveat). No auto deep-dive (autonomy bar not met: no compact/accretor anomaly beyond normal M-dwarf activity); flagged for optional referee.
- **Instrument caveat recorded:** PS1 forced-warp formal errors are ~10x underestimated population-wide — any future use must calibrate thresholds on the population, never on formal errors.
- Provenance: /tmp/ps1_register_screen/ (final_verdicts.csv authoritative).

### 2026-07-02 — ASAS-SN bright-pool screen (queued blind-spot audit): 0 credible detections; guardrail upgraded
- 9 named candidates screened (Sky Patrol v2, V+g 2012-2025). **CLOSED-QUIET with mmag floors:** 1593152 (~3), 3155543 (~2, cleanest), 5858574 (~2 g-only), UCAC4 313 (~13, no flares), WDJ020915 (~16 — ATLAS-quiet corroborated, orbit-reality strengthened again). **PARTIALLY closed (G<~10.5 saturation):** HD 157033, HD 207141 (<~50 mmag), HD 264291. WDJ060042 too faint. 0 outbursts/eclipses anywhere.
- **GUARDRAIL UPGRADE (institutionalized):** two white-permutation "detections" at exactly P/P2 (FAP 5e-4..1e-3: HD 207141 @P, HD 264291 @P/2) were KILLED by a red-noise LOCAL null (power at P vs 500 random long periods, same LC) + per-camera phase coherence -> saturation red noise. RULE: for long-period claims in bright/saturated light curves, the white-noise permutation FAP is INSUFFICIENT — require the red-noise local null + camera coherence.
- Remaining lever for the saturated trio: ASAS-3 / KELT / Hipparcos epoch photometry (queued, low priority).
- Provenance: /tmp/asassn_bright_screen/ (verdicts.csv authoritative); 9 per-object ledger rows appended.

### 2026-07-02 — APOGEE DR17 ASPCAP ingest (allStarLite local bulk): bulge-symbiotic lane CLOSED; portfolio RV sweep all-null
- **Catalog banked (durable asset):** `data/external_catalogs/apogee_dr17/allStarLite-dr17-synspec_rev1.fits` (1.83 GB, 733,901 rows, gitignored, re-downloadable from SDSS SAS). Carries GAIAEDR3_SOURCE_ID natively — direct DR3 source_id joins, no 2MASS gymnastics.
- **Arm A — bulge-symbiotic closure (idea #8 enabler tested):** Akras+2019 (J/ApJS/240/21, 410 rows) × allStarLite 3″: **25/410 overall, 1/123 bulge-box (|l|≤10,|b|≤10), 2/193 inner-plane (|b|≤5), 0 near-misses 3–10″**; the single bulge hit (AS 255) has NaN TEFF/LOGG (ASPCAP non-converged). Independently reproduces the 2026-06-10 review probe (1/140). **The "APOGEE = no-telescope bulge confirmation route" hypothesis is REFUTED by fiber coverage; lane stays PARKED for 4MOST/SDSS-V; the lost 137-candidate list will NOT be regenerated.**
- **Arm B — portfolio sweep (20 journaled objects):** 2/20 matched. 1593152388271709824 single-visit (constrains nothing); 4111149395881722496 (HD 157033) VSCATTER=35.7 with SUSPECT_BROAD_LINES/VSINI_BAD — re-derives the existing "unreliable APOGEE RV" ledger caveat verbatim. **All 7 active candidates: no new APOGEE RV constraint** (5 not observed; ledger nulls appended for all 20, incl. 4 first-time APOGEE rows: 2909342818326298112, 3161546596480983040 Object B, 332248057157474176, 5612039087715504640 UCAC4 313).
- **Arm B2 — findings-register screen (1,997 rows):** 25 matched; 5 with NVISITS≥3 & VSCATTER≥1 km/s — all known-recoveries (1 WR spectral-fit failure, 3 eRASS1 knowns, KIC 4069063 = published Conroy+2014 triple); **0 uncatalogued/novel flagged**.
- Note: `data/external_catalogs/apogee_dr17_v2_pool.csv` (559 rows) is an SB9-style RV pool, not an APOGEE extract, despite the filename — matched 0/20.
- Provenance: /tmp/apogee_ingest_2026_07_02/ (REPORT.md + armA/armB/armB2 CSVs authoritative); 20 per-object ledger rows appended via journal.py.

### 2026-07-02 — Bright-trio follow-up: Hipparcos/ASAS-3/KELT screen (closes the ASAS-SN saturation blind spot)
- 3 saturated targets (HD 157033, HD 264291, HD 207141); source_ids SIMBAD-verified first — **HD 207141 = 6811355413155399040 confirmed exact**. Red-noise local-null + dataset-coherence guardrail throughout.
- **ASAS-3 delivered for all 3** (368–781 epochs, 7–8.8 yr, floors 12–18 mmag): ALL QUIET, 0 signals survive the guardrail; HD 264291's marginal P/2 (FAP 0.10) fails coherence → independently corroborates the ASAS-SN P/2 kill with a decade-earlier instrument.
- Hipparcos: only HD 157033 present (Hp scatter 25 mmag, flag=constant 1989–93); other 2 genuinely absent (Tycho-2 controls); raw Hipparcos epochs not publicly exposed anywhere. KELT: unusable ×3 (2 field gaps, 1 saturation-excluded — verified against archive's own data).
- **Verdict: HD 264291 + HD 207141 photometric lanes CLOSED; HD 157033 mostly closed** (36-yr zero-outburst baseline; mass ambiguity untouched, DR4/telescope-gated). The queued "ASAS-3/KELT/Hipparcos bright trio" item is DONE.
- Provenance: docs/reports/bright_trio_screen_2026_07_02.md (report of record) + /tmp/bright_trio_screen/; 9 ledger rows appended.
