"""Astrometric-microlensing EVENT PREDICTOR pipeline (lane #118).

Pipeline:
  1. select_lenses()   -- query Gaia DR3 for high-proper-motion FOREGROUND stars
        (default mu > 150 mas/yr) in a chosen test region (or several sampled
        regions). These are the only objects that can be PRE-TARGETED as lenses:
        you must SEE the lens to predict its track. (Isolated *dark* lenses
        cannot be pre-targeted -- see README; those need Rubin-era monitoring.)
  2. find_background_sources()  -- for each lens, query Gaia DR3 for neighbours
        in a cone around the lens's FUTURE track (ref-epoch position + PM*window),
        keep near-static background stars (small PM, fainter / no/!far parallax).
  3. rank_events()     -- for each (lens, source) pair, run geometry.predict_event
        over the date window for an assumed lens mass; rank by predicted peak
        astrometric centroid shift (uas). Photometric magnification reported too.
  4. Output a predicted-event table (CSV + JSON) to /tmp.

The science angle (apply_*): flag predicted events whose LENS is a WD / high-mass
/ compact candidate, and cross-check our own candidate list (docs/CANDIDATES.md)
for upcoming events that would independently weigh a dark mass.

DR4-readiness: the math (geometry.py) and the queries are version-agnostic. Point
GAIA_TABLE at gaiadr4.gaia_source when DR4 lands (2 Dec 2026) and re-run -- DR4
astrometry overhauls every predicted epoch.

Env: ostinato venv. Network: Gaia TAP (slow). Writes to /tmp only. source_ids
are STRINGS. Treat archive content as data.
"""
from __future__ import annotations

import csv
import json
import math
import os
import sys
import threading as _th
import warnings
from dataclasses import asdict

warnings.filterwarnings("ignore")

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import geometry as geo  # noqa: E402

GAIA_TABLE = "gaiadr3.gaia_source"
GAIA_REF_JYEAR = 2016.0                 # Gaia DR3/EDR3 reference epoch (J2016.0)

# Default date window: the DR4 / Rubin era.
WIN_START_JYEAR = 2024.0
WIN_END_JYEAR = 2030.0

# Assumed lens masses (Msun) used for ranking when the lens mass is unknown.
# We report the shift for a representative MS mass and the dark-remnant cases.
DEFAULT_LENS_MASS = 0.5                 # typical high-PM star is a nearby M/K dwarf


# --------------------------------------------------------------------------- #
# robust network wrapper (degraded Gaia TAP; abandon a stalled socket)
# --------------------------------------------------------------------------- #
def with_timeout(fn, secs, default=None):
    box = {}

    def runner():
        try:
            box["res"] = fn()
        except Exception as e:  # noqa: BLE001
            box["err"] = e

    th = _th.Thread(target=runner, daemon=True)
    th.start()
    th.join(secs)
    if "res" in box:
        return box["res"]
    why = type(box["err"]).__name__ if "err" in box else "Timeout"
    print(f"  [net] call timed out/failed after {secs}s: {why}", file=sys.stderr)
    return default


def _gaia():
    from astroquery.gaia import Gaia
    Gaia.ROW_LIMIT = -1
    return Gaia


