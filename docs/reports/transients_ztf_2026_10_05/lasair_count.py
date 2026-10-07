import os, json, requests
from astropy.time import Time
tok = open(os.path.expanduser("~/.config/lasair/token_ztf")).read().strip(); H = {"Authorization": "Token " + tok}; now = Time.now().jd
r = requests.post("https://lasair-ztf.lsst.ac.uk/api/query/", data=dict(selected="objects.objectId, objects.ramean, objects.decmean, objects.jdmin, objects.jdmax, objects.ncandgp, objects.maggmin, objects.magrmin, objects.glatmean", tables="objects", conditions=f"objects.jdmin > {now-5:.1f} AND objects.ncandgp >= 2", limit=20000), headers=H, timeout=300)
r.raise_for_status(); d = r.json(); print("no-sherlock-join count:", len(d)); json.dump(d, open("fresh_objects_only.json", "w"))
a = {x["objectId"] for x in json.load(open("fresh_all.json"))["all"]}; m = [x for x in d if x["objectId"] not in a]; print("missing sherlock:", len(m)); print(m[:20])
