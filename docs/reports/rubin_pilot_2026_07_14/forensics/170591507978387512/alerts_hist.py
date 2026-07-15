import os, requests, json
def safe(fn):
    try: fn()
    except Exception as e: print("ERR:", repr(e)[:150])

def lasair():
    tok = open(os.path.expanduser("~/.config/lasair/token")).read().strip()
    for host in ["https://lasair-ztf.lsst.ac.uk", "https://lasair.roe.ac.uk"]:
        try:
            r = requests.get(host + "/api/cone/", headers={"Authorization": f"Token {tok}"},
                params={"ra": 313.22651, "dec": -14.84044, "radius": 15.0, "requestType": "all"}, timeout=25)
            print("lasair", host, r.status_code, r.text[:300]); return
        except Exception as e:
            print("lasair", host, "ERR", repr(e)[:100])
safe(lasair)

def alerce():
    r2 = requests.get("https://api.alerce.online/ztf/v1/objects",
        params={"ra": 313.22651, "dec": -14.84044, "radius": 15, "page_size": 20}, timeout=40)
    print("alerce ztf cone:", r2.status_code)
    j = r2.json()
    items = j.get("items", [])
    print("n ztf alert-objects within 15as:", len(items))
    for it in items:
        print(" ", it.get("oid"), "ndet", it.get("ndet"), "mjd", it.get("firstmjd"), "-", it.get("lastmjd"))
safe(alerce)

def fink_ztf():
    r3 = requests.post("https://api.ztf.fink-portal.org/api/v1/conesearch",
        json={"ra": 313.22651, "dec": -14.84044, "radius": 15}, timeout=40)
    print("fink-ztf cone:", r3.status_code, r3.text[:300])
safe(fink_ztf)
