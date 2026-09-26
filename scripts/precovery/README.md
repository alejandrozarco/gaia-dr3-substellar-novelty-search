# Tier-1 Bycatch Harvester (`scripts/precovery/`)

Turn every precovery/arc-extension wave into a **passive novelty net**. A wave already
downloads single-exposure catalog detections for the field/night it is searching while
chasing one target. `bycatch.py` re-reads *all* of those detections and asks: does any
*other* same-night set form a moving-object tracklet? Matched to a known minor planet →
**known-object bycatch** (logged). Unmatched → an **UNKNOWN candidate** — the discovery
channel, flagged for human/referee review, **never auto-claimed**.

This is the passive twin of the active precovery lane (gate R1 = GO, community-confirm
mode): zero extra downloads, zero telescope, MPC-creditable if a real unknown survives
referee review.

## Files
| File | Role |
|---|---|
| `bycatch.py` | Core module + CLI. Form tracklets → reject stationarity/static/mag → identify vs MPC. |
| `test_bycatch.py` | pytest suite driven by REAL campaign artifacts (2009 HW77 positive, 2001 QT322 negative) + unit tests. |
| `README.md` | This file. |

## Pipeline
1. **Same-night pairs/triplets** whose implied sky motion is in a rate window
   (default `0.5–120 "/hr`); triplets also require a consistent direction (PA within
   `20°`) and consistent segment rate.
2. **Reject stationarity** — implied rate below `0.5 "/hr`, **or** either endpoint within
   `1.5"` of a supplied static-source (mean-object) catalog. *This static catalog is the
   decisive false-positive filter* (see below).
3. **Magnitude consistency** between endpoints (`≤1.0` mag same filter, `≤2.0` cross-filter).
4. **Identify** each survivor against the **MPC MPChecker** CGI at the tracklet's mean
   position/epoch/obscode: nearest known minor planet within `30"` → `known` (log the
   designation); none → `unknown_candidate`; query failed/offline → `unidentified_offline`.

Output: `bycatch_tracklets.csv` (one row per surviving tracklet, with `classification`,
`mpc_designation`, rate, PA, members) + a summary dict (counts + rejection tally + config).

## Why the static (mean-object) catalog is not optional
On the 2001 QT322 negative control, `~0.1"` of catalog scatter on the *same* fixed star
across exposures `~1.5` min apart reads as a few `"/hr` — enough to pass the rate floor.
The full QT322 field produces **9 spurious tracklets with no static catalog** and **0**
once the mean-object catalog is supplied. Always pass `static_sources`. When you have a
survey `object`/mean table use it directly; otherwise build one from the detections'
repeat-source ids with `bycatch.mean_object_catalog(detections, group_key="objectid")`.

## Controls baked into the test suite
- **POSITIVE** — the 6 (330836) Orius detections (`verify/2009_HW77/updated_astrometry.csv`):
  the 2013-03-02 (`~0.81 "/hr`) and 2015-04-27 (`~3.52 "/hr`) same-night pairs emerge as
  tracklets; the live MPC step resolves both to `(330836) Orius` (`0.7"` / `1.7"` match).
  The 2014 detections are 2 days apart and correctly do **not** pair.
- **NEGATIVE** — the stationary NSC detections (`verify/2001_QT322/nsc_real_results.json`,
  incl. the spurious short-baseline pair): with the mean-object catalog, **zero** tracklets
  survive; the net stays silent on a valid null.

Run: `PYTHONPATH=scripts/precovery ~/claude_projects/ostinato/.venv/bin/python -m pytest scripts/precovery/test_bycatch.py -v`
(the two MPC asserts skip-if-offline; set `BYCATCH_OFFLINE=1` to force offline.)

## Input format
CSV path or list of dicts. Column aliases are auto-detected (case-insensitive):
`mjd`|`mjd_utc`, `ra`|`ra_deg`, `dec`|`dec_deg`|`decl`, `mag`|`V`, `filter`|`filt`,
`id`|`measid`, `objectid`|`group_id` (for mean-object grouping), `exposure`|`expo`|`frame`,
`obscode`|`oc`. Only `mjd`/`ra`/`dec` are required.

## CLI
```
PYTHONPATH=scripts/precovery python scripts/precovery/bycatch.py \
    detections.csv --static meanobjects.csv --out /tmp/novelty_gate/bycatch/out.csv
# --no-identify to skip the network MPC step; --rate-min / --rate-max to retune the window
```

---

## Wave usage paragraph (copy verbatim into a wave's steps)

> **Bycatch pass (run once per searched field/night, after the primary target search).**
> Collect every single-exposure catalog detection you already pulled for the field into a
> list of dicts or a CSV with at least `mjd, ra, dec, mag, exposure` (plus a per-detection
> `id` and, if available, the survey mean-object `objectid` as `group_id`). Build the
> static-source catalog: if the survey exposes a mean `object` table use it, else call
> `bycatch.mean_object_catalog(detections, group_key="objectid")`. Then run
> `summary = bycatch.run_bycatch(detections, static_sources=static, identify=True,
> out_csv="/tmp/novelty_gate/bycatch/<target>_bycatch.csv")` using the ostinato python.
> Read `summary["n_unknown_candidate"]`: if `0`, note "bycatch: 0 unknown candidates" in the
> wave log and move on. For any `unknown_candidate` row in the CSV, do **not** claim a
> discovery — treat it as a lead: re-query the MPC by hand, widen the match radius, check the
> endpoints are not artifacts/known-object blends, and surface it to the main thread for
> referee review and (only on the user's action) possible MPC submission. Log every `known`
> row's designation as bycatch provenance. The static catalog is mandatory — without it the
> field fabricates spurious same-star tracklets (verified on the 2001 QT322 control).
