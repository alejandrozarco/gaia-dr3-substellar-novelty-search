"""Recent ZTF transients (Lasair-ZTF) with a Sherlock SN / NT / ORPHAN context and no TNS cross-match (2026-09-30).
Query 1: objects with jdmax within 10 d, jdmin within 60 d, >= 3 positive detections, Sherlock class SN/NT/ORPHAN.
Query 2: the same conditions joined to crossmatch_tns. Difference = candidates without a TNS entry.
Every call is retried (3x); a failed call aborts (no silent empty result). Output: no_tns.json, lasair_recent2.json."""
import os, sys, json, time, requests, collections
from astropy.time import Time
tok = open(os.path.expanduser("~/.config/lasair/token_ztf")).read().strip(); H = {"Authorization": "Token " + tok}; now = Time.now().jd
D1, D0 = float(os.environ.get("DMAX", 10)), float(os.environ.get("DMIN", 60))
def Q(sel, tab, cond, lim=10000):
    for k in range(4):
        try:
            r = requests.post("https://lasair-ztf.lsst.ac.uk/api/query/", data=dict(selected=sel, tables=tab, conditions=cond, limit=lim), headers=H, timeout=300)
            r.raise_for_status(); return r.json()
        except Exception as ex: print("retry", k, repr(ex)[:120], flush=True); time.sleep(20 * (k + 1))
    sys.exit("Lasair query failed")
cond = f"objects.jdmax > {now-D1:.1f} AND objects.jdmin > {now-D0:.1f} AND objects.ncandgp >= 3 AND sherlock_classifications.classification IN ('SN','NT','ORPHAN')"
allo = Q("objects.objectId, objects.ramean, objects.decmean, objects.jdmin, objects.jdmax, objects.ncandgp, objects.maggmin, objects.magrmin, sherlock_classifications.classification, sherlock_classifications.separationArcsec, sherlock_classifications.catalogue_table_name, sherlock_classifications.z, sherlock_classifications.photoZ",
         "objects, sherlock_classifications", cond)
tns = Q("objects.objectId, crossmatch_tns.tns_name", "objects, sherlock_classifications, crossmatch_tns", cond)
T = {x["objectId"] for x in tns}; U = [x for x in allo if x["objectId"] not in T]
print("recent SN/NT/ORPHAN:", len(allo), "with TNS:", len(T), "without TNS:", len(U), collections.Counter(x["classification"] for x in U), flush=True)
json.dump(dict(all=allo, tns=tns, jd_now=now), open("lasair_recent2.json", "w")); json.dump(U, open("no_tns.json", "w"))
for x in sorted(U, key=lambda x: -x["ncandgp"])[:50]:
    print(x["objectId"], round(x["ramean"], 5), round(x["decmean"], 5), x["classification"], "ndet", x["ncandgp"], "gmin", x["maggmin"], "rmin", x["magrmin"], "sep", x["separationArcsec"], "z", x["z"], x["photoZ"], "span", round(x["jdmax"] - x["jdmin"], 1), "age", round(now - x["jdmin"], 1))
