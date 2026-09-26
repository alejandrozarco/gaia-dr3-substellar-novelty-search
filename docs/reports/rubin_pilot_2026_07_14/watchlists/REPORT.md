# Lasair-LSST passive watchlists — build report

**Date:** 2026-07-14 (UTC)
**Job:** community-scan rank 1 — build Lasair-LSST watchlists from existing project lists.
**Work dir:** `/tmp/rubin_pilot/watchlists/`

---

## 1. Token gate — BLOCKED (service unreachable, token validity UNDETERMINED)

The Lasair token (`~/.config/lasair/token`, 40 chars, value never printed) could **not**
be tested: every Lasair host at `*.lsst.ac.uk` is unreachable at build time, from **two
independent network paths**:

| Host | Local curl (this machine) | Anthropic fetcher (independent path) |
|---|---|---|
| `api.lasair.lsst.ac.uk` (192.41.122.98) — documented lasair-lsst API base | connect timeout (HTTP 000, 15-45 s; ping 100% loss; port 80 also dead) | — |
| `lasair-lsst.lsst.ac.uk` (192.41.122.53) — LSST web UI | connect timeout | `ECONNREFUSED` |
| `lasair-ztf.lsst.ac.uk` (192.41.122.132) — ZTF control instance | connect timeout | `ECONNREFUSED` |
| `lasair.lsst.ac.uk` | connect timeout | — |
| control: `www.google.com` | HTTP 200 | (readthedocs fetches fine) |

