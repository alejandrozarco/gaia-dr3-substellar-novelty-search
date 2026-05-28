# Reproducibility notes — v2.0.0

This document describes how to reproduce the v2-corrected catalog from the contents of this repository plus public archive data. It supersedes the pre-v2 reproducibility notes archived at `docs/archive/root_v1/`.

## What's reproducible from this repo alone

| Artifact | Reproducible? | How |
|---|---|---|
| The two cascade-correction methodology | ✓ fully | `docs/CASCADE_CORRECTIONS_2026_05_28.md` derives both corrections analytically; Gaia BH2 K_1 verification numbers are deterministic |
| `data/derived/main_hunt_derived_v2.parquet` (the v2 catalog) | ✓ from cached data | The v1 parquet (`data/archive/v1_2026_05_27/main_hunt_derived.parquet`) plus a supplementary Gaia ADQL pull for NSS-plx + logg_gspspec_ann columns is sufficient. See `scripts/streaming/v2_corrected/run_v2.py`. |
| `data/derived/acceleration_v3.parquet` (NSS Acceleration channel) | ✓ from fresh Gaia pull | Requires fresh ADQL queries against `gaiadr3.nss_acceleration_astro`. See `scripts/streaming/v3_acceleration/`. |
| 70-source benchmark self-test | ✓ | `scripts/validate_cascade_extended_2026_05_28.py` pulls all 70 benchmark sources via Gaia ADQL and runs the v2 cascade. |
| The 7-step novelty verification | ✗ requires external services | Live web queries to SIMBAD, NASA Exoplanet Archive, arXiv API, Google. Results cached at `data/candidate_dossiers/novelty_verification_2026_05_28/` for the 32 truly-novel subset. |
| Per-candidate deep dossiers (HD 1957, HD 216783, etc.) | ✓ from external archives | Each dossier in `docs/` lists every catalog query made; rerunning them against the live Vizier / IRSA / MAST returns the same data. |
| CV-period orbital periods (Pile F) | ✓ from ZTF DR23 + TESS | `scripts/streaming/` has the BLS pipeline; refresh against ZTF DR23 via IRSA cutout API. 14 BLS periods listed in `docs/CV_PERIOD_PAPER_DRAFT_2026_05_28.md`. |
| Streamlit web tool single-source verdicts | ✓ from cached parquets | `streamlit run scripts/web_tool/app.py` works offline with cached sample data; live ADQL extends to any Gaia DR3 source. |

## What's NOT reproducible from this repo

- **Original Gaia DR3 NSS data**. The raw NSS Orbital + AstroSpectroSB1 + Acceleration catalogs (a few hundred MB total) are not redistributed. Pull via `astroquery.gaia.Gaia.launch_job_async` from the ESA Gaia archive.
- **Müller-Horn 2026 Zenodo catalogs**. ~19 MB of CSVs at https://zenodo.org/records/19181131. Pull manually + cache locally.
- **NASA Exoplanet Archive `ps` table snapshot**. Live TAP queries (not redistributed).
- **The 65 MB River ML model** (`main_river_model.pkl`) — superseded by v2 and gitignored. Regenerable via `scripts/streaming/river_ml.py` if needed.
- **Raw Gaia chunks** in `data/raw_chunks/` — gitignored; regenerable via `scripts/streaming/producer.py`.

## Required external catalogs

See `CATALOG_DEPENDENCIES.md` for the full list. Critical ones for the v2 pipeline:

