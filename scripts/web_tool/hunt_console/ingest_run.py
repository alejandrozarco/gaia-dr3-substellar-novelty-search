"""ingest_run.py — convert a raw /tmp hunt into the hunt-output contract.

This is a *demo / adapter* script.  A real hunt would write the contract
directly (see "How a hunt should write the contract" in README.md); this script
retro-fits an existing run that pre-dates the contract so the console has real
content to show on first launch.

It does two things:

  1. ``ingest_ir_nova()`` — converts hunt **B** (the IR-obscured nova lane,
     just completed) from its raw /tmp CSVs + PNG into
     ``<runs>/ir_nova_2026_06_01/``.

  2. ``make_synthetic_running()`` — fabricates one tiny synthetic *running* demo
     run with a fresh heartbeat so the Live dashboard's in-progress state (and
     STALE detection) is demonstrable on first launch.

Run directly to do both::

    python ingest_run.py

Honours HUNT_RUNS_DIR (default /tmp/hunt_runs), same as the app.
"""
from __future__ import annotations

import json
import math
import os
import shutil
import time
from pathlib import Path

import pandas as pd

RUNS_DIR = Path(os.environ.get("HUNT_RUNS_DIR", "/tmp/hunt_runs"))

# ---- raw hunt-B inputs (pre-contract) -------------------------------------
SRC = Path("/tmp")
B_CANDIDATES = SRC / "ir_nova_candidates_2026_06_01.csv"   # 97 rows, Stage-1/2 verdicts
B_RUN        = SRC / "ir_nova_run_2026_06_01.csv"          # 97 rows, Stage-2 metrics
B_VETTED     = SRC / "ir_nova_vetted_2026_06_01.csv"       # 25 rows, gauntlet verdicts
# The plot script names files /tmp/ir_nova_cand_<id with . -> p>.png; we glob.
B_PLOT_GLOB  = "ir_nova_cand_*.png"

B_HUNT_ID = "ir_nova_2026_06_01"


# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------

def _clean(v):
    """JSON-safe scalar: NaN/NA -> None, numpy -> python."""
    if v is None:
        return None
    try:
        if isinstance(v, float) and math.isnan(v):
            return None
    except (TypeError, ValueError):
        pass
    if pd.isna(v) if not isinstance(v, (list, dict)) else False:
        return None
    # numpy scalar -> python
    item = getattr(v, "item", None)
    if callable(item):
        try:
            return v.item()
        except Exception:
            return v
    return v


def _png_id_from_filename(path: Path) -> str:
    """Recover the source id from a plot filename.

    The plotter writes ``ir_nova_cand_<sid-with-dots-as-p>.png``; the dots in the
    id (``3152p454_b0-000375`` came from ``3152.454`` style tiles) are already
    encoded as ``p`` in BOTH the filename and the candidate id, so the stem maps
    1:1 onto the candidate id with the prefix stripped.
    """
    stem = path.stem  # ir_nova_cand_3152p454_b0-000375
    return stem.replace("ir_nova_cand_", "", 1)


def _score_from_metrics(run_row: dict | None) -> float | None:
    """Synthesize a 0..1-ish 'interestingness' score from the Stage-2 metrics.

    There is no native score column in hunt B.  A genuine IR riser would have a
    large, significant, monotonic brightening, so we combine the W1/W2 rise
    significance and amplitude into a single rank-able score:

        score = clip( max(W1,W2 brightening evidence) , 0, 1 )

    where per-band evidence = (nsig/10) * (|dmag|/1.0) gated to only count
    *brightening* (negative slope) bands.  Non-risers score near 0; this matches
    the run's headline finding (zero clean risers) while still giving the
    dashboard a meaningful sort.
    """
    if not run_row:
        return None
    best = 0.0
    for band in ("w1", "w2"):
        slope = run_row.get(f"{band}_slope")
        nsig = run_row.get(f"{band}_nsig")
        dmag = run_row.get(f"{band}_dmag")
        try:
            slope = float(slope); nsig = float(nsig); dmag = float(dmag)
        except (TypeError, ValueError):
            continue
        if math.isnan(slope) or math.isnan(nsig) or math.isnan(dmag):
            continue
        # brightening = negative slope (mag decreasing)
        if slope >= 0:
            continue
        ev = (nsig / 10.0) * (abs(dmag) / 1.0)
        best = max(best, ev)
    return round(min(best, 1.0), 4)


