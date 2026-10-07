"""ALeRCE ZTF objects with firstmjd >= MJD0 (default now-5 d) and ndet >= 2 (2026-10-01). Page cap 30 x 1000; probe a known object first.
Output: alerce_fresh.csv"""
import requests, time, sys, pandas as pd
from astropy.time import Time
A = "https://api.alerce.online/ztf/v1"; now = Time.now().mjd; m0 = now - 5
pr = requests.get(f"{A}/objects/ZTF26absimmf", timeout=60); print("probe", pr.status_code, pr.json().get("firstmjd") if pr.ok else pr.text[:100])
rows = []
for p in range(1, 31):
    for k in range(4):
        try:
            r = requests.get(f"{A}/objects", params=[("firstmjd", m0), ("firstmjd", now + 1), ("ndet", 2), ("ndet", 100000), ("page_size", 1000), ("page", p), ("count", "false"), ("order_by", "firstmjd"), ("order_mode", "DESC")], timeout=180)
            if r.ok: break
            print("http", r.status_code, r.text[:150])
        except Exception as ex: print("exc", repr(ex)[:100])
        time.sleep(15 * (k + 1))
    else: sys.exit(f"page {p} failed -> HOLE")
    it = r.json().get("items", []); rows += it; print("page", p, len(it), flush=True)
    if len(it) < 1000: break
df = pd.DataFrame(rows).drop_duplicates("oid"); df.to_csv("alerce_fresh.csv", index=False)
print(len(df), "objects; firstmjd range", df.firstmjd.min(), df.firstmjd.max(), "now", now)
print(df.columns.tolist())
