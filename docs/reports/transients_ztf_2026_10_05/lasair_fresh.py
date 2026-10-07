"""Fresh ZTF objects from Lasair-ZTF (2026-10-01): jdmin within DAYS (default 5), >= 2 positive detections, any Sherlock class.
Positive control: same query on a wider window must be non-empty. Failed call aborts. Output: fresh_all.json, fresh_tns.json"""
import os, sys, json, time, requests, collections
from astropy.time import Time
tok = open(os.path.expanduser("~/.config/lasair/token_ztf")).read().strip(); H = {"Authorization": "Token " + tok}; now = Time.now().jd
DAYS = float(os.environ.get("DAYS", 5))
def Q(sel, tab, cond, lim=20000):
    for k in range(4):
        try:
            r = requests.post("https://lasair-ztf.lsst.ac.uk/api/query/", data=dict(selected=sel, tables=tab, conditions=cond, limit=lim), headers=H, timeout=300)
            r.raise_for_status(); return r.json()
        except Exception as ex: print("retry", k, repr(ex)[:200], flush=True); time.sleep(20 * (k + 1))
    sys.exit("Lasair query failed")
# probe: most recent jdmax in the database
p = Q("objects.objectId, objects.jdmax", "objects", f"objects.jdmax > {now-3:.1f} ORDER BY objects.jdmax DESC", lim=3)
print("probe latest jdmax:", p, "now jd", round(now, 3), flush=True)
cond = f"objects.jdmin > {now-DAYS:.1f} AND objects.ncandgp >= 2"
allo = Q("objects.objectId, objects.ramean, objects.decmean, objects.jdmin, objects.jdmax, objects.ncand, objects.ncandgp, objects.maggmin, objects.magrmin, objects.glatmean, sherlock_classifications.classification, sherlock_classifications.separationArcsec, sherlock_classifications.catalogue_object_id, sherlock_classifications.catalogue_table_name, sherlock_classifications.z, sherlock_classifications.photoZ",
         "objects, sherlock_classifications", cond)
tns = Q("objects.objectId, crossmatch_tns.tns_name", "objects, crossmatch_tns", cond)
T = {x["objectId"]: x["tns_name"] for x in tns}
print("fresh:", len(allo), "lasair-tns-joined:", len(T), collections.Counter(x["classification"] for x in allo), flush=True)
json.dump(dict(all=allo, tns=tns, jd_now=now), open("fresh_all.json", "w"))
