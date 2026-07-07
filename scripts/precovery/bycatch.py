"""Tier-1 bycatch harvester — turn a precovery search region into a passive novelty net.

Every precovery wave already downloads single-exposure catalog detections for a
searched field/night while chasing one target. This module re-reads *all* of those
detections and asks a different question: does any OTHER same-night set of detections
form a moving-object tracklet? Matched to a known minor planet -> known-object
bycatch (logged). Unmatched -> an UNKNOWN candidate (the discovery channel; flagged
for human/referee review, NEVER auto-claimed).

Pipeline (see README.md for the wave paragraph):
  (a) form SAME-NIGHT pairs/triplets whose implied sky motion lies in a rate window
      (default 0.5-120 "/hr), with a consistent direction for triplets;
  (b) reject stationarity: implied rate below the minimum, OR either endpoint within
      ~1.5" of a supplied static-source (mean-object) catalog = not a mover;
  (c) require magnitude consistency between endpoints (default within 1.0 mag);
  (d) identify survivors against the MPC (MPChecker CGI) — a match within a tolerance
      is a known object (log its designation); no match is an UNKNOWN candidate.

Honest limits: this is a *catalog-level* net. Astrometric scatter on faint 2-point
pairs makes the implied rate noisy (a real ~3"/hr mover measured over 2 min can read
0.8"/hr), so the rate window is deliberately wide and 2-point tracklets are weak
evidence — the value is in flagging, not confirming. The static-source catalog is the
decisive false-positive filter: without it, two different stationary stars in two
exposures mimic a fast tracklet. Requires numpy; astropy (calendar dates) and requests
(MPC step) are optional and degrade gracefully offline.

Conventions: stdlib + numpy + astropy + requests, outputs to a caller-chosen path
(default /tmp). No side effects beyond the CSV it is told to write.
"""
from __future__ import annotations

import argparse
import csv
import json
import math
from dataclasses import dataclass, asdict, field
from pathlib import Path
from typing import Any, Iterable, Optional, Sequence

import numpy as np

try:                                    # calendar dates for the MPC query
    from astropy.time import Time
    _HAVE_ASTROPY = True
except Exception:                       # pragma: no cover - env-dependent
    _HAVE_ASTROPY = False

try:
    import requests
    _HAVE_REQUESTS = True
except Exception:                       # pragma: no cover - env-dependent
    _HAVE_REQUESTS = False


# --------------------------------------------------------------------------- #
# Configuration
# --------------------------------------------------------------------------- #
@dataclass
class BycatchConfig:
    """Tunable thresholds. Defaults are the campaign-vetted starting points."""
    rate_min_arcsec_hr: float = 0.5     # below this = stationary (reject)
    rate_max_arcsec_hr: float = 120.0   # above this = too fast / spurious (reject)
    same_night_max_hr: float = 8.0      # max time span for a same-night pair
    static_tol_arcsec: float = 1.5      # endpoint within this of a mean object = static
    mag_tol: float = 1.0                # |dmag| between endpoints (same filter)
    cross_filter_mag_tol: float = 2.0   # looser tol when endpoints differ in filter
    direction_tol_deg: float = 20.0     # PA consistency for a triplet
    rate_ratio_tol: float = 0.6         # |r1-r2|/mean segment-rate consistency (triplet)
    mpc_match_arcsec: float = 30.0      # tracklet<->known-object match tolerance
    mpc_search_radius_arcmin: float = 5.0
    mpc_limit_mag: float = 24.0
    default_obscode: str = "500"        # geocentric fallback when none supplied


# Column-name aliases (case-insensitive) accepted on input.
_ALIASES = {
    "mjd": ["mjd", "mjd_utc", "mjd_utc_", "epoch_mjd", "time_mjd"],
    "ra": ["ra", "ra_deg", "radeg", "ra_j2000", "alpha"],
    "dec": ["dec", "dec_deg", "decdeg", "dec_j2000", "delta", "decl"],
    "mag": ["mag", "magnitude", "v", "mag_auto", "cat_mag"],
    "filter": ["filter", "filt", "band"],
    "id": ["id", "det_id", "measid", "measurement_id", "detid"],
    "group_id": ["group_id", "objectid", "object_id", "meanobjectid"],
    "exposure": ["exposure", "expo", "frame", "frame_id", "exposure_id", "exp"],
    "obscode": ["obscode", "obs_code", "oc", "obs"],
}


