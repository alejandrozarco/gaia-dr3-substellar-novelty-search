# Comprehensive v2-pipeline scan report (2026-05-13)

After surfacing two methodology issues during the supplementary-pool vetting
(inappropriate RUWE cut for AstroSpectroSB1; missing exoplanet.eu coord-match
+ HGCA chi^2 tier filter), pipeline v2 was built with three new filters:

  #1 Conditional RUWE: skip RUWE<2 cut for solution types where orbital
     reflex is expected to elevate RUWE (Orbital, AstroSpectroSB1,
     OrbitalTargetedSearchValidated)
  #3 exoplanet.eu coord cross-match within 5 arcsec
  #4 HGCA Brandt 2024 chi^2 tier filter for HIP-named candidates:
     chi^2 > 100 -> REJECTED stellar
     chi^2 30-100 -> FLAG mass-ambiguous
     chi^2 5-30 -> CORROBORATED real companion
     chi^2 < 5 -> isolated (no outer body)

The full v2 cascade was applied to the **9,498-candidate combined NSS pool**
(2,673 Orbital substellar + 6,825 Acceleration substellar).

## Headline funnel

| Verdict | N |
|---|---:|
| SURVIVOR_no_hgca_corroboration | 8,652 |
| REJECTED_ruwe_quality | 633 |
| REJECTED_hgca_stellar (chi^2 > 100) | 150 |
| CORROBORATED_real_companion (chi^2 5-30) | 22 |
| FLAG_hgca_mass_ambiguous (chi^2 30-100) | 15 |
| REJECTED_published_nasa_exo | 14 |
| REJECTED_sahlmann_ml_imposter | 12 |

The 22+15 = **37 HGCA-corroborated candidates** (independent 25-yr Hipparcos-
Gaia astrometric anomaly) are the strongest output of this scan. After
post-hoc exoplanet.eu + SB9 cross-match, **4 of the 37 were published**:

  - G 239-52 / HIP 75202 = HIP 75202 Ab (exoplanet.eu)
  - G 15-6 / HIP 73800 (SB9)
  - BD+05 5218 / HIP 117179 = HIP 117179 b (exoplanet.eu)
  - L 194-115 / HIP 60321 = HIP 60321 b (exoplanet.eu, 68 MJ, P=530d, e=0.34,
    confirmed 2023). NOTE: HIP 60321 was inadvertently promoted to
    novelty_candidates.csv in commit d88b10c based on incomplete cross-match;
    this commit removes it.

**33 truly novel HGCA-corroborated candidates remain.** Filtering further to
substellar mass (M_2_marg < 100 M_J) + sig > 10 + chi^2 in CORROBORATED/FLAG
range yields **14 high-priority candidates**, of which:

  - 3 are already in novelty_candidates.csv (HD 101767, LP 335-104 = HIP 91479,
    BD+35 228)
  - 2 are OrbitalTargetedSearch solution type (FP-class concern; HD 42606,
    HD 185501) — supplementary only
  - 6 are anonymous Gaia DR3 sources with HGCA via HIP cross-match but no
    bright host — supplementary
  - **2 NEW promotions** to novelty_candidates.csv:
    - **HIP 60865 (G 123-34)**: Orbital, P=500.7 d, e=0.25, M_2 marg=49 MJ,
      sig=34, HGCA chi^2=10.5, M-dwarf host V=12.09. P_real_substellar=0.665
    - **HIP 20122**: Orbital, P=254.7 d, e=0.17, M_2 marg=64 MJ, sig=28.6,
      HGCA chi^2=5.1, faint M-dwarf V=13.49. P_real_substellar=0.553

## Updated candidate ranking (11 in novelty_candidates.csv)

| # | Candidate | P(real_substellar) | Provenance |
|---:|---|---:|---|
| 1 | HD 101767 | 0.98 | original 8 |
| 2 | HD 104828 | 0.89 | original 8 |
| 3 | HIP 60865 (NEW) | 0.665 | v2 scan HGCA-corroborated |
| 4 | HIP 91479 (LP 335-104) | 0.62 | AstroSpectroSB1 expansion |
| 5 | HIP 20122 (NEW) | 0.55 | v2 scan HGCA-corroborated |
| 6 | HD 140940 | 0.32 | multi-body original |
| 7 | HD 75426 | 0.30 | original 8 |
| 8 | HD 140895 | 0.28 | multi-body original |
| 9 | BD+35 228 | 0.24 | multi-body original (HGCA-corroborated now) |
| 10 | BD+46 2473 | 0.21 | multi-body original (HGCA-corroborated now) |
| 11 | HD 120954 | 0.00 | stellar |

Aggregate expected substellar yield: **5.07** (up from 3.85 after HIP 91479
promotion, then 4.4 after HIP 60321, then 5.07 after the v2 scan promotions).

## Files

- `v2_scan_full_pool.csv` — 9,498 candidates with v2 verdict
- `v2_scan_corroborated_22.csv` — 22 HGCA-corroborated (chi^2 5-30)
- `v2_scan_flag_mass_ambiguous_15.csv` — 15 FLAG (chi^2 30-100)
- `v2_scan_corroborated_with_novelty.csv` — 37 HGCA-quality with exoplanet.eu + SB9 check
- `scripts/pipeline_v2_tuned_filters_2026_05_13.py` — v2 filter cascade library
- `scripts/comprehensive_v2_scan_v2_2026_05_13.py` — full pool scan
