"""Pure-python data layer for the hunt console.

This module contains NO streamlit imports — it is the unit-testable core that
reads the hunt-output contract off disk and hands plain python / pandas objects
back to the thin Streamlit layer (``hunt_console.py``).  Keeping it streamlit-free
means it can be exercised from a plain ``python`` REPL or a pytest run.

The hunt-output contract (see README.md for the full spec)::

    <runs_dir>/<hunt_id>/
        manifest.json   # static run metadata
        progress.json   # live heartbeat, overwritten each batch
        candidates.csv  # ranked; cols: id, ra, dec, score, verdict, + extras
        triage.json     # human triage keyed by id  (written by THIS module)
        targets/<id>/
            findings.json
            *.png

Design rules honoured throughout:

* **Defensive reads.**  The dashboard polls files that a *running* hunt is
  actively rewriting, so every reader tolerates a missing file, an empty file,
  a half-written file (truncated JSON), and a CSV that is missing the
  "required" columns.  A bad read degrades to an empty/placeholder result, it
  never raises up to the UI.
* **IDs are strings.**  Source ids look numeric for some lanes
  (``3142p439_b0-000375``) but must never be coerced to int/float — pandas would
  silently turn a 19-digit Gaia id into a lossy float.  ``read_candidates`` forces
  the ``id`` column to ``str`` and ``read_findings`` / triage all key on ``str``.
* **Triage is sidecar.**  Human verdicts are written to ``triage.json`` keyed by
  id; ``candidates.csv`` (the hunt's own output) is NEVER mutated.
"""
from __future__ import annotations

import json
import os
import tempfile
import time
from pathlib import Path
from typing import Any

import pandas as pd

# ---------------------------------------------------------------------------
# Runs directory resolution
# ---------------------------------------------------------------------------
# Configurable via the HUNT_RUNS_DIR env var so a deployment can point the app
# at a real shared scratch area; defaults to /tmp/hunt_runs for the demo.
DEFAULT_RUNS_DIR = "/tmp/hunt_runs"

# The required candidate columns per the contract.  read_candidates guarantees
# these exist (filling with NaN / "") so downstream UI code can rely on them.
REQUIRED_CANDIDATE_COLS = ["id", "ra", "dec", "score", "verdict"]

# Allowed human-triage verdicts.  write_triage validates against this set.
TRIAGE_VERDICTS = ("promote", "flag", "reject", "clear")

# Heartbeat-age thresholds for a 'running' hunt (seconds). A hunt that is mid
# long blocking query (a NEOWISE single-exposure batch is ~110s; a slow Gaia TAP
# call while the archive is "in evolution" can block for minutes) legitimately
# goes quiet between flushes, so we GRADE staleness instead of crying "dead" at
# the first 60s gap:
#   age <= QUIET_HEARTBEAT_S  -> live   (fresh)
#   QUIET < age <= STALE      -> quiet  (almost always mid-query, still alive)
#   age >  STALE_HEARTBEAT_S  -> stale  (silent long enough to suspect a dead worker)
QUIET_HEARTBEAT_S = 180
STALE_HEARTBEAT_S = 600


def runs_dir() -> Path:
    """Return the configured runs directory as a Path (not required to exist)."""
    return Path(os.environ.get("HUNT_RUNS_DIR", DEFAULT_RUNS_DIR))


# ---------------------------------------------------------------------------
# Low-level helpers
# ---------------------------------------------------------------------------

def _read_json(path: Path) -> dict | None:
    """Read a JSON file, tolerating absence / empty / mid-write truncation.

    Returns the parsed dict, or ``None`` if the file does not exist, is empty,
    or fails to parse (e.g. caught mid-write by a live hunt).  Never raises.
    """
    try:
        if not path.exists():
            return None
        raw = path.read_text()
    except OSError:
        return None
    if not raw.strip():
        return None
    try:
        obj = json.loads(raw)
    except (json.JSONDecodeError, ValueError):
        # Half-written file — the live hunt is mid-flush.  Treat as "no data
        # yet" rather than crashing the dashboard.
        return None
    return obj if isinstance(obj, dict) else None