def _pick(row: dict, key: str):
    low = {str(k).lower(): k for k in row}
    for alias in _ALIASES[key]:
        if alias in low:
            v = row[low[alias]]
            if v is not None and str(v).strip() != "":
                return v
    return None


# --------------------------------------------------------------------------- #
# Geometry
# --------------------------------------------------------------------------- #
def sep_arcsec(ra1: float, dec1: float, ra2: float, dec2: float) -> float:
    """Great-circle separation in arcsec (haversine; robust near the pole)."""
    r1, d1, r2, d2 = map(math.radians, (ra1, dec1, ra2, dec2))
    dr, dd = r2 - r1, d2 - d1
    a = math.sin(dd / 2) ** 2 + math.cos(d1) * math.cos(d2) * math.sin(dr / 2) ** 2
    return math.degrees(2 * math.asin(min(1.0, math.sqrt(a)))) * 3600.0


def position_angle_deg(ra1: float, dec1: float, ra2: float, dec2: float) -> float:
    """PA of point 2 as seen from point 1, degrees E of N (0=N, 90=E)."""
    cd = math.cos(math.radians(0.5 * (dec1 + dec2)))
    d_ra = (ra2 - ra1) * cd            # local tangent-plane, arcsec-proportional
    d_dec = (dec2 - dec1)
    return math.degrees(math.atan2(d_ra, d_dec)) % 360.0


def _pa_diff(pa1: float, pa2: float) -> float:
    d = abs(pa1 - pa2) % 360.0
    return min(d, 360.0 - d)


# --------------------------------------------------------------------------- #
# Detection loading
# --------------------------------------------------------------------------- #
def load_detections(source: "str | Path | Iterable[dict]") -> list[dict]:
    """Normalize a CSV path or a list of dicts into canonical detection records.

    Canonical keys: mjd, ra, dec (floats, required); mag, filter, id, group_id,
    exposure, obscode (optional). Rows missing mjd/ra/dec are skipped.
    """
    if isinstance(source, (str, Path)):
        with open(source, newline="") as fh:
            rows = list(csv.DictReader(fh))
    else:
        rows = [dict(r) for r in source]

    out: list[dict] = []
    for i, row in enumerate(rows):
        mjd, ra, dec = _pick(row, "mjd"), _pick(row, "ra"), _pick(row, "dec")
        if mjd is None or ra is None or dec is None:
            continue
        mag = _pick(row, "mag")
        det = {
            "mjd": float(mjd),
            "ra": float(ra),
            "dec": float(dec),
            "mag": float(mag) if mag is not None else None,
            "filter": (str(_pick(row, "filter")) if _pick(row, "filter") else None),
            "id": (str(_pick(row, "id")) if _pick(row, "id") else f"det{i}"),
            "group_id": (str(_pick(row, "group_id")) if _pick(row, "group_id") else None),
            "exposure": (str(_pick(row, "exposure")) if _pick(row, "exposure") else None),
            "obscode": (str(_pick(row, "obscode")) if _pick(row, "obscode") else None),
        }
        out.append(det)
    return out


def mean_object_catalog(detections: Sequence[dict], group_key: str = "group_id") -> list[dict]:
    """Collapse detections to one static source per mean-object id (survey `object` table).

    Detections that repeat under the same group id (e.g. NSC objectid) are a single
    stationary star; their mean position is a static source. Detections lacking a
    group id each become their own static source. Use the output as `static_sources`
    to reject anything sitting on a catalogued fixed star.
    """
    groups: dict[str, list[dict]] = {}
    singles: list[dict] = []
    for d in detections:
        g = d.get(group_key)
        if g:
            groups.setdefault(str(g), []).append(d)
        else:
            singles.append(d)
    table: list[dict] = []
    for g, members in groups.items():
        table.append({
            "ra": float(np.mean([m["ra"] for m in members])),
            "dec": float(np.mean([m["dec"] for m in members])),
            "id": g,
            "ndet": len(members),
        })
    for s in singles:
        table.append({"ra": s["ra"], "dec": s["dec"], "id": s["id"], "ndet": 1})
    return table


def _near_static(ra: float, dec: float, static: Sequence[dict], tol: float) -> Optional[dict]:
    best, best_sep = None, tol
    for s in static:
        sp = sep_arcsec(ra, dec, s["ra"], s["dec"])
        if sp <= best_sep:
            best, best_sep = s, sp
    return best


