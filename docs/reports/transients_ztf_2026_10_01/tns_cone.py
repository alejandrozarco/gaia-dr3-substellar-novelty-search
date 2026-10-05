"""TNS cone (10 arcsec) per position, one request per 20 s, 5-min pause on 429; positive control first (AT 2026adff =
ZTF26abxydtt at 17.7867 +8.77329); aborts if the control does not return its AT. Appends to tns_check.csv with UTC timestamp.
Usage: python tns_cone.py name:ra:dec [...]"""
import sys, io, time, os, requests, pandas as pd
from datetime import datetime, timezone
def cone(ra, de):
    for a in range(6):
        try:
            q = requests.get("https://www.wis-tns.org/search", params=dict(ra=ra, decl=de, radius=10, coords_unit="arcsec", format="csv"), headers={"User-Agent": "Mozilla/5.0 (literature check)"}, timeout=60)
            if q.status_code == 429: time.sleep(300); continue
            if q.ok and q.text.startswith('"ID"'):
                d = pd.read_csv(io.StringIO(q.text)); return "; ".join(f"{x.Name} {x['Obj. Type']} disc {x['Discovery Date (UT)']} {x.get('Reporting Group/s')}/{x.get('Discovery Data Source/s')} internal={x.get('Disc. Internal Name')}" for _, x in d.iterrows()) or "none"
            time.sleep(30)
        except Exception: time.sleep(30)
    return "HOLE"
c = cone(17.7867, 8.77329); print("control:", c, flush=True)
if "2026adff" not in c: sys.exit("control failed -> all results would be HOLE")
time.sleep(20)
for arg in sys.argv[1:]:
    nm, ra, de = arg.split(":"); r = cone(float(ra), float(de)); ts = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
    pd.DataFrame([dict(oid=nm, ra=ra, dec=de, tns=r, checked_utc=ts)]).to_csv("tns_check.csv", mode="a", header=not os.path.exists("tns_check.csv"), index=False)
    print(nm, ts, r, flush=True); time.sleep(20)
print("ALL-DONE")
