# Gaia DR3 dormant compact-object & substellar companion search

[![release v2.0.1](https://img.shields.io/badge/release-v2.0.1-blue)](https://github.com/alejandrozarco/gaia-dr3-substellar-novelty-search/releases/tag/v2.0.1)
[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.20162959.svg)](https://doi.org/10.5281/zenodo.20162959)

Filter-cascade pipeline that derives companion-mass estimates from the Gaia DR3 NSS Orbital, AstroSpectroSB1, OrbitalAlternative, and Acceleration channels, cross-references them against published catalogs, and surfaces candidate dormant black holes, neutron stars, sub-Chandrasekhar white dwarfs, brown dwarfs, and exoplanets.

> Experimental. Confirmed candidates are those with **independent second-method evidence** from archival data. All other candidates require follow-up before any discovery claim.

## What's in this repo

| Path | Purpose |
|---|---|
| **`docs/CANDIDATES.md`**  | **Authoritative candidate list with verdicts and dossier links.** |
| **`docs/dossiers/`**       | **Per-target 9-section archival workups.** |
| `docs/METHODOLOGY.md`     | The three v2 cascade corrections (NSS-parallax + K_obs/2 + F#30 logg fallback). |
| `CATALOG_DEPENDENCIES.md` | Required external catalogs (Brandt HGCA, Kervella PMa, NEA, exoplanet.eu, Shahaf+ 2023, Gentile Fusillo, …). |
| `data/derived/*.parquet`  | v2 + v2_relaxed + v2_alt + v3 production catalogs. |
| `scripts/streaming/`      | Cascade pipeline: producer + consumer + filters. |
| `scripts/streaming/v2_corrected/` | v2 cascade + relaxed-producer + OrbitalAlternative ingest. |
| `scripts/streaming/v3_acceleration/` | NSS Acceleration channel (P-degenerate compact-object candidates). |
| `scripts/web_tool/`       | Streamlit single-source interactive cascade. |
| `tests/`                  | Cascade end-to-end + filter unit tests + benchmark regressions. |

## Confirmed candidates (independent 2-channel)

| Object | Class | Confirmation |
|---|---|---|
| CRTS J051419+0111 | CV (DN, period gap) | ZTF DR23 P=180.05 min + TESS 25% eclipse at the ZTF period |
| Gaia DR3 3155543945892767232 | NS candidate around K1III RGB giant | NSS AstroSpectroSB1 P=543.27 d + LAMOST 2-epoch ΔRV consistent with predicted NSS phase at χ²=0.36 |

All other candidates (Strong / Tier-1 / Tier-2 / demoted) are listed in `docs/CANDIDATES.md`.

## Quick start

```bash
# Single-source interactive cascade
source .venv/bin/activate
streamlit run scripts/web_tool/app.py
```

Enter any Gaia DR3 source_id, HD/HIP/TYC/2MASS name, or one of the discovery aliases (`Gaia BH1`, `Gaia BH2`, `Gaia BH3`).

```bash
# Reproduce the bulk catalogs
python scripts/streaming/producer.py
python scripts/streaming/v2_corrected/run_v2.py          # → main_hunt_derived_v2.parquet
python scripts/streaming/v2_corrected/producer_relaxed.py
python scripts/streaming/v2_corrected/run_v2_relaxed.py  # → main_hunt_derived_v2_relaxed.parquet
python scripts/streaming/v2_corrected/run_orbital_alt.py # → main_hunt_derived_v2_alt.parquet
python scripts/streaming/v3_acceleration/run_acceleration.py # → acceleration_v3.parquet
```

External catalogs required by the cross-matches: see `CATALOG_DEPENDENCIES.md`.

## Citation

If you use this pipeline or its candidate lists, please cite:
- Gaia Mission (Gaia Collaboration 2016, A&A 595, A1) + Gaia DR3 (Gaia Collaboration 2023, A&A 674, A1)
- Gaia DR3 NSS pipeline (Halbwachs et al. 2023, A&A 674, A9)
- This repository — concept DOI [10.5281/zenodo.20162959](https://doi.org/10.5281/zenodo.20162959) (latest archived release), or the per-version DOI. v2.0.1 = [10.5281/zenodo.20421566](https://doi.org/10.5281/zenodo.20421566).

## License

Code: `LICENSE`. Data: `LICENSE-DATA`. Citation metadata: `CITATION.cff`.