# --------------------------------------------------------------------------- #
# Motion / pairing
# --------------------------------------------------------------------------- #
def pair_motion(d1: dict, d2: dict) -> dict:
    """Implied motion of the earlier->later detection pair.

    Returns dt_hr, sep_arcsec, rate_arcsec_hr, pa_deg, and the pair midpoint.
    """
    if d2["mjd"] < d1["mjd"]:
        d1, d2 = d2, d1
    dt_hr = (d2["mjd"] - d1["mjd"]) * 24.0
    sep = sep_arcsec(d1["ra"], d1["dec"], d2["ra"], d2["dec"])
    pa = position_angle_deg(d1["ra"], d1["dec"], d2["ra"], d2["dec"])
    rate = sep / dt_hr if dt_hr > 0 else float("inf")
    return {
        "dt_hr": dt_hr,
        "sep_arcsec": sep,
        "rate_arcsec_hr": rate,
        "pa_deg": pa,
        "ra_mid": 0.5 * (d1["ra"] + d2["ra"]),
        "dec_mid": 0.5 * (d1["dec"] + d2["dec"]),
        "mjd_mid": 0.5 * (d1["mjd"] + d2["mjd"]),
        "_a": d1,
        "_b": d2,
    }


def _mag_consistent(d1: dict, d2: dict, cfg: BycatchConfig) -> bool:
    if d1["mag"] is None or d2["mag"] is None:
        return True                     # cannot test -> do not reject on mag
    tol = cfg.mag_tol
    if d1["filter"] and d2["filter"] and d1["filter"] != d2["filter"]:
        tol = cfg.cross_filter_mag_tol
    return abs(d1["mag"] - d2["mag"]) <= tol


def form_tracklets(
    detections: Sequence[dict],
    cfg: Optional[BycatchConfig] = None,
    static_sources: Optional[Sequence[dict]] = None,
) -> tuple[list[dict], dict]:
    """Form same-night moving-object tracklets and count rejections.

    Returns (tracklets, reject_counts). Each tracklet dict carries n_points,
    member ids/exposures, mean position, rate, pa, mag stats, and a 'kind'
    ('pair' or 'triplet'). Rejection reasons are tallied in reject_counts.
    """
    cfg = cfg or BycatchConfig()
    static_sources = list(static_sources or [])
    dets = sorted(detections, key=lambda d: d["mjd"])
    reject = {"stationary_rate": 0, "too_fast": 0, "on_static_source": 0,
              "mag_inconsistent": 0, "not_same_night": 0}

    # --- candidate same-night pairs ---
    pairs: list[dict] = []
    n = len(dets)
    for i in range(n):
        for j in range(i + 1, n):
            m = pair_motion(dets[i], dets[j])
            if m["dt_hr"] <= 0 or m["dt_hr"] > cfg.same_night_max_hr:
                reject["not_same_night"] += 1
                continue
            # stationarity by rate
            if m["rate_arcsec_hr"] < cfg.rate_min_arcsec_hr:
                reject["stationary_rate"] += 1
                continue
            if m["rate_arcsec_hr"] > cfg.rate_max_arcsec_hr:
                reject["too_fast"] += 1
                continue
            # stationarity by coincidence with a catalogued fixed star
            if static_sources and (
                _near_static(m["_a"]["ra"], m["_a"]["dec"], static_sources, cfg.static_tol_arcsec)
                or _near_static(m["_b"]["ra"], m["_b"]["dec"], static_sources, cfg.static_tol_arcsec)
            ):
                reject["on_static_source"] += 1
                continue
            if not _mag_consistent(m["_a"], m["_b"], cfg):
                reject["mag_inconsistent"] += 1
                continue
            pairs.append(m)

    # --- promote consistent pair chains to triplets ---
    used_pair_idx: set[int] = set()
    tracklets: list[dict] = []
    for a in range(len(pairs)):
        for b in range(len(pairs)):
            if a == b or a in used_pair_idx or b in used_pair_idx:
                continue
            p, q = pairs[a], pairs[b]
            if p["_b"]["id"] != q["_a"]["id"]:      # share the middle detection
                continue
            if _pa_diff(p["pa_deg"], q["pa_deg"]) > cfg.direction_tol_deg:
                continue
            mean_rate = 0.5 * (p["rate_arcsec_hr"] + q["rate_arcsec_hr"])
            if mean_rate <= 0 or abs(p["rate_arcsec_hr"] - q["rate_arcsec_hr"]) / mean_rate > cfg.rate_ratio_tol:
                continue
            used_pair_idx.update({a, b})
            tracklets.append(_tracklet_from_members(
                [p["_a"], p["_b"], q["_b"]], kind="triplet"))
            break
    for k, p in enumerate(pairs):
        if k in used_pair_idx:
            continue
        tracklets.append(_tracklet_from_members([p["_a"], p["_b"]], kind="pair"))

    # --- drop redundant sub-tracklets --------------------------------------
    # Triplet promotion consumes only the two adjacent middle-sharing pairs,
    # so a genuine 3-point mover would also surface its un-consumed
    # long-baseline endpoint pair (m0,m2), and 4+ collinear points fan out
    # further. A tracklet whose members are a subset of another's is the same
    # object seen twice: keep only the longest chain (exact duplicates keep
    # the first). Never drops a detection — only redundant groupings.
    member_sets = [set(t["member_ids"].split(",")) for t in tracklets]
    tracklets = [
        t for i, t in enumerate(tracklets)
        if not any(
            (member_sets[i] < member_sets[j])
            or (member_sets[i] == member_sets[j] and j < i)
            for j in range(len(member_sets)) if j != i
        )
    ]

    return tracklets, reject