Tested 2026-07-14 ~09:10-09:26 UTC (final retry 09:26:33 UTC, 30 s timeout, sandbox
disabled — same result). DNS resolves; TCP connections are refused/black-holed on both
443 and 80. Because **both** the LSST instance and the ZTF control failed identically at
the network layer, the planned discrimination ("token invalid" vs "token valid but wrong
instance") could not be run — the gate outcome is **service-side outage/firewall, not a
token verdict**. The Lasair front page (via web search snippet) says "25 June 2026:
Upgrade complete, Lasair running normally", so this looks like a transient outage or an
IP-range block, not a decommissioning.

**Re-test command (no token echoed):**
```bash
TOKEN=$(cat ~/.config/lasair/token)
curl -s -o /dev/null -w "%{http_code}\n" --header "Authorization: Token $TOKEN" \
  --data "ra=194.494&dec=48.851&radius=10.0&requestType=count" \
  https://api.lasair.lsst.ac.uk/api/cone/     # lasair-lsst
curl -s -o /dev/null -w "%{http_code}\n" --header "Authorization: Token $TOKEN" \
  --data "ra=194.494&dec=48.851&radius=10.0&requestType=count" \
  https://lasair-ztf.lsst.ac.uk/api/cone/     # ztf control
# 200 = token valid on that instance; 401 = invalid/wrong instance; 000 = still down
```
Docs consulted: https://lasair-lsst.readthedocs.io/en/main/core_functions/rest-api.html
(base URL `https://api.lasair.lsst.ac.uk/api/`, header `Authorization: Token <key>`).

## 2. API watchlist creation — NOT AVAILABLE (independent of the outage)

The lasair-lsst REST API documents only `/cone/`, `/query/`, `/object/`,
`/sherlock/object/`, `/sherlock/position/` — **no watchlist-creation endpoint**. The
watchlists doc (https://lasair-lsst.readthedocs.io/en/main/core_functions/watchlists.html)
describes creation via the **web interface only** (logged-in users). So even with a valid
token, `ao-dormant-co-2026` / `ao-known-objects-2026` cannot be created programmatically;
the upload is the user's UI action (section 6).

## 3. Watchlist (a): `ao-dormant-co-2026.csv` — 13 rows

Source: `docs/CANDIDATES.md` roster + the 9 pre-registered objects of
`docs/dr4_preregistration_2026_06_01.md` (core 4 + Addendum A.1-A.5). Coordinates from
one **anonymous Gaia DR3 TAP query** by source_id (all 13 resolved;
raw pull: `/tmp/rubin_pilot/gaia_dr3_coords_raw.csv`).

- **9 pre-registered core:** WG26 (6092654861665006592), WDJ020915 (332248057157474176),
  WDJ060042 (2909342818326298112), UCAC4_313-025977 (5612039087715504640),
  3155543945892767232, 5858574810404752256, 1593152388271709824,
  HD157033 (4111149395881722496), ObjectB (3161546596480983040).
- **4 roster context:** HD264291 (3378588057203660160), WDJ205650 (1736555475066523008),
  APMPM_J0710-5704 (5486916932205092352), SCR_J1441-7338 (5796338299045711232).

**Epoch handling (time-axis rule):** Gaia DR3 positions are `ref_epoch=2016.0`; each row
was proper-motion-propagated to **J2026.5** (dt = +10.5 yr; pmra already contains cos-dec;
`ref_epoch==2016.0` asserted for every row). Per-row match radius =
`max(1.5, 1.5 + PM_tot x 10 yr)` arcsec, so another decade of PM drift stays inside the
cone — e.g. APMPM J0710 (PM ~468 mas/yr) gets 6.18", WG26 2.40", low-PM rows 1.5-2".
File format: `RA, Dec, ID, radius` (decimal degrees / arcsec), **no header** — the
documented Lasair upload format with the optional 4th per-row radius column.
Full provenance (source_id, PM, parallax, G, tier): `ao-dormant-co-2026_provenance.csv`.

## 4. Watchlist (b): `ao-known-objects-2026.csv` — 19,168 rows

Source: project known-objects store
(`~/claude_projects/ostinato/data/external_catalogs/known_objects/known_objects.parquet`,
schema per `scripts/known_objects/store.py` / README; 11,345,365 rows total).

**Scoping decision (honest bucket):** the store is 99.83% two *bulk all-sky reference
catalogs* — `vsx_full` 10,304,353 + `milliquas` 1,021,800 = 11,326,153 rows — ingested as
front-filter reference data, not project objects. A watchlist that size is impossible
(docs: large lists hit Gateway Timeout at ~60 s — orders of magnitude beyond UI upload)
and redundant (Lasair's own Sherlock/annotation layer already crossmatches major
variable/AGN catalogs). **Excluded.** The watchlist carries the 11 curated project
catalogs, deduped (19,212 -> 19,168 after removing identical name+position rows shared
across catalogs; unique IDs enforced):

| catalog | rows |
|---|---:|
| garciazamora2023_xp_wd | 12,094 |
| ritter_kolb | 2,156 |
| downes_cv | 1,797 |
| erass1_gaia_v2 | 665 |
| rodriguez2025_erass1_cv | 589 |
| xp_carbon_stars | 451 |
| erass1_cv_cat | 444 |
| akras2019_symbiotic | 406 |
| halbwachs2023_binary_masses_amrf3 | 306 |
| garciazamora2023_xp_dz | 257 |
| session_deflated | 3 |

Format: `RA, Dec, ID`, no header, no per-row radius -> set the **default radius 1.5"**
at creation time (per task spec; note the store's own front-filter matches at 3" because
catalog positions are heterogeneous-epoch — if high-PM CVs matter, 2" is a defensible
default instead). Names sanitized (`[,| ]` -> `_`). Full provenance (otype, catalog,
source_id, pulled_utc): `ao-known-objects-2026_provenance.csv`.
Caveat: at 19k rows this is near the size where the docs warn watchlist *creation* can
time out; if the UI 504s, the docs say to email the Lasair team.

## 5. Solar-system movers — EXCLUDED from both lists

Fixed-position watchlists crossmatch a static RA/Dec cone against alerts; a solar-system
object moves degrees per month, so a fixed cone is meaningless for it — Rubin SSOs are
handled by the MPC/Rubin SSP pipeline, not broker watchlists. Checked concretely:

- The known-objects store contains **0 solar-system entries** (all 11 curated catalogs
  are stellar/AGN; regex scan of `otype` for asteroid/comet/SSO/minor-planet = 0 rows).
- The project's actual movers — precovery-campaign targets (330836) Orius, (88268)
  2001 KK76, 2001 KN76, etc. — were **deliberately not added**. Tracking them on Rubin
  requires an ephemeris-keyed service (MPC observation matching / Rubin SSP), not a
  Lasair fixed-position watchlist.

## 6. USER actions required (you, personally — not the agent)

1. **When Lasair is back up** (check https://lasair-lsst.lsst.ac.uk/): log in. Your
   account/token are from the ZTF-era instance; **lasair-lsst is a separate instance**,
   so if the login or token is not recognized, re-register there (agent must not create
   accounts). After login, your LSST-instance API token is on your profile page
   (top-right menu -> "My Profile").
2. Optionally verify the old token first with the re-test commands in section 1.
3. **Create watchlist 1:** Watchlists (top menu) -> Create/new watchlist ->
   name `ao-dormant-co-2026`, default radius 1.5 (per-row radii in the file override it)
   -> paste or upload `/tmp/rubin_pilot/watchlists/ao-dormant-co-2026.csv` -> tick
   **active** -> save.
4. **Create watchlist 2:** same flow, name `ao-known-objects-2026`, default radius 1.5"
   (or 2", see section 4) -> upload
   `/tmp/rubin_pilot/watchlists/ao-known-objects-2026.csv` -> tick **active** -> save.
   If it 504s (19k rows), email the Lasair team per the docs.
5. Copy the files somewhere durable — `/tmp` does not survive a reboot
   (provenance CSVs sit alongside them).

## Deliverables

| File | Rows | What |
|---|---:|---|
| `ao-dormant-co-2026.csv` | 13 | candidate roster, J2026.5, per-row radius |
| `ao-dormant-co-2026_provenance.csv` | 13 | + source_id, PM, plx, G, tier |
| `ao-known-objects-2026.csv` | 19,168 | curated known-objects store extract |
| `ao-known-objects-2026_provenance.csv` | 19,168 | + otype, catalog, source_id |
| `/tmp/rubin_pilot/gaia_dr3_coords_raw.csv` | 13 | raw Gaia DR3 TAP pull |

**Bottom line:** both watchlist files are ready; token validity on lasair-lsst is
*undetermined* (full lsst.ac.uk outage from two networks at build time, ZTF control
equally dead -> network-layer, not auth-layer); API creation is impossible by design
(no watchlist endpoint) -> the upload is a 5-minute user UI action once the service
returns.
