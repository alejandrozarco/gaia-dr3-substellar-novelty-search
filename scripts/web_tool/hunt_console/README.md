# Hunt Console

A multi-hunt **discovery console** for archival-discovery runs. Where
`scripts/web_tool/app.py` is a *single-source* deep dive onto one Gaia DR3 object,
this console sits one level up: it **monitors, browses, and triages the output of
whole hunts** — each of which scans thousands of sources and emits a ranked
candidate list.

It is a **sibling** of `app.py`, not a replacement. The two compose: the console
points you at interesting targets; you open a target in `app.py` for the full
single-source work-up.

## Six capabilities

1. **Dashboard (LIVE)** — one card per run: progress bar, survivors, status,
   runtime, and a "last heartbeat N s ago" readout with a **STALE** warning when a
   `running` hunt's heartbeat is older than 60 s. Auto-refreshes (~15 s) behind a
   🔴 Live toggle.
2. **Target Browser** — a run's `candidates.csv` as a sortable, filterable table
   (score slider + verdict multiselect + a triage-status column); click a row to
   select a target.
3. **Target Findings** — the selected target's `findings.json` (metrics/tables)
   plus every PNG in its directory. Per-lane render hook with a generic fallback.
4. **Sky map** — Aladin Lite v3 embed of the hunt's candidate RA/Dec (markers →
   id); degrades to a matplotlib RA/Dec scatter if the CDN/JS is unavailable.
5. **Triage** — promote / flag / reject buttons (on the Findings view) that write
   a human verdict to a sidecar `triage.json`; reflected in the Browser table.
6. **Cross-hunt search** — a source-id box that finds the id across every hunt's
   candidate list.

## Files

| File | Layer | Purpose |
|------|-------|---------|
| `hunt_data.py` | **pure python (no streamlit)** | the data layer — reads/writes the contract; unit-testable |
| `hunt_console.py` | Streamlit (thin) | the six views; all disk I/O delegated to `hunt_data` |
| `ingest_run.py` | adapter | retro-fits an existing raw run into the contract (demo) |
| `README.md` | — | this file |

The split is deliberate: `hunt_data.py` imports **no streamlit**, so it runs in a
plain `python` REPL or pytest. Streamlit caching (`@st.cache_data(ttl=15)`) lives
only in `hunt_console.py`.

---

## The hunt-output contract

The runs directory is configurable via the `HUNT_RUNS_DIR` environment variable
(default `/tmp/hunt_runs`). Each hunt is one sub-directory:

```
$HUNT_RUNS_DIR/<hunt_id>/
  manifest.json          # static run metadata (written once at start, status updated at end)
  progress.json          # LIVE heartbeat — overwritten each batch
  candidates.csv         # ranked candidate list
  triage.json            # human triage, keyed by id   (written by the CONSOLE, not the hunt)
  targets/<id>/
    findings.json        # per-target structured result
    *.png                # per-target plots (light curve, cutouts, spectra overlay, ...)
```

### `manifest.json`

```json
{
  "hunt_id": "ir_nova_2026_06_01",
  "lane": "ir_nova",
  "title": "IR-obscured eruption / nova lane — North-America / Pelican window",
  "status": "running | done | failed",
  "started_at": "2026-06-01T00:05:00Z",
  "ended_at":   "2026-06-01T01:07:00Z",
  "params": { "...": "lane-specific knobs (box, cuts, catalogs)" },
  "total_planned": 97
}
```

Any extra keys (e.g. a `headline`) are preserved and surfaced by the dashboard.

### `progress.json` — the live heartbeat

Overwritten **atomically** each batch. The dashboard polls it; a `running` hunt
whose `ts` is > 60 s old is flagged **STALE**.

```json
{
  "ts": 1748739600.0,          // epoch seconds of this heartbeat
  "processed": 1840,
  "total": 5000,
  "survivors": 12,
  "stage": "stage2_neowise_lightcurves",
  "last_id": "demo_b0-001840",
  "message": "processing visit light curves (1840/5000)"
}
```

### `candidates.csv`

Ranked best-first. **Required** columns (the console guarantees these exist even
if a hunt omits one):

| column | type | meaning |
|--------|------|---------|
| `id` | **string** | source id — *kept as a string everywhere*; never coerce to int/float (Gaia-style ids overflow float64; tile ids are alphanumeric) |
| `ra` | float (deg) | right ascension |
| `dec` | float (deg) | declination |
| `score` | float | ranking score, larger = more interesting (lane-defined) |
| `verdict` | string | the hunt's own automated classification (e.g. `PLATE_BLANK_NO_CATALOG`, `SIMBAD:Y*O`, `NOT_RISING_CLEAN`) |

Any number of **lane-specific extra columns** may follow and are preserved
(displayed in the Browser and the candidate-row expander).

> **Note on `score` for the `ir_nova` lane:** here `score` encodes *IR-rise
> evidence* — the brightening significance × amplitude of the W1/W2 NEOWISE light
> curve. A genuine nova/FU-Ori riser scores high; non-risers (including a real
> optical-blank survivor that is *fading*) score near 0. This faithfully reflects
> hunt B's headline (zero clean risers). Use the **verdict filter** to surface the
> rare survivors regardless of score.

### `triage.json` — human verdicts (sidecar)

Written by the **console**, never by the hunt. Keyed by id. The hunt's
`candidates.csv` is **never mutated** — human opinion lives entirely here.