def _tracklet_from_members(members: Sequence[dict], kind: str) -> dict:
    members = sorted(members, key=lambda d: d["mjd"])
    a, z = members[0], members[-1]
    dt_hr = (z["mjd"] - a["mjd"]) * 24.0
    sep = sep_arcsec(a["ra"], a["dec"], z["ra"], z["dec"])
    mags = [m["mag"] for m in members if m["mag"] is not None]
    return {
        "kind": kind,
        "n_points": len(members),
        "mjd_start": a["mjd"],
        "mjd_end": z["mjd"],
        "dt_hr": dt_hr,
        "ra_mean": float(np.mean([m["ra"] for m in members])),
        "dec_mean": float(np.mean([m["dec"] for m in members])),
        "rate_arcsec_hr": (sep / dt_hr) if dt_hr > 0 else float("inf"),
        "pa_deg": position_angle_deg(a["ra"], a["dec"], z["ra"], z["dec"]),
        "mag_mean": float(np.mean(mags)) if mags else None,
        "dmag": (float(max(mags) - min(mags)) if len(mags) > 1 else 0.0),
        "filters": "/".join(sorted({m["filter"] for m in members if m["filter"]})) or None,
        "member_ids": ",".join(m["id"] for m in members),
        "member_exposures": ",".join(m["exposure"] or "" for m in members),
        "obscode": next((m["obscode"] for m in members if m["obscode"]), None),
    }


# --------------------------------------------------------------------------- #
# MPC identification (MPChecker CGI)
# --------------------------------------------------------------------------- #
_MPCHECKER_URL = "https://cgi.minorplanetcenter.net/cgi-bin/mpcheck.cgi"
import re as _re
_MPC_LINE = _re.compile(
    r"^(?P<desig>.+?)\s+(?P<rah>\d{2})\s(?P<ram>\d{2})\s(?P<ras>\d{2}(?:\.\d+)?)"
    r"\s+(?P<sgn>[+-])(?P<dd>\d{2})\s(?P<dm>\d{2})\s(?P<ds>\d{2}(?:\.\d+)?)"
    r"\s+(?P<v>-?\d+\.\d+)")


def _mjd_to_ymd(mjd: float) -> tuple[int, int, float]:
    if _HAVE_ASTROPY:
        t = Time(mjd, format="mjd", scale="utc")
        y, mo, d, hh, mm, ss = t.ymdhms
        return int(y), int(mo), d + (hh + (mm + ss / 60.0) / 60.0) / 24.0
    # stdlib fallback: MJD -> proleptic Gregorian (Fliegel-Van Flandern)
    jd = mjd + 2400000.5
    z = math.floor(jd + 0.5)
    f = (jd + 0.5) - z
    a = z
    if z >= 2299161:
        alpha = math.floor((z - 1867216.25) / 36524.25)
        a = z + 1 + alpha - math.floor(alpha / 4)
    b = a + 1524
    c = math.floor((b - 122.1) / 365.25)
    dd = math.floor(365.25 * c)
    e = math.floor((b - dd) / 30.6001)
    day = b - dd - math.floor(30.6001 * e) + f
    month = e - 1 if e < 14 else e - 13
    year = c - 4716 if month > 2 else c - 4715
    return int(year), int(month), day


