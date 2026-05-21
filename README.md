# Filter-Cascade Pipeline for Substellar Tertiary Candidates from Gaia DR3 NSS Data

> **This work is experimental and exploratory.** Nothing in this repository has been observationally confirmed. The candidate list is the output of an automated filter cascade applied to public archival data; surviving candidates are tentative and may turn out to be stellar binaries, photometric/activity artifacts, or already-published systems that the literature cross-match missed. **No claims of discovery are made. The pipeline does not detect companions — Gaia DR3 already did. See the "Detection vs. interpretation vs. curation" section below for the precise division of labor.**

## What this is

A software pipeline that searches public Gaia DR3 Non-Single-Star (NSS) data for stars showing astrometric wobbles consistent with brown-dwarf-mass companions (roughly 13 to 80 times the mass of Jupiter), then applies a long sequence of filters to remove sources that are likely stellar binaries, already published, or affected by other systematics.

## A short description of brown dwarfs

Brown dwarfs are objects whose mass falls between approximately 13 and 80 times the mass of Jupiter. They form through gas-cloud collapse like stars do, but they never reach the mass threshold required for hydrogen fusion. They sit between planets and stars in the mass hierarchy.

Finding brown dwarfs in orbit around nearby stars is difficult because:
- They are much fainter than the stars they orbit (a factor of 10⁴ to 10⁶ in visible light).
- Their presence is mainly revealed by their gravitational tug, which makes the host star wobble by a tiny amount.
- The wobble is small — typically a few milliarcseconds on the sky, or a few hundred meters per second in line-of-sight velocity.

## How the pipeline operates

The European Space Agency's Gaia satellite measured the precise positions of more than one billion stars between 2014 and 2017. When a star has a brown-dwarf companion, both objects orbit a common center of mass, and the host star traces a small ellipse on the sky. Gaia's third data release (DR3, published in 2022) identified roughly 440,000 stars showing such wobbles, distributed across two complementary tables:

- **NSS Orbital**: stars where Gaia detected a full orbital cycle in the 3-year observing window, with measured period, eccentricity, and orbital geometry.
- **NSS Acceleration**: stars where Gaia detected only the curvature of the wobble (because the orbit is longer than 3 years), with measured acceleration components but not the full orbit.

This pipeline starts from those Gaia detections and applies the following sequence:

### Stage 1 — Candidate selection
Apply a broad substellar mass cut (under 200 Jupiter masses at face-on minimum) plus quality cuts on parallax, astrometric residuals, and detection significance. This yields about 26,000 candidate sources.

### Stage 2 — Inclination-marginalized mass estimates
For NSS Orbital sources, derive a mass posterior from the published orbital geometry plus assumed host mass. For NSS Acceleration sources, marginalize over an isotropic inclination prior and a log-uniform period prior. These posteriors are pipeline-derived ranking signals and depend on prior assumptions, not direct mass measurements.

### Stage 3 — Filter cascade
Cross-reference against 30+ public catalogs and surveys to filter out:
- Already-published companions (NASA Exoplanet Archive, exoplanet.eu, SIMBAD, plus specialized BD literature: Sahlmann 2011, Barbato 2023, Unger 2023, Mills 2018, Feng 2022)
- Known stellar binaries (Hipparcos-Gaia long-baseline proper-motion anomaly via Brandt 2024 and Kervella 2022, Washington Double Star catalog, SB9 spectroscopic binaries, Tokovinin Multiple Star Catalog, GALAH SB2 cross-correlation flag, Trifonov 2025 HIRES RV-variable flag)
- Activity-driven false signals (TESS rotation period matching the NSS period, Gaia variability classifier, Gaia rotational broadening)
- Specific candidates already identified by the pipeline as imposters during earlier deep-dive examination

### Stage 4 — Multi-archive radial-velocity joint Bayesian analysis
For candidates with sparse RV measurements across multiple archives (HARPS, HIRES, APOGEE, GALAH, NASA Exoplanet Archive, CARMENES), combine the data into a joint Keplerian fit with per-instrument zero-point offsets and per-instrument jitter. This can sometimes reveal signals invisible to any single survey alone. The fit is run with the `dynesty` nested sampler.

## Results

