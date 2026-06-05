"""Apply the microlensing predictor to the PROJECT's science: the dormant
compact-object & substellar candidate list (lane #118, step 4).

Two cross-checks:

  (A) Are any of OUR candidates (docs/CANDIDATES.md source_ids) themselves
      viable astrometric-microlensing LENSES in 2024-2030 -- i.e. do they have
      enough proper motion to sweep past a background source, giving an
      INDEPENDENT weigh of the (dark) mass via the centroid deflection? For
      each candidate we pull its Gaia DR3 astrometry, compute theta_E for its
      estimated total/companion mass, and search its forward track for
      background neighbours.

  (B) Flag predicted events (from predict.py over a region) whose LENS is itself
      a white-dwarf / high-mass / compact candidate (a WD lens is the LAWD 37
      case -- the most scientifically valuable, since the deflection then
      measures a WD or remnant mass directly).

HONEST framing (see README): astrometric microlensing weighs a mass you can
ALREADY SEE (the lens must be in Gaia to predict its track). It cannot find an
unseen isolated dark remnant -- it can only INDEPENDENTLY WEIGH a known
foreground object that happens to line up with a background source. For our
candidates whose companion is dark but whose PRIMARY is luminous and moving,
the primary's track is what we predict; a microlensing deflection then weighs
the TOTAL system mass (primary + dark companion), a check on the photocentric
mass function -- but only IF a chance alignment occurs in the window, which for
any single target is rare.

Env: ostinato venv. Network: Gaia TAP. Writes /tmp. source_ids are STRINGS.
"""
from __future__ import annotations

import json
import math
import os
import sys
import warnings

warnings.filterwarnings("ignore")
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import geometry as geo       # noqa: E402
import predict as P          # noqa: E402

# --------------------------------------------------------------------------- #
# Our candidate roster (docs/CANDIDATES.md, 2026-06-04) -- source_id -> (label,
# estimated mass used for theta_E). Mass is the TOTAL system mass where the
# primary is luminous (the lens is the photocentre ~ the primary), else the
# companion/object mass. source_ids are STRINGS.
# --------------------------------------------------------------------------- #
CANDIDATES = {
    # Strong
    "2909342818326298112": ("WDJ060042 (WD + dark M2~1.37; M_tot~1.98)", 1.98),
    "3161546596480983040": ("Object B (blue Galactic compact/CV cand.)", 0.8),
    # Weaker
    "332248057157474176":  ("WDJ020915 (WD + dark M2~1.32; M_tot~2.04)", 2.04),
    "5612039087715504640": ("UCAC4 313 (M-dwarf + ~13 MJ substellar)", 0.4),
    # Watch-list
    "1593152388271709824": ("G-subgiant + dark M2~1.27 (WD/NS bound)", 2.7),
    "3155543945892767232": ("K-giant + M2~1.26 (NS cand.)", 2.7),
    "5858574810404752256": ("M2~1.48 (triple-favored)", 3.0),
    "4111149395881722496": ("HD 157033 (companion 0.4-6 Msun)", 3.0),
    # Confirmed/known context
    "6092654861665006592": ("WG 26 (confirmed sub-Ch double-WD)", 1.27),
    "3378588057203660160": ("HD 264291 (RV-confirmed heavy NS, M2~1.94)", 3.7),
    # M-dwarf super-Jupiter (Pile B)
    "5486916932205092352": ("APMPM J0710-5704 (M4V + ~9.5 MJ)", 0.4),
    "5796338299045711232": ("SCR J1441-7338 (M5.5V + ~11 MJ)", 0.3),
}


