# Supplementary investigation + catalog-expansion brainstorm (2026-05-13)

Three things this session:
1. HD 42606 / HD 185501 supplementary literature search
2. Retroactive exoplanet.eu coord-filter on the 11 candidates
3. Brainstorm + web search for catalog expansion options

## 1. Supplementary investigations

### HD 185501 (HIP 96576, Gaia DR3 2047188847334279424)

**Found in Marcussen & Albrecht 2023 Table 1** (arXiv:2305.08623) as a
low-mass companion candidate:

> "2047188847334279424 | OTS | Unknown | No | 0.96 (-0.82, +1.01) | 14 (-7, +22) | [0,1] | 7.3 | 32.6"

Verdict: **"Unknown"** — apparent astrometric companion (mass ~14 +22/-7 M_J)
but ground-based RV joint analysis was inconsistent or unverified. This is
exactly the same status we landed on independently (real companion, low M,
OrbitalTargetedSearch yellow flag).

Marcussen & Albrecht 2023 specifically lists this as needing further follow-up.
Our v2 scan independently flagged it via HGCA chi^2 = 5.9 (CORROBORATED) +
sig = 23.8. The two independent analyses agree: real companion, mass uncertain.

**Recommendation**: Document in supplementary list with the Marcussen
"Unknown" verdict. Do not promote.

### HD 42606 (HIP 29330, Gaia DR3 2994437527894182272)

**Not found in Marcussen & Albrecht 2023, Brandt+Sosa 2025 (156-companion),
Kiefer 2025 (9698-source), or any other recent (2024-2026) Gaia DR3 NSS
validation catalog.**

Web search returned no published planet or BD claim for this designation.
The high NSS significance (76.9) + HGCA chi^2 (58.9) + low gof (1.24) strongly
suggest a real companion, but the OrbitalTargetedSearch class makes it
FP-class. Without independent literature corroboration, status remains
supplementary.

**Recommendation**: Document as supplementary with explicit "FP-class but
strong signal" caveat. Investigate in DR4.

## 2. Retroactive exoplanet.eu coord-filter on 11 candidates

Applied 5-arcsec exoplanet.eu coord-match to every entry in
`novelty_candidates.csv`:

| # | Candidate | exoplanet.eu match? |
|---|---|---|
| 1 | HD 101767 | clean |
| 2 | HD 75426 | clean |
| 3 | HD 104828 | clean |
| 4 | HD 140895 | clean |
| 5 | HD 140940 | clean |
| 6 | BD+46 2473 | clean |
| 7 | BD+35 228 | clean |
| 8 | HD 120954 | clean |
| 9 | HIP 91479 | clean |
| 10 | HIP 60865 | clean |
| 11 | HIP 20122 | clean |

**All 11 clean.** No retroactive demotions needed.

## 3. Catalog-expansion brainstorm + web search

### Catalogs we've already used

