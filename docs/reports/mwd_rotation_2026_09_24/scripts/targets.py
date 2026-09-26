import os
# Build the target list (27 new magnetic DA WDs) with Gaia DR3 astrometry, and list Gaia DR3 neighbours within 5" (and 10").
import csv, json, sys, requests, io
import numpy as np
SUM = os.path.expanduser("~/claude_projects/gaia-recovered-2026-05-27/docs/reports/mwd_zeeman_sdssv_2026_09_23/data/novelty_summary.csv")
rows = [r for r in csv.DictReader(open(SUM)) if r["verdict"] == "NO_MAGNETIC_LABEL"]
ids = [r["gaia_dr3"] for r in rows]
extra = ["4198738558061020928", "5807585134758743040", "50526755482496000", "2833867392391927936", "4241409569220727424"]
ids += extra
print("n targets", len(ids), "unique", len(set(ids)))
TAP = "https://gea.esac.esa.int/tap-server/tap/sync"
def adql(q):
    r = requests.post(TAP, data=dict(REQUEST="doQuery", LANG="ADQL", FORMAT="csv", QUERY=q), timeout=300)
    if r.status_code != 200: print("HOLE HTTP", r.status_code, r.text[:300]); sys.exit(2)
    return list(csv.DictReader(io.StringIO(r.text)))
q = ("SELECT source_id, ra, dec, pmra, pmdec, parallax, parallax_error, phot_g_mean_mag, phot_bp_mean_mag, phot_rp_mean_mag, "
     "ruwe, phot_variable_flag, has_epoch_photometry, ipd_frac_multi_peak, phot_bp_rp_excess_factor FROM gaiadr3.gaia_source WHERE source_id IN (" + ",".join(ids) + ")")
G = adql(q); print("gaia rows", len(G))
assert len(G) == len(ids), "missing rows"
byid = {g["source_id"]: g for g in G}
# neighbours within 10" of each target (2016.0 positions)
out = []
for sid in ids:
    g = byid[sid]
    qn = ("SELECT source_id, ra, dec, pmra, pmdec, parallax, phot_g_mean_mag, phot_bp_mean_mag, phot_rp_mean_mag, "
          f"DISTANCE(POINT({g['ra']},{g['dec']}), POINT(ra,dec))*3600 AS sep FROM gaiadr3.gaia_source "
          f"WHERE 1=CONTAINS(POINT(ra,dec), CIRCLE({g['ra']},{g['dec']},{10/3600})) AND source_id != {sid} ORDER BY sep")
    N = adql(qn)
    rec = dict(g); rec["neighbours_10as"] = N
    src = next((r for r in rows if r["gaia_dr3"] == sid), None)
    rec["name"] = src["simbad_name"] if src else ""
    rec["B_Ha_MG"] = src["B_Ha_MG"] if src else ""
    rec["dist_pc"] = src["dist_pc"] if src else ""
    rec["group"] = "no_label_22" if src else "second_look_5"
    out.append(rec)
    nb5 = [n for n in N if float(n["sep"]) < 5]
    print(sid, rec["name"][:26].ljust(26), "G=%.2f" % float(g["phot_g_mean_mag"]), "dec=%+.2f" % float(g["dec"]),
          "var=%s ep=%s" % (g["phot_variable_flag"], g["has_epoch_photometry"]),
          "nb<5\":", [(round(float(n["sep"]), 2), round(float(n["phot_g_mean_mag"]), 2) if n["phot_g_mean_mag"] else None) for n in nb5])
json.dump(out, open("data/targets.json", "w"), indent=1)