def query_mpchecker(
    ra_deg: float, dec_deg: float, mjd: float,
    obscode: str = "500", cfg: Optional[BycatchConfig] = None,
    session: Any = None, timeout: float = 60.0,
) -> list[dict]:
    """Return known minor planets near (ra,dec) at `mjd` per the MPC MPChecker CGI.

    Each hit: {designation, ra_deg, dec_deg, v, sep_arcsec} (sep to the query point),
    sorted nearest-first. Raises on a network/parse failure so callers can mark the
    tracklet 'unidentified_offline' rather than silently claiming novelty.
    """
    if not _HAVE_REQUESTS:
        raise RuntimeError("requests not available; cannot query MPChecker")
    cfg = cfg or BycatchConfig()
    y, mo, day = _mjd_to_ymd(mjd)
    h = ra_deg / 15.0
    hh = int(h); mm = int((h - hh) * 60); ss = ((h - hh) * 60 - mm) * 60
    sgn = "-" if dec_deg < 0 else "+"
    ad = abs(dec_deg); dd = int(ad); dm = int((ad - dd) * 60); ds = ((ad - dd) * 60 - dm) * 60
    data = {
        "year": str(y), "month": f"{mo:02d}", "day": f"{day:.2f}", "which": "pos",
        "ra": f"{hh:02d} {mm:02d} {ss:05.2f}", "decl": f"{sgn}{dd:02d} {dm:02d} {ds:04.1f}",
        "TextArea": "", "radius": f"{cfg.mpc_search_radius_arcmin:g}",
        "limit": f"{cfg.mpc_limit_mag:g}", "oc": obscode or cfg.default_obscode,
        "sort": "d", "mot": "h", "tmot": "s", "pdes": "u", "needed": "f",
        "ps": "n", "type": "p",
    }
    poster = session or requests
    resp = poster.post(_MPCHECKER_URL, data=data, timeout=timeout)
    resp.raise_for_status()
    m = _re.search(r"<pre>(.*?)</pre>", resp.text, _re.S)
    body = m.group(1) if m else resp.text
    hits: list[dict] = []
    for line in body.splitlines():
        mt = _MPC_LINE.match(line.strip())
        if not mt:
            continue
        oh = int(mt["rah"]) + int(mt["ram"]) / 60.0 + float(mt["ras"]) / 3600.0
        ora = oh * 15.0
        odec = (int(mt["dd"]) + int(mt["dm"]) / 60.0 + float(mt["ds"]) / 3600.0)
        odec = -odec if mt["sgn"] == "-" else odec
        hits.append({
            "designation": mt["desig"].strip(),
            "ra_deg": ora, "dec_deg": odec, "v": float(mt["v"]),
            "sep_arcsec": sep_arcsec(ra_deg, dec_deg, ora, odec),
        })
    hits.sort(key=lambda x: x["sep_arcsec"])
    return hits


