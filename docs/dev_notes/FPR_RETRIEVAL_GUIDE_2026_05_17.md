# Gaia FPR retrieval walkthrough (2026-05-17)

This is the practitioner's walkthrough for the Gaia Focused Product Release
(FPR, 2023-10-10) — what it contains, what's queryable, why we previously
listed it as "dead end" for our pool, and the actual numbers behind that
verdict.

## What Gaia FPR is (and isn't)

FPR is the **third** Gaia data release (after DR1, DR2, DR3). It sits
between DR3 (2022-06-13) and the upcoming DR4 (expected Dec 2026).
Crucially, it is *not* a re-issue of the main catalog. It is a focused
release of **seven specific data products** that benefitted from a
second-pass refined-processing pipeline:

| FPR table                                | What it has                                         | Pool size       |
|------------------------------------------|------------------------------------------------------|-----------------|
| `gaiafpr.crowded_field_source`           | Re-processed astro+phot for omega Cen + 8 dense fields | ~526k sources |
| `gaiafpr.vari_epoch_radial_velocity`     | Epoch RV time-series for ~~9.5k LPVs                | ~~9k sources    |
| `gaiafpr.vari_long_period_variable`      | LPV-summary subset (period, type, mean RV)           | ~~9k sources    |
| `gaiafpr.vari_rad_vel_statistics`        | Per-source RV summary statistics for FPR LPV series  | ~~9k sources    |
| `gaiafpr.interstellar_medium_params`     | DIB-based ISM properties                             | ~~5M sources    |
| `gaiafpr.interstellar_medium_spectra`    | DIB spectra                                          | ~~5M sources    |
| `gaiafpr.lens_candidates`                | Gravitationally-lensed quasar candidates             | ~~5k sources    |
| `gaiafpr.sso_source`                     | Solar-system bodies (asteroids, etc.)                | ~158k sources   |

There is **no FPR `nss_*`, no FPR `epoch_astrometry`, no FPR `vari_classifier`** —
those re-processings are planned for DR4, not FPR.

## How to query FPR (programmatically)