- Gaia DR3 NSS Orbital + Acceleration (primary mining pool)
- Gaia DR3 main source catalog (astrometry, photometry, RV)
- Hipparcos main catalog + van Leeuwen 2007 IAD
- HGCA Brandt 2024 (Hipparcos-Gaia 25-yr PMa anomaly)
- Kervella 2022 H2G2 PMa
- NASA Exoplanet Archive PS + PSCompPars
- exoplanet.eu (added in v2 cascade as Filter #3)
- SB9 Pourbaix spectroscopic binaries
- WDS Washington Double Star
- Tokovinin Multiple Star Catalog
- Sahlmann 2025 ML imposter labels
- Stefansson 2025 G-ASOI (partial cached)
- Marcussen+Albrecht 2023 SB2 vetting
- TIC v8.2 (host masses)
- TESS lightcurves (lightkurve)
- ZTF lightcurves
- HARPS RVBank Trifonov+ 2020
- HIRES Trifonov 2025 (HGCA subset)
- APOGEE DR17 (RVs)
- GALAH DR4 (SB2 flag + RVs)
- LAMOST DR10
- CARMENES DR1 (Cortes-Contreras+ 2024)
- Vari summary + vari classifier + vbroad (Gaia DR3 auxiliary)

### Catalogs identified as potentially missing (NEW from web search)

#### Tier 1 — should be mined

**(a) Kiefer 2025 catalog (A&A 702 A77, Vizier J/A+A/702/A77)**
- 9,698 substellar candidate hosts identified from RUWE + Hipparcos-Gaia PMa
- **EXPLICITLY EXCLUDES NSS sources** (NSSflag) — complementary to our pool
- Mass cut < 13.5 M_J face-on (planet regime); sma 1-3 AU
- Cross-match of our 11: **0 hits** (confirmed by direct query). Their channel
  is "stars with astrometric signature but no NSS solution" — a different
  detection mode.
- **Action**: Mine this 9,698-source catalog with v2 cascade for candidates
  passing our HGCA chi^2 + NASA + exoeu + SB9 filters.

**(b) Brandt+Sosa 2025 (IOPscience adfa99, 156-companion validation)**
- 156 orbital solutions from combined astro + RV joint fits
- 111 stellar + 12 BD + 33 planet companions
- Cross-match of our 11: **0 hits** (our candidates are not yet in this
  validated subset — good, confirms they're novel)
- **Action**: Confirm none of our 11 conflict with published Brandt+Sosa
  values; use as future validation reference once we have RV.

#### Tier 2 — may have value

**(c) Cooper et al. 2024 Ultracool Dwarf Companion Catalogue
(arXiv:2408.07024, MNRAS 533 3784)**
- 598 ultracool dwarfs in 278 systems within 100 pc
- M7-Y dwarf census (much lower mass + wider separation than our parameter space)
- Orthogonal channel: searches for resolved UCD companions to nearby stars
- **Action**: cross-match our 11 hosts; very unlikely to overlap but cheap
  to check.

**(d) Halbwachs/Holl 2024 ML classifier (arXiv:2404.09350, MNRAS 537 1130)**
- Machine learning classifier for Gaia DR3 NSS Orbital solutions to identify
  best exoplanet/BD candidates
- Semi-supervised anomaly detection + XGBoost / Random Forest
- **Action**: get their classifier or the trained labels and apply to our
  candidates. (Vizier ID not yet established — paper appendix may have
  supplementary table.)

**(e) Kiefer 2025a "GaiaPMEX" tool (A&A 702 A77 companion paper)**
- Tool to characterize companion mass + sma from RUWE alone, or with
  Gaia+Hipparcos PMa
- Could be applied directly to our 11 candidates to get an independent
  mass-sma constraint
- **Action**: if open-source code is published, run on our 11 hosts.

#### Tier 3 — niche but worth noting

**(f) Penoyre IPD-based companion catalog** (was hoping for this; webfetch
returns no current published version. May be private/in-prep.)

**(g) Northern RV survey public archives** (already partial)
- NEID DR1 (Kitt Peak)
- MAROON-X DR1 (Gemini-N)
- ESPRESSO DR1 (VLT)
- NIRPS DR1 (La Silla 3.6m, IR M-dwarf RV)
- SOPHIE Hara 2025 catalog

### What's NOT in our pipeline that should be (in priority order)

1. **Kiefer 2025 mining**: 9,698 substellar candidates from a complementary
   non-NSS pool — could be a new candidate pool of comparable size to ours.
2. **Stefansson 2025 G-ASOI full Vizier**: currently we have a partial cache
   from a single deep-dive (ross1063 dossier). The full Vizier table would let
   us cross-match all 9,498 v2 scan candidates.
3. **Cooper 2024 UCD coord-match** for our 11 hosts: 5-min cheap check.
4. **Halbwachs/Holl 2024 ML labels** if accessible: independent vetting.
5. **NEID DR1 / MAROON-X DR1 public RV** for the 2 new northern candidates
   (HIP 60865 G 123-34, HIP 20122) if any data exists.

## Recommendation

**Strongest single action**: mine the **Kiefer 2025 9,698-source catalog**
with our v2 cascade. The pool is genuinely complementary (non-NSS Gaia
sources) — we have not touched this parameter space at all. Even at the
substellar mass threshold (M < 80 M_J vs Kiefer's 13.5 M_J), there's
overlap and the methodology can be extended.

If Kiefer 2025 mining is fruitful, this could expand our candidate base
substantially.
