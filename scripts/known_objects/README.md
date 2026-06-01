# known_objects — front-of-pipeline "is it already catalogued?" filter

**Problem this solves.** Hunts were checking novelty at the *back* — a candidate
got full deep-vet effort and only then turned out to be a catalogued object (e.g.
the eRASS1 lane deep-vetted **ASASSN-14gb** and **ATO J103.1497−07.9895**, both
already-published dwarf novae, because its novelty gate hit a single null-prone
SIMBAD field). This package stores the "already known" objects + the catalogues
they came from, and crossmatches candidates **at the front**, so vetting is spent
only on genuinely-uncatalogued sources.

## Layout
- `reference_catalogs.py` — the registry: which public catalogues define "known"
  per lane class (`cv`, `accretor`, `wd`, `runaway`, `variable`), with VizieR/TAP
  ids. Programmatic companion to `CATALOG_DEPENDENCIES.md`.
- `store.py` — `KnownObjectStore`: load the cached store, `annotate(df)` /
  `match(ra, dec, source_id)` (positional cone + exact Gaia source_id), `append`.
- `build.py` — pull the registry catalogues into the store + seed this session's
  deflated objects. Re-runnable, incremental, per-catalogue-graceful.
- `test_known_objects.py` — offline unit tests.

## Store
Persisted as parquet in the catalogue cache (**not** committed — rebuildable;
same no-redistribute policy as the rest of `data/external_catalogs/`):
`data/external_catalogs/known_objects/known_objects.parquet`
(override with `GAIA_NOVELTY_DATA_ROOT` or `KnownObjectStore(path=...)`).

Schema: `source_id` (Gaia DR3, where the catalogue provides it), `ra`, `dec`,
`name`, `otype`, `catalog` (provenance tag), `pulled_utc`.

Matching = positional cone (default 3″) **plus** exact Gaia `source_id` — the
source-id leg catches high-proper-motion stars whose catalogue position has
drifted arcseconds from the Gaia epoch (the trap that made naive SDSS cones miss
the hyper-velocity-WD spectra this session).

## Build / refresh
```bash
PY=/Users/legbatterij/claude_projects/ostinato/.venv/bin/python
$PY scripts/known_objects/build.py                 # all catalogues + session seed
$PY scripts/known_objects/build.py --classes cv     # CV/accretor catalogues only
$PY scripts/known_objects/build.py --no-vsx         # skip the big VSX pull
$PY scripts/known_objects/build.py --dry-run
```
Seeded catalogues (curated, not "all of VizieR"): Ritter-Kolb `B/cb`, Downes
`V/123A`, **Rodriguez+2025 `J/PASP/137/A4201`** (the published eRASS1×Gaia CV
selection — caught both of this session's false "new" CVs), eROSITA-CV
`J/A+A/698/A321`, VSX cataclysmic subset `B/vsx`, Gaia DR3 `vari_classifier_result`
CV class, Raddi+2019 LP40 `J/MNRAS/489/1489`. Extend by adding a `CatalogSpec`.

## Use it in a hunt (the point)
```python
from known_objects import KnownObjectStore
store = KnownObjectStore()                      # cached parquet
cand  = store.annotate(cand, ra_col="ra", dec_col="dec", id_col="id")
fresh = cand[~cand["known"]]                    # spend vetting ONLY on these
# cand["known_catalogs"], ["known_name"], ["known_otype"], ["known_sep_arcsec"] carry provenance
```
For the small surviving shortlist, still do a **live** SIMBAD/VizieR check as a
backstop for classes not yet cached — the store narrows the field cheaply; the
live check is the final word.

## Feeding it back
When a hunt or deep-vet identifies a known object, append it (with the catalogue
that settled it) so the next hunt catches it at the front:
```python
store.append(known_rows_df, catalog="erass1_gaia_v2")   # then store.save()
```
This is how the store accumulates — every deflation makes the next run faster.
