import os, requests, json
tok = open(os.path.expanduser("~/.config/lasair/token")).read().strip()
# Lasair-ZTF cone search (historical ZTF alerts)
r = requests.get("https://lasair-ztf.lsst.ac.uk/api/cone/",
    headers={"Authorization": f"Token {tok}"},
    params={"ra": 313.22651, "dec": -14.84044, "radius": 15.0, "requestType": "all"}, timeout=60)
print("lasair-ztf cone:", r.status_code, r.text[:500])

# ALeRCE ZTF cone
r2 = requests.get("https://api.alerce.online/ztf/v1/objects",
    params={"ra": 313.22651, "dec": -14.84044, "radius": 15, "page_size": 20}, timeout=60)
print("alerce ztf cone:", r2.status_code)
try:
    j = r2.json()
    print("n ztf objects within 15as:", len(j.get("items", [])))
    for it in j.get("items", []):
        print(" ", it.get("oid"), it.get("ndet"), it.get("firstmjd"), it.get("lastmjd"))
except Exception:
    print(r2.text[:300])