FPR sits in the same Gaia archive ESA TAP+ endpoint as DR3
(<https://gea.esac.esa.int/tap-server/tap>). The astroquery `Gaia` module
talks to it directly, with no extra config:

```python
from astroquery.gaia import Gaia

# Confirm a table is reachable
job = Gaia.launch_job("SELECT TOP 1 * FROM gaiafpr.vari_epoch_radial_velocity")
print(job.get_results().colnames)
# -> ['solution_id', 'source_id', 'transit_id', 'rv_obs_time', 'radial_velocity',
#     'radial_velocity_error', ...]

# Cross-match a list of Gaia source IDs against an FPR table
ids = "841536616165020416,3905850581902839168,..."  # comma-separated
q = f"SELECT source_id FROM gaiafpr.vari_epoch_radial_velocity " \
    f"WHERE source_id IN ({ids})"
job = Gaia.launch_job(q)
hits = job.get_results()
```

Same endpoint works in any ADQL client (TopCat → "Gaia DR3 TAP" service,
PyVO `Service("https://gea.esac.esa.int/tap-server/tap")`, or raw curl
against `/tap-server/tap/sync` with `LANG=ADQL`).

Live confirmation today (2026-05-17): all 8 FPR tables respond. See
`data/intermediate/fpr_table_inventory_2026_05_17.csv`.

## Why FPR matters in principle (for a brown-dwarf hunt)

Of the seven products, **only two** could plausibly add information for
our candidate list:

### (A) `gaiafpr.vari_epoch_radial_velocity` — the prize channel

This is the only place where Gaia publishes per-transit RV time-series
that you can actually fit for orbital reflex. (DR3 only publishes the
**summary** statistic `rv_amplitude_robust`; the per-epoch RVs are
restricted to the ~~370 RV-standards in `gaiadr3.epoch_radial_velocity`.)

If one of our 11 candidates were in here, we would get:

- ~~30 epoch RVs over ~~5 years of Gaia DR3 time baseline
- On Gaia's own wavelength scale (so no cross-instrument zero-point error)
- Per-epoch error bars
- → Enough to fit (P, K, e) directly, fully independently of the NSS Orbital
  astrometric solution.

That is a brand-new orbital-confirmation channel. It would convert
"tentative astrometric" to "tentative astrometric + tentative RV" without
us booking any telescope time.

**Catch**: the FPR `vari_epoch_radial_velocity` sample is selected from
DR3 `vari_long_period_variable`. LPVs are M-giant pulsators (Mira,
semiregular, OSARG). Our 11 are F/G/K dwarfs and one G8III. None of them
are LPVs. So we expect 0 cross-matches a priori.

### (B) `gaiafpr.crowded_field_source` — sanity channel

This is the re-reduction of stars in 9 dense fields (omega Cen + clusters
in the Magellanic Clouds + Sgr) that DR3 dropped or mis-fit due to
crowding. If any of our candidates were in those fields, the FPR
solution could:

- Confirm or refute the DR3 NSS Orbital fit (FPR uses the same baseline
  but a different prior on crowding).
- Sometimes produce a parallax shift, which would change M_1 and thus
  M_2.

**Catch**: none of our 11 are in any of those 9 fields. All are bright
field stars within ~~200 pc; the FPR dense fields are at distances of
4 kpc (omega Cen) to ~~50 kpc (LMC clusters).

### Tables (C)–(G) are irrelevant for us

- `interstellar_medium_*` — ISM DIB equivalent widths, not stellar.
- `lens_candidates` — extragalactic.
- `sso_source` — asteroids.

## Actual cross-match for our 11 candidates

Script: `scripts/fpr_walkthrough_2026_05_17.py`.
Live result, 2026-05-17:

| FPR table                              | Hits (out of 11) |
|----------------------------------------|------------------:|
| `gaiafpr.vari_epoch_radial_velocity`   | **0**            |
| `gaiafpr.vari_rad_vel_statistics`      | 0                |
| `gaiafpr.vari_long_period_variable`    | 0                |
| `gaiafpr.crowded_field_source`         | 0                |

For context, the DR3 back-check on the same source-id list:

| DR3 table                              | Hits |
|----------------------------------------|-----:|
| `gaiadr3.vari_rad_vel_statistics`      | 0    |
| `gaiadr3.nss_acceleration_astro`       | 2    |
| `gaiadr3.nss_two_body_orbit`           | 11   |

(NSS Orbital = 11 is expected: that table is the pool from which the 11
were originally selected. NSS Acceleration = 2 means two of our candidates
have **both** an Orbital and an Acceleration NSS solution — HD 134574 is
one, and at least one of the multi-body Orbital_Inner sources is the
other.)

## Verdict

**FPR yields zero new information for our current 11 candidates.** This
is not a pipeline limitation — it is a *selection-function mismatch*
between the FPR LPV pool and our F/G/K-dwarf pool. We should not return
to FPR for this list.

FPR **could** become relevant if we expand into:

- **Long-period giant primaries** with NSS Acceleration solutions whose
  hosts happen to also be DR3 LPVs. (Plausibly tens of sources — worth a
  separate scan, but those would be very-low-mass-ratio detections of
  hot Jupiters around dying stars, not the substellar regime we are
  hunting for.)
- **Cluster-member sources** that happen to be NSS Orbital binaries —
  the FPR crowded-field re-reduction could refute / confirm the orbit.

Neither of those is on our active roadmap. FPR is parked.

## What to revisit at DR4 (Dec 2026)

DR4 is expected to publish:

- **NSS solutions for ~10x more sources** (DR3 NSS: ~813k; DR4 NSS: ~10M+).
- **Epoch astrometry for all sources with >10 transits** — this is the
  game-changer; it lets us re-fit orbital solutions ourselves from the
  raw scans, escaping the NSS pipeline's prior assumptions.
- **Epoch RVs for all sources with sufficient transits**, not just LPVs.

When DR4 lands, every single one of our 11 candidates will get re-checked
against:

1. DR4 epoch astrometry (independent orbit fit)
2. DR4 epoch RV (independent RV time-series)
3. DR4 NSS Orbital + DR4 HGCA + DR4 Kervella PMa (refined versions of
   the channels we already used)

That is why our README states "confirmation requires Gaia DR4 (Dec 2026)
or new ground-based RV". The FPR walkthrough above just makes the "or"
explicit: FPR cannot do it.

## Reference files

- `scripts/fpr_walkthrough_2026_05_17.py` — the executable walkthrough.
- `data/intermediate/fpr_table_inventory_2026_05_17.csv` — proof all 8
  FPR tables are reachable.
- `data/intermediate/fpr_candidate_crossmatch_2026_05_17.csv` — the
  zero-hit cross-match against our 11 candidates.
- `data/intermediate/fpr_dr3_rv_backcheck_2026_05_17.csv` — DR3-side
  back-check for context.