def _atomic_write_json(path: Path, obj: dict) -> None:
    """Write JSON atomically (temp file + os.replace) so a concurrent reader
    never sees a half-written file."""
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=str(path.parent), prefix=".tmp_", suffix=".json")
    try:
        with os.fdopen(fd, "w") as fh:
            json.dump(obj, fh, indent=2, default=str)
        os.replace(tmp, path)  # atomic on POSIX
    finally:
        if os.path.exists(tmp):
            try:
                os.remove(tmp)
            except OSError:
                pass


# ---------------------------------------------------------------------------
# Run discovery + metadata
# ---------------------------------------------------------------------------

def list_runs(base: str | os.PathLike | None = None) -> list[str]:
    """List hunt_ids present under the runs directory.

    A directory counts as a run if it contains *either* a manifest.json or a
    candidates.csv (so a freshly-started hunt with only a manifest still shows,
    and an older run missing its manifest is still browsable).  Sorted with the
    most-recently-modified first so the newest hunt floats to the top of the
    dashboard.  Returns ``[]`` if the runs dir does not exist.
    """
    root = Path(base) if base is not None else runs_dir()
    if not root.exists():
        return []
    entries: list[tuple[float, str]] = []
    for child in root.iterdir():
        if not child.is_dir():
            continue
        if (child / "manifest.json").exists() or (child / "candidates.csv").exists():
            try:
                mtime = child.stat().st_mtime
            except OSError:
                mtime = 0.0
            entries.append((mtime, child.name))
    entries.sort(key=lambda t: t[0], reverse=True)
    return [name for _, name in entries]


def _run_path(hunt_id: str, base: str | os.PathLike | None = None) -> Path:
    root = Path(base) if base is not None else runs_dir()
    return root / hunt_id


def read_manifest(hunt_id: str, base: str | os.PathLike | None = None) -> dict:
    """Read a run's manifest.json, with safe defaults for every documented key.

    Always returns a dict (never None) so the UI can render a card even for a
    run whose manifest is missing or mid-write.
    """
    data = _read_json(_run_path(hunt_id, base) / "manifest.json") or {}
    # Fill documented keys with neutral defaults.
    out = {
        "hunt_id": hunt_id,
        "lane": data.get("lane", "unknown"),
        "title": data.get("title", hunt_id),
        "status": data.get("status", "unknown"),
        "started_at": data.get("started_at"),
        "ended_at": data.get("ended_at"),
        "params": data.get("params", {}),
        "total_planned": data.get("total_planned"),
    }
    # Preserve any extra keys the lane chose to write.
    for k, v in data.items():
        if k not in out:
            out[k] = v
    return out


def read_progress(hunt_id: str, base: str | os.PathLike | None = None) -> dict | None:
    """Read a run's live progress.json heartbeat.

    Returns ``None`` when there is no (readable) progress file yet — the UI
    interprets that as "no heartbeat", distinct from a stale heartbeat.
    """
    return _read_json(_run_path(hunt_id, base) / "progress.json")


def heartbeat_age_s(progress: dict | None, now: float | None = None) -> float | None:
    """Seconds since the progress heartbeat's ``ts`` (epoch seconds).

    Returns ``None`` if there is no progress or no parseable ``ts``.  Used by
    the dashboard to flag a 'running' hunt whose heartbeat has gone stale.
    """
    if not progress:
        return None
    ts = progress.get("ts")
    try:
        ts = float(ts)
    except (TypeError, ValueError):
        return None
    return (time.time() if now is None else now) - ts


def is_stale(manifest: dict, progress: dict | None, now: float | None = None,
             threshold_s: float = STALE_HEARTBEAT_S) -> bool:
    """True iff the run claims status 'running' but its heartbeat is older than
    ``threshold_s`` (or has no heartbeat at all).  A done/failed run is never
    'stale'."""
    if (manifest or {}).get("status") != "running":
        return False
    age = heartbeat_age_s(progress, now=now)
    if age is None:
        return True  # running but never wrote a heartbeat — suspicious
    return age > threshold_s