# --------------------------------------------------------------------------- #
# Driver
# --------------------------------------------------------------------------- #
def run_bycatch(
    detections: "str | Path | Iterable[dict]",
    static_sources: "Optional[str | Path | Sequence[dict]]" = None,
    identify: bool = True,
    cfg: Optional[BycatchConfig] = None,
    out_csv: "Optional[str | Path]" = None,
    session: Any = None,
) -> dict:
    """End-to-end bycatch pass over one search region's single-exposure detections.

    Forms tracklets, (optionally) identifies each against the MPC, writes
    `out_csv`, and returns a summary dict. Classifications:
      known               - matched a known minor planet within cfg.mpc_match_arcsec
      unknown_candidate   - no known object matched (the discovery channel; REVIEW)
      unidentified_offline- identification skipped or the MPC query failed
    UNKNOWN candidates are flagged for human/referee review and never auto-claimed.
    """
    cfg = cfg or BycatchConfig()
    dets = load_detections(detections)

    static: list[dict] = []
    if isinstance(static_sources, (str, Path)):
        static = _load_static_csv(static_sources)
    elif static_sources:
        static = [dict(s) for s in static_sources]

    tracklets, reject = form_tracklets(dets, cfg, static)

    n_known = n_unknown = n_offline = 0
    for t in tracklets:
        t["classification"] = "unidentified_offline"
        t["mpc_designation"] = ""
        t["mpc_sep_arcsec"] = ""
        t["mpc_all_hits"] = ""
        if identify:
            try:
                hits = query_mpchecker(t["ra_mean"], t["dec_mean"], t["mjd_start"],
                                       obscode=t.get("obscode") or cfg.default_obscode,
                                       cfg=cfg, session=session)
                t["mpc_all_hits"] = ";".join(
                    f"{h['designation']}@{h['sep_arcsec']:.1f}\"" for h in hits[:5])
                if hits and hits[0]["sep_arcsec"] <= cfg.mpc_match_arcsec:
                    t["classification"] = "known"
                    t["mpc_designation"] = hits[0]["designation"]
                    t["mpc_sep_arcsec"] = round(hits[0]["sep_arcsec"], 2)
                else:
                    t["classification"] = "unknown_candidate"
            except Exception as exc:    # network/parse failure -> honest offline label
                t["classification"] = "unidentified_offline"
                t["mpc_all_hits"] = f"query_failed:{type(exc).__name__}"
        if t["classification"] == "known":
            n_known += 1
        elif t["classification"] == "unknown_candidate":
            n_unknown += 1
        else:
            n_offline += 1

    if out_csv:
        _write_csv(tracklets, out_csv)

    return {
        "n_detections": len(dets),
        "n_static_sources": len(static),
        "n_tracklets": len(tracklets),
        "n_known": n_known,
        "n_unknown_candidate": n_unknown,
        "n_unidentified_offline": n_offline,
        "rejections": reject,
        "config": asdict(cfg),
        "out_csv": str(out_csv) if out_csv else None,
        "tracklets": tracklets,
    }


_CSV_COLS = ["kind", "n_points", "classification", "mpc_designation", "mpc_sep_arcsec",
             "mjd_start", "mjd_end", "dt_hr", "ra_mean", "dec_mean",
             "rate_arcsec_hr", "pa_deg", "mag_mean", "dmag", "filters",
             "obscode", "member_ids", "member_exposures", "mpc_all_hits"]


def _write_csv(tracklets: Sequence[dict], out_csv: "str | Path") -> None:
    Path(out_csv).parent.mkdir(parents=True, exist_ok=True)
    with open(out_csv, "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=_CSV_COLS, extrasaction="ignore")
        w.writeheader()
        for t in tracklets:
            row = dict(t)
            for k in ("rate_arcsec_hr", "pa_deg", "dt_hr", "ra_mean", "dec_mean",
                      "mag_mean", "dmag"):
                if isinstance(row.get(k), float):
                    row[k] = round(row[k], 6)
            w.writerow(row)


def _load_static_csv(path: "str | Path") -> list[dict]:
    with open(path, newline="") as fh:
        rows = list(csv.DictReader(fh))
    out = []
    for r in rows:
        low = {str(k).lower(): v for k, v in r.items()}
        ra = low.get("ra") or low.get("ra_deg")
        dec = low.get("dec") or low.get("dec_deg") or low.get("decl")
        if ra is None or dec is None:
            continue
        out.append({"ra": float(ra), "dec": float(dec),
                    "id": low.get("id", ""), "ndet": int(low.get("ndet", 1) or 1)})
    return out


def main(argv: Optional[Sequence[str]] = None) -> int:
    ap = argparse.ArgumentParser(description="Tier-1 bycatch harvester")
    ap.add_argument("detections", help="CSV of single-exposure detections")
    ap.add_argument("--static", help="CSV of static/mean-object sources (ra,dec)")
    ap.add_argument("--out", default="/tmp/novelty_gate/bycatch/bycatch_tracklets.csv")
    ap.add_argument("--no-identify", action="store_true",
                    help="skip the MPC identification step (offline)")
    ap.add_argument("--rate-min", type=float, default=None)
    ap.add_argument("--rate-max", type=float, default=None)
    args = ap.parse_args(argv)
    cfg = BycatchConfig()
    if args.rate_min is not None:
        cfg.rate_min_arcsec_hr = args.rate_min
    if args.rate_max is not None:
        cfg.rate_max_arcsec_hr = args.rate_max
    summary = run_bycatch(args.detections, static_sources=args.static,
                          identify=not args.no_identify, cfg=cfg, out_csv=args.out)
    summary.pop("tracklets", None)
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