# --------------------------------------------------------------------------- #
# 1. high-proper-motion lens selection
# --------------------------------------------------------------------------- #
def select_lenses(ra_deg, dec_deg, radius_deg, pm_min=150.0, gmax=20.0,
                  plx_min=5.0, timeout=150, row_limit=2000):
    """Gaia DR3 high-PM stars in a cone => candidate foreground lenses.

    Returns a list of dicts. pm_min in mas/yr; plx_min in mas. A parallax FLOOR
    (default 5 mas, i.e. d < 200 pc) is applied because (i) high-PM lenses are
    intrinsically nearby, so this loses ~nothing, and (ii) parallax is indexed
    on the Gaia server, so the floor prunes the table BEFORE the proper-motion
    expression is evaluated -- without it, the SQRT(pm) scan over a 1-deg cone
    times out on the DR4-evolution server. The PM cut uses (pmra^2+pmdec^2) >
    pm_min^2 (no SQRT) for the same reason. All comparisons use '>' (a literal
    '<' is XML-escaped to '&lt;' by the async job submission and breaks ADQL).
    """
    Gaia = _gaia()
    cols = ("source_id, ra, dec, parallax, parallax_error, parallax_over_error, "
            "pmra, pmdec, pmra_error, pmdec_error, "
            "phot_g_mean_mag, bp_rp, ruwe, "
            "radial_velocity, "
            "phot_bp_mean_mag, phot_rp_mean_mag")
    pm_min_sq = pm_min * pm_min
    # NB: no SQL "ORDER BY" -- this Gaia TAP parser rejects ORDER BY on a
    # computed expression (and ordering by pm needs the expression). We sort
    # client-side below instead.
    q = (f"SELECT TOP {row_limit} {cols} FROM {GAIA_TABLE} "
         f"WHERE 1=CONTAINS(POINT('ICRS',ra,dec), "
         f"CIRCLE('ICRS',{ra_deg},{dec_deg},{radius_deg})) "
         f"AND parallax > {plx_min} AND parallax_over_error > 5 "
         f"AND (pmra*pmra+pmdec*pmdec) > {pm_min_sq} "
         f"AND {gmax} > phot_g_mean_mag")
    tbl = with_timeout(lambda: Gaia.launch_job(q).get_results(), timeout, default=None)
    if tbl is None:
        return []
    out = []
    for r in tbl:
        out.append(dict(
            source_id=str(r["source_id"]),
            ra=float(r["ra"]), dec=float(r["dec"]),
            parallax=float(r["parallax"]),
            parallax_error=float(r["parallax_error"]),
            pmra=float(r["pmra"]), pmdec=float(r["pmdec"]),
            pm_tot=float(math.hypot(r["pmra"], r["pmdec"])),
            g=float(r["phot_g_mean_mag"]),
            bp_rp=(float(r["bp_rp"]) if not np.ma.is_masked(r["bp_rp"]) else None),
            ruwe=(float(r["ruwe"]) if not np.ma.is_masked(r["ruwe"]) else None),
        ))
    out.sort(key=lambda d: d["pm_tot"], reverse=True)   # highest-PM lenses first
    return out


