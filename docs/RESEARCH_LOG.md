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

---

## Net state (as of 2026-06-03)

**0 confirmed novel compact objects across every archival lane.** All methods
validated. Remaining expected value is **XP-at-scale** (a build, highest ceiling)
and **fresh data** (Gaia DR4, 2 Dec 2026; eROSITA-east; Rubin/LSST). Breadth on
existing data is exhausted. Active candidates (all unconfirmed, pending DR4): see
`docs/CANDIDATES.md` + the per-object journals.

Pending lanes (network-gated): #101 ELM/sdB + NS/BH tail, #102 ETV dark/compact
tertiary, #103 XP-catalogue ingest, #104 CPM wide-companion check.

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
