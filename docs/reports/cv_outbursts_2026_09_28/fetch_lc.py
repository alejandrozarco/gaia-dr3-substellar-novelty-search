"""Fetch ALeRCE ZTF alert detections for every object in pool_unknown.csv into lc/<oid>.csv (mjd, fid, magpsf, sigmapsf,
magpsf_corr, sigmapsf_corr, isdiffpos, diffmaglim, corrected, rb, drb, dubious). Resumable; failures -> lc_failed.txt."""
import os, time, requests, pandas as pd
from concurrent.futures import ThreadPoolExecutor
P = pd.read_csv("pool_unknown.csv").oid.tolist(); COLS = ["mjd", "fid", "magpsf", "sigmapsf", "magpsf_corr", "sigmapsf_corr", "isdiffpos", "diffmaglim", "corrected", "rb", "drb", "dubious"]
def get(oid):
    f = f"lc/{oid}.csv"
    if os.path.exists(f): return "cached"
    for k in range(4):
        try:
            r = requests.get(f"https://api.alerce.online/ztf/v1/objects/{oid}/detections", timeout=120)
            if r.ok:
                d = pd.DataFrame(r.json())
                (d[[c for c in COLS if c in d.columns]] if len(d) else pd.DataFrame(columns=COLS)).to_csv(f, index=False); return "ok"
            if r.status_code == 429: time.sleep(30)
        except Exception: pass
        time.sleep(5 * (k + 1))
    open("lc_failed.txt", "a").write(oid + "\n"); return "fail"
t0 = time.time(); n = 0
with ThreadPoolExecutor(4) as ex:
    for res in ex.map(get, P):
        n += 1
        if n % 500 == 0: print(n, "/", len(P), f"{time.time()-t0:.0f}s", flush=True)
print("ALL-DONE", n, "failed:", sum(1 for _ in open("lc_failed.txt")) if os.path.exists("lc_failed.txt") else 0, flush=True)