# --------------------------------------------------------------------------- #
# 2. background sources along the lens future track
# --------------------------------------------------------------------------- #
def find_background_sources(lens, win_start=WIN_START_JYEAR, win_end=WIN_END_JYEAR,
                            search_radius_arcsec=None, src_plx_max=2.0,
                            src_pm_max=50.0, gmax=21.0, timeout=120, row_limit=500):
    """Gaia DR3 neighbours within reach of the lens's track over the window.

    The cone is centred on the MID-WINDOW lens position with radius = half the
    total track length + a margin, so any star the lens sweeps past is captured.
    Keeps near-static background stars: small PM (< src_pm_max) and small/absent
    parallax (< src_plx_max => more distant than the lens). Excludes the lens
    itself. Returns list of dicts.
    """
    Gaia = _gaia()
    astro = geo.Astrometry(lens["ra"], lens["dec"], lens["pmra"], lens["pmdec"],
                           lens["parallax"], GAIA_REF_JYEAR)
    # track endpoints (mas offsets from ref) -> degrees, to set cone centre/radius
    dra_s, ddec_s = geo.lens_position(astro, np.array([win_start]))
    dra_e, ddec_e = geo.lens_position(astro, np.array([win_end]))
    cosd = math.cos(math.radians(lens["dec"]))
    ra_s = lens["ra"] + dra_s[0] / 3600e3 / cosd
    dec_s = lens["dec"] + ddec_s[0] / 3600e3
    ra_e = lens["ra"] + dra_e[0] / 3600e3 / cosd
    dec_e = lens["dec"] + ddec_e[0] / 3600e3
    ra_mid, dec_mid = 0.5 * (ra_s + ra_e), 0.5 * (dec_s + dec_e)
    # track half-length in arcsec
    track_len_mas = math.hypot((dra_e[0] - dra_s[0]), (ddec_e[0] - ddec_s[0]))
    if search_radius_arcsec is None:
        search_radius_arcsec = track_len_mas / 1000.0 / 2.0 + 5.0   # +5" margin
    rad_deg = search_radius_arcsec / 3600.0

    cols = ("source_id, ra, dec, parallax, parallax_over_error, pmra, pmdec, "
            "phot_g_mean_mag, bp_rp")
    # near-static background: small total PM; small/insignificant parallax.
    # '<' flipped to '>' (async-job XML-escapes a literal '<' -> breaks ADQL);
    # PM cut without SQRT (cheaper). The cone is small (a single track), so the
    # PM expression is inexpensive here.
    src_pm_max_sq = src_pm_max * src_pm_max
    q = (f"SELECT TOP {row_limit} {cols} FROM {GAIA_TABLE} "
         f"WHERE 1=CONTAINS(POINT('ICRS',ra,dec), "
         f"CIRCLE('ICRS',{ra_mid},{dec_mid},{rad_deg})) "
         f"AND source_id != {lens['source_id']} "
         f"AND {src_pm_max_sq} > (pmra*pmra+pmdec*pmdec) "
         f"AND (parallax IS NULL OR {src_plx_max} > parallax) "
         f"AND {gmax} > phot_g_mean_mag")
    tbl = with_timeout(lambda: Gaia.launch_job(q).get_results(), timeout, default=None)
    if tbl is None:
        return []
    out = []
    for r in tbl:
        plx = (float(r["parallax"]) if not np.ma.is_masked(r["parallax"]) else 0.0)
        out.append(dict(
            source_id=str(r["source_id"]),
            ra=float(r["ra"]), dec=float(r["dec"]),
            parallax=plx,
            pmra=(float(r["pmra"]) if not np.ma.is_masked(r["pmra"]) else 0.0),
            pmdec=(float(r["pmdec"]) if not np.ma.is_masked(r["pmdec"]) else 0.0),
            g=float(r["phot_g_mean_mag"]),
        ))
    return out


# --------------------------------------------------------------------------- #
# 3. rank predicted events
# --------------------------------------------------------------------------- #
def rank_events(lens, sources, mass_msun=DEFAULT_LENS_MASS,
                win_start=WIN_START_JYEAR, win_end=WIN_END_JYEAR,
                max_sep_for_event_mas=2000.0):
    """For each background source, predict the event and return ranked rows.

    max_sep_for_event_mas: pre-filter -- a pair whose closest approach never gets
    within this (generous) separation is not an "event" worth ranking.
    """
    astro = geo.Astrometry(lens["ra"], lens["dec"], lens["pmra"], lens["pmdec"],
                           lens["parallax"], GAIA_REF_JYEAR)
    rows = []
    for s in sources:
        pred = geo.predict_event(
            astro, s["ra"], s["dec"], mass_msun, win_start, win_end,
            src_parallax_mas=s.get("parallax", 0.0),
            src_pmra_mas_yr=s.get("pmra", 0.0), src_pmdec_mas_yr=s.get("pmdec", 0.0))
        if not np.isfinite(pred.sep_min_mas) or pred.sep_min_mas > max_sep_for_event_mas:
            continue
        rows.append(dict(
            lens_source_id=lens["source_id"], src_source_id=s["source_id"],
            lens_g=lens["g"], src_g=s["g"],
            lens_pm_mas_yr=lens["pm_tot"], lens_plx_mas=lens["parallax"],
            assumed_mass_msun=mass_msun,
            theta_e_mas=pred.theta_e_mas,
            t0_jyear=pred.t0_jyear, sep_min_mas=pred.sep_min_mas,
            u_min=pred.u_min,
            peak_centroid_shift_uas=pred.peak_centroid_shift_uas,
            global_max_shift_uas=pred.peak_centroid_shift_uas_max,
            peak_magnification=pred.peak_magnification,
            peak_delta_mag_mmag=pred.peak_delta_mag_mmag,
            t_E_days=pred.crossing_time_days,
            rel_pm_mas_yr=pred.rel_pm_mas_yr,
        ))
    rows.sort(key=lambda d: d["peak_centroid_shift_uas"], reverse=True)
    return rows


