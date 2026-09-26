import os
import sys, json; sys.path.insert(0, "/tmp/kk76_fix")
from fitlib import *
from common import horizons_hstcentric_radec
FC = pickle.load(open("fits/fitCE.pkl", "rb")); FB = pickle.load(open("fits/fitB.pkl", "rb"))
ref = pickle.load(open("/tmp/kk76_referee/work/fits2.pkl", "rb"))
def el_from_ref(v):
    e, q, tp, om, w, inc = v["el"]
    return {"elements": {"epoch": 2453857.5, "e": float(e), "q": float(q), "Tp": float(tp), "asc_node": float(om), "arg_per": float(w), "i": float(inc)}}
july = list(json.load(open(os.path.expanduser("~/claude_projects/gaia-recovered-2026-05-27/docs/reports/precovery_campaign_2026_07_07/kk76_refit/fit_joint/elements.json")))["objects"].values())[0]
ORB = {"MY fit C (all 53)": FC["C"], "REFEREE fit C": el_from_ref(ref["C ground+REF2006+REF2010"]),
       "MY fit D (ground)": FB["D"], "REFEREE fit D (ground)": el_from_ref(ref["D ground-only"]),
       "JULY joint (wrong 2006 pts)": july}
dates = {"2026-09-22": Time("2026-09-22T00:00:00", scale="utc").jd, "2030-01-01": Time("2030-01-01T00:00:00", scale="utc").jd,
         "2040-01-01": Time("2040-01-01T00:00:00", scale="utc").jd}
P = {k: horizons_pred(v, list(dates.values()), center="500@399") for k, v in ORB.items()}
# JPL's own orbit (SBDB) geocentric
jpl = horizons_hstcentric_radec("88268;", list(dates.values())) if False else None
import urllib.parse, subprocess
def jpl_geo(jds):
    params = {"format": "json", "COMMAND": "'88268;'", "OBJ_DATA": "NO", "MAKE_EPHEM": "YES", "EPHEM_TYPE": "OBSERVER",
              "CENTER": "500@399", "QUANTITIES": "1", "ANG_FORMAT": "DEG", "EXTRA_PREC": "YES", "CSV_FORMAT": "YES",
              "TIME_TYPE": "UT", "TLIST_TYPE": "JD", "TLIST": " ".join(f"{j:.6f}" for j in jds)}
    js = json.loads(subprocess.run(["curl", "-sL", "--max-time", "120", "https://ssd.jpl.nasa.gov/api/horizons.api?" + urllib.parse.urlencode(params)], capture_output=True, text=True).stdout)
    body = js["result"].split("$$SOE")[1].split("$$EOE")[0].strip().splitlines()
    return [(float(l.split(",")[3]), float(l.split(",")[4])) for l in body]
P["JPL SBDB orbit (ground only)"] = jpl_geo(list(dates.values()))
base = P["MY fit C (all 53)"]
print("Geocentric predicted position minus MY fit C, arcsec (dRA*cosDec, dDec):")
print(f"{'orbit':32s}" + "".join(f"{d:>22s}" for d in dates))
for k, v in P.items():
    print(f"{k:32s}" + "".join(f"   ({o[0]:+8.2f},{o[1]:+6.2f})" for o in [offset_arcsec(a[0], a[1], b[0], b[1]) for a, b in zip(v, base)]))
print("\nMY fit C absolute 2026-09-22 geocentric: RA %.6f Dec %.6f" % base[0])