The full cascade reduces about 26,000 initial candidates to **26 tentative substellar candidates** documented in `novelty_candidates.csv` plus **4 cascade by-products** in `cascade_byproducts.csv` (latest release v1.17.0, 2026-05-18; released as a single tag consolidating the v1.16.0 multi-channel-expansion development phase and the v1.17.0 negative-control specificity audit + Filter #29 + HD 76078 removal). 11 of the 26 came from the NSS Orbital/Acceleration pool (v1.7-v1.15); 15 were added in v1.16.0 from the multi-channel SB1 pool expansion: **3 HGCA-corroborated** (HD 156239, HD 156342, HD 11042); **3 Tycho-Gaia CORROBORATED-tier from original pool** (HD 343905, HD 199695, CD-70 5); **3 Tycho-Gaia FLAG-tier strong-BD from original pool** (HD 83408, HD 153386, HD 221068); **3 Tycho-Gaia CORROBORATED-tier widened-66 strong-BD** (HD 22782, HD 1912, HD 90072); **3 Tycho-Gaia CORROBORATED-tier widened-502 borderline-BD** (TYC 4291-119-1, HD 114124, BD+37 3282); and **1 HIP NSS-orbital × Gaia SB1 dual-detected** (BD+14 4993 = HIP 115718). Notable: **HD 22782 and BD+14 4993 both have M_2_marg ≈ 11.5 M_J** — formally below the deuterium-burning boundary, the smallest masses in the project. v1.16.0 also retrieved the full Hipparcos van Leeuwen 2007 NSS catalog (I/311/hip2, 117,955 rows), which revealed that **HD 104828 has Hipparcos Sn=7 (stochastic-motion)** — making it the project's first triple-corroborated candidate (HIP Sn=7 + HGCA χ²=23.6 + Gaia DR3 NSS Acceleration).

**v1.16.0 negative-control correction.** An independent leak-free negative control set (24 stellar imposters labelled by the Gaia SB2/SB2C and APOGEE-SB2 channels — neither of which the cascade uses as a filter) measured the cascade's out-of-sample specificity at **0.33** (Wilson 95% CI 0.16–0.56) and exposed its dominant blind spot: **no filter on the Gaia double-lined-binary (SB2) channel**. The set caught one false positive in the headline list — **HD 76078**, which carries a Gaia SB2 solution (K1=18.8, K2=17.6 km/s, q≈0.93: two luminous stars). HD 76078 was removed from the headline (27→26) and moved to `cascade_byproducts.csv`; **Filter #29 (Gaia SB2/SB2C rejection)** now closes the blind spot. See `docs/dev_notes/NEGATIVE_CONTROL_SET_2026_05_17.md`. Documentation for the other v1.16.0 channels: `docs/dev_notes/SB1_POOL_AND_TYCHO_GAIA_PMA_2026_05_17.md`, `HIPPARCOS_NSS_PORT_2026_05_17.md`.

A separate **frontier supplementary list of 62 no-HIP candidates** is provided in `data/supplementary/no_hip_frontier_clean.csv` — these are sources without Hipparcos cross-match (so HGCA and Kervella corroboration are unavailable) but which pass the cascade with substellar mass + tight 2σ posterior + high NSS detection significance, and are absent from every external published catalog. The frontier list is a target catalog for future Gaia DR4 follow-up rather than a discovery claim. See BENCHMARK.md for details.

### Candidate table — 26 substellar candidates

Pipeline-derived parameters for the 26 substellar survivors (11 NSS
Orbital/Accel + 3 SB1+HGCA + 6 Tycho-Gaia CORROB + 3 Tycho-Gaia FLAG-tier
strong-BD + 3 widened-502 borderline-BD + 1 HIP-orbital×SB1 dual; HD 76078
removed as a Gaia SB2 stellar binary). M₂ is the inclination-marginalized posterior median (1σ range in the next column). HGCA χ² is from Brandt 2024; values in the 5–30 range are independent corroboration of a real companion at 25-yr astrometric baseline. Where no HGCA entry was available (faint M-dwarfs, mostly), the strongest independent astrometric witness is cited instead.

| Name | HIP | V | SpT | d (pc) | NSS solution | P (d) | e | M₂ median (M_J) | M₂ 1σ (M_J) | Indep. witness | Category |
|---|---|---|---|---|---|---|---|---|---|---|---|
| HD 101767 | 57135 | 8.88 | F8 | 82 | Orbital | 486 | 0.45 | 62 | 55–68 | HGCA χ² = 14.2 | substellar |
| HD 104828 ✦ | 58863 | 9.86 | K0 | 33 | Acceleration | ~3600 | — | 41 | 30–55 | HIP Sn=7 + HGCA χ² = 23.6 | substellar (**triple-corroborated**) |
| HD 140895 | 77262 | 9.39 | — | — | Orbital (inner) | 1460 | — | 113 | — | Kervella 17.6σ excess | multi-body (outer) |
| HD 140940 | 77357 | 8.72 | — | — | Orbital (inner) | 924 | — | 183 | — | Kervella 18.4σ excess | multi-body (outer) |
| BD+46 2473 | 90060 | 8.97 | F5 | 286 | Orbital (inner) | 496 | 0.33 | 74 | — | HGCA χ² = 17.8 | multi-body (outer) |
| BD+35 228 | 5787 | 9.08 | G0 | 134 | Orbital (inner) | 560 | 0.40 | 53 | — | HGCA χ² = 18.9 | multi-body (outer) |
| HIP 60865 | 60865 | 12.09 | M dwarf | 41 | Orbital | 501 | 0.25 | 49 | 40–65 | HGCA χ² = 10.5 † | substellar |
| HIP 20122 | 20122 | 13.49 | M2.0Ve | 41 | Orbital | 255 | 0.17 | 64 | 50–85 | HGCA χ² = 5.1 † | substellar |
| BD+56 1762 ‡§ | 72389 | 10.03 | G5/G7 | 98 | Orbital | 197 | 0.42 | 69 | 60–95 | HGCA χ² = 10.3 | substellar (Em\* activity caveat) |
| HD 134574 ¶ | 74357 | 7.01 | G8III | 116 | Acceleration9 | — | — | 29 | 25–35 (marg)/up to 140 (2σ) | HGCA χ² = 17.9 | substellar (Acceleration; mass-ambiguous at 2σ) |
| HD 156239 ※ | 84737 | 8.10 | — | 75 | **SB1** | 110 | 0.47 | 13 | 12–21 | HGCA χ² = 8.7 | substellar (SB1 push, strong BD) |
| HD 156342 ※ | 84506 | 8.15 | — | 86 | **SB1** | 370 | 0.21 | 20 | 17–32 | HGCA χ² = 9.6 | substellar (SB1 push, strong BD) |
| HD 11042 ※ | 8278 | 7.59 | — | 108 | **SB1** | 191 | 0.07 | 59 | 52–80 | HGCA χ² = 9.3 | substellar (SB1 push, solid BD) |
| HD 343905 ★ | — | 9.99 | — | 77 | **SB1** | 42 | 0.51 | 24 | 21–40 | **Tycho-Gaia χ² = 75 (8.57σ)** | substellar (Tycho-Gaia PMa-corroborated) |
| HD 199695 ☆ | 103488 | 7.94 | — | 108 | **SB1** | 62 | 0.22 | 22 | 19–36 | Tycho-Gaia χ² = 7.2 (CORROB) | substellar (SB1 cont. push, strong BD) |
| CD-70 5 ☆ | — | 9.70 | — | 137 | **SB1** | 76 | 0.25 | 59 | 51–96 | Tycho-Gaia χ² = 9.6 (CORROB) | substellar (SB1 cont. push, solid-borderline) |
| HD 83408 ☉ | — | 7.63 | — | 58 | **SB1** | 73 | — | 20 | 17–32 | Tycho-Gaia χ² = 96 (FLAG) | substellar (FLAG-tier strong-BD) |
| HD 153386 ☉ | — | 7.34 | — | 75 | **SB1** | 359 | — | 25 | 22–41 | Tycho-Gaia χ² = 42 (FLAG) | substellar (FLAG-tier strong-BD) |
| HD 221068 ☉ | — | 8.83 | — | 72 | **SB1** | 62 | — | 21 | 18–33 | Tycho-Gaia χ² = 77 (FLAG) | substellar (FLAG-tier strong-BD) |
| HD 22782 ♦ | — | 7.23 | — | 465 | **SB1** | 14 | 0.33 | **12** | 10–19 | Tycho-Gaia χ² = 18.7 (CORROB) | **planet/BD boundary, RUWE=1.03** |
| HD 1912 ♦ | — | 7.05 | — | 486 | **SB1** | 521 | 0.10 | 16 | 14–25 | Tycho-Gaia χ² = 12.9 (CORROB) | substellar (RUWE=1.01 cleanest) |
| HD 90072 ♦ | — | 7.75 | — | 476 | **SB1** | 327 | 0.16 | 19 | 17–30 | Tycho-Gaia χ² = 8.6 (CORROB) | substellar (long-P, RUWE=1.03) |
| TYC 4291-119-1 ♣ | — | 9.98 | — | 255 | **SB1** | 17 | 0.20 | 35 | 31–56 | Tycho-Gaia χ² = 17.2 (CORROB) | borderline-BD (widened-502, RUWE=0.84) |
| HD 114124 ♣ | — | 7.54 | — | 303 | **SB1** | 1179 | 0.53 | 34 | 29–56 | Tycho-Gaia χ² = 11.5 (CORROB) | borderline-BD (widened-502 long-P) |
| BD+37 3282 ♣ | — | 8.30 | — | 365 | **SB1** | 1015 | 0.53 | 38 | 34–62 | Tycho-Gaia χ² = 7.9 (CORROB) | borderline-BD (widened-502 long-P) |
| **BD+14 4993** † | 115718 | 8.62 | — | 1007 | **SB1** | 50 | 0.32 | **12** | 10–18 | **HIP Sn=1 (orbital) + Gaia SB1** | dual-channel, M=11.5 MJ |

† **HIP 60865 and HIP 20122** have HGCA χ² values (10.5 and 5.1) at the bottom edge of the CORROBORATED tier (≥5). Their classification as corroborated is threshold-sensitive; pushing the threshold to χ² ≥ 8 would remove HIP 20122 and leave HIP 60865 marginal. These two are the weakest of the 8 HGCA-corroborated candidates from v1.7.0. Joint orvara HGCA + Thiele-Innes posteriors (rather than the marginalized inclination prior used here) would tighten the verdict — pending in `scripts/orvara_runs/`.

‡ **BD+56 1762** was new in v1.8.0, surfaced by an internal "hunt" run that fed all v7 verdicts back through a corrected Filter #28 (see `BENCHMARK.md` for the v8 cascade audit). It passes HGCA corroboration (χ² ∈ 5–30), is absent from exoplanet.eu and NASA Exoplanet Archive at 10″ PM-corrected radius, and is absent from Sahlmann 2025 G-ASOI lists. **HD 76078 was also promoted in v1.8.0 but REMOVED in v1.16.0**: the independent negative-control set found it carries a Gaia DR3 SB2 (double-lined) solution (K1=18.8, K2=17.6 km/s) — a stellar binary, not a substellar host. It now sits in `cascade_byproducts.csv`; Filter #29 (Gaia SB2/SB2C rejection) prevents recurrence. This is a worked example of why the marg-mass-only verdict is unsafe without an SB2 check: HD 76078's M₂ posterior median (78 M_J) looked borderline-substellar, but the double-lined detection settles it as stellar.

§ **BD+56 1762** has SIMBAD object_type **Em\*** (emission-line star), which raises a chromospheric-activity-imposter risk. The Gaia DR3 quality flags do not show the typical activity-imposter signature (`ipd_frac_multi_peak=1`, `non_single_star=1` Orbital-only, no `duplicated_source` flag), so we keep it in the candidate list with the explicit caveat. A targeted Hα + Ca II H&K activity-amplitude check before any confirmation observation is recommended.

✦ **HD 104828** has Hipparcos van Leeuwen 2007 Sn=7 (stochastic-motion classification) — Hipparcos itself flagged anomalous motion not fit by the single-star model. This is the project's first triple-corroborated candidate, with three INDEPENDENT astrometric witnesses: (1) Hipparcos Sn=7 (1991 epoch, pre-Gaia), (2) HGCA Brandt 2024 χ² = 23.6 (1991→2016 25-yr PMa anomaly), and (3) Gaia DR3 NSS Acceleration9 (2014–2016 internal). The HIP Sn=7 flag was discovered in v1.16.0 (2026-05-17) by bulk-pulling the full van Leeuwen 2007 catalog (I/311/hip2, 117,955 rows). This finding is the strongest pre-Gaia astrometric corroboration in the project; the companion has been detectable since 1991 but never published.

† **BD+14 4993 = HIP 115718** is the first **dual-detected** candidate in the project: pre-Gaia Hipparcos van Leeuwen 2007 Sn=1 (orbital NSS solution, the strongest HIP classification) AND Gaia DR3 SB1 spectroscopic fit. Two independent orbital detections separated by 25 years — Hipparcos in 1991 saw it as orbital astrometrically, Gaia DR3 in 2022 saw it as SB1 spectroscopically. Pourbaix mass function with M_1=1.0 M_sun fallback gives M_2_marg=11.5 MJ (1σ 10-18) — at the deuterium-burning boundary. Caveats: (1) distance 1007 pc (parallax 0.99 mas) is the largest in the candidate list; (2) FLAME M_1 not retrieved, so M_1 could be 2-3 M_sun for an evolved host, scaling M_2 to ~15-20 MJ (still substellar). RUWE=1.02 is ultra-clean. Significance=8.6. RA=351.7, Dec=+15.1 — easy follow-up from any northern facility. This source is the cleanest archival-only multi-channel BD candidate in the project; orbital periods agree across the two independent fits (HIP Sn=1 implies P < 4-yr HIP baseline; Gaia DR3 gives P=50.3 d which is well within that). Surfaced from the v1.16.0 HIP NSS × Gaia SB1 intersection pool (29 sources total, only 2 substellar by mass function).

♣ **TYC 4291-119-1, HD 114124, BD+37 3282** are widened-502 borderline-BD candidates added in v1.16.0. The widened-502 cascade (the M_2_marg 30-80 MJ subset of the 502 widened-pool substellar candidates NOT in the strong-BD 66) surfaced 9 clean CORROBORATED-tier with RUWE<2; these three are the cleanest by combined evidence. All have M_2_marg in 33-38 MJ (solidly substellar but in the upper BD half), low RUWE (0.84-1.06; one statistically below single-star baseline), Tycho-Gaia chi^2 in [7.9, 17.2] CORROBORATED tier, and vetting-clean. TYC 4291-119-1 has the strongest PMa (chi^2=17.2) and lowest RUWE (0.84). HD 114124 and BD+37 3282 are long-period eccentric systems (P=1015-1179 d, e=0.53) that match the Gaia DR3 5-yr baseline.

♦ **HD 22782, HD 1912, HD 90072** are the three cleanest survivors from the **widened SB1 pool** processed in v1.16.0 (V<13, plx>2, sig≥3, P 10-10000 d → 31,668 sources, vs the original 3,049). All three have:
- RUWE in [1.01, 1.03] — astrometrically the quietest hosts in the entire 23-candidate pool (single-star quality astrometry despite SB1 RV reflex);
- HD-named, V<8 (very bright; Gaia DR3 `hipparcos2_best_neighbour` missed them);
- Tycho-Gaia 25-yr PMa χ² in the CORROBORATED tier [5, 30];
- Vetting clean (not in SB9 / exoplanet.eu / NASA Exo / Sahlmann 2025 / v9b cascade).

The widened pool's relaxed parallax cut (plx>2 mas vs original >5) puts these at d ≈ 465–486 pc — farther than the headline list's <200 pc subset, but the multi-channel evidence (SB1 + Tycho-Gaia + clean RUWE) holds despite the distance. **HD 22782** has M_2_marg=11.5 MJ — formally below the 13 MJ deuterium-burning boundary and within the planet-mass tail. The widened pool surfaced 568 NEW substellar candidates total (M_2_marg<80 MJ) and 66 NEW strong-BD (M_2_marg<30 MJ); 3 promoted, 16 more held in Tier-2 (`cascade_widened66_2026_05_17.csv`).

☉ **HD 83408, HD 153386, HD 221068** are FLAG-tier (30 ≤ χ² < 100) Tycho-Gaia PMa-corroborated SB1 candidates added in v1.16.0 (2026-05-17). All three have substellar M_2_marg (19.8, 25.1, 20.6 MJ respectively) with 1σ upper bounds entirely below the deuterium-burning boundary, but their PMa χ² puts them in the FLAG-tier of the Brandt-2024 calibration — meaning "real companion confirmed, mass ambiguous". The mass ambiguity arises because a high PMa χ² is consistent with EITHER a substellar companion at moderate inclination OR a stellar companion at extreme face-on inclination where M_2 sin³(i) makes the apparent mass small. The SB1 fit's K_1 and the low-RUWE host profile (RUWE = 2.2-4.1) favor the substellar interpretation, but disambiguation requires orvara joint HGCA-Thiele-Innes posterior or single-quadrature RV at predicted K. These three are HD-named bright (V = 7.3-8.8) nearby (d = 58-75 pc) targets — easy ground follow-up. They were anonymous to HIP because the Gaia DR3 `hipparcos2_best_neighbour` cross-match table missed them, not because they're below HIP completeness. The Tycho-Gaia PMa channel surfaced six FLAG-tier substellar candidates total; three with M_2_marg < 25 MJ were promoted; three with M_2 30-65 MJ (HD 337746, HD 171384, HD 118687) are held in Tier-2 pending orvara fit.

☆ **HD 199695 and CD-70 5** are Tycho-Gaia PMa-corroborated SB1 candidates added in v1.16.0 (2026-05-17). The 25-yr PMa channel was computed for all 110 anonymous SB1 substellar candidates via per-source Vizier I/259/tyc2 coord queries — 101/110 obtained a Tycho-2 PM, of which 11 land in the FLAG tier (χ² ≥ 30), 32 in the CORROBORATED tier (5 ≤ χ² < 30). After deep vetting (SB9 + exoplanet.eu + Sahlmann 2025 + SIMBAD) the cleanest CORROBORATED-tier promotions were HD 199695 (χ² = 7.16, M_2_marg = 22 MJ, P=62d, V=7.94, distance 108 pc — strong-BD) and CD-70 5 (χ² = 9.6, M_2_marg = 59 MJ, P=76d, V=9.70, distance 137 pc — solid borderline). HD 199695 = HIP 103488 with HIP Sn=5 (no Hipparcos NSS detection); the "anonymous" classification was a Gaia DR3 `hipparcos2_best_neighbour` table miss recovered by direct SIMBAD coord query. CD-70 5 is genuinely southern and below HIP completeness. A third Tier-2 candidate (HD 104289 = Gaia 1576108450508750208) was rejected at the vetting stage: published as HD 104289 b in exoplanet.eu and with a Sahlmann 2025 verdict, so not novel.

★ **HD 343905** is the strongest Tycho-Gaia PMa-corroborated SB1 candidate added in v1.16.0. Originally surfaced as an anonymous SB1 source (Gaia DR3 4521257204320883712, no HIP cross-id, M_2_marg = 24.5 M_J, P = 41.9 d, e = 0.51, K_1 = 1.42 km/s). SIMBAD coord-resolution returned its HD identifier (HD 343905, fainter than HIP completeness V<8 so HIP didn't observe it but the HD catalog did). The killer witness is the **Tycho-2 (1991) vs Gaia DR3 (2016) proper-motion anomaly**: pm_RA disagreement of -8.0 mas/yr (TYC) vs -17.58 mas/yr (DR3) → 8.57σ offset in RA alone → χ² = 75.1 over both RA and Dec components. This is well above the Brandt 2024 HGCA-system "FLAG" threshold (χ² > 30). The substellar M_2_marg = 24.5 M_J from the SB1 fit + the χ² = 75 PMa together strongly support a BD-mass companion. HD 343905 is northern (Dec = +23.5) and reasonably bright (V = 10.0), so confirmation requires only single-quadrature RV at K ≈ 1.4 km/s level. The Tycho-Gaia PMa channel is the project's third independent astrometric witness type (alongside HGCA Brandt 2024 for HIP-named candidates and HIP Sn=7 for direct Hipparcos NSS).

※ **HD 156239, HD 156342, HD 11042** are new in v1.16.0, surfaced by the NSS SB1 (pure single-line spectroscopic binary) pool push. These three are HD-named bright (V ≈ 7.6–8.2) targets whose Gaia DR3 NSS solution type is pure SB1 — Gaia solved their host RV reflex but did not fit an Orbital astrometric solution (the wobble was below the Orbital threshold). M₂ is derived from the Pourbaix spectroscopic mass function f(M) = K_1³ P (1 − e²)^(3/2) / (2 π G), marginalized over an isotropic-inclination prior, with M_1 from `mass_flame` (FLAME isochrone fit). All three pass HGCA Brandt 2021 χ² in the [5, 30] CORROBORATED tier (independent 25-yr Hipparcos–Gaia PMa corroboration), are absent from SB9 (Pourbaix's own orbital-solution catalog at 5″), absent from exoplanet.eu (at 30″), absent from the Sahlmann 2025 verdict table, and absent from the v9b cascade's output (the v9b cascade ignored SB1 sources entirely; the SB1 push patches that gap). Confirmation requires ground-based RV time-series for the system parameters; the SB1 sources are bright enough (V < 8.5) that even a single quadrature epoch at K ≈ 0.5–1.3 km/s amplitude (predicted from the SB1 fit) is decisive at typical 30 m/s instrument floors. See `docs/dev_notes/SB1_POOL_AND_TYCHO_GAIA_PMA_2026_05_17.md` for the full vetting cascade.

¶ **HD 134574** is new in v1.15.0, surfaced by extending the conditional-RUWE rule (v1.9.0 Fix C) from Orbital-only to also include Acceleration solution types (Fix E). Acceleration sources have the same physical orbital-reflex cause of elevated RUWE as Orbital sources, but the v9 cascade only applied the lax cut to Orbital types. The G8III host (M_star ≈ 2.24 M_☉) means the cascade-derived M_2 is more sensitive to the assumed host mass than the main-sequence candidates above. HGCA χ²=17.9 independently corroborates a real 25-year proper-motion anomaly. The 2σ_hi=140 M_J mass-ambiguous tail extends into stellar regime — this is a tentative substellar candidate that requires either Gaia DR4 (which will publish per-transit RV for V=7.0, σ_K ~ 10 m/s) or long-baseline ground-based RV monitoring (P > 3 yr from the Acceleration solution, so multi-year campaign) to constrain the period and refine the mass. Dec=-33.6° → Southern (ESO/La Silla accessible: HARPS, FEROS, CORALIE). Acceleration-class candidate; mass interpretation more uncertain than the Orbital-class candidates above due to the unconstrained period.

### Cascade by-products (separate file: `cascade_byproducts.csv`)

Two sources that surfaced through the cascade but **do not belong in the substellar-candidate list**:

| Name | HIP | V | SpT | NSS solution | M₂ median (M_J) | M₂ 1σ (M_J) | Why moved to by-products |
|---|---|---|---|---|---|---|---|
| HD 75426 | 43197 | 6.72 | F5IV/V | Acceleration7 | 282 | 100–1343 | 1σ range wider than the BD/star boundary; median lands in early-M-dwarf regime. Mass-ambiguous, not substellar. |
| HD 120954 | 67777 | 8.76 | G1V | Acceleration | 1637 | 1018–3621 | Pipeline itself classifies as stellar (~1.56 M_⊙). Genuinely interesting as a methodology by-product (5 independent witnesses converging on a ~70-yr stellar companion) but not a substellar candidate. |

The 4 BD+ / HD multi-body rows in the substellar table have the inner orbit characterized from NSS but the outer companion mass is inferred from Kervella PMa excess and is not directly observed.

### How the candidates were arrived at

Of about 12 sources that received individual deep-dive investigation in v1:

- 7 sources turned out to be likely stellar M-dwarf companions in eccentric or moderate-inclination orbits.
- 2 sources turned out to be previously published planets/brown-dwarf candidates that the initial catalog cross-match missed because of naming or catalog-policy gaps. These cases helped identify which catalogs needed deeper cross-matching.
- 1 source turned out to be a known hierarchical triple system already catalogued in the Tokovinin Multiple Star Catalog and the Washington Double Star catalog (the latter since 1876).
- 1 source emerged as an apparent stellar companion discovery (HD 120954 in the table above), with multiple converging astrometric and radial-velocity signals. This is also tentative and depends on the joint fit.
- A handful of sources have astrometric evidence and partial archival radial-velocity statistics that are consistent with brown-dwarf-mass companions, but lack sufficient observational data for independent verification.

The v2 pipeline (Filters #27-30: documented-FP, exoplanet.eu coord, HGCA chi² tier, conditional RUWE) applied to the full 9,498-source pool surfaced 22 HGCA-corroborated candidates + 15 mass-ambiguous flagged candidates. From this 37, 2 truly novel substellar candidates with HIP cross-match were promoted (HIP 60865 and HIP 20122) — both originally filtered out of v1 because the uniform RUWE < 2 cut is inappropriate for solution types where orbital reflex is the signal.

The v8 pipeline (released 2026-05-17) fixes a silent failure in Filter #28 (exoplanet.eu coord cross-match): the v2-v7 production pool never propagated `ra`/`dec` from Gaia DR3, so the coord-match was a no-op for every source. The v8 fix auto-fetches Gaia DR3 `ra`, `dec`, `pmra`, `pmdec` per source, projects coords from epoch J2016.0 back to J2000.0, and matches at a 10″ radius. This newly rejects 33 sources that had silently survived as published-in-exoplanet.eu, including 6 in the previously-CORROBORATED or FLAG tiers: HD 33636 (HIP 24205), HD 68638 (HIP 40497), BD+05 5218 (HIP 117179), HD 30246 (HIP 22203), L 194-115 (HIP 60321), G 239-52 (HIP 75202). Two further novel candidates were promoted from the resulting v8 CORROBORATED pool: HD 76078 (HIP 43870) and BD+56 1762 (HIP 72389).

The v9 pipeline (this release, 2026-05-17) adds four cascade recall improvements identified by a Sahlmann-disagreement audit:
1. **Fix A** — Sahlmann CONFIRMED_BINARY_FP filter rejects HD 185501 (cascade FP corrected).
2. **Fix B** — SIMBAD object_type=`**` filter demotes HD 222805 (resolved visual hierarchical binary).
3. **Fix C** — RUWE verdict-logic re-sync (filter labels were drifted from conditional-RUWE rule introduced post-v2).
4. **Fix D** — Kervella-substitute-for-HGCA promotion for short-period orbits (HGCA's 25-yr arc averages out P < 4 yr orbits; Kervella's 10-yr arc retains them).

Net effect: cascade recall on Sahlmann's 12 confirmed brown dwarfs in our pool improved from 8/12 (67%) to 11/12 (92%). The substellar-candidate list remains at 10 — all four newly-CORROBORATED sources from v9 are already published by Sahlmann 2025 (HD 5433, HD 89707, HD 92320) or in Sahlmann's candidate tier (BD+32 92). v9 is therefore a methodology / recall hygiene release rather than a candidate-list change.

Cross-checked against 10 recent published catalogs (Gaia DPAC 1843 BD, Halbwachs 2023 binary_masses, Marcussen+Albrecht 2023, Stevenson 2023 BD-desert, Brandt+Sosa 2025, Kiefer 2025, Wallace 2026, Stefansson 2025 G-ASOI, Halbwachs+Holl 2024 ML, Cooper 2024 UCD Companion): **none of the headline substellar candidates are in any of these catalogs as a published-orbit companion**. None have a published orbital characterization. (Caveat added v1.16.0: this "no published companion" check does NOT include the Gaia DR3 SB2/SB2C channel, which is itself a published double-lined detection — Filter #29 now screens that channel separately. HD 76078, formerly cited here, was removed in v1.16.0 precisely because it carries a Gaia SB2 solution; BD+56 1762 has 24 ADS bibcodes but none claim a substellar companion mass.)

> **A note on what "novelty" means here.** Each of those 10 catalogs applies its own selection criteria (e.g., Kiefer 2025 *explicitly excludes* NSS-tagged sources; Brandt+Sosa 2025 requires archival RV; Halbwachs 2023 binary_masses requires spectroscopic K₁). Our 11 fall in the *intersection of selection-criterion gaps* across these catalogs — not in a region where someone looked and found nothing, but in a region no one's currently searching with the specific filter combination we use (conditional RUWE × multi-pool NSS × HGCA χ² tier × M-dwarf hosts permitted). Finding parameter-space regions other catalogs don't actively probe is **necessary** for novelty but not **sufficient** to claim real undiscovered companions. The candidates are tentative either way; the "novelty" label refers to the absence of prior published orbital characterization, not to evidence of intrinsic rarity. See `CATALOG_COMPLETENESS_ANALYSIS.md` for the per-catalog selection-criterion breakdown.

See `REPORT.md` for the detailed methodology and `novelty_candidates.csv` for the full column set (including per-candidate Bayesian posterior scores and filter-cascade trace). Many parameters in the candidate table are pipeline estimates (e.g., inclination-marginalized mass posteriors) rather than direct measurements.

### Methodology validation

The cascade has been benchmarked against a 71-entry truth set assembled from Sahlmann 2025 verdicts and the Gaia DR3 documented-FP list. Headline numbers:

| Metric | v2 (released) | v3 (proposed tie-breaking) |
|---|---|---|
| In-pool novelty recall | 58.8% | 85.3% |
| End-to-end specificity | 72.7% | 72.7% |
| Documented-FP catch (Filter #27) | 100% | 100% |
| Period recovery (median \|ΔP/P\|) | 0.005% | unchanged |
| Mass recovery (median \|ΔM/M\|) | 6.5% | unchanged |

See `BENCHMARK.md` for the full report (confusion matrix, per-filter destruction analysis, FP escapes, parameter-recovery table). The benchmark is reproducible from this repo with `make benchmark` once `config.yaml` is configured — see `REPRODUCIBILITY.md` for the quickstart.

## Detection vs. interpretation vs. curation — what is novel and what is not

Reviewers and users sometimes ask: where exactly does the novelty in this repository sit, given that Gaia DR3 has already published orbital fits for every source we look at? The answer requires careful separation of three layers.

### What Gaia DR3 already published (not novel to us)

For every source in our candidate list, Gaia DR3 (June 2022) already published in the `nss_two_body_orbit` or `nss_acceleration_astro` tables:

- The detection itself (i.e., "this source's residuals to a single-star astrometric model are statistically significant")
- The orbital period, eccentricity, time of periastron, and Thiele-Innes geometric constants (when Orbital solution applies)
- The photocenter semi-major axis (`a_phot`) and its uncertainty
- The acceleration vector and its uncertainty (when Acceleration solution applies)
- Internal quality and significance metrics

For HIP-named sources, **Brandt 2021/2024 (HGCA)** independently published a Hipparcos-to-Gaia proper-motion-anomaly χ² statistic based on the 25-year arc between the Hipparcos catalog (epoch 1991) and Gaia DR3 (epoch 2016). For a subset of those, **Kervella+2022 (H2G2)** published a separate Tycho-Hipparcos-to-Gaia 10-year arc PMa SNR. Both are independent detections of the wobble, computed without using Gaia's internal NSS pipeline.

For 5,099 NSS sources, the Gaia DPAC team also published in **`gaiadr3.binary_masses`** (Halbwachs+ 2023) a joint photometric+astrometric+spectroscopic decomposition that gives a direct M_2 measurement (where the geometry was solvable). That table is the closest thing Gaia DR3 has to a published mass.

### What our pipeline derives (standard calculations on Gaia outputs)

Given the published `a_phot`, period, eccentricity, and an assumed host mass M_1 (typically from Gaia BP-RP color and isochrone), we compute:

- `M_2_face_on`: the lower bound on the companion mass, assuming inclination i = 90° (edge-on), via the Pourbaix mass function applied to `a_phot`
- `M_2_marginalized`: the most-probable companion mass, marginalizing over an isotropic inclination prior

These are standard derivations that anyone with the Gaia NSS catalog and a copy of the Pourbaix mass-function formula could reproduce.

### What our pipeline actually contributes (the novelty layer)

What is novel is the **cross-reference and curation layer**:

1. **Mass interpretation as substellar.** For each Gaia NSS solution, the derived M_2 is checked against the substellar threshold (~80 M_J). The interpretive claim is "this NSS Orbital solution corresponds to a brown-dwarf-mass companion." Nobody in published literature has made this claim for the candidates in `novelty_candidates.csv`.

2. **Cross-match against 30+ published catalogs.** We test whether each candidate is already in exoplanet.eu, NASA Exoplanet Archive, Sahlmann 2025, Halbwachs/Gaia DR3 `binary_masses`, Marcussen+Albrecht 2023, Stefánsson 2025, Trifonov 2025 HIRES, and others. Our headline 10 are absent from all of them as substellar companions.

3. **Multi-witness corroboration.** For HIP-named candidates, we layer the Gaia NSS detection with the Brandt 2024 HGCA χ² (25-yr arc) and Kervella 2022 H2G2 SNR (10-yr arc). Triple-corroborated candidates are detected by Gaia, by HGCA, and by Kervella — three independent astrometric baselines from three different teams. The triple coincidence is what makes them more robust than NSS-only candidates.

3b. **Independent wobble re-detection (v1.11.0).** As of v1.11.0, the cascade includes a fourth independent channel: for every headline candidate, we compute the 25-year Hipparcos-to-Gaia proper-motion anomaly directly from raw catalog positions (Hipparcos van Leeuwen 2007 + Gaia DR3) without using Brandt 2024's intermediate HGCA processing. See `scripts/independent_pma_verification_2026_05_17.py` and `data/intermediate/independent_pma_verification.csv`. All 10 headline candidates show real Δμ > 0 at >2σ in this independent calculation, with median agreement of 1.4× to Brandt's published χ². For HD 76078 and BD+56 1762, which lack any RV time-series, this independent PMa is the primary verification that the orbital signature is not an artifact of the Gaia NSS pipeline.

4. **Methodology hygiene.** During cascade development we identified and fixed several non-trivial bugs in the published-systems vetting flow: Filter #28's silent failure since v1.0.0 (ra/dec never propagated), Sahlmann CONFIRMED_BINARY_FP filter missing, RUWE verdict-logic drift, SIMBAD `**` visual-double filter missing, WD-host M_1 default assumption (still pending). These are useful methodology contributions even if no individual candidate ends up confirmed.

5. **Tentative claim on 28 sources with zero SIMBAD bibcodes.** Of the 63 no-HIP frontier supplementary candidates, 28 have no SIMBAD bibcodes at all. For these, no published literature exists about the source besides the Gaia DR3 catalog entry itself. If we publish their cascade-derived parameters, that is the first characterization of these objects. This is the closest thing in the repo to a genuine first-detection claim — but even here, the detection itself was Gaia's; we're the first to *characterize* it.

### What this pipeline still does not do

- We do not re-fit Gaia's epoch-level astrometry. Gaia DR3 did not release per-transit data; that arrives with DR4 in December 2026. Our pipeline operates on the published NSS catalog outputs.
- We do not perform joint orbital fits combining Gaia astrometry with archival radial-velocity time-series. Some `scripts/orvara_runs/` exist for individual candidates (HIP 20122, HIP 60865, HIP 91479) but this is not yet end-to-end for all 10. A joint RV+astrometric fit would give a direct M_2 measurement without the inclination-prior assumption.
- We do not propose or carry out new telescope observations.
- We do not make discovery claims. Confirmation of any candidate requires either Gaia DR4 (free, December 2026) or targeted ground-based RV (paid, telescope-allocation dependent).
- It has not been peer-reviewed.

### How a reader should think about the 10 candidates

The honest framing is: "Gaia DR3 detected these 10 stars as astrometric binaries with orbital periods consistent with substellar mass at moderate inclinations. Brandt 2024 and Kervella 2022 independently see the wobble at different baselines. No published companion catalog has interpreted any of them as brown dwarfs. Confirmation observations are required to distinguish substellar from stellar-at-moderate-inclination interpretations." That is the strongest defensible statement.

## What this pipeline does not do

- It does not propose or carry out new observations. All data come from public archives.
- It does not make discovery claims. Surviving candidates may be stellar at moderate inclinations, may be affected by systematics not captured by current filters, or may be pre-published in sources not in the cross-match.
- It does not provide definitive mass measurements. The reported masses are pipeline-derived from astrometric geometry plus prior assumptions on inclination and period.
- It has not been peer-reviewed.

## Paths forward for the tentative candidates

Confirmation of the tentative candidates listed in `novelty_candidates.csv` would require either:

1. **Gaia DR4** (currently scheduled for December 2026 with public release expected in early 2027). DR4 will publish per-transit radial velocities and intermediate astrometric data for all sources, which can resolve the inclination–mass degeneracy through joint epoch-level inference. This costs nothing and requires no new telescope time. For HD 101767, for instance, the 21 individual radial-velocity epochs that produced the summary `rv_amplitude_robust = 3.0 km/s` will become public.

2. **Targeted radial-velocity observations** with northern small-aperture spectrographs (TRES at Whipple, FIES at Nordic Optical Telescope, SOPHIE at Observatoire de Haute-Provence, HARPS-N at Telescopio Nazionale Galileo) or southern equivalents (CHIRON at SMARTS, FEROS at MPG 2.2m). Typically 2–6 epochs at orbital quadrature spacing per target. This requires telescope-allocation proposals that this archival-only pipeline does not address.

3. **ESA PLATO** (launch December 2026 — the same window as Gaia DR4). PLATO detects companions by transit photometry, which requires edge-on geometry (i ≈ 90°) — exactly orthogonal to our astrometric / RV-reflex / PMa detection channels, all of which favor non-edge-on orbits. A transit detection pins sin(i) ≈ 1, collapsing the SB1 minimum mass M_2 sin(i) onto the true M_2 and **resolving the mass–inclination degeneracy** that is our principal caveat (a 13–80 M_J brown dwarf produces a ~1–2% transit at ~Jupiter radius, well above PLATO's noise floor for V<11 hosts). PLATO also delivers asteroseismic host parameters (mass ~10%, radius ~2%, age ~10%) for every bright in-field star regardless of transits, which tightens the Pourbaix M_2 estimates that currently depend on `mass_flame` or a 1.0 M_sun fallback. Cross-match (see `docs/dev_notes/PLATO_FIELD_CROSSMATCH_2026_05_17.md`): **0 of 27 candidates fall in the confirmed LOPS2 southern field; 2 (BD+46 2473, BD+37 3282) fall in the provisional LOPN1 northern deep field** — though both have long periods (496 d, 1015 d) that make transit detection geometrically unlikely, so for these two PLATO's asteroseismic host characterization is the realistic gain. The strategic implication is that future candidate searches should prioritize the LOPS2/LOPN1 footprints, where PLATO transit follow-up is automatic, and that our short-period candidates (HD 22782 P=14 d, HD 221068 P=62 d, HD 156239 P=110 d) are strong PLATO guest-observer / step-and-stare targets.

## Repository contents

- `README.md` — this file (non-technical introduction)
- `REPORT.md` — technical methodology and results in more detail
- `novelty_candidates.csv` — tentative candidate list with pipeline-derived parameters
- `scripts/` — pipeline source code (Python; uses `polars`, `numpy`, `astropy`, `dynesty`, `orvara`)
- `CATALOG_DEPENDENCIES.md` — list of external catalogs the scripts assume are locally cached, with URLs for download
- `CANDIDATE_FP_AUDIT.md` — per-candidate audit against Gaia DR3 documented false-positive sources (cosmos.esa.int/web/gaia/dr3-known-issues) and independent vetting catalogs (Sahlmann 2025, Stefansson 2025, Tokovinin MSC). Adds an `fp_risk_tier` column to `novelty_candidates.csv`.
- `candidate_bayesian_scores.csv` — per-candidate Bayesian confidence score consolidating all diagnostics. Columns include `P_real_companion`, `P_substellar_given_real`, `P_real_substellar`, and the log-odds contributions from each evidence factor (significance, solution_type, baselines, RV, RUWE, etc.). The same probabilities are mirrored into `novelty_candidates.csv`.
- `docs/dev_notes/EXPANSION_AUDIT.md` — exploration of additional archival directions: AstroSpectroSB1 deep-dive (37 BD candidates with joint astro+spec orbit detection), CPM wide-companion check (0 contamination for our 8), cluster-member cross-match (none in Hunt+Reffert 2023), TESS long-period transit search for HD 101767 / HD 104828 (no transit signal), SB1+Kervella PMa hierarchical-triple expansion (61 candidates).
- `data/supplementary/astrospectrosb1_candidates_supplementary.csv` — 37 AstroSpectroSB1 candidates surfaced by the expansion audit. NOT promoted to `novelty_candidates.csv` because they need further per-candidate vetting; documented as a separate supplementary pool.
- `data/supplementary/sb1_kervella_hierarchical_triple_candidates_supplementary.csv` — 61 NSS SB1 sources with substellar K1 and Kervella PMa cross-match (potential hierarchical triples). NOT promoted to `novelty_candidates.csv`; documented as a supplementary expansion of the multi-body candidate category.
- `cascade_byproducts.csv` — 2 sources surfaced by the cascade that do **not** belong in the substellar-candidate list: HD 75426 (mass-ambiguous, posterior straddles BD/star boundary) and HD 120954 (apparent stellar-mass companion, methodology by-product).
- `docs/dev_notes/` — iterative dev notes preserved as audit trail: V2_SCAN_REPORT, POOL_VETTING_REPORT, TASKS_A_F_REPORT, DECENT_CANDIDATES_CHECK, SUPP_AND_CATALOG_EXPANSION. Not load-bearing for the headline result; kept for reproducibility of the iteration history.
- `data/intermediate/` — intermediate scan products (v2_scan_corroborated_22, v2_scan_flag_mass_ambiguous_15, v2_scan_published_systems_caught_via_exoeu_coord, multibody_v2_hgca_tier, decent_candidates_check, supplementary_pool_27_tiered). Used by the cascade run; not headline outputs.

## Setup notes

The pipeline scripts expect catalog files to be present at a location set via the `GAIA_NOVELTY_DATA_ROOT` environment variable. The required catalogs are listed in `CATALOG_DEPENDENCIES.md` along with their public access URLs. The catalogs themselves are not redistributed in this repository.

Python package dependencies are listed in `requirements.txt`. Install with `pip install -r requirements.txt`.

## Reproducibility status

This repository is **not a turn-key reproduction package.** The pipeline source code is included, but the input data (Gaia DR3 NSS tables, HGCA, Kervella, Penoyre, Tokovinin MSC, NASA Exoplanet Archive, WDS, HARPS RVBank, HIRES, APOGEE, GALAH, LAMOST, etc.) totals roughly 100–200 GB of public catalog downloads that are not bundled here. Each catalog is listed in `CATALOG_DEPENDENCIES.md` with its public download URL.

The final candidate output (`novelty_candidates.csv`) is the result of multiple iterative passes, manual deep-dive verifications, and methodology refinements rather than a single automated pipeline run. Running the scripts blindly on a fresh catalog cache may produce a candidate list that differs from this CSV. See `REPRODUCIBILITY.md` for the full scope statement, script ordering notes, and known reproducibility caveats.

## A note on tone

The methodology lessons and filter rules in this repository were accumulated through iterative deep-dive analysis of individual sources, many of which turned out to be stellar in the end. The lessons themselves are heuristic and have not been independently validated. The pipeline is intended as a tool for examining Gaia DR3 NSS data systematically, not as a confirmed discovery system.

## Contact

For questions about specific candidates, the filter cascade, the v2 scan methodology, or anything else in this repository:

- **GitHub Issues** — [open an issue](https://github.com/alejandrozarco/gaia-dr3-substellar-novelty-search/issues) for technical bugs, candidate-parameter clarifications, or specific cross-reference requests.
- **GitHub Discussions** — [start a discussion](https://github.com/alejandrozarco/gaia-dr3-substellar-novelty-search/discussions) for open-ended threads: "anyone planning RV follow-up on candidate X?", methodology-question threads, etc.
- **Email** — `alejandro.zarcos@gmail.com` for things that don't fit a public thread (e.g., in-prep papers that overlap with a candidate, private Gaia DPAC follow-up status, coordinated submissions).

If you publish a confirmation, falsification, or independent re-analysis of any candidate in `novelty_candidates.csv`, please cite this repository's Zenodo DOI (see `CITATION.cff` for the concept DOI and version-specific DOIs).