def _verdict_rank(verdict: str) -> int:
    """Secondary sort key so the rare/interesting verdicts float up even when
    scores tie at ~0 (the null-result case)."""
    v = (verdict or "").upper()
    if "PLATE_BLANK_NO_CATALOG" in v:
        return 100              # the prize: real blank, no catalog id
    if v.startswith("SIMBAD:Y*"):
        return 60               # vetted to a YSO — explained, but a real survivor
    if v.startswith("SIMBAD:"):
        return 50
    if "FLAGGED" in v:
        return 20
    if "NOT_TESTABLE" in v:
        return 10
    return 0


# ---------------------------------------------------------------------------
# hunt B ingest
# ---------------------------------------------------------------------------

def ingest_ir_nova(runs_dir: Path = RUNS_DIR) -> Path:
    out = runs_dir / B_HUNT_ID
    (out / "targets").mkdir(parents=True, exist_ok=True)

    # --- read the three raw frames (ids as strings throughout) -------------
    cand = pd.read_csv(B_CANDIDATES, dtype={"id": str})
    run = pd.read_csv(B_RUN, dtype={"source_id": str})
    vetted = pd.read_csv(B_VETTED, dtype={"source_id": str})

    # Stage-2 metrics keyed by id (dedupe defensively — the raw vetted file has
    # a couple of duplicate / malformed ids; first occurrence wins).
    run = run.drop_duplicates(subset="source_id", keep="first")
    run_by_id = {str(r["source_id"]): {k: _clean(v) for k, v in r.items()}
                 for _, r in run.iterrows()}

    # Gauntlet (vetted) verdicts take precedence over the Stage-1/2 verdict for
    # the 25 survivors that went through the full cross-match gauntlet.
    vetted = vetted.drop_duplicates(subset="source_id", keep="first")
    vetted_verdict = {str(r["source_id"]): str(r["verdict"]) for _, r in vetted.iterrows()
                      if isinstance(r.get("verdict"), str) and r.get("verdict")}
    vetted_by_id = {str(r["source_id"]): {k: _clean(v) for k, v in r.items()}
                    for _, r in vetted.iterrows()}

    # --- build the contract candidates.csv ---------------------------------
    rows = []
    for _, c in cand.iterrows():
        sid = str(c["id"])
        # verdict: prefer the gauntlet verdict, else the candidate-file verdict
        verdict = vetted_verdict.get(sid, str(c.get("verdict", "")))
        score = _score_from_metrics(run_by_id.get(sid))
        row = {
            "id": sid,
            "ra": _clean(c.get("ra")),
            "dec": _clean(c.get("dec")),
            "score": score if score is not None else 0.0,
            "verdict": verdict,
            "vetted": sid in vetted_verdict,
            # keep lane-specific extras from the candidate file
            "W1_rise_dmag": _clean(c.get("W1_rise_dmag")),
            "W2_rise_dmag": _clean(c.get("W2_rise_dmag")),
            "W1_brighten": _clean(c.get("W1_brighten")),
            "W2_brighten": _clean(c.get("W2_brighten")),
            "opt_blank_gaia_ps1": _clean(c.get("opt_blank_gaia_ps1")),
            "fp_flags": _clean(c.get("fp_flags")),
            "nearest_catalog_match": _clean(c.get("nearest_catalog_match")),
        }
        # enrich with a couple of Stage-2 metrics for the table
        m = run_by_id.get(sid, {})
        row["w1mw2"] = m.get("w1mw2")
        row["w2mpro"] = m.get("w2mpro")
        rows.append(row)

    cdf = pd.DataFrame(rows)
    # Rank: score desc, then verdict-rank desc (so PLATE_BLANK floats up even at
    # score ~0), then brightness (w2mpro asc).
    cdf["_vrank"] = cdf["verdict"].map(_verdict_rank)
    cdf = cdf.sort_values(
        by=["score", "_vrank", "w2mpro"],
        ascending=[False, False, True],
        na_position="last",
    ).drop(columns="_vrank").reset_index(drop=True)
    cdf.to_csv(out / "candidates.csv", index=False)
    n_total = len(cdf)

    # --- manifest (status=done) --------------------------------------------
    manifest = {
        "hunt_id": B_HUNT_ID,
        "lane": "ir_nova",
        "title": "IR-obscured eruption / nova lane — North-America / Pelican window",
        "status": "done",
        "started_at": "2026-06-01T00:05:00Z",
        "ended_at": "2026-06-01T01:07:00Z",
        "total_planned": n_total,
        "params": {
            "box_ra_deg": [313.0, 317.0],
            "box_dec_deg": [43.5, 46.0],
            "area_deg2": 7.10,
            "seed_catalog": "CatWISE2020",
            "cuts": "W1-W2>1, W2<11, no Gaia DR3 / PS1 within 3 arcsec",
            "neowise_epochs": "2014.85-2024.37",
        },
        "headline": ("NULL (clean): of 97 optically-blank red bright WISE sources, "
                     "ZERO show a clean monotonic NEOWISE IR rise. Method validated "
                     "end-to-end; one true PLATE_BLANK_NO_CATALOG survivor remains."),
    }
    (out / "manifest.json").write_text(json.dumps(manifest, indent=2))

    # --- progress (synthesized; processed=total since the run is done) -----
    n_vetted = int(cdf["vetted"].sum())    # sources that ran the full gauntlet
    progress = {
        "ts": time.time(),                 # 'done' runs aren't checked for staleness
        "processed": 97,
        "total": 97,
        # 'survivors' = GENUINE eruption candidates (clean monotonic IR-risers) = 0
        # for this clean null. n_vetted is a funnel count (sources that ran the full
        # gauntlet), NOT a discovery count — surfacing it as 'survivors' overstated
        # the result on the dashboard.
        "survivors": 0,
        "stage": "complete",
        "last_id": cdf["id"].iloc[0] if len(cdf) else None,
        "message": (f"gauntlet complete: {n_vetted} sources fully vetted, "
                    "0 clean IR-risers (no eruption); 1 plate-blank-no-catalog "
                    "oddity retained for inspection."),
    }
    (out / "progress.json").write_text(json.dumps(progress, indent=2))

    # --- per-target dirs for every plotted candidate -----------------------
    plots = sorted(SRC.glob(B_PLOT_GLOB))
    plotted_ids = []
    for png in plots:
        sid = _png_id_from_filename(png)
        plotted_ids.append(sid)
        tdir = out / "targets" / sid
        tdir.mkdir(parents=True, exist_ok=True)
        shutil.copy2(png, tdir / png.name)

        # synthesize findings.json from the merged metric / gauntlet rows
        crow = cdf[cdf["id"] == sid]
        crow = crow.iloc[0].to_dict() if len(crow) else {}
        met = run_by_id.get(sid, {})
        vet = vetted_by_id.get(sid, {})
        verdict = crow.get("verdict", "")
        flags = []
        fp = met.get("fp_flags") or crow.get("fp_flags")
        if isinstance(fp, str) and fp:
            flags.extend(fp.split(";"))
        if vet.get("plate_blank"):
            flags.append("PLATE_BLANK")
        if not vet.get("allwise2010_present", True):
            flags.append("ALLWISE2010_ABSENT")

        classification = (
            "real optical blank, no catalog counterpart — KEEP for follow-up"
            if "PLATE_BLANK_NO_CATALOG" in verdict.upper()
            else f"explained by cross-match: {verdict}"
        )

        findings = {
            "id": sid,
            "lane": "ir_nova",
            "classification": classification,
            "key_values": {
                "ra": crow.get("ra"),
                "dec": crow.get("dec"),
                "W2_mag": met.get("w2mpro") or vet.get("w2mpro"),
                "W1_minus_W2": met.get("w1mw2") or vet.get("w1mw2"),
                "W1_slope_mag_per_yr": met.get("w1_slope"),
                "W2_slope_mag_per_yr": met.get("w2_slope"),
                "W1_rise_significance_sigma": met.get("w1_nsig"),
                "W2_rise_significance_sigma": met.get("w2_nsig"),
                "neowise_n_epochs": met.get("nw_nepoch"),
                "dasch_plates": vet.get("dasch_nplates"),
                "dasch_baseline_yr": (f"{vet.get('dasch_yr0')}-{vet.get('dasch_yr1')}"
                                       if vet.get("dasch_yr0") else None),
                "poss1_snr": vet.get("poss1_snr"),
                "poss2_snr": vet.get("poss2_snr"),
                "simbad_id": vet.get("simbad_id"),
                "simbad_otype": vet.get("simbad_otype"),
                "score": crow.get("score"),
            },
            "flags": flags,
            "notes": (
                "NEOWISE W1/W2 visit light curve (left) + DSS POSS-I/II optical "
                "cutouts (right). Optical blank on plates spanning the DASCH "
                "baseline confirms a genuine dust-obscured source rather than a "
                "magnitude-limit artifact. " +
                ("This survivor has NO catalog counterpart within the gauntlet "
                 "radii — the single retained candidate of the run."
                 if "PLATE_BLANK_NO_CATALOG" in verdict.upper()
                 else "Cross-match resolves it to a known object (see simbad_id).")
            ),
        }
        with open(tdir / "findings.json", "w") as fh:
            json.dump(findings, fh, indent=2, default=str)

    print(f"[hunt B] ingested {B_HUNT_ID}: {n_total} candidates, "
          f"{progress['survivors']} survivors, {len(plotted_ids)} plotted target(s): {plotted_ids}")
    return out