def run_health(manifest: dict, progress: dict | None, now: float | None = None) -> str:
    """Coarse health state driving the dashboard badge. One of:

    * ``done`` / ``failed`` — taken straight from the manifest status.
    * ``starting`` — running but no heartbeat yet (just launched; benign).
    * ``live``  — running, heartbeat fresh (age <= QUIET_HEARTBEAT_S).
    * ``quiet`` — running, QUIET < age <= STALE_HEARTBEAT_S; almost always a long
      blocking query (NEOWISE/Gaia), NOT a dead worker — shown amber, not red.
    * ``stale`` — running, heartbeat older than STALE_HEARTBEAT_S; suspect dead.
    * ``unknown`` — any other status.

    Intentionally more lenient than :func:`is_stale` on the never-flushed case
    (``starting`` vs stale) so a freshly-launched run does not flash a "worker
    may have died" alarm before it has written its first heartbeat.
    """
    status = (manifest or {}).get("status")
    if status in ("done", "failed"):
        return status
    if status != "running":
        return "unknown"
    age = heartbeat_age_s(progress, now=now)
    if age is None:
        return "starting"
    if age <= QUIET_HEARTBEAT_S:
        return "live"
    if age <= STALE_HEARTBEAT_S:
        return "quiet"
    return "stale"


# ---------------------------------------------------------------------------
# Candidates
# ---------------------------------------------------------------------------

def read_candidates(hunt_id: str, base: str | os.PathLike | None = None) -> pd.DataFrame:
    """Read a run's candidates.csv into a DataFrame.

    Guarantees:

    * Returns an empty DataFrame (with the required columns) if the file is
      missing or unreadable / caught mid-write — never raises.
    * The ``id`` column is forced to ``str`` (Gaia-style ids must not become
      lossy floats).
    * The required contract columns (id/ra/dec/score/verdict) always exist;
      any the hunt omitted are added as NaN (numeric) or "" (verdict).
    * Lane-specific extra columns are preserved as-is.
    """
    path = _run_path(hunt_id, base) / "candidates.csv"
    empty = pd.DataFrame(columns=REQUIRED_CANDIDATE_COLS)
    if not path.exists():
        return empty
    try:
        # dtype on id keeps long/alphanumeric ids exact; everything else
        # inferred. keep_default_na so empty verdict cells read as NaN -> "".
        df = pd.read_csv(path, dtype={"id": str})
    except (pd.errors.EmptyDataError, pd.errors.ParserError, OSError):
        # Empty or half-written CSV (a live hunt may be rewriting it).
        return empty
    if df.empty:
        return empty
    # Force id to string even if the CSV had no header-declared dtype path.
    if "id" in df.columns:
        df["id"] = df["id"].astype(str)
    else:
        df["id"] = ""
    # Ensure required columns exist.
    for col in ("ra", "dec", "score"):
        if col not in df.columns:
            df[col] = pd.NA
        else:
            df[col] = pd.to_numeric(df[col], errors="coerce")
    if "verdict" not in df.columns:
        df["verdict"] = ""
    else:
        df["verdict"] = df["verdict"].fillna("").astype(str)
    return df


def candidate_row(hunt_id: str, target_id: str,
                  base: str | os.PathLike | None = None) -> dict | None:
    """Return the candidates.csv row for ``target_id`` as a dict, or None."""
    df = read_candidates(hunt_id, base)
    if df.empty or "id" not in df.columns:
        return None
    hit = df[df["id"] == str(target_id)]
    if hit.empty:
        return None
    return hit.iloc[0].to_dict()


# ---------------------------------------------------------------------------
# Per-target findings + plots
# ---------------------------------------------------------------------------

def target_dir(hunt_id: str, target_id: str,
               base: str | os.PathLike | None = None) -> Path:
    return _run_path(hunt_id, base) / "targets" / str(target_id)


def read_findings(hunt_id: str, target_id: str,
                  base: str | os.PathLike | None = None) -> dict | None:
    """Read targets/<id>/findings.json.  Returns None if absent / unreadable."""
    return _read_json(target_dir(hunt_id, target_id, base) / "findings.json")


def list_target_plots(hunt_id: str, target_id: str,
                      base: str | os.PathLike | None = None) -> list[str]:
    """Sorted absolute paths of every PNG in targets/<id>/.  [] if none."""
    d = target_dir(hunt_id, target_id, base)
    if not d.exists():
        return []
    return sorted(str(p) for p in d.glob("*.png"))