| Catalog | Vizier ID | Used for |
|---|---|---|
| Gaia DR3 main + NSS | live ADQL | Primary input |
| Brandt 2021 HGCA | `J/ApJS/254/42/catalog` | 25-yr PMa corroboration (HIP-named candidates) |
| Kervella 2022 H2G2 | `J/A+A/657/A7/tablea1` | Independent astrometric baseline |
| Gentile Fusillo 2021 Gaia WDs | `J/MNRAS/508/3877` | WD-primary reverse hunt |
| Shahaf 2023 Triage I NS | `J/MNRAS/518/2991` | NS-candidate cross-check |
| Müller-Horn 2026 RGB+MS BH | Zenodo 10.5281/zenodo.17271785 | Most-recent BH-candidate catalog |
| Sahlmann 2025 G-ASOI ML labels | (project-internal) | Imposter labels |
| NASA Exoplanet Archive `ps` | TAP | Known planet hosts (HD 81040, HD 111232 recovery) |
| exoplanet.eu | CSV cache | Independent exoplanet catalog |
| ZTF DR23 | IRSA TAP | CV-period light curves |
| TESS QLP/SPOC + Tesscut | MAST | Eclipse confirmation |

## Pipeline versions

| Tag | Date | What's in it | Notes |
|---|---|---|---|
| **v2.0.0** | 2026-05-28 | Corrected NSS plx + K_obs/2 + F#30 logg fallback; v3 Acceleration channel; 32 truly-novel candidates; 7-step novelty | Current canonical release |
| v1.17.0 | 2026-05-18 | Multi-channel SB1 / Tycho-Gaia expansion; negative-control specificity audit; Filter #29 SB2 added | Superseded by v2 corrections |
| v1.15.0 | 2026-05-13 | Fix E (conditional-RUWE for Acceleration); HD 134574 promoted | |
| v1.14.0 / v1.13.0 / older | 2026-04 / 05 | Earlier cascade iterations | |

The v2 corrections changed M_2 values across the catalog by factors of 1.2–2.5× for high-RUWE binaries. Direct M_2 numbers from v1 should NOT be cited; use the v2 values from `data/derived/main_hunt_derived_v2.parquet` (column `M2_msun_v2`).

## How to reproduce a single source's verdict

The fastest path is the Streamlit web tool:

```bash
cd /path/to/repo
source .venv/bin/activate
streamlit run scripts/web_tool/app.py
```

Then enter any Gaia DR3 source_id, HD/HIP/TYC name, or known discovery name (Gaia BH1/BH2/BH3 are aliased). The page shows the v2-corrected verdict with all 4 filters + likely-companion-type probability spectrum + Bayesian-style HR diagram.

## How to reproduce the full catalog

```bash
# Set up environment
cd /path/to/repo
uv venv && source .venv/bin/activate
uv pip install astroquery polars pandas lightkurve emcee dynesty plotly streamlit

# 1. Fetch fresh Gaia DR3 NSS data (chunked, resumable)
python scripts/streaming/producer.py

# 2. Apply v2-corrected cascade
python scripts/streaming/v2_corrected/run_v2.py
# → produces data/derived/main_hunt_derived_v2.parquet

# 3. Apply v3 NSS Acceleration channel
python scripts/streaming/v3_acceleration/run_acceleration.py
# → produces data/derived/acceleration_v3.parquet

# 4. Run the 70-source benchmark self-test
python scripts/validate_cascade_extended_2026_05_28.py
# → produces data/validation_2026_05_28/results.csv

# 5. Apply 7-step novelty verification (requires web access)
# (no canonical script yet — manual per-candidate workflow documented in PROJECT_STATE_2026_05_28.md §3)
```

Expected runtime: ~30 min for the v2 cascade re-run; ~5 min for the v3 acceleration channel; ~10 min for the benchmark; novelty verification is per-candidate web-bound.

## Version control conventions

- One commit per logical change; no force-pushes.
- Annotated tags only for releases (v1.x.x, v2.x.x).
- v1 outputs archived to `data/archive/v1_2026_05_27/`.
- v1 docs archived to `docs/archive/root_v1/` and `docs/archive/dev_notes_v1/`.
- Production v2 outputs live in `data/derived/` and v2 docs in `docs/*_2026_05_28.md`.
- Large files (>50 MB ML models, raw Gaia chunks) are gitignored; regeneration paths documented above.
