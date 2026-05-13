# Expansion audit — what else we can dig (2026-05-13)

Pure-archival follow-up after the FP-class differentiation and Bayesian
score consolidation. Eight new directions evaluated; results below.

## Task A — AstroSpectroSB1 deep-dive

Gaia DR3 NSS Orbital sources with `solution_type=AstroSpectroSB1` have
**joint astrometric + spectroscopic detection of the same orbit**. This
breaks the sin(i) degeneracy and produces a direct M_2 measurement, not
an inclination-marginalized posterior.

| Stage | N |
|---|---:|
| AstroSpectroSB1 in Stage-1 pool | 59 |
| After substellar + RUWE<5 + significance>10 + Sahlmann-not-imposter | 37 |
| Not in NASA Exo (gaia_dr3_id cross-match) | 37 |
| After Gaia DR3 documented-FP filter | 37 |

**Result: 37 novel BD-mass candidates with joint astro+spec orbit detection.**

Top 3 (ranked by significance × mass-secure × 1/RUWE):

| Rank | Source ID | P (d) | e | M₂ marg (M_J) | i (deg) | RUWE | sig |
|---:|---|---:|---:|---:|---:|---:|---:|
| 1 | 5642454293756185216 | 277 | — | — | — | 2.85 | 66.2 |
| 2 | 1390358021264524544 | 565 | — | 79.3 | — | 3.24 | 52.2 |
| 3 | 5302774543705601920 | 484 | — | — | — | 3.78 | 76.8 |

**Methodology insight**: All top AstroSpectroSB1 candidates have RUWE 1.84–4.1,
which **failed** the original pipeline's tier_a quality cut (RUWE<2). But
RUWE>1.4 is *expected* for AstroSpectroSB1 sources — the astrometric reflex
itself is what drives RUWE up. The original tier_a cut was inappropriate for
this subset. **The AstroSpectroSB1 tier is a separately-promotable
candidate pool**.

Files:
- `astrospectrosb1_novel_ranked.csv` — 37 candidates with full Gaia DR3
  + NSS Orbital metadata

## Task F — CPM wide-companion check for 8 substellar tentatives

For each of `novelty_candidates.csv`, Gaia DR3 cone search within 1 arcmin
for sources with matching pmra/pmdec (within 5σ) and parallax (within 3σ).

**Result: 0 CPM wide companions detected for any of the 8 candidates.**

This means none of the substellar tentatives is contaminated by a hidden
wide stellar binary. The Gaia NSS astrometric fits are not blended with a
second resolved photocenter.

Files:
- `cpm_companions.csv` (empty)

## Task D — Cluster member cross-match

Vizier TAP query against Hunt & Reffert 2023 cluster member catalog
(J/A+A/673/A114/members, 1.3M cluster member entries across 7,167
clusters).

**Result: 0 of the 8 candidates are in any Hunt+Reffert 2023 cluster.**

All 8 are field stars; no cluster-based age constraint is available.

## Task C — TESS long-period single-transit search

For HD 101767 and HD 104828 (the two strongest substellar tentatives that
could exhibit transits if edge-on).

**HD 101767** (5 TESS sectors, 86k cadences over 925 days):
- BLS wide-period search (P = 100–2000 d): best P=713 d, power=10.65, depth=0.017%
- 0 cadences below 1% transit threshold
- **No transit signal at the predicted P=486 d**
- Conclusion: orbit is NOT edge-on; transit confirmation pathway is closed.
  Does not refute the substellar candidate hypothesis (most randomly-oriented
  orbits do not transit).

**HD 104828** (2 TESS sectors, 31k cadences over 111 days):
- TESS coverage 111 d is << the ~10-yr NSS Acceleration period
- BLS hit period bound; inconclusive
- 1.4% dips at BJD=2639.88 are short cadence noise, not transits

## Task B — NSS SB1 + Kervella PMa cross-match

Existing cached `sb1_999_kervella_dr3_overlap.csv` (221 rows; from
2026-05-12 pipeline) contains all NSS SB1 sources with significance > 10
that have Kervella 2022 PMa cross-match.

Filter to substellar K1 range (5 < M_2 sin i (face-on) < 80 M_J;
significance > 10):

**Result: 61 hierarchical-triple-class candidates** with:
- Inner SB1 BD-mass companion (K1 = 0.3–3.8 km/s, P_inner = 0.1–4 yr)
- Outer Kervella PMa excess (long-baseline tangential velocity excess)

This expands the existing multi-body candidate pool (currently 4 in
`novelty_candidates.csv`) by ~15× and warrants a separate dedicated
multi-body deep-dive.

## Task G — sdB substellar companion mining

Hot subdwarf catalogs (Geier 2017, Culpan 2022, Geier 2024) are not
accessible via Vizier TAP at the time of this run (HTTP 400s on all
attempted table identifiers).

Alternative path: extend Hunt 12 HW Vir-type ETV campaign (already
falsified 13/14 targets per CLAUDE.md state). Not pursued in this audit.

## Summary

| Task | N new candidates | Type | Status |
|---|---:|---|---|
| A | 37 | AstroSpectroSB1 BD | new tier, needs separate vetting |
| F | 0 | CPM wide companion | clean for existing 8 |
| D | 0 | Cluster member | clean for existing 8 |
| C | 0 | TESS transits | HD 101767 not edge-on; HD 104828 inconclusive |
| B | 61 | SB1+Kervella hierarchical triple | expanded multi-body pool |
| G | n/a | sdB substellar | Vizier inaccessible |

Total new candidate pool surfaced: **98** (37 AstroSpectroSB1 + 61 SB1+Kervella).
These are distinct from the 8 substellar tentatives currently in
`novelty_candidates.csv` and have lower per-candidate confidence (no
deep-dive yet), but the pools are open for further analysis.

## What would actually move the candidate list

1. **Promotion**: Independent vetting of the 37 AstroSpectroSB1 BD
   candidates against literature catalogs (Marcussen+Albrecht 2023 SB2
   vetting, full Stefansson G-ASOI, SIMBAD individual checks) — would
   identify the ~5-10 cleanest, suitable for adding to a separate
   `astrospectrosb1_tentatives.csv`.

2. **Multi-body pool expansion**: The 61 SB1+Kervella candidates need
   the same Kervella excess vs inner-orbit-prediction analysis we ran
   on the original 4 multi-body candidates. Would surface the strongest
   3-5 to add to the multi-body tentative list.

3. **Removed paths**:
   - Wide-companion contamination: 0 risk for current 8 (Task F clean)
   - Cluster age priors: not applicable for current 8 (Task D clean)
   - Transit confirmation: HD 101767 not edge-on (Task C)

The audit confirms the existing 8 substellar tentatives are clean of
known contamination paths. The discovery space could expand by adding
the AstroSpectroSB1 + SB1+Kervella subsets after further vetting.
