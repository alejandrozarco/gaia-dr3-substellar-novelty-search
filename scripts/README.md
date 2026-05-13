# Pipeline Scripts

Each script is independently runnable from a Python environment with `polars`, `numpy`, `astropy`, `dynesty`, and `orvara`. Scripts are numbered in the order they would be applied in a fresh pipeline run.

| File | Purpose |
|---|---|
| `01_filter_cascade_mega.py` | Apply the full Stage 1–3 cascade (substellar mass cut + inclination marginalization + 16 filter sources) to combined NSS Orbital + Acceleration tables |
| `02_inclination_marginalize.py` | Compute inclination-marginalized M_2 posterior from Thiele-Innes elements (NSS Orbital) or accel + jerk (NSS Acceleration9) |
| `03_published_stellar_filter.py` | Cross-match against Barbato 2023, SB9, Marcussen 2023, Sahlmann ML, Unger 2023 |
| `04_filters_l17_l18_l19.py` | Apply K_RV/K_pred pre-screen (#17), Trifonov 2025 HIRES sb_flag (#18), WDS visual binary within 15" (#19) |
| `05_lessons_33_34_retroactive.py` | Apply universal Kervella M_2 filter (#34) + inclination-marginalized A9 jerk (#33) retroactively |
| `06_rv_archive_inventory.py` | Cross-match all candidates against HARPS RVBank, HIRES, APOGEE DR17, GALAH DR4, LAMOST DR10, NASA Exoplanet Archive |
| `07_multi_body_methodology.py` | Pick #2 multi-body methodology: compute excess Kervella dVt above inner-orbit prediction |
| `08_two_keplerian_joint_fitter.py` | Multi-archive Bayesian 0/1/2-Keplerian joint fit via dynesty NestedSampler with per-instrument γ + σ_jit |

## External catalog dependencies

The scripts assume locally cached copies of the following catalogs (see `REPORT.md` Section 1 for full reference list):

- Gaia DR3 `nss_two_body_orbit` and `nss_acceleration_astro` (TAP query at gea.esac.esa.int)
- HGCA Brandt 2024 (ApJS supplementary table)
- Kervella 2022 PMa (VizieR J/A+A/657/A7)
- Penoyre 2022 RUWE catalog (Zenodo 10.5281/zenodo.6792290)
- Tokovinin MSC (VizieR J/ApJS/235/6)
- Sahlmann & Gomez 2025 ML labels (GitHub supplementary)
- Arenou 2023 multiplicity catalog (Gaia DR3 paper)
- Unger 2023 (A&A 680 A16 Table A.1)
- Barbato 2023 (VizieR J/A+A/674/A114 table 2)
- SB9 Pourbaix (VizieR B/sb9)
- Marcussen & Albrecht 2023 (AJ 165 266 Table 1)
- Trifonov 2025 HIRES catalog (VizieR or arXiv supplementary)
- WDS Washington Double Star (VizieR B/wds)
- NASA Exoplanet Archive `ps` table (TAP at exoplanetarchive.ipac.caltech.edu)
- exoplanet.eu catalog (https://exoplanet.eu/catalog/csv/)
- TESS QLP HLSP light curves (MAST)
- HARPS RVBank Trifonov 2020 (Zenodo)
- HIRES Trifonov 2025 catalog
- APOGEE DR17 allVisit (SDSS DR17)
- GALAH DR4 (data.galah-survey.org)
- LAMOST DR10 (LAMOST data center)
- CARMENES DR1 (Cortés-Contreras+ 2024)
- ESO Archive Phase 3 + dbo.raw (TAP at archive.eso.org/tap_obs/sync)