def list_targets_with_findings(hunt_id: str,
                               base: str | os.PathLike | None = None) -> list[str]:
    """Ids that have a targets/<id>/ directory (findings and/or plots)."""
    troot = _run_path(hunt_id, base) / "targets"
    if not troot.exists():
        return []
    return sorted(p.name for p in troot.iterdir() if p.is_dir())


# ---------------------------------------------------------------------------
# Triage  (sidecar — never touches candidates.csv)
# ---------------------------------------------------------------------------

def _triage_path(hunt_id: str, base: str | os.PathLike | None = None) -> Path:
    return _run_path(hunt_id, base) / "triage.json"


def read_triage(hunt_id: str, base: str | os.PathLike | None = None) -> dict:
    """Read the whole triage map ``{id: {verdict, ts, note}}`` for a run.

    Returns ``{}`` if there is no triage file yet.  Always keyed by str id.
    """
    raw = _read_json(_triage_path(hunt_id, base)) or {}
    # Normalise legacy / hand-written shapes: a bare string verdict -> dict.
    out: dict[str, dict] = {}
    for k, v in raw.items():
        key = str(k)
        if isinstance(v, dict):
            out[key] = v
        else:
            out[key] = {"verdict": str(v)}
    return out


def get_triage_verdict(hunt_id: str, target_id: str,
                       base: str | os.PathLike | None = None) -> str | None:
    """Convenience: the current human verdict for one id, or None if untriaged."""
    entry = read_triage(hunt_id, base).get(str(target_id))
    if not entry:
        return None
    v = entry.get("verdict")
    return v if v else None


def write_triage(hunt_id: str, target_id: str, verdict: str,
                 note: str = "", base: str | os.PathLike | None = None) -> dict:
    """Set the human triage verdict for one id and persist to triage.json.

    * ``verdict`` must be one of TRIAGE_VERDICTS; "clear" removes the entry.
    * Read-modify-write of the sidecar map, written atomically.  Never touches
      candidates.csv.
    * Returns the updated full triage map.
    """
    verdict = (verdict or "").strip().lower()
    if verdict not in TRIAGE_VERDICTS:
        raise ValueError(f"verdict must be one of {TRIAGE_VERDICTS}, got {verdict!r}")
    target_id = str(target_id)
    current = read_triage(hunt_id, base)
    if verdict == "clear":
        current.pop(target_id, None)
    else:
        current[target_id] = {
            "verdict": verdict,
            "ts": time.time(),
            "note": note,
        }
    _atomic_write_json(_triage_path(hunt_id, base), current)
    return current


def triage_counts(hunt_id: str, base: str | os.PathLike | None = None) -> dict[str, int]:
    """Tally of human verdicts for a run, e.g. {'promote': 2, 'reject': 5}."""
    counts: dict[str, int] = {}
    for entry in read_triage(hunt_id, base).values():
        v = entry.get("verdict")
        if v:
            counts[v] = counts.get(v, 0) + 1
    return counts


# ---------------------------------------------------------------------------
# Cross-hunt source search
# ---------------------------------------------------------------------------

def cross_hunt_search(source_id: str,
                      base: str | os.PathLike | None = None) -> list[tuple[str, dict]]:
    """Find a source id across every hunt's candidates.

    Returns a list of ``(hunt_id, row_dict)`` for each run whose candidates.csv
    contains ``source_id`` (exact string match on the ``id`` column).  Each row
    dict is enriched with two convenience keys the UI surfaces directly:

    * ``_hunt`` — the hunt_id it was found in
    * ``_triage`` — the current human verdict in that hunt (or None)

    Returns ``[]`` if the id appears nowhere.  Tolerates unreadable runs.
    """
    source_id = str(source_id).strip()
    if not source_id:
        return []
    hits: list[tuple[str, dict]] = []
    for hid in list_runs(base):
        try:
            df = read_candidates(hid, base)
        except Exception:
            continue
        if df.empty or "id" not in df.columns:
            continue
        match = df[df["id"] == source_id]
        if match.empty:
            continue
        row = match.iloc[0].to_dict()
        row["_hunt"] = hid
        row["_triage"] = get_triage_verdict(hid, source_id, base)
        hits.append((hid, row))
    return hits
