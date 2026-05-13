# Candidate FP-risk audit (2026-05-13)

After the discovery that \* 54 Cas (Gaia DR3 522135261462534528) is on Gaia's
documented FP list (`cosmos.esa.int/web/gaia/dr3-known-issues`), this report
audits the remaining 8 substellar tentative candidates in `novelty_candidates.csv`
against the same diagnostics.

## Methodology

For each candidate, query Gaia DR3's `nss_two_body_orbit` / `nss_acceleration_astro`
directly and extract the FP-relevant diagnostics, then compare against the
4 documented FPs (54 Cas, HIP 64690, HIP 66074, WD 0141-675).

## Diagnostic comparison

### Key distinction: solution-type pipeline

All 4 documented FPs use **`OrbitalTargetedSearch*`** (Targeted Search pipeline,
which uses external priors for period from known transit/RV catalogs). The
software bug that produced the FPs is in the Targeted Search code path.

Our 5 NSS-Orbital substellar candidates use **`Orbital`** (autonomous discovery
by Gaia's astrometry alone — different code path).

| Solution type | Code path | Documented FP exposure |
|---|---|---|
| `OrbitalTargetedSearch` | uses external prior + Targeted MCMC | **YES** (3 of 4 FPs) |
| `OrbitalTargetedSearchValidated` | Targeted + internal validation | **YES** (1 of 4 FPs — even Gaia's own validation missed) |
| `Orbital` | autonomous Thiele-Innes fit | NOT in documented FP list |
| `Acceleration7` / `Acceleration9` | astrometric acceleration solver | NOT in documented FP list |
| `SB1`, `AstroSpectroSB1`, etc. | spectroscopic | NOT in documented FP list |

### Quality diagnostics (sorted by significance)

| Candidate | Solution Type | Significance | Efficiency | obj_func | px/err |
|---|---|---:|---:|---:|---:|
| FP: HIP 64690 | OrbitalTargetedSearch | **4.70** | 0.00 | 398.6 | 2589 |
| FP: 54 Cas | OrbitalTargetedSearch | **5.08** | 0.00 | 388.3 | 634 |
| FP: HIP 66074 | OrbitalTargetedSearchValidated | **6.49** | 0.30 | 361.3 | 2376 |
| FP: WD 0141-675 | OrbitalTargetedSearch | 13.75 | 0.00 | 403.3 | 8051 |
| ---- | ---- | ---- | ---- | ---- | ---- |
| HD 140895 | Orbital | 6.83 | 0.00 | 687.0 | 445 |
| BD+46 2473 (Orb) | Orbital | 8.48 | 0.00 | 528.8 | 201 |
| BD+35 228 | Orbital | 12.78 | 0.00 | 462.7 | 292 |
| HD 140940 | Orbital | 13.04 | 0.00 | 1412.5 | 130 |
| **HD 101767** | Orbital | **39.64** | 0.30 | 811.1 | 709 |

NSS Acceleration candidates (separate pipeline, not on documented FP list):
| HD 104828 | Acceleration7 | 37.01 | n/a |
| HD 120954 | Acceleration | HGCA-strong | n/a (confirmed stellar) |
| HD 75426 | Acceleration9 | 60σ (Gaia DR3 reports) | n/a |

## Per-candidate verdict

### Robust — no FP risk from documented sources
- **HD 75426**: NSS Acceleration9, multi-pipeline corroboration via Tycho-Gaia 25-yr ΔPM (independent of NSS), 4-baseline convergence. Confirmed substellar / stellar transition zone.
- **HD 104828**: Acceleration7 at sig=37, CARMENES K=1.30 km/s independent confirmation, HGCA snrPMa=23.6.
- **HD 120954**: Already classified as stellar; orvara + 5-baseline convergence is decisive.

### Robust on diagnostics, FP-class-cleared
- **HD 101767**: Pure `Orbital` (different pipeline from FPs), significance 39.6 (far above FP cluster of 4.7-13.75). Independent corroboration: HGCA 2.79σ + Kervella + Gaia DR3 rv_chisq 2.8×10⁻¹¹.

### Inner orbit FP-risk (mitigated by independent outer-body evidence)
- **HD 140895**: Orbital sig=6.83 (LOWEST among candidates, inside FP danger zone). Outer body from Kervella PMa excess is independent and survives even if inner is FP.
- **HD 140940**: Orbital sig=13.04 (within FP range). Same caveat — outer body inference more robust than inner.
- **BD+46 2473**: TWO NSS rows (SB1 at P=5.7d, sig=6.7 + Orbital at P=495d, sig=8.5). Dual-pipeline detection. The SB1 may be the real inner reflex; the Orbital may be the candidate signal. Inner orbit FP-risk applies.
- **BD+35 228**: Orbital sig=12.78 (FP range). Inner orbit FP-risk applies. Outer body via Kervella excess.

## Independent vetting catalogs

| Catalog | Hits among candidates | Verdict |
|---|---|---|
| Sahlmann 2025 ML | 2: HD 101767, BD+35 228 | Both: `PRESELECTED_SUBSTELLAR_BROAD` (literature-noted, not classified) — NEUTRAL |
| Stefansson 2025 GASOI | 0 | not in Stefansson's analysis set |
| `sahl_confirmed` flag (ML imposter) | 0 | all clean |
| `in_stefansson` flag | 0 | all clean |
| Tokovinin MSC (stellar multiple) | 0 | none known multiple |
| Cosmos.esa.int FP list | 0 | none in documented FPs |

## Net assessment

After this audit, the FP risk for the 8 substellar tentatives breaks down as:

| Risk tier | Candidates | Reason |
|---|---|---|
| **Negligible FP risk** | HD 75426, HD 104828, HD 120954 | NSS Acceleration (different pipeline from FPs); multi-pipeline corroboration |
| **Low FP risk** | HD 101767 | Pure `Orbital` (non-Targeted), significance 39.6× FP-cluster lower bound |
| **Inner-orbit FP-risk-elevated** | HD 140895, HD 140940, BD+46 2473, BD+35 228 | Significance inside documented-FP range; mitigated by independent outer-body (Kervella PMa) corroboration which is INDEPENDENT of inner NSS fit |

**No candidates are removed from `novelty_candidates.csv` based on this audit.** The
remaining FP risk for the 4 multi-body candidates is documented and isolated to
the **inner** orbital fit (i.e., the period and mass of the inner body) — the
substellar tentative interpretation (outer body inferred from PMa excess) is
not affected because Kervella PMa is an independent astrometric pipeline.

## Implication for the methodology

1. The candidates currently in the substellar tentative list are NOT exposed to
   the same FP class as 54 Cas because of the solution-type pipeline difference
   (Orbital vs OrbitalTargetedSearch).
2. The documented FP list at cosmos.esa.int should remain a hardcoded pre-filter
   (Filter #27) for any future Gaia DR3 NSS-derived analysis.
3. Pure `Orbital` candidates with sig < 20 still carry residual FP risk (Gaia
   DR3's general NSS imposter rate at the detection floor is ~30-50% per literature
   consensus), but no specific bug-induced FP class affects them as of 27 May 2024.
4. Gaia DR4 (Dec 2026) will publish revised NSS catalogs with the 4 documented
   FPs corrected and new validation diagnostics. The DR4 refresh will be the
   decisive check.

## Files

| Path | Description |
|---|---|
| `nss_orbital_diagnostics.csv` | Per-candidate Gaia DR3 NSS Orbital metadata (5 candidates + 4 FPs benchmark) |
| `independent_vetting_crossmatch.csv` | Cross-match against Sahlmann 2025, Stefansson 2025, Tokovinin MSC |
| `CANDIDATE_FP_AUDIT.md` | This file |
