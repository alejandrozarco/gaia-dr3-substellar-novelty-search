# Gaia DR3 dormant compact-object & substellar companion search

[![release v2.0.0](https://img.shields.io/badge/release-v2.0.0-blue)](https://github.com/alejandrozarco/gaia-dr3-substellar-novelty-search/releases/tag/v2.0.0)

> **This work is experimental.** None of the candidates listed here have been observationally confirmed by independent methods (with one exception: CRTS J051419+0111 has TESS-photometric eclipse confirmation). The pipeline applies a corrected filter cascade to public Gaia DR3 NSS data and external catalogs; surviving candidates require follow-up observations or community catalog cross-checks before any discovery claim.

## What this is

A reproducible pipeline that searches Gaia DR3 Non-Single-Star (NSS) catalogs for stars whose astrometric or spectroscopic signature is consistent with a **dormant compact-object companion** (black hole, neutron star, white dwarf) or a **substellar companion** (brown dwarf, exoplanet). The cascade applies a corrected mass-function inversion plus a chain of filters (#29 SB2, #30 K-giant chromatic, #31 RV reality, #32 joint K_obs/K_pred) and cross-references against 30+ public catalogs.

The current production pipeline is the **v2-corrected cascade** (this release, v2.0.0). It supersedes v1 by fixing two compensating bugs that left v1 M_2 values systematically wrong by ~2× without breaking internal consistency.

## Quick links

| Document | What it is |
|---|---|
| **`docs/MASTER_OBJECTS_OF_INTEREST_2026_05_28.md`** | **Single source of truth for the current candidate list (32 truly-novel candidates across 6 papers).** |
| `docs/PROJECT_STATE_2026_05_28.md` | Comprehensive state inventory + 20 numbered lessons learned |
| `docs/CASCADE_CORRECTIONS_2026_05_28.md` | The two v2 cascade corrections + GAIA BH2 verification |
| `docs/CASCADE_VALIDATION_EXTENDED_2026_05_28.md` | Validation against 70 published systems (93% recall, 14% FP, 4.5% mass-error) |
| `docs/CV_PERIOD_PAPER_DRAFT_2026_05_28.md` | Full MNRAS Letter draft (~4,800 words) for the CV-period discoveries |
| `docs/HD216783_DEEP_ARCHIVAL_2026_05_28.md` | Deep dossier on HD 216783 (the strongest single near-discovery NS candidate) |
| `scripts/web_tool/app.py` | Streamlit interactive cascade UI (`streamlit run scripts/web_tool/app.py`) |

## v2 cascade — the three corrections

1. **NSS parallax** preferred over `gaia_source.parallax`. For binaries with significant orbital reflex, gaia_source.parallax is biased low by 1.2–2.5×, which inflates M_2 by the same factor.
2. **K_obs = rv_amplitude_robust / 2** — Gaia DR3 publishes a peak-to-trough robust amplitude, not the semi-amplitude K_1. Verified against Gaia BH2 (published K_1 = 21.2 km/s vs rv_amplitude_robust = 36.96, ratio 1.74 ≈ 2 suppressed by e=0.52).
3. **Filter #30 logg fallback chain**: `logg_gspphot → logg_gspspec_ann → logg_gspspec`. GSP-Phot returns NaN for many binaries; the fallback catches K-giant chromatic-bias false positives (HD 1957 case study).

After both bugs are fixed, the v1 catalog's headline "BH candidates" mostly collapse to sub-Chandrasekhar WD-companion systems. See `docs/CASCADE_CORRECTIONS_2026_05_28.md`.

## Candidate inventory (v2.0.0)

| Pile | Truly novel | Status | Telescope time needed |
|---|---:|---|---|
| CV-period (F) | 14 | MNRAS Letter drafted; 1 TESS-confirmed | None — archival only |
| HGCA + no-NSS BH-class (A) | 8 → 1 after vetting | HD 157033 promoted, others demoted as visual binaries | GALAH DR4 RV available free for HD 157033 |
| WD-primary Type Ia progenitor (E) | 2 | Both not in SIMBAD | 6 mo HARPS / X-shooter |
| M-dwarf super-Jupiters (B) | 3 | APMPM J0710-5704 has 37 TESS sectors | 0-1 night NEID / CHIRON / FEROS per target |
| Stefánsson substellar (D) | 3 | BD+05 5218 dropped (Stevenson 2023 scoop) | 4 nights TRES |
| Multi-survey (C) | 2 | Gaia 5476986 with APOGEE+RAVE K_1=163 | 1 night confirmation |

**Total truly novel: 32 candidates.** **Discovery-grade (independent second-method): 1 (CRTS J051419+0111 via TESS eclipse).** The remaining 31 are strong candidates needing observational follow-up.

## Repository structure

```
.
├── README.md                          # this file
├── CATALOG_DEPENDENCIES.md            # required external catalogs
├── REPRODUCIBILITY.md                 # how to reproduce the v2 catalog
├── data/
│   ├── derived/                       # v2 + v3 production catalogs (parquet)
│   ├── upstream_audit/                # F#5 G<13 binding-constraint audit
│   ├── validation_2026_05_28/         # 70-source benchmark self-test
│   ├── intermediate/                  # working intermediate outputs
│   ├── supplementary/                 # supplementary candidate lists
│   └── archive/
│       ├── v1_2026_05_27/             # v1 cascade outputs (superseded)
│       └── candidate_history_v1.18-v1.22/  # historical candidate states
├── docs/
│   ├── MASTER_OBJECTS_OF_INTEREST_2026_05_28.md  # ← canonical candidate list
│   ├── PROJECT_STATE_2026_05_28.md               # state + 20 lessons learned
│   ├── CASCADE_CORRECTIONS_2026_05_28.md         # v2 methodology
│   ├── CASCADE_VALIDATION_EXTENDED_2026_05_28.md # benchmark numbers
│   ├── CV_PERIOD_PAPER_DRAFT_2026_05_28.md       # discovery letter draft
│   ├── PAPER_READY_CATALOG_v2.md                 # corrected catalog markdown
│   ├── UPSTREAM_FILTER_AUDIT_2026_05_28.md       # F#5 audit
│   ├── ACCELERATION_NSS_EXTENSION_2026_05_28.md  # v3 BH3-regime
│   ├── FILTER33_PROPOSAL_2026_05_28.md           # SB1 self-consistency
│   ├── HD1957_DEEP_ARCHIVAL_2026_05_28.md        # K-giant calibration case
│   ├── HD216783_DEEP_ARCHIVAL_2026_05_28.md      # strongest near-discovery
│   ├── GALEXJ033455_VETTING_2026_05_28.md        # Simon+ 2026 falsification
│   ├── GALEXJ145250_VISUALDOUBLE_RESOLUTION_2026_05_28.md
│   └── archive/                                  # all pre-v2 docs
│       ├── root_v1/                              # superseded root docs
│       └── dev_notes_v1/                         # pre-v2 development notes
└── scripts/
    ├── streaming/                     # core pipeline (producer + consumer + filters)
    ├── streaming/v2_corrected/        # v2-corrected production pipeline
    ├── streaming/v3_acceleration/     # v3 NSS Acceleration channel
    ├── web_tool/                      # Streamlit interactive cascade UI
    └── analysis/                      # ad-hoc analysis scripts
```

## How to reproduce

See `REPRODUCIBILITY.md`. TL;DR:

```bash
# Set up the venv (uv-managed, Python 3.12)
cd /path/to/repo
uv venv && source .venv/bin/activate
uv pip install -r requirements.txt

# Run the v2 cascade against a fresh Gaia DR3 NSS pull
python scripts/streaming/producer.py        # chunked Gaia ADQL fetch
python scripts/streaming/v2_corrected/run_v2.py     # v2-corrected cascade

# Or interactively explore one source
streamlit run scripts/web_tool/app.py
```

## Detection vs. interpretation vs. curation

This pipeline does NOT detect companions — Gaia DR3 already did. The pipeline does three things on top of Gaia's published NSS catalogs:

1. **Interpretation**: invert the Thiele-Innes mass function with a per-source M_1 prior to give M_2 in M_⊙.
2. **Filtering**: apply F#29–32 (SB2, K-giant chromatic, RV reality, joint K_obs/K_pred) to remove known systematic false-positives.
3. **Curation**: cross-reference against 30+ public catalogs (NASA Exoplanet Archive, exoplanet.eu, SIMBAD, Brandt HGCA, Kervella PMa, WDS, SB9, Tokovinin MSC, GALAH SB2, Trifonov 2025, plus specialized BH/NS literature: Müller-Horn 2026, Shahaf 2023/2024, Andrews 2022, El-Badry 2023/2024, Sahlmann 2025) to flag already-published candidates.

After all three stages, the surviving 32 candidates are flagged "truly novel" per the 7-step novelty protocol documented in `docs/PROJECT_STATE_2026_05_28.md`.

## Validation summary

`docs/CASCADE_VALIDATION_EXTENDED_2026_05_28.md` reports validation against 70 published benchmark systems:

| Group | Result |
|---|---|
| Confirmed Gaia BHs (BH1/BH2/BH3) | 2/3 caught as compact-mass (BH3 not in DR3 NSS by construction) |
| Shahaf 2024 NS subset (21) | **21/21 = 100%** with M_2 ≥ 1.2 M_⊙; median \|ΔM\|/M = **4.5%** |
| Andrews/Shahaf candidate sample (40) | 40/40 produce M_2 ≥ 1.2; **14% Tier-1 false-positive rate** on adversarial subset |
| FP calibrators (4 UMi, A-dwarf phantom, HD 76078) | 2/3 caught by the right filter (HD 76078 architectural rejection) |
| Sub-stellar recovery (HD 81040, HD 111232) | Both classified as `planet_candidate` with ~10% mass error |

**Class-level recall on confirmed compact / sub-stellar: 93% (25/27).**

## What's archived

- `data/archive/v1_2026_05_27/` — v1 cascade outputs (16 BH + 104 NS candidates, mostly invalidated by v2 corrections)
- `data/archive/candidate_history_v1.18-v1.22/` — historical candidate snapshots from v1.18 through v1.22
- `docs/archive/root_v1/` — superseded root docs: BENCHMARK v1, CANDIDATE_FP_AUDIT, CATALOG_COMPLETENESS_ANALYSIS, HIP91479_DOSSIER, REPORT v1
- `docs/archive/dev_notes_v1/` — 16 pre-v2 development notes (2026-05-17 / 18)

These are kept for reproducibility of older releases but should NOT be used as the current candidate state. The single source of truth is `docs/MASTER_OBJECTS_OF_INTEREST_2026_05_28.md`.

## Citation

If you use this pipeline or its candidate lists, please cite:
- The Gaia Mission (Gaia Collaboration et al. 2016, A&A 595, A1) and Gaia DR3 (Gaia Collaboration 2023, A&A 674, A1) for the underlying data
- The Gaia DR3 NSS pipeline (Halbwachs et al. 2023, A&A 674, A9) for the orbital solutions
- This repository as `https://github.com/alejandrozarco/gaia-dr3-substellar-novelty-search` v2.0.0

The corrections methodology paper is in preparation; the CV-period discovery letter is drafted at `docs/CV_PERIOD_PAPER_DRAFT_2026_05_28.md`.

## Author + acknowledgments

Independent research. Pipeline + corrections by the repository owner with assistance from Claude (Anthropic) for iterative analysis. Uses public archival data from ESA Gaia, NASA TESS, NSF/AURA/IRSA, and ZTF/Palomar.
