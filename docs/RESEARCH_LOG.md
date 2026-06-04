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

---

## Net state (as of 2026-06-03)

**0 confirmed novel compact objects across every archival lane.** All methods
validated. Remaining expected value is **XP-at-scale** (a build, highest ceiling)
and **fresh data** (Gaia DR4, 2 Dec 2026; eROSITA-east; Rubin/LSST). Breadth on
existing data is exhausted. Active candidates (all unconfirmed, pending DR4): see
`docs/CANDIDATES.md` + the per-object journals.

Pending lanes (network-gated): #101 ELM/sdB + NS/BH tail — **INFRA-NULL, never
actually tested** (2026-06-03 re-vet); #102 ETV dark/compact tertiary —
**INFRA-NULL, never tested**; #103 XP-catalogue ingest; #104 CPM wide-companion
check; #108 re-vet orphan TYC 7350-249-1; #110 regenerate 5858574 post-bugfix.

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