```json
{
  "3152p454_b0-000375": { "verdict": "promote", "ts": 1748740000.0, "note": "queue for RV follow-up" }
}
```

Verdicts: `promote` | `flag` | `reject` (and `clear` to remove an entry).

### `targets/<id>/findings.json`

```json
{
  "id": "3152p454_b0-000375",
  "lane": "ir_nova",
  "classification": "real optical blank, no catalog counterpart — KEEP for follow-up",
  "key_values": { "W2_mag": 7.32, "W1_minus_W2": 1.51, "dasch_plates": 20967, "...": "..." },
  "flags": ["PLATE_BLANK"],
  "notes": "free text shown as a blockquote on the Findings view"
}
```

`key_values` is a flat dict of scalars; the generic renderer shows the first few
as `st.metric` and the rest as a table. A lane can register a richer layout — see
**Adding a lane** below.

---

## How a hunt should write the contract

A hunt does **not** need this repo. It just writes the files. Minimal recipe:

```python
import json, os, time, tempfile, csv
from pathlib import Path

RUN = Path(os.environ.get("HUNT_RUNS_DIR", "/tmp/hunt_runs")) / "my_hunt_2026_06_01"
(RUN / "targets").mkdir(parents=True, exist_ok=True)

# 1) manifest once, at start
(RUN / "manifest.json").write_text(json.dumps({
    "hunt_id": "my_hunt_2026_06_01", "lane": "my_lane", "title": "My hunt",
    "status": "running", "started_at": time.strftime("%Y-%m-%dT%H:%M:%SZ"),
    "ended_at": None, "params": {...}, "total_planned": N,
}, indent=2))

# 2) heartbeat — ATOMIC overwrite each batch (temp file + os.replace) so the
#    dashboard never reads a half-written file:
def heartbeat(**kw):
    kw["ts"] = time.time()
    tmp = RUN / ".progress.tmp"
    tmp.write_text(json.dumps(kw))
    os.replace(tmp, RUN / "progress.json")

heartbeat(processed=i, total=N, survivors=k, stage="stage2", last_id=sid, message="...")

# 3) candidates.csv — id FIRST and as a STRING; ranked best-first.
#    Write to a temp file and os.replace if you rewrite it live.
with open(RUN / "candidates.csv", "w", newline="") as fh:
    w = csv.writer(fh); w.writerow(["id","ra","dec","score","verdict","my_extra"])
    for c in ranked: w.writerow([c.id, c.ra, c.dec, c.score, c.verdict, c.extra])

# 4) per interesting target: findings.json + any plots
tdir = RUN / "targets" / sid; tdir.mkdir(parents=True, exist_ok=True)
(tdir / "findings.json").write_text(json.dumps({
    "id": sid, "lane": "my_lane", "classification": "...",
    "key_values": {...}, "flags": [...], "notes": "..."}, indent=2))
fig.savefig(tdir / "lightcurve.png")

# 5) at the end: flip status, write a final heartbeat
man = json.loads((RUN / "manifest.json").read_text())
man["status"] = "done"; man["ended_at"] = time.strftime("%Y-%m-%dT%H:%M:%SZ")
(RUN / "manifest.json").write_text(json.dumps(man, indent=2))
```

**Atomicity matters** for `progress.json` and any live rewrite of `candidates.csv`:
the dashboard reads them while the hunt is still writing. `hunt_data` already
tolerates a truncated/half-written file (it treats an unparseable read as
"no data yet"), but writing atomically with `os.replace` makes that the rare path
rather than the common one. `hunt_data._atomic_write_json` does this for triage.

---

## Adding a lane (custom findings layout)

`hunt_console.py` has a `LANE_RENDERERS` dict mapping `lane -> callable(findings,
candidate_row)`. Register a function to control the Findings layout for your lane;
anything not registered uses `_render_generic_findings`. Example shipped:
`_render_ir_nova` lays out the WISE colours, rise significance, DASCH plate count,
and POSS SNRs as metrics.

---

## Running

```bash
# populate the demo (hunt B + a synthetic live run)
python ingest_run.py

# launch (ostinato/web_tool streamlit env)
HUNT_RUNS_DIR=/tmp/hunt_runs streamlit run hunt_console.py
```

### Auto-refresh on the Dashboard

The 🔴 Live toggle picks the best available backend, degrading gracefully:

1. `streamlit_autorefresh` if importable (smoothest);
2. else `st.fragment(run_every=15)` (Streamlit ≥ 1.33) — what this environment
   uses, since `streamlit_autorefresh` is not installed;
3. else a manual **Refresh** button + `@st.cache_data(ttl=15)`.

The Sky map degrades the same way: Aladin Lite v3 via CDN, with a matplotlib
RA/Dec scatter fallback when the JS/CDN is blocked.

## Demo content

`ingest_run.py` produces:

- **`ir_nova_2026_06_01/`** — hunt B (the IR-obscured nova lane, completed):
  97 candidates mapped to the contract, verdicts taken from the gauntlet
  (`ir_nova_vetted_*.csv`) where available, plus the one plotted survivor
  `3152p454_b0-000375` (the lone `PLATE_BLANK_NO_CATALOG`) with its NEOWISE +
  POSS plot copied in and a synthesized `findings.json`. `status="done"`,
  `progress.json` synthesized to `processed=97, total=97`.
- **`demo_live_running/`** — a tiny fabricated `running` hunt with a fresh
  heartbeat so the Live dashboard's in-progress state (and STALE detection, once
  the heartbeat ages past 60 s) is demonstrable on first launch.
```