def candidate_astrometry(source_ids, timeout=90):
    """Pull Gaia DR3 astrometry for a list of (string) source_ids in one query."""
    Gaia = P._gaia()
    ids = ",".join(str(s) for s in source_ids)
    q = ("SELECT source_id, ra, dec, parallax, parallax_error, pmra, pmdec, "
         "phot_g_mean_mag, ruwe, ref_epoch "
         f"FROM gaiadr3.gaia_source WHERE source_id IN ({ids})")
    tbl = P.with_timeout(lambda: Gaia.launch_job(q).get_results(), timeout, default=None)
    if tbl is None:
        return {}
    d = {}
    for r in tbl:
        d[str(r["source_id"])] = dict(
            ra=float(r["ra"]), dec=float(r["dec"]),
            parallax=float(r["parallax"]),
            parallax_error=float(r["parallax_error"]),
            pmra=float(r["pmra"]), pmdec=float(r["pmdec"]),
            pm_tot=float(math.hypot(r["pmra"], r["pmdec"])),
            g=float(r["phot_g_mean_mag"]),
            ruwe=(float(r["ruwe"]) if not np.ma.is_masked(r["ruwe"]) else None),
            ref_epoch=float(r["ref_epoch"]))
    return d


def check_candidates_as_lenses(win_start=2024.0, win_end=2030.0, timeout=90):
    """(A) For each candidate, assess its viability as an astrometric-
    microlensing lens in the window and search its track for background sources.

    Returns a dict per source_id with theta_E (at the estimated mass), the
    forward track length, and any predicted events found.
    """
    astro = candidate_astrometry(list(CANDIDATES.keys()), timeout=timeout)
    results = {}
    for sid, (label, mass) in CANDIDATES.items():
        if sid not in astro:
            results[sid] = dict(label=label, note="not returned by Gaia query")
            continue
        a = astro[sid]
        lens = geo.Astrometry(a["ra"], a["dec"], a["pmra"], a["pmdec"],
                              a["parallax"], a.get("ref_epoch", 2016.0))
        theta_e = geo.einstein_radius_from_parallax(mass, a["parallax"])
        # forward track length over the window (mas)
        d0 = geo.lens_position(lens, np.array([win_start]))
        d1 = geo.lens_position(lens, np.array([win_end]))
        track_mas = math.hypot(d1[0][0] - d0[0][0], d1[1][0] - d0[1][0])
        rec = dict(label=label, assumed_mass_msun=mass,
                   ra=a["ra"], dec=a["dec"], pm_mas_yr=a["pm_tot"],
                   parallax_mas=a["parallax"], g=a["g"], ruwe=a["ruwe"],
                   theta_e_mas=theta_e, track_length_mas_2024_2030=track_mas,
                   events=[])
        # Search for background neighbours along the (often short) track. We use
        # a lens dict shaped like predict.select_lenses output.
        lens_d = dict(source_id=sid, ra=a["ra"], dec=a["dec"], pmra=a["pmra"],
                      pmdec=a["pmdec"], parallax=a["parallax"], g=a["g"],
                      pm_tot=a["pm_tot"])
        srcs = P.find_background_sources(lens_d, win_start, win_end,
                                         timeout=timeout)
        rec["n_background_neighbours"] = len(srcs)
        if srcs:
            rows = P.rank_events(lens_d, srcs, mass_msun=mass,
                                 win_start=win_start, win_end=win_end,
                                 max_sep_for_event_mas=5000.0)
            rec["events"] = rows[:5]
        results[sid] = rec
    return results


def flag_project_candidate_lenses(event_rows):
    """(B-i) Flag predicted-event rows whose LENS source_id is one of our
    compact/substellar candidates."""
    cand_ids = set(CANDIDATES.keys())
    return [r for r in event_rows if str(r.get("lens_source_id")) in cand_ids]


def is_white_dwarf_locus(abs_g, bp_rp):
    """Crude Gaia-HRD white-dwarf locus test: M_G > 10 and (blue) bp_rp < 1.0,
    or M_G > 8 + 3*bp_rp (below the main sequence). A WD lens is the highest-
    value microlensing target -- the deflection weighs the WD mass directly
    (the LAWD 37 case). For a definitive class, cross-match Gentile-Fusillo 2021.
    """
    if abs_g is None or not np.isfinite(abs_g):
        return False
    if bp_rp is None or not np.isfinite(bp_rp):
        return abs_g > 12.0          # very faint absolute mag => likely WD/sd
    return (abs_g > 10.0 and bp_rp < 1.0) or (abs_g > 8.0 + 3.0 * bp_rp)


