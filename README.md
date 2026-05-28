# Gaia DR3 dormant compact-object & substellar companion search

[![release v2.0.1](https://img.shields.io/badge/release-v2.0.1-blue)](https://github.com/alejandrozarco/gaia-dr3-substellar-novelty-search/releases/tag/v2.0.1)
[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.20162959.svg)](https://doi.org/10.5281/zenodo.20162959)

A reproducible pipeline that derives companion mass estimates from the Gaia DR3 Non-Single-Star (NSS) Orbital, AstroSpectroSB1, and Acceleration catalogs, cross-references them against published catalogs, and surfaces candidate dormant black holes, neutron stars, sub-Chandrasekhar white dwarfs, brown dwarfs, and exoplanets.

> Experimental. None of the candidates listed here are observationally confirmed by independent methods except CRTS J051419+0111 (TESS-photometric eclipse). All others require follow-up before any discovery claim.

## What's in this repo

| Path | Purpose |
|---|---|
| **`docs/CANDIDATES.md`** | **Authoritative candidate list with M_2, P, e, status, and follow-up notes per target.** |
| `docs/METHODOLOGY.md` | The three v2 cascade corrections (NSS-parallax + K_obs/2 + F#30 logg fallback) — explains how the estimates were derived |
| `CATALOG_DEPENDENCIES.md` | Required external catalogs (Brandt HGCA, Kervella PMa, NEA, exoplanet.eu, etc.) |
| `data/derived/*.parquet` | v2 + v3 production catalogs: per-source M_2, filter verdicts, and provenance |
| `scripts/streaming/` | Core cascade pipeline: producer + consumer + filters |
| `scripts/streaming/v2_corrected/` | v2-corrected production pipeline (NSS plx + K_obs/2 + F#30 fallback) |
| `scripts/streaming/v3_acceleration/` | v3 NSS Acceleration channel (BH3 regime, P > Gaia baseline) |
| `scripts/web_tool/` | Streamlit single-source interactive cascade UI |

## Quick start

Interactive single-source verdicts:

```bash
source .venv/bin/activate
streamlit run scripts/web_tool/app.py
```

Then enter any Gaia DR3 source_id, HD/HIP/TYC name, or one of the discovery-name aliases (`Gaia BH1`, `Gaia BH2`, `Gaia BH3`).

Bulk reproduction of the v2 catalog:

```bash
python scripts/streaming/producer.py              # chunked Gaia ADQL fetch
python scripts/streaming/v2_corrected/run_v2.py   # v2-corrected cascade → data/derived/main_hunt_derived_v2.parquet
python scripts/streaming/v3_acceleration/run_acceleration.py  # → data/derived/acceleration_v3.parquet
```

## Candidate inventory (v2.0.0)

After second-method verification, the candidate list shrinks from 32 nominally-novel to:

| Confidence | Count | Examples |
|---|---:|---|
| **Confirmed discovery** (independent second method) | 1 | CRTS J051419+0111 — TESS photometric eclipse at the ZTF-derived 3.013 hr period |
| **Strong candidate** (single-method, awaiting follow-up) | ~5 | HD 157033 (GALAH DR4 RV available), WDJ020915.51+380425.92, WDJ060042.75-293041.36, BD+35 228, 13 additional CV-period periods |
| **Demoted / falsified by second-method** | ~26 | HGCA "BH-class" mostly stellar binaries; Gaia 5476986 retracted (RAVE noise); Stefánsson 3 likely hierarchical triples; APMPM J0710-5704 non-eclipsing |

See `docs/CANDIDATES.md` for the full table with per-target estimates and follow-up requirements.

## The v2 corrections

Two compensating bugs in the v1 cascade left M_2 systematically off by ~2× without breaking internal consistency. Both are fixed in v2:

1. **NSS parallax** preferred over `gaia_source.parallax` (the latter is orbital-motion-biased low for binaries by 1.2–2.5×).
2. **K_obs = rv_amplitude_robust / 2** — Gaia DR3 publishes peak-to-trough, not the semi-amplitude K_1. Verified against Gaia BH2 (published K_1 = 21.2 km/s vs rv_amplitude_robust = 36.96; ratio 1.74 ≈ 2 suppressed by e=0.52).
3. **Filter #30 logg fallback** chain: `logg_gspphot → logg_gspspec_ann → logg_gspspec`. Catches K-giant chromatic-bias false positives that GSP-Phot NaN missed.

Details in `docs/METHODOLOGY.md`.

## Validation against 70 published systems

| Group | Result |
|---|---|
| Confirmed Gaia BH1/BH2 | 2/2 caught as compact-mass (BH3 absent from DR3 NSS by construction) |
| Shahaf 2024 NS subset (21 confirmed via multi-epoch RV) | 21/21 produce M_2 ≥ 1.2 M_⊙; median \|ΔM\|/M = 4.5% |
| Sub-stellar recovery (HD 81040, HD 111232) | Both classified as `planet_candidate` with ~10% mass error |
| Tier-1 false-positive rate (adversarial set) | 14% |
| **Class-level recall on confirmed compact + sub-stellar** | **93% (25/27)** |

## Citation

If you use this pipeline or its candidate lists, please cite:
- Gaia Mission (Gaia Collaboration 2016, A&A 595, A1) + Gaia DR3 (Gaia Collaboration 2023, A&A 674, A1) for the underlying data
- Gaia DR3 NSS pipeline (Halbwachs et al. 2023, A&A 674, A9) for the orbital solutions
- This repository — concept DOI [10.5281/zenodo.20162959](https://doi.org/10.5281/zenodo.20162959) (always resolves to the latest archived release), or the per-version DOI for the release you used. v2.0.1 = [10.5281/zenodo.20421566](https://doi.org/10.5281/zenodo.20421566); v2.0.0 = [10.5281/zenodo.20421316](https://doi.org/10.5281/zenodo.20421316); v1.0.0 = [10.5281/zenodo.20162960](https://doi.org/10.5281/zenodo.20162960).

## License

Code: see `LICENSE`. Data: see `LICENSE-DATA`. Cite as in `CITATION.cff`.