# ---------------------------------------------------------------------------
# synthetic 'running' demo run (so the Live dashboard has an in-progress card)
# ---------------------------------------------------------------------------

def make_synthetic_running(runs_dir: Path = RUNS_DIR) -> Path:
    hid = "demo_live_running"
    out = runs_dir / hid
    (out / "targets").mkdir(parents=True, exist_ok=True)

    total = 5000
    processed = 1840
    manifest = {
        "hunt_id": hid,
        "lane": "demo",
        "title": "DEMO — synthetic in-progress hunt (live heartbeat)",
        "status": "running",
        "started_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(time.time() - 600)),
        "ended_at": None,
        "total_planned": total,
        "params": {"note": "fabricated by ingest_run.make_synthetic_running for the Live demo"},
    }
    (out / "manifest.json").write_text(json.dumps(manifest, indent=2))

    # Fresh heartbeat (ts = now) so it shows as a healthy live run, not stale.
    progress = {
        "ts": time.time(),
        "processed": processed,
        "total": total,
        "survivors": 12,
        "stage": "stage2_neowise_lightcurves",
        "last_id": "demo_b0-001840",
        "message": f"processing visit light curves ({processed}/{total})",
    }
    (out / "progress.json").write_text(json.dumps(progress, indent=2))

    # A few partial candidates so the Target Browser isn't empty for the live run.
    part = pd.DataFrame([
        {"id": "demo_b0-000042", "ra": 314.10, "dec": 44.20, "score": 0.71,
         "verdict": "RISING_CANDIDATE", "w1mw2": 1.9},
        {"id": "demo_b0-000311", "ra": 315.55, "dec": 45.01, "score": 0.44,
         "verdict": "RISING_CANDIDATE", "w1mw2": 1.4},
        {"id": "demo_b0-001102", "ra": 313.80, "dec": 43.70, "score": 0.12,
         "verdict": "NOT_RISING_CLEAN", "w1mw2": 1.1},
    ])
    part.to_csv(out / "candidates.csv", index=False)

    print(f"[demo] wrote synthetic running run {hid}: {processed}/{total} processed, "
          f"fresh heartbeat (ts=now)")
    return out


def main() -> None:
    RUNS_DIR.mkdir(parents=True, exist_ok=True)
    ingest_ir_nova()
    make_synthetic_running()
    print(f"\nruns dir: {RUNS_DIR}")
    for child in sorted(RUNS_DIR.iterdir()):
        if child.is_dir():
            print("  -", child.name)


if __name__ == "__main__":
    main()