def flag_wd_lenses(event_rows, timeout=90):
    """(B-ii) For the distinct lenses in an event table, pull Gaia colours +
    parallax, compute M_G, and flag those on the white-dwarf locus. Returns the
    event rows whose lens is a WD-locus object, annotated with M_G / bp_rp.
    """
    lens_ids = sorted({str(r["lens_source_id"]) for r in event_rows})
    if not lens_ids:
        return []
    Gaia = P._gaia()
    ids = ",".join(lens_ids)
    q = ("SELECT source_id, parallax, phot_g_mean_mag, bp_rp "
         f"FROM gaiadr3.gaia_source WHERE source_id IN ({ids})")
    tbl = P.with_timeout(lambda: Gaia.launch_job(q).get_results(), timeout, default=None)
    if tbl is None:
        return []
    info = {}
    for r in tbl:
        plx = float(r["parallax"])
        G = float(r["phot_g_mean_mag"])
        m_g = G + 5 + 5 * math.log10(plx / 1000.0) if plx > 0 else None
        bp_rp = (float(r["bp_rp"]) if not np.ma.is_masked(r["bp_rp"]) else None)
        info[str(r["source_id"])] = dict(abs_g=m_g, bp_rp=bp_rp,
                                         is_wd=is_white_dwarf_locus(m_g, bp_rp))
    flagged = []
    for r in event_rows:
        i = info.get(str(r["lens_source_id"]))
        if i and i["is_wd"]:
            rr = dict(r); rr.update(lens_abs_g=i["abs_g"], lens_bp_rp=i["bp_rp"],
                                    lens_is_wd_locus=True)
            flagged.append(rr)
    return flagged


def main():
    print("=== (A) Are our compact/substellar candidates viable lenses "
          "(2024-2030)? ===")
    res = check_candidates_as_lenses()
    summary = []
    for sid, rec in sorted(res.items(),
                           key=lambda kv: kv[1].get("track_length_mas_2024_2030", 0),
                           reverse=True):
        if "note" in rec:
            print(f"  {sid}  {rec['label']}: {rec['note']}")
            continue
        nev = len(rec["events"])
        best = (max((e["peak_centroid_shift_uas"] for e in rec["events"]),
                    default=0.0))
        print(f"  {sid}  mu={rec['pm_mas_yr']:7.1f} mas/yr  "
              f"track(2024-30)={rec['track_length_mas_2024_2030']:7.0f} mas  "
              f"theta_E={rec['theta_e_mas']:5.2f} mas  "
              f"bg_neigh={rec['n_background_neighbours']:3d}  "
              f"events={nev}  best_shift={best:6.1f} uas  | {rec['label']}")
        for e in rec["events"]:
            print(f"        -> src {e['src_source_id']} (G={e['src_g']:.1f}): "
                  f"shift={e['peak_centroid_shift_uas']:.1f} uas @ "
                  f"J{e['t0_jyear']:.2f}, sep_min={e['sep_min_mas']:.0f} mas, "
                  f"u={e['u_min']:.1f}")
        summary.append(dict(source_id=sid, **{k: rec[k] for k in
                       ("label", "pm_mas_yr", "track_length_mas_2024_2030",
                        "theta_e_mas", "n_background_neighbours")},
                       n_events=nev, best_shift_uas=best))

    out = dict(candidates=res, summary=summary)
    with open("/tmp/ml_candidate_crosscheck.json", "w") as f:
        json.dump(out, f, indent=2, default=float)
    print("\nwrote /tmp/ml_candidate_crosscheck.json")
    return out


if __name__ == "__main__":
    main()
