# Research log — project lab notebook

This file is a chronological record of the project's search lanes and their iterations, with the newest entry at the bottom of each section. Per-object history is kept in `docs/object_journals/<source_id>.md`.

Status tags: `OPEN` / `PROMISING` / `PARKED` / `NULL` / `SUPERSEDED` / `INFRA`.

---

## Lane & iteration index

| date(s) | lane / activity | outcome | detail |
|---|---|---|---|
| ~05-12 → 05-27 | Gaia DR3 NSS dormant-compact cascade (v1) + repo | built | README, `scripts/streaming/` |
| 05-27 | repo recovery + v1.17.0 | done | — |
| 05-28 | v1 → v2 cascade corrections (NSS parallax, K_obs/2, F#30 logg) | SUPERSEDED v1 | `docs/METHODOLOGY.md` |
| 05-28 | Retractions (CRTS J051419 CV period/eclipse; mass-gap-BH sin-i inflation) | NULL/corrected | release v2.1.0; CANDIDATES.md retraction table |
| 05-28 | Per-target dossiers (17) | built | `docs/dossiers/` |
| 05-28 | Triple-vs-compact assessment (Shahaf AMRF) | finding | most Tier-1 NS are hierarchical triples, not single compact objects |
| 05-29 | HD 264291 — independent RV confirmation (heavy NS M₂≈1.94) | known (Shahaf) | the only compact-favoured survivor; not novel |
| 05-30 | Substellar novelty cross-check | corrected | UCAC4 313 = novel (superseded 2026-09-22: orbit published by Bailer-Jones & Kreidberg 2026; in Shahaf+2023 table 1); APMPM J0710 / SCR J1441 = already published |
| 05-31 | Inclination Thiele-Innes cos i sqrt bug fixed (6 sites/3 scripts) | corrected | biased spectroscopic M₂ high; pre-fix outputs stale |
| 05-31 | WD-binary framing correction (not a super-Ch WD, not a Type-Ia progenitor) | corrected | WDJ020915/060042: M_tot>M_Ch split between two bodies |
| 05-31 | Self-lensing search | PARKED | — |
| 05-31 | eRASS1 v1 → v2 (multi-catalogue gate, high-PM J2000 propagation) | NULL | 671 known / 137 uncatalogued / 0 outburst-confirmed-new |
| 06-01 | Fresh-lane sweep: XP-pilot, hyper-v WD, eRASS1, bulge-symbiotic, spectral-diff, IR-nova | all NULL | 0 confirmed novel in any of these archival lanes |
| 06-01 | XP-at-scale feasibility milestone | NO-GO | artefact-dominated, structurally blind, prior work in the field |
| 06-01 | DR4 pre-registration (falsifiable confirm/refute thresholds) | built | `docs/dr4_preregistration_2026_06_01.md` |
| 06-01 | Occurrence upper limit (Poisson rule-of-3) | result | f < 5.7×10⁻⁵ (95% CL) in the searched regime |
| 06-01 | Known-object front-filter (6104 objects, source_id-keyed) | built | `scripts/known_objects/` |
| ~06-01 | Hunt console (live dashboard + dossier viewer) | built | `scripts/web_tool/hunt_console/` |
| 06-03 | Object-journal + research-log system | built | this file + `docs/object_journals/` |
| 06-03 | UCAC4 313 "Shahaf recovery" claim | corrected | mislabelled; recorded then as not in Shahaf (superseded 2026-09-22: in Shahaf+2023 table 1, AMRF class I) |
| 06-03 | Project-wide re-vet (all files + history) | audit; null holds | 1 orphan (TYC 7350-249-1); front-filter gap closed (26 pool objects = published AMRFClassIII); ELM/sdB and ETV-tertiary runs = INFRA nulls (untested); 5858574 soft demotion |
| 06-05 | Field-status / prior-art screen (cross-survey lanes vs the literature) | prior art found; tool built | multi-survey fusion is the prevailing approach in the literature; the Fermi-spider and Gaia×eROSITA×ZTF accretor lanes and the SN-runaway and anomaly ideas are all published 2024–26 (Rodriguez+25 eRASS1×Gaia×ZTF; COBIPLANE & ZTF×4FGL spiders; high-v X-ray 2026; SNAD). Built `scripts/litcheck/prior_art.py` + prior-art gate |
| 06-05 | Cross-survey quiescent-XRB lane (Gaia NSS dark-companion pool × eRASS1-DE), widened from an earlier eRASS1 lane | NULL; parked | 6468-source pool, 110 eRASS1 matches (1.70%); all coronal (log fx/fopt ≤ −2.09; max Lx 8.2e30); 0 compact accretors |
| 06-05 | DR4 day-one: blind re-hunt harness | built | `scripts/dr4_pipeline/rehunt/`; cascade code imported, not copied; DR3 dry run reproduces the roster exactly (0/56,100 tier mismatches); input staleness found: raw chunks lack `flags`, committed v2 parquet predates the M1 correction → DR4 diff baseline = `_M1corrected` |
| 06-05 | DR4 day-one: candidate re-fit engine | built | `scripts/dr4_pipeline/refit/`; epoch-astrometry orbit fitter + 1-body-vs-multi-body (ΔBIC/F-test/accel-SNR/F2); pre-reg thresholds wired and cross-checked against the document; 8 synthetic tests pass (0% false-triple, 72% 2-body detection); WDJ020915: bare f(M) M2=1.223, at the 1.2 floor → full-TI MC used on DR4 day |
| 06-05 | Odd-axis D: PMa × RV-trend | NO-GO (duplicate) | already done in-repo in both forms: Pile-A HGCA (HD 157033 + 7 demoted) + acceleration_v3 (16,949 srcs, 6,828 dual-signal, 3,761 RV-demoted); limited by inclination/period degeneracy and telescope-gated → DR4 follow-up |
| 06-05 | Odd-axis F: IR-variability × astrometry | NO-GO (structural null) | NSS G<13 cap and dusty-symbiotic G~13-16 disjoint; 0/2,330 unsaturated red NSS giants with W1−W2>0.2; 13 raw hits all WISE-saturation artefacts; no increment over the IR-nova/bulge-symbiotic lanes → revisit with DR4 (fainter) |
| 06-05 | Odd-axis B: variability-phase × orbit-phase | NO-GO as discovery lane; self-audit passed | prior art (Holl+2023a/b; DPAC already filters spurious-period artefacts) and inoperative: P_orb median 585d vs P_phot median 1.9d (disjoint, max ratio 0.22); all 16 candidates photometrically quiet (0/16 VARIABLE) |
| 06-05 | Cross-survey Fermi-spider hunt (4FGL-DR3 × eRASS1-DE × Gaia) | NULL; parked (pipeline validated) | 2154 unassoc 4FGL → 733 in-ellipse eROSITA → 384 γ+X+optical pairs → 0 novel spiders; positive control passed (12 known PSR / 5 SpiderCat, incl. full J0639 redback triple); survivors all known CV/YSO/EB + chance alignments (count tracks stellar density); eastern Galactic plane not covered → eROSITA-east. 2 CV recoveries → register |
| 06-05 | Odd-axis G: Galactic kinematics × companion mass (demographics, no new object) | NULL (opposite sign); decision: box in the limits paper | UVW+Toomre: 641 compact-favoured + 149 Tier-1 vs 53,659 stellar-companion NSS binaries (Sahlmann orbit parent, 87% real RV). Compact pool kinematically colder / thin-disk, not hotter: thick+halo 0.9% vs 3.8% (Fisher p=1.5e-5); holds under dist/mag/colour matching (KS p=2e-6) → independent kinematic support for the contamination/triple null and for f<5.7e-5 |
| 06-05 | Odd-axis C: GALEX UV × astrometry | NO-GO as discovery lane; adopted as vetting step | published (Makarov 2017; Shahaf+2023 Triage II; Garbutt/Parsons+2024). Candidate re-test: WDJ060042 UV excess +0.4σ → remains compact-compatible; WDJ205650 (known He+He DD) +9.2σ = positive control; WDJ020915 no detection. 0 novel → UV-excess screen added to candidate vetting |
| 06-05 | Odd-axis H: "absence"-as-selection (eRASS1 → Gaia, no-binarity + faint/blue + high fx/fopt) | NO-GO | premise fails (true INS are V≳25, below Gaia → an optical counterpart selects against INS; XDINS controls RX J1856/J0720 have no real Gaia source); cut selects AGN (8/8 full-cut survivors PQSO=1.0; 50/67 X-ray-loud extragalactic); published (Kurpas+2024, 33 XDINS cand). Known-object store has no AGN catalogue → novelty cannot be gated here |
| 06-05 | Odd-axis I: Gaia QSOC/DSC rejects (Object B generalised) | NO-GO | the rejects are the Gentile-Fusillo Gaia WD catalogue (97% already-known WDs, same plx/PM cut); Object B was selected for its eRASS1 X-ray detection, not its reject status; the recipe reduces to the NULL Gaia×eROSITA×ZTF lane + a completeness-reducing pre-filter; published both ways (CatNorth/Quaia purification; GF21 recovery). arXiv check failed (429) |
| 06-05 | Odd-axis E: asteroseismology × astrometry | NO-GO / NULL | seismic M1 adds information (19 pool overlaps all had default M1=1.5; median M_seis 1.59) but companions stay stellar: max min-M2=1.97 (already demoted), 0 compact; at most ~46 systems available (Kepler × all-sky NSS overlap); established prior art. arXiv check failed (429) |
| 06-05 | Odd-axis A: chemistry × astrometry (Ba/CH × Gaia NSS) | NO-GO / PARKED (feasible, not novel) | 437 Escorza Ba/CH → 60 with NSS orbits, 25 AMRF-derivable; companion masses 0.31-0.84 M⊙ (median 0.60 = typical CO WD), none >1.0; sample, objects and method published (Escorza/Jorissen WD-mass distributions of this sample; Shahaf AMRF); Gaia P matches literature → AMRF-pipeline validation. arXiv check failed (429) |
| 06-05 | Astrometric microlensing predictor | built + validated; candidate cross-match NULL | `scripts/microlensing/` (geometry/predict/validate/apply + 13 tests); reproduces LAWD 37 (θ_E 31.4 vs 32.8 mas, TCA exact, mass→0.61 M⊙; fixed a 2× parallax-factor bug); 12 candidates as lenses → NULL (low-PM, distant); WD-lens flagging works. Method validation + DR4-ready tool, not novel; isolated dark lenses require Rubin monitoring (unseen lenses cannot be pre-targeted) |
| 06-09→06-10 | Full project review (5 repository audits; 36 ideas → 12-lane shortlist → independent verification) | 4 GO lanes; debt list; NO-GO ledger | `docs/reports/project_review_2026_06_10.json` (verdicts + prior-art refs); detailed entry below |
| 06-10 | F#33 → corrected-tier propagation (review debt item) | FIXED | 41 main + 4 relaxed corrected-Tier-1 NS carried the bit-13 flag → new `tier_v2_corrected_f33` column: Tier-1 NS 148→107 (main), 13→9 (relaxed), roster = 116; `scripts/apply_f33_to_corrected_tiers_2026_06_10.py`; the DR4 re-hunt diffs on this column |
| 06-10 | WD full-TI-covariance MC regeneration (earlier outputs had been deleted) | REPRODUCED | WDJ020915 M₂=1.322 [1.267–1.379], P(>1.4)=8.7% (anchor 8.6); WDJ060042 1.368 [1.229–1.521], P(>1.4)=41.4% (anchor 41); corr_vec used; `docs/reports/wd_ti_mc_regen_2026_06_10.md` |
| 06-10 | Phase-2 archival sweep (eRASS1 / GALEX / 4XMM / CSC / 2SXPS / DASCH / LAMOST-DR11+DR12 / SDSS-V DR19 / ESO raw) on 6 roster objects | logged (14 ledger rows) | Object B: GALEX = coverage gap (UV unconstrained; dossier S3 superseded), XMM/Chandra = no coverage, DASCH = no nova-scale outburst 1889–1989; WDJ060042 + WG 26 eRASS1 NULL; no new RV epochs (1593152, 3155543; DR12 login-gated); HD 157033 ESO archive = zero spectra (positive control verified) → telescope-gated. `docs/reports/phase2_archival_checks_2026_06_10.md` |
| 06-10 | DR4 prereg Addendum A+B (5 remaining roster objects + floor convention + WDJ020915 MC requirement) | built; coverage 9/9 | `docs/dr4_preregistration_2026_06_01.md` addenda; corrects the "(pre-registered)" claim in the PMa × RV-trend entry: HD 157033 is pre-registered only as of A.4 |
| 06-10 | Register backfill (AMRFClassIII 25 rows; relaxed Tier-1 NS 13 rows incl. 8 not previously logged) | done | `findings_register.csv` → 1,997 rows; per-object 2026-05-28 triage verdicts unrecoverable (temporary outputs deleted); logged as triaged in aggregate |
| 06-11 | ATLAS forced photometry light curves for Object B + WDJ020915 (10.4 yr, o+c) | WDJ020915 quiet / Object B unmeasurable | WDJ020915: no outbursts, no signal at P_orb=274.5d or P/2 (perm-FAP 0.27–1.0), LS peaks = diurnal/seasonal aliases → variability does not explain the F2=+8.39 weak fit (orbit reality strengthened pre-DR4). Object B: blend with the 4.76″ G=13.8 neighbour dominates the 4″ ATLAS PSF (σ_rob=740 µJy) → only sustained mag≲15 events excluded; next test = ZTF forced photometry (ZFPS; account registration pending). LAMOST DR12 NADC validation pending. `docs/reports/atlas_forcedphot_2026_06_11.md` |
| 06-10 | F#34 astrometric-quality caution flag (closes the 05-30 "global RUWE gate" follow-up) | built; gate PASS | `consumer_v2.filter34_astromqual`: a flag, never a cut: F2>+5 / ipd≥4 / RUWE≥12.5. Tier-1 RUWE 2.6–28.8 (median 6.1) = normal photocentric-binary signature → an absolute RUWE gate does not discriminate; orbit F2 does. F2+ipd fetched for 1,251 candidate-tier sources; 51/108 main + 3/9 relaxed Tier-1 flagged (incl. GALEX J145250 F2=+8.0, HD 75567, HD 264291 caution). Cascade-regression gate: PASS (conditional): 0 behavioural regressions; conditions fixed the same day (stale BH1 + HD 207141 benchmark expectations corrected; HD 207141 journal created incl. a flagged 1.31-vs-1.75 M₂ reconciliation item; Shahaf 49-object cross-match saved to `docs/reports/tier1_x_shahaf_t1_2026_06_10.csv`; 93% recall claim marked unverified, truth set never committed). Shahaf gate statistic: 9/49 Tier-1 with PIII≥0.5 (median 0.015), consistent with the triple-dominated finding |

---

## Net state (as of 2026-06-04)

0 confirmed novel compact objects in any archival lane. Methods validated. Remaining options: XP-at-scale (a build) and new data (Gaia DR4, 2 Dec 2026; eROSITA-east; Rubin/LSST); lanes on existing data are closed. Active candidates (all unconfirmed, pending DR4): `docs/CANDIDATES.md` and the per-object journals.

**Online re-runs (2026-06-04):** all NULL; they replace the untested 2026-06-03 infra-null attempts of the ELM/sdB and ETV lanes.
- **ELM/sdB + NS/BH:** 66k hot subdwarfs × live Gaia NSS with no period floor; short-P ZTF/Gaia photometry; 3 positive controls pass → 0 novel sdB/ELM with a dark compact companion. Gaia NSS cannot detect hours-period sdB orbits; that channel needs an RV f(M) (telescope-gated).
- **ETV compact tertiary:** Borkovits+2016 LTT + Gaia accel/RUWE; controls pass → 0 novel compact tertiaries (the "compact" cases drop to ~1–1.5 M⊙ at realistic inner mass); 3 partial-arc systems are DR4 targets.
- **CPM:** NULL (no wide tertiary for WG 26 / WDJ020915 / WDJ060042). Orphan TYC 7350-249-1: REFUTED. 5858574: ambiguous, watch list (Orbital solution, so the inclination bug never applied; NS mass 1.48, not BH).
- **eRASS1 re-exam** of the 2 top uncatalogued leads: A (5526308…) rejected (reddening artefact); B = Gaia DR3 3161546596480983040, an uncatalogued blue Galactic compact-object candidate (Gaia QSOC "AGN" class overturned by 5.3σ parallax + 36σ PM); journal created and deep-dive started; needs a spectrum; X-ray identification ambiguous.

Pending as of 2026-06-04: XP-catalogue ingest (network), bulk import of remaining hunt findings (offline), Object B deep-dive (running). Update 2026-06-10: all three completed in commit 7b7c4a2, and a further Object B item was closed in the Object B journal (see the 2026-06-10 detailed entry).

**Done offline 2026-06-03:** front-filter novelty gap closed. 306 in-pool Halbwachs+2023 `binary_masses` AMRFClassIII compact candidates ingested into the known-object store (`scripts/known_objects/ingest_binary_masses.py`); 26 objects of the candidate pool (incl. 5 Tier-1 NS + 1 Tier-1 BH) are published AMRFClassIII → not novel.

---

## Catalogs & findings ledger

**Catalogs in use:** authoritative list in `CATALOG_DEPENDENCIES.md`; known-object front-filter contents in `scripts/known_objects/`. Includes Gaia DR3 NSS (Orbital / AstroSpectroSB1 / OrbitalAlternative / Acceleration), Shahaf+2023 Triage I (J/MNRAS/518/2991), Gentile Fusillo 2021 WDs, Brandt HGCA, Kervella PMa, Ritter-Kolb + Downes CVs, Akras 2019 symbiotics, eRASS1-Gaia, LAMOST DR11 (V/162 MRS, V/164 LRS), APOGEE DR17, GALAH, RAVE.

**Findings and method criteria:**
- The astrometric mass function cannot separate a single dark companion from a hierarchical triple; the Shahaf AMRF classification is used for this distinction.
- No sin-i inflation for dark companions: M₂ comes directly from the photocentric mass function. The earlier `rv_amplitude_robust/2` error produced spurious mass-gap BHs.
- RV epochs clustered in one MJD window sample a single orbital phase; a low χ²/dof on few points does not count as a detection.
- Outburst-contaminated folds and minimum-of-noise depths at S/N<1 produced false periods and eclipses; periodograms are masked and significance uses permutation FAPs.
- Novelty check: a known object is not novel. The check uses several catalogues, not SIMBAD alone, and cross-matches by source_id and by J2000-back-propagated position (high-PM objects).
- NSS parallax bias: the single-star parallax is biased low for binaries; `nss_two_body_orbit.parallax` is used.
- APOGEE DR17 ASPCAP not yet ingested; the bulge-confirmation route without new observations is open as of this entry.

---

## Detailed entries

### 2026-06-03 — Object-journal and research-log system
- **Did:** built `docs/object_journals/` (README/TEMPLATE/INDEX + per-object ledgers), this research log and `scripts/journal/journal.py`.
- **Reason:** UCAC4 313 had been mislabelled as a "Shahaf recovery" (it is not in Shahaf). Dated, sourced ledgers make such claims checkable.

### 2026-06-03 — Project-wide candidate re-vet
- **Did:** re-checked all files and history (demoted/triple-favoured pool, Tier-2 and uncatalogued objects, parked lanes, all 17 dossiers, orphaned mentions) for dropped candidates.
- **Result:** the campaign null holds. No novel object was demoted prematurely; every demotion uses the Shahaf-AMRF / RUWE / flux-ratio criteria, which do not depend on the corrected inclination/sin-i calculation. Four items:
  1. **Orphan:** TYC 7350-249-1 (6021285355771958528), an SB1 BH candidate with M₂,min=3.36 M⊙, computed 2026-05-31 but not logged in the roster. SB1-only; RUWE=6.99 may be an SB2 artefact. Journal created; re-vet scheduled.
  2. **Front-filter novelty gap closed:** the known-object filter held only CV/symbiotic catalogues, so absence from it did not establish novelty for a compact candidate. Ingested 306 in-pool Halbwachs+2023 `binary_masses` AMRFClassIII compact candidates. 26 objects of the candidate pool are published AMRFClassIII → not novel, incl. Tier-1 NS 5446310318525312768, 5788346533133183744, 4042401027000908928, 6453094358292937984, 2208943221256515712 and Tier-1 BH 6281177228434199296; their published M₂ agrees with the cascade NS masses.
  3. **ELM/sdB and ETV-tertiary runs were infra-nulls:** the offline runs used wrong-regime data (ELM/sdB: a 100-d period floor against a minutes-to-hours target; ETV: only re-scored old Kepler EBs). Hypotheses untested; the 2026-06-03 re-attempts were blocked; network runs required.
  4. **5858574810404752256:** the only novel former compact prospect; its demotion sits on the triple/ambiguous boundary and used pre-bugfix calculations. Journal created; post-fix regeneration scheduled.
- **Minor:** CANDIDATES.md:100 generalises to "all triples" (not true for ~12 known Shahaf-PIII>0.5 objects, all known). HD 264291's M₂=1.94 depends on the bugfix but was regenerated with the fixed script (bias direction safe).
- **Script:** `scripts/known_objects/ingest_binary_masses.py`.

### 2026-06-05 — Prior-art screen of cross-survey lanes; prior-art gate added
- **Did:** literature check (arXiv + web) of the cross-survey ideas in progress.
- **Result:** each queued or proposed cross-survey lane has a 2024–26 published counterpart:
  - Gaia×eROSITA×ZTF accretors (the Object-B recipe) = Rodriguez et al. 2025, eRASS1 (arXiv:2505.10478), the same 3-step selection.
  - SN-runaway + X-ray = "high-velocity X-ray sources in the Gaia era" (arXiv:2601.02287, Jan 2026).
  - Fermi-unassociated × multiwavelength → spiders = COBIPLANE + ZTF×4FGL searches (e.g. PSR J1544−2555, arXiv:2509.09605); Fermi has enabled 62/84 of known spiders.
  - Multi-modal anomaly detection = SNAD/PineForest + AHA on the ZTF alert stream; they report ~68% non-astrophysical detections, consistent with the XP-pilot NO-GO.
  - Rubin/LSST is live (first alerts 24 Feb 2026, ~800k/night); the broker network (ALeRCE, ANTARES, Fink, …) performs multi-survey fusion.
- **Method:** candidates from these lanes are checked against the published lists, not only SIMBAD.
- **Built:** `scripts/litcheck/prior_art.py` (stdlib arXiv prior-art screen) and a prior-art gate, run before a new lane is opened.

### 2026-06-05 — Cross-survey quiescent-XRB lane — NULL
- **Did:** cross-matched the full Gaia NSS dark-companion pool (6468 non-demoted Tier-1/2 with M2_central>1 M⊙: 366 v2 robust-orbital + 6102 v3 acceleration) to eRASS1-DE (J/A+A/682/A34) at 5″, PM-propagated to 2019.96; coronal-saturation-ceiling test on every X-ray match. Widened from an earlier eRASS1 lane.
- **Result:** 110 matches = 1.70% X-ray-detected fraction. All 110 have log fx/fopt ≤ −2.09 (coronal; median −3.16); max Lx = 8.2e30 erg/s (below the 1e31–1e34 quiescent-XRB range). 3 nominally exceed Lx/Lbol=1e-3 (by ≤1.4×) and none has a robust or compact mass floor (all acceleration-channel, M2_min≈0.12). The 14 robust-orbital matches (incl. all Tier-1 NS) are far below the ceiling. Known recovery: 3160943617433900672 = RX J0702.0+1257 (XB*, K0IV-Ve+DA, WD companion; the high M2 is a period-degeneracy artefact). NULL: no quiescent compact accretor. Overlap with the earlier lane 1/110 → 109 newly X-ray-screened.
- **Caveat:** eRASS1-DE covers only the western Galactic hemisphere, and a fully dormant object is X-ray-silent; this lane tests only the faint-accretion hypothesis.
- **Logged:** 109 coronal-null matches → findings_register.csv (lane "eRASS1×NSS quiescent-XRB widened"). No source met the deep-dive criterion.

### 2026-06-05 — DR4 blind re-hunt harness — built
- **Did:** built `scripts/dr4_pipeline/rehunt/` (adapter.py, rehunt.py, diff.py, test_rehunt.py, README.md), which re-runs the v2 cascade on a new NSS table and diffs tiers against a DR3 baseline by source_id. Cascade code is imported from `scripts/streaming/v2_corrected/consumer_v2.py` (derive_row_v2 + all 5 filters), not copied; the harness only maps columns (DR3-raw / DR3-derived / DR4-stub profiles; a_phot from Thiele-Innes) and diffs tiers (NEW/PROMOTED/DEMOTED/VANISHED/mass and period movers). Running on DR4 requires filling `adapter.PROFILES['dr4']` with the DR4 column names.
- **Result:** the DR3 dry run reproduces the roster exactly: 0 tier mismatches / 56,100 rows, max|ΔM2|=0, Tier-1 NS+BH 199→199 (regression check PASS); repo test suite 50/50. Input staleness found (not cascade bugs): (1) the raw producer chunks lack the NSS `flags` column (F#33 added 2026-05-31, after the 2026-05-27 chunks), so F#33 has no effect there and ~51 demoted sources re-surface as Tier-1; (2) the committed `main_hunt_derived_v2.parquet` was written with M1 fixed at 1.5 (before select_m1/FLAME), so a re-run re-tiers about half the pool (~17.2k mass movers); the M1-corrected roster is `main_hunt_derived_v2_M1corrected.parquet`. For DR4: the export must carry `flags`, and the diff baseline is `_M1corrected`.

### 2026-06-05 — DR4 candidate re-fit engine — built
- **Did:** built `scripts/dr4_pipeline/refit/` (model/modelselect/prereg/synth/adapter/run + README; 8 files, stdlib+numpy/scipy/astropy). Re-fits the photocentric orbit from DR4 per-transit along-scan astrometry: 1-body vs multi-body (acceleration / double-Keplerian) via ΔBIC + nested F-test + accel-SNR + Gaia F2. Pre-registered confirm/refute thresholds are transcribed into PREREG and cross-checked against the document in tests. Uses the a_phot + cos i=|AG−BF|/a² (no sqrt; the 2026-05-31 bugfix) + f(M) chain. DR4 column names are isolated in one adapter map (the only stub).
- **Result:** 8 synthetic tests pass. Clean 1-body → 'single' (0% false-triple over 25 seeds); 2-body (274d inner + ~1300d outer) → 'multi' (ΔBIC≈+3850, accel-SNR~69σ, both periods recovered; 72% detection power). Per-candidate wiring verified on the 4 anchor orbits (CONFIRM for the nominal orbits; triple injection → REFUTE; HST/COS-FUV auto-flagged for WD-vs-NS-degenerate cases).
- **WDJ020915:** the bare f(M) at the pre-reg anchors gives M2=1.223, at the 1.2 M⊙ NS floor; ~1 in 7 noise realisations land on DOWNGRADE even with a perfect orbit. Decision: on DR4 day, run the full-TI-covariance MC, not the bare inversion.

### 2026-06-05 — Odd-axis D: PMa × RV-trend — NO-GO (duplicate of existing work)
- **Did:** feasibility and prior-art check for "Hipparcos-Gaia PMa × long-term RV linear trend → massive dark companion at 5-50 AU". The arXiv prior-art check failed (2× timeout + HTTP 429); the verdict rests on the internal-duplication finding.
- **Result:** already done in-repo in both forms. (A) Literal: the Pile-A HGCA BH-class family — HD 157033 (4111149395881722496, χ²=1583, Kervella snrPMa=14.85, P≈5-20 yr → AMBIGUOUS 0.4-6 M⊙) + 7 sibling demotion scripts (7/8 → luminous stellar); 0 confirmed compact. (B) Systematic: `acceleration_v3.parquet` (16,949 srcs) already computes joint acceleration + RV mass + inclination; 6,828 dual-signal; 3,761 RV-demoted; the surviving high-M₂ cases are period-degenerate artefacts (i pegged at 90°) and were not promoted.
- **Verdict:** NO-GO. Limits: inclination/period degeneracy; confirmation needs a telescope. Carried forward only as a pre-registered DR4 test. arXiv prior-art check to be repeated.

### 2026-06-05 — Odd-axis F: IR-variability × astrometry — NO-GO (structural null)
- **Did:** tested the increment over the earlier IR-nova and bulge-symbiotic (pure-IR) lanes: a measured Gaia DR3 NSS orbit combined with a WISE W1−W2 excess + WISE variability flag. Red NSS subsample bp_rp>1.4 (3,576) + 11 candidates → AllWISE XMatch at 3″ (99%); saturation/quality checks; Akras2019/store front-filter. arXiv prior-art check failed (HTTP 429, 2×).
- **Result:** raw join = 13 sources (0 known), all WISE-saturation artefacts (NSS is Gaia-bright, G≈6-11 → W1≈3-8, brighter than the W1≈8 saturation onset; K−W3≈0 → no dust). Among the 2,330 unsaturated red NSS giants, W1−W2 centres at −0.03 and 0 reach >0.2: no symbiotic excess. No candidate shows an excess.
- **Result (structure):** the DR3 NSS bright cap (G<13) and the dusty-symbiotic regime (G≈13-16) are essentially disjoint, the same limit as the bulge-symbiotic lane. Re-run on DR4 (fainter). Method criterion: a WISE W1≥8 & W2≥7 saturation cut is applied before an excess on bright NSS giants is accepted.

### 2026-06-05 — Odd-axis B: variability-phase × orbit-phase — NO-GO as discovery lane; self-audit passed
- **Did:** tested the photocentric-artefact validator (P_phot ≈ P_orb harmonic ⇒ possible artefact; mismatch ⇒ real orbit). Gaia TAP: 16 candidates + 1,014 NSS-Orbital × vari-period pairs. arXiv prior-art check failed (HTTP 429, 4 attempts); web search used instead.
- **Result (prior art):** not novel. Holl+2023a/b, Halbwachs+2023 and Bashi+2022 characterise it; DPAC pre-filters scan-angle spurious periods out of nss_two_body_orbit; `gaiadr3.vari_compact_companion` is the complementary product.
- **Result (feasibility):** 0/16 candidates are VARIABLE or in vari_summary → no period to match → no flag for any candidate. Population flag rate 0.0% (control 0.0%). The cause is structural: P_orb median 585d vs P_phot median 1.9d, max ratio 0.22, 0 pairs in the [0.3,3]×P_orb overlap, so a harmonic lock cannot occur for these long-period orbits.
- **Verdict:** NO-GO as a discovery lane (prior art; inoperative in this regime). As a self-audit it passes: none of the 16 candidates carries a photocentric-variability period artefact. It applies only to short-P NSS orbits (P≲tens d), rare in the pool.

### 2026-06-05 — Cross-survey spider-MSP hunt (Fermi 4FGL-DR3 × eROSITA eRASS1-DE × Gaia DR3) — NULL, parked
- **Did:** took 4FGL-DR3 (IX/67; 2154 unassociated), cross-matched eROSITA eRASS1-m within each 95% γ-ellipse (1152 in the western-hemisphere footprint; 733 with an in-ellipse X-ray source), front-filtered ATNF (B/psr) + SpiderCat (J/ApJ/994/8), required a faint Gaia DR3 optical counterpart with significant Galactic PM (anti-blazar criterion), then VSX/SIMBAD/store novelty check.
- **Result:** 0 novel spiders. The 238-Fermi / 384-pair candidate set is dominated by chance star + X-ray alignments at low |b| (count tracks stellar density: 189 at |b|<5° → 41 at |b|>20°). The 5 distinctive survivors are all known (2 VSX CVs incl. J1528.2-2448 = Gaia 6238744394658069376, 2 YSOs, EBs). Positive control passed: 12 known pulsars / 5 SpiderCat spiders recovered, incl. full source-level recovery of the J0639.1-8009 redback triple (eROSITA J064100.6-801127 + Gaia 5207836863615934080).
- **Method:** the anti-blazar discriminator on Gaia is significant Galactic proper motion of a faint counterpart (spider companions pm_snr≈5-36; blazar cores ≈0); a Gaia-variability or high-parallax requirement would reject distant or faint spiders.
- **Decision:** parked; confirmation needs radio/γ pulsation timing. eRASS1-DE covers only l∈[180,360]; the eastern Galactic plane is not covered → re-run when eROSITA-east is public. 2 CV recoveries → findings_register.

### 2026-06-05 — Odd-axis G: Galactic kinematics × companion mass — NULL (opposite sign)
- **Did:** derived UVW + Toomre for 641 compact-favoured (NS+BH) + 149 Tier-1 vs 53,659 stellar-companion NSS binaries, from the local Sahlmann gaia_source_astrometric_orbits parquet (169k NSS, 87% real Gaia RV; 100% of the hunt sources present). galpy absent → velocity space only. arXiv prior-art check failed (HTTP 429 on all attempts, incl. a direct fallback).
- **Result:** the hypothesis that compact-companion binaries are kinematically hotter/older (thick disk/halo, SN kicks) is falsified in the opposite direction: the compact-favoured pool is colder / more thin-disk. Thick+halo 0.9% [0.3-1.7%] vs 3.8% (Fisher p=1.5e-5, OR=0.24); σ(Vtot) 25.6 vs 31.7 (KS p=9e-8). Holds against a distance/magnitude/colour-matched control (KS p=2e-6). All 4 named candidates with a Gaia RV are thin-disk.
- **Interpretation:** the missing high-velocity tail expected for SN-kicked remnants is most simply explained by a contamination-dominated high-f(M) pool (unresolved triples / degeneracy-inflated f(M)); this is kinematic support for the campaign null, independent of the Shahaf AMRF axis.
- **Decision:** include the demographics result as a box in the limits/methods paper (supports f<5.7e-5; DR4 prediction: real DR4 remnants should populate the high-Vtot tail). The general method is not novel; the differential framing (high-f(M) pool runs colder ⇒ contamination diagnostic) is the new element. The arXiv prior-art check is to be re-run before that framing is used.

### 2026-06-05 — GALEX UV excess × astrometry: not pursued as a search; adopted as a vetting screen
- **Method:** UV-excess companion typing on the NSS pool and the candidates: GALEX AIS (II/335), 8″ cone, photosphere-normalised UV-excess σ; hd*_pma 2-component SED fit.
- **Prior art:** Makarov 2017 (arXiv:1705.01114); Shahaf+2023 Triage II (2309.15143, WD census on the same NSS pool); Garbutt/Parsons+2024 WD-pathways X (2403.07985, Gaia orbits for known UV-excess binaries). Photometric counterpart of the Shahaf AMRF test.
- **Re-test (5/15 NUV-detected):** WDJ060042 (tier STRONG) excess +0.09 mag / +0.4σ, no hot companion, still compact-compatible (HST/COS needed). WDJ205650 (confirmed He+He double degenerate) +9.2σ NUV / +5.8σ FUV, positive control. WDJ020915 not detected (AIS depth). 1593152 −13.6σ "deficit" is a single-temperature blackbody artifact for cool primaries (use a model atmosphere for Teff≲6000 K).
- **Decision:** Not pursued as a search (published; for compact candidates UV only rules out a hot companion). Adopted as a vetting screen: reuse companion_excess_sigma; model atmosphere / Makarov NUV envelope for cool primaries; flag NUV excess ≳+0.3 mag at ≥3σ with FUV corroboration.
- **Logged:** ledger rows in the WDJ060042 and WDJ020915 journals.

### 2026-06-05 — Isolated neutron stars selected by absence of a binary signature: closed
- **Method:** eRASS1-DE X-ray sources selected as single, BP−RP<0.5, RUWE<1.4, log fx/fopt>−1. Controls: XDINS RX J1856 and RX J0720 (in footprint, soft). Population test on a 161-source high-|b| cone with Gaia DSC class probabilities.
- **Result:** Isolated NS have V≈25–28 (RX J1856 V=25.6), 4.6–7.6 mag below Gaia G≈21; neither control has a Gaia counterpart. The full cut leaves 8 survivors, all Gaia DSC PQSO=1.000; 50/67 X-ray-bright counterparts are extragalactic. No usable parallax at G≈20.8 (Object B has 5.3σ). The discriminant (soft kT≈45–100 eV blackbody) needs spectral fitting plus a V>25 non-detection (telescope).
- **Prior art:** eROSITA-DE team (NWAY + soft-spectral method): Kurpas/Schwope+2024 (arXiv:2405.12846; 33 new XDINS candidates, nothing brighter than V≈25 in optical follow-up); Salvato+2025 (2509.02842).
- **Front-filter gap:** the known-object store has no AGN/QSO catalogue, so absence from it does not show novelty in extragalactic-prone lanes. Action: add Milliquas.
- **Decision:** Lane closed.

### 2026-06-05 — Gaia QSOC/DSC pipeline rejects as a selection axis: closed
- **Method:** Anchored on Object B (3161546596480983040); its qso_candidates row reproduces the journal (plx 5.34σ, PM 36.3σ, crf=False, DSCq=0.505, z=4.36). qso_candidates 6.65M; astrometric_selection_flag=False 4.75M (71%); Object-B-like (0.45<DSCq<0.6, z>2, asf=F) 147k. Top-2000 with plx_SNR>8: 100% non-CRF, median PM_SNR≈62, 77% blue and subluminous (median M_G≈12.8, hot-WD sequence).
- **Result:** 58/60 blue subluminous rejects already catalogued, 57 as WD/WD?; they are the Gentile-Fusillo WD catalogue (GF21 uses the same parallax/PM cut; Object B is in it).
- **Prior art:** QSO purification (CatNorth, Quaia, Apsis III); WD recovery (GF21); X-ray + colour accretor subset (Rodriguez+2025). KUV 23182+1007 (suspected AM CVn, a quasar) shows a reject is not a compact-object indicator.
- **Decision:** Lane closed: ~97% catalogued WDs; Object B stood out by its eRASS1 X-ray detection; the rest reduces to the null eRASS1×Gaia lane with a QSO pre-filter.

### 2026-06-05 — Asteroseismic primary masses on the NSS pool: null
- **Method:** APOKASC-2 (J/ApJS/239/32) + Yu+2018 (J/ApJS/236/42) = 16,566 unique-KIC giants × Gaia NSS (3″): 46 with a mass-function orbit (32 AstroSpectroSB1 + 14 Orbital), 19 pass the quality cut. M2 recomputed with seismic M1 (project f(M) convention, no sin i inflation). Local match on a Kepler-field download (Gaia upload crossmatch returned HTTP 500).
- **Result:** All 19 previously had default M1=1.5; seismic median 1.59, |ΔM1|≈0.43. Maximum minimum-M2 (sin i=1) 1.97 (KIC 11502218 = Gaia 2132620694633811456, already demoted by F#30); 0 compact/NS, 0 mass gap. Seismic masses 0.95–2.48. SIMBAD: all RG*/HB*/SB*.
- **Decision:** Not pursued: established area (APOGEE-Kepler seismic binaries; Gaia NSS × Kepler seismology ~2022–24); at most ~46 systems (TESS too weak for P~0.6–4 yr). Possible use: seismic vs catalogue M1 check. arXiv prior-art check incomplete (rate-limited); manual re-check needed.

### 2026-06-05 — Ba/CH stars × Gaia NSS: feasible, not novel, parked
- **Method:** Escorza+2017 (VizieR J/A+A/608/A100, 437 Ba/CH/dwarf-Ba/C stars) → 400/437 (92%) in Gaia DR3 → 60 with an NSS orbit (~14%; SB1=35, AstroSpectroSB1=17, Orbital=7, OTS=1); 25 AMRF-derivable (Shahaf-validated AMRF-from-Thiele-Innes code in prime3_deepdive_2026_05_29.py). Per-star cones and batched source_id queries (tap_upload returned HTTP 500).
- **Result:** AMRF photocentre masses 0.31–0.84 M⊙ (median 0.60, CO WD); SB1 f(M) lower bounds 0.01–0.70 M⊙; none >1.0 M⊙. Gaia periods match the literature (HD 50264: 916 vs 910 d), validating the AMRF pipeline. 0/60 in the known-object store (below the Class-III threshold); SIMBAD: SB* with Ba/CH types.
- **Prior art:** McClure; Jorissen/Pourbaix; Escorza+2017/2019 and Jorissen+2019 (WD companion masses of this sample); Shahaf+2023/24 (AMRF); Escorza/Shahaf Gaia DR3 Ba-star astrometry 2023–24.
- **Decision:** Parked (sample, objects and method published); kept as an AMRF pipeline validation (passed). arXiv check incomplete (rate-limited); manual re-check needed before any novelty claim.

### 2026-06-05 — Astrometric-microlensing event predictor: built and validated; candidate cross-check null
- **Built:** `scripts/microlensing/`: geometry.py (Einstein radius, A(u), dark-lens and luminous-blend centroid shift, PM+parallax closest-approach solver, mass-from-shift inversion); predict.py (Gaia DR3 high-μ lenses → background neighbours along the 2024–2030 track → ranked events); validate.py; apply_candidates.py; README; 13 offline unit tests (pass).
- **Validation:** LAWD 37 (Gaia DR3 5332606522595645952; Klüter+2018 prediction, McGill+2023 measurement): θ_E 31.4 vs 32.8±0.3 mas (4.4%, in band); TCA J2019.860 exact; major-image shift 2.83 vs ~2.8 mas; mass 0.61 M⊙. Fixed a 2× parallax-factor bug (astropy Earth ephemeris, <0.1 mas).
- **Applied:** 12 CANDIDATES.md source_ids as lenses 2024–2030: null (PM 5–48 mas/yr, tracks <0.3″). 3 WD-locus lenses among top sample events (LAWD 37 and two with ~30–47 µas shifts).
- **Prior art:** Klüter+2018 (×2), McGill+2018/19/20, Bramich 2018, Klüter+2024.
- **Scope:** DR4 re-run tool (GAIA_TABLE→gaiadr4), not a new channel; dark lenses without a Gaia entry cannot be predicted. Tests: `tests/test_microlensing.py`.

### 2026-06-10 — Project review and first follow-up items
- **Method:** Repo audit; 36 lane ideas → 12-lane shortlist, each checked for prior art, duplication and no-telescope feasibility. Verdicts: `docs/reports/project_review_2026_06_10.json`.
- **Lanes kept:** (1) Freeze the DR4 prereg as a citable document plus a watch list of GF21 WDs with RUWE/AEN excess and no NSS solution (missed by the DR4 re-hunt); prereg coverage extended first (Addendum A, same day). (2) RVS mean-spectrum SB2 screen on the 23 Tier-1 NS with has_rvs (sensitivity 15–30% flux ratio; possible until DR4). (3) M1 correction: substellar bins still at M1=1.5 (81/82 main, 113/115 relaxed), acceleration_v3 100% default → re-tier, BD extraction, [Fe/H]<−1 astrometric-BD-host slice (front-filter vs Stevenson+2023/DPAC/Wallace&Casey 2026/GaiaPMEX); the dossier reference "Bailer-Jones & Kreidberg 2026" could not be located, re-check. (4) DR4 joint epoch-astrometry + epoch-RV fitter (absent in repo); validate on the 854 FPR×SB1 overlap (AstroSpectroSB1×FPR overlap empty).
- **Lanes closed:**
  - Occurrence-limit paper: El-Badry+2024 (arXiv:2405.00089) measured ~1e-6, ~50× below our f<5.7e-5, so our limit is non-constraining; kinematics box kept as a methods element only.
  - Gomel vari_compact_companion × archival RV: best candidates refuted by Nagarajan & El-Badry 2023; 17/6306 have NSS rows.
  - FPR-LPV blind RV Keplerian search: Nagarajan+2024.
  - Eastern 4XMM/2SXPS/CSC screen: ~0 expected detections.
  - APOGEE-ASPCAP both-arms ingest: bright-limit mismatch, discriminants need telescopes; closes the "missing data" item.
  - Bug stress test of published lists: Bashi+2022 = bit-13 audit; Gomel join empty; DR4 predictions for published lists folded into lane 1.
  - Also: MARVELS, radio quiescence, DASCH as survey, OGLE-ETV, self-lensing, CPM ages, TESS BD transits, dark-lens π_E, e–P mining (reasons in the JSON).
- **Gaps:** ASAS-SN/ATLAS photometry unused though the pool is G≈6–13, where ZTF saturates. No publication monitor for the 4 novel candidates. No security review of the hunt console / web-ingest path. eROSITA-east is held by IKI with no scheduled public release.
- **Phase 1 done:** F#33 tier propagation (roster 161→116); WD full-TI MC regenerated and reproduced (`docs/reports/wd_ti_mc_regen_2026_06_10.md`); prereg Addenda A+B (coverage 4/9→9/9; floor convention; WDJ020915 MC requirement); register backfill (25 AMRFClassIII + 13 relaxed Tier-1 → 1,997 rows); GALEX ledger rows added to WDJ205650 and 1593152; `docs/reports/` created for lane outputs (three earlier outputs, incl. the prereg mass-MC provenance, had been lost from temporary storage).
- **Closures:** XP ingest, register bulk import, Object B follow-up (commit 7b7c4a2). Object B ZTF re-check inconclusive (no ZTF source within 2″); classification needs a spectrum; CANDIDATES.md updated.
- **Correction:** An earlier entry called the HD 157033 PMa test "(pre-registered)"; false at the time. It is pre-registered from Addendum A.4 (2026-06-10).
- **Phase 2 checks** (`docs/reports/phase2_archival_checks_2026_06_10.md`; 14 ledger rows): Object B GALEX null is a coverage gap (dossier S3 superseded; UV unconstrained). DASCH 1889–1989 excludes nova-scale outbursts of the blend (dwarf-nova scale hidden by the B≈13.7 floor). HD 157033 has no ESO archival spectra (Proxima control); its RV needs a telescope. No new public RV epochs for 1593152/3155543; LAMOST DR12 login-gated (watch item: re-query at international release).
- **Unrecoverable:** per-object verdicts of the 2026-05-28 ns_pool_triage and membership of three earlier per-object nulls (incl. the 2026-06-05 microlensing cross-check) were lost with temporary files; register rows say "triaged-in-aggregate"; no backfill.
- **Queued:** RUWE flag in consumer_v2 with cascade-regression test; GALEX and Milliquas checks in vetting; lanes 1–4; ASAS-SN/ATLAS bright-pool screen; publication monitor; CITATION.cff/version reconciliation; unified-parquet regeneration.

### 2026-06-10 — F#34 astrometric-quality caution flag and cascade-regression test
- **Did:** `filter34_astromqual` in `consumer_v2.py` (the 2026-05-30 RUWE follow-up) as a caution flag that never changes the tier. Fetched NSS `goodness_of_fit` (F2) and `ipd_frac_multi_peak` for all 1,251 candidate-tier sources (`docs/reports/f2_ipd_fetch_2026_06_10.csv`); merged into the three `_M1corrected` parquets (`nss_gof_f2`, `ipd_frac_multi_peak`, `filter34_v2`, `filter34_reason_v2`; `scripts/apply_f34_astromqual_2026_06_10.py`); wired into `derive_row_v2` for the DR4 re-run.
- **Design:** Tier-1 spans RUWE 2.6–28.8 (median 6.1), normal for photocentric binaries; an absolute cut would flag 52% at >6 (motivating cases 6.46/9.35 lie in the bulk). Criteria: F2 > +5 (prereg "unreliable" convention); ipd_frac_multi_peak ≥ 4 (resolved double); RUWE ≥ 12.5 (Tier-1 P95). Explicit `NO_DATA` when all inputs are missing.
- **Result:** 51/108 main + 3/9 relaxed Tier-1 NS flagged, incl. GALEX J145250 (F2=+8.0, the motivating case), HD 75567 (triple favoured, F2=+6.3), 2129927539681151872 (F2=+17.2). HD 264291 flagged (F2=+6.8; marginal astrometry, sig 12.5); independent RV confirmation, so flag, not cut.
- **Cascade-regression test:** passed with conditions: 63/63 pytest; BH2 fixture Tier-1 (1/1); 6/6 negative controls rejected; frozen tiers reproduced; 3 misses by design (BH1 F#31 NO_DATA, BH2 F#30, BH3 no NSS). Conditions closed the same day: (1) stale BH1 expectation in `benchmarks.json` ("Tier-1 BH" → by-design Tier-2 string) fixed; (2) HD 207141 entry "heaviest BH candidate M₂=7.57" corrected and journal created (`docs/object_journals/6811355413155399040.md`) with the Shahaf PIII=1e-5 triple verdict and an open 1.31 vs 1.75 M₂ reconciliation item (demoted table vs M1-corrected parquet); (3) the 49-object Tier-1×Shahaf cross saved to `docs/reports/tier1_x_shahaf_t1_2026_06_10.csv` (9/49 PIII≥0.5, median 0.015; consistent with a triple-dominated Tier-1); (4) "93% recall on 27 systems" marked unverified in CANDIDATES.md (truth set never committed; CITATION.cff says 70); re-commit or revise before release.

### 2026-06-12 — Data access: ZTF ZFPS granted; LAMOST DR12 requires a host institution
- **ZTF ZFPS:** account granted (IPAC). Request prepared (`scripts/ztf_zfps_objectB_request.sh`) for Object B and the 4.76″ neighbour (contamination control); user submits; results by email (queue can exceed 7 d).
- **LAMOST:** DR11 public (checked 2026-06-10; nothing new for 1593152/3155543). DR12+ collaborator access requires a Chinese host institution, host researcher and recommendation letter (form sections 5+7); not available. Plan: re-query at the DR12 international release, or via a collaborator.
- **Object B contamination:** Gaia BP/RP diagnostics clean (C*=+0.056, 0% blended transits, ipd_mp=0). The neighbour is a close double (ipd_mp=91, RUWE 18.95), weakening the coronal-ceiling argument to ~1.3×. X-ray ID rests on the positional match (unaffected). Ledger row added.

### 2026-07-01 — Object B: PS1 DR2 photometry; ZFPS access revoked
- **ZFPS:** revoked (institutional policy). Replacement: local forced photometry on public ZTF difference images (ztfquery/ztflc-type; anonymous IBE feasibility test) and a status email to IPAC (user).
- **PS1 DR2:** suggested ~0.1–0.3 mag variability. Resolved 15-epoch photometry 2011.8–2014.3; scatter p89–p100 of a 37-star control; g-band bright-state offset at percentile 0 (4/4 detections 0.24–0.38 mag above the stack+forced average); no outbursts; deblending loss a stated confound. Consistent with CV flickering; needs a resolved ZTF light curve.
- **LSST alerts:** not completed (Fink unreachable locally; ALeRCE/ANTARES ZTF-only; Lasair token-gated). ZTF alert nulls at both positions through 2026-06 (no bright outburst 2018–2026).

### 2026-07-01 (late) — Object B PS1 variability claim retracted; variability untested until DR4
- **Retraction:** with blend-geometry controls (9 faint stars 3–6″ from a bright one) Object B's scatter is at percentile ~67, typical. The signal is a neighbour halo/wing systematic (seeing over-subtraction sign, chip-aliased "seasons", anticorrelation with the neighbour, error-model-inflated sigmas). The numbers reproduced; the isolated-star controls were the error.
- **Method criterion:** for blended targets the control sample must match the blend geometry, not only the magnitude.
- **Status:** variability untested in all archives (PS1 undecided at this geometry; ZTF floor 0.21–0.36 mag; ATLAS/DASCH blend-limited), except: not a dwarf nova (ZTF duty cycle <5–9%, 2018–2025); no bright outburst 1889–1989 (DASCH, nova scale) or 2018–2026 (alerts). Subtype needs a spectrum; variability test deferred to Gaia DR4 epoch photometry (Dec 2), which resolves the pair. Results and retraction ledgered; status and dossier never changed.

### 2026-07-02 — PS1 forced-warp variability screen of the uncatalogued register
- **Method:** 155 uncatalogued register objects; MAST PS1 DR2 forced-warp TAP; population-calibrated thresholds; blend-geometry check (flags Object B UNRELIABLE).
- **Result:** near-null. 149 Gaia-resolvable: 94 not in PS1 (93 at Dec<−30; the register is mostly southern, so LSST is its time-series source), 28 quiet, 11 saturated, 5 blend-flagged, 5 too few epochs, 3 seeing systematics (demoted), 1 photometry inconsistent (3851730042602531584: forced vs mean 2-mag discrepancy, RUWE 4.08 unresolved pair; needs image-level inspection).
- **Candidate variables** (pending re-check; possibly ordinary active M dwarfs, no compact-object signature): 3137896273168859648 (1eRASS J073600.6+034909; time-coherent 0.2–0.6 mag; X-ray M dwarf; beat 5/5 matched controls and systematics checks); 6315134987927550592 (weaker; 92 mas/yr PM caveat). No follow-up started.
- **Method criterion:** PS1 forced-warp formal errors are ~10× underestimated; calibrate thresholds on the population, not on formal errors.

### 2026-07-02 — ASAS-SN bright-pool screen: no credible detections
- **Data:** 9 candidates, Sky Patrol v2, V+g, 2012–2025.
- **Result:** quiet, with floors: 1593152 (~3 mmag), 3155543 (~2), 5858574 (~2, g only), UCAC4 313 (~13, no flares), WDJ020915 (~16; ATLAS also quiet; consistent with a real orbit). Partly constrained (saturation at G≲10.5): HD 157033, HD 207141 (<~50 mmag), HD 264291. WDJ060042 too faint. No outbursts or eclipses.
- **Rejected signals:** permutation detections (FAP 5e-4 to 1e-3: HD 207141 at P, HD 264291 at P/2) failed a local red-noise null (power at P vs 500 random long periods, same light curve) and per-camera coherence (saturation red noise).
- **Method criterion:** for long-period signals in bright/saturated light curves a white-noise permutation FAP is insufficient; require the local red-noise null and camera coherence.
- **Next:** ASAS-3 / KELT / Hipparcos for the three saturated targets. 9 ledger rows appended.

### 2026-07-02 — APOGEE DR17 ASPCAP ingest: bulge-symbiotic lane closed; portfolio RV check null
- **Catalogue:** `data/external_catalogs/apogee_dr17/allStarLite-dr17-synspec_rev1.fits` (1.83 GB, 733,901 rows, gitignored, from SDSS SAS); has GAIAEDR3_SOURCE_ID for direct DR3 joins.
- **Arm A (bulge symbiotics):** Akras+2019 (J/ApJS/240/21, 410 rows) × allStarLite 3″: 25/410 overall, 1/123 bulge box (|l|≤10, |b|≤10), 2/193 inner plane (|b|≤5), 0 at 3–10″. The bulge match (AS 255) has NaN TEFF/LOGG (ASPCAP not converged). Reproduces the 2026-06-10 probe (1/140). APOGEE fiber coverage cannot confirm bulge symbiotics; lane parked for 4MOST/SDSS-V; the lost 137-candidate list is not regenerated.
- **Arm B (20 journaled objects):** 2/20 matched. 1593152388271709824 single visit (no constraint). 4111149395881722496 (HD 157033) VSCATTER=35.7 with SUSPECT_BROAD_LINES/VSINI_BAD, matching the existing "unreliable APOGEE RV" caveat. No new RV constraint for the 7 active candidates (5 not observed). Nulls logged for all 20, incl. first APOGEE rows for 2909342818326298112, 3161546596480983040 (Object B), 332248057157474176, 5612039087715504640 (UCAC4 313).
- **Arm B2 (register, 1,997 rows):** 25 matched; 5 with NVISITS≥3 and VSCATTER≥1 km/s, all known (1 WR spectral-fit failure, 3 eRASS1 known objects, KIC 4069063 = Conroy+2014 triple); 0 uncatalogued flagged.
- **Note:** `data/external_catalogs/apogee_dr17_v2_pool.csv` (559 rows) is an SB9-style RV pool, not an APOGEE extract; matched 0/20. 20 ledger rows appended via journal.py.

### 2026-07-02 — Hipparcos/ASAS-3/KELT screen of three saturated targets
- **Targets:** HD 157033, HD 264291, HD 207141 (SIMBAD-verified; HD 207141 = 6811355413155399040). Local red-noise null and dataset coherence applied.
- **ASAS-3:** all 3 (368–781 epochs, 7–8.8 yr, floors 12–18 mmag) quiet. HD 264291's marginal P/2 (FAP 0.10) fails coherence, consistent with the ASAS-SN P/2 rejection, from an instrument a decade earlier.
- **Hipparcos:** only HD 157033 (Hp scatter 25 mmag, constant, 1989–93); other 2 absent (Tycho-2 controls); raw epochs not public. **KELT:** unusable for all 3 (2 outside fields, 1 saturation-excluded; verified against the archive).
- **Verdict:** HD 264291 and HD 207141 photometry closed; HD 157033 mostly closed (36-yr baseline without outbursts; mass ambiguity needs DR4 or a telescope). Report: docs/reports/bright_trio_screen_2026_07_02.md; 9 ledger rows.

### 2026-07-02 — PS1 candidate variables re-checked: 1 artifact, 1 active M dwarf
- **Method:** 11 matched isolated controls per band (screen: 5), epoch-level seeing/sky/chip/psf-ap diagnostics, PM propagation, ZTF check.
- **3137896273168859648 (1eRASS J073600.6+034909): retracted.** Signal drops 0.96→0.29 mag without ferr>10% epochs; residual 92–97% chip-locked zero-point offset; chi2-driving epochs have negative aperture flux; seeing ρ up to +0.77; ZTF (839 epochs) flat. Stays register tier.
- **6315134987927550592 (1eRASS J152614.8-111331): variable, ordinary active M dwarf.** 100th percentile of controls; psf-ap co-motion +0.90 to +0.95; ZTF zi chi2/dof=26; ~0.1 mag dip-dominated spot modulation, no coherent period, d≈121 pc, coronal X-rays. Journal created (21st). Not a compact-object candidate.
- **Status:** 0 novel compact objects; PS1 register screen complete. Register rows, 4 ledger rows, journal entry appended.

### 2026-07-03 — eRASS1-register time-domain classification: go/no-go check passed
- **16 CMD-bridge objects vs:** Wang & Takata 2025 (J/A+A/698/A321; 444 objects, 177 new CV candidates): 0 matches, nearest 1.2°. Fang+2026 (arXiv:2606.01085; 43 COB candidates): 0 matches; their Dec −27..+32 misses ours (−35..−87). Freund+2024 HamStar: all 16 associated but Coronal=0 for all (mild support for accretors, not prior art). VSX, SIMBAD: no entries. KnownObjectStore: known=False ×16.
- **Result:** pool 15 (Object B excluded): 10 southern + 5 northern; preregistered rule ≥5 southern; build proceeds. Table: docs/reports/erass1_lane1_gate_table_2026_07_03.csv.
- **Next:** phase 1 (ASAS-SN Sky Patrol v2, 137 register objects) started; phase 2 (ATLAS forced photometry, needed for Dec<−50) awaits a user account at fallingstar-data.com/forcedphot.

### 2026-07-03 — eRASS1-register classification, phase 1 (ASAS-SN): no clean accretor; 8 leads pending ATLAS
- **Data:** 136 objects (Object B excluded); 98 in the ASAS-SN catalogue; 87 light curves (11 lost to a backend outage; 38 not in the ASAS-SN input catalogue, left to ATLAS).
- **Outbursts:** one cross-camera outburst, 6482924963452562432, is almost certainly a blend: HD 197847 (G=8.56, 6.5″ away, near saturation) dominates, and a 1.3-mag blended outburst from the G=14.8 target is physically excluded. 7 single-camera candidates (1.2–2.0 mag) pending ATLAS.
- **Periods:** 17 screened: 0 coherent, 17 marginal (1-d/0.5-d/lunar-month aliases failing cross-camera coherence). No magnetic-CV signal.
- **Bridge objects:** 10/15 with light curves (quiet or aliases). Lead: 6342358797048816128 (1eRASS J195248.1-872256, G=18.7, Dec −87°), one unblended 2.04-mag one-night brightening, candidate-artifact tier; only ATLAS covers it. 5/15 untested (4 outage, 1 no counterpart).
- **Checks:** 2 bugs fixed (outburst-clustering inflation 12→1; red-noise null saturating on noise); calibrated on synthetic data and the 2026-05-28 CV-period retraction.
- **Ledger:** bridge-object rows deferred to one ASAS-SN+ATLAS write; final tiers after cross-confirmation. Report and proposed rows: docs/reports/erass1_lane1_asassn_phase1_2026_07_03.md; table erass1_lane1_verdict_asassn_2026_07_03.csv (136 rows). ATLAS phase 2 in progress.

### 2026-07-04 — Lane 1 lead 6342358797048816128 refuted by TESS
- ASAS-SN lead, bridge object 1eRASS J195248.1-872256 (dec −87°, 2.04-mag single-camera brightening): refuted as an artifact.
  - TESS Sector 67 covers the event epoch (MJD 60130-60131 = 2023-07-05/06, after a JD→MJD correction) and is flat. It shows −0.11σ, against a predicted 91.8σ detection if real (worst-case dilution by the 12.7″ G=17.4 pixel neighbour).
  - No credible periodicity. SkyMapper/NSC baselines end in 2021/2017.
- The object remains an uncatalogued CMD-bridge eRASS1 source. Astrometry is unreliable (RUWE 4.18) and Gaia in_qso_candidates=True, so CV vs AGN is unresolved. Closed at register level.
- Method: TESS decides far-southern single-night events directly when it observed the epoch (south-ecliptic/CVZ coverage). The test is extended to other single-camera outbursters with events in 2018+.
- Provenance: docs/reports/lead_6342358797048816128_2026_07_04.md.

### 2026-07-04 — TESS epoch-coincidence test on 5 ASAS-SN outbursters: 2 refuted, 3 not covered
- **Refuted** (TESS covered the epoch, flat):
  - 4756545648896550400 event 3: S61, +0.38σ vs 80σ if real.
  - 5495005386415020032: 60-day span; S61/62/63 all 0.00σ vs 220-352σ if real. 0.55″ blend; RUWE 17.7.
- **Not covered** (TESS sector gaps; ATLAS pending):
  - 4631587866085502592 (1010 d gap)
  - 4809992221923571840 (1761 d gap)
  - 5523321418610194048 (687 d gap)
  - 4756545648896550400 events 1-2 (pre-TESS / 573 d gap)
- Correction: a far-southern position does not imply TESS coverage. TESS has multi-hundred-day gaps between sectors even near the CVZ, so coverage is checked per target and epoch.
- Tally (7 outbursters): 3 refuted (6342358797048816128, 4756545648896550400 event 3, 5495005386415020032); 0 confirmed. 4 are ATLAS pending: the 3 not covered, plus pre-TESS 5222573240011621760.
- Provenance: docs/reports/erass1_tess_outburst_batch_2026_07_04.csv.

### 2026-07-04 — Lane 1 ATLAS screen of 15 CMD-bridge objects: 1 chromatic-outburster lead
- All 15 CMD-bridge objects have complete ATLAS forced photometry (c+o, 2015-2025, ~500-6000 epochs each); 112/137 register objects were still downloading.
- Screen: outbursts (c/o coincidence required); LS periods (FAP, red-noise null, c/o coherence); blends.
- **Lead:** 5808732887468490368 (eRASS1 J163428.7-693348).
  - It is the only chromatic-consistent outburster: 7 c + 22 o coincident events, a DN signature, on a CV-locus X-ray source.
  - Flagged ambiguous_blend (3 Gaia neighbours <15″).
  - Follow-up started: outburst localisation (target vs neighbour), novelty, Lx.
- **Others:**
  - 2 single-band outbursters (5086290/4933000); their c and o events do not coincide.
  - 3 accretor_possible (4822674/2993086/4688120): marginal non-alias period, no outburst, no blend.
  - 9 coronal_or_quiet / ambiguous_blend quiet.
  - 0 cross-survey coincidences. Most lack ASAS-SN data; ATLAS is the only time-domain source in the deep south.
- Provenance: docs/reports/erass1_atlas_bridge_2026_07_04/verdict.csv and 15 plots. 6 register rows appended. ATLAS download at 34/137.

### 2026-07-04 — Lane 1 discovery pool closed: both ATLAS bridge leads retracted
- **Retracted:**
  - 5808732887468490368: crowded-field PSF-fit artifact. chi/N degrades monotonically with flux; RUWE 24; the quality-cut light curve is flat. The bright 6.85″ neighbour is a VSX RS CVn.
  - 4933000119641126912 (clean PSF, single band): ATLAS camera-unit-02a reference-template step at MJD~58900. A flat plateau at the true magnitude, then a hard step to zero; o band flat; negative excursions 9:1.
  - 5086290: crowded-field artifact suspect (82% bad fits).
- **Result:** the 15-object pool is null, with 0 confirmed accreting binaries. The 3 accretor_possible objects (4822674/2993086/4688120) have marginal periods only and were not followed up.
- **Method criteria for ATLAS outburst screens** (they would have rejected both leads):
  - Reject epochs with PSF-fit chi/N>>1. An outburst whose chi/N degrades with flux is a blend artifact.
  - Check the camera-unit `Obs` ID. A plateau-then-step in one camera unit or epoch range is a template change, even at clean chi/N.
  - Apply a negative-excursion symmetry control.
- Remaining (ATLAS 34/137): 4 TESS-not-covered outbursters and ~105 coronal/quiet objects, to be checked with these criteria.
- Provenance: docs/reports/erass1_atlas_bridge_2026_07_04/ (verdict.csv, follow-up reports, plots).

### 2026-07-05 — Lane 1 closed: all 7 eRASS1 outbursters adjudicated, 0 confirmed accretors
- The 4 ATLAS-pending outbursters finished downloading (105/137). They were adjudicated at their event epochs using chi/N<50, negative-excursion symmetry and c/o chromaticity.
  - Refuted: 4631587866085502592 (c flat/symmetric); 4809992221923571840 (single c epoch, o flat, negative-dominated); 5523321418610194048 (39σ o spike flanked by physically impossible −18σ negative flux).
  - Not covered: 5222573240011621760 (no ATLAS data near its 2017 event).
- **Final tally:** 0 confirmed accreting binaries. Rejected:
  - 7 outbursters (3 by TESS, 3 by ATLAS, 1 not coverable);
  - 1 blend false positive (HD 197847);
  - 2 ATLAS bridge leads (PSF crowding; template step).
  - The 15-object pool is null. The ~105 coronal/quiet objects remain as housekeeping.
- The chi/N pre-filter, camera-unit `Obs`-ID check and negative-excursion control were applied across 5 rejected leads, together with the TESS epoch-coincidence method.
- ATLAS download restarted for the last ~32 coronal objects. Provenance: docs/reports/erass1_atlas_bridge_2026_07_04/ and register rows.

### 2026-07-05 — Discovery-menu gates: DESI DR1 = GO, DASCH one-dip = MARGINAL
- **DESI DR1 repeat-RV dark-companion hunt: GO.**
  - Per-epoch FITS pulled: 90 healpix, 32,641 epoch rows. DESI DR1 has been public since Mar 2025.
  - The MWS catalogue (Koposov+2026 arXiv:2505.14787) has >1M stars with >=2 epoch RVs.
  - Same-night epoch-pair fraction 18.9% (kill threshold >90%).
  - Usable pool (multi-day baseline, ZTF footprint, G16-18.5): ~480k (kill threshold <100-200k).
  - Prior art: one single-object RNAAS note (Smith 2026, Gaia DR3 3802130935635096832, front-filtered); no systematic survey.
  - Target regime: dark companions at G=16-20, beyond Gaia RVS.
- **DASCH one-dip period recovery: MARGINAL.**
  - Survivors: 13 clean / 18 including marginal (GO>=25, NO-GO<10).
  - DASCH DR7 access confirmed with daschlab: an RY Cnc control light curve (3,653 points) in 35 s; ~30-40 s per object.
  - The ZTF 81-dipper table is withheld for the ApJ supplement (29/81 in the preprint), which limits the funnel.
  - Related work: Tzanidakis & Davenport (ZTF list; DASCH+dipper work). The ASAS-SN team's DASCH attempt on one dipper was a null ("too much scatter").
  - Options: a 1-3 d run on the 13 clean survivors, waiting for the ZTF table, or deferral.
- **Tool fix:** scripts/litcheck/prior_art.py AND-quoted every query token. Long queries therefore returned a false "NO MATCHES" and missed the Smith 2026 note.
  - Now: fallback to an OR query on zero results, a related-work warning, and a web-search cross-check prompt.
  - Verified on the DESI query.
- Provenance: docs/reports/gates_2026_07_05/.

### 2026-07-05 — DASCH one-dip mini-campaign (13 survivors): null, lane closed
- The 13 clean ASAS-SN single-dip survivors were run through DASCH DR7 (daschlab): 0 periods recovered, 4 DASCH-null (scatter-limited), 9 with no historical dips.
- 4/13 (31%) are scatter-limited, with plate noise about equal to dip depth (worst J183210: 0.287 mag scatter vs a 0.31 mag dip). This matches the ASAS-SN team's DASCH result.
- Isolated single-epoch 3σ faint plates were not counted as dips (look-elsewhere, photographic outliers).
- Lane closed (null). Deferred: the ZTF 81-dipper table and the 5 marginal survivors.
- daschlab fixes: ECSV Time-mixin .jd read; manual AFLAGS-bitmask rejection. Provenance: docs/reports/dasch_mini_2026_07_05/.

### 2026-07-05 — DESI DR1 dark-companion hunt Phase 1 (RV-variability screen): 26,427-object tail
- **Route:** bulk per-healpix rvtab_spectra FITS, the only route with per-epoch VRAD/VRAD_ERR/MJD. Astro Data Lab TAP was rejected: desi_dr1.mws is coadd-only.
  - All 31,925 healpix (3 programs): 14.8 GB, 72 workers, ~23 min, 0.075% pixel loss.
  - 5,840,078 good epoch rows.
- **Funnel:** 1,211,271 unique stars (>=2 epochs) → 931,803 (baseline >=1 d) → 458,898 (G16-18.5, dec>-30) → 57,140 (p_const<1e-3) → 27,043 (dRV>=5σ) → 26,429 (STAR) → 26,427 not in the store. Front-filtering removed the Smith 2026 object, 3802130935635096832.
- **Caveats:**
  - The top-ranked objects (dRV 173-751 km/s, chi2_red 1e4-1e5) are suspected pipeline artifacts: RV failures, blended fibres, template mismatch. Ranking by dRV puts these first.
  - The known_objects store had zero VSX rows (built with --no-vsx), and live VizieR VSX queries were unreliable (empty on Algol; timeouts). A SIMBAD check of the top 30 found 3 of the top 17 already known (CRTS/ZTF variables). "Novel" here means not in the store and not in SIMBAD; VSX was not checked.
- **Phase 2 plan:**
  - (2A) Artifact rejection (dRV/chi2, RVS quality, SB2 as stellar). Novelty check against VSX, SIMBAD and published DESI RV-variable/binary lists.
  - (2B) ZTF periods → f(M) → follow-up of high-f(M) objects.
- Provenance: docs/reports/desi_hunt_phase1_2026_07_05/ (REPORT, candidates.csv.gz). Open item: rebuild the known_objects store with VSX.

### 2026-07-05 — DESI hunt Phase 2A (artifact rejection + novelty): 26,427 → 18,946; VSX gap fixed
- **Funnel:**
  - 26,427 → 20,488 after artifact rejection (5,939 removed). chi2_red>200 was the discriminant (3,926 rows).
  - The dRV>600 km/s ceiling removed zero unique rows; chi2_red rises from 39 to 8,100+ across dRV bins.
  - → 18,946 clean and novel.
  - 1,542 known (VSX 615, SIMBAD 1,347), mostly RR Lyrae, EB and rotational variables. The store matched 0 because of the VSX gap.
- **VSX gap:**
  - Cause: a VizieR primary-mirror outage; the cfa.harvard.edu mirror works.
  - Full VSX pulled: 10,304,362 rows, vs ~2.1M in older docs; the growth is from Gaia DR3 ROT entries.
  - Ingested into known_objects.parquet (1.04M → 11.3M rows, tag vsx_full) with scripts/known_objects/ingest_vsx.py.
  - The row-wise annotate() did not scale to 11.3M rows (killed at 5 min). Novelty came from a vectorised crossmatch. Open item: vectorise annotate().
- **Top candidates** (clean, novel, single-lined SB1s): dRV 30-98 km/s, 18-25σ, baselines 45-365 d, 5-8 epochs. Top 15, plus an outlier: 1487470319907416832 (dRV 155.9 km/s over 42.8 d, 10.3σ, novel).
- The 18,946 are uncatalogued significant RV variables, not identified dark companions. Companion type needs a period and f(M) (Phase 2B: ZTF periods on the top ~30, DESI RV fold).
- Provenance: docs/reports/desi_hunt_phase2a_2026_07_05/ (REPORT, clean_candidates.csv.gz, 18,946 rows).

### 2026-07-05 — known_objects VSX fix verified; annotate() scaling fixed
- Both Phase 2A open items closed. The store holds vsx_full (10,304,353 rows).
- **Verification:** the three objects Phase 1 missed now flag `known` via both `store.match()` and `store.annotate()`, all with tag `vsx_full`:
  - 1154769341272239616 → CSS_J150219.2+031156 (EB, 1.50″)
  - 1058868906306003072 → ZTF J104819.80+655559.4 (BY, 0.09″)
  - 1480681355298504960 → CSS_J142114.7+352838 (EB, 0.35″)
- **annotate() now scales to the 11.3M-row store:**
  - Cause: memory. It built a SkyCoord/KD-tree over the whole store and assembled results with per-row `.iloc` over StringDtype columns. This gave a ~2-3 GB spike and swapping (~15 MB free RAM, 21.4/22.5 GB swap used).
  - Fix in `scripts/known_objects/store.py`: a 1° (dec, ra) grid pre-filter, so the KD-tree covers only rows near the candidates, plus vectorised assembly.
  - Speed: 2,003 candidates went from 5+ min (never completed) to 6.7 s, with ~0 added peak RSS; loading takes ~21 s.
  - Correctness: 14/14 unit tests and a superset test against brute-force search (random all-sky, pole |dec|>89, ra 0/360 wrap, larger radii), with 0 matches dropped.
- **Build hardening:**
  - astroquery `Vizier.get_catalogs("B/vsx")` returns an empty list (0 tables) without an error, even on the cfa mirror.
  - The raw-ASU-votable recno-window fetcher is now in the repository (`scripts/known_objects/fetch_vsx_bulk.py`). `build.py` routes the VSX spec (`reference_catalogs.py`: key `vsx_full`, source `vsx_bulk`) through it and raises an error on a zero-row fetch. Other VizieR pulls fall through mirrors (cfa→unistra).
  - Test: `build.py --classes variable --vsx-max-recno 60000` gave 149,997 rows in a test store.
  - The ASU endpoint rejects a server-side `Type=` filter, so VSX is pulled whole; `--vsx-cv-only` filters client-side.
- Provenance: scripts/known_objects/{store,build,reference_catalogs,ingest_vsx}.py, fetch_vsx_bulk.py, README.

### 2026-07-05 — DESI hunt Phase 2B (ZTF period + RV mass function, top 31): 0 dark companions
- 30/31 processed. One job failed on a transport error, and the batch had 30 distinct source_ids.
- Verdicts: 0 DARK_COMPANION_CANDIDATE, 4 STELLAR_SB1, 3 ARTIFACT, 23 NO_PERIOD_PENDING.
- **STELLAR_SB1** (credible ZTF period, clean RV fold): M2_min 0.47-0.62 Msun, i.e. M/K dwarfs below any WD/NS/BH threshold. These are new eclipsing/ellipsoidal SB1s. Registered: 1487470319907416832 (P=1.32 d), 3831414946076844032 (P=1.53 d), 1126496666779064064 (P=3.45 d).
- **ARTIFACT:**
  - 1 SX Phe/δ Scuti pulsator (2688492537652631424), whose RV signal is pulsation. Registered.
  - 2 with RVs incoherent with the period (one bad epoch; smooth drift vs a short period).
- **NO_PERIOD_PENDING (23, 77%):** significant single-lined RV variability (chi2/dof 100-800), uncatalogued, with a clean ZTF null (LS, BLS, bootstrap FAP, alias checks).
  - Not rejected: ZTF cannot recover ellipsoidal/eclipse periods at G~17-18.5, and 5-9 sparse DESI epochs cannot give a period.
  - Their nature depends on more RVs or on Gaia DR4 (Dec 2026) orbits.
- **Lane status:** 0 dark companions in the top-30 FoM. Output: a catalogue of ~18,946 novel significant RV-variable SB1s, the top 30 period-searched. The periodless majority is DR4-gated.
- Decision: the 23 pending objects and the high-significance tail go to the DR4 target list. Lower-FoM candidates are not pursued (same period limit).
- Data-quality flags (to correct upstream): 2516386605326462848 is a DR2 id (DR3 = 2516386605326602496); 3633111495656814592 is a DR2 id (DR3 = 3633111499952596480).
- Provenance: docs/reports/desi_hunt_phase2b_2026_07_05/ (phase2b_verdicts.csv, synthesis.json).

### 2026-07-05 — DESI dark-companion shortlist for DR4: 1/15 DR4-decisive
- **Selection:** 18,946 → 288 → top 15.
  - Cuts for the 288: dRV 40-150 km/s, nsig>=8, chi2r 5-200, baseline>=30 d, G<=18.3, clean, not resolved in Phase 2B.
  - The top 15 are ranked by a DR4-feasibility FoM (brightness, parallax S/N, RUWE, amplitude, significance).
  - File: docs/reports/desi_dr4_darkcompanion_shortlist_2026_07_05.csv.
- **Limitation:** the faintness (G=16-18.5) that puts the sample outside Gaia RVS also puts it beyond DR4.
  - DR4 RVS stops at ~G16.2.
  - DR4 astrometry at G~16-17 and 2.3-5.4 kpc gives wobbles too small for an orbit.
- 1 of the top 15 is DR4-astrometry-decisive: 1506270319907416832... = 1506270323771488768 (950 pc, parallax S/N 22). It is marginal (dRV 40 km/s, RUWE 1.07, no DR3 binary excess). The other 14 (2-5.4 kpc) need spectroscopy, which is outside the no-telescope scope.
- Decision: the catalogue is kept as a spectroscopic target list (docs/reports/desi_hunt_phase2a plus this shortlist). The DR4-decisive object is noted for the Dec-2 pass. No further work.

### 2026-07-05 — Gate: extreme-velocity / HVS in DESI×Gaia = NO_GO
- **Selection:**
  - 1.17M DESI multi-epoch stars → |RV| >300 km/s: 11,963; >400: 1,549; >500: 142.
  - → 394 robust (chi2r<5, epochs agree, ≥3 epochs) → 379 uncatalogued (1 known: V0757 Vir, HADS).
  - The tail reaches ~565 km/s, below the 600 km/s artifact flag.
- **Prior art:**
  - Verberne+2025 (arXiv:2506.19570): GC-ejecta null.
  - Cavieres & Koposov+2026 (arXiv:2601.19866, A&A): DESI-312, 698 km/s, G≈17.1, in the same faint regime. Koposov is the DESI MWS lead.
  - Deng+2026 (arXiv:2604.21646): DESI-HVS1.
- **Confirmation limit:**
  - 0/15 of the top-|RV| stars have a Gaia RV.
  - The one star with a usable parallax has 3D v=420 km/s and is bound.
  - Faint DESI parallaxes cannot confirm unbound orbits.
- Verdict: NO_GO. Not pursued: a check of Cavieres/Deng for a completeness gap in the dark/backup program.
- Status: extreme velocities closed (prior art); DESI dark companions null (DR4-gated). No archival pivot lane remains open.
- Provenance: docs/reports/gate_hvs_2026_07_05/.

### 2026-07-05 — Gate: DESI RV-variable catalogue × X-ray/UV/IR = MARGINAL
- Cross-matched the 18,946 catalogue (XMatch, <2.5″):
  - GALEX UV: 6,681 (35%), with ~6 at >3σ UV excess (106 at >2σ). The only usable channel.
  - eRASS1: 6 total, limited by sky coverage (western sky).
  - AllWISE: 18,200 (96%). The W2-W3 dust channel is unusable, since 92% of W3 values are upper limits at G16-18.5. W1-W2 is noisy (11-261).
- **Caveat:** GALEX separations are wide (median 0.92″, 90th percentile 2.2″, vs WISE 0.14″/0.47″), so blends are a risk. An offset control is needed first; it was not run in the gate.
- **Prior art:**
  - The GALEX UV-excess PCEB method is published: Makarov 2017; Shahaf+2023 Triage II; Garbutt/Parsons+2024.
  - It was applied here on 2026-06-05 to the Gaia-NSS pool (NO-GO standalone).
  - The 18,946 sample itself was new. The Smith 2026 RNAAS object has 0 overlap.
- **Verdict: MARGINAL, no full lane.** Reasons: only 1/3 channels is usable, the method is not new, and ~6 candidates remain, each needing a 2-component SED fit.
  - Bounded side task: an offset control, then SED fits of the ~6-15 flagged objects with `companion_excess_sigma`.
  - Highest excess: 5097036946581138688 (G=17.11, BP-RP=1.03, NUV=16.05, 9.4σ, clean flags, no SIMBAD entry).
- Provenance: docs/reports/gate_mwl_2026_07_05/ (report, top 10).

### 2026-07-05 — PCEB check (SED fit + offset control, 10 GALEX UV-excess candidates): null
- **Setup:** 2-component SED fits (single MS vs MS+hot WD, Δχ²) on the 10 GALEX UV-excess candidates from the 18,946-row catalogue. A shifted-position offset control (chance alignment) came first.
- **Offset control:** all 10 pass p_chance<0.004 ("RELIABLE"). The `tighter_than_min_chance_sep` criterion splits them into 6 tight (≤1.69″) and 4 wide (2.08-2.47″, blend suspect). 5097036946581138688 (2.41″) is wide.
- **SED:**
  - The 6 tight matches show no WD requirement: Δχ² = 0.2, 0.2, 0.2, 0.3, 5.1, 67.7.
  - 4356687522233455616 (1.18″, Δχ²=67.7) rests on one NUV point, with the WD at the grid edge (40000 K). Without FUV, a hot WD cannot be told from chromospheric activity.
  - SED signal appears only in the wide matches.
- **5097036946581138688 rejected:**
  - Its UV match is blend-suspect (2.41″).
  - It is NUV-bright and FUV-faint, the activity signature; a hot WD brightens both bands. Its Δχ²=21241 comes from the NUV point, and MS+WD overshoots the faint FUV.
  - It has the worst spectral fit of the 10 (worst_chisq_tot=30362 vs ~7-9k; chisq_relative_max=2.96), so its RV variability (drv_max 3.6 km/s) is suspect.
- **Result: 0 confirmable novel PCEBs.**
  - All 10 are uncatalogued in the VSX-complete store; novelty is moot.
  - 4356687522233455616 is parked as an FUV/spectrum-gated watch item.
  - No register entry (screen null).
  - DESI × multi-wavelength avenue closed.

### 2026-07-05 — Pre-DR4 gate A: false-positive self-validation harness for the DR4 re-fit engine (19/19 pass)
- **Purpose:** one of two pre-DR4 tasks (decision (user): do both). The DR4 re-fit engine must reproduce the skeptical verdict on every documented false positive before its new verdicts are used.
- **Corpus:** from the dated ledgers (RESEARCH_LOG, CANDIDATES.md, object journals, CITATION.cff). 23 documented false positives: 11 astrometric (this engine), 7 spectroscopic SB2, 3 photometric, 2 crossmatch.
- **Corrections found:**
  - HD 76078 is not a campaign retraction but a v1 benchmark fixture; it is excluded.
  - 5858574 was demoted for the rv/2→sin i inflation, not the cos i sqrt bug (its NSS solution is Orbital).
- **Additional false positives:** 5406907, 6802634, TYC 7350-249-1, two superposed-SB1 NS, three triple-favoured NS, HD 207141, WDJ205650, RAVE-noise 5476986, Pile-A HGCA.
- **Built:**
  - `scripts/dr4_pipeline/refit/fp_registry.py`: source_id-keyed corpus with `fp_class`/`owning_subsystem` and `validate_registry()`.
  - `test_fp_selfvalidation.py`: integrity and completeness checks, plus one synthetic-DR4 assertion per astrometric false positive.
  - `run.py --self-validate`: a gate that runs before day-one analysis and aborts on failure.
- **Reproduced verdicts** (matching documented values):
  - cos i bug: M2 1.20→1.42, crossing Chandrasekhar. The corrected fit recovers i to 0.05°.
  - rv/2 sin i=0.53: direct M2=1.55 becomes the retracted 2.82 mass-gap BH.
  - Triples 5858574/HD 75567/2127900 → `multi`.
  - Weak-fit WDJ020915 (F2=+18.8) → PARK, not CONFIRM.
  - Low-a_phot WDJ020915 → DOWNGRADE (M2=1.15<1.2).
  - WDJ060042 at anchor M2=1.36 → CONFIRM, no super-Chandrasekhar claim.
  - Near face-on → REFUTE-stellar (TYC 4562/UCAC4 class).
  - WDJ205650: default M1=1.5 gives the retracted M_tot=2.07; real M1=0.38 gives 0.64 (sub-Ch).
- **Result:** refit suite 19/19 pass (8 existing + 11 new). Tooling only; no new objects. Provenance: 4 files under scripts/dr4_pipeline/refit/ and the corpus.

### 2026-07-05 — Pre-DR4 gate B: DESI DR1 dark-companion occurrence selection function = MARGINAL
- **Question:** could a period-marginalised DESI occurrence upper limit improve on the Gaia-RVS/TESS constraint?
- **Method:**
  - Injection-recovery on the real epoch sampling of 30,000 stars from the 458,898-star G16-18.5 pool, using their real MJDs and heteroscedastic vrad_err.
  - Phase-1 two-part detection statistic, then a Poisson-0 95% upper limit.
  - A re-check confirmed the physics, arithmetic and comparison (K1 sanity 79.4 km/s).
- **Result: MARGINAL.** Median per-epoch σ is 1.44 km/s. 2-epoch pairs (60% of the pool) recover 60-96% of high-amplitude signals at P≤100 d. η_UL ~ 7×10⁻⁶ at short P; ~0.9-1.1×10⁻⁵ per star period-marginalised.
- **No improvement:**
  - At P≤3 d, DESI only matches Green/El-Badry+2024 (arXiv:2412.02082, <10⁻⁵ at 2σ). This assumes f_primary=1 (0.9 M⊙ single primaries) and 0 detections.
  - The 0-detection premise rests on the Phase-2B top-of-list null over 26,427 unvetted survivors; any k>0 loosens every limit.
  - At P~30-1000 d (η_UL ~1.1-1.5×10⁻⁵), TESS ellipsoidal (a≤20 R⊙, P≤3 d) has no sensitivity. This limit also depends on the 0-detection premise.
  - The re-check found the recovery statistic slightly looser than Phase 1 for ≥3-epoch stars, which biases the limit optimistic.
- Decision: the short-period claim is parked for DR4. The long-period limit is to be re-evaluated with DR4's longer baseline. No new object.

### 2026-07-07 — Pivot scan beyond compact objects (community-confirm mode evaluated): 5 options
- Decision (user): look for pivots toward discoveries beyond the compact-object frame closed on 2026-07-05. Axes:
  - target classes limited by vetting labour, not capability;
  - community-confirm mode (MPC/TNS/VSX/AAVSO or professional confirmation; no owned telescope);
  - GO-IF menu items 4-8.
  - 20 ideas → 9 shortlisted → 5 survivors.
- **Archival precovery / arc extension** of short-arc MPC and Rubin solar-system objects (Sam Deen's approach):
  - Find short-arc objects (unlinked singletons, TNOs, slow movers) in ZTF/NSC/DECaLS/PS1/SDSS archival images. MPC attributes accepted astrometry by name.
  - Precedents: Deen's 3I/ATLAS precovery (MPEC K25N12); Jan-Feb 2026 attributions (516P/2026 B1 SDSS precovery; 2024 PN7 ZTF).
  - Related work: an LLNL/GT cross-archive prototype (arXiv:2510.07588); Rubin automation.
  - Gate (1 day): a positive-control recovery via the B612/ADAM API against ZTF+NSC, and a check of Rubin SSP linking to external archives.
- **DASCH prior-eclipse recovery** on the 2025-26 dipper/long-eclipse inventory:
  - Precedent: Nair & Denisenko recovered ASASSN-24fw's 1937 and 1981 eclipses, derived P=15,999±2 d, and predicted the confirmed May-2025 egress (Zheng et al. 2026 AJ).
  - The ASAS-SN team checked DASCH for 1 of ~31 candidates.
  - Limitation: plate depth. Gate (0.5-1 d): a pilot on the 6-8 brightest.
- **Other survivors:**
  - WZ Sge / one-outburst CVs in the 2018-24 ZTF/ATLAS backlog; live detection is now covered by Rubin.
  - A big-dipper gap search in the 11<g<13 and 14<g<16 ASAS-SN bins (no established attribution mechanism).
  - A TESS-FFI deep-dip screen below the ground-survey limit, using cached CVZ sectors.
- **Rejected:**
  - Comoving UCDs: prior art arXiv:2604.01323 (Apr 2026, 3,006 candidates, WISE+Gaia+NSC).
  - TESS-EB quad/triple vetting: ~80% overlap with the multiples hunt (0 novel over 4,571 TICs). The cache is the screened Prša catalogue; VSG is invitation-only.
  - Red-nova progenitors: active professional work in 2024-26 (e.g. TYC 3801-1529-1, q=0.024, ApJ Jan 2026).
  - Kilonova Seekers: co-authorship is curated.
- **Decision required (user):** all 5 survivors need community-confirm mode, and none survives under the strict mode. Adopting one relaxes the confirmation half of the no-telescope filter.

### 2026-07-07 — Community-confirm mode adopted; gates R1 and R2 started
- **Decision (user):** community-confirm mode: archival finds, confirmed by MPC/VSX/AAVSO or professional follow-up with the finder named; no telescope used. No-telescope guardrail amended; archive-only remains the default where available. Gates R1 and R2 started.
- **Gate R1 (precovery):** no-account precovery route (SSOIS/Horizons/IRSA/NSC; B612 stack assessed); positive control on a published precovery with a scrambled-ephemeris negative control; short-arc target supply via MPC; Rubin SSP self-linking status and MPC ADES measurer attribution.
- **Gate R2 (DASCH dippers):** 2025–26 dipper/long-eclipse inventory (arXiv:2507.19594 + ZTF + named events), filtered to plate-analyzable targets (≤13.5–14 mag, ≥0.5 mag depth); ADS check for prior plate work; daschlab DR7 pilot on the 6–8 brightest targets for multi-point, blend-guarded pre-1990 sub-baseline epochs.
- Independent checks: falsifiable positive control, Rubin documentation re-read, pilot light curves re-examined under isolated-plate/blend/plate-limit guards.

### 2026-07-07 — Gate results: R1 precovery GO; R2 DASCH dippers NO-GO, lane closed
- **R1 = GO (independently verified).**
  - Positive control, Centaur 10199 Chariklo: an ephemeris derived blind (Horizons, ZTF obs code I41) matched the MPC OBS80 ZTF positions to 0.07″ and 0.25″ (predicted V~18.8 vs reported 18.75r); a re-derivation gave 0.075″/0.245″. Negative control: +1° scrambled ephemeris 0 matches, true ephemeris 2.
  - Tooling, no accounts: Horizons (astroquery) → CADC SSOIS backend (`ssosclf.pl` TSV; DECam/CFHT/HSC/PS1/ZTF/HST/VISTA; 11,676 archival image rows for the control) → NSC/PS1 confirmation. IRSA MOST validated for ZTF. B612/ADAM not used (account/indexing dependency).
  - Supply: MPC distant_extended has 2,524 single-opposition distant objects, 1,966 with arc ≤60 d. The slow movers are too faint for ZTF (0% at V<21); ~395 at V<23 fall in DECam/CFHT/HSC/PS1. Shortlist (5–35 d arcs preferred): 2000 FY53, 2001 QU297, 1999 JB132, 1995 KJ1, 1997 CW29, 2000 YQ142, 2002 PE155, 2000 QB226, 2000 QO252, 2001 KM76.
  - Prior art and mechanics: arXiv:2510.07588 is a prototype (no public code, NEA-focused). Rubin DP0.3/DP1 SSP self-links only; external-archive precovery planned. MPC archival submission is manual (ADES to obs@cfa; survey imagery via SARC under the survey obs code, measurer named). Verified: MPEC 2025-N12 names amateur S. Deen (W68/M22) for the 3I/ATLAS precovery.
  - Caveat: the control has a long arc; short-arc uncertainty at archival epochs is untested. Decision: pilot 2–3 short-arc SSOIS recoveries before scaling.
- **R2 = NO-GO (verified on all three axes); cause is supply, not tooling or prior art.**
  - Positive control TYC 2505-672-1 (V~11.7): 1,403 good DASCH detections, σ=0.154; a multi-point 1945 eclipse epoch is recovered.
  - Inventory: ASAS-SN big-dipper box already covered by the 2026-07-05 mini-campaign; ZTF-81 wrong class (aperiodic, 1/81 periodic); ASASSN-24fw already plate-worked (Nair & Denisenko; Zheng+2026); ZTF-CBO class recurring (P=30–530 d) but r=15.5–18.6 vs the ~14–15 plate limit. The brightest, ZTF-CBO-1 (r=15.52, 1.2 mag dip): 11–20 usable plates over a century, σ=0.472, 0 dip epochs, blend-clean.
  - Analyzable + fresh + recurring: 0–1 vs a GO floor of ≥10–15. Fresh deep-dipper discoveries have r~16–19, fainter than the plate limit.
  - **Lane closed.** Reopening trigger: a new V≲13.5 long-eclipse event of the ASASSN-24fw class.
- **Next step:** short-arc pilot on 2000 FY53 (35 d, V~22.0), 2001 QU297 (23 d, V~22.6), 1999 JB132 (8 d, V~22.6): archival-epoch ephemeris and uncertainty → SSOIS deep-archive search → motion-consistent chains with offset negative controls. Measurement only; submission is the user's action.

### 2026-07-07 — R1 short-arc pilot: 3/3 unusable (orbit uncertainty); SMIA pre-gate adopted; campaign re-cut
- **Result:** all 3 UNUSABLE_UNCERTAINTY, numbers reproduced independently. The limit is orbit determination, not depth or coverage.
  - 2000 FY53 (35 d, ~44 AU, Horizons OCC=9): within-arc 3σ ~3–7″; 1,620′ (27°) at +1 yr; ~whole-sky (~34,000 deg²) by 2014. 815 SSOIS footprints, 5 in-arc.
  - 2001 QU297 (23 d): along-track spans 128° at the first archival epoch (2003). The +1°-offset control field held more mag-consistent sources than the target field (679/2933 vs 638/4399): no discriminating power.
  - 1999 JB132 (8 d): along-track wraps the orbit 4–43× by 2003–14; minor axis 4.3–28.5°; SSOIS returned "No positional uncertainty".
  - 0 chains, 0 false positives; unconstrained regions not searched.
- **Finding:** searchability is set by arc length × heliocentric distance × time to archive epoch, not depth. A short arc leaves the semi-major axis free, so along-track uncertainty grows ~quadratically. At ~40–45 AU cross-track 3σ exceeds 10′ within ~1–4 yr; DECam/PS1/HSC start ≥3 yr after these late-1990s/2000s arcs. Bare ≤10 d distant arcs are not precoverable; 20–40 d arcs also fail at ~40 AU. Recoverable: multi-opposition or ≳60 d-arc distant objects, and well-constrained inner-system objects (Centaurs/NEOs/short-period, as the Chariklo control).
- **Method criterion (SMIA pre-gate):** one astroquery Horizons call (quantities 36/37) at the archive epoch; drop unless cross-track SMIA < ~10′ and SMAA is not sky-spanning. Automatic drops: SSOIS "No positional uncertainty"; Horizons-vs-MPCORB nominal divergence >10′.
- **Recipe v2:** tooling unchanged. Short single-opposition distant arcs dropped (all 10 gate-R1 shortlist objects unless each passes SMIA); multi-opposition / ≥60 d-arc distant and inner-system lanes added; SMIA pre-gate before any SSOIS query. Campaign smaller than the initial ~395. MPC mechanics unchanged. Nothing to submit (0 chains).
- **Next step:** re-cut with the SMIA gate, rank by searchability × arc improvement, attempt recoveries on the top gate-passers (motion-consistent chains, negative controls, no submission).

### 2026-07-07 — Precovery campaign: candidate chains for 2009 HW77 and 2001 KN76; 2001 QT322 null voided by an epoch-ordering bug
- **Re-cut:** MPC distant_extended (7,353) → inner 1,140 / distant 6,213 → faintness proxy vidx=H+10·log10(a)<23.3 → 144 SMIA-gated, 103 passed. Fresh Horizons calls reproduced 7/7 sampled gate decisions. Selected: 2001 QT322, 2009 HW77, 2001 KN76. Multi-opposition distant objects (2001 QT322/KK76/KN76/KJ76/KP76, 2009 HW77) have sub-arcsec cross-track uncertainty across two decades of deep imagery; last observed 2004–2012. SSOIS footprint counts are an upper bound on searchable frames, not on-chip detections.
- **2009 HW77: candidate chain, stands.** Six DECam/NSC-DR2 detections at 4 post-arc epochs (2013-03-02 ×2 same-night r; 2014-06-27; 2014-06-29; 2015-04-27 ×2 same-night VR) fit the JPL orbit at 0.03–0.41″; mags 21.5–21.8 vs predicted V≈21.6. Extends a 7-opposition 2002–2012 arc by +2.9 yr. Verified: 6 ephemerides re-derived (agree to 6 decimals), residuals reproduced, negative control re-run from raw NSC CSVs (+1° offset boxes: 0 same-night hits within 1.2″ vs 1–2 mag-matched hits in every science box), stationary rejection and motion guard re-checked. Astrometry: docs/reports/precovery_campaign_2026_07_07/attempts/2009_HW77/FINAL_astrometry.csv.
- **2001 KN76: candidate chain, marginal.** Four DECam detections at two epochs 2.3 yr apart (2013-03-11 ×2; 2015-07-15 ×2), inside the gated ellipse. Reproduced: ephemeris, residuals, authenticity, stationary rejection, negative control, chance density (0.016/0.053); the 2015-05 non-detection is at the field edge. Caveats: 2015-07-15 frame sub-seeing marginal (fwhm 0.77″, cstar 0.41–0.52); only 2013 photometrically robust; both epochs within ~0.25σ on the poorly constrained along-track axis; r~23.2 vs predicted V 22.55. Pixel confirmation and a joint refit required before any submission decision. Astrometry: .../attempts/2001_KN76/astrometry_for_review.csv.
- **2001 QT322: null voided → UNUSABLE_UNCERTAINTY.** Bug: Horizons returns rows time-sorted; the script indexed them by position against an SMAA-ranked night list, assigning predictions to wrong nights. 11/12 deep boxes were off by 70″–2.1° (box sizes 43–84″). Reproduced independently; the MJD 57193 stationarity rejection used the wrong night's prediction. PS1 channel correct but depth-limited (~21.5–22 vs V~22), cannot support a null. Re-run required.
- **Method criterion:** multi-epoch Horizons rows are keyed by datetime_jd, with a per-night JD assertion as a hard check.
- **State: CHAIN_FOUND.** Next wave: 2001 KK76 (last observed 2004), 2001 KJ76, 2001 KP76 (4,808 footprints), 2006 JG57 (V20.1 Centaur), 2004 YH32 (2005 near-perihelion window only), then the 2025-vintage long-arc tier. Submission (ADES via survey SARC, measurer named) is the user's action, after pixel verification and, for KN76, a refit. Artifacts: docs/reports/precovery_campaign_2026_07_07/ (gate report, pilot, campaign_targets.csv, smia_gate_log.csv, attempts).

### 2026-07-07 — Verification: 2009 HW77 pixel-confirmed (submission-ready); 2001 KN76 parked; 2001 QT322 catalog-level null
- **2009 HW77: confirmed; submission-ready.** All 6 detections inspected in FITS cutouts (NOIRLab /svc/cutout, exact InstCal exposures): PSF-like sources at every predicted position (forced-aperture SNR 8.5–19.4; FWHM matches frame seeing; not cosmic rays, 2 same-night detections per bracketing epoch). Moving-object test passed at all 4 epochs: 2014-06-27 same-night disappearance (SNR 15.4 → 0.1 in the +4.3 h frame); 2014-06-29 and 2015-04-27 positions empty on 3 non-detection nights each; crowded 2013 epoch: static red star 1.0″ SW contributes k=0.44, +10 SNR excess only on detection nights (~0 on 4 off-nights). A re-check of 6 detection + 5 control cutouts with separate WCS/photometry reproduced all of this from raw pixels.
  - Final astrometry: docs/reports/precovery_campaign_2026_07_07/verify/2009_HW77/updated_astrometry.csv (NSC deblended PSF positions, per-axis σ 0.25″/0.15″/0.12″/0.18″, obscode W84).
  - Correction: the older FINAL_astrometry.csv swaps the two 2013 tu-exposure↔MJD labels (frames 2 min apart, values unaffected); updated_astrometry.csv is reconciled.
  - Method: /svc/cutout must use the `_ooi_` product; `_ood_`/`_oow_` return near-zero arrays and corrupt SNR.
- **2001 KN76: weakened; parked, not submitted.**
  - Pixels: all 4 detections real and blend-free (2013 pair SNR~9–10). The 0.77″ flag on the 2015 frame is a SExtractor artefact, not a cosmic ray, but detections there are 2.6–4.6σ per frame.
  - Legacy Survey DR10 deep coadds: 2013 position blank in r/i/z; 2015 position shows flux only in the r/g planes containing the 2015-07-15 data, blank in i (2017) and z (2019): the flux is KN76's own.
  - find_orb joint refit (built from source; 44 MPC obs + 4 new, all retained) inconclusive: self-consistent (a=43.837 AU, RMS 0.91″), along-track shrinks ~4× (partly tautological), but a shifts 0.094 AU ≈ 11σ of the formal error, U 4.1→4.0, and the new points have the largest residuals, with a coherent −0.7″ Dec residual (~3σ at 0.3″ per-point σ). Two-body fit only.
  - Verdict: neither confirmed nor rejected; needs a third independent epoch and a DE-ephemeris refit with realistic σ.
- **2001 QT322: re-run, catalog-level null.** datetime_jd-keyed rebuild (per-night assertions; 2 nights re-derived to 0.000″). 21 in-3σ NSC sources across 5 nights, all catalogued stationary objects (e.g. 22 detections over 1,204 d, mas/yr-level pm); the one motion-consistent pair is two exposures of one fixed star; +1° control field 18 vs 21 sources, with its own spurious pair. Scope: NSC/PS1 catalogs; forced photometry on the 3 tightest nights not done. Closed as a null.
- **HW77 filing steps (user):** ADES PSV from updated_astrometry.csv (obscode W84, measurer named); coordinate with the DECam SARC representative; submit to the MPC; verify via WAMO.
### 2026-07-08 — KK76/(88268) refit with HST points; wave 4: 2007 HV90 null
- **Refit:** ground arc only (41 obs, 2001–2004, U=4.6) vs joint fit adding 4 HST obscode-250 points as MPC satellite S/s records with HST geocentric vectors (parallax verified applied). All 4 retained: residuals 0.04–0.08″, mean pull 0.55σ, max 0.66σ.
  - Sky-plane 1σ (geocentric): 2026-07 11.2″→0.855″ (13.1×); 2030-01 13.7″→0.834″ (16.4×); 2040-01 24.0″→0.312″ (76.9×). Arc-only prediction offset 36–82″ = 3.2–3.4σ (same pattern as Orius, larger).
  - Caveat: osculating a shifts +0.19 AU ≈ 35× the arc-only formal σ_a; read as optimistic short-arc covariance (find_orb without JPL DE; JPL's arc-only a differs by ~0.2 AU), not an HST-point discrepancy (pulls <0.7σ). U 4.6→4.2; oppositions 4→5.
  - ADES draft (satellite rows, no photometry, astCat Gaia3 via HSC30, to confirm with SARC): docs/reports/precovery_campaign_2026_07_07/kk76_refit/ades_draft_88268_2001kk76.psv. Pending independent verification.
- **Wave 4 (1 of 3 done):** 2007 HV90 = NULL_SEARCHED, verified. Rules 7+8 applied (fresh get-obs arc-end 2016-06-13; 2017-05-17 window not self-arc); boxes sub-0.16″, centred. Single Y-band night with the target at or below NSC Y depth, so the null cannot be corroborated. Bycatch: 0 tracklets (2,788 pairs rejected by the static catalog), 0 unknowns. 2002 KW14 and 2010 JK124 in progress.
- Artifacts: docs/reports/precovery_campaign_2026_07_07/{kk76_refit/, wave4/}.

### 2026-07-08 — KK76/(88268) refit verified: second submission-ready package
- **Independent re-run of both fits reproduced all values:** arc-only a=42.515/e=0.015 (41 obs), joint a=42.707/e=0.019 (45 obs), to the digit; HST residuals exact (−0.044/+0.059 … +0.079/−0.032); pulls 0.43–0.66σ confirm the 0.16″/0.10″ weighting.
- **Satellite parallax verified by ablation:** without the S/s offset lines find_orb excludes all 4 obscode-250 points ('X'); the satellite-pair file retains them. HST geocentric |r|=6,946–6,948 km (~570 km altitude). Ephemeris table consistent (13.1×/16.4×/76.9×; 3.22/3.28/3.42σ).
- **Correction:** "joint 2006 O−C should match the wave-3 ~0.29″ mean" is not derivable from wave-3 artifacts (scan_result.txt holds pixel search-grid offsets, not an O−C). Measured arc-only→joint 2006 offset ~0.95″ ≈ 4× the arc-only 2006 σ (0.232″), consistent with the optimistic arc-only covariance.
- **ADES draft checked field by field:** UTC times match the truth CSV; positions to the digit; stn=250 + ICRF_KM/ctr=399 vectors match the OBS80 s-records; no photometry; measurer/submitter/SARC blocks present. Open for SARC: astCat=Gaia3 (via HSC v3.0). In deweight tests find_orb retains prior state; the S/s-strip test is the parallax check.
- **Status:** (88268) submission-ready alongside Orius (user files). Journal: docs/object_journals/mp_88268_2001kk76.md. Artifacts: kk76_refit/ (78 files, both fit and verification directories).

### 2026-07-08 — Wave 4 complete: 3/3 nulls; 2010 JK124 chain refuted; rules 10 and 11 adopted
- **2007 HV90 and 2002 KW14 = NULL_SEARCHED.** Both windows reduce to one 2017-05-17 DECam night. HV90: 8 Y exposures, target at NSC Y depth ~21.4, not proof of absence. KW14: one ~8-min 4-dither sequence, 3/4 exposures off-array or in chip gaps; the usable one is 1–2.5 mag deeper than the target, nothing in the 0.44″ ellipse. Rules 7+8 re-verified (fresh get-obs; windows post-arc). Negative controls clean; 0 bycatch unknowns. One night cannot chain a slow TNO.
- **2010 JK124: claimed chain refuted → NULL_SEARCHED.** Claimed: 3-epoch NSC chain (2014/2015/2016, residuals 0.26–0.97″, joint chance coincidence ~6e-9). The 2016-03-08 detection (SNR~17) is absent from the identical-depth exposure 3 min later (a TNO moves <0.1″ in 3 min), and the 2014-06-06 detection is absent from the equal-depth frame 4 h earlier: both spurious ndet=1. Only the 2015-06-20 ndet=2 epoch is real; one epoch is not a chain. The chance value assumed all three points were real. Pixel stage not run.
- **Method criteria:** Rule 10: a chain member must reappear in a same-night exposure of equal depth; ndet=1 detections are never chain members. Rule 11: the pre-gate requires ≥2 distinct post-arc imaging nights with real baseline.
- **Campaign totals:** 12 targets → 2 submission-ready packages (Orius 6-point DECam, KK76 4-point HST), 1 parked mover (KN76), 9 nulls, 0 false chains after verification (2 caught: QT322 epoch ordering, JK124 ndet=1). Both packages await user filing (SARC → obs@cfa). Optional: re-cut the remaining ~90 gate passers with rules 7+8+10+11. Artifacts: wave4/ (3 target directories; JK124 candidate_astrometry.csv kept, marked refuted).

### 2026-07-08 — Frontier scan: pointed-HST astrometry mining GO; occultation need as a prioritisation criterion; no asteroid/comet lane
- Scope: extending the KK76 pointed-archive approach, asteroid/comet variants, relevance. Four web-based scans, each checked independently; all verdicts stood, with corrections.
- **Lane 1, pointed-HST astrometry: GO.**
  - Prior art: Benecchi & Noll 2010 (arXiv:1006.5949) reported 256 TNOs, 1428 measurements from programs 10514/10800/11113/11178 to the MPC; not repeated.
  - Remaining: (a) SSOLS GO-15648 (Cycle 26, WFC3/UVIS, 198 cold-classical KBOs, V≈21–25.2); its 2024 reprocessing (arXiv:2406.02808) measured relative binary astrometry only; absolute positions not submitted. Priority: 43 DES-discovered targets with 1998–2005 arcs (151 OSSOS-sourced near-redundant). (b) The V>24 tail excluded by the Noll programs' "brighter than 24" cut; KK76 (V~24.3) is in it.
  - Method criterion: prior submission is checked per object (get-obs, obscode 250) before any attempt.
  - A single HST epoch is not 10-mas occultation grade; it shrinks the recovery box.
- **Lane 3, occultation-ephemeris rescue: GO/MARGINAL boundary; used as a prioritisation criterion, not a lane.**
  - Consumer: Lucky Star NIMA (413 TNOs/Centaurs, event-driven refits; a single detection improves the ephemeris).
  - Prior art: DES southern version (Banda-Huarca+2019: 202 TNOs/Centaurs from 4.29M DECam frames). Open: non-DES archives (CFHT/HSC/PS1/HST), targets outside Rubin coverage.
  - Orius is an occultation rescue; KK76 is a baseline extension of a nearly lost object.
  - Correction: Rubin LSST full operations began 2026-06-30 (>11k new asteroids incl. ~380 TNOs so far); Rubin overlap for southern/ecliptic occultation targets by DRY1 (~mid-2028). "North of +33.5° unaffected" is overstated: the Northern Ecliptic Spur reaches ecliptic latitude +10°. Remaining classes: HST/space epochs, long pre-2024 baselines, high-ecliptic-latitude or dec>+33.5° objects.
- **Lane 2, asteroid/comet variants: MARGINAL; no campaign.**
  - NEO risk-list precovery is automated daily (B612 ADAM::Precovery, ESA Aegis, JPL Sentry); image-only archives remain (precedent Deen & Lam 2024 YR4).
  - Comet/ISO precovery is done within hours to days (3I/ATLAS arc extended ~17 d within days; Deen on MPEC 2025-N12).
  - Archival activity discovery is the Active Asteroids method; HSC/PS1 ingested via UNIONS; "Rubin Comet Catchers" successor active. Main-belt astrometry: no product.
  - Triggers instead: (i) deep-archive precovery of the next ISO/distant-comet announcement; (ii) single-object activity detections to the Chandler team.
- **Lane 4, the two packages:** no prior submission of these points. Orius has a current consumer (Lucky Star/RECON; 14″ ephemeris uncertainty). KK76 is not on occultation lists; its use is recovery by 2040 and a space-epoch baseline. Correction: "first space-based astrometry" is object-specific only (journal row amended). The 13–77× factors partly reflect the short-arc prior. "Submission-ready" means ready to present to SARC (one-time archival-submitter verification).
- **Decision:** file Orius and KK76 first. If scaling: one ranked list (SSOLS + faint-tail targets × per-object get-obs × NIMA/RECON needs × Horizons SMAA × non-DES/HST coverage × outside Rubin), piloting the top ~5–10 DES-discovered SSOLS objects through the KK76 verification procedure. No asteroid/comet campaign. Breadth search paused until Gaia DR4 (2 Dec 2026).

### 2026-07-08 — Comet benchmark (C/2014 UN271): 3/3 pre-registered criteria passed; photocentre offset measured
- Target C/2014 UN271 (Bernardinelli–Bernstein): its MPC record holds the DES team's W84 astrometry from the same DECam exposures (same-frame comparison) plus a JPL orbit. Self-arc rule inverted for the benchmark; nothing submitted (duplicates).
- **(i) Same-frame: pass.** Blind NSC re-measurement at 10 epochs (10 nights, 2014–2018, 0.02–0.39″ from the Horizons prediction) agrees with the published astrometry to 0.029″ (RA) / 0.043″ (Dec) RMS, the catalog noise floor; 2 epochs pixel-confirmed.
- **(ii) O−C ≤0.3″: pass.** The −0.107″ Dec systematic is also in the published data (intrinsic).
- **(iii) Orbit swap: pass.** Our points in place of the professional ones change every element <0.1σ and the 2030 prediction by 0.0003″ (information content equal to <1%). The find_orb no-DE offset (~3.6″ at 2030) is shared by all three fits and cancels.
- **Photocentre:** offset from the JPL orbit grows sunward on approach (−0.1″ anti-sunward at 28–29 AU → +0.28–0.35″ sunward at 23–25 AU; r=−0.873 over 32 epochs, outlier-robust; perpendicular ~0 while the sunward axis rotates). Literature: arXiv:1507.01980 (tailward offset with aperture); arXiv:2507.13409 (3I/ATLAS Rubin points sunward of a tailward-dragged orbit). Interpretations: sunward inner-coma fan, or orbit absorbing biased later astrometry; both activity effects, not pipeline defects.
- **Method criterion:** comet astrometry requires a quiescence check or an activity-dependent photocentre caveat before submission.
- **Verification:** fresh per-epoch Horizons calls reproduce stored ephemerides to 4–14 mas and PsAng exactly (rule 1 holds); sunward projection re-derived to 1 mas (sign convention correct); search centres are predictions, never published positions. Data notes (REPORT.md): packed designation CK14UR1N; exposure-name timestamps offset ≤140 s. Artifacts: comet_benchmark/ (54 files).
- **Update (2026-07-08, later):** full independent verification complete; verdict stands; all criteria pass with 6–20× margins. Corrections (REPORT.md addendum):
  1. "≈0 sunward at 28–29 AU" is wrong: early epochs are −0.163″±0.022 anti-sunward (zero crossing ≈27.7 AU), so the early offset is at least partly a JPL-arc artefact.
  2. Sunward and anti-velocity frames are degenerate here (anti-velocity r=−0.889 vs sunward −0.873; PA-rotation discriminant weak). Mechanism: a mix of real sunward photocentre in the active phase (Farnham+2021: sunward coma enhancement in UN271) and orbit-arc absorption (Rubin 3I/ATLAS §4.4/4.6).
  3. The earlier 3I/ATLAS paraphrase had the sign reversed: their coma is sunward, residuals anti-sunward of the dragged orbit.
  4. find_orb e=1.004 vs SBDB 0.9991 is an osculating-epoch effect; find_orb matches Horizons same-epoch e to 2×10⁻⁵.
  5. "10/10 detected" is 10/10 of an undocumented hard-coded subset; a non-selected epoch gave a clean detection at 0.255″ (no forcing).
- **Method criterion (refined):** active-phase comet astrometry carries a ~0.2–0.4″ photocentre systematic, not the 0.05″ TNO floor.

### 2026-07-07 — Wave 3: KK76/(88268) HST 4-point chain measured; rule-v3 re-cut failed verification; refit started
- **Track A (HST): DETECTED_PARTIAL, stands.** 2001 KK76 is numbered (88268). The 2006-05-02 frames are ACS/HRC (not WFC), program 10514 (PI Noll), TARGNAME 88268 (pointed).
  - Chain: one source in all 4 frames, flux stable to 5%, moving along the @hst-parallax-modulated predicted vector (first interval to 1 mas); mean O−C 0.29″ = 0.18σ inside the verified ellipse.
  - Negative controls: reversed/perpendicular vectors 0 chains; stationary 21 static stars; 16/18 field stars static <50 mas while the source moved 690 mas.
  - WCS: per-exposure FLT (no drizzle), full SIP+CPDIS distortion, HSC30 (Gaia-tied) active WCS, pooled Gaia DR3 anchor N=17 (residual −2,−7 mas).
  - Astrometry: 4 positions, obscode 250, per-axis σ 0.16″/0.10″ (weighted at these σ, not the tens-of-mas internal level); arc +1.94 yr past 2004-05-28. File: wave3/hst_kk76/candidate_astrometry.csv.
  - 2010 WFC3 visit: bounded non-detection (off the small UVIS subarrays along the 8.3″ 1σ axis; IR motion unresolved) after 5 search strategies. @hst observer-centre ephemerides required (96-min orbital parallax wobble).
- **Track B: rule-v3 re-cut failed verification.** Claimed 50 passers (top 8 ranked). An independent get-obs parse found self-arcs (2009 QV38 and 2008 SJ236 have F51 observations inside the claimed overlap windows) and wrong arc-end years (2002 KW14 ends 2015, not 2009; 2004 HF79 ends 2016). No attempts run (0 attempts, 0 bycatch). Vetted trio for wave 4: 2007 HV90, 2002 KW14, 2010 JK124 (2017-07 DECam clusters).
- **Method criteria (re-cut):** arc-end parsed from get-obs, never from the campaign CSV staleness column; a target whose overlap window contains its own observations is rejected (self-arc test).
- **Next step:** KK76 joint refit + ADES draft with the local find_orb build (UTC/TT column fix; σ 0.16″/0.10″; no photometry, HRC CLEAR mags are lower bounds only). Wave-4 execution and re-cut repair: pending user decision. Artifacts: docs/reports/precovery_campaign_2026_07_07/wave3/.

### 2026-07-07 — (330836) Orius = 2009 HW77: literature, occultation context and effect of 6 archival positions
- **Literature (reproduced in a re-check):** 3 refereed papers, all from the discoverers' group (Wlodarczyk/Černis/Eglītis 2011 MNRAS, 2016 data paper, 2024 Open Astronomy), dynamics only. Verified absent (source tables checked) from TNOs-are-Cool (no thermal size), MBOSS (no colours), LCDB (no rotation), Johnston, and all 4 DES catalogs. Physical data: H=9.73 only, giving D≈30–65 km; colour, rotation and spectrum unmeasured. Dynamics: "diffusing" Centaur, half-life ~4.5–5 Myr, ~27% JFC-capture probability.
- **Occultations:** on the Lucky Star and RECON target lists (RECON attempted a 2018 event: 1σ 576 s / 2141 km). Arc-only ephemeris 3σ sky error ~14″ (~230,000 km).
- **find_orb with and without our 6 points (reproduced to the digit):** sky-plane 1σ uncertainty 3.69″→1.11″ (2026), 4.27″→1.34″ (2030), 7.33″→2.51″ (2040), i.e. ~3× per axis and ~10× in area. The arc-only prediction is offset 6.9–14.1″ (≈1.9σ) at all three epochs. U 3.0→2.5. All 6 points retained; max residual 0.33″.
- **Photometry (corrected):** the first consistency check used wrong comparison dates (epoch-substitution error). Corrected: our magnitudes sit at the ~1σ faint edge of H=9.725±0.343 (H≈9.9–10.1), consistent with the Hv=9.9 adopted by Lucky Star/RECON. No variability detected at n=6.
- **Journal:** first solar-system object journal: docs/object_journals/mp_330836_orius.md (key `mp:<number>`) + INDEX row. Artifacts: docs/reports/precovery_campaign_2026_07_07/orius_deepdive/.

### 2026-07-07 — Precovery wave 2 (5 targets): 0 recoveries; pointed HST frames found for 2001 KK76
- All five outcomes confirmed on re-check; search-box centering sub-arcsec correct for all targets.
- **2001 KJ76: null (pixel level).** 16 deep CFHT/MegaCam 2006-04-23 CCDs, Gaia-DR3-re-anchored WCS rms 0.02–0.09″; ±40″ digital-tracking scan shows only noise at predicted V~22.8; control stars to i~23.
- **2001 KP76: null (two-channel catalog).** NSC 13 nights + PS1 35 nights; 212/216 in-ellipse objectids are catalogued stationary stars; the 4 others are all ≥1.3 mag too bright, with no cross-night track.
- **2001 KK76: soft null (depth- and crowding-limited).** The only tight epoch (2005) has no deep imaging; deep epochs lie in the bulge with 21–122″ boxes; PS1 field statistically identical to the +1° control. NSC service was down (logged, not counted).
- **2006 JG57 and 2004 YH32: no archival coverage.** JG57: SDSS scanned the RA box in 2005 at Dec 19–24 while the object was at Dec ~51 (minimum separation 1773.4′, reproduced). YH32: the whole 2005 apparition was at 33–70° solar elongation, matching its MPC arc gap; 0 SSOIS rows in 2005.
- **Finding:** for early-2000s discoveries, tight-uncertainty epochs (~2005) predate the deep archives (SSOIS deep imaging from ~2006, DECam 2012+), while imaged epochs (2013+) carry large post-arc boxes in bulge crowding. Wave 1's recovery (HW77) had its arc end in 2012, inside the DECam era.
- **Target-selection criteria adopted:** arc end ≳2010, so that epochs passing the SMIA cut overlap deep imaging; require imaging at the passing epoch (SSOIS per epoch), not whole-arc footprint counts (KK76 had deep_fp=1283 but no imaging at the tight epoch).
- **2001 KK76 pointed HST frames:** 12 frames targeted on the object (2006-05-02 ACS 4×240 s; 2010-03-13 WFC3 F606W/F814W/F139M/F153M ×8), astrometry not in the MPC record (arc ends 2004-05-28; no code-250 observations). Measuring them (FLT pixel astrometry, Gaia-DR3-anchored WCS) would extend this 4-opposition TNO's arc by +6 yr. Pending user decision; frame IDs and Datalink URLs preserved.
- No submissions from wave 2 (nothing measured). Artifacts: docs/reports/precovery_campaign_2026_07_07/wave2/.

### 2026-07-07 — Blind NSC novelty gate: no-go (prior art); bycatch harvester built (18/18 tests)
- **Gate: no-go.** Blind NSC catalog-tracklet mining for new solar-system objects has prior art:
  - Asteroid Institute/B612 ADAM::THOR (arXiv:2105.01056) ran over 100% of NSC DR2 (~1.7B sources): ~27,500 new candidates incl. 100s of Centaurs and 10s of TNOs (b612.ai/thor-nsc).
  - CANFind DR2: AAS 241 (2023AAS...24113603F) reports ~600,000 SSOs identified in DR2 (corrects an earlier description of the project as stalled).
  - Below catalog depth (V≳23.5), shift-and-stack is done by DES/Bernardinelli (incl. C/2014 UN271), DEEP I–VI, YOSO (arXiv:2605.06913) and Rubin (DP1 30 Jun 2025; SSP links nightly).
- **Pilot:** one 9 deg² non-DES DECam night gave ~46 raw 2-point pairs/deg² with a monotonic rate histogram, consistent with chance coincidences. Orphan query re-run bit-exact (22,446).
- Lane closed; no NSC DR3 exists. The arXiv-only prior-art check had missed the THOR release; gates now also search press coverage.
- Naming rules verified: archival comet finds carry the finder's name (UN271, MPEC 2021-M53); minor-planet discoverer status is assigned at numbering.
- **Bycatch harvester built:** `scripts/precovery/{bycatch.py, test_bycatch.py, README.md}`. Same-night pair/triplet former (0.5–120″/hr, direction and rate-ratio consistency), stationarity rejection, magnitude check, live MPChecker identification (knowns logged; unknowns flagged for review, never auto-claimed).
  - Positive control: the 6 Orius detections give exactly 2 same-night tracklets (0.81″/hr and 3.52″/hr), both identified live as (330836) at 0.66″/1.7″.
  - Negative control: QT322's stationary field gives 0 survivors.
  - Method criterion: the static/mean-object catalog filter is required; catalog scatter on one star produces in-window "movers" that the rate floor alone does not remove.
  - Re-check with synthetic movers and fakes passed; epoch-shuffle error absent.
  - Defect fixed: a 3-point mover no longer emits a redundant endpoint pair (subset-dedup in form_tracklets); 2 regression tests added; 18/18 passing, including both live MPC asserts.
  - Scope: provenance logger for the precovery lane, not a discovery tool; used from wave 3 on.
- **2026-07-07 (late): ADES draft prepared** at docs/reports/precovery_campaign_2026_07_07/verify/2009_HW77/ades_draft_330836_orius.psv. 6 rows from updated_astrometry.csv (obsTime = FITS-header MJDs, verified to 5 decimals; NSC Gaia-calibrated positions; per-axis rms 0.12–0.25″; W84; measurer A. Keur; per-row exposure IDs in remarks; header states SARC first). Not submitted; awaiting SARC contact and review.
- **Terminology correction:** SARC = Singletons and Archival observations Committee (minorplanetcenter.net/mpcops/documentation/sarc/), not "Survey Astrometry Review Committee" as written earlier. First-time archival submitters are verified by SARC before the MPC accepts the file.
- KN76: decision pending (seek a 3rd epoch or park). Verification tooling (cutout/PSF harness, find_orb joint-fit and MC-covariance scripts) in docs/reports/precovery_campaign_2026_07_07/verify/.

### 2026-07-05 — Literature scan of candidate archival lanes: breadth search frozen until Gaia DR4
- Scan of new lane ideas against closed lanes, with prior-art and telescope-requirement checks: 12 ideas, 5 shortlisted, 0 discovery lanes retained (empty target population, 2025–26 prior art, or telescope confirmation needed).
- **Two lane-closing prior-art results (verified against arXiv):**
  1. **XP-at-scale: closed.** Li, Rix, Ting, Müller-Horn, El-Badry et al., "Millions of Main-Sequence Binary Stars from Gaia BP/RP Spectra" (arXiv:2507.09622 = A&amp;A 704 A126, 13 Jul 2025): full-archive XP single-vs-binary χ² search, 35M stars → 14M binary candidates → ~1M high-purity. A dark companion leaves no XP flux signature, so BH/NS/WD companions fall in the single-star bucket (the paper needs kinematic/astrometric data for them).
  2. **Sub-NSS dormant-BH cut: requires telescope follow-up.** Müller-Horn, Rix, El-Badry et al., "Dormant black hole candidates from Gaia DR3 summary diagnostics" (arXiv:2510.05982, 7 Oct 2025, rev. Mar 2026): RUWE + RV-scatter below-threshold cut gives 389 RGB+BH candidates (+279 MS); confirmation deferred to FEROS spectroscopy and Gaia DR4.
- **Other prior art found:**
  - ETV+astrometry dark-tertiary method: arXiv:2512.20087 (V Pup / CY Ari).
  - Independent audits of published compact-object candidates: An &amp; Gu arXiv:2601.22490; Nagarajan et al. arXiv:2601.22071 (PASP); Simon et al. arXiv:2603.20371, which demoted this project's GALEX J033455 from archival data alone.
  - DESI-DR1 object search: A. Smith, RNAAS 10.3847/2515-5172/ae3f28; occurrence-limit method: El-Badry et al. arXiv:2412.02082.
  - Physical limits: a compact object cannot eclipse a luminous primary (that channel is self-lensing, already covered); NSS inclination is already Thiele-Innes-fitted.
- **Decision: breadth search on existing archives frozen until Gaia DR4 (2 Dec 2026)**; DR4 harnesses and 9-object pre-registration ready. Two optional pre-DR4 bench tasks:
  - (A) fold the documented retraction set (CRTS J051419, GALEX J145250 ellipsoidal, 5858574 mass-gap→triple, WDJ super-Chandra, Thiele-Innes cos-i bug) into the DR4 re-fit engine as a labeled false-positive test harness;
  - (B) compute the DESI-DR1 selection function to test whether a dark-companion occurrence limit could improve on Gaia RVS.

### 2026-07-14 — Community-initiative scan: Rubin unadopted-tail forensics and VSX data-mining as gated candidates; citizen-science platforms not pursued
- Scope: new novelty-discovery routes modelled on community initiatives.
- **Landscape changes since 07-08 (verified):**
  1. Rubin vetting gap: 7 full-stream brokers live (~7M alerts/night, public); spectroscopic follow-up <0.1%; Fink anomaly review = top-10/night to 31 volunteers (arXiv:2603.29511); ELEPHANT hostless funnel 877→67 over 28 months, now running on the Rubin stream (arXiv:2605.22407).
  2. Recent public-archive results: And XXXVI dwarf galaxy in 15-yr-old PAndAS data (arXiv:2603.28492); Deen & Lam 2024 YR4 precovery (arXiv:2603.00449).
  3. NEOWISE archive mining has prior art: VarWISE arXiv:2605.19059 (all-sky) and Guidry/Hermes/De arXiv:2406.18646 (WD-targeted); BYW's 3,006-candidate release was SPHEREx-typed by a professional team within weeks (arXiv:2604.22012).
- **Citizen-science platforms: no-go (revised from marginal).** Zooniverse volunteer classifications are the ML training product (automating them would contaminate outputs incl. Rubin's real/bogus score); both niches examined had prior art.
- **Lanes and gates:**
  - Go: Lasair-LSST passive watchlists (dormant-CO candidates + known-objects file, Kafka output). Gate: token/re-login check; the Lasair-ZTF token does not transfer (user re-registration if needed).
  - Go candidate: Rubin post-flag archival forensics on the unadopted tail (hostless/anomaly leftovers; ATLAS/ZFPS/DECam/DASCH; output as annotations, AstroNotes, VSX). Gates: measured year-1 artifact ratio; a demonstrated consumer. Southern ZFPS gap noted.
  - Go candidate: VSX archival variable mining (VSX policy verified: data-mining discoveries without own photometry are credited by name; SNAD-VIII: ~1.5 novel/field, mostly mundane). Gate: AAVSO account + current VSX manual; stop below the SNAD baseline.
  - Go candidate: TESS FFI morphological-oddity triage of the ~4,400 cached EB light curves. Gate: novelty audit against VSG/EBP/TESS-Ten-Thousand/VSX; not a repeat of the closed M2 hunt.
  - Marginal: ultra-faint satellites in deep pointed archives (gate: residual parameter space vs Martin+ completeness); SWAN comet sidecar (Bezugly precedent; gate: dry-run on C/2025 F2/R2 windows); Fink anomaly-loop vetting (Fink files under its own name; ZTF-only until a Rubin port is confirmed).
- **Not pursued:** NEOWISE WD IR mining (two prior works; photon-limited); BYW downstream vetting (consumed by professionals within weeks); wide-field LSB/dwarf ML mining (GOBLIN arXiv:2505.18307, Euclid); radio-ORC solo search (platform/membership-gated). Rejected as precedents: AM CVn 2505.20842 (real-time discovery); 820-CV precedent (2019 data); "~10 individuals worldwide" (unverifiable). Also excluded: real-time discovery races, TFOP SG1, Einstein@Home, IOTA analysis, GMN, VASCO (dormant), Exoplanet Watch.
- **Planned sequence:** watchlists; one-night pilot (forensics on 3–5 unadopted hostless/anomaly flags, both gates); TESS novelty audit; AAVSO account. Marginal lanes blocked until a gate passes. Orius/KK76 filings and Gaia DR4 (2 Dec 2026) remain the main items.

## 2026-07-15 — Rubin pilot: watchlists prepared; unadopted-tail forensics gates answered; lane proceeds

- **Pilot ran 2026-07-14→15.** Artifacts and synthesis in `docs/reports/rubin_pilot_2026_07_14/` (summary: `PILOT_SYNTHESIS.md`).
- **Gate 1 (artifact ratio): pass, measured.** 772 Fink/LSST flags over 6 nights; stratified vetted sample n=40 gives 37.5% artifacts, channel-dependent: hostless/ELEPHANT 0/10, bright lt20mag 0/10, faint extragalactic_new 15/20 (year-1 template residuals). Lane restricted to the clean channels until DR1.
- **Gate 2 (consumer): prepared.** 4 consumer packages (TNS AT ×2, AstroNote+VSX, Fink feedback); mechanisms verified live. In-sample: SN 2026uid was adopted only after FLEET's TNS filing. Gate 2 completes only on filing; otherwise it reverts to untested.
- **Five candidates (4 interesting, 1 mundane; verdicts confirmed on re-check):**
  - 170587105461272950 = unreported SN (=ZTF26abfwqfp); TNS draft ready; near peak.
  - 170635519425249637 = active unreported SN II-plateau candidate; ZFPS shows the rise 22 d before Rubin; TNS draft ready.
  - 170591519677875016 = month-long blue transient; ATLAS pre-discovery ≥16 d; Rubin template shows an r=23.96 counterpart below archival depth (ELEPHANT "hostless" is depth-limited).
  - 170587115976392822 = ZTF19abxfaon, uncatalogued ~5.2-mag CV-like variable over 8 yr; AstroNote+VSX drafts.
  - 170591507978387512 = mundane SN (negative control); PS1 "precursors" rejected as masked-pixel artifacts (precovery acceptance rule 10 applied to PS1).
- **Package corrections:**
  - -950: atlas_fp.csv regenerated from completed ATLAS task 4542361 (0/1,023 pre-event nightly stacks ≥4σ); task-id fixes.
  - -822: epoch error fixed: peak zr=17.976 at MJD 59218.078, not ~59470; first-bright 21.24; ALeRCE CV/Nova 0.95–0.97 added.
  - -637: "precursor" relabelled as pre-Rubin confirmation; ZTF-r/LSST-r 0.4-mag calibration caution added.
  - -016: template-epoch caveat added.
- **ZFPS:** 6 IPAC light curves mapped by reqid→position and analysed (`zfps/ZFPS_ANALYSIS.md`). Parsing correction: procstatus 56/57 are warnings (57 = no ref-catalog source within 5″, expected at hostless positions) and the flux is valid; a first-pass procstatus==0 cut had wrongly nulled 2 candidates. Corrected analysis: -950 quiet for 8 yr, then SN; -637 rise 22 d before Rubin; -822 variable over the full 8 yr; -512 single g 7.8σ at MJD 60094.4 rejected as ndet=1 single-band (r −0.6σ the same night, +57 min).
- **Watchlists:** both CSVs built (13-row dormant-CO list, PM-propagated J2026.5 positions; 19,168-row known-objects list). Creation is web-UI only (user). Live instance is lasair.lsst.ac.uk; the ZTF token returns 401 there (valid on lasair-ztf); user must re-register.
- Stamp classifiers miscalled all 4 interesting objects (bogus/asteroid/AGN).
- **Pending user actions:** TNS ATs for -950 and -637; AstroNote+VSX for -822; Fink feedback for -016; Lasair re-registration, 2 watchlists and annotator-topic request; Orius and KK76 MPC filings.

## 2026-07-15 (later) — Period search on ZTF19abxfaon: null
- 1,687 ZFPS epochs over 8.1 yr (per-band + rfid 15-d running-median de-trend).
- LS 30 min–2 d: one marginal r-band 46.6-min alias family (power 0.048 vs bootstrap 99% 0.044), rejected by split-sample test (both halves peak elsewhere, below their own thresholds), colour (g power 0.009) and amplitude (4.2 µJy < 5.0 µJy median error).
- BLS 1.4–48 h: null (229 vs 1220). 10–300 d: weak ~200 d quasi-periodicity only, not claimed.
- Injection-recovery: semi-amplitude ≥5 µJy (≈0.06 mag in bright state) recovered 20/20 at P=1.5–4 h. Excludes an eclipsing CV and high-amplitude superhumpers; consistent with a low-inclination CV.
- VSX/AstroNote drafts updated with this null. Method: rubin_pilot_2026_07_14/forensics/170587115976392822/PERIOD_SEARCH_2026_07_15.md.

## 2026-07-15 — Lane scan v5: 17 ideas, 6 clusters, 5 open, 1 closed
- Full menu with gates: docs/reports/ideation_scan_2026_07_15/MENU.md.
- **Lanes:**
  - Go: by-products: RNAAS note on the Rubin year-1 channel-resolved artifact rate (RNAAS: free, no affiliation, DOI/ADS, accepts nulls); Zenodo year-1 RB benchmark; limited AstroNotes.
  - Go candidate: CV state census (Duffy+2024 8-object baseline, ~1,500 nova-likes in ZTF/ASAS-SN/ATLAS). Users of the output: AAVSO campaign #926, recurring HST low-state scheduling alerts, VSX subtype revisions (MGAB precedent). Symbiotic sub-lane cut: Merc/NODSV works the same targets.
  - Go candidate: orphan worklists into the VSX lane: GFCAT 588 undescribed UV variables (live zero-record VSX check), Gaia Science Alerts 19,515 unknowns, EXOD 32,247. Gate: moderator pre-clearance.
  - Go candidate (gated): demand-driven solar-system astrometry. Gate: occultation-demand census (a re-check found 0 qualifying events this month vs an initial 2–5/month). Long-period comet precovery: prior art by Deen. ITF as support tool only. Euclid DR1-Foundation (Nov 2026) window and obscode inquiry noted.
  - Go candidate (background): spectral-archive VSX corrections (SDSS-V DR20 southern BOSS + LAMOST DR12). Moderator acceptance untested.
  - No-go: irregular-moon recovery. The Ashton team re-mined its own archive 4 months earlier (MPEC 2026-F14); a 3-mag depth gap separates this from the Kai Ly precedent. Closed permanently.
- **Execution order adopted:** SSOLS pointed-HST + RNAAS note → AAVSO-gated census and worklist pilots → occultation census gate → TESS audit → demand-filtered precovery re-cut (replacing the blanket ~90-target re-cut).

## 2026-07-15 (later) — Decision (user): SSOLS and propagation lanes shelved; objective set to novelty discovery
- Decision (user): SSOLS pointed-HST mining and the propagation-labor lanes (VSX orphan worklists as main lane, spectral corrections) shelved. Objective: novelty discovery; lanes ranked by novelty per unit labor.
- Active: Rubin unadopted-tail weekly lane, CV/state-cycler novelty search (lane scan v5 CV cluster + uncatalogued-CV archetype), TESS cached-EB oddity audit, Gaia DR4 (2 Dec 2026). Orius/KK76 filings unaffected. RNAAS note optional.

## 2026-07-15 (later) — RNAAS note drafted (year-1 channel-resolved artifact rates); novelty checked; one correction
- Draft at rubin_pilot_2026_07_14/rnaas_draft/ (rnaas_note.tex): 957 words vs the 1,500-word/150-word-abstract limit (verified at journals.aas.org); Wilson 68% CIs computed and checked; AI-use disclosure per AAS policy DOI 10.3847/25c2cfeb.c3619710.
- Novelty check 2026-07-15: 11 arXiv queries plus scope checks on near matches (ELEPHANT/ZTF 2605.22407, DP1 papers, Prompt Processing 2603.19541); none measures channel-resolved artifact rates on the live year-1 stream.
- Submission route (user, optional): ORCID → Overleaf compile → aas.msubmit.net; no fee; ~72 h. Not submitted.
- **Correction (also applied to PILOT_SYNTHESIS.md):** bright lt20mag channel = 7/10 non-transients (5 AGN + 2 variables), not 6/10. ALeRCE miscalls per flags_sample.csv are asteroid 0.89–0.98 (7 objects) and bogus 0.83–0.90 (3 hostless, including the TNS-confirmed SNe); the "bogus 0.65" figure applies only to ZTF26abfwqfp's ALeRCE-ZTF stamp. Artifact-rate conclusions unchanged.

## 2026-08-13 — State-cycler density pilot v1: 0/40 confirmed; ranking metric biased against the target class
- Field: 298.5 deg² (RA 330–360, Dec 0..+10, |b| 34–60). ALeRCE harvest: 1,976 candidates with amp≥2.0; 40 screened survivors; 10 verified: 9 flat bright stars whose "amplitude" was difference-image magpsf blow-up (subtraction residuals dominated by isdiffpos=-1) + 1 known SN 2022okv.
- **Systematic:** alert-space amp_proxy is inflated for bright references and compressed for the target class (faint quiescence): ZTF19abxfaon's 5.2 mag becomes 2.24, below the effective 2.72 screening cutoff, so the archetype would be harvested but not screened. The 50–300 sky-wide estimate is not tested.
- **Method criteria adopted:** (a) difference-mag amplitudes are invalid within ~1″ of a bright reference; rank on corrected/DR photometry. (b) A template-driven search must recover its archetype by injection before any density claim. (c) Negative-diff fraction and a bright Gaia counterpart are used as pre-kills.
- **Bycatch:** ZTF18abxnwmb = uncatalogued detached EA eclipsing binary, G=12.7, P=3.72689 d, depths 0.2/0.1 mag (for VSX).
- v2 planned: re-rank the cached 1,976 on corrected photometry, injection test, re-screen, verify top ~20. Pre-registered: ≥1 novel/ambiguous keeps the lane open; 0 after a passed injection gives an upper limit and closes it. Report: docs/reports/state_cyclers_2026_08_13/PILOT_V1_REPORT.md.

## 2026-08-13 (later) — State-cycler re-rank v2: injection test failed; rerun required
- v2 (corrected-photometry re-rank of the 1,976): 19 passers, all catalogued (13 known dwarf novae recovered from v1's kill list, which validates the metric for detected-state cyclers; 1 SN, so a transient veto was added for v3); 0 survivors.
- **Injection failed:** ZTF19abxfaon's corrected p98–p2 amplitude = 1.31 (r) < 2.0 gate. Its 5.2-mag range spans quiescence below the alert threshold (r~23, zero detections) and outburst, so any detection-only statistic is capped at the detected bright-state spread. Hostless objects also lose g entirely (corrected=false, magpsf_corr all null). v2 was stricter than v1 for the target class.
- Density for the target class: not computable (completeness ~0). Conditional result: <151 uncatalogued detected-state cyclers sky-wide (95%, high-|b| caveat).
- All 274 v1 screen kills were within 2″ (no wide-radius over-kill; 0 resurrections).
- **v3 method:** injection first, as a hard gate. Amplitude = brightest positive-diff detection minus deepest same-band non-detection limit (ALeRCE non_detections diffmaglim), a lower bound that includes below-threshold quiescence; no corrected-photometry requirement for hostless objects; pre-kills unchanged (archetype passes both); TNS-window transient veto added. Report: state_cyclers_2026_08_13/V2_RERANK_REPORT.md.

## 2026-08-13 (final) — State-cycler search v3: injection passed; lane closed with a density upper limit
- **v3 limit-based amplitude recovers the archetype:** ZTF19abxfaon amp_v3 = 2.185 (g 2.085 / r 2.185; brightest r detection 18.318 vs deepest r limit 20.504; neg_diff_frac 0; hostless).
- Chain on the cached 1,976 (298.5 deg², RA 330–360, Dec 0..+10, |b| 35–60 S): 799 pass → 744 screened in / 520 catalogued → 60 uncatalogued survivors → 0 confirmed novel. 14/14 individually vetted (top 8 by amplitude + 6 more, including ZTF19acueloy, the only out-of-channel object) are artifacts; the other 46 share the same signature (bright in-reference Gaia star with parallax at the alert position).
- **Purity problems (v4 fixes):** the bright_ref pre-kill was inactive (ALeRCE /objects/{oid}/lightcurve omits `magnr`); the amp_v3≥2.5 waiver is inverted for saturated/in-reference stars (amp_v3 inflated by construction, 5.9–7.4); max(diffmaglim) is sensitive to single bad limits (one 23.86 seen), use p95; shallow-limit fields under-measure amplitude.
- **Result (pre-registered criterion: 0 novel/ambiguous with passed injection → lane closes):** high-latitude surface density of ZTF19abxfaon-like state-cyclers < 0.0100 deg⁻² (95% Poisson UL, 0 in 298.5 deg²). Sky-wide <~415 only under a uniform-density assumption, which does not hold (the class follows stellar density; |b| 35–60 says nothing about the plane/bulge). Completeness rests on one injection at a 0.185 mag margin. The "50–300 sky-wide" estimate is not excluded (a plane-weighted population fits a high-latitude null).
- **Bycatch (for VSX, pending an AAVSO account):** ZTF18abxnwmb (detached EA, G=12.7, P=3.72689 d, depths 0.2/0.1 mag); ZTF18abtqnkv (uncatalogued low-amplitude variable, DR ptp ~0.8–0.9 mag gri over 8 yr, G=15.99, plx 1.90).
- Report: docs/reports/state_cyclers_2026_08_13/V3_FINAL_REPORT.md (with PILOT_V1_REPORT.md and V2_RERANK_REPORT.md for v1 and v2); scripts alongside.

## 2026-09-18 — TNS cone re-check: 170587105461272950 reported by Fink as AT 2026uxw; 170635519425249637 not in TNS
- 170587105461272950 = ZTF26abfwqfp = AT 2026uxw (TNS 214935), reported 2026-07-16 08:34:55 UT by R. Durgesh (independent), P. Pessi, E. E. O. Ishida, J. Peloton for the Fink collaboration (ELEPHANT module authors). Same position (22:16:59.909 −18:12:28.62), same discovery alert (their 2026-06-26 08:50:38 UT = our MJD/TAI 61217.3685 08:50:02; 37 s = TAI−UTC), same 1.31 mag/15 d i-band rise.
- Our package was complete on 2026-07-15 and not filed (~17 hours before the Fink report; corrected below).
- **Status:** discovery reported by Fink; unclassified (Type ---, no classification reports). Our archival results (8-yr ZFPS null / 857 pre-event epochs; 11-yr ATLAS null, 0/1,023 nightly stacks ≥4σ; ZTF confirmation at 0.12″) could go to an AstroNote or the reporters.
- 170635519425249637: not in TNS at 10″ and 60″. AT draft still filable; spectroscopic classification no longer feasible (~2 months post-plateau).

## 2026-09-18 (same day) — Timing correction; re-checks of the remaining objects
- **Correction:** the interval between package completion and the Fink report was 24 h 57 m, not ~17 hours. Package committed complete 2026-07-15 07:37:58 UTC (bff17af); Fink report 2026-07-16 08:34:55 UT. The 17 h figure was unverified arithmetic.
- Live checks 2026-09-18, all clean: TNS 60″ on 170635519425249637, 170591519677875016, 170587115976392822 and the control 170591507978387512; VSX 30″ + SIMBAD 10″ on ZTF19abxfaon and both state-cycler bycatch objects (ZTF18abxnwmb RA 338.60553 Dec +8.11656; ZTF18abtqnkv RA 355.37745 Dec +3.75413; coordinates recovered from ALeRCE).
- VSX cone parser positive-controlled on SS Cyg and RR Lyr.

## 2026-09-18 (third) — AT 2026uxw timeline; Fink ELEPHANT module
- **Correction to the timeline:** discovery epoch 2026-06-26 08:50 UT; Fink report 2026-07-16 08:35 UT, i.e. 20.0 days unreported. Our sweep of MJD 61228–61235 (Jul 7–14) found it at ~day 19; package complete at day 19.0; Fink report 24 h 57 m later.
- **ELEPHANT (arXiv:2605.22407; A&A 2024 arXiv:2404.18165):** continuously running Fink module (stamp-based hostless selection). 877 ZTF objects flagged Sep-2023 to Dec-2025; 67 confirmed hostless + 51 with visible but uncatalogued hosts; accuracy 0.84. On the Rubin stream since Feb 2026; 3 candidates reported from the early LSST stream, 2 spectroscopically classified, including SN 2026ejf (SLSN).
- Their TNS report gives one sentence of photometry (1.31 mag / 15 d i-band rise, "appears to be at its peak"); unclassified at 2 months.
- Our per-object data: 857 pre-event ZTF epochs, 1,041 ATLAS nightly stacks, two-survey astrometric confirmation at 0.12″.

## 2026-09-18 (fourth) — Rubin alert stream empty since MJD 61235; Prost host-association code
- Fink/LSST returns 0 alerts for every API-supported tag (hostless_candidate, extragalactic_lt20mag/new, most_likely_sn, sn_near_galaxy, in_tns, faint_trails) from 2026-07-15 to 2026-09-19. Control window 2026-07-07 to 07-15 returns 20/105.
- Last night with alerts in every channel: MJD 61235 (2026-07-14/15), the last night of our pilot sweep. ALeRCE-LSST stops at the same timestamp (lastmjd 61235.41918): a Rubin-side gap, not a Fink outage. Cause not established. No lane input for ~2 months.
- **Method gap:** `astro-prost` (Gagliano; github.com/alexandergagliano/Prost, readthedocs astro-prost), found via the ELEPHANT team's stack: Bayesian host-galaxy association related to PATH (Aggarwal+2021, arXiv:2102.10627). Monte-Carlo samples candidate-galaxy brightness, redshift and fractional offset against configurable priors over GLADE+, DECaLS, Pan-STARRS and SkyMapper; returns a posterior per candidate, including "host unseen/unobserved". Not previously used in the repo.
- Pilot host association was LS DR10 tractor nearest-neighbour plus offset plausibility (e.g. "REX at 1.01″ ≈ 1.4 Re", "PS1 stack source at 0.71″"). The depth-limited-hostless claim for 170591519677875016 (template flux r=23.96, below every archival catalog) needs a P(unseen host) value.
- Planned: run Prost on the 5 dossiers; consider FrankenBlast (arXiv:2509.08874) for host photometry/SED.

## 2026-09-18 (fifth) — Prost re-analysis of the 5 dossiers: not usable as configured
- Report: docs/reports/prost_reanalysis_2026_09_18/REPORT.md (+ raw CSVs + scripts). astro-prost with demo-default SN priors, catalogues glade+decals+panstarrs.
- **Result: not usable.** Prost assigns hosts at 10.5–18.1″ (P = 0.46–0.92) where the pilot identified candidates at 0.48–1.01″; all redshift/absmag columns null.
- Cause: Prost queries DECaLS DR9, which does not cover these DES-footprint fields (DECaLS-only control gives best_cat NaN for all 4 transients). Our pipeline used LS DR10 via Data Lab TAP (deeper). With DECaLS empty, Prost falls back to Pan-STARRS offset-only ("panstarrs does not support conditioning on absmag"): purely geometric association.
- Self-association: at ZTF19abxfaon's position DECaLS DR9 catalogues the CV itself as extragalactic (z_phot 0.93, M_r −21), giving P(host)=1.000 at 0.14″. Method criterion: Galactic point sources pass a star/galaxy gate before host association.
- **Correction:** `none_posterior` ≈ 1e-12 for every object, including the depth-limited-hostless one; Prost as configured does not give P(unseen host), contrary to the previous entry. A PATH-style P(U) with a depth-tied unseen-host prior is not built.
- Rubin status: community status (last update 2026-08-02) reports summit access blocked by heavy snow on the Cerro Pachón road. The live alert-stream Grafana dashboard linked from rubinobservatory.org live-status is the lane's go/no-go check.
- **Prior art:** "Lost and found: a gallery of overlooked optical nuclear transients from the ZTF archive" (A&A 2026, aa58465-25), described here as archival mining of unreported ZTF transients (scope corrected next entry); MeerLICHT archival transient mining (arXiv:2609.01052); ATLAS100 volume-limited sample (arXiv:2603.03069); SNAD Transient Miner (ZTF DR k-D trees). Common practice: multi-survey composite light curves (ZTF g/r + ATLAS c/o + MeerLICHT/Pan-STARRS), as in our forced-photometry stack.

## 2026-09-18 (sixth) — "Lost and Found" (ZTF archive) cross-check: no overlap
- Paper: arXiv:2511.19016 / A&A 2026 (aa58465-25), Fink collaboration. A TDE early-detection classifier for ZTF; 19 optical nuclear transients found during development or by applying it to the archive (9 passive hosts, 8 active, 2 uncertain; 2 repeating-TDE candidates, 1 >5-yr transient, 3 ENT candidates).
- **Cross-check, no overlap:** (a) by name, none of ZTF26abfwqfp, ZTF19abxfaon, ZTF18abxnwmb, ZTF18abtqnkv is among the 27 ZTF IDs in the paper; (b) by position, all 27 IDs resolved via ALeRCE (27/27) and matched against our 7 objects; closest pair 1.54° (ZTF19abxfaon vs ZTF19aayijkh), ~5,500″.
- A first regex coordinate extraction from the paper text returned measurement values (e.g. 0.016/0.089) and "matched" at 300°+; discarded for ID-to-ALeRCE resolution.
- **Scope correction:** the paper is a nuclear-transient/TDE classifier applied to the ZTF archive (galaxy cores), not our selection (hostless/faint-host SNe + Galactic CV). The Fink collaboration applies purpose-built classifiers to the archive of its own streams.

## 2026-09-18 (seventh) — Fink classifier and crossmatch coverage
- Report: docs/reports/fink_coverage_2026_09_18/REPORT.md.
- Rubin/LSST stream (live alert packet, fink_science 8.52.0): 4 classifiers (CATS multiclass, SuperNNova SN-vs-others, Early SN Ia, ELEPHANT hostless) + 10 per-alert crossmatches (SIMBAD, TNS, Gaia DR3, VSX, GCVS, Legacy DR8, Mangrove, SPICY, 3HSP, 4LAC). No anomaly tag on LSST (re-confirmed).
- ZTF instance (~200k alerts/night) adds kilonova/fast transients, AGN, Solar System objects, anomaly detection, SLSN, TDE (new), orphan GRB afterglows, microlensing, multiclass; release 2.9 adds a second anomaly module + a time-series transformer. ZTF Fink API hosts unreachable (TCP) on 2026-09-18.
- Fink crossmatches VSX and GCVS on every alert, so "uncatalogued variable" status is computed; ZTF19abxfaon was visible to them but not followed up. Every Fink module ends in a transient candidate or contaminant label; none in a variable-star catalogue entry.
- Anomaly detection runs on ZTF and is absent on Rubin. All four INTERESTING pilot verdicts involved a year-1 classifier mislabel.

## 2026-09-18 (eighth) — VSX bycatch: ZTF18abxnwmb confirmed EA, ZTF18abtqnkv retracted
- Decision (user): file both bycatch variables (VSX submission is by the user's AAVSO account). Both re-derived from source data; the 2026-08-13 values came from a scratch run that no longer exists.
- **ZTF18abxnwmb = Gaia DR3 2710029878791087616 = 2MASS J22342534+0806596: confirmed detached EA.** ZTF DR (IRSA, 2,564 epochs / 7.4 yr, catflags==0): flat baseline ±0.007 mag; primary depth 0.216 mag (zr) / 0.250 (zg) / 0.189 (zi); secondary 0.105/0.114/0.110 at phase 0.5.
- P = 3.727026 ± 0.000082 d from 5 primary eclipses over 3.0 yr (timing rms 23 min); Min I HJD 2458257.8225 ± 0.0348 (revised in the tenth entry). Gaia: G=12.749, BP−RP=0.969, plx 1.368±0.025 (d≈730 pc), RUWE 1.20. The 2026-08-13 values (EA, P=3.72689, depths ~0.2/0.1) are reproduced. Light-curve and phase plots in vsx_bycatch_2026_09_18/.
- Meets the AAVSO VSX manual criteria, including period analysis for data-mined submissions. Primary name = 2MASS ID per manual §V.b (not Gaia). Open: passband (manual prefers V; data are ZTF zg/zr/zi; UCAC4/APASS mapping to verify) and optional finding chart.
- **ZTF18abtqnkv = Gaia DR3 2647761374214436352: retracted, not submitted.** Robust (95–5 pct) range 0.061–0.076 mag vs the recorded "0.8–0.9 mag ptp"; MAD 0.016–0.021. The raw range comes from 5 of 561 zr points; 2 of those 5 nights have normal same-night points (fails the criterion that a detection must reappear in same-night exposures). LS FAP 1.2e-2 (not significant); BLS = noise. Gaia RUWE 0.87. Not a proven variable. Reopen only if independent forced photometry (ATLAS/ASAS-SN) shows coherent variability.
- Cause: min–max amplitude is outlier-dominated (also inflated the state-cycler v1 list, difference-image mags). Method criterion: amplitudes are percentile ranges, not peak-to-peak.
- Journals created for both objects (2710029878791087616, 2647761374214436352) with ledger rows.

## 2026-09-18 (ninth) — Backlog of submittable candidates
- **VSX queue (AAVSO account):**
  - ZTF18abxnwmb: package and plots ready.
  - ZTF19abxfaon (170587115976392822): proven variable (846-epoch master record, ~5.4 mag range, 8 yr); draft corrected 2026-07-15; cone clean 2026-09-18. To do: regenerate the lost `lightcurve_master.png`; no Gaia source (quiescent below Gaia depth), so astrometric ID from LS DR10 (ls_id 10995383192785753) or PS1 per manual §III.a; type "CV:" with AGN caveat (VSX excludes quasars).
  - Gaia DR3 6315134987927550592 = 1eRASS J152614.8-111331: VSX 30″ and SIMBAD 10″ clean 2026-09-18. Variability established 2026-07-02: 709 ZTF epochs, zi chi2/dof 26.2, σ_excess 0.091 mag = 5× errors, 68 epochs >3σ, dip-dominated, interpreted as starspot rotational modulation; G=17.53, BP−RP=2.30, plx 8.28 mas ≈ 121 pc. Type BY:/VAR possible; amplitude ~0.10–0.13 mag, no coherent period (manual cautions on very low amplitudes). Ledger row added.
- **TNS queue (account pending):** 170635519425249637 (SN II candidate, AT draft, cone clean) and 170591519677875016 (AstroNote + Fink feedback).
- **MPC queue (SARC verification pending):** (330836) Orius and (88268) 2001 KK76 ADES drafts, unfiled since July.
- **Not submittable:** the Gaia dark-companion candidates (no registry accepts candidate dark companions; paper- or DR4-gated) and the 168 "uncatalogued" findings_register rows (triage-level, not characterised for variability).

## 2026-09-18 (tenth) — ZTF19abxfaon VSX draft; ZTF18abxnwmb ephemeris corrected
- **Correction (ZTF18abxnwmb):** each of the five "resolved eclipses" is one night of 3–5 exposures spanning ~12 min at one magnitude. No ingress or egress is sampled anywhere in the dataset; these are not measured minima, and "5 timings, rms 23 min" overstated the evidence.
- Refit (2-D (P, T0) grid maximising in-eclipse depth; 120-iteration night-resampled bootstrap): P = 3.727023 ± 0.000063 d (from phase coherence of 36 in-eclipse nights over 7.4 yr), Min I HJD = 2458257.856 ± 0.029 (±41 min), duration ≈ 8.9 h (0.10 phase). Classification unchanged (EA); draft corrected. Method criterion: an eclipse timing requires sampled ingress/egress.
- **ZTF19abxfaon draft** (VSX_SUBMISSION_ZTF19abxfaon.md + 13-yr light-curve figure). Position from LS DR10 ls_id 10995383192785753 (326.828336, −13.474691). No Gaia DR3 / 2MASS / UCAC4 / GSC 2.3 / PS1 DR1 / CatWISE counterpart (quiescence below their depths); primary name = ZTF survey ID per manual §V.a.
- Max 17.98 r (ZTF zr, 2021-01-04) / Min 23.44 r (DECam, 2013-08-07) ≈ 5.5 mag (cross-system caveat). No phase plot (required only for periodic variables); period null documented with injection–recovery limits.
- Two contaminants excluded: a single PS1 i=18.65 at 3.5″ and a single NEOWISE W1=16.2 at 1.4″, both probable asteroids (field at ecliptic latitude −0.12°).
- AGN question (VSX excludes quasars): ALeRCE stamp AGN 0.88, DECaLS DR9 z_phot≈0.93; but no mid-IR (CatWISE/AllWISE empty; LS forced W1=22.1), radio, UV or X-ray; a 5.5-mag turn-on after 4+ yr of stability is outside AGN behaviour; photo-z aliased by mixing pre/post-turn-on epochs; ALeRCE light-curve classifiers CV/Nova 0.95–0.97. **Verdict:** Galactic CV favoured; AGN not formally excluded without a spectrum. Disclosed in the draft, with VAR as fallback type.

## 2026-09-18 (eleventh) — Turn-on lane: prior-art gate qualified pass; pilot scoped (not run)
- Document: docs/reports/turnon_lane_gate_2026_09_18/GATE_AND_PILOT_SCOPE.md.
- **Gate result:** repo screen 0 matches for the method. Component-level prior art: Duffy+2024 (VY Scl states, ZTF+TESS); Bernhard+2025 arXiv:2502.00736 (new VY Scl from survey data); Szkody+2020/2021 annual ZTF CV catalogues; ML CV discovery in the ZTF alert stream (MNRAS 527,8633); ZTF SCP variable catalogues; VSX holds >15,300 CVs; NSC DR2 ships variability indices flagging ~23M variable objects. Deep archives for quiescence are standard practice. Not found published: deep-archive selection of turn-ons that never alert.
- Framing: supply-limited selection in a crowded field, not a novel method; front-filter against the published lists, not SIMBAD/VSX alone.
- **Pilot, gate zero = footprint check:** NSC/LS DECam coverage × ZTF coverage at |b| 5–20°; if usable overlap is <50 deg² the lane closes on footprint. Selection: pre-2018 point sources r>22 × ZTF DR r<20.5 on ≥2 nights, Δ>2.5 mag, bright state sustained >30 d (to separate from dwarf-nova outbursts). Pre-registered kills: footprint <50 deg²; >90% of candidates already catalogued; 0 verified survivors (then publish a density limit and close).
- Low |b|: the closed state-cycler null covered |b| 35–60° only (a plane-weighted population is compatible with it); CV density rises toward the plane.
- ZTF19abxfaon low states from ZTF DR (272 zr detections, 2018–2025). Season medians: 2020 18.91, 2021 18.73, 2022 20.61, 2023 19.31, 2024 19.01, 2025 21.12. The 2022 low state spans MJD 59732–59904 (≈172 d, 8 separate nights at 20.5–21.7); the 2025 one MJD 60834–60884 (≥50 d, 5 nights at 20.8–21.6). Sustained months-long low states, not single outliers, and not a return to the pre-2018 r≈23.2 quiescence. ZTF DR lists detections only, so low states may be deeper or longer (forced photometry would fill them in).

## 2026-09-18 (twelfth) — Turn-on lane gate zero passed (~24×); pilot field Galactic anticentre
- From nsc_dr2.exposure + live ZTF checks (numbers and exposure table in docs/reports/turnon_lane_gate_2026_09_18/, gate0_exposures.csv): |b| 5–20°, dec −30..+32, pre-2018, exptime≥60 s, griz gives 4,046 exposures, 3,023 with depth95>22 (2,931 DECam). Area covered: 1,458 deg² any griz, 1,190 deg² in r, against the <50 deg² kill threshold.
- r-band depth95 median 23.09 (58% deeper than 23.0), the regime in which ZTF19abxfaon's quiescence was measured at r = 23.05–23.44.
- ZTF side, verified live: 5 random deep-exposure centres in l=195–235 return 13–42 ZTF objects per 30″ cone, 16–73 epochs each, 7.1–7.6 yr baselines.
- **Pilot field:** Galactic anticentre l = 195–235° (1,163 deep exposures, median depth95 23.03, dec −22..+23.5, ~400–500 deg² deep). Inner-Galaxy blocks (l 0–20 / 340–360, 259+142 deg²) not used: southern, at ZTF's declination edge, heavily extincted and crowded.
- Remaining pre-registered kills unchanged: >90% of candidates already catalogued → close; 0 verified survivors → publish a density limit and close.

## 2026-09-18 (thirteenth) — Turn-on pilot build: feasibility and selection design
- No server-side join: Data Lab has NSC DR2 + ~60 crossmatch tables but no ZTF; IRSA has ztf_objects_dr20–24 (medianmag/minmag/maxmag/magrms/chisq/ngoodobsrel/refmag). Join is local; pilot is area-bounded, pulled per tile (IRSA TAP COUNT over 4 deg² exceeded 500 s).
- Sizing (2×2° anticentre box): NSC 284,874 objects → 107,789 at 22<r<24 → 66,304 stellar, i.e. ~16,500 faint stellar archival sources/deg²; a 25 deg² pilot ≈ 400 k rows.
- nsc_dr2.object provides per-band mags, mjd+deltamjd (for "all epochs pre-2018"), class_star, ndetr, and variability columns (rmsvar/madvar/chivar/etavar/nsigvar/variable10sig).
- Main false-positive mode: blending (ZTF ~2″ resolution vs NSC ~0.9″); a faint NSC source 1–2″ from a bright star mimics a turn-on. Required: faint source isolated (no NSC source brighter than r=21 within 3″) and ZTF centroid closer to the faint source than to any neighbour.
- **Design refinement:** objects that turned on before ZTF and stayed on look constant in ZTF and are missed by ZTF-internal variability searches (SNAD, ZTF SCP, Szkody catalogues, alert-stream ML). Selection requires low magrms as well as bright medianmag (the complement of the closed state-cycler lane, which required variability within ZTF).

## 2026-09-18 — ZTF18abxnwmb filed to VSX as 2MASS J22342534+0806596
- First registry submission from this project. Filed by the user via the VSX New Star Wizard (12 pages) in their AAVSO account. Provisional designation 2MASS J22342534+0806596; AUID to be issued on moderator approval.
- Submitted values: detached eclipsing binary, EA, P = 3.727023 ± 0.000063 d, Min I HJD 2458257.856 ± 0.029, max 12.712 r / Min I 12.928 r (Sloan), secondary 12.817 r, eclipse duration ~8.9 h, discoverer A. Keur. Supporting file: ZTF DR light curve + phase plot.
- **Pre-submission novelty check:** VSX (VizieR mirror + native API), SIMBAD, TNS, six published catalogues (Chen+2020 ZTF periodic variables, ZTF variable catalogue, both Gaia DR3 EB catalogues, ASAS-SN variables, GCVS): all clean within 10″. Absent from Chen+2020 despite G=12.7 and a clean period in the same ZTF data; eclipses are narrow (10% duty cycle) and shallow (0.2 mag) on a flat baseline (ZTF robust range 0.125 mag). Not covered: ADS/arXiv coordinate search; others' submissions pending moderation.
- **Correction before submission:** the review page showed catalogue names (page 4) and variability type (page 5) unsaved (PHP "Undefined index" notices, "None provided"); position, magnitudes, period, epoch and upload were saved. Both fields re-entered and verified before submitting.
- Next: ZTF19abxfaon, after its own prior-publication search.

## 2026-09-18 — Turn-on pilot running (anticentre, ~10 deg²); morphology criterion added
- **Pipeline:** NSC DR2 archival cuts (22<r<24, class_star>0.5, g−r<0.6, all epochs pre-2018 via mjd+deltamjd/2<58119, ndetr≥2) over 7 anticentre tiles give 4,403 candidates in 10.1 deg² (~436/deg²). Then a per-position ZTF light-curve query (12-way parallel, ~1.3 s each) tests for a bright state (5th-pct mag <20.5), amplitude >2.5 mag vs the archival magnitude, ≥2 bright nights and a bright span >30 d.
- IRSA's ZTF object tables are unusable for bulk work: sync TAP timed out on 0.09 deg² (240 s); an async job on 1 deg² was still executing after 20 min. The per-position `nph_light_curves` API (~1.3 s/position) is used instead; Data Lab (NSC) is fast.
- **Criterion revised at candidate 1:** the first hit (RA 117.75853 Dec +10.28674, NSC r=22.94 → ZTF zr=16.07, amp 6.87 mag) passed on "2 bright nights, span 370 d": two isolated bright epochs a year apart (WZ Sge-like pattern), not a sustained turn-on. Bright span does not separate sustained states from repeated outbursts.
- Added to vetting: duty cycle (fraction of observed nights within 1 mag of peak), longest unbroken bright run, and a class: SUSTAINED_TURNON (duty >0.5 AND run >100 d) / OUTBURST_LIKE_DN (duty <0.15 AND run <30 d) / AMBIGUOUS.
- Interim at 266 assessed: 220 NO_ZTF, 20 ZTF_SPARSE, 25 NO_TURNON, 1 CANDIDATE; NO_ZTF read as r~23 sources below ZTF's detection floor.
- Vetting on completion: isolation (no NSC source brighter than r=21 within 3″), novelty (VSX, Chen+2020, Gaia EB, ASAS-SN, GCVS, Milliquas, SIMBAD), Gaia counterpart, morphology test.

## 2026-09-18 — Turn-on pilot candidate 1: uncatalogued single-epoch outburst (ATLAS check pending)
- Decision (user): dwarf novae are kept as output alongside sustained turn-ons (VSX type UG).
- **Candidate: RA 117.75853 Dec +10.28674** (pilot tile 118.3/10.4). NSC DR2 id 80807_1921: g=23.50, r=22.94, class_star 0.68, ndetr=4/ndetg=2, epochs spanning 1040 d centred on MJD 57120 (2013–2016), rrms 0.055, variable10sig=0 (stable, faint). No Gaia DR3 source within 3″.
- ZTF: 6 detections, one at zr = 16.07 ± 0.01 on 2018-11-10 (MJD 58432.507), five at 20.3–21.5 in 2019–2024, all ZTF oid 516208300035735 within 1.2″ of the archival position. Implied amplitude 22.94 → 16.07 = 6.87 mag.
- Asteroid test (ecliptic latitude −10.5°): SkyBoT (positive-controlled on an on-ecliptic field) nearest known minor planet 149″ away at V=22.4. Detection error 0.01 mag.
- Novelty: clean in 8 catalogues (VSX, Chen+2020, ASAS-SN, GCVS, Ritter–Kolb, Szkody ZTF CV yr1+yr2, Milliquas).
- **Open:** the outburst rests on a single epoch; needs independent corroboration. ATLAS forced photometry submitted (task 5006731, MJD 58000–61000); ATLAS (~2 d cadence) would detect a 16th-mag outburst. If confirmed: amplitude ~6.9 mag, faint blue quiescent counterpart (g−r≈0.56 at r≈23) and rare outbursts indicate a WZ Sge-type dwarf-nova candidate.

## 2026-09-18 — Turn-on pilot closed: all 13 candidates are artifacts; ~25% of the footprint queried
*(supersedes the candidate 1 entry above)*
- **Candidate 1 refuted.** ATLAS task 5006731 returned 4,037 epochs (MJD 58021–61000; 4,023 pass chi/N<4). Same night, 3.5 h after the ZTF exposure (MJD 58432.6539), ATLAS measured 36 ± 24 µJy = 1.5σ; mag 16.07 = 1,359 µJy would be 57σ. The only ≥5σ single epoch in 8 yr (MJD 58152, 10.3σ, mag 17.87) stacks to mag 20.07 / 4.1σ over its 8 exposures (1 high, 7 at baseline): a second single-exposure artifact.
- ZTF metadata: the 16.07 epoch is the only one of six with catflags≠0, chi=5.20 (others 0.28–0.99) and sharp=+0.378 (others −0.41…+0.04). Cosmic ray / hot pixel, not a WZ Sge candidate.
- **All 13 candidates fail:** 9 blends, 3 sub-threshold noise, 1 cosmic ray. Analysis: `docs/reports/turnon_lane_gate_2026_09_18/PILOT_RESULTS.md`.
- **v1 vetting defect:** all four checks returned identical values on all 13 objects. Empty (rate-limited) responses were scored as findings: `hits["SIMBAD"] = 0 if (...) else 1` scored a failed query as "already catalogued" (uncatalogued=false on all 13). Fix: queries retry and return an explicit error value.
- **Per-epoch astrometry as blend test:** ZTF gives a centroid per detection; 9/13 have the bright-state centroid 2.2–3.2″ off target, on a brighter NSC neighbour. Example: two NSC sources 2.87″ apart (r=22.88 target, r=19.53 neighbour); ZTF centroid 0.65″ from the neighbour, where Gaia has G=19.47, ϖ=1.41 mas. Every duty_cycle≈1.0 object is a blend (a constant star seen through a coarser PSF).
- **Frame limits:** for 3 candidates every detection is fainter than its frame's 5σ `limitmag`; amplitude came from night-to-night depth variation ("bright" 19.42 epoch on the shallowest frame, limitmag 18.93; faint epochs from frames reaching 22.2).
- **Coverage correction:** `ztf_at()` used `curl -s` without retry; a transport failure returned empty stdout without raising and was recorded as `NO_ZTF`. Zero ZTF_ERROR across 4,403 threaded queries. Re-query of 60 random NO_ZTF positions with retries: 20/60 (33.3%) have data, 0 hard errors. By completion order, hit rate 15–23% for the first ~1,100 queries, 0.0% for the remaining ~3,300 (IRSA stopped serving the 12-thread client). Effective coverage ~2.5 deg², not 10.1.
- All 13 candidates falling in one tile reflects processing order (that tile ran before the cutoff). The throttled archive returned empty HTTP 200 responses, not errors.
- **Structural result:** "faint in a deep sharp survey, bright in a shallow coarse one" is satisfied by blending, sub-threshold noise and cosmic rays, all scaling with the depth gap. Only per-epoch astrometry, not photometry, separates a sustained turn-on from a blend.
- **Re-run started 14:41 UTC** (`turnon_pilot2.py`): eight artifact filters in-pipeline (centroid <1″, mag ≥0.3 above frame limitmag, catflags=0, |sharp|<0.3, chi<2, ≥2 bright nights, duty<0.9, amp>2.5), throttled to ~2.2 req/s with adaptive backoff and explicit ZTF_ERROR, covering all 4,403 positions.
- **Self-recovery test (validates the filters, not the selection):** targets = the 3 catalogued dwarf novae inside the pilot tiles. 2/3 recovered (CSS 140121:075258-000709 offset 0.06″ amp 3.00 duty 0.58; ASASSN-15tr offset 0.03″ amp 3.45 duty 0.17). The third (SDSS J075117.00+100016.2) is rejected as CONSTANT (ZTF era r≈18.0, duty 1.00, amp 0.45; not a turn-on on this baseline). The `mag ≤ limitmag − 0.3` cut keeps real modest-amplitude events: CSS 140121 lost 58% of epochs to quality filters and still passed.
- **Limitation:** selection not validated end-to-end: the templates have NSC r = 18.4–20.8, outside the 22–24 window; no known object of the target class exists at the target faintness in this footprint.
- **Faint-end sensitivity** (963 in-field zr frames; median limitmag 20.50, 10th pct 19.89, 90th pct 21.30). Fraction of usable frames vs turn-on brightness: r=18.0 → 100%, r=19.0 → 98%, r=19.5 → 91%, r=20.0 → 71%, r=20.3 → 45%, r=20.5 → 34%, r=21.0 → 10%. Near-full sensitivity only for turn-ons reaching r ≲ 19.5 (amp ≳ 3.5 from r=23); ~34% per-frame efficiency at the nominal amp>2.5; none below r≈21. Density limits are quoted against this curve, not the raw position count.
- **Correction (recovery test):** its first pass reported 2/3 as BLEND, both test artifacts: VSX positions are 1.25–1.35″ off here (NSC and Gaia agree to 0.03″), and an empty re-resolution query left a wrong hard-coded anchor in place. Method criterion: astrometric tests are anchored on NSC/Gaia positions, not variable-star catalogue coordinates.

## 2026-09-19 — Correction to the 2026-07-15 period-search entry (ZTF19abxfaon)
The 2026-07-15 entry stands as written; this entry supersedes its final inference.
- **Withdrawn:** the clause "consistent with low-inclination CV". The injection-recovery result (semi-amplitude ≥5 µJy ≈ 0.06 mag recovered 20/20 at P = 1.5–4 h) constrains the searched amplitude/period space, not the geometry. Corrected: no eclipses were detected under that sampling and those search assumptions; moderate inclinations can be non-eclipsing, narrow or shallow eclipses can be missed, and an aperiodic light curve does not imply the absence of an orbital period.
- **Also withdrawn:** the 20/20 recovery as a completeness proof. It applies to the 20 injected sinusoids at those periods and phases (95% binomial lower bound 0.83), not across waveform, alias or eclipse duty cycle.
- The same wording was in `consumer_package/astronote_draft.md`, `consumer_package/vsx_draft.md`, `PERIOD_SEARCH_2026_07_15.md` and the current VSX draft (earlier corrections had been applied to the submission file only). All four are corrected; the journal's Current-class field is updated.

## 2026-09-19 — EB lane opened: shallow, short-duty-cycle eclipsing binaries missed by scatter-based selection
- **Prior art** (`scripts/litcheck/prior_art.py` failed with HTTP 406; web search used instead): a ZTF eclipsing-binary catalogue of 575,526 systems (input to a double-EB BLS search, A&A 2024, doi:10.1051/0004-6361/202348451); ZTF Source Classification Project periodicity and variability metrics (MNRAS 505, 2954); several published systematic BLS searches on ZTF light curves.
- **Gap addressed:** ZTF18abxnwmb (filed to VSX on 2026-09-18 as 2MASS J22342534+0806596) was uncatalogued at r = 12.7 with 2,564 ZTF epochs. Duty cycle 5.7% and depth 0.216 mag give an RMS contribution of ~0.05 mag, within ordinary scatter at that brightness, so scatter-based preselection (Gaia variability flag, most ZTF variable catalogues) does not select it; a direct BLS does.
- **Scope:** method validation with a narrow novelty gap. Front-filter: live VSX plus the 11-catalogue check (VSX ingests the published ZTF EB catalogues).
- **Selection:** Gaia DR3 sources with `phot_variable_flag != 'VARIABLE'`, G ≈ 13–17 (ZTF precision 0.01–0.03 mag, so a 0.15 mag eclipse is a >5σ event), in the ZTF footprint; BLS with no RMS pre-cut.
- **Acceptance:** ≥3 distinct eclipse events on separate nights; a period fitted on early data must predict events in held-out later data; every in-eclipse epoch is checked against its frame `limitmag`, `catflags`, `sharp` and `chi`; contiguity is required before any duration is quoted.
- **Harness:** retries with explicit error status, randomised order, checkpointing, throttling to ~2 req/s.
- **First calibration object (negative):** Gaia DR3 2729280192794112256 (337.156778 +10.322418, G=16.44), highest BLS SNR of the opening batch: snr 35.2, P=1.4958 d, duty 0.060, 90 in-eclipse epochs across 35 nights, 1,960 clean zr epochs; clean in SIMBAD, VSX, Chen+2020, the Gaia DR3 EB table and GCVS. Not an eclipsing binary: the deep phase bins scatter (+0.27, +0.25, −0.09, −0.41, −0.39), and the first-half period is 0.3324 d against 1.4958 d for the full set (78% mismatch). MAD scatter 0.0451 against median photometric error 0.0133 (3.4x excess variance). Uncatalogued aperiodic variable.
- **Acceptance criterion added:** held-out period match |P_half − P_full|/P < 2%; SNR, depth and the number of in-eclipse nights are not sufficient on their own.
- **Two pipeline bugs found by the self-recovery test:**
  1. **Sign bug:** `BoxLeastSquares` was given magnitudes and so searched for brightenings (569 objects affected). Found on Gaia DR3 2710186593557691136, whose "in-eclipse" epochs were 0.26–0.30 mag brighter than baseline (13.87 vs 14.148, clean frames 4.5 mag above the limit). Fix: relative flux. On the filed EB, flux gives snr 70.4 against 21.1 for magnitudes.
  2. **Harmonic bug:** on ZTF18abxnwmb the pipeline returned 11.181729 d, 3× the known 3.727023 d. A first fix (shortest sub-harmonic above a power threshold) over-divided to n=5. Adopted rule: the true period has the maximum SNR across harmonics (n=3 snr 90.1; n=1 71.9, n=2 71.4, n=4 59.9, n=5 50.2). n=6 (half-period, 1.8635 d) scores 88.7; the half-period ambiguity is resolved by testing for unequal alternating depths (0.216 vs 0.105 mag for ZTF18abxnwmb).
- **Self-recovery passes:** P = 3.727019 d against the known 3.727023 d (error 0.0001%). Method criterion: the template must be recovered before any absence claim. Test script: `docs/reports/eb_lane_2026_09_19/selftest.py`.
- **Added:** day-alias rejection (0.5/0.9973/1.0/1.0027/2.0 d; the opening batch gave several P = 0.99997 d hits with 139 "in-eclipse" epochs, the ZTF cadence alias) and an in-eclipse floor `n_inecl >= max(4, 0.5*N*duty)` replacing a flat floor of 8, which rejected short-duty-cycle signals.
- **Third gap (hold-out tests periodicity, not morphology):** Gaia DR3 2723173268990926336 (337.179826 +9.555768, G=15.68) passed every gate (P=0.799978 d, depth 0.0535, duty 0.1125, snr 61.4, 148 eclipse nights, hold-out pass) but is not a detached EB: folded at 2P = 1.599956 d it is a smooth double-humped wave (maxima +0.063/+0.054, minima −0.034/−0.042) with 42% of phase bins deviating (contact binary or ellipsoidal variable). MAD scatter 0.066 exceeded the fitted depth 0.0535, and duty 0.1125 = 0.09 d sat at the maximum duration-grid value.
- **Fix (shape gate):** reject when the fraction of phase bins deviating by >30% of the folded range exceeds max(0.25, 3×duty). ZTF18abxnwmb scores 0.083 against the 0.25 threshold and passes; the contact binary scores 0.42.
- **Correction:** day fractions (0.8, 0.4, 2/3, 1/3, 1/4 d) added to the alias list were removed again, because these periods contain real short-period binaries; the shape gate handles short-period continuous variables.
- **Bycatch (uncatalogued):** Gaia DR3 2723173268990926336, clean in SIMBAD (10″), VSX and Chen+2020. P ≈ 1.599956 d (double-humped; 0.799978 d single-wave), range 0.104 mag, G = 15.676, BP−RP = 1.088, parallax 0.343 ± 0.054 mas (6.3σ), RUWE 1.016. Most consistent with a contact or ellipsoidal binary; M_G ≈ +3.4 at the nominal parallax favours a subgiant-scale system over a K-dwarf rotator (distance loosely constrained). Possible VSX filing as EW/ELL; not pursued (outside the target class).
- **Fourth and fifth gaps (grid-dependent period determination); hunt stopped after a failed template test.** Second candidate Gaia DR3 2709150853604276224 (337.653173 +6.034736, G=15.23, depth 0.49 mag, duty 0.0195, snr 175) is known in VSX as AISV-BD J337.653+6.035 (OID 10848462, type EA, 0.36″) with P = 9.216540 d; the hunt reported 4.608193 d, exactly half.
  - Gap 4: `refine_period` divided the raw BLS peak but never multiplied it. On the hunt's 7,000-point grid ZTF18abxnwmb returned 1.863510 d against 3.727023 d (50% error). The run was stopped and 4,968 assessed rows quarantined.
  - Gap 5: with scanning in both directions, a 5,000-point grid still failed (raw peak 2.5448 d, no integer relation to 3.727023 d). Fix: seed from the top-5 distinct periodogram peaks.
- **Validation:** ZTF18abxnwmb (P=3.727023 d) recovers on grids of 5,000 / 7,000 / 9,000 / 12,000 points at 0.0001–0.0006% error. AISV-BD J337.653+6.035 (VSX EA, P=9.216540 d) recovers at 0.003%, correctly doubled, with eclipse depths differing at 7.8σ (0.343 vs 0.403); an earlier measurement gave 1.7σ because of a poor epoch and duration. The novelty front-filter identified it as known.
- **Method criterion:** template tests use the pipeline's production configuration (grid resolution, thread count, tuned constants). The template passed at 12,000 grid points and failed at 7,000, the grid the hunt used.

## 2026-09-20 — EB hunt: hold-out gate rejected the filed template; fixed and re-queued

At 11,938 of 20,007 objects the hunt had returned 0 CANDIDATE and 264 WEAK. The WEAK set included Gaia DR3 2709919102994455168 at P=0.842 d, depth 0.32 mag, 58 distinct eclipse nights, SNR 205.

**Diagnosis.** 229 of 264 (87%) failed on the period clause alone, 38 of them at harmonic ratios (×2, /3, /4, /8…). The hold-out compared the raw periodogram argmax of a first-half BLS fit with the harmonically refined `P` of the main path.

**Test on ZTF18abxnwmb** (2MASS J22342534+0806596, P=3.727023 d, accepted by VSX):

    OLD hold-out raw argmax on half 1 : P1 = 1.863422 d
    full-fit refined period           : P  = 3.727043 d
    ratio                             : 0.5000
    |P1-P|/P = 0.5000, gate required < 0.02  ->  WEAK

The gate rejected the catalogued template at the half-period.

**Fix.** The half-baseline fit runs the same pipeline as the full fit (`top_peaks` + `refine_period`), and the period clause accepts low-order harmonics (×1,2,3,4 and /2,3,4). Unchanged criteria: ≥3 in-eclipse epochs at the predicted phase, at >0.5× the full-fit depth, in data not used to find the signal. After the fix the template returns CANDIDATE, hold-out ratio 0.9999, period correct to 0.0005%.

395 objects (264 WEAK + 6 ZTF_ERROR + 125 NO_ZTF) re-queued; 11,543 pre-hold-out verdicts (NO_ECLIPSE / CONTINUOUS_MODULATION / SPARSE / DAY_ALIAS) retained, as they are decided before the hold-out runs. Run resumed with 8,464 remaining.

The template test had been run only against the main path; the hold-out was added afterwards. Earlier defects in this lane with the same effect: a duty>0.9 veto, the BLS sign inversion and grid-dependent period seeding. Method criterion: template tests assert on the final verdict string, end to end.

## 2026-09-20 — EB lane: an uncatalogued EA and two catalogued recoveries

The corrected gate was run on the five highest-SNR objects previously rated WEAK. Three became CANDIDATE; two are catalogued recoveries:

- **CSS J223442.2+072335** (VSX EA, P = 1.684270 d): recovered at 0.842152 d = P/2 (equal-minima fold).
- **AISV-BD J337.653+6.035** (VSX EA, P = 9.216540 d): recovered at 9.216247 d (0.003%).

The third is in no variable-star catalogue.

### Gaia DR3 2716884161263924224 = ZTF J223451.69+090546.4 (22 34 51.69 +09 05 46.4)

Detached eclipsing binary, P = 1.9846349 d, T0 = HJD 2458258.63656, zr 16.318 → 17.004 (0.686 ± 0.013 mag), zg 16.816 → 17.515 (0.699 ± 0.015), T14 = 4.3 h = 9.1% duty, V-shaped (T23 ≈ 0, partial), out-of-eclipse flat at 0.020 mag rms. 701 clean zr + 594 clean zg epochs over 2695 d; 49 distinct eclipse nights. Gaia: G = 16.375, BP−RP = 0.916, parallax 0.336 ± 0.057 mas, RUWE 0.91; nearest neighbour 18.03″ at G = 20.7, so unblended.

**Novelty checks (coverage verified for each null):** absent from VSX, SIMBAD, Gaia DR3 variability (37 classified variables in the same 30′), Chen+2020 ZTF periodic variables (4 in 30′) and ASAS-SN (4 in 30′, including one at V = 17.16, fainter than this target). Gaia DR3 lists the source with `phot_variable_flag = NOT_AVAILABLE`.

**ATLAS:** Heinze+2018 lists it at 0.02″ as `ATO J338.7153+09.0962` with `fp-period = 1.984637 d` (agrees with this period to 2×10⁻⁶ d), class `dubious`, P(dubious) = 0.813, all four eclipsing-binary class probabilities 0.000. ATLAS measured the period but assigned no type (a Fourier series does not represent a 9%-duty box eclipse).

**Period ambiguity.** Folded at 2P, the minima at phase 0.0 and 0.5 are equal within 0.08 mag (3σ); zr and zg differ in sign (−0.036 ± 0.027 vs +0.002 ± 0.032). The orbital period is 1.9846349 d or twice that (two near-identical eclipses, more natural for a detached pair of similar stars). The shorter period is adopted; the ambiguity is stated in the VSX remarks.

**Method notes:** the BLS duration grid stops at 0.09 d while the eclipse is 0.159 d, so duty is under-reported. Period and epoch are fitted in the HJD frame; a median HJD−MJD offset is wrong by up to ±8 min across a year, over an ephemeris spanning 1358 cycles.

**False null:** VizieR `II/366/catalog` and `II/366/table` return zero rows at any position, target and control alike; only `II/366` returns data. Found by the control-field density test.

Package: `docs/reports/eb_lane_2026_09_20/VSX_SUBMISSION_2716884161263924224.md`. Journal: `docs/object_journals/2716884161263924224.md`. Prepared, not filed (filing by the user). The VSX native-API duplicate check returns a Cloudflare interstitial and is to be re-run in the wizard at filing.

### Addendum (same day) — effect of the truncated BLS duration grid

The BLS duration grid `[0.012, 0.025, 0.05, 0.09]` d tops out at 2.2 h; 2,746 of 11,938 records (23%) are at that limit. `duty` feeds the detection floor (`0.005 ≤ duty ≤ 0.15`) and the shape gate (`frac_dev > max(0.25, 3·duty)`).

- Short-period end (0.2–1 d): 1,213 records at the limit; duty is inflated above the 0.15 ceiling, which rejects contact binaries and rotators as intended.
- Long-period end: 118 records in the 15–20 d bin were rejected with duty under the 0.005 floor. Of those, 36 would have passed every other cut (depth ≥ 0.045, snr ≥ 10, ≥3 eclipse nights).
- Those 36 have snr 10–16, 3–5 eclipse nights, depth 0.05–0.11 mag and periods of 18–55 d, outside the 0.2–20 d search grid (reached only as harmonic multiples from `refine_period`): noise fits at long trial periods.

**Decision: no restart.** The limit distorts reported duration and duty for long eclipses (the new EA is fitted at 0.09 d against T14 = 0.159 d) but removes no detections inside the search range. Method criterion: pipeline duty and duration are screening quantities; a candidate's duration is re-derived from the epochs with a trapezoid fit before it is quoted (4.34 ± 0.07 h for 2716884161263924224).

## 2026-09-20 — ADS literature search; follow-up of the ATLAS "dubious" class

The earlier prior-art check could not reach ADS (no token; 401 unauthenticated, JS-only UI). It was run with an ADS API token supplied by the user.

### Part 1 — the object: zero hits for twelve designations

`ATO J338.7153+09.0962`, `ZTF18accrxjd`, `2MASS J22345167+0905464`, `J223451.69+090546.4`, `J223451.68+090546.4`, `2716884161263924224`, `394_000547_zg_c04_q1` (Arevalo+2026 internal OID), `TIC 415929979`, `PSO J338.7154+09.0962`, `SDSS J223451.68+090546.4`, `DESI J338.7153+09.0962`, `ATO J338.7153`: 0 full-text hits for each.

The VSX package claims the first published ephemeris and eclipse solution. Arevalo+2026 lists the star only in a machine-readable table, which full-text search does not reach.

Verified at source: Arevalo+2026 = 2026A&A...705A.247A (cited 5×), "Unlocking AGN variability with custom ZTF photometry…", an AGN-selection paper. Its EA label is an unvetted output of the AGN classifier; no study of the star as a binary was found. Heinze+2018 = 2018AJ....156..241H (cited 390×).

### ADS query construction

Full-text search `full:"dubious"` returned unrelated papers (matrix exponentials, dolphin populations, foundation models), and `abs:"classif"` returned 0 of 390 citers, a tokenisation artifact. These queries were replaced by the bounded query below.

### Part 2 — no systematic follow-up of the ATLAS "dubious" class found

Bounded test: every paper citing Heinze+2018 that contains "dubious" (70 papers), titles checked individually. None mines or reclassifies the dubious class: they are Gaia DR3 cross-match/classification papers, ASAS-SN/OGLE/NGTS/ZTF catalogues, single-object studies (CzeV502, THOR 42, Romanov V48, U Sco), ML/methods papers and unrelated fields.

Follow-up work on the ATLAS variable catalogue:

| paper | scope |
|---|---|
| Bernhard+2021 (2021MNRAS.506.4561B) | magnetic chemically peculiar stars only (class-targeted) |
| Toth+2021 (2021OEJV..214....1T) | "Confirmation of seven faint ATLAS variable star candidates" |
| Khruslov+2019 (2019MNRAS.490.1283K) | "three short period ATLAS variable stars" |
| Toth+2021 (2021JAVSO..49...12T) | "Three faint variable stars… and eleven others" |

Within 1°, 12/12 non-dubious ATLAS entries appear in the Gavras+2023 Gaia known-variable compilation, against 4/32 dubious entries. ZTF J223451.69+090546.4 is an ATLAS "dubious" entry with a correct period, found independently in this lane.

### Other ZTF eclipsing-binary publications, 2023–2026

The ZTF eclipsing-binary papers found are specialised: ELM Survey South (low-mass WD binaries), a 13.7-minute accreting binary, doubly-eclipsing quadruples, post-common-envelope WD+MS, and accretion-disk EBs from LAMOST+ZTF. No systematic new-EB sweep of ZTF DR was found. A related candidate-list publication: 2022RNAAS...6...96H, "370 New Eclipsing Binary Candidates from TESS Sectors 1-26" (18 citations).

**Decision:** reconsider the EB hunt target list against the ATLAS dubious catalogue directly (objects with a measured period and no classification), not only the Gaia-selected sample.

## 2026-09-22 — Literature re-check of open candidates

Method: all-table VizieR cone (6″) and ADS full text on every designation.

| object | result |
|---|---|
| UCAC4 313-025977 (5612039087715504640) | Bailer-Jones & Kreidberg 2026 (A&A 708, A249) table 1: M₂ = 0.0104 M☉ (10.9 M_J), P = 592.32 d. Shahaf+2023 table 1: AMRF class I. ESMORGA (Pérez-Couto+2024): two-M-dwarf model. |
| UCAC4 499-043649 (3155543945892767232) | Müller-Horn+2026 (A&A 709, A62): companion 2.1 (+2.1/−1.1) M☉, P ≈ 908 d. LAMOST RV variable (Qian+2019; Tian+2020). |
| 3161546596480983040 (Object B) | Schwope+2026 (arXiv:2607.28066), entry 45: CV, "MCV or DN"; no period reported. eRASS:3 counterpart: this source. |
| WDJ060042.75-293041.36, WDJ020915.51+380425.92 | WD catalogues only; no binary publication found; ADS 0 hits. |
| TYC 3477-27-1 (1593152388271709824) | Green+2023 table 2 (score 0.83, P = 0.678 d); Kostov+2025 table 2. |
| 5858574810404752256 | No publication found. |

The 2026-05-30 ledger rows for UCAC4 313 (not in Bailer-Jones & Kreidberg 2026, not in Shahaf+2023) are superseded by the rows of 2026-09-22.

## 2026-09-22 — EB hunt: re-runs complete

- 96 ZTF_ERROR targets re-queried: 0 candidates.
- 212 NO_ZTF targets re-run with a 3″ cone and a 2″ per-epoch filter: 29 with data (8 NO_ECLIPSE, 15 SPARSE, 4 DAY_ALIAS, 2 WEAK), 0 candidates; 183 without ZTF light curves.
- Totals: 20,007 targets → 6 CANDIDATE (2 known EBs, 1 listed by Arévalo+2026, 3 without a classification in the checked catalogues), 420 WEAK, 183 without ZTF data.

## 2026-09-22 — Loose-end checks

| item | result |
|---|---|
| TYC 3477-27-1 | 0.6776-d periodic signal (0.8% semi-amplitude) in 5 TESS sectors, 2019–2024, centred on the star. |
| (88268) 2001 KK76, 2010 WFC3 | Search around the July-orbit prediction: no detection (superseded; see the KK76 entry below). |
| J075308.47+003535.6 | NED: WISEA J075308.45+003535.7 only; no redshift or classification. |
| MGAB-V774 | Outburst detection (r = 18.48, MJD 58291) is in a programid-3 exposure; public ZTF alerts are programid 1. |
| Rubin public alerts | Newest alerts in Fink at MJD 61235 (2026-07-14/15). |
| 2001 KN76 | SBDB arc ends 2008-04-13 (unchanged). |

Pilot started: Arévalo+2026 reservoir (1,281 stars: predClass nonvar-star, Pvar ≥ 0.99, Std ≥ 0.04) and 1,127 controls (Pvar < 0.5), same EB pipeline with a 3″ cone.

## 2026-09-22 — (88268) 2001 KK76: HST positions re-measured against Gaia DR3

- 12 public HST frames: 4 × ACS/HRC 2006-05-02 (GO-10514); 8 × WFC3 2010-03-13 (GO-11644).
- Positions tied to Gaia DR3 stars in each frame (proper motions to the epoch). The 2006 positions differ from the July package by 1.10–1.19″. KK76 is present in all 8 frames of 2010.
- Two independent measurements agree to 0.008–0.021″.
- find_orb: ground + 2006 predicts the 2010 positions within 0.43″; all 53 observations fit with HST residuals ≤ 0.031″. Predicted 2026-09-22 position: 41″ from the July orbit, 58″ from the JPL orbit; two fitting codes agree to 1.7″ (2026) and 2.0″ (2040).
- Revised ADES draft (12 rows): `precovery_campaign_2026_07_07/kk76_gaia_fix_2026_09_22/`. Not submitted.

## 2026-09-22 — (330836) Orius not detected in 2019 DECam frames

- Six 180-s i-band frames of 2019-05-16 cover the predicted position on six different CCDs. Motion-aligned stack: -0.6 sigma at the position; 5-sigma limit i > 24.70. Predicted V = 22.45 (JPL, H = 9.73), i ~ 21.6-22.2.
- Controls from the same frames: 2016 WZ80 (V = 22.9) detected at 5.7 sigma, 1.1" from its predicted position; 2008 GV40 (V = 20.9) at 13.4 sigma.
- Position checks: JPL 3-sigma 6.45" x 0.61"; our combined fit within 0.97" of JPL; stamps +/-20"; nearest source static to 0.02" over 17 minutes (a star, not in Gaia).
- No DECam frames >= 60 s cover the path between 2015-06 and 2019-05; 2021-2023 frames are being measured.
- Orius filing on hold; 2021-2023 epochs pending. KK76 unaffected.
- Work continues in a separate project (sso-recovery-2026-09-22).

## 2026-09-22 — Arévalo+2026 `nonvar-star` reservoir: EB pilot result

Samples: 1,281 stars drawn from the 274,249 with `predClass = nonvar-star`, `Pvar >= 0.99`, `Std >= 0.04`
(14.5-19.5 mag, >= 80 epochs), and a control of 1,127 drawn from the 8,576,864 with `Pvar < 0.5`. Same EB
pipeline as the 20,007-star hunt; both templates recovered before the run.

- Reservoir: 8 CANDIDATE (0.62%), 54 WEAK. Control: 0 CANDIDATE, 21 WEAK.
- Of the 8: 6 eclipsing binaries, 1 broad continuous modulation (not pursued), 1 rejected (signal from
  dense single-night sequences).
- 3 of the 6 are in VSX and the Gaia DR3 EB table. For all three the catalogued period (Gaia DR3) does not
  phase the ZTF light curve; the ZTF period does.
- 3 have no type or period in the checked catalogues (absence with coverage proved in VSX, Chen+2020,
  ATLAS, Gaia DR3 vclassre/veb and Gavras+2023; SIMBAD none; ADS 0 hits): Gaia DR3 3828306424841718656
  (P = 3.482506 d or 6.965012 d; M-dwarf primary, 269 pc), 1738942132557316864 (P = 1.076989 d),
  2709405317531811840 (P = 6.381715 d; DESI K star, RV −178 km/s, one epoch). Journals created.

Report: `docs/reports/arevalo_reservoir_pilot_2026_09_22/REPORT.md`.

## 2026-09-22 — Orius 2019 result withdrawn; Orius, KK76 and KN76 moved to sso-recovery

The entry "(330836) Orius: measured in 2019 DECam frames, not detected; filing on hold" (commit 4fc631a) is withdrawn: its limit i > 24.70 came from an analytic noise estimate that is 1.4-3x optimistic on resampled stamps. Re-derived in the separate project sso-recovery-2026-09-22, the 2019 frames contain candidate signals at the predicted position (i ~ 22.7, g ~ 23.35), and 3 of 4 of this campaign's 2013-2015 nights re-measure within 0.37" of JPL. All of it is unconfirmed (internal tests only). Decision (user): Orius, (88268) 2001 KK76 and 2001 KN76 are handled in that project from today; the KK76 filing package stays in `kk76_gaia_fix_2026_09_22/`. Journals here carry pointer entries.

## 2026-09-22 — Compact-object candidates and the unreviewed pools

**Candidates.**
- TYC 3477-27-1 (1593152388271709824): the 0.678-d eclipsing pair (two K dwarfs; R₁+R₂ ≥ 1.3 R⊙, ~2-3% of the light each) accounts for the 1.27 M⊙ dark companion. The light-travel-time amplitude this predicts from the Gaia orbit (390-560 s) is consistent with the TESS timings once spot-driven timing noise (~100 s) is allowed for; the timings do not discriminate. Triple interpretation favoured.
- WDJ060042 and WDJ020915: no radio, pulsar, gamma-ray or X-ray counterpart in any catalogue with coverage (NVSS, VLASS, RACS-low, TGSS, GLEAM, LoTSS-DR2, ATNF, 4FGL-DR4, 2RXS, eRASS1, 2SXPS). At 84-98 pc this excludes a pulsar companion beamed toward us. VizieR `J/ApJS/260/53` returned 0 rows within 5 deg of both (false null); `IX/72` (4FGL-DR4) was used instead.
- Tier-1 NS pool: the 2026-05-28 archival-RV triage, re-run unchanged, reproduces 117/40/2/2 and recovers the eight per-source verdicts that had been lost (all NO_ARCHIVAL_RV). Shahaf+2024 (arXiv:2309.15143) table I contains 9 of the pool; 8 have a red-colour-excess probability ≥ 70%. The Tier-1 BH 6281177228434199296 is at 99.99%.

**Previously closed objects re-opened.**
- 1eRASS J152614.8-111331 (6315134987927550592), closed on 2026-07-02 as an active M dwarf without a period: coherent P = 2.2511 h in ZTF g and r (the 2.4848 h alias is the only competitor); M_G 12.12 at BP-RP 2.30; g-r 0.25-0.46 with r-i 1.3-1.5 in SkyMapper and PS1; eRASS:3 L_X ≈ 1e29 erg/s. Not in Schwope+2026 or Rodriguez+2025. Candidate white dwarf + M dwarf binary; needs a spectrum.
- DESI Phase 2B: 3831414946076844032 is a detached EB (P = 1.52799 d, 0.2 mag), metal-poor ([Fe/H] -1.0 to -1.8), not in VSX. 4416914787767626240 was in the verdict file but never registered; 1126496666779064064 was registered under its Gaia DR2 id (DR3: 1126496671074947200).

**Pools.**
- eRASS1-Gaia v2 uncatalogued X-ray counterparts: 42 of 137 have ZTF data. A fine-grid period screen (replacing a first pass whose coarse grid and strict alias criterion failed on the known positive) finds two coherent short periods: 6315134987927550592 (above) and 3021820276571880064, which is already in VSX as BLVS J061325.64-030239.2 (AM:, P = 0.160912 d; recovered at 0.1609121 d). The lane's 'uncatalogued' label for it was wrong. 95 of the 137 have no ZTF coverage.
- XP-outlier pilot, 578 never novelty-checked: 526 in SIMBAD (451 hot subdwarfs, 51 white dwarfs, 11 PNe); of the remaining 52, 51 are in Culpan+2022, Gentile Fusillo+2021, VSX or Gaia DR3 variability tables. One left (4662317674220795776, towards the LMC).
- EB-hunt and pilot WEAK class (495): other-band re-vet running; all 8 templates pass.
- DESI Phase 2B no-period binaries (23): period re-search on current ZTF data running.

Reports: `docs/reports/ns_pool_triage_rerun_2026_09_22/`, `docs/reports/erass1_j1526_2026_09_22/`.

## 2026-09-23 — Track 1 opened: X-ray-selected white dwarf + M dwarf binaries (eRASS:3 × Gaia)

**Prior art** (ADS; `scripts/litcheck/prior_art.py` did not run, arXiv HTTP 406): eRASS1 × Gaia accretor / CV searches are
published — Rodriguez+2025 (ApJ 991, 125), Wang+2025 (A&A 698, A321), Schwope+2024 (A&A 690, A243; 686, A110), Schwope+2026
(arXiv:2607.28066), Muñoz-Giraldo+2024, SDSS-V DR20 eROSITA CVs (arXiv:2607.27960); pre-polar polarimetry (arXiv:2608.25439);
a period-bouncer study (arXiv:2607.27855). Scope: eRASS:3 (deeper than eRASS1), systematic periodicity, southern coverage from
ATLAS.

**Selection and screen** (`docs/reports/track1_wd_binaries_2026_09_23/`): 108,404 nearby eRASS:3 Gaia counterparts -> 335 below
the main sequence -> 175 without a VSX / CV / WD / emission-line identification (74 in ZTF's sky, 101 southern). ZTF: J1526 is
the only two-band detection; new periodic signals in 6285270400986331136 (2.334 h, 83 pc; published by Koen 2022 as an M+M
ultrashort binary, Teff/Mbol mismatch attributed there to two similar stars) and 3016053028844771456 (1.133 h, 236 pc, not
catalogued); three weaker eRASS:3-only signals to vet. ATLAS screen of the southern 101 in progress.

**J1435:** period published (Koen 2022; ATLAS half-period). WD + M dwarf evidence: under-luminosity (1.7 mag below the ridge),
g-band excess, X-ray detections (eRASS1, eRASS:3, Swift LSXPS 2024-25), band-dependent light curve.


## 2026-09-23 (night) — J1526/J1435 prior publication; lane M (WISE infrared-excess variability) opened

**Corrections.**
- 6315134987927550592 (J1526) is published: Koen & Kniazev 2024, PASA 41, e108 ('WISE J152614.95-111326.4, an unusual variable
  star'): SAAO B-z photometry, SALT spectra, cool WD (7250-7900 K) + M6, P = 2.25 h, low-accretion pre-CV, WISE amplitudes
  attributed to cyclotron emission. ADS finds it only by the AllWISE name.
- 6285270400986331136 (J1435) is in the same paper (section 9, as ATO J218.9548-17.7890) as a probable WD + red dwarf pre-CV; ADS
  does not index the paper body. The J1435 VSX package now cites it.
- ApJ 991, 125 (arXiv:2505.10478) is Liu, Gu, Lu, Liu & Liu 2025, not Rodriguez et al. (entry above and J1526 rows).

**Lane M.** Selection: Petrosky+2021 WISE periodic variables with P < 0.35 d (37,617) × Gaia DR3, below the main-sequence ridge
(58), colour-consistent G-W1 (6). Method: NEOWISE-R single-exposure period search; W1/W2 vs ZTF amplitudes at the same period;
blend tests (photocentre vs brightness, WISE proper motion); field controls. Recovered: J1526 (W1 0.73 mag vs r 0.20 at the
orbital period; joint ZTF+WISE P = 0.093796948 +/- 1.2e-8 d), QS Vir, DDE 157, 1635581274974672768 (published: Li+2024 XP WD+MS
catalogue; Shani+2025, arXiv:2510.17957, P = 0.116195 d; VSX/ZTF type DSCT is a misclassification).
- 513958743252720768 = ZTF J0220+6303 (90 pc): known deeply eclipsing binary (Brown+2023), pre-polar suspect without circular
  polarisation (Hakala+2026, arXiv:2608.25439). Eclipse ephemeris BJD_TDB 2459501.883344 + 0.099084412(30) E. NEOWISE IR hump at
  orbital phase ~0.78 (0.2-0.5 mag in 2014-2019, ~0.05 mag in 2021-2023), ending at eclipse ingress.
- 3513017956589117056 = J1226-2304 (253 pc; journal): Pelisoli+2025 (arXiv:2505.04693) WD-pulsar candidate of unclear nature (no
  optical variability). NEOWISE P = 0.07968185 d, W1 0.46 / W2 0.29 mag; ZTF r 0.10 +/- 0.045 mag at that period; WISE
  photocentre and proper motion follow the Gaia star; eRASS1 + eRASS:3 (Lx ~2e29 erg/s); PS1 g ~0.8 mag bluer than an M4-M5
  dwarf. Candidate magnetic WD binary.
- 3016053028844771456 (J0541): 1.133 h also in NEOWISE (FAP 1e-13) and ATLAS o and c (FAP 8e-111, 9e-6). No literature under any
  designation.

**Track-1 selection gap.** J1226 has eRASS:3 pany = 0.38 (pi = 1.0, separation 1.1 arcsec), below the cut pany > 0.5. eRASS:3
Gaia counterparts with 0.05 <= pany < 0.5, parallax > 2 mas at >5 sigma, below the main sequence or on the WD side: 1,479; the 243
within 3 arcsec include 18 catalogued CVs (dwarf novae, WZ Sge stars, polars V1033 Cen and CRTS J1944-4202); 175 unidentified.

**VarWISE (Paz+2026, IRSA varwisepure/varwiseext):** 80,186 entries with parallax > 5 sigma and M_G > 7; 226 below the main
sequence at |b| > 10 deg with consistent G-W1. VarWISE labels J1526 and J1226 'ew'.

**J1226-2304 re-analysis.** 3513017956589117056, with the 2010 cryogenic WISE frames (227 W1 / 223 W2 over 14.4 yr):
P = 0.07968186 +/- 0.00000004 d, W1 maximum BJD_TDB 2459999.9470 +/- 0.0012; only viable alias the 182-d alias (4% of
bootstraps). W1 full amplitude 0.96 mag (2010), 0.82, 0.66, 0.36, 0.25, 0.34 mag (2022-24) at constant phase. No instrumental
correlation; 98 field stars max power 0.089. WISE proper motion (-52.8 +/- 4.8, +1.8 +/- 6.0) mas/yr. ZTF forced r amplitude 0.06
(95% upper limit 0.14 mag). VHS M_J 9.51 (M5-M5.5, consistent with a Roche-filling donor at 1.91 h). Residual blue component on
the WD track (~6500-8000 K). eRASS counts 6 and 9.6. Status: candidate low-field magnetic WD + M5 binary (low-state polar or
pre-polar); test = phase-resolved optical/near-IR spectrum.

**Further results.**
- 548694338491992960 (WISE J022948.85+753126.0, 225 pc): eclipsing hot WD + M4-5, mid-eclipse BJD_TDB 2459476.991530 +
  0.150207823(67) E; the 0.0751 d Gaia/ZTF/WISE period is the ellipsoidal half-period; GALEX FUV 19.46; only automated
  variability entries (Gaia DR3 short-timescale, VarWISE 'ew', Petrosky+2021). Journal created.
- 3965186104852552448 (3eRASS J111431.9+131627, 333 pc): P = 0.06914240 d, SDSS u-g 0.51, GALEX NUV, eRASS:3 (DetLike 31),
  eRASS1 supplementary (DetLike 5.4); Lx ~1e30 erg/s. Journal created.
- Pelisoli+2025 'unclear' sample (7): only J1226-2304 has a coherent WISE period; the other six: no significant period or
  blended/crowded WISE photometry.
- eRASS:3 low-pany pool, ZTF (62 reachable, 53 with ZTF): no coherent period (two one-band ~1.03 d daily aliases rejected).
- SDSS DR20 spAll (APO + LCO): no spectrum of J1226, J1114, J0541, J1526 or J1435; J0220+6303 has spec-103700-60626 (M dwarf +
  blue continuum + H-alpha emission, orbital phase 0.67-0.75).
- eRASS1 checks use J/A+A/682/A34 (main, hard and supplementary tables).
- Screens complete: VarWISE 226/226 (strict flags: J1526, J1226, J1059 with caveats, two artefacts, known or ordinary binaries);
  eRASS:3 low-pany 243/243 (155 with >= 150 WISE epochs; 0 holes): J1226 is the only strict flag.

## 2026-09-23 (day) — J1114+1316 and J0229+7531 follow-up

- 548694338491992960 (ZTF J0229+7531) is catalogued: van Roestel's ZTF eclipsing white dwarf catalogue (Zenodo 15007293, April
  2026; public explorer table, not in ADS or VizieR), P = 0.150207791 d (tags eclipsing, ellipsoidal, spot). The previous night's
  'new eclipsing WD binary' is withdrawn. Catalogue added to the known-object filter (quick_known.py).
- 3965186104852552448 (J1114+1316): against 40,000 M dwarfs of the same PS1 i-z/z-y, g-r 0.48 vs 1.27 (bluer than 99.6%). WD
  strongly indicated; Lx/Lbol ~0.026; orbital period 1.6594 h or 3.3188 h (ellipsoidal) unresolved, Roche density favours 3.32 h
  for an ordinary M4. Label: candidate short-period WD + M-dwarf binary, possible low-rate accretion; VSX type SIN if filed. Not
  in van Roestel's (eclipsing) or Rebassa-Mansergas+2025 catalogues.

## 2026-09-23 (afternoon) — Cross-check of EC 10246-2707 (Planet Hunters TESS Talk)

- Gaia DR3 5468670738602933504 = TIC 193092806, HW Vir-type sdB + dM binary (Barlow+2013); known (VSX, SIMBAD, 9 ADS papers).
  Outside our selections (parallax 1.02 mas, M_G 4.48). NEOWISE amplitude equals the optical one at the orbital period (W1 0.27,
  ZTF r 0.24 mag): no infrared excess. Matches in GALEX, variability catalogues, Ritter-Kolb CV/LMXB/pre-CV table (B/cb),
  Gentile Fusillo+2021; no radio, X-ray or gamma-ray match.
- TESS sector 100: primary eclipse FWHM 9.7 min (depth 0.40), secondary at phase 0.5 FWHM 10.2 min (depth 0.12). In 20-min bins
  the primary eclipses alternate between one-bin and two-bin appearances (P = 8.53 bins).
  Report: `docs/reports/ec10246_crosscheck_2026_09_23/`; journal created.

## 2026-09-23 (evening) — J1226-2304 deep dive; lane M Galactic-plane screen; ATLAS screen v3

- J1226-2304 (3513017956589117056): PS1 grizy (2010-14), SkyMapper i/z (2016-20) and DECam folded on the WISE ephemeris: no
  coherent modulation. Per WISE visit, mean W1 flux flat (0.39-0.44 mJy); W1 semi-amplitude 0.15-0.19 mJy (2011-16), 0.04-0.07 mJy
  (2018-24), 0.12 mJy in mid-2024; phase of maximum stable. Odd/even (2P) term delta chi2 5.5 (p = 0.06). Mean flux 2.0x (W1) and
  3.6x (W2) the photosphere predicted from VHS J/Ks; unWISE W1 and W2 centroids agree within 0.1". Label: coherent infrared
  periodic variable with a mid-IR excess and candidate magnetic WD + M-dwarf binary; cyclotron emission favoured, orbital period
  unconfirmed. Scripts, data, figure: `docs/reports/lane_m_wise_ir_2026_09_23/`.
- Lane M extension started: VarWISE below-MS variables at |b| <= 10 deg (522) plus 24 high-latitude rows that met the cuts but
  were missed in the first run (546 total).
- Southern Track-1 ATLAS screen v3: a band is unmeasurable if its median difference-flux error exceeds max(200 uJy, half the
  star's flux); frames with errors > 3x the band median are dropped. Of the three v1 flags, 4732816401257508480 has no coherent
  signal, 4756815201043718784 is unmeasurable (G = 9.5 star at 3.5"), 4864794492789757568 pending.

## 2026-09-23 (night) — Lane M: J0753 and J1059 audits

- Lane M screen periods were computed from UTC MJD. J1059-2740 (5456743064671253632): the barycentric audit prefers
  P = 0.1209716 d, the +2/yr alias of the screened 0.1210522 d; ZTF amplitude 0.20 mag at the corrected period (0.09 at the alias).
  J0753-0042 (3082614748370926848): screened period survives. Other screened WISE periods unaudited.
- Bright-minus-faint NEOWISE W1 difference imaging (`scripts/wise_localise.py`): J0753 variable flux within 0.1-0.2" of Gaia;
  J1059 within ~0.1-0.2" (one registration star). Scan-direction centroid offsets of ~0.3-0.5" are common to field stars.

## 2026-09-23 (late) — Zeeman-split Balmer lines in SDSS-V DR20 white dwarfs

- Sample: 78 SnowWhite stars with p_dah + p_dahe + p_dbh + p_mwd > 0.3 (19 already DAH/DAP in SIMBAD). A triplet-vs-one-Gaussian
  test flags every star; adopted null = core + wing profile, then visual inspection and free-centre triplet fits per line (B_split
  on the linear-splitting scale; published dipole fields of four sample stars are 1.4-2.0x higher).
- 32 selected by eye: 10 already magnetic (DESI DR1 x8, LAMOST/Jewett+2024 x1, Garcia-Zamora+2026 x1); 22 with no magnetic
  classification outside SnowWhite (SIMBAD, MWDD, VizieR all-table, ADS short names, DESI DR1 Amorim+2026 and Swan+2026, LAMOST
  DR10, arXiv source text of 18 catalogue papers). A full-spectrum look at the other 27 adds 5 (B_split 9-11 MG, beyond the
  continuum-window range). 27 journals; 78 register rows.
- Astra 0.8.1 visit spectra are shifted with XCSAO velocities of -725 to +8176 km/s for these stars; three apparently exotic
  spectra are this artefact (older SDSS spectra of two show normal DA lines). Triplet stars have consistent fields per visit and
  between H-alpha and H-beta.
- J2159+5102 (1980205739970324224), 79 pc: B_split 5.6 MG; new ZZ Ceti in Vincent+2020 (1286 s, 1.2%, one 1.7-h run). ZTF
  2018-2025: no coherent signal (injected 1.2% recovered 40/40 in g). Neighbours at 1.6" and 2.3". J2316-5529
  (6499095244738784128), 62 pc: B_split 8.0 MG; common-proper-motion pair with HD 219458; ESO X-shooter (2020, public) and UVES
  (2025, proprietary to 2026-10-27) spectra exist. Re-check: J2159 magnetic; of the 22, 8 secure, 9 probable, 5 possible.
  Report: `docs/reports/mwd_zeeman_sdssv_2026_09_23/`.

## 2026-09-24 (night) — Track 1: eclipsing white dwarf + M dwarf 2MASS J03531244-5502363

- Southern ATLAS flag 4731701084150029824 (3eRASS J035311.8-550237, 4XMM J035312.2-550238; 110 pc, 2.1 mag below the main
  sequence): flat-bottomed 10.6-min eclipse every 0.14786971 +- 0.00000004 d in ATLAS o and c (depths ~30% and ~57%), no secondary;
  the screen's half period is excluded by unequal alternate dips (48 vs 6 uJy). Not in VSX, SIMBAD, ADS, Gaia DR3 variability
  tables, SSS, ASAS-SN or TESS EB catalogues. VSX package prepared, not submitted: `docs/reports/vsx_j0353_2026_09_24/`. Two other
  flags dropped (unmeasurable; not reproduced + equal-parallax neighbour at 1.73").
- The sinusoid screen finds narrow eclipses only at a harmonic and in one band; a fine-grid box search recovers the binary in both
  bands and is being applied to all finished southern light curves.

## 2026-09-24 (night) — Pulsating versus magnetic white dwarfs

- 882 published pulsators (30 sources) x 8,512 magnetic-classification rows (23 sources): 37 overlaps, each judged; SDSS-V spectra
  of 238 pulsators screened. J2159+5102 remains the only published pulsator with a confirmed Zeeman triplet. Label conflicts
  recorded (a ZZ Ceti catalogued DAH without visible splitting; DBVs labelled DBH:; SIMBAD Pu* from a candidate list; MWDD magnetic
  flags on G 29-38 and GW Vir stars). The Amorim+2026 DESI file stores Gaia ids as rounded floats; the 27-star novelty check was
  redone by position (no entry within 917"). Report: `docs/reports/magnetic_pulsators_2026_09_24/`; 34 register rows.

## 2026-09-24 — Lane M Galactic-plane screen finished

- 546 targets (522 |b| <= 10 deg + 24 high-latitude), 542 with enough NEOWISE epochs. Strict cuts (W1 power >= 0.3, n >= 150,
  A_W1 >= 0.15, not a WISE-orbit alias within 2%) leave 5: J0753-0042 (lead, journal), J0724-2531 and J1236-5430 (dropped earlier:
  neighbour blend; unreliable parallax), and two new at 1.540 h and 1.550 h (3422836150319231744, 3369213208749088256), within 3%
  of the WISE orbital sampling with no ZTF signal: registered as unvetted, probable sampling aliases.

## 2026-09-24 — TIC 685214650 (Gaia DR3 4771958598593101184): TESS pixel test

- The Huang+2026 109.7-s signal of this 75-pc cool DC white dwarf is reproduced in Sector 87 (6.3 sigma, same phase in both orbits,
  not in the background, absent from 12 same-CCD controls) and localised to the WD rather than the G = 16 star 28" away
  (single-source PSF fits, delta chi2 11). Absent in Sector 94 six months later (0.05 +- 0.04 vs ~0.24 e/s expected). Not a
  stable rotation signal as seen; origin open. Report: `docs/reports/tic685214650_tess_2026_09_24/`.

## 2026-09-24 (night) — High-field magnetic white dwarfs and CVs in SDSS-V DR20

- High-field (`docs/reports/highfield_mwd_sdssv_2026_09_24/`): SnowWhite p_mwd is uninformative (max 0.057); high-field magnetic
  WDs sit in DC/DC:/CV classes. Of ~200 screened spectra, four magnetic DAs at ~17-60 MG without prior magnetic classification:
  PHL 4443 (secure, 4 visits), WDJ024544.82+721144.58, WDJ204048.29-572123.13 and the wide companion of HIP 20180 (probable);
  three possibles; by-products a warm DQ catalogued as DC: and a possible DAQ. Fields carry a factor-2 systematic (0.5-1.05 on 7
  controls). Coverage ~10% of the DC selection.
- CVs (`docs/reports/cv_sdssv_2026_09_24/`): 605 SnowWhite CV rows dispositioned. New: A1 J225737.41+541619.9 (WD-dominated dwarf
  nova, 196 pc), A12 J213306.16+463819.3 (dwarf nova, probable). Three eROSITA-field CVs uncheckable until Brink+2026 is public; A8
  (MGAB-V3675) looks like a polar; A10's SIMBAD type (QSO) is wrong.
- Exotic-atmosphere and rotation-period searches incomplete here; not integrated.

## 2026-09-24 — Lane 1 (+3): ZZ Ceti and DBV search, SDSS-V DR20 spectroscopy x TESS Cycles 6-8

- Prior art (arXiv queried directly; `prior_art.py` HTTP 406): Romero+2022 (74 new, Cycles 1-3), Romero+2025 (32 new, Cycles
  4-5), Bognar+2023, Huang+2026 (Cycle 7 20-s, >= 50 c/d). No SDSS-spectroscopy-selected search; those papers form the known
  filter.
- 912 SDSS-V strip stars (G < 18; SnowWhite DA 10-13.5 kK, DB with GF21 Teff_He 19-36 kK), 1,506 TESS 120-s light curves
  (Sectors >= 70). 29 known pulsators recovered (PG 1310+583 only via ADS: the 882-star list lacks Bognar+2026). New ZZ Ceti:
  [OHD2001] WD J2324-595 (1049 and 882 s, 3 sectors), GALEX J214927.5-515827 (472.6 s in 4 sectors, 947.5 s), both on target in
  the pixels; probable: GALEX J054243.4-261011 (692 s), GALEX J033619.1-564435 (971 s). No DBV in 36 DB stars. Two long-period
  detections were contamination or not in the pixels. Report: `docs/reports/zzceti_sdssv_tess_2026_09_24/`.
- Lane 5 (Gaia DR4 readiness): 180 known DAV/DBV stars have DR3 epoch photometry for a template test; Gaia DataLink returned
  HTTP 503 (hole).

## 2026-09-24 — Rotation search for the 27 new SDSS-V magnetic white dwarfs

- Method: ZTF DR24 + TESS SPOC, Lomb-Scargle with permutation null and injection A90, band/time/depth splits, TESS pixel
  localisation. Controls: 4 published rotators recovered (EGGR 156, SDSS J2223+2319, J1630+2724, J1543+3021); 3 non-magnetic DAs
  clean.
- 16 null (A90 0.5-5% ZTF, 2-20% TESS), 5 without usable data. The TESS 14.6 h signal near GALEX J231613.4-552927 is on the
  G 14.27 star 22" away (VSX ROT, P 0.60621 d; register row). GALEX J095130.1-245723 10.17 h is in one TESS sector only
  (unconfirmed). Two ZTF short-period peaks fail the permutation null (FAP 0.098). No rotation period established.
  Report: `docs/reports/mwd_rotation_2026_09_24/`; ledger rows on all 27 journals.

## 2026-09-24 — Exotic white dwarf atmospheres in SDSS-V DR20; ZZ Ceti lane 1b

- Exotic atmospheres (`docs/reports/exotic_atm_sdssv_2026_09_24/`): DAHe emission screen of 3,214 spectra with injection
  completeness -> no new DAHe (known J1437+0309 recovered). Absorption-class inspection (186) and hot-DQ locus (95): hot DQ with
  strong C II, Gaia DR3 5208047381438507520 (GALEX J073504.2-794409, G 16.56, 96 pc; catalogued DA from photometry/XP, XP mass
  1.24 Msun); probable broadened hot DQ 4792264314911712512; possible 6466745168812781568; carbon + hydrogen WD 5836110898905253760
  (C I + H-alpha, 76 pc, not in MWDD); 11 DQ reclassification candidates. Novelty check: SIMBAD, VizieR, MWDD, DESI/LAMOST, ADS
  aliases, 55-paper source grep. TESS for the hot DQ: no periodic signal above ~5 ppt.
- Lane 1b (Cycles 1-5, 2,294 light curves): 31 known pulsators + PG 1310+583 recovered; L 210-25 (817 s, S13, on target) is a
  probable ZZ Ceti (VSX type WD from Gaia DR3); two contamination cases. 20-s lane (1,518 light curves) in progress.
- Gaia DataLink epoch photometry still HTTP 503 (lane 5 template test a hole); GAVO and ARI TAP mirrors lack DR3 epoch photometry.

## 2026-09-24 — Deep dive: Gaia DR3 5208047381438507520 (GALEX J073504.2-794409)

- Carbon in two independent spectra: SDSS-V optical C II (many lines, common velocity ~+93 km/s) and public HST/COS G130M from
  SNAP 17420 (PI Gaensicke, 2024-07-13; C III 1175/1247, C II 1324, excited C II 1335.71 at +96 km/s). Probable hydrogen
  (H-alpha). Provisional class hot DQ with probable hydrogen (DQA); composition and temperature need an atmosphere fit.
- GALEX FUV-NUV +0.32, redder than every DA of the same colour incl. 16 gravity-matched DAs (max -0.13). No variability (TESS,
  SkyMapper, Gaia). No prior carbon-rich classification; the HST proposers list it as DA with a noted FUV deficit.
- A re-check reproduced the numbers; seven corrections applied (WISE AB/Vega mix-up, CCF significance wording, velocity error,
  COS continuum systematics, extinction statement, variability limits, a failed ESO query).
  Report: `docs/reports/hotdq_j0735_2026_09_24/`.
- 20-s ZZ Ceti lane finished: no new pulsator; L 210-25 has a second on-target detection (941 s, S105).

## 2026-09-24 — Public data release of the SDSS-V white-dwarf results

- Decision (user): separate public repository https://github.com/alejandrozarco/sdssv-white-dwarfs-2026 (commit 87fed5e,
  2026-09-24T16:09Z) as a timestamped record: 28 Zeeman-split WDs, 3 carbon WDs (optical line tests, HST/COS lfac0z010, GALEX),
  5 ZZ Ceti TESS results with pixel tests, the ATLAS eclipse of 4731701084150029824, 2 Balmer-emission objects, the TIC 685214650
  pixel test. All table values recomputed from public data by the included scripts. Not included: high-field magnetic WDs (not
  reproducible by a simple script), DQ reclassifications, CVs other than A1/A12, objects from earlier lanes.
- Commit 6d11dbb: Zeeman central-component shift range widened from +-15 to +-40 A (five stars at 8.8-10.7 MG had H-beta shifts at
  the old limit; fitted H-beta shifts -18 to -26 A, growing with B^2 as expected from the quadratic Zeeman effect). H-beta B_split
  changed by -0.10 to -0.17 MG for 4198738558061020928, 4241409569220727424, 50526755482496000 and 2833867392391927936 (-0.01 for
  5807585134758743040); H-alpha unchanged. Table now lists fitted centres, shifts, asymmetries; figure marks fitted centres.
  Correction: the earlier figure drew symmetric lines at the laboratory wavelength, missing shifted or lopsided troughs.
- Magnetic by-products of the exotic lane (12 SnowWhite stars not in the 78-star list): two new Zeeman-split DAs,
  4679463733391272448 (GALEX J040038.6-615458, 4.28/4.22 MG) and 3290180587821828480 (GALEX J050006.8+080244, 5.44/5.11 MG), two
  visits each, components at 7-23 sigma; pass SIMBAD/MWDD/VizieR/DESI/LAMOST/88-paper/ADS/eRASS1 checks. GALEX J033833.9-332802
  (9.2 MG) is already in Hernandez-Diaz+2026 (arXiv:2607.27855; found via ADS full text). Bright stars 5920596066603197056 (G 15.6)
  and 4883191104733786496: hot, nearly featureless WDs, not triplets (open). The 28 released stars are not in Hernandez-Diaz+2026;
  none is an eRASS1 source.
- Decision (user): TIC 685214650 section removed from the public repo and purged from its history by rewrite and force-push
  (commits 87edc83, 91a4432 keep original dates); old hashes remain reachable on GitHub until garbage collection.

## 2026-09-24 (evening) — Follow-up of the open magnetic leads (SDSS-V DR20 exotic-atmosphere by-products)

- Gaia DR3 6021870154194477312 (GALEX J161854.1-355427; GF21 38,970 K, log g 9.22, 1.31 Msun; featureless SDSS-V spectrum):
  P = 103.3757 min (f = 13.929771 +- 0.000007 c/d) in three independent data sets:
  - TESS S65 (FAP 3e-7; blended aperture, CROWDSAP 0.01);
  - ATLAS forced photometry 2015-2026 (c 5.4 +- 0.3 %, o 5.7 +- 0.3 %; nearly sinusoidal; phase-stable over 10.5 yr);
  - Gaia DR3 epoch photometry 2014-2017 (G 6.9 +- 0.2 %, same phase as ATLAS).
  Gaia resolves the three neighbours at 9-13 arcsec; ATLAS at their positions shows no independent signal (0.3-3 uJy residuals,
  roughly anti-phased with the WD, consistent with its variability in their background): the signal is the WD's. The period is
  only a GLS frequency in Gaia DR3 vari_spurious_signals (computed for every variable source); VSX lists type WD, no period. Not
  in Steen+2024 (105 Gaia-period WDs, though it meets their parent selection), Jestin+2026 (ZTF-only; Dec -35.9), or ADS full
  text under any alias. Interpretation: most likely rotation of a strongly magnetic, ultramassive WD (no lines at 39,000 K points
  to a very strong field). Companion disfavoured: amplitude nearly flat with wavelength (irradiation would rise steeply to the
  red); no emission lines; VHS and CatWISE exclude M and early/mid-L companions. Needs spectropolarimetry. Journal:
  `docs/object_journals/6021870154194477312.md`.
- Gaia DR3 4909119551717563520 (WT 37; SIMBAD WD* D, MWDD DC:): high-field magnetic DA. Hydrogen-in-B template best Bp 26 MG
  (26-42); no-field model worse by 3018 (featureless negative controls: 25-470). TESS, 9 sectors: no periodic signal above ~0.5 %.
  No magnetic classification in SIMBAD, MWDD, VizieR, ADS or the 89-paper source grep.
- BPM 25260 (5920596066603197056) is known magnetic (Bagnulo+2024): a recovery. Gaia DR3 4883191104733786496 still open.
  HS 2157+8152 is a data-quality case.
- Remaining by-products with inconsistent H-alpha/H-beta fits (2246631460497465472, 3987356721738829184, 6915353300288749440 =
  a Kilic+2026 DESI DA, 4867935694432066304): registered, no claim.
- Zeeman DAs 4679463733391272448 and 3290180587821828480:
  - 4679: wide common-proper-motion F5V companion (HD 25636, 86 arcsec, Gaia FLAME age 2.0-3.3 Gyr), an age benchmark; field
    stable between visits.
  - 3290: no rotation signal in ZTF (daily aliases only); per-visit H-alpha splitting differs by ~4 sigma at S/N 7.
- Correction: the Astra mwmStar coadd is in the XCSAO frame, and XCSAO velocities of magnetic WDs are hundreds of km/s, so the
  public Zeeman table's shift and centre columns for 'coadd' rows are offset by up to ~13 A; B_split nearly unaffected.
  Re-measured on XCSAO-corrected visit coadds: B_split changes <= 0.21 MG except 2069622487994113408 (H-alpha -0.91 MG; its two
  visits differ by 470 km/s in XCSAO velocity) and 5848754492268362624 (H-alpha +0.43 MG). Corrected H-beta shifts -2 to -18 A,
  correlated with B^2 (Spearman -0.60 at H-beta, -0.67 at H-alpha), as expected from the quadratic Zeeman effect. Public-repo
  correction prepared, not pushed. Earlier internal Zeeman fits on mwmStar coadds carry the same offset in shift and centre.

## 2026-09-24 (evening) — Public repo updated; VSX and contact drafts for GALEX J161854.1-355427

- Public repository (github.com/alejandrozarco/sdssv-white-dwarfs-2026), pushed (decision: user):
  - 3e4c55e: Zeeman coadds re-measured on in-stack visits with the XCSAO shift removed.
  - cc13faa: photometric period of Gaia DR3 6021870154194477312 (table, script, figure, ATLAS inputs for the star and its 3
    neighbours, Gaia epoch photometry). Recomputed f = 13.9297708 +- 0.0000067 c/d. Times of maximum agree across ATLAS c/o,
    Gaia G and TESS within 1-2 min; the neighbours peak half a cycle later.
- Drafted, not filed or sent: VSX revision adding P = 0.07178869 d (type WD kept); letter to Bagnulo & Landstreet (Armagh), who
  found the field of the analogue WD 1754-550 = BPM 25260 (A&A 692, A174: hot DC, ~35 kK, 1.33 Msun, >~100 MG, circular
  polarisation varying on ~15 min).
- BPM 25260 TESS (TIC 76392634, 5 sectors, CROWDSAP 0.08-0.22): after high-pass filtering, 51.75 c/d (27.8 min) is the top peak
  above 5 c/d in S13, S104 and combined (FAP 0.007, ~0.5 %). Weak; ATLAS check below.

## 2026-09-24 — Rubin public alert stream re-checked: still dark

- Fink LSST (`/api/v1/tags`: in_tns, most_likely_sn, extragalactic_new_candidate, hostless_candidate) and ALeRCE LSST
  (`object_api/list_objects?order_by=lastmjd`): newest data MJD 61235.419 (2026-07-14 10:04 UTC), as on 2026-09-18.
- Rubin public alert-stream dashboard (grafana.slac.stanford.edu, public dashboard 26d8f1d4…, via ls.st/alert-stream-status):
  "Alerts in plotting interval" = 0 over 24 h, 7 d and 30 d; broker status = 1 (up); prompt-processing and raw-ingestion panels
  empty. No pause or resumption notice on the Rubin community forum (2026-07-10 update: LSST began on 29 June). No Rubin-lane
  input for 72 days.

## 2026-09-24 (night) — New lane: Gaia DR3 GLS periods of white dwarfs, confirmed with ATLAS / ZTF / TESS

- **Background:** GALEX J161854.1-355427's 103-min period sat uninterpreted in Gaia DR3 vari_spurious_signals. Steen+2024
  (ApJ 967, 166; 105 WDs) required recovery in ZTF, TESS or a second Gaia band; Jestin+2026 (A&A 712, A243; 864 WDs) is
  ZTF-only. Southern (Dec < -30) and post-2024-TESS cases are unvetted.
- **Prior art:** repo arXiv screen no strict match (broad hits Steen+2024, Jestin+2026); ADS: no paper using vari_spurious_signals
  for WDs; Ranaivomanana+2025 (A&A 693 A268; 704 A70) cover the MS-WD valley and hot subdwarfs, not the WD sequence. ATLAS is the
  independent confirmer.
- **Selection:** Gaia DR3 vari_spurious_signals × gaia_source.
  - parallax/error > 5; M_G > 4.5(BP-RP) + 9 (Steen's cut); BP-RP < 1.5 -> 2,084.
  - GLS FAP < 1e-5 and N >= 20 -> 159, 72 of them in Steen's 105.
  - Not in Steen, Jestin or VSX-with-period: 25 (tier 1). Tier 2 (FAP 1e-5 to 1e-3, M_G > 9.5, IPD correlation < 0.5, away from
    the 4 c/d spin harmonics): 16, 6 unvetted.
  - Gaia BP/RP phase consistency checked for all.
- **Confirmed** (period found independently, same phase where testable):
  - Gaia DR3 2883364038621038208 = GALEX J060343.7-380911: 101 pc, 8,400 K, 0.76 Msun. P = 10.802 h in ATLAS (FAP 7e-123,
    4.7 %) and TESS S87+S98 (top peak in both); Gaia phase agrees.
  - Gaia DR3 6456720612064924928 = GALEX J211204.8-571801: 88 pc, 8,500 K, 0.79 Msun. P = 61.33 min in ATLAS (FAP 1e-26, 3.2 %).
  - Gaia DR3 178685757799822080 = GALEX J043613.3+383720: 104 pc, 8,900 K, 0.77 Msun. P = 7.30 d in ZTF (FAP 2e-14, 4.9 %).
  - Gaia DR3 437628614520520320: 96 pc, 8,300 K, 0.69 Msun. P = 5.04 d in ZTF (FAP 7e-46, 4.6 %).
  - All four: XP class DA; no published period or magnetic classification (SIMBAD, MWDD, VizieR, DESI, ADS, arXiv sources). Most
    likely spotted/magnetic rotation (a ~8,500 K DA varying by 5 % at a single period); fields not measured.
  - Recoveries: EC 21277-2231 (1.52 h; Ranaivomanana+2025), Feige 7.
  - Not confirmed: 5055036663256963072 (Gaia 11.986 c/d = 12 - 1/63, a spin-harmonic sideband).
  - Method criterion: Gaia frequencies near 12 c/d (12 - 1/63) and 4k c/d are treated as suspect.
- ATLAS server outage ~21:25-22:05; 10 ATLAS light curves and 3 ZTF checks pending.
- BPM 25260 TESS 27.8-min signal not confirmed by ATLAS (95th percentile of control windows); dropped from the Armagh letter.
- ZTF: 367659027423727232 not confirmed (Gaia 1.111 c/d; ZTF rank 2850). 382731618150879616 and 388756456537099392 (M31 field):
  IRSA ZTF queries timed out twice (hole).
- 23:2x-23:47 update, two more ATLAS confirmations:
  - 2888030331609338240 = GALEX J054140.8-362248: 125 pc, 9,700 K, 0.57 Msun. P = 16.353 h (FAP 3e-50, 2.4 %), also TESS S98 (top
    peak, FAP 2e-10). Its W1 excess is a WISE blend with a star 3.2 arcsec away.
  - 3496637913394359680 = GALEX J124819.8-261413: 95 pc, 7,900 K, 0.65 Msun. P = 5.886 d (FAP 2e-100, 4.5 %), TESS S101
    consistent.
  - Six confirmed in total; five pushed to the public repo (2be3383, tables/periodic_white_dwarfs.csv). Gaia and TESS times of
    maximum agree with the ground-based fit to 0.00-0.09 cycles. 437628614520520320 awaits an IRSA download. VSX revision drafts
    for the five, not filed.
- Hot massive sub-lane (GF21 Teff > 15 kK, M > 1.05 Msun, Gaia VARIABLE, G < 18.5; 15 stars): mostly known (PHL 657 hot DQ, VSX
  2.11 d; CL Oct ZZ Ceti; two VSX periods). TESS 120 s and 20 s for PG 0136+251, PG 1058-129, GALEX J002958.9+364834: no coherent
  signal (low-frequency sector trends only).
  - PG 1658+441: coherent 42.235 min (34.0949279 c/d), 0.150+-0.019 %, in all 7 sectors (2020-2025) at consistent phase; pixel
    test on the WD in 3 sectors. Published as 42.24 min by Jewett+2024 (ApJ 974, 12; Hernandez+2024 reported none): a recovery.
  - Jewett+2024 and Hernandez+2024 added to the novelty-check sources; none of the six new periods is in Jewett's rotation table.

## 2026-09-25 — Hot DQ 5208047381438507520: second classification check

- Independent checks covered the optical spectrum, UV/temperature and prior work.
- Classification: hot DQ confirmed.
  - The optical C II equivalent widths match the classical hot DQs of Dufour+2008.
  - The Balmer lines are weaker than in all 16 comparable DAs.
  - COS shows no broad Lyα wings; C I troughs are present.
  - Teff about 22 kK (empirical).
- Corrections (`review2/SUMMARY.md`):
  - Hydrogen is only possible; Si II 1260 is interstellar.
  - The velocity error is ±20–40 km/s; the red optical lines carry quality flags.
  - The 17420 "DA" label is generic; hot DQs with hydrogen are not new.
- Prior work: the 17420 team fits C and Si in every SNAP spectrum; Sahu presented a COS C/Si survey of 427 DAs at EuroWD in August 2026. The contact email draft was revised to offer the optical SDSS-V spectrum and to disclose the public repository.
- Side lead (unchecked): other 17420 targets with FUV deficits of 1.7–3.0 mag, e.g. WDJ030350.56+060748.75.
- FUV-deficit check of the 17420 targets: the four with larger deficits than J0735 are a known magnetic DXP (WDJ0303+0607), two known DBs, and WDJ0800+0040 (He I in SDSS-V; SnowWhite DB:; no carbon). J0735 is the only carbon-rich one.
- Public repository README condensed (917b200); methods moved to METHODS.md; hot DQ comparison figure added.
- EC 21277-2231 ATLAS: 15.77662 c/d, FAP 4e-188 (recovers the Ranaivomanana+2025 period). 6644157726508197504: Gaia 12.04 c/d not confirmed. J1819-1208 (nearest hot DQ, Kilic+2023) added as the reference for J0735.

## 2026-09-25 — Hidden hot DQs among SDSS-V "DA" white dwarfs (GALEX FUV deficit)

- **Method:**
  - SDSS-V SnowWhite spectra with plx > 3, G < 18.8, BP-RP -0.6 to -0.1, S/N > 8: 3,672 stars.
  - GALEX AIS cross-match within 4 arcsec: 2,240.
  - FUV-NUV compared with the SnowWhite-DA locus at the same BP-RP: 230 outliers redder by more than 0.35 mag, mostly DBs.
  - Carbon line test on the 47 non-DBs.
- **Validation:** J0735 is a 9.0-sigma outlier with C II contrast 16.7.
- **New:** GALEX J205119.1-161749 = Gaia DR3 6886051830805052288 (187 pc, G 17.55, BP-RP -0.40).
  - Catalogued DA in SIMBAD, MWDD, GF21 and Gaia XP; SnowWhite gives 'DC/DA'.
  - SDSS-V shows 9 C II lines (10-43 sigma) and C I, with contrast about 16 in each visit separately.
  - No He, no H.
  - FUV-NUV 0.86 mag redder than DAs of the same colour; FUV-NUV temperature about 20 kK.
  - v_tan about 82 km/s.
  - No prior carbon classification found (SIMBAD, MWDD, VizieR, DESI, 91 paper sources, ADS, MAST, ESO). Outside the 100 pc samples; fails the Kilic+2025 FUV cut.
- **Prior art:** Kilic+2025 (arXiv:2507.12655) select merger remnants by FUV-G_RP within 100 pc. J0735 and J2051 both fail that cut; the FUV-NUV plus optical-spectrum selection is a method extension.
- Row and figure committed locally, not pushed; decision pending (user).
- 6639666736903611136 = GALEX J191430.4-572023 (51 pc, 8.2 kK, 0.60 Msun): P = 3.711 d in ATLAS (FAP 1e-32), Gaia and 5 TESS sectors; no IR excess, probable slow rotator; public repo aa6b315; VSX draft. 4764068163850888064 (CV) not confirmed. Hidden-DQ lane pushed (4ca451f).
- Tier 3 (Gaia GLS FAP 1e-3..1e-2, WD locus, G<18.5): only GD 279 passes the cuts; TESS rules out its Gaia 24.27 c/d. No further candidates at these cuts. Gaia-period lane totals: 9 confirmed new periods (J1618 + 7 WDs + hot DO + HV low-mass DA), 2 recoveries, rest unconfirmed or known.
- J2159 pulsation claim, new sources (2026-09-25): ZTF high-cadence night 2018-12-01 (132 x 30 s, 4 h) excludes 1.2 % at 1286 s (limit ~0.7 % over 1080-1570 s); Gaia G scatter at the 39th percentile (no excess); TMTS not listed (coverage unknown). The 2020 single PESTO run remains the only detection.

## 2026-09-25 00:40 UTC: astrometric catalogue sweep, hot-DQ time series, SDSS-V carbon screen, TESS strip scan, SMOKA

- **Astrometric catalogue sweep, J0735 and J2051** (`docs/reports/hidden_hotdq_fuv_2026_09_25/allsources/`): Gaia DR2 and DR3 proper motions agree (<1.7 sigma); 33 VizieR astrometric catalogues agree or are too shallow; no comoving Gaia DR3 source within 1 pc projected; neither star is in El-Badry+2021. No acceleration, no wide companion. Most listed catalogues are Gaia-anchored or re-packaged.
- **Hot DQ rotation limits:** J2051 ZTF (1,016 epochs): no period at 0.02-300 c/d; >~1 % excluded at 5 min-4 h; PS1, SkyMapper DR4 and NSC DR2 epochs show no significant variability. J0735 ATLAS (3,351 points): the ~1 % peaks are incoherent (first vs second half, filters, nightly bins); >~1 % excluded at 0.1-72 h. 4883191104733786496: ATLAS null, >2 % excluded.
- **Correction (gate bug):** the DESI step of `gate_mag.py` failed to parse (Amorim separator; Swan id column) and returned strings instead of HOLE. All 15 affected objects re-checked (`gate_desi_fix/desi_recheck.csv`): 14 are outside DESI; 6915353300288749440 is in DESI (Amorim DA, Swan DBA 33 kK) and already known via Kilic+2026. Ledger correction rows added; script patched.
- **Carbon screen of SDSS-V DR20 massive DA-type WDs** (`carbon_screen2.py`): 3,480 spectra (DA-type, parallax >5 sigma, S/N >5, log g >= 8.5 or CMD-massive). Method: weighted matched filter of C I+C II templates, velocity prior -200..+400 km/s; tuned on 7 known carbon WDs, all above the sample 99th percentile. Prior art: Kilic+2024 (DAQ class), Kilic+2025 (FUV), arXiv:2602.02670 (Q-branch DAQs), Garcia-Zamora+2026; lane scope is validation plus stars beyond 100 pc.
  - Partial run (1,458 of 3,480 spectra): 3 published carbon WDs labelled DA by SnowWhite recovered: SDSS J0008+2507 (DQA), LP 648-58 (DQA), LAWD 65 (DAQ in arXiv:2602.02670; SIMBAD and MWDD still list DA).
  - Open: 2076678981825545088 (MWDD DA, 145 pc; C I 4775/5055/5385/7120 in 2 visits plus strong H-alpha, DAQ/DQA-like, no carbon classification found) and 4377432592229753472 (MWDD DC:, S/N 5, possible).
  - Artefacts: 5011403746899517568, 5659624950224046464, 2170138123020775040.
  - Rest of the sample pending.
- **TESS strip scan:** 2,586 SPOC 120-s light curves (S70-107) of GF21 ZZ/DBV-strip WDs; 2,455 analysed, 131 download holes. 60 stars with a detection, 49 in the known-pulsator list. Of the other 11, most have periods >2,300 s at CROWDSAP <0.1 (probably contamination). Candidates: 1810475401285228928 (DBV strip, 334.8 s), 6370863945235959680 (956-960 s in 2 sectors), 6123269216744427008 (256.7 s), 4693541467955966848. Novelty and pixel tests pending.
- **SMOKA:** no frames cover J2159, J2051, J0735, LAWD 65 or 2076678981825545088. Test candidate: Suprime-Cam 2007-06-20 Rho Oph exposures covering the predicted position of (119066) 2001 KJ76 (11 x 160 s, i band, ~12' from the pointing centre). Not submitted; decision pending (user).

## 2026-09-25 01:10 UTC: SMOKA test request, carbon screen complete, TESS strip scan vetted, Gaia EB white dwarfs

- **SMOKA:** positive-control object searches work (GD 358, G 29-38, PG 1159-035). Of 66 lane targets, 11 have frames, all imaging (Kiso KWFC, HSC, MITSuME); none has HDS spectroscopy. Tomo-e Gozen (SMOKA sub-archive) has 274 sparse 6-9 s frames of J2159+5102 (2019-2023), not usable for its 1286 s pulsation.
  - Test request P06USER0925100419FT submitted: 488 MITSuME Akeno frames (2013-10-30 and 2013-11-07, g/R/I, 60 s) of the XTE J1908+094 field, which contains the 8.4 MG Zeeman WD Gaia DR3 4307667617377160704. Purpose: fast-rotation search (minutes to ~2 h).
  - ZTF for that WD shows only synodic-month systematics (0.0338 c/d and its daily aliases); nothing at >2 c/d.
  - Report directory: `docs/reports/smoka_2026_09_25/`.
- **Carbon screen (3,480 massive DA-type SDSS-V spectra):** complete. All 17 known carbon controls recovered (DAQ 5666458346271348992 at contrast 39.7). Published carbon WDs labelled DA by SnowWhite: LAWD 65 (DAQ, arXiv:2602.02670), SDSS J0008+2507, LP 648-58, 5243591401210032000, 4528933302988697344.
  - False positives: known DAH (Zeeman components, e.g. 5764355941030501632, J0902+5111), artefact spikes, edge velocities.
  - New candidates (journals):
    - 883885440381808000: C II + C I + H-alpha; the LAMOST 2011 spectrum independently peaks at the same +110 km/s; LAMOST pipeline class WDMagnetic; 222 pc.
    - 4847399905305694080: C I + H-alpha; GALEX GII FUV-NUV +3.13, against 0/2,040 DAs as red; 257 pc.
    - 2076678981825545088: C I + H; M_G 12.9 (massive); 144 pc; KIC 5801947 (Kepler FFI only).
  - Possible (register rows): 6482049958353650048, 4377432592229753472.
- **TESS strip scan vetted:** 60 detections; the 11 outside the 882-star list are known or contamination:
  - EC 02251-6933 = the 47-min eclipsing double WD of Munday+2023; the 1415.8 s signal is P/2;
  - DBV SDSS J2037+1453; ZZA GALEX J2127-7258 and J1422-3323;
  - WD 0032-317 (WD + brown dwarf);
  - EB 2MASS J1358-3556;
  - the rest have CROWDSAP <0.1.
  - No new pulsator; lane closed as validation (131 download holes remain).
- **Gaia DR3 EB white-dwarf candidates, ATLAS** (`gaia_wd_periods_2026_09_24/eb_folds.png`):
  - 5310197547872256512: ~9.5 kK WD at 165 pc, ~9% sinusoidal modulation at P = 11.09 h (not the Gaia 22.2 h). The 1.9" neighbour is not Gaia-variable. Candidate magnetic/spotted WD; journal opened.
  - 6645284902019884928: GALEX eclipse in Rowan+2019, no period. ATLAS P = 4.069 h (the Gaia 11.42 h is an alias). SDSS-V: hot DA with narrow H-alpha emission. New PCEB period; journal opened.
  - 6216651490910555008: ELM candidate (Pelisoli+2019), ~12% modulation, P_phot 4.45 h; journal opened.
  - 4263036176971760768: too faint for ATLAS; ZTF check pending.
- **Hidden hot-DQ DB-outlier and faint scans:** finished (183 + 98 spectra). No carbon beyond the known 6466745168812781568.

## 2026-09-25 09:50 UTC: SMOKA data processed, carbon screen of non-DA classes, J2159 status

- **SMOKA MITSuME test (request P06USER0925100419FT):** 488 frames, checksum OK. Header TAN WCS agrees with Gaia to < 1 px. Differential aperture photometry of the 8.4 MG Zeeman WD 4307667617377160704 against 143 Gaia comparison stars (`docs/reports/smoka_2026_09_25/`).
  - Target S/N per 60 s frame: 2.3 (g), 2.7 (R), 0.7 (I); field stars of the same G have S/N 1-3. The data are too shallow.
  - Result: no period at 12-700 c/d; only modulations above about 20% are excluded, at 3 min-2 h.
  - The SMOKA search, request and retrieval route works end to end; this dataset does not constrain the target. Raw frames deleted; photometry kept.
- **Carbon screen v2, SnowWhite non-DA classes** (DB/DC/DZ/DQ etc.; 3,286 spectra, parallax/error > 3, S/N > 5; sample p99 6.65):
  - Known warm DQs recovered: WD 0916+028, the DQ 1558730836735094528 (6 visits), 1287258636998635008 (DQA), 6589369272547881856, 2087569060381096960.
  - Only 11/261 DQ-labelled spectra pass, mostly cool Swan-band DQs, for which the atomic-line templates are not built.
  - New warm-DQ classifications (journals): GALEX J213644.9-515758 (6465542891501713408, catalogued DC:) and GALEX J014648.4+400114 (343958710690034944, catalogued DB, in the Cheng+2019 massive-WD catalogue). Both show C I in two visits, M_G 13.15-13.17; no carbon classification found.
  - LSPM J2059+1334 (1758536430493058944, catalogued DB:) confirmed as a warm DQ.
  - DB hits at the -200 km/s window edge are He I leakage; 2821261624722089216 (DESI DB) and 6651133479247436032 (noise) are false positives.
- **J2159+5102:** no new data; status reviewed after the ZTF 2018-12-01 high-cadence null and the normal Gaia scatter.

## 2026-09-25 11:25 UTC: DESI DR1 carbon screen; TESS download holes explained; J2051 ATLAS

- **DESI DR1 carbon screen** (SPARCL; spectra retrieved by TARGETID; carbon_screen2 matched filter; scripts in `carbon_screen_sdssv_2026_09_25/data/`):
  - Sample: 10,191 Amorim+2026 massive DAs and DB/DC/DZ, plus 119 DESI DQ-class controls. DQA controls recovered 7/8; cool DQ 5/80, as expected for atomic templates.
  - 60 hits. After resolving true Gaia ids by position, every true carbon hit already has a Swan+2026 DAQ/DQA/DQ class; several are in Kilic+2026. 36 wrong ids came from rounded values in the Amorim file.
  - Swan-DA/DB/DC hits are He-line leakage, noise or window-edge artefacts. **Result:** DESI DR1 carbon WDs are fully catalogued; no new objects. Many carbon WDs carry an Amorim "DAH"/"DB(A)" label that Swan+2026 corrects.
  - 27 register rows (recoveries).
- **TESS strip scan holes:** the 131 were multi-sector data-validation obs_ids (e.g. s0002-s0072) misparsed as sector products. No per-sector 120-s light curve exists for them; they are not coverage gaps.
- **J2051 (6886051830805052288) ATLAS** (4,828 points): marginal 12.42 c/d (1.93 h, 0.8%, FAP 2e-5), not confirmed by ZTF (0.40%). Rotation above ~1% excluded at 0.1-72 h.
- **Rubin alert stream** re-checked 10:40 UTC: ALeRCE LSST newest lastmjd still 61235.419 (73 days without alerts).

## 2026-09-25 13:40 UTC: Gaia DR3 EB white-dwarf candidates, second ATLAS batch; lane closed

- 8 more of the 76 WD-locus Gaia DR3 EB candidates checked (all G < 18.9, away from the Magellanic Clouds).
  - 7 of 8 have a much brighter Gaia source (G 11.1-14.0) within 2.0-4.4 arcsec; ATLAS forced photometry there is dominated by the neighbour (chi/N 130-640), and the Gaia EB solutions are probably contamination.
  - The 8th (3999033225988190720; cool, M_G 14.3) shows only the 2 c/d ATLAS alias.
- Faint WD-locus Gaia DR3 EBs next to bright stars are mostly spurious. Criterion: a G < 15 neighbour within 5 arcsec flags a candidate as likely contaminated.
- The three first-batch signals have no bright neighbour:
  - 6645284902019884928: PCEB, 4.069 h;
  - 6216651490910555008: 4.45 h;
  - 5310197547872256512: 11.09 h; its 1.9 arcsec neighbour is of the same brightness and not variable in Gaia.
- Lane closed. Register rows for all 8.

## 2026-09-25 14:05 UTC: carbon screen of the remaining SDSS-V DA-type spectra: null

- Streaming screen (stream_screen.py: download, screen, delete) of 25,268 SnowWhite DA-type spectra with parallax/error > 5, S/N > 8, not in the massive or non-DA samples.
  - 18,303 on the WD locus (M_G > 9); p99.9 of the carbon contrast 9.35.
  - 91 hits above 8 in the velocity window ranked; the top ~12 inspected. All ordinary DAs: Balmer-wing residuals, noise, red-end artefacts, or visits that disagree. No carbon.
- Consistent with carbon in H atmospheres appearing mainly in massive merger remnants, which the massive-DA screen covered. The SDSS-V DR20 DA sample is now screened in full; 4 download holes.

## 2026-09-25 17:51 UTC: gaseous debris discs (Ca II triplet emission) in SDSS-V DR20 white dwarfs: setup

- **Prior art** (web search and ADS 2024-2026 abstracts):
  - DESI EDR searched: Ma+2025 (AJ 170, 345; arXiv 2510.25097), 22 weak candidates from 2,706 WDs.
  - DESI DR1 (Swan+2026, arXiv 2609.04314): no targeted search; 3 systems noted during classification.
  - Saker+2025 (RMxAA 61, 154) compiles the known sample. Bhattacharjee+2025 (PASP 137, 074202): one ZTF transit candidate with gas emission.
  - No SDSS-V DR19/DR20 gas-disc or DAHe search found; Adamane Pallathadka+2026 and Crumpler+2025 cover other topics. Lane opened.
- **Sample:** all 50,960 classified SnowWhite (snow_white_boss_star) objects. MS and CV classes included and flagged; the known gas-disc WD J2133+2428 is classed DA_MS.
- **Controls:** 8 known gas-disc WDs in DR20:
  - WD 0842+572, SDSS J0738+1835, WD J1930-5028, WD J2133+2428, WD J0529-3401, SDSS J0234-0406, WD 1622+587;
  - WD J0914+1914 (evaporating planet: H, O and S emission, no Ca);
  - plus 7 DESI EDR candidates.
- **First-pass matched filter** (cubic continuum, double-peaked templates): recovers 0842+572 (z 86), J0738 (33), J1930 (15), J2133 (14; visits 3.6 and 16.6, so variable) and J0529 (13). J0234 and 1622+587 not recovered. J0914 shows O I 8446 (z 16) and H-alpha (11).
- The random-sample null is biased (median 2.5, tail to 10) because DA Paschen lines lie within 20-75 km/s of the Ca II lines. Planned: a second pass with empirical photospheric templates (Teff/logg neighbours).
- The stream stores compact coadd regions plus per-visit H-alpha and CaT regions.

## 2026-09-25 20:08 UTC: SDSS-V gas-disc screen complete; two new gas-disc white dwarfs released

- **Stream finished:** 50,961 objects, 49,983 OK, 978 BADCAT (poor CaT coverage).
- **Pass 2** (neighbour-template subtraction), WD locus (parallax/error > 3, M_G > 8.5):
  - z_cat p99 / p99.9: 8.8 / 19.1 for DA-type (30,090); 14.7 / 27.6 for other WD classes; p99.9 38 (MS) and 78 (CV).
  - Poor-parallax DA-labelled A/F stars give unstable z (neighbour templates fail there); vetting restricted to the WD locus.
- **Control correction:** "WD J2133+2428" in the lane-start entry was box-matched to Gaia DR3 1797494017250709632 (WDJ213352.72+242747.79, DA_MS, G 15.94), which is the wrong star.
  - The Saker+2025 object is WDJ213350.72+242805.93 = Gaia DR3 1797494081674032512 (G 17.33, TeffH 26 kK), 28 arcsec away; it has no SDSS-V spectrum.
  - The DA_MS star's narrow CaT emission (visits 3.2 / 16.6) comes from its M-dwarf companion.
  - Corrected validation: 6 of 8 known Ca-emission gas discs in SDSS-V recovered (WD 0842+572, SDSS J0738+1835, WD J1930-5028, WD J0529-3401, WD J1829+4537, WD J2307-0002). Not recovered: SDSS J0234-0406, WD 1622+587 (S/N 4.7). DESI EDR candidates: 0 of 7.
  - Criterion: a control is identified by its full WDJ name, not by a Jhhmm+ddmm box match.
- **New gas discs** (journals):
  - WD 0856+048 (578709631539357440);
  - WD J1959+2208 (1827014701883095680): DB, double-peaked CaT, EW 17.8 and 26.6 A in consecutive visits.
- **ZTF:**
  - 0856: 69 r points, flat within 5%, no period.
  - J1959: about 4,000 points, no dips in 3 high-cadence nights. The formal 7.0245 c/d peak is incoherent across data sets and appears in comparison stars; not adopted.
- **Public release** (approved by the user; 5b5f0e2):
  - gas_disc_screen.py, gas_disc_epochs.py, ztf_lightcurve.py;
  - tables gas_disc_white_dwarfs, gas_disc_epochs, gas_disc_screen;
  - repository reorganised into docs/ topic pages, figures per object in figures/<topic>/.
- **Pending:** vetting of the remaining WD-locus hits (narrow single-peaked emitters 2527617665632689024, 422688489185463680, 191101206879480704; companions in MS/CV) and the literature status of the narrow emission in WD J2245+2016.

## 2026-09-25 20:41 UTC: SDSS-V DR20 visit-RV cross-check of the dark-companion candidate pools: no BH/NS verdict changed

- **Targets:** 27,555 Gaia DR3 ids:
  - roster 9; unified candidate list 17,760; DESI 23 + 15; Shahaf+2024 non-class-I 9,786; AMRF-III 306;
  - Gaia BH1/2/3 and NS1 as controls; none has an SDSS-V visit, so there is no BH/NS positive control.
- **Data:** CAS mwm_apogee_allvisit + mwm_boss_allvisit.
  - 2,158 targets with clean visits (1,334 with 2 or more nights).
  - Most APOGEE visits are SDSS-III/IV (3,054; already in DR17). SDSS-V adds 127 APOGEE and 2,296 BOSS visits (BOSS XCSAO about 3-10 km/s).
- **Orbit test:** 648 NSS orbits fetched. The TI-to-omega conversion validated against 48 AstroSpectroSB1 C/H omegas (agree mod 180 deg); SB1 catalogue K reproduced (e.g. 15.06 vs 15.12, 24.66 vs 25.82 km/s).
  - 52 well-constrained astrometric orbits: median R = |A|/K_pred(photocentre) = 1.04, mostly Shahaf+2024 systems. This matches the dark-companion expectation and validates the Gaia orbits; not a new finding.
- **Own candidates:**
  - Tier-1 NS 2127900555635640832 and 2129927539681151872: 2026-05-28 triage verdicts reproduced (APOGEE-2 visits).
  - Tier-2 3858881884705215232: R = 0.87 +- 0.06 from 5 visits over 37 d; consistent, but M2 ~1.24 is at the WD/NS boundary.
  - Tier-2 3369528356272086528: A star; APOGEE RVs unreliable; no constraint.
  - Roster: no new epochs for HD 157033; 1593152388271709824 has 2 epochs 7.7 yr apart (no constraint).
- **Not pursued:** Shahaf systems whose RVs disagree with the Gaia orbit:
  - 5585964306891994240 (R 0.13, chi2 428/4);
  - 1301730202881275008 (R 0.03 over 8 d near periastron);
  - AMRF-III 3868385307301381760 (R 2.07; luminous companion or triple).
- **Conclusion:** DR20 adds almost nothing for BH/NS: the highest-tier candidates lack SDSS-V visits, and BOSS precision is too coarse for K = 5-20 km/s. Decision: BH/NS work waits for Gaia DR4 (2 Dec 2026). Scripts and tables in docs/reports/rv_dr20_crosscheck_2026_09_25.

## 2026-09-25 21:33 UTC: LAMOST DR11 carbon screen (pass 1): null

- **Sample:** 7,096 LAMOST DR11 v1.1 WD-class spectra; 6,667 screened; 429 download holes being retried.
- **Contrast percentiles** (p99 / p99.9): C 5.7 / 10.0, C I 6.5 / 11.6, C II 6.0 / 11.4. 67 hits of 8 or more; 36 remain after removing He I leakage (He I < 5) and window-edge velocities.
- **Identifiers:** the catalogue's GaiaDR3 column is rounded (80% multiples of 256). Ids re-resolved by position; the gpID column matches for 34 of 36.
  - With true ids, 14 of the 36 hits have M_G 0.8-7: distant stars and sdBs labelled WD by LAMOST (e.g. 3330288469904253824, M_G 1.7).
- **Visual vetting:** all 24 hits with M_G > 8 or the highest contrast inspected.
  - Only the known DQA 1475194238223608064 shows carbon (recovery, positive control).
  - All others are ordinary DAs (Balmer-wing or window-edge artefacts) or noise.
- **Result:** no new carbon white dwarf in LAMOST DR11 (hole retry pending). Files in docs/reports/carbon_screen_sdssv_2026_09_25/lamost_dr11/.

## 2026-09-25 21:50 UTC: gas-disc screen, vetting of the remaining hits

- **Selection:** WD locus (parallax/error > 3, M_G > 8.5), H/nonH groups, z_cat > 10, z_cat > 2.5 x max(z_fake, z_abs), at least 2 lines above 3 and none below -1: 122 objects; the red ones (BP-RP > 0.7, M_G 8.5-15) are dominated by M-dwarf companions or M dwarfs.
  - The M_G > 8.5 cut admits M dwarfs; an additional cut M_G > 4.5 (BP-RP) + 7.5 is adopted for later runs.
  - 16 blue candidates plus 4 narrow emitters inspected.
- **New gas-disc candidates** (journals):
  - 2527617665632689024 (GALEX J0039-0356, DA 22.8 kK):
    - narrow Ca II triplet emission in all 4 visits (EW 23-49 A, variable; centroid -17 to -71 km/s);
    - no H emission;
    - WISE excess about 10x in W1 and 20x in W2 (LS DR10 deblended; neighbouring galaxies at 5-7.5 arcsec);
    - no other spectra, no literature.
  - 1764314497240770176 (SDSS J2054+1610, hot DA 27.5 kK):
    - narrow Ca II triplet plus strong O I 7774/8446 emission, no H emission;
    - first spectrum (SIMBAD: WD? only);
    - outside WISE/LS reach.
  - Neither shows H emission, which argues against irradiated companions and points to metal-rich (planetary) gas. Their narrow lines (FWHM 260-340 km/s) resemble WD J1829+4537 (Ma+2025).
- **Other candidates** (register):
  - 422688489185463680 (DB, Ca II + O I, fading 2020-2023, WISE excess flagged contaminated);
  - 191101206879480704 (massive DA, 1 visit);
  - five low-S/N possibles.
- **Companions, not gas discs:**
  - LB 567 = 3834895969825628800 (H-alpha emission);
  - WD J2245+2016 = 2833849800205759360: 0.28 Msun DA with WISE excess (Xu+2020), ZTF 3.9 h (Jestin+2026), Ca II + H-alpha emission; probable irradiated companion;
  - 3126919298834022528 (in the SDSS-V DR19 DA binary catalogue).
- **ZTF:** no dips or periods for 2527617665632689024 or 1764314497240770176; the faint outliers of the latter are at airmass 1.9-2.4 or have shallow limits.
- Not public; decision pending (user).

## 2026-09-25 22:37 UTC: LAMOST DR11 carbon screen complete: null

- **Holes:** the 429 were retried; 27 returned from v1.1. The other 402 were "Not Found" JSON bodies (HTTP 200, 159 bytes) at dr11/v1.1 but exist at dr11/v2.0; the fetch now falls back to v2.0. All 7,096 spectra screened.
- **Hits from the 429:** 9 at 8 or more: two He I leakage, five distant stars (M_G 3.0-3.6); the two catalogued DAs (203828633790026496, 1752156823511885184) are noisy ordinary DAs.
- **Result:** no new carbon white dwarf in LAMOST DR11; one DQA recovered. The carbon search is complete across SDSS-V DR20, DESI DR1 and LAMOST DR11.

## 2026-09-25 23:00 UTC: H-alpha emission and variability screens of the SDSS-V spectra: null

- **H-alpha variability** (halpha_screen.py; 11,768 WD-locus objects with 2 or more good visits): per-visit EW(+-40 A) chi2 and pair-profile chi2.
  - The top of the list is single-visit artefacts (cosmic rays, spikes) and continuum-normalisation effects in magnetic WDs.
  - The two known DESI DAHe in SDSS-V (3656469211440196736, 1428562506980546688; both SnowWhite "DC") are not outliers (chi2_ew 10-13): the method does not isolate DAHe.
- **Emission above the continuum** (runs of 3 or more pixels): weak for DAHe (3.3-3.8 sigma).
- **Balmer structure in 'featureless' classes:** chi2 about a quadratic over 6400-6750 A for 962 nonH-group objects on the DAHe locus; DAHe controls rank 14 and 83.
  - Top 12 inspected: a known magnetic DAP recovered (WD 1135+579, SnowWhite DC); two spectra with nebular H-alpha, [N II] and [S II] contamination; the rest single-visit artefacts or noise.
- **Result:** no new DAHe or DAe. A DAHe search requires Zeeman-emission templates. Parked.

## 2026-09-26 00:09 UTC: DESI DR1 gas-disc screen (44,302 spectra)

- **Method:** all Amorim+2026 DESI DR1 WD TARGETIDs streamed via SPARCL; 116 bad spectra; positive control WD 0856+048 stored first and last. SDSS-V pass-2 method applied with Amorim colours/M_G and classes.
  - z_cat p99.9: H 14.3, nonH 12.5, MS 38, CV 104. DESI is cleaner than SDSS-V at CaT.
- **Recoveries:** WD J1829+4537 (39.7), WD J2307-0002 (14.7), WD 0856+048 (12.3), WD J0857-2245 (9.2). EDR candidates WD J0842+2300 (9.1) and J0719+4021 (8.1) weakly above 8; the other EDR candidates 3.6-4.8.
- **46 candidates** (z_cat > 8, ratio > 2.5, 2 or more lines above 3). Swan DR1 classes remove 20 WD+MS, 1 CV and 2 STAR. Among Swan DA/DB, 4 show H-alpha emission and are overluminous: irradiated companions, registered.
- **New:**
  - WDJ1448+3225 (1283510882895711872, DBA): double-peaked Ca II emission in BOSS 2010, DESI 2021 and DESI 2022 (EW 19-37 A), persistent over 12 years. Journal.
  - WDJ1611+4017 (DA): weak emission in DESI 2021 (5.9 +- 0.4 A) and BOSS 2012 (3.5 +- 1.1 A).
  - WDJ0957+4241 and WDJ1745+5838: possible.
- Not public; decision pending (user).

## 2026-09-26 00:50 UTC: gas-disc Ca II emission timelines (population): setup

- **Prior art (ADS 2012-2026):** single-object variability studies exist (SDSS J1228 precession, SDSS J1617 fading, HE 1349-2305 rapid evolution). The closest population work is on dust, not gas: Noor+2025 (MNRAS 543, 1602, "Activity in white dwarf debris discs I", Spitzer) and Guidry+2024 (WISE 3.4 um). No population-level Ca II gas-emission timeline found. Lane opened.
- **Targets (32):**
  - 19 established gas discs, resolved via Sesame WD/HE names, Melis+2020 coordinates plus GF21, or verified Gaia ids;
  - 7 more from DESI and recent papers: WD J1829+4537, WD J2307-0002, WD J0857-2245, WD J1930-5028, WD J0529-3401, WD J2212-1352, WD J2133+2428 (true id 1797494081674032512);
  - the 6 found in this project.
- **Sources:** SPARCL (SDSS/BOSS/DESI), SDSS-V visits, LAMOST DR11 (local WD catalogue, 3 arcsec), ESO X-shooter VIS and UVES red arm (phase 3). Per spectrum: EW of the three lines with the gas_disc_epochs normalisation, S/N, Gaussian centroid and FWHM.
- **Test** on 3 stars: SDSS J1228+1040 has 43 spectra over 2003-2025 (EW 55-79 A). Two 2026 X-shooter products fail to read (probably still proprietary), logged as holes. Full run in progress.

## 2026-09-26 01:18 UTC: gas-disc timelines: first population result

- **Data:** 32 stars, 414 spectra, 2000-2025.
  - Holes: 29 X-shooter products from 2025-26 are empty (proprietary; these stars are still being monitored), plus 9 BITPIX-16 products.
  - QC (continuum median within 5%, continuum robust rms 0.25 or less, S/N 3 or more, error outliers) leaves about 350 spectra.
  - Errors include a 10% + 1 A floor for cross-instrument systematics.
- **Result:** of 25 stars with 3 or more spectra spanning a year or more, 9 vary significantly (chi2r > 3 and max-min > 3 sigma):
  - WD J2133+2428: 12.2 -> 1.0 -> 5.4 A over 2022-2025, X-shooter;
  - WD 0856+048: onset after 2010;
  - SDSS J0845+2257: about 21 -> 6 A over 2005-2024;
  - GALEX J0039-0356;
  - SDSS J0738+1835;
  - SDSS J1617+1620: the known fading is recovered;
  - WD J2212-1352;
  - Gaia J0611-6931: 2021 spike, consistent with Rogers+2025 weeks-scale variability;
  - SDSS J0959-0200 (weak; one negative outlier).
- **Steady, 16:** among them SDSS J1228+1040 (about 65 A over 22 yr), J0006, J1930, J1829, J2307. SDSS J0347+1624 rises about 21 -> 35 A over 2020-2024 but is borderline under the floor.
- **Next:** per-object literature check of which changes are already reported; a structure function; an onset search in polluted WDs with 2 or more epochs.

## 2026-09-26 02:26 UTC: gas-disc timelines: literature check, structure function, onset search; by-product binary

- **Literature check** (ADS aliases and arXiv sources of Dennihy+2020, Melis+2020, GF21, Rogers+2024 I/II):
  - Already published: J1617, J0845 (low state continues to 2024), J0959, J2212, J0347 (rise).
  - Retracted from the variable list:
    - SDSS J0738+1835: its photospheric Ca II triplet absorption confounds the EW window; the profiles look the same at every epoch.
    - Gaia J0611-6931: the 87 A value is from a poor spectrum (S/N 18, continuum rms 0.15). Otherwise it rises slowly from 48 to 57 A between 2019 and 2023.
  - WD J2133+2428 switch-off: 10.5 -> 1.3 -> 0.8 A (2022-05, 2023-05, 2025-05) after removing cosmic-ray spikes; the raw 2025 value of 5.4 A was spikes. The data come from two monitoring programmes (Manser 109.2383; Ramirez Ramirez 115.27XT); the result belongs to the programme owners and is registered, not claimed.
  - Correction: the earlier note "J0611 consistent with Rogers+2025 weeks-scale variability" is not supported; ADS has no such Rogers+2025 paper for J0611.
- **Structure function** (14 stars, 1,424 pairs): median fractional EW change per star about 4% within days and about 19% over 1-10 years. Factor-of-several changes are confined to J1617, J0845, WD 0856+048 and J2133.
- **Onset search: null.**
  - SDSS-V per-visit on/off: 80 candidates, 16 inspected, 0 onsets.
  - SDSS-V x DESI: 10,379 pairs, 74 formal switches, 13 re-measured template-free in every epoch: 0 new.
  - Recoveries: WD J0234-0406, WD J0857-2245 (still faded), WD J0842+2300 (weak, 0.7 A).
  - Criterion: per-visit matched-filter z at SDSS-V S/N is dominated by single-visit spikes; a switch is accepted only with a template-free EW in every epoch plus a profile plot.
- **By-product: Gaia DR3 3107374277060584064** (WDJ064438.09-004550.51, G 17.27, 550 pc).
  - Hot white dwarf (He II 4686) with an irradiated companion, P = 0.592887 d, maximum light at BMJD 59300.28308.
  - The period is present in the CoRoT IRa01/LRa01/LRa06 light curves (2007-2012), Gaia DR3 (spurious-signal diagnostics, GLS 1.68667 c/d) and ZTF (2018-2024); the cycle count is secure.
  - The r amplitude (11%) is larger than g (4%): reflection.
  - SDSS-V H-alpha, H-beta and Ca II emission velocities follow the companion's orbital phase; no emission near minimum light.
  - Ferreira Lopes+2025 assigned the CoRoT period to the 4.1" F8 IV neighbour, which is constant in ZTF.
  - Novelty check clean (SIMBAD, MWDD, VSX, VizieR, ADS, DESI, LAMOST, ESO, mwcheck).
  - Journal created. VSX revision drafted, not filed. Report: docs/reports/pceb_3107374277060584064_2026_09_26/.

## 2026-09-26 03:14 UTC: gap-fill of the 2026-09-24 Gaia-period lane: 2 new periods, 3 recoveries
- **Trigger:** the reflection binary 3107374277060584064 was in the 2026-09-24 input (FAP 1.4e-5) but was not tested. Two causes: the tier-2 M_G > 9.5 cut dropped hot, bright white dwarfs, and every star listed in Jestin+2026 was treated as known, although Jestin marks it "Variable False".
- **Selection** (select_gap.py): 55 untested stars at FAP < 1e-3 (north, not in Steen). After removing Jestin-confirmed stars and VSX periods, 13 were tested with ZTF at the Gaia frequency.
- **Selection criterion:** catalogue members are excluded by the catalogue's verdict, not by membership. Jestin+2026 "Variable False" stars: 4 of 4 have their Gaia frequency as the top ZTF peak.
- **Results:**
  - **New periods:**
    - SDSS J1022+1611 (3890059941364406144): 87.33 min. A 0.32 Msun low-gravity DA; the r amplitude (4.6%) is 2.6 times the g amplitude. Candidate: reflection off a substellar or late-M companion. Journal created.
    - GALEX J0037+1901 (2795150147707769728): 18.241 h, achromatic 3%, in a 1.08 Msun hot DA (likely rotation). Journal created.
  - **Recoveries:**
    - 3138305596433476480 and 2208250945549692672 (Ranaivomanana+2025 A&A 704 A70);
    - GALEX J0751+1059 (Reindl+2023, reflection 6.64 h).
  - **Not confirmed:** 2 faint stars; 1 hole.
- **Prior-art sources for hot white-dwarf periods:** Reindl+2023 (bright hot pre-WDs, photometric-variable table) and Ranaivomanana+2025 (693 A268 and 704 A70).
- **Catalogue access:** the invalid VizieR catalogue id J/A+A/677/A29 returns an all-table cone without an error. VizieR J/ApJ/967/166 returns nothing even for a Steen member; Steen+2024 membership is checked via the arXiv source.
- **Filing:** VSX revision drafts prepared for all three new periods (including the PCEB); not filed.

## 2026-09-26 04:42 UTC: gap-fill, part 2: weak Gaia periods (ZTF) and southern hot white dwarfs (ATLAS)
- **ZTF, 77 stars** at Gaia FAP 1e-3 to 5e-2 (north, not Jestin-confirmed, not tested before). IRSA timeouts were re-run; 1 hole remains (974895286283420160).
  - 7 confirmed (the Gaia frequency is the top ZTF peak).
  - 5 recoveries: PHL 1016 (Steen+2024), WD 0831+537 (Steen+2024), PB 6015 = SDSS J0032+0739 (Liu+2024), J0606+2507 (Chen+2020), J2215+2530 (Ranaivomanana+2025).
  - 2 new periods, journals created:
    - 3123625093275668736 (WD 0.35 Msun + 2800 K M dwarf, Rebassa-Mansergas+2025): 10.393 h, red-enhanced, probably the orbital period of a post-common-envelope binary.
    - 3354819845628139904 (hot subdwarf candidate, J0659+1547): 12.589 h.
- **ATLAS, southern hot white dwarfs without any period:**
  - New periods, journals created:
    - GALEX J1322-4224 (6136817910121524096): 18.456 h, larger in c than o.
    - Gaia DR3 6170660401283991680, a 138 kK DO: 27.0 h, larger in c than o. Not in the Reindl+2021 UHE paper, Reindl+2023, Steen or Ranaivomanana.
  - 2 stars pending: the ATLAS server was unreachable.
- GALEX J1739-6439 (Gaia period known): its SDSS-V spectrum shows H-alpha, H-beta and Ca II emission from an irradiated companion. Registered.
- **Tally for the gap-fill:** 7 new periods (J1022+1611, J0037+1901, J1322-4224, J1400-3302 (DO), J0618+0115, J0659+1547, plus the PCEB found via SDSS-V) and 8 recoveries. The literature check (Steen, Liu, Chen, Ranaivomanana) identified 8 known periods not found by a SIMBAD/VSX check.
- **Addendum:** the last two southern ATLAS stars, GALEX J105228.9-295308 and 4658259853535794432 (LMC field, blended), are both recoveries. Their periods are in live VSX but were missing from the cached cand_annot VSX flags. Final novelty verdicts use a live VSX query. Final gap-fill tally: 8 new periods (including the PCEB), 12 recoveries.

## 2026-09-26 10:55 UTC: correction: reflection-binary ephemeris (CoRoT time zero point)
- **Error:** the joint CoRoT + ZTF ephemeris for 3107374277060584064 converted CoRoT DATEBARTT as MJD = DATEBARTT + 51544.5. DATEBARTT is BJD - 2400000, so the CoRoT times were 51545 d off.
- **Corrected** (scripts/reflection_3107374277060584064.py): P = 0.59288582 d (was 0.59288695 d). The nearest cycle-count alias is at delta chi2 81066 (chi2 per point 62); all data sets from 2007 to 2024 are in phase within 0.02 cycles.
- **Unaffected:** the per-run CoRoT detections, ZTF, Gaia, the emission-velocity phases (ZTF-based) and the eclipse null.
- **Updated:** journal, report README and VSX drafts.
- **Check:** the CoRoT start 2007-02-03T13:05 UTC gives DATEBARTT = 54135.05, which is JD - 2400000.

## 2026-09-26 10:57 UTC: public release of the new periods and the reflection binary
- **Decision (user):** public release approved.
- **Public repository commit 0279cb1:** the reflection binary 3107374277060584064 (script, tables, two figures) and seven new white-dwarf periods added to the periodic table. The table gains per-filter ZTF rows (values for the earlier stars are unchanged), and J1022+1611 gets a TESS FFI table.
- **Not pushed:** the gas-disc timeline results (population measurements, not new objects); the WD J2133+2428 switch-off in those results uses another team's monitoring data.

## 2026-09-26 12:22 UTC: four outlier searches in stored SDSS-V spectra (double WDs, two-faced, lithium, anomalous spectra)
- **Prior art (ADS):**
  - SDSS-V DR19 double white dwarfs, arXiv:2509.02906: sub-exposure RVs, 63 candidates. Its 66 Gaia ids are used as controls and as the front-filter.
  - Two-faced white dwarfs: Janus (2023) and a magnetic double-faced DBA (Moss+2024).
  - Lithium in white dwarfs: Kaiser+2025 (ApJ 979, 111) and earlier.
  - J-PLUS outlier analysis (Lopez-Sanjuan+2025).
- **Double WDs:**
  - H-alpha RVs per visit against each star's own coadd: 9,599 DA WD-locus stars with at least 2 visits; 257 formal candidates.
  - The H-alpha-only shifts are mostly artefacts: night-sky residuals land near H-alpha at different wavelengths per visit, because the XCSAO undo shifts them.
  - Three-line consensus (H-alpha, H-beta, H-gamma; at least 2 agreeing) over 298 stars. Large visit offsets are 67% in_stack=False visits (base rate 11%), and several equal that visit's XCSAO velocity. in_stack=False visits are also shifted and are excluded from RV measurements.
  - In-stack only: 11 candidates pass. 6 of them show several varied velocities with about 10 km/s errors and are registered: SDSS J2057+1650, 2190010593106909568, 2153427951457223040, 3185643733834595456, SDSS J0736+1618, 2QZ J1410-0234. The rest are single-visit outliers and remain suspect.
  - Sensitivity: 9 of 52 DR19 candidates recovered across visits.
- **Two-faced:** null. The per-visit H-alpha / He I EW variability is dominated by the same sky residuals and by H-alpha-wing normalisation; the top 12 are artefacts.
- **Lithium:** parked, not null. The Li 6708 depth screen does not recover LHS 2534, the only known Li-polluted WD in SDSS-V (magnetic, 2.1 MG, noisy); the top hits are noise or a corrupted plate (8831xxxx).
- **Anomalous spectra** (PCA + 10-nearest-neighbour chi2; 5-pixel median filter; winsorised residuals):
  - The top ranks are sky-subtraction residuals (8250-8950 A) and single-visit problems:
    - a fibre mix-up with an emission-line galaxy (109698692);
    - a broken blue/red join (GALEX J1714+6849);
    - contamination by a G 9.2 companion 4" away (4584823991592186880).
  - One astrophysical outlier: WDJ0605-5050, a heavily polluted DZ with K I, previously DC:. It is already a Gaensicke X-shooter target (114.27DZ.001); registered only.
- Report: docs/reports/sdssv_fun_outliers_2026_09_26/.

## 2026-09-26 13:24 UTC: outlier follow-ups: per-exposure RVs, extra epochs, hot-star model fits
- **(a) BOSS per-exposure RVs** (spec-full files, independent of Astra XCSAO; commit 3df69ca):
  - SDSS J2057+1650 (1764456441613885952): RV-variable, +38 to -29 km/s over a week (chi2r 8.2); three lines agree. Journal created.
  - WDJ0437-0857: variable, but a known CV in MWDD.
  - 2190010593106909568: unreliable (G 9.85 star 5" away).
  - 2153427951457223040: constant.
  - 2QZ J1410-0234: not variable in reliable exposures.
  - SDSS J0736+1618: inconclusive.
- **(b) SPARCL extra epochs** (sparcl_epochs.csv): one usable epoch, DESI 2022 for WDJ0437-0857 (-116 km/s). The other SDSS/BOSS/DESI spectra give inconsistent line velocities.
- **(c) Hot-star fits** (hot_fits/): TheoSSA TMAP H+He grid, 280 models, 60-200 kK.
  - **Balmer lines:** reproduce the Balmer-line problem (median fit/literature 0.75).
  - **He I + He II only:** median 1.04, 16-84% 0.87-1.39 on 10 controls with S/N >= 19. Controls at S/N <= 15 fail.
  - **No published spectroscopy:** six stars (MWDD, VizieR all-table, SIMBAD refs, ADS full text, SPARCL, SDSS specObj all checked) are DAOs with SDSS-V first spectra: J0550-1554 ~110 kK, J0629-4158 ~100, J0814+0225 ~90, 4036084504408126976 ~90, J1906-7558 unconstrained, and WDJ0958-1758 (weak He II; a known 3.27 d variable) unreliable.
  - **Already published:** three stars previously taken as unclassified. SALT J1740-7214 and SALT J1723-6725 are O(He) stars at 140 and 130 kK (Jeffery+2023, arXiv:2301.03550), and GALEX J2044-0256 is a DAO at 92.5 kK (MWDD).
  - **Correction:** the hottest star in the sample with a published value is SALT J1740-7214 (140 +- 15 kK), not PN Lo 1 (118 kK). The earlier literature compilation used SIMBAD measurement tables, which lack the Jeffery+2023 values.
  - No new star is credibly hotter.
- All nine hot stars registered (lane sdssv_hot_fits_2026_09_26).

## 2026-09-26 14:11 UTC: public release of the six hot DAO white dwarfs
- **Decision (user):** public release approved.
- **Public repository commit e76c647:** the six DAOs whose SDSS-V DR20 spectra are the first found (J0550-1554, J0629-4158, J0814+0225, 4036084504408126976, J1906-7558, WDJ0958-1758). The commit contains:
  - page docs/hot_white_dwarfs.md;
  - script scripts/hot_white_dwarfs.py, which downloads the TheoSSA grid and reproduces all 36 local fits exactly;
  - table tables/hot_white_dwarfs.csv;
  - star list and grid list in data/;
  - two figures.
- **Correction:** the "Fleury+2024" reference in hot_fit_summary.csv is Filiz et al. 2024 (A&A 691, A290), verified in ADS.
- **Downloads:** the eight 200 kK grid files first came back as VOTable; re-downloaded as text, the spectra are identical (maximum difference 0).

## 2026-09-26 15:10 UTC: rating wording removed from the documents
- **Decision (user):** wording that rated results by publication potential was removed from CANDIDATES.md, this log, three dossiers, three object journals, and eight reports and notes. Facts, verdicts, references and prior-art citations are unchanged.
- Archived input scripts (precovery_campaign_2026_07_07/workflow_scripts/*.mjs) keep their original wording, because they produced recorded outputs.

## 2026-09-26 15:21 UTC: GitHub push: 108 local commits squashed into f88296d
- **Decision (user):** push approved.
- The local history since 2026-09-22 (108 commits) was squashed into one commit on top of the last pushed commit and pushed. The unsquashed history is on the local branch backup/local-history-2026-09-26 (not pushed). Local commit hashes cited earlier in this log (for example 3df69ca and 5cd730a) are on that branch.
- Before the push:
  - Absolute local paths were replaced: ~ in text, os.path.expanduser in Python, $HOME in shell. All 91 changed Python files compile, and each imports os before first use.
  - The contact email was replaced by os.environ["CONTACT_EMAIL"] in scripts and by <email> in text.
  - Credential scan: none in the pushed tree.
- Not changed:
  - scripts/known_objects/README.md and ingest_vsx.py still hold local paths (edits in progress).
  - Earlier GitHub history keeps the old paths and email; removing them would need a force-push.

## 2026-09-26 16:28 UTC — Log and journal wording
- This log and 37 object journals were rewritten in neutral wording. Dates, identifiers, measurements, verdicts, corrections and references are unchanged; per section, the headings and table rows are the same.
- The journal subtitle line is now "Append-only." in all journals, in the template and in scripts/journal/journal.py.
- The SMOKA request id is masked as P06USER0925100419FT, and the checksum file was renamed to request.md5.
