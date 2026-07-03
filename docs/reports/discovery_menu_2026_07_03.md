# Discovery-avenue menu — 2026-07-03 (adversarially refereed wishlist)

Product of a 20-agent ideation workflow (6 orthogonal-lens generators → triage → per-idea adversarial
feasibility referees → synthesis). 29 raw ideas → 12 triaged → **8 GO-IF survivors, 4 NO-GO**.
Every survivor has a cheap gate (0.5–2 days) that must pass before committing to the build.
Full referee reports: workflow wf_31893a88-247 output (session archive); key facts inlined below.

**Bottom line (synthesizer, verbatim spirit):** nothing here rivals Gaia DR4 (2 Dec 2026) for the core
dark-companion goal — all 8 lanes combined honestly expect ~1–5 genuine novelties, mostly CV/accretor-grade;
dormant-BH mode remains zero. BUT the top-3 are complementary to DR4 (different magnitude/wavelength/time
axes), two have live named scoop risk, and the three gates cost ~2.5 days total. Rational play: run gates
for ranks 1–3, commit only where gates pass; ranks 4–8 are fallback ballast.

## The menu

1. **eRASS1 register classification (STARTED 2026-07-03 — gate dispatched).** Classify our 137 uncatalogued
   eRASS1-Gaia sources with ATLAS forced photometry + ASAS-SN Sky Patrol v2 (both public; ATLAS covers
   dec<−50). Referee-corrected facts: sample is G 12.2–19.0 (median 15.9), all plx/err>5; 105/137 = likely
   coronal K/M rotators (housekeeping); **discovery pool = 16 CMD-bridge objects, 10 at dec<−30** — the
   niche ZTF-based competitors physically cannot reach. Honest yield 1–4 new archive-confirmed accreting
   binaries. Effort 1.5–2.5 wk. GATE: crossmatch the 16 bridge ids vs arXiv:2504.10794 (177 new CV cand.),
   Freund+2024 HamStar (arXiv:2401.17282), arXiv:2606.01085 (43 compact-binary cand.), fresh VSX/SIMBAD;
   GO only if ≥5 southern bridge objects survive unclaimed. Bridge ids: 5086290113773259776,
   5518166598858566528, 4933000119641126912, 5700916082915916032, 5698053847990609920, 4822674126477654784,
   6342358797048816128, 2993086056306989824, 6006980297150138112, 5713277789070104960, 6414835064496112640,
   3161546596480983040 (=Object B, already deep-dived), 5289353281310733696, 5808732887468490368,
   4688120596457178624, 4715379894891417856. Localization caveat at dec<−30: ATLAS 6.5″/ASAS-SN 8″ pixels →
   use NSC DR2 (Astro Data Lab) + Gaia neighbour census; downgrade any claim with a neighbour within ~10″.
   Cap polar/spider claims at "candidate" (spectrum-gated); DN confirmations = ≥2 independent-survey outbursts.

2. **One-dip wonders (DASCH period recovery for single-eclipse mysteries).** Union the 2025 dip inventories
   (ASAS-SN 13 = arXiv:2507.19594; ZTF 81 bright subset = arXiv:2508.03964) + VSX slow-fades + Gaia-alert
   fades; for quiescent B≲14 targets search DASCH DR7 century plates for prior eclipses → period → falsifiable
   next-eclipse prediction (ASASSN-24fw template, headline-grade archive-only paper). 1–2 wk. SCOOP RISK:
   Tzanidakis/Davenport are DASCH-native — move-this-month lane. GATE (1 day): funnel census; GO if ≥~25
   plate-analyzable targets, NO-GO below ~10. Two-event chance-alignment FAP must be a first-class deliverable.

3. **DESI DR1 repeat-RV dark-companion hunt (G=16–20).** The only lane at the core quarry, in the regime
   Gaia RVS (and DR4, limit ~16.2) never reaches. MWS epoch-RV tables × ZTF periods → f(M). Honest yield:
   ~10–30 clean high-ΔRV survivors, 0–2 reaching f(M)>1; mode for genuine NS/BH = zero; ceiling = the one
   outcome that changes the project. 3–4 wk. Jan-2026 RNAAS flag-plant exists (assume competitors mid-build).
   GATE (1 day): pull MWS epoch-RV for a few healpix; kill if >~90% of epoch pairs are same-night splits
   or <~100–200k sources have multi-day baselines within ZTF r<18.5 footprint.

4. **DASCH Mira period-drift census** (southern/neglected Miras; He-shell flashes; null publishable —
   JAAVSO certain, A&A plausible). 2–4 wk. GATE: 20–30 known-period pilot; need ≥5–8 maxima per 15–20 yr
   window and <~1% period recovery vs ASAS-SN.
5. **TESS EB dP/dt census** (our cache + refit pipeline; 50–200 robust dP/dt; catalogue paper, not discovery;
   red-nova-precursor EV ≈ 0). 3–5 wk. GATE: top-20 drift systems — do ASAS-SN/ZTF minima give ~1–2 min timing?
6. **Tidally-tilted-pulsator sweep** (zero-download, hours of compute, 0–3 new TTPs; field owners announced
   same survey 2022). GATE: ADS check for a 2025–26 systematic survey + blind-recover a known TTP + census ≥80 targets.
7. **Plate-era eruption archaeology** (DASCH DR7 × our 6,104-object accretor store + register; 0–2 new
   historical symbiotic novae, each publishable; ~15–20 known ever). GATE (half-day): DR7 pipeline LCs must
   cleanly show ~20 known plate-era eruptions (PU Vul, RT Ser, RR Tel, HM Sge, T CrB 1946, V2487 Oph).
8. **Prša+2022 ephemeris erratum/failure-tail note** (RNAAS/Zenodo data note; Kostov 2025 refreshed 2,065
   already; partially duplicates task #128 machinery). GATE: refit cache, count true failure tail, check
   whether Villanova live catalogue refits ephemerides.

## NO-GOs (do not revive without new facts)
- **Apsidal-motion survey of the cache**: Thornton+2025 (arXiv:2512.07934) already ran the blind screen on
  1,590 TESS EBs incl. the hidden-companion product; Claret & Giménez own the relativity tests.
- **Pixel-level eclipse host reassignment**: false premise — Prša+2022 vetting ran per-candidate pixel-level
  centroid localization (CONTAMINANTE, 3× weight); catalogue is pre-screened for exactly this.
- **Circumbinary dust occultations in EB residuals**: occurrence ≈ 0 in bright field EBs; chromaticity
  confirmation leg breaks on saturation.
- **SDSS-V DR19 spectral unlock**: referee EXECUTED the join — measured 0 spectra for all headline targets;
  footprint structurally wrong (APO-only release vs candidate median dec −45°).
