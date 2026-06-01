# Candidates

Authoritative list of objects currently in the discovery queue, with the
evidence that produced each verdict.

## Backing data (machine-readable)

| File | Pool | Rows |
|---|---|---:|
| `data/derived/main_hunt_derived_v2.parquet`         | v2 production: NSS Orbital + AstroSpectroSB1; G ≤ 13, plx ≥ 1.0 mas, 100 ≤ P ≤ 3000 d, significance ≥ 12 | 56,100 |
| `data/derived/main_hunt_derived_v2_relaxed.parquet` | Relaxed producer: G ≤ 15, plx ≥ 0.5 mas (mostly faint AstroSpectroSB1)                                  | 71,346 |
| `data/derived/main_hunt_derived_v2_alt.parquet`     | OrbitalAlternative + OrbitalAlternativeValidated channel                                                |    629 |
| `data/derived/acceleration_v3.parquet`              | NSS Acceleration channel (P-degenerate compact-object candidates)                                       | 16,949 |

Per-target columns include: `source_id`, `nss_solution_type`, `P_d`, `e`,
`significance`, `M2_msun_v2`, `sini_implied_v2`, `tier_v2`, `class_v2`,
all four filter verdicts + reasons.

## Headline

| Bucket | Count (M_1-corrected) |
|---|---:|
| **Confirmed (independent 2-channel)** | **0** — 3155543 downgraded to candidate on re-verification (external RV is 2 phases / 2.66σ); CRTS J051419 retracted. Firmly-confirmed binaries = the SED-based WD systems only (next two rows). |
| **Confirmed double-degenerate (WD+WD), sub-Chandrasekhar** | **2** — WG 26 (novel identification) + WDJ205650 (**already published**: Munday+2024, DBL Survey I) |
| **WD + unresolved massive companion** (M_total > M_Ch; *long-period* DD or WD+NS — **not** a super-Chandra WD, **not** a Type-Ia progenitor; see 2026-05-31 framing note) | **2** — WDJ020915 (M_tot≈2.04, P=275 d), WDJ060042 (M_tot≈1.98, P=935 d); both novel, companion WD-vs-NS unresolved, both need RV |
| Strong candidate | **1 — HD 264291** (Gaia DR3 3378588057203660160): RV-confirmed orbit + Shahaf P(compact)=0.75, M₂≈2.0 (heavy NS / lower mass-gap); caveats — known Shahaf object, Ap-star primary. The 3 former "strong" (5406907 / HD 157033 / 5858574) were all downgraded on re-verification. |
| **Tier-1 NS pool** (after M_1 correction) | **160** (was 291 at fixed M_1=1.5; 131 demoted to WD/low-mass at real M_1). **F#33 (2026-05-31) down-tiers a further 79 AstroSpectroSB1 + 1 BH** whose Gaia NSS period is flagged non-significant (flags bit 13) → "Tier-2 (period non-significant)"; raw-v2 Tier-1 NS parquet count drops 277→198. |
| Tier-1 BH pool | **0 STRONG** — 5406907 downgraded to weak/suspect (orbit DPAC-rejected + Gaia RV non-detection); HD 157033 BH-claim now ambiguous (0.4–6 M⊙) |
| Tier-2 (RV-inconclusive) | 426 (after M_1 correction; was 958) |
| v3 Acceleration P-degenerate compact-object | 10,818 (not yet M_1-corrected) |
| Demoted / falsified after 2nd method | ~32 named |

> **⚠ UNCONFIRMED — follow-up embargo (2026-05-31).** The genuinely-novel candidates in this catalog are **astrometric/SED candidates only — not second-method-confirmed and not published** — pending a clean RV epoch (and HST/COS FUV for the WD-vs-NS question). Treat as preliminary; **do not cite as confirmed discoveries**:
> - **WG 26** (6092654861665006592) — novel sub-Chandra double-WD (companion class SED-decided; orbit RV pending)
> - **WDJ020915** (332248057157474176) — novel long-period M_total>M_Ch DD/WD+NS (mass provisional — weak DR3 orbit F2=+8.4 → awaits DR4)
> - **WDJ060042** (2909342818326298112) — novel long-period M_total>M_Ch DD/WD+NS (companion WD-vs-NS unresolved)
> - **UCAC4 313-025977** (5612039087715504640) — novel ~15 M_J brown dwarf (astrometry-only, inclination-degenerate)
> (The novel astrometric triples HD 75567 / TYC 4562-535-1 / 5858574810404752256 are likewise unpublished but triple-favored, not compact — already flagged as such below.)

> **M_1 systematic correction (task LL, 2026-05-28)**: the bulk cascade originally derived M_2 at a fixed primary mass M_1 = 1.5 M_⊙. The photocentric mass function f(M) = M_2³/(M_1+M_2)² is invariant, so M_2 scales with the assumed M_1 — overestimated for WD/M-dwarf primaries, underestimated for A-star/giant primaries. Re-solving with the actual primary mass (Gaia FLAME for 74% of sources, StarHorse/TIC/GF21/Kervella for the rest) re-tiers **665 of 1251 candidates**. The Tier-1 NS pool collapses from 291 → 160. **All four headline dormant candidates survive** (3155543 NS holds at M_1=1.67; 5406907 BH holds at M_1=0.82, M_2=4.02; 5858574 strengthens at M_1=2.07, M_2=1.75; HD 157033 unaffected — no NSS row). Corrected catalogs: `data/derived/*_M1corrected.parquet`. Root-cause fix applied to `consumer_v2.py::select_m1()`.

> **⚠ SURVIVOR RE-VERIFICATION (2026-05-28).** Independent re-analysis of the named compact-object survivors (`scripts/survivor_revet_2026_05_28.py`, `scripts/survivor_verify.py`), applying the rigor that falsified the CV avenue, **downgrades all four — none holds at its prior "confirmed"/"strong" label.** The cascade *masses* are sound (audited, validated on Gaia BH2); these are real Gaia binaries, but their headline classifications were overstated:
>
> | Object | Was | Now | Why |
> |---|---|---|---|
> | 3155543 | CONFIRMED NS (2-channel) | **Candidate (NS-mass)** | Gaia AstroSpectroSB1 (sig 40.7, M₂≈1.3) is solid, but the *external* LAMOST "confirmation" is only 2 distinct phases at 2.66σ; the dossier χ²=0.36 was a 2-point free-ω overfit. Strong Gaia binary, weak external corroboration. **Also carries Gaia NSS flags bit 13 (NO_SIGNIFICANT_PERIODS) → F#33 flags it (period astrometrically supported, so not fatal — but a further caution).** |
> | 5858574 | (candidate) | **Triple-favored — demoted** (2026-05-29) | AMRF P(compact)≈0.21–0.35 → likely inner MS pair; the "mass-gap BH 2.8" was a sin-i error → M₂≈1.5–1.6; no archival RV. |
> | HD 157033 | STRONG BH | **Ambiguous (0.4–6 M⊙)** | Real companion (Gaia RV p=1.8e-15, Kervella snrPMa 14.85, APOGEE 3-visit scatter 35.7 km/s), BUT APOGEE RVs are suspect for this hot A9/F0 star (Chi2RV=7.9, spurious [Fe/H]=−1.45); Kervella face-value M₂=0.45; ruwe=0.85 (no astrometric orbit). Mass unconstrained between M-dwarf and BH — needs one clean optical RV. |
> | 5406907 | STRONG BH | **Weak / suspect** | Single OrbitalAlternative solution (DPAC-rejected from Validated, max\|corr\|=0.98). For P=25 d / M₂≈4 (K₁~100 km/s) Gaia shows NO RV variability (rv_amplitude_robust NULL, RV 2.34±4.12 over 27 transits) — the orbit itself may be spurious. The dossier's "rv_chisq_pvalue=0 corroboration" was incorrect. |
>
> **Net: 0 confirmed/strong compact objects remain.** The only firmly-confirmed binaries are the SED-based WD systems — two double-degenerates (WG 26, novel; WDJ205650, already in Munday+2024) plus two novel long-period (P≈275, 935 d) double-degenerate / WD+NS binaries with total mass above the Chandrasekhar mass (WDJ020915, WDJ060042; companion class unresolved — **not** super-Chandra WDs and **not** Type-Ia progenitors, see the framing-correction note below). The dormant-NS/BH list is now a set of *candidates*: the one that survives the triple-vs-compact test is **HD 264291** (RV-confirmed heavy NS — but a known Shahaf+2023 object); 3155543 (NS-mass, weak external RV) and HD 157033 (ambiguous 0.4–6 M⊙) remain candidates; 5858574 is now triple-favored (demoted). All novel candidates need a clean external RV to advance.

