# External Catalog Dependencies

The scripts in this repository expect local cached copies of the catalogs listed below. None of the catalogs are redistributed here — all are publicly available at their respective archives.

## Setup

Scripts locate the catalog cache via the `GAIA_NOVELTY_DATA_ROOT` environment variable:

```bash
export GAIA_NOVELTY_DATA_ROOT=/path/to/your/data/root
```

If `GAIA_NOVELTY_DATA_ROOT` is unset, scripts fall back to the directory above `scripts/`. The expected layout under that root is:

```
$GAIA_NOVELTY_DATA_ROOT/
└── data/
    ├── external_catalogs/
    │   ├── parquets/             # parquet-converted Vizier / TAP downloads
    │   └── raw/                  # raw CSV / FITS / TSV downloads
    └── candidate_dossiers/       # pipeline output goes here
```

You only need the catalogs that the scripts you intend to run actually load.

## Catalog list

| Catalog | File path (relative to `GAIA_NOVELTY_DATA_ROOT`) | Access |
|---|---|---|
| Gaia DR3 `nss_two_body_orbit` | `data/external_catalogs/parquets/gaia_dr3_nss_two_body_orbit.parquet` | Gaia ESA Archive TAP at https://gea.esac.esa.int/tap-server/tap |
| Gaia DR3 `nss_acceleration_astro` | `data/external_catalogs/parquets/gaia_dr3_nss_acceleration_astro.parquet` | Gaia ESA Archive TAP |
| HGCA Brandt 2024 | `data/external_catalogs/raw/hgca_brandt_2024.csv` | Brandt 2024 ApJS supplementary table; see also Brandt 2021 (`brandt2021_hgca.parquet`) |
| Kervella 2022 PMa | `data/external_catalogs/parquets/kervella2022_pma_dr3.parquet` | VizieR catalog `J/A+A/657/A7` |
| Penoyre 2022 RUWE catalog | `data/candidate_dossiers/penoyre_mining_2026_05_12/binarydata.ecsv` | Zenodo `10.5281/zenodo.6792290` (paper II "binarydata") |
| Tokovinin MSC | `data/external_catalogs/raw/tokovinin_msc/tokovinin_msc_2018_components.csv` | VizieR `J/ApJS/235/6` |
| Sahlmann & Gomez 2025 ML labels | `data/external_catalogs/literature/sahlmann_gomez_ml/labelled_sources.csv` + supplementary tables | https://github.com/Johannes-Sahlmann/gaia-dr3-astrometric-orbits-ml (or paper supplementary) |
| Arenou 2023 (Gaia Coll. 2023b) | extracted from Tables 11 + §8.5–8.8 of A&A 674 A34 | Vizier `J/A+A/674/A34` or paper PDF |
| Unger 2023 verdicts | extracted from A&A 680 A16 Tables | paper PDF text extraction |
| Barbato 2023 CORALIE table 2 | `data/external_catalogs/barbato2023/table2.tsv` | VizieR `J/A+A/674/A114` |
| SB9 Pourbaix | `data/external_catalogs/sb9_pourbaix/sb9_main.tsv` + `sb9_orbits.tsv` | VizieR `B/sb9` |
| Marcussen & Albrecht 2023 Table 1 | local PDF text extraction | AJ 165 266 (arXiv:2305.08623) |
| Mills 2018 N2K target list | extracted from AJ 156 213 | paper PDF text |
| Feng 2022 230-companion catalog | `data/external_catalogs/literature/feng2022/table3.dat` | VizieR `J/ApJS/262/21` |
| Trifonov 2025 HIRES catalog | `data/external_catalogs/parquets/trifonov2025_hires_targets.parquet` + `trifonov2025_hires_rv.parquet` | Trifonov 2025 supplementary (catalog v2) |
| WDS Washington Double Star | `data/external_catalogs/wds/wds_b_wds.parquet` (or .tsv) | VizieR `B/wds` |
| NASA Exoplanet Archive `ps` | `data/external_catalogs/parquets/nasa_exo_ps_gaia_id.parquet` | TAP at https://exoplanetarchive.ipac.caltech.edu/TAP/sync |
| exoplanet.eu catalog | `data/external_catalogs/exoplanet_eu_catalog.csv` | https://exoplanet.eu/catalog/csv/ |
| HARPS RVBank Trifonov 2020 | `data/external_catalogs/parquets/harps_rvbank.parquet` + `harps_rvbank_targets.parquet` | Trifonov 2020 A&A 636 A74 (Zenodo) |
| HIRES RVs (Trifonov 2025) | same as above HIRES files | Trifonov 2025 |
| APOGEE DR17 allVisit | `data/external_catalogs/parquets/apogee_dr17_allVisit.parquet` | SDSS DR17 (https://www.sdss.org/dr17/) |
| GALAH DR4 RVs | `data/external_catalogs/parquets/galah_dr4_rv.parquet` | https://www.galah-survey.org/dr4/ |
| LAMOST DR10 RVs | `data/external_catalogs/parquets/lamost_dr10_multi_epoch_rv.parquet` | LAMOST data center (https://www.lamost.org/lmusers/) |
| CARMENES Cortés-Contreras 2024 | local TSV download from VizieR | VizieR `J/A+A/680/A180` |
| NASA Exoplanet Archive published RVs | `data/external_catalogs/parquets/nasa_exo_rv.parquet` + `nasa_exo_rv_star_coords.parquet` | NASA Exoplanet Archive TAP |
| TIC v8.2 stellar parameters | TAP query at MAST | https://archive.stsci.edu/missions/tess/catalogs/ |
| TESS QLP HLSP light curves | downloaded as needed via `lightkurve` | MAST |
| ESO archive | TAP at https://archive.eso.org/tap_obs/sync | per-target on demand |
| SIMBAD | live query (no local cache needed) | https://simbad.cds.unistra.fr (or https://simbad.harvard.edu mirror) |

## Notes

1. Several scripts include partial CDS Vizier ingest helpers but assume the user has already downloaded the relevant table. Add fresh downloads if any cached file is missing.
2. The pipeline is built to fail gracefully when a catalog is missing — the missing filter simply has no effect on the cascade, and the source survives that filter by default. This means an incomplete catalog setup will produce more permissive (more false-positive-prone) results, not fewer results.
3. Catalog file formats vary (parquet, CSV, TSV, ECSV, FITS). The scripts use `polars.read_csv`, `polars.read_parquet`, or `astropy.table.Table.read` as appropriate.
4. The CARMENES catalog and certain VizieR-only resources require manual download from the CDS interactive query form; bulk TAP-based pulls do not always work for these.
5. None of the catalogs in this list are redistributed in this repository. All are publicly available at the URLs above. The local cache layout described here is a convenience for the scripts, not a redistribution.
