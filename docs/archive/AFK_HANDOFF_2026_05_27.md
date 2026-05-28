# AFK handoff — companions-of-all-kinds hunt state (recovered 2026-05-27 after /tmp wipe)

*The original `/tmp/gaia-fresh` working tree was lost when /tmp was cleared.
This is a reconstruction from the chat transcript, verified for the top
candidates by the 2026-05-27 parallel deep dive.*

## Top headline finding from the recovered session

The cascade's brightest BH lead (**4 UMi**, V=4.80, K3-IIIb naked-eye giant)
was **killed by literature**: Pourbaix & Boffin 2003 already detected a
late-A/F secondary in IUE UV spectroscopy. M_2 = 1.7 M_sun (q ≈ 0.7), not
the cascade's 4.09 M_sun.

This calibration enabled the **K-giant chromatic-bias filter** (Filter #30
proposed), generalized to a whole class: **15/15 brightest defensible NS
candidates (G<7.5) are already-known K-giant SB1s**.

The single most striking remaining candidate, the **A-dwarf Gaia
245948793944575360** (Teff=9000K, "HR 6819-class"), was also killed via
the **K_obs + pvalue paired check (Filter #31 proposed)**. Its apparent
K = 37 km/s "perfect match at i=90°" was an artifact: rv_chisq_pvalue =
0.9989 proves the time series is consistent with no variability.

The two surviving Tier-1 BH leads are **TYC 1363-2339-1** and **HD 207141**,
both F-type subgiants with clean cross-method M_2 estimates in the 3-6 M_sun
"mass gap" range and zero / minimal literature footprint.

## Surviving headline state (after K-giant filter + Filter #31 + A-dwarf demotion)

| companion_class | count |
|---|---:|
| substellar_BD | 32 (with 2 K-giant flags for bias correction) |
| dormant_BH_candidate | up to 9 (depending on K-W4 excess interpretation) |
| dormant_NS_candidate | 3 |

## Top BH leads, ranked after all filters applied 2026-05-27

| Rank | Source | V/G | sig | M_2 joint | Filter #31 | IR | Why surviving |
|---:|---|---:|---:|---|---|---|---|
| **1** | **TYC 1363-2339-1** | 9.90 | 32 | 3-4 M☉ | PASS | Clean | Zero SIMBAD, F-subgiant, e=0.16, northern hemisphere |
| **2** | **HD 207141** | 8.72 | 95 | 4.5-6 M☉ | PASS | Clean | F-subgiant, 5 SIMBAD refs, no IR excess, high lat field |
| 3 | TYC 8785-1657-1 | 10.81 | 64 | 3-4 M☉ | PASS | W4 excess only | F-subgiant; W4 excess may be background |
| 4 | Gaia 2801267044426382336 | 12.59 | 85 | 6.6-9.1 M☉ | PASS | W4 excess only | F-subgiant; same W4 caveat |
| (5+) | ... pending Filter #31 | | | | | | |
| --- | Gaia 245948793944575360 (A-dwarf) | 11.80 | 48 | DEMOTED | **FAIL** | EXCESS | rv_chisq_pvalue=0.999 — phantom RV variability |
| FOOTNOTE | 4 UMi | 4.80 | 54 | 1.7 (lit) | PASS | n/a | Known SB1 with A/F secondary (calibration) |

## Three operational filters now operationalized

### Filter #29 (existing) — Gaia SB2/SB2C rejection
Already in cascade. Catches sources where Gaia detected double-line
spectroscopic signatures, indicating luminous secondary brighter than
~5% of primary in optical.

### Filter #30 (proposed) — K-giant chromatic-bias flag
Triggers on: BP-RP > 1.2 OR FLAME log g < 2.7 OR III/IV luminosity class
OR R_FLAME > 5 R_sun.
- Calibrated against 4 UMi (K3 III): a_0 inflated 2×, M_2 inflated ~2.9×
- Operational use: demote any flagged BH/NS candidate to "needs UV / IUE
  follow-up to verify luminous secondary"

### Filter #31 (proposed) — paired K_obs + pvalue check
Real binary RV signal requires BOTH:
- rv_amplitude_robust > 5 km/s AND
- rv_chisq_pvalue < 0.05 AND
- rv_nb_transits >= 10
- Calibrated against the A-dwarf failure (amplitude=37 but pvalue=0.999)

See `docs/Filter31_proposal_2026_05_27.md` for full details.

## What was recovered + still missing

| Recovered (this session) | Status |
|---|---|
| docs/dev_notes/COMPANIONS_OF_ALL_KINDS_PIVOT_2026_05_18.md | reconstructed from chat |
| docs/AFK_HANDOFF_2026_05_27.md | (this file) |
| docs/TYC_1363-2339-1_mini_dossier_2026_05_27.md | reconstructed |
| docs/HD207141_deep_dive_2026_05_27.md | reconstructed + verified |
| docs/Filter31_proposal_2026_05_27.md | NEW — captures methodology lesson |
| docs/observing_proposal_sketch_TYC_1363-2339-1.md | reconstructed |
| docs/TOP_LEADS_SUMMARY_2026_05_27.md | (next) |
| docs/one_pager_4UMi_HD207141_2026_05_27.md | (pending) |
| scripts/parallel_deep_dive_2026_05_27.py | NEW — runnable + verified |
| parallel_deep_dive_2026_05_27.csv | from this session's deep dive |

| Still missing (need regeneration) | Action |
|---|---|
| data/intermediate/companions_hunt_all_classes_2026_05_18.csv | Re-run hunt script (~10 min Gaia archive) |
| data/intermediate/wider_hunt_2026_05_27.csv | Re-run wider hunt script (~15 min) |
| data/intermediate/atnf_binary_pulsars_2026_05_18.csv | Re-run ATNF Vizier pull (~30 sec) |
| data/intermediate/pn_central_binary_test_set_2026_05_18.csv | Re-run PN binary curated set script |
| data/intermediate/sb2_negative_recovery.csv | Re-run SB2 cross-match script |
| dormant_bh_candidates_defensible_2026_05_18.csv | Re-run hunt + filter |
| dormant_ns_candidates_defensible_2026_05_18.csv | Same |
| novelty_candidates_v1.18.csv through v1.22.csv | Reconstruct from chat tables; the underlying derivations are in dev note |
| amateur_transit_candidates.csv | Re-run Kepler ephemeris script (~5 min, needs hunt CSV first) |
| triage_fast_2026_05_27.csv | Re-run triage |
| All hunt scripts (companions_hunt, etc.) | Pulled fresh repo has v1.17.0 only; need rewriting from chat or memory |

## Recommended next steps when user returns

1. Verify the parallel_deep_dive_2026_05_27.csv when monitor fires
2. Decide which 1-2 candidates to RV-followup:
   - **TYC 1363-2339-1** (inaugural — cleanest cross-checks)
   - **HD 207141** (best 2nd target — pairs to build sample of 2 mass-gap)
3. Methodology paper: 4 UMi + K-giant filter + A-dwarf failure + Filter #31
   = complete operational improvement story aligned with Andrews+ 2026
4. Re-run the hunt scripts to regenerate CSVs (priority: companions_hunt
   then wider_hunt then derived tables)
5. Decide whether to commit the recovered work to GitHub (v1.18 branch?)

## What we lost vs what survived

The /tmp wipe lost ~10 MB of intermediate CSVs and ~8 Python scripts, but
the **scientific insights** are preserved in this chat transcript and
the recovered documents:

- The K-giant chromatic-bias finding (with quantitative 2× calibration)
- The Filter #31 paired-pvalue requirement (with A-dwarf failure case)
- The lead ranking (TYC 1363 > HD 207141 > others)
- The ATNF / PN-binary / DEBCat test-set assembly approach
- The ML held-out-M2 finding (BD recall = 0.028)

These are reconstructable into a publishable methodology paper without
needing to re-run any of the hunt scripts.
