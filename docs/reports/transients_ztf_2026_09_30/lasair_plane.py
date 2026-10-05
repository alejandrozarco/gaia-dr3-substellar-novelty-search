"""Nova search (2026-09-30): Lasair-ZTF objects created in 2026 (object id ZTF26*), |b| < 15 deg, jdmax within 10 d,
>= 4 positive detections, any Sherlock class; TNS cross-match flagged by a second joined query. Output: plane.json."""
import os, sys, json, time, requests, collections
from astropy.time import Time
tok = open(os.path.expanduser("~/.config/lasair/token_ztf")).read().strip(); H = {"Authorization": "Token " + tok}; now = Time.now().jd
def Q(sel, tab, cond, lim=20000):
    for k in range(4):
        try:
            r = requests.post("https://lasair-ztf.lsst.ac.uk/api/query/", data=dict(selected=sel, tables=tab, conditions=cond, limit=lim), headers=H, timeout=300)
            r.raise_for_status(); return r.json()
        except Exception as ex: print("retry", k, repr(ex)[:120], flush=True); time.sleep(20 * (k + 1))
    sys.exit("Lasair query failed")
cond = f"objects.objectId LIKE 'ZTF26%' AND ABS(objects.glatmean) < 15 AND objects.jdmax > {now-10:.1f} AND objects.ncandgp >= 4"
A = Q("objects.objectId, objects.ramean, objects.decmean, objects.glatmean, objects.jdmin, objects.jdmax, objects.ncandgp, objects.maggmin, objects.magrmin, objects.maggmean, objects.magrmean, sherlock_classifications.classification, sherlock_classifications.separationArcsec, sherlock_classifications.catalogue_table_name",
      "objects, sherlock_classifications", cond)
T = {x["objectId"]: x["tns_name"] for x in Q("objects.objectId, crossmatch_tns.tns_name", "objects, sherlock_classifications, crossmatch_tns", cond)}
for x in A: x["tns"] = T.get(x["objectId"], "")
json.dump(A, open("plane.json", "w")); print(len(A), "objects;", sum(bool(x["tns"]) for x in A), "with TNS;", collections.Counter(x["classification"] for x in A))
for x in sorted([x for x in A if not x["tns"]], key=lambda x: min(x["maggmin"] or 99, x["magrmin"] or 99))[:60]:
    print(x["objectId"], round(x["ramean"], 5), round(x["decmean"], 5), "b %.1f" % x["glatmean"], x["classification"], "ndet", x["ncandgp"], "gmin", x["maggmin"] and round(x["maggmin"], 2), "rmin", x["magrmin"] and round(x["magrmin"], 2), "sep", x["separationArcsec"], x["catalogue_table_name"], "age %.1f" % (now - x["jdmin"]))