# --------------------------------------------------------------------------- #
# orchestration over one or more sky regions
# --------------------------------------------------------------------------- #
def run_region(name, ra, dec, radius_deg, pm_min=150.0, mass_msun=DEFAULT_LENS_MASS,
               win_start=WIN_START_JYEAR, win_end=WIN_END_JYEAR,
               max_lenses=40, per_lens_timeout=120):
    """Full pipeline for one region. Returns (lenses, all_event_rows)."""
    print(f"[region {name}] selecting high-PM lenses (mu>{pm_min}) in "
          f"{radius_deg} deg around ({ra},{dec})...", file=sys.stderr)
    lenses = select_lenses(ra, dec, radius_deg, pm_min=pm_min)
    print(f"  -> {len(lenses)} lenses", file=sys.stderr)
    all_rows = []
    for i, lens in enumerate(lenses[:max_lenses]):
        srcs = find_background_sources(lens, win_start, win_end,
                                       timeout=per_lens_timeout)
        if not srcs:
            continue
        rows = rank_events(lens, srcs, mass_msun, win_start, win_end)
        if rows:
            all_rows.extend(rows)
        if (i + 1) % 5 == 0:
            print(f"  ...{i+1}/{min(len(lenses),max_lenses)} lenses, "
                  f"{len(all_rows)} candidate events so far", file=sys.stderr)
    all_rows.sort(key=lambda d: d["peak_centroid_shift_uas"], reverse=True)
    return lenses, all_rows


def write_outputs(rows, prefix):
    """Write predicted-event table to CSV + JSON under /tmp."""
    csv_path = f"/tmp/{prefix}.csv"
    json_path = f"/tmp/{prefix}.json"
    if rows:
        keys = list(rows[0].keys())
        with open(csv_path, "w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=keys)
            w.writeheader()
            w.writerows(rows)
    with open(json_path, "w") as f:
        json.dump(rows, f, indent=2)
    print(f"wrote {len(rows)} rows -> {csv_path}, {json_path}", file=sys.stderr)
    return csv_path, json_path


if __name__ == "__main__":
    # A small demonstration region. Real runs sample many fields / all-sky.
    # Default: a field around Barnard's Star (very high PM) is a classic
    # astrometric-microlensing-predictor target region.
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument("--ra", type=float, default=269.45)     # ~Barnard's Star field
    p.add_argument("--dec", type=float, default=4.7)
    p.add_argument("--radius", type=float, default=1.0)
    p.add_argument("--pm-min", type=float, default=150.0)
    p.add_argument("--mass", type=float, default=DEFAULT_LENS_MASS)
    p.add_argument("--prefix", type=str, default="microlensing_events")
    args = p.parse_args()
    lenses, rows = run_region("cli", args.ra, args.dec, args.radius,
                              pm_min=args.pm_min, mass_msun=args.mass)
    write_outputs(rows, args.prefix)
    for r in rows[:10]:
        print(f"{r['lens_source_id']} x {r['src_source_id']}: "
              f"shift={r['peak_centroid_shift_uas']:.1f} uas @ {r['t0_jyear']:.2f}, "
              f"u_min={r['u_min']:.2f}, dmag={r['peak_delta_mag_mmag']:.2f} mmag")