> **⚠ NSS period-confidence filter (F#33, 2026-05-31).** A QA audit found the producer never pulled the Gaia DR3 `nss_two_body_orbit.flags` bitmask, so bit 13 = `NO_SIGNIFICANT_PERIODS_CAN_BE_FOUND` (Gaia's own "period confidence below threshold") was never applied. It is set on **49% of all AstroSpectroSB1** solutions (Bashi+2022 drop ~half for a clean sample) and ~14% of high-f(M) pure SB1. Because the companion mass scales with the period, a non-significant period makes f(M) unreliable. **F#33** now hard-FAILs pure SB1/SB1C with bit 13 (period is spectroscopic-only) and down-tiers AstroSpectroSB1 with bit 13 to **"Tier-2 (NSS period non-significant — needs corroboration)"** (the astrometric orbit still constrains the period). Re-derivation (all `data/derived/main_hunt_derived_v2*` parquets, with new `flags`/`filter33_v2`/`nss_period_nonsignificant` columns + re-tiered) moves **79 Tier-1 NS + 1 Tier-1 BH → Tier-2**; the raw-v2 Tier-1 NS count drops 277→198. **3155543** (AstroSpectroSB1, sig 40.7) carries bit 13 → flagged (a further caution on an already-downgraded candidate; period is astrometrically supported, so not fatal). The RV-led spectroscopic-f(M) probe's two SB1 "survivors" both fail this cut (one bit-13 → F#33 FAIL, one sig=12.5 < the SB1-chain sig>40 clean line). Refs: Gaia DR3 datamodel; Bashi+2022 (MNRAS 517,3888); SB1 chain (arXiv:2410.14372). Audit: `/tmp/sb1_flags_audit_2026_05_31.md`. (`compact_object_candidates_unified.parquet` is a separate curated schema — regenerate downstream of these.)

> **⚠ WD-binary framing correction (2026-05-31).** A full-Thiele-Innes-covariance Monte-Carlo mass re-analysis of the two "Pile E" massive WD-primary binaries (WDJ020915, WDJ060042) corrects the earlier **"super-Chandrasekhar Type-Ia-progenitor candidate"** label, which was overstated two ways. **(1) Not super-Chandra *white dwarfs*:** the refined *companion* masses are M₂ = 1.32 [1.27–1.38] (WDJ020915) and 1.37 [1.23–1.52] (WDJ060042) — both just *below* 1.4 M⊙, with P(M₂>1.4) = **8.6%** and **41%**; M_total > M_Ch (≈2.04, 1.98) holds only trivially (~0.6 + ~1.3). **(2) Not Type-Ia progenitors:** at P = 275 d and 935 d the GW inspiral time ≫ a Hubble time → these wide systems **do not merge**, so the double-degenerate Type-Ia channel does not apply (the known M_total≥1.4 DWDs are all short-period, < 1.2 d, *because* merging is the selection). **Honest reframing:** novel **long-period (P≈275–935 d) detached double-degenerate (WD+WD) or WD+NS binaries with M_total > M_Ch** — a wide-orbit massive-WD-binary regime that spectroscopic DWD surveys cannot reach (longest catalogued DWD period ≈30 d; only ~3 M_total≥1.4 DWDs known, all short-period) and that is uniquely accessible to Gaia astrometry. Companion class (cool WD vs dormant ~1.3 M⊙ NS) is SED-**indistinguishable** (no UV/optical band breaks it; K₁ is identical for both classes, so even RV won't decide it — needs HST/COS FUV). **Caveats:** WDJ020915's astrometric orbit is a poor Keplerian fit (goodness-of-fit F2 = +8.4) → its mass awaits Gaia DR4 confirmation; **no optical RV spectroscopy exists** for any of the three (verified MAST/SDSS 2026-05-31 — WG 26 has only HST/COS FUV). Novelty re-locked vs the SDSS-V DR19 DWD catalog, Munday CloseDWDbinaries (314 systems), SPY, and DBL I/II — all clear. Deliverables: `/tmp/wd_novelty_lock_2026_05_31.md`, `/tmp/wd_sed_mass_refinement_2026_05_31.md`, `/tmp/wd_rv_observing_plan_2026_05_31.md`.

> **⚠ Post-2.2.0 avenue sweep (2026-05-31) — every accessible archival channel exhausted, all null for a novel dormant compact object.** A closing sweep of the remaining mineable channels, to establish the DR3-era null as robustly as the data allow:
> - **Isolated dark lenses (Gaia DR3 `vari_microlensing`, 363 events):** mass-blind in DR3 (no π_E/θ_E until DR4); the long-t_E dark-remnant tail is already published (Kruszyńska+2024, 11 candidates). Null.
> - **Spectroscopy-first high-f(M) SB1 not in Gaia NSS — all four major RV surveys:** APOGEE DR14/17 (+ Wu & Hawkins 2024's independent null on full DR17), SDSS-V DR19, DESI DR1, LAMOST DR11 MRS. Clean-fit non-NSS SB1 cap at f(M) ≈ 0.5–0.6 (below the NS threshold); every BH-regime outlier was pipeline noise (low-S/N or blue-vs-red band split — the RAVE-noise pattern). DESI DR1 epoch RVs are not reachable via Astro Data Lab (coadd-only; per-exposure `rvtab` is NERSC-bulk). LAMOST DR11 (VizieR `V/162`, per-epoch MRS RVs, Gaia-DR3-keyed) independently **corroborates HD 264291** (P=1035 d ≈ astrometric 999 d, χ²/dof=0.61, M₂≈1.5–1.8) — the known Shahaf object, not novel. Null for novel objects.
> - **El-Badry blind-spot gap analysis:** ~0 of our compact-favored candidates fall in the El-Badry et al. dormant-BH selection's *excluded* region — we sit **inside** their well-searched space, and their NS catalog + BH1/BH2 land in our Tier-2/Demoted pool (our cascade is more conservative). The real discriminator is the Shahaf AMRF compact-vs-triple axis, not a selection gap. Null.
> - **Cluster membership (Cantat-Gaudin 2020 / Hunt 2023–24 / Vasiliev 2021):** ~6 genuine open-cluster members, **all** sub-turnoff ~1 M⊙ stars from the already-Tier-2 acceleration pool → the cluster CMD *lowers* M₁ and leaves the period degeneracy intact, weakening (not strengthening) the compact case. 0 GC members. Null.
> - **TESS-FFI Doppler-beaming / ellipsoidal (bright Tier-1 NS):** clean null (beam SNR ≤ 1.8, perm-FAP ≥ 0.09; injection-recovery confirms a real beam would have been recovered at ~12σ). Physically expected: **all Tier-1 NS have P > 114 d**, so tidal/ellipsoidal channels are dead and beaming sits below the TESS red-noise floor. The skepticism caught the CV-eclipse trap again (cross-sector flux offsets alias into the long period).
>
> **Net:** every accessible DR3-era dataset — Gaia DR3 NSS cascade + FPR, HGCA/PMA (Brandt/G23H), Shahaf AMRF, WD-primary reverse (GF21), X-ray (eROSITA/CSC/4XMM/2RXS/2SXPS), radio (ATNF), variability annex, microlensing, four multi-epoch RV surveys, cluster membership, TESS-FFI — is exhausted and null for a novel dormant compact object. The triple-vs-compact degeneracy is broken only by phase-resolved RV or **Gaia DR4 epoch astrometry (2 Dec 2026)**. Reports under `/tmp/*_2026_05_31.md`. Reusable DR4-era vetting resources mapped: LAMOST DR11 VizieR `V/162` (per-epoch MRS RVs, Gaia-DR3-keyed), DESI DR1 MWS via Astro Data Lab TAP (coadd-level), SDSS-V DR19 `mwm_apogee_allvisit`.

> **⚠ Fresh-lane discovery sweep (2026-06-01) — six new archival lanes beyond the compact-object cascade, all null; methods validated, reusable tooling built.** A push into less-picked-over data and fresher sky, each lane required to FIND *and* CONFIRM from archives (no telescope), front-filtered against a new known-object store. Every lane recovered its known population (method validated) and deflated every novel candidate under deep-vetting:
> - **Cross-survey stellar spectral differencing (SDSS×DESI, 1,080 pairs):** recovered 51 known CV accretion-state changes (specificity falls 69→3.3→0.8→0.7% across CV/B/WD/M, proving the metric tracks real variability); **0 new**. CV+B strata complete, the discovery-relevant WD+M strata only ~3% covered (throughput-walled at ~0.14 DESI pairs/s).
> - **IR-obscured nova/eruption (NEOWISE, 6 low-extinction plane windows, 107 optically-blank sources):** 2 IR-rising, 1 clean riser = known YSO (SPICY 2002); **0 genuine eruptions** — YSO/AGB-dominated, exactly as the Galactic nova rate predicts (≪1/window).
> - **eRASS1 × Gaia X-ray-first accretors — v1 + fixed-gate v2:** 808 bright accretor candidates; recovered 161 CV / 24 XRB / 7 symbiotic (validation). v1's two "new" CVs were both **already-published dwarf novae** (leaky SIMBAD-only crossmatch). v2 (corrected multi-catalogue gate + outburst test): **671 known / 137 uncatalogued → 0 outburst-confirmed new** (residue = Gaia-quiet normal stars + 2 AGN; 43 southern archive-untestable). Clean null.
> - **Type-Ia-survivor / hypervelocity & runaway WDs (Gaia high-v_tan + GF21):** recovered 2/5 published D6/LP40 stars (3 misses principled parallax/luminosity exclusions); 153 FP-gated high-v_tan WDs; **0 new D6/partly-burnt remnants**. Top lead (catalogue-typed "DOX") deep-vetted via SDSS+DESI composition → ordinary **halo DBZ** WD (fast but not hypervelocity).
> - **Gaia XP-spectra outlier mining (pilot, 702 of ~219M):** top anomalies all known exotica (PNe central stars, WDs, hot subdwarfs, WR stars); **0 confirmed novel**. Pipeline validated; the full-archive run is a *build* (GaiaXPy + bulk coefficients + autoencoder), not a session — **highest remaining ceiling**.
> - **Bulge/inner-plane symbiotic + dust-obscured accretor (feasibility):** the genuinely under-mined sky, but **CONFIRMATION-LIMITED for a solo/archive effort** — the IR "find" half works (2MASS+WISE recover 90–94% of known donors; selection re-found 7 catalogued symbiotics in-window), but the X-ray/UV-on-a-cool-giant discriminant is *dead in the bulge* (eRASS1 3/119, GALEX 0/119 — genuine non-coverage), leaving optical spectroscopy (telescope) as the only confirmation. 137 selected → 0 archive-confirmable. **Parked for Rubin/LSST + 4MOST/SDSS-V bulge spectroscopy.**
>
> **Net:** the archive-confirmable-in-one-session space is exhausted across fresh and picked-over data alike — **0 confirmed novel objects**, the project's signature outcome. The no-telescope filter held (it correctly predicted bulge + self-lensing as parks). Methodological lessons recorded: (i) a Gaia-epoch positional crossmatch *leaks high-PM accretors* (missed Kapteyn's Star, RR Cae) → match by source_id + J2000 propagation; (ii) never gate novelty on a single null-prone SIMBAD field — use VSX + Gaia-vclass + Ritter-Kolb/Downes/Rodriguez+2025 + the store; (iii) **APOGEE DR17 ASPCAP is not yet ingested here** (the one no-telescope bulge-confirmation route — highest-value missing data). **Remaining EV: XP-at-scale (a build), and fresh data — Gaia DR4 (2 Dec 2026), eROSITA-east, Rubin/LSST.** Reusable tooling built + committed this session: the **hunt console** (live dashboard + per-object dossier viewer, `scripts/web_tool/hunt_console/`) and a **known-object front-filter** (`scripts/known_objects/`, 6,104 objects, source_id-keyed, catches catalogued objects before vetting). Per-lane reports under `/tmp/*_2026_06_01.md`; per-run contracts under `/tmp/hunt_runs/`.

## Tier-1 NS pool triage + Shahaf+2023 cross-check (2026-05-28)

All 161 M₁-corrected Tier-1 NS run through a rigorous second-method triage (archival-RV census + NSS-locked Keplerian; `scripts/ns_pool_triage_2026_05_28.py`) and cross-matched to Shahaf+2023 Triage I (`scripts/ns2127900_deepdive_2026_05_28.py`), whose AMRF analysis distinguishes a single dark companion from a hierarchical triple — the discrimination the cascade itself lacks.

| Triage verdict | N |
|---|---:|
| No archival RV (remain candidates) | 117 |
| Inconclusive (RV, too few distinct phases) | 40 |
| Outer-orbit RV corroborated | 2 (1 verified real) |
| **REFUTED → demoted** | **2** |

**Demoted** (archival RV grossly inconsistent with the astrometric orbit — a superposed/inner short-period binary, not the astrometric companion): Gaia DR3 **2129927539681151872** (spectroscopic f(M) ≈ 220× astrometric) and **1379150557507688960** (ruwe = 20.2; f(M) ≈ 860×).

**Key finding — the compact-vs-triple problem.** Shahaf+2023 independently **corroborates the cascade masses** (M₂min consistent) but assigns most high-significance candidates a *low* compact probability — i.e. they are more likely **hierarchical triples** (an inner main-sequence pair) than single neutron stars:

| Source | AMRF | M₂ | P(compact) | Read (deep-dive 2026-05-29, `scripts/prime3_deepdive_2026_05_29.py`) |
|---|---:|---:|---:|---|
| **3378588057203660160 (HD 264291)** | 0.635 | **1.94** | **0.75** | **HEAVY NEUTRON STAR — RV-CONFIRMED** (the one surviving compact-favored candidate; full dossier `docs/dossiers/HD264291_DOSSIER_2026_05_29.md`). Free-period fit of 50 LAMOST RVs recovers P≈1026–1095 d (= astrometric 999 d), confirming the orbit despite marginal astrometry (sig 12.5). With honest errors (jitter 1.6 km/s → χ²/dof 3.15, K₁=16.5±0.35) and M₁=1.81±0.15 (FLAME; Ap-star systematic broadened) at i≈67°: **M₂ = 1.94 [1.80, 2.09] M⊙, P(heavy-NS)=0.95, P(mass-gap)=0.05, P(BH)=0.** Single dark companion (no SB2; a separate 32-d residual = Ap rotation, decoupled from the orbit). **NOT novel** — it is the Shahaf+2023 headline; our contribution is the independent RV confirmation. |
| 2127900555635640832 | 0.591 | 1.45 | 0.21 | external RV confirms the *outer* orbit, but Shahaf favors a triple ~4:1; M₂ at the WD/NS edge |
| 6419437207856851584 (sig 212) | 0.575 | 1.30 | ~0.0 | triple |
| 823243942431149568 (sig 194) | 0.563 | 1.42 | ~0.0 | triple |
| **5640825637852070016 (sig 295, HD 75567)** | 0.588 | 1.35 (dark) | **0.15** | **TRIPLE-FAVORED — downgraded.** Calibrated P(III\|A,M1) over 322 Shahaf neighbours = 0.85 triple; spectroscopic/astrometric a-ratio = 1.23 (>1 → luminous inner pair pulls the photocentre back). Novel, but not a compact object. |
| **1714530637958169600 (sig 208, TYC 4562-535-1)** | 0.586 | 1.26 (dark) | **0.13** | **TRIPLE-FAVORED — downgraded.** 448 neighbours; a-ratio = 1.31; near face-on (i≈22°) inflates M₂. Novel, but not a compact object. |

**Net:** the cascade masses are real and Shahaf-AMRF-corroborated, but the **only** candidate that survives the triple-vs-compact test is **HD 264291** — a *known* Shahaf object whose orbit we independently **RV-confirmed** (heavy neutron star, M₂ ≈ 1.94), with an Ap-star-primary caveat. Every other high-significance Tier-1 NS — including all three genuinely novel ones (HD 75567, TYC 4562-535-1, and Gaia DR3 5858574810404752256) — is favored to be a hierarchical triple. **No novel compact object survives anywhere in the catalog;** the only compact-favored object (HD 264291) was already published by Shahaf+2023.

## Confirmed (independent 2-channel)

### CRTS J051419+0111 — ⚠ RETRACTED 2026-05-28 (no longer a confirmed detection)

**The 3.013-hr period and the TESS eclipse are artifacts; only Gaia DR3 3155543945892767232 remains in this section.** Rigorous re-analysis — outburst-masked Lomb-Scargle + BLS on the *identical* ZTF DR23 data, plus a proper test of the actual S98 2-min SPOC product (`scripts/crts_j051419_ztf_recheck.py`, `scripts/crts_j051419_spoc_recheck.py`):

| Original claim | Re-analysis verdict |
|---|---|
| P = 180.77 min (BLS power 43,842) | **Not supported** — outburst-masked LS FAP at 180.77 min = 1.0 in all 3 ZTF bands; only 1-sidereal-day aliases survive; BLS best period disagrees across bands (zg 256 / zr 154–269 / zi 110 min). The "power 43,842" came from folding outburst-*including* data. |
| TESS "71% median quiescent eclipse, i≈84°" | **Falsified** — S98 SPOC per-cadence S/N = 0.66; the folded dip at 180.77 min is 3.37σ vs a random-period null *mean* of 4.07σ (permutation FAP = 0.87). The 71% was a per-cycle minimum-of-noise artifact. S5/S32 FFI give negative net flux — TESS cannot detect this source's eclipse at all. |

**Real (survives):** a dwarf nova with 6 ZTF + 1 CRTS outbursts and a genuine 2023 superoutburst (7-day, g = 14.41) → SU UMa subtype. **No orbital period, eclipse, or inclination.** CV identity is prior (Drake+ 2014, Coppejans+ 2016, and **Gaia DR3 variability classifier best_class = CV, 0.911** — previously only the DSC QSO false-positive was cited). VSX entry not found in the Vizier `B/vsx` mirror (reconcile vs live AAVSO VSX). Residual publishable value: an outburst/superoutburst note (RNAAS-level), not the eclipsing-period discovery originally claimed. Dossier: `docs/dossiers/CRTS_J051419+0111_DOSSIER_2026_05_28.md` (body §3/§4/§6 numbers superseded by the retraction banner at its head).

### Gaia DR3 3155543945892767232

| Field | Value |
|---|---|
| Class | NS candidate (62% NS, 20% mass-gap BH, 38% WD on the posterior) |
| Primary | K1III RGB giant, Teff = 5100 K, log g = 3.4, M_1 = 1.4 ± 0.3 M_⊙, d ≈ 1050 pc |
| NSS solution_type | AstroSpectroSB1 — significance 40.7, n_obs = 206 |
| Orbit | P = 543.27 ± 4.56 d, e = 0.089 ± 0.045, K_1 ≈ 15.5 km/s |
| First channel | NSS AstroSpectroSB1 astrometric + spectroscopic joint fit |
| Second channel | LAMOST LRS 2 epochs: MJD 56352 (RV 31.78 km/s), MJD 57325 (RV 45.45 km/s). Predicted ΔRV at the NSS-phase pair (0.874 → 0.665) matches observed at **χ² = 0.36**, residuals 0.22σ + 0.32σ. ΔTeff = 13 K, Δlogg = 0.022 between epochs → no SB2 contamination. |
| M_2 posterior at M_1 = 1.4 | 1.08 / 1.57 / 2.34 M_⊙ (16/50/84%) |
| Dossier | `docs/dossiers/3155543945892767232_DOSSIER_2026_05_28.md` |

## Strong candidates (single-method)

### Gaia DR3 5406907085973524224 — ⚠ DOWNGRADED 2026-05-29 (weak / suspect)

**The orbit may be spurious:** a single DPAC-rejected OrbitalAlternative solution (max|corr| = 0.98), and Gaia shows **no RV variability** (RV 2.34 ± 4.12 km/s over 27 transits) where a P = 25-d / M₂ ≈ 4 orbit predicts ~100 km/s. The "rv_chisq_pvalue = 0 corroboration" row below is **incorrect** (rv_amplitude_robust is NULL). Table retained for the audit trail.

| Field | Value |
|---|---|
| NSS solution_type | OrbitalAlternative (high parameter correlation, not luminous-binary inconsistency) |
| Orbit | P = 25 d, e = 0.28, K_1 sin i predicted ≈ 100 km/s (87-130 km/s 16-84%) |
| Primary | M_1 = 0.85 ± 0.15 M_⊙ (StarHorse + GSP-Phot + TIC convergent), G = 14.53 |
| M_2 posterior at M_1 = 0.85 | 3.1 / 4.5 / 6.6 M_⊙ (16/50/84%) |
| P(M_2 > 1.4) | 99.7% (WD ruled out) |
| P(M_2 > 2.2) | 96.7% (NS upper limit exceeded) |
| P(M_2 > 3.0) | 85.5% (stellar-mass BH) |
| RV-variability corroboration | ~~Gaia `rv_chisq_pvalue = 0`~~ **RETRACTED — incorrect**: rv_amplitude_robust is NULL; RV = 2.34 ± 4.12 over 27 transits shows no variability |
| Follow-up | HARPS half-night (3 epochs × 30 min) — predicted K_1 ≈ 100 km/s vs HARPS σ_RV = 5 m/s |
| Prior identification | ResearchGate preprint #403022650 (unreviewed; their a_phot uses √(s/2) not Pourbaix-Halbwachs, giving M_2_min ≈ 1.95 M_⊙) |
| Dossier | `docs/dossiers/5406907085973524224_DOSSIER_2026_05_28.md` |

### Gaia DR3 5858574810404752256 — ⚠ DEMOTED 2026-05-29 (triple-favored, not a compact object)

**Re-verification** (`scripts/hd264291_dossier_2026_05_29.py`): the AMRF + Shahaf calibrated P(compact|A,M₁) classifier gives **P(compact) ≈ 0.21–0.35 → favored to be a hierarchical triple** (unresolved inner main-sequence pair), like HD 75567 / 1714530. The prior "**M₂ ≈ 2.82 (mass-gap BH)**" is **FALSIFIED** — it misused `rv_amplitude_robust/2` to invent sin i = 0.53; the astrometric photocentric mass function gives M₂ ≈ **1.48–1.63 M⊙** directly (no sin-i inflation), and there is **no archival RV** (the "Gaia RV corroboration" was variability only). Original table retained for the audit trail.

| Field | Value |
|---|---|
| Primary | G0 IV subgiant, M_1 = 1.5 ± 0.3 M_⊙, R_1 ≈ 3.9 R_⊙, d ≈ 1.69 kpc, G = 11.97 |
| Orbit | P = 506.135 ± 2.8 d, e = 0.542, significance 20σ, a_phot = 0.527 mas |
| f(M) | 0.367 M_⊙ |
| AMRF (Shahaf+ 2019) | 0.63 — dark companion confirmed |
| RV evidence | rv_amplitude_robust = 23.9 km/s peak-to-peak, p_χ² = 1.6×10⁻¹⁴ over 22 RVS transits |
| M_2 interpretation | rv_amplitude as 2K_1 (v2 convention): K_1 ≈ 12 km/s, sin i ≈ 0.53 → **M_2 ≈ 2.82 M_⊙ (mass-gap BH)**; as half-amplitude: K_1 = 24 km/s, sin i = 1.0 → M_2 = 1.48 (NS / heavy WD) |
| Novelty | ~~Truly novel — not in SIMBAD, not in Shahaf+ 2023 / 2024~~ — the *novelty* fact stands, but **COMPACTNESS demoted 2026-05-29 (triple-favored — see banner above)**; most likely a hierarchical triple, not a compact object |
| Follow-up | 3-5 RV epochs (~5 h CHIRON/FEROS) at periastron |
| Dossier | `docs/dossiers/5858574810404752256_DOSSIER_2026_05_28.md` |

### HD 157033 — ⚠ DOWNGRADED 2026-05-29 (ambiguous 0.4–6 M⊙, NOT a confirmed BH)

**Companion is real, but the mass is unconstrained.** The APOGEE RVs are unreliable for this hot A9/F0 star (high Chi2RV, spurious [Fe/H] = −1.45); Kervella's face-value is M₂ = 0.45 M⊙; ruwe = 0.85 (no astrometric orbit); and the "K₁ ≥ 16.3" is `rv_amplitude_robust` (≈ 2K₁), not a clean K₁. Needs one clean optical RV to resolve M-dwarf vs BH. Table retained for the audit trail.

| Field | Value |
|---|---|
| Gaia DR3 source_id | 4111149395881722496 (= HIP 84960 = TYC 6825-498-1) |
| Primary | A9/F0V, G = 9.95, d = 293 pc, M_1 = 1.60 ± 0.20 M_⊙ (consensus of FLAME 1.67 / StarHorse 1.59 / TIC 1.42 / GALAH 1.43 / Kervella 1.82) |
| Channel 1 — HGCA Brandt 2021 | **χ² = 1583** (one of the highest in the catalog — far above the 30 corroborated threshold) |
| Channel 2 — Kervella H2G2 2022 | snrPMa = 14.85, dVt = 3.15 km/s; Kervella M_2_5AU = 0.45 M_⊙ at face value (the often-quoted "4 M_⊙" only comes from accounting for orbit-averaged PMa dilution at P ≈ 10 yr — see dossier §6) |
| Channel 3 — Gaia DR3 RV variability | `rv_amplitude_robust = 16.305 km/s` over 17 transits; `rv_chisq_pvalue = 1.78×10⁻¹⁵` (> 9σ rejection of single-velocity); `rv_renormalised_gof = 7.22` (≫ 4 = binary) |
| Channel 4 — Multi-archive direct RV (task HH) | **4 archival epochs across 4.3 yr**: GALAH DR3 MJD 57479 = −39.94 km/s; APOGEE DR17 MJD 58567 = +26.54, MJD 58570 = −2.41, MJD 59057 = −44.52 km/s. **ΔRV peak-to-peak = 71 km/s → model-free K_1 ≥ 35.5 km/s, central ≈ 47 km/s — 2-3× larger than the Gaia rv_amplitude_robust.** Strengthens the BH classification. |
| NSS solution | None — P ≈ 10 yr exceeds the Gaia mission 1000-d cutoff (no Keplerian fit possible from the 4 epochs without ephemeris) |
| M_2 (at M_1 = 1.60, P = 10 yr, K_1 = 16.3) | sin i = 1: 3.62 M_⊙; ⟨sin i⟩ = 0.785: 5.65 M_⊙ |
| M_2 (optimistic end, IF the suspect APOGEE K_1 ≈ 47 is real) | 6–17 M_⊙ — but this rests on **unreliable APOGEE RVs**; the honest range is **0.4–6 M⊙** (M-dwarf to BH). NOT a solid BH; could also be a hierarchical triple. |
| P(M_2 > 3.0) | ~75% from Gaia channel alone; substantially higher when HH archival K_1 included |
| Novelty | **Zero SIMBAD bibcodes** — no peer-reviewed paper has ever discussed HD 157033. Absent from Halbwachs+ 2023, Shahaf+ 2023, Müller-Horn+ 2026 (excluded by RUWE = 0.85 < 1.4, M_1 = 1.6 > MS cutoff 1.51, rv_amp = 16.3 < 20 threshold). The accurate claim is only that no peer-reviewed paper has discussed HD 157033 as a binary; the snrPMa = 14.85 PMa was already published (Kervella 2022). |
| Follow-up | ~1 hr on FEROS or 4 epochs of new RV to derive 5-epoch Keplerian; would **resolve the M-dwarf-vs-BH ambiguity** (mass is currently unconstrained) |
| Dossier | `docs/dossiers/HD157033_DOSSIER_2026_05_28.md` |
| Status of sibling Pile-A candidates | 7/8 demoted to stellar binaries via Kervella H2G2 (M_2 = 0.4–2.9 M_⊙ at 5 AU): CD-46 10032A, HD 173689, HD 16385, HD 81825, HD 37943, HD 5514, LP 155-298. Detailed demotion dossiers for CD-46 10032A and HD 173689 at `docs/dossiers/CD-46_10032A_DOSSIER_2026_05_28.md` and `docs/dossiers/HD_173689_DOSSIER_2026_05_28.md`. |

### WD-primary binaries (Pile E)

Hand-curated (WDJ060042, WDJ020915): **novel long-period WD-primary binary with an unresolved massive companion** — total mass above the Chandrasekhar mass (M_tot≈2.0), but **neither companion is confidently super-Chandra** (P(M₂>1.4)=9% / 41%, full-Thiele-Innes-covariance MC) and at P=275 / 935 d the system **will not merge in a Hubble time → not a Type-Ia progenitor** (see the 2026-05-31 framing-correction note above). Companion class (cool WD vs dormant ~1.3 M⊙ NS) undecided; WDJ020915's astrometric orbit is a weak Keplerian fit (F2=+8.4) → awaits DR4. SED two-component fits exclude an M-dwarf companion at >10σ via W1/W2 and a hot-WD companion (T_2 ≳ 19 000–20 000 K) at >3σ via Pan-STARRS / Gaia **blue optical** (GALEX has an AIS coverage gap for WDJ020915, so its hot-WD exclusion rests on blue optical, **not UV** — correcting the dossiers' UV-based wording). Surviving companion classes: a cool double-degenerate WD or a dormant ~1.3 M_⊙ neutron star — SED-indistinguishable.

Pipeline-derived (WG 26, WDJ205650 — from task GG GF21 cross-match of the v2 + v2_relaxed + v2_alt "WD or low-mass star" bin):

| Source | M_1 (WD) | M_2 | M_total | P | G | Pool | Notes | Dossier |
|---|---:|---:|---:|---:|---:|---|---|---|
| **WDJ060042.75-293041.36** (Gaia DR3 2909342818326298112) | 0.612 | 1.368 | 1.98 | 935 d | 18.4 | hand-curated | d = 98 pc. NOT in SIMBAD (novelty re-locked 2026-05-31). M_total≈1.98 > M_Ch, but P=935 d → **non-merging, not a Type-Ia progenitor**; companion WD-vs-NS unresolved (P(M₂>1.4)=41%; clean orbit F2=+0.8 — most likely a true NS). No optical RV (verified); long-baseline X-shooter, RV-min not until 2028. | `docs/dossiers/WDJ060042-293041_DOSSIER_2026_05_28.md` |
| **WDJ020915.51+380425.92** (Gaia DR3 332248057157474176)  | 0.718 | 1.323 | 2.04 | 274 d | 16.2 | hand-curated | d = 84 pc. NOT in SIMBAD (novelty re-locked 2026-05-31). M_total≈2.04 > M_Ch, but P=275 d → **non-merging, not a Type-Ia progenitor**; companion WD-vs-NS unresolved (P(M₂>1.4)=9%). Astrometric orbit a weak fit (F2=+8.4) → mass awaits DR4. Best RV target: ~5 HARPS-N epochs yield >50σ K_1 in one 2026–27 season. | `docs/dossiers/WDJ020915+380425_DOSSIER_2026_05_28.md` |
| **WG 26** = WDJ141039.06-474439.48 (Gaia DR3 6092654861665006592) | 0.62 | **0.65** | **1.27** | 176 d | 14.35 | v2_relaxed | **CONFIRMED_WD_BINARY_SUB_CHANDRASEKHAR** (JJ dossier). Hot DA WD primary (**Sahu 2023**, MNRAS 526, 5800, HST/COS: T_eff=21,705 K, log g=7.99, M_1=0.62, cooling age 42 Myr — *not* "Shahaf 2023") at d=56.4 pc. NSS Orbital P=175.9d, e=0.064, sig=68.8, measured i=77° → M_2=0.60–0.65 (dark; a deprojected measurement, not a sin-i=1 floor), M_total=1.13–1.27 across WD M_1 priors (**sub-Chandrasekhar — not Type Ia**). Likely cool double-degenerate; M-dwarf companion excluded >10σ by SED. Binarity essentially un-studied (Sahu 2023 + Vincent 2024 catalog ingest only). LISA-precursor DD at one of the smallest distances in Gaia DR3 NSS. | `docs/dossiers/WG26_DOSSIER_2026_05_28.md` |
| **WDJ205650.56+062149.68** (Gaia DR3 1736555475066523008) | 0.39 (He WD) | **0.26** | **0.64** | 81 d | — | v2_alt | **CONFIRMED_WD_WD_LOW_MASS** (KK dossier). He+He double-degenerate at d=93 pc. SED consistent with single 9,300–10,500 K LM He WD primary; cascade M_2=0.56 was at default M_1=1.5 → self-consistent at M_1=0.39 gives M_2=0.26, M_total=0.64. BOTH components require binary mass-transfer history → post-CE He+He DD that survived the 2nd CE (wide enough at a=68 R_⊙ to NOT merge in a Hubble time, t_GW ≈ 5×10¹⁶ yr). **NOT NOVEL — Munday+2024 (DBL Survey I, 2024MNRAS.532.2534M / arXiv:2407.02594) already characterized this as a wide double-WD with the 81-d Gaia astrometric period; our only new element is the dynamical M₂/M_total inversion.** (The pipeline's earlier stored super-Chandra M_total=2.06 was an artifact — the GF21 WD mass was never joined into the M₁-correction step, leaving the default M₁=1.5.) NEEDS_RV. | `docs/dossiers/WDJ205650+062149_DOSSIER_2026_05_28.md` |

Plus 4 additional candidates from the v3 Acceleration channel (separate pipeline), notably **WDJ173708.52+242024.77** with M_WD = 1.22 M_⊙ — massive ONe WD with significant acceleration.

**Methodological note from GG**: cross-matching the 83 k v2 "WD or low-mass star" rows against Gentile Fusillo 2021 yields only **2 GF21-confirmed WD primaries**. The bin is dominated by M-dwarf primaries, not WD primaries — GF21's Gaia HRD position cut systematically excludes WD+M-dwarf systems where the M-dwarf dominates the visible flux. Pile E expansion is limited; the 50× expansion hoped for via systematic GF21 cross-match is not achievable from this catalog alone.

### M-dwarf super-Jupiter candidates (Pile B)

| Source | SpT | d (pc) | M_2 (M_J) face-on | P (d) | G | TESS sectors | Dossier |
|---|---|---:|---:|---:|---:|---:|---|
| **APMPM J0710-5704** (Gaia DR3 5486916932205092352) | M4V    | 17.07 | 9.5 ± 1.5 | 253.48 | 12.2 | 37 | `docs/dossiers/APMPM_J0710-5704_DOSSIER_2026_05_28.md` |
| **SCR J1441-7338**   (Gaia DR3 5796338299045711232) | M5.5-M6V | 25.55 | 11-12 | 488.05 | 14.8 |  9 | `docs/dossiers/SCR_J1441-7338_DOSSIER_2026_05_28.md`. eROSITA-DE DR1 counterpart at 3.45″, L_X ≈ 1.4×10²⁸ erg/s — consistent with M-dwarf coronal emission, not a compact-companion signature; doesn't affect the SJ companion claim. |
| **UCAC4 313-025977** (Gaia DR3 5612039087715504640) | M4-M5V | 32.39 | 13 | 592.32 | (TBD) |  4 | `docs/dossiers/UCAC4_313-025977_DOSSIER_2026_05_28.md` |

APMPM J0710: 37 TESS sectors stitched show **no phase modulation at P or P/2 below ~200 ppm**, but at a/R₁ ≈ 446 even an edge-on *stellar* companion would produce only ~0.02 ppm ellipsoidal modulation — so this non-detection is **uninformative** about the companion's mass or darkness (it does *not* establish a dark companion "across all inclinations"). The substellar case rests on the astrometric mass function alone; RV is required.

**Novelty (2026-05-30 cross-check):** APMPM J0710 (5486916932205092352) and SCR J1441-7338 (5796338299045711232) are **already published** Gaia-NSS substellar candidates — both appear in Marcussen & Albrecht 2023 (AJ 165, 266) and Bailer-Jones & Kreidberg 2026 (A&A 708, A249) at consistent ~10–12 M_J. Our analysis is an independent reanalysis/cross-check, **not a discovery**; the dossiers' "TRULY NOVEL" claims (from a stale SIMBAD snapshot) are corrected. Only **UCAC4 313-025977** (5612039087715504640, ~15 M_J brown dwarf, P=592 d) is not previously cataloged. All three are astrometry-only and inclination-degenerate (M_2 ∝ 1/sin i): substellar-favored but unconfirmed pending RV.

## Marginal archival corroboration (1 candidate — tasks BB2 + II2)

| Source | NSS class | Sig | P (d) | e | Archival evidence |
|---|---|---:|---:|---:|---|
| **Gaia DR3 1593152388271709824** | Orbital | 104.5 | 597.4 | 0.404 | **MARGINAL_2CHANNEL.** 4 archival RV epochs across 3 distinct phases (1 LAMOST LRS 2016 + 1 APOGEE DR17 2017 + 2 LAMOST MRS 2023) fit the NSS-locked Keplerian at χ²/dof = 0.002, K_1 = 17.5 ± 5.9 km/s; spectroscopic f(M) = 0.26 agrees with astrometric f_phot = 0.29 (< 0.2σ) → K–ω degeneracy broken, both channels corroborate. **But K_1 is only ~3σ** (the amplitude rests on one ±10.54 km/s LAMOST LRS epoch), short of CONFIRMED. At M_1 = 1.40 (FLAME): M_2 ≈ 1.27 M_⊙ on the WD/NS boundary → most likely a massive WD; P(NS) ≈ 42%, P(BH) ≈ 2%. Corrects the earlier "2 LAMOST DR11 + K_fit = 4.09" note, which rested on a mis-dated LRS epoch — PlanId `HD145818N500615V01` encodes the plate field-center coords, not 2015-06-15; true epoch MJD 57501 = 2016-04-23. **Settling epoch:** one ~1 km/s RV near periastron MJD 61060 (2026-01-20) measures the predicted ~30 km/s swing at > 50σ — the highest-value single Tier-2 epoch. Dossier: `docs/dossiers/1593152388271709824_DOSSIER_2026_05_28.md`. |

## Tier-1 BH pool — verdicts

| Source | M_2 (cascade) | Verdict |
|---|---:|---|
| Gaia DR3 5406907085973524224 (v2_alt) | 4.79 | **WEAK / SUSPECT** (2026-05-29) — orbit may be spurious (DPAC-rejected OrbitalAlternative; Gaia RV-silent); see above |
| Gaia DR3 3263804373319076480 (GALEX J033455+000910, v2) | 3.22 | DEMOTED — Simon, Lam, El-Badry, Reggiani 2026 (arXiv:2603.20371) published as WD with M_2 ≤ 0.9 via 7 MIKE + 4 FEROS + APOGEE + LAMOST RV epochs |
| Gaia DR3 6281177228434199296 (GALEX J145250-192225, v2) | 12.75 | DISPUTED — **RUWE = 6.46** (astrometric solution severely compromised → NSS photocentric M_2 unreliable; cascade also needs sini ≈ 0.12, near-face-on); RAVE–Gaia RV drift inconsistent; Shahaf+ 2023 Triage I. **Ellipsoidal claim retracted 2026-05-28** (`scripts/galex_j145250_ellip_recheck.py`): only a single 27-d TESS sector (QLP) vs P_orb = 154 d, so P/2 = 77-d ellipsoidal is unmeasurable — folded P2P at P/2 is indistinguishable from random periods (perm FAP = 0.28); the prior "0.138%" was a post-detrend noise-floor, not a detection. |

> **Pipeline note — no global RUWE gate (cascade-regression, 2026-05-30).** The bulk consumer (`consumer_v2.derive_row_v2`) applies no astrometric-quality (RUWE) cut, so two RUWE > 6 sources reach Tier-1: GALEX J145250 (RUWE = 6.46 — the catalog's only Tier-1 BH) and GALEX J033455 (RUWE = 9.35, since published as a WD). Both are individually flagged/demoted in the table above, and the corrected headline makes **no** astrometry-only BH/Tier-1 claim, so this affects no current result. But any *future* Tier-1/BH headline must re-vet on RUWE first; adding a global RUWE flag to the tiering is a tracked follow-up.

## X-ray non-detection note (task Q2)

5-catalog cone search (eROSITA-DE DR1, CSC2.1, 4XMM-DR13, 2RXS, 2SXPS at 10″) on the 4 strong dormant compact-object candidates — 5406907, 5858574, HD 157033, 3155543 — returns **zero counterparts**. Expected: at d = 296 pc – 1.33 kpc, quiescent NS/BH XRB flux would be F_X ~ 10⁻¹⁵ – 10⁻¹⁶ erg/s/cm², below all-sky-survey sensitivity. The null rules out *persistent* L_X > 10³¹ erg/s for 3155543 (only candidate inside the eROSITA-DE footprint); HD 157033, 5406907, 5858574 are in the Russian eROSITA half and not yet probed by any public all-sky X-ray catalog at the required depth. Targeted Chandra/XMM at quiescent-XRB sensitivity is the next confirmation channel.

## Demoted / falsified

| Object | Why demoted |
|---|---|
| HD 207141                                | v2 NSS plx correction: M_2 = 7.57 → 1.31 M_⊙ |
| HD 1957                                  | F#30 K-giant chromatic FP (logg_gspspec_ann = 2.63) |
| TYC 1363-2339-1                          | NSS plx correction: M_2 = 3.88 → 1.12 M_⊙ |
| TYC 1299-727-1                           | NSS plx correction: M_2 = 3.50 → 1.18 M_⊙ |
| TYC 2773-348-1                           | NSS plx correction: M_2 = 3.21 → 1.03 M_⊙ |
| TYC 8785-1657-1                          | NSS plx correction: M_2 = 3.63 → 1.06 M_⊙ |
| TYC 4791-2322-1                          | NSS plx correction: M_2 = 2.66 → 1.34; F#32 sin_i_implied = 1.51 fails joint check |
| Pile-A HGCA "BH-class" (7 of 8)          | Kervella H2G2 M_2 = 0.4-2.9 M_⊙ at 5-AU reference → stellar binaries |
| BD+05 5218                                | = HIP 117179 b; Stevenson 2023 (MNRAS 526, 5155 = arXiv:2310.02695) published as 44 M_J BD |
| HD 37419                                  | Known visual triple ADS 4267; HGCA signal is the inner pair |
| HD 12871                                  | Hierarchical triple — APOGEE 3-visit K_1 = 11.9 matches Gaia SB1 K_1; outer companion drives Acceleration |
| Gaia DR3 5476986108823894400              | Multi-survey "K_1=163 km/s" retracted: APOGEE σ = 6.96 (real) vs RAVE σ = 115 km/s (RAVE pipeline noise floor) |
| Gaia DR3 6802634430521968000              | Gaia MSC pipeline converged on luminous G2V+K3V binary at d = 553 pc (logposterior_msc = 589); 17σ NSS-plx vs gaia_source-plx tension; e = 0.871 in known FP class |
| Gaia DR3 411532290151732992               | Already in Shahaf+ 2023 Triage I (M_2_min = 1.75) |
| Gaia DR3 2899685738980957568              | Already in Shahaf+ 2023 Triage I (M_2_min = 1.58) |
| Gaia DR3 504135672000072064               | Already in Shahaf+ 2023 Triage I (M_2_min = 1.30) |
| Gaia DR3 1985832181476519936 (HD 216783)  | Gaia MSC luminous-binary fit (`logposterior_msc > 50`) AND DSC `binary_prob > 0.5` — near-certain stellar-binary contaminant |

## Pile F — CV-period orbital periods (full table)

14 candidate periods from ZTF DR23 BLS + 4 blind methodology rediscoveries (the latter match RKcat/Hardy/Bruch — validating the method *when a real period exists*).

> **⚠ CV-period pipeline RETRACTION (2026-05-28).** The CV-period pipeline produces **false positives** — it folded outburst-*including* light curves (outbursts inject power across all frequencies), read eclipse depths as the per-cycle *minimum* of noise-dominated cadences, and applied no alias control. Rigorous re-vetting (outburst-masked Lomb-Scargle + BLS + permutation/refined-null FAP, plus the actual TESS SPOC product; scripts `crts_j051419_*recheck.py`, `cv_period_revet_2026_05_28.py`) **falsifies every claim tested — 5 of 5:**
>
> | # | Object | claimed P (min) | verdict |
> |---|---|---:|---|
> | 13 | CRTS J051419.8+011120 | 180.05 | **NOT_SUPPORTED** — masked-LS FAP = 1.0; TESS S/N 0.66 |
> | 2 | SDSS J154953.41+173939 | 116.68 | **NOT_SUPPORTED** — masked-LS FAP = 1.0 (ZTF S/N 27, ample); BLS bands disagree |
> | 7 | SDSS J091935.66+502825 | 93.51 | **NOT_SUPPORTED** — masked-LS FAP = 1.0; bands disagree |
> | 10 | CRTS J151836.0-054803 | 24.64 | **NOT_SUPPORTED** — masked-LS FAP = 1.0 (ZTF S/N 11, ample → true falsification, not sensitivity); proposed 172-min parent absent |
> | 11 | SDSS J160419.02+161548 | 128.80 | **NOT_SUPPORTED** — masked-LS FAP = 1.0; "23% eclipse" is min-of-noise (refined-null FAP 0.63) |
>
> In every case the claimed period vanishes when outbursts are masked, only 1-sidereal-day aliases survive, the BLS best period disagrees across bands, and TESS "eclipses" are minimum-of-noise. **Two targets had ample ZTF S/N (27 and 11) yet still failed — these are genuine false periods, not sensitivity limits.** The 4 "blind rediscoveries" (below) only recovered *known* RKcat/Hardy/Bruch periods. **Net: the CV-period avenue produced ZERO verified novel periods.** The 9 untested ZTF-only entries (#1,3,4,5,6,8,9,12,14) used the same method and are presumed unreliable pending re-vet. The objects remain genuine dwarf novae (outbursts are real); only their *periods and eclipses* are retracted.

| # | Name | RA | Dec | G | P (min) | Subtype | TESS confirmation |
|---:|---|---:|---:|---:|---:|---|---|
|  1 | MGAB-V701                       | 204.066 | +38.159 | 19.39 | 29.41  | DN       | — |
|  2 | SDSS J154953.41+173939.0        | 237.473 | +17.661 | 19.44 | 116.68 | NL:      | — |
|  3 | PQ J225417.5+074227             | 343.573 |  +7.708 | 18.78 | 232.15 | CV       | — |
|  4 | (unnamed) J0834+1854            | 128.518 | +18.905 | 19.23 | 172.00 | Polar    | — |
|  5 | CRTS J212654.5-012053           | 321.727 |  -1.348 |   —   | 213.03 | Polar    | — |
|  6 | CRTS J164017.8+080822           | 250.074 |  +8.140 | 16.10 | 105.43 | U Gem    | — |
|  7 | SDSS J091935.66+502825.1        | 139.899 | +50.474 | 19.86 |  93.51 | DN       | S21 superoutburst recovered |
|  8 | SDSS J110706.76+340526.8        | 166.778 | +34.091 | 19.48 |  95.84 | DN:      | — |
|  9 | SDSS J115419.06+575750.9        | 178.579 | +57.964 | 20.62 |  21.58 | ER UMa:  | — |
| 10 | CRTS J151836.0-054803           | 229.650 |  -5.801 | 16.50 |  24.64 | DN       | 16.6% per-eclipse depth at ZTF P (3.8σ MARGINAL); BLS best at 172 min ≈ 7× ZTF P → ZTF 24.64-min period may be a 1/7 sub-harmonic alias |
| 11 | SDSS J160419.02+161548.5        | 241.079 | +16.263 | 19.09 | 128.80 | SU UMa   | 23% eclipse |
| 12 | SDSS J080142.37+210345.8        | 120.426 | +21.063 | 18.86 | 115.11 | Polar:   | — |
| 13 | CRTS J051419.8+011120           |  78.583 |  +1.189 | 15.40 | ~~180.05~~ | DN       | **⚠ RETRACTED 2026-05-28 — period + eclipse are artifacts (masked-LS FAP = 1.0 at claimed P; TESS S/N 0.66). Real: DN + 2023 superoutburst only.** |
| 14 | SDSS J115639.48+630907.7        | 179.164 | +63.152 | 20.72 |  29.13 | Polar    | — |

Blind methodology rediscoveries: CRTS J041133.6-090729 → 93.7 min (RKcat 93.6), CRTS J163120.8+103133 → 91.9 min (RKcat 90.3), CRTS J233003.0+303300 → 224.6 min (Hardy 2017 224.6), CRTS J005152.8+204017 → 295.7 min (Dağ 2026 / Bruch 2026 290.6).

## Method

Three corrections vs the v1 cascade:

1. **NSS parallax** preferred over `gaia_source.parallax` (the latter is orbital-motion-biased low for binaries by 1.2–2.5×).
2. **K_obs = rv_amplitude_robust / 2** — Gaia DR3 publishes peak-to-trough, not the semi-amplitude K_1. Verified against Gaia BH2: published K_1 = 21.2 km/s vs rv_amplitude_robust = 36.96 (ratio 1.74 ≈ 2 × (1 - 0.13·e) for e = 0.52).
3. **Filter #30 logg fallback** chain: `logg_gspphot → logg_gspspec_ann → logg_gspspec`. Catches K-giant chromatic-bias false positives that GSP-Phot NaN missed.

Full details + per-source verification in `docs/METHODOLOGY.md`.

Cascade validation: 93% class-level recall on 27 confirmed compact + sub-stellar systems, 14% adversarial-FP rate, 4.5% median |ΔM_2|/M_2 on the Shahaf+ 2024 NS sample.

## Reproducibility

Required external catalogs listed in `CATALOG_DEPENDENCIES.md`.

```bash
# Setup
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

# Production v2 (NSS Orbital + AstroSpectroSB1, G ≤ 13, plx ≥ 1.0)
python scripts/streaming/producer.py
python scripts/streaming/v2_corrected/run_v2.py
# → data/derived/main_hunt_derived_v2.parquet

# Relaxed-producer expansion (G ≤ 15, plx ≥ 0.5)
python scripts/streaming/v2_corrected/producer_relaxed.py
python scripts/streaming/v2_corrected/run_v2_relaxed.py
# → data/derived/main_hunt_derived_v2_relaxed.parquet

# OrbitalAlternative + Validated channel
python scripts/streaming/v2_corrected/run_orbital_alt.py
# → data/derived/main_hunt_derived_v2_alt.parquet

# v3 NSS Acceleration channel
python scripts/streaming/v3_acceleration/run_acceleration.py
# → data/derived/acceleration_v3.parquet

# Interactive single-source web tool
streamlit run scripts/web_tool/app.py
```

Tests: `pytest tests/` (cascade end-to-end + filter unit tests + regression assertions on Gaia BH1, Gaia BH2, HD 1957, HD 81040, HD 111232).
