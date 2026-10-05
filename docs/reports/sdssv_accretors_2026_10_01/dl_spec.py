"""Download BOSS v6_2_1 daily spec-lite files (DR20 SAS) for download_list.csv. Resumable; status appended to dl_status.csv.
Path: spectra/daily/lite/{FFF}XXX/{field:06d}/{mjd}/spec-{field:06d}-{mjd}-{catalogid}.fits"""
import os, sys, csv, time, requests, threading, pandas as pd
from concurrent.futures import ThreadPoolExecutor, as_completed
D = os.path.dirname(os.path.abspath(__file__)); OUT = os.path.join(D, "spec"); os.makedirs(OUT, exist_ok=True)
BASE = "https://data.sdss.org/sas/dr20/spectro/boss/redux/v6_2_1/spectra/daily/lite"
L = pd.read_csv(os.path.join(D, "download_list.csv"), dtype={"sdss_id": str, "catalogid": str, "gaia": str})
ST = os.path.join(D, "dl_status.csv"); done = set(pd.read_csv(ST, dtype=str).fname) if os.path.exists(ST) else set()
tl = threading.local(); lock = threading.Lock()
def name(r): return f"spec-{int(r.field):06d}-{int(r.mjd)}-{r.catalogid}.fits"
def fetch(r):
    fn = name(r); p = os.path.join(OUT, fn)
    if os.path.exists(p) and os.path.getsize(p) > 50000: return fn, "cached"
    if not hasattr(tl, "s"): tl.s = requests.Session(); tl.s.headers["User-Agent"] = "sdssv-accretor-scout"
    f = f"{int(r.field):06d}"; url = f"{BASE}/{f[:3]}XXX/{f}/{int(r.mjd)}/{fn}"
    for k in range(4):
        try:
            q = tl.s.get(url, timeout=180)
            if q.status_code == 200 and len(q.content) > 50000 and q.content[:6] == b"SIMPLE":
                open(p + ".part", "wb").write(q.content); os.replace(p + ".part", p); return fn, "ok"
            if q.status_code == 404: return fn, "404"
        except Exception: pass
        time.sleep(5 * (k + 1))
    return fn, "fail"
todo = [r for r in L.itertuples() if name(r) not in done]; print("todo", len(todo), flush=True)
new = not os.path.exists(ST); f = open(ST, "a", newline=""); w = csv.writer(f)
if new: w.writerow(["fname", "status"])
t0 = time.time(); n = 0; stat = {}
with ThreadPoolExecutor(int(sys.argv[1]) if len(sys.argv) > 1 else 16) as ex:
    for fu in as_completed([ex.submit(fetch, r) for r in todo]):
        fn, s = fu.result(); stat[s] = stat.get(s, 0) + 1
        with lock: w.writerow([fn, s]); n += 1
        if n % 200 == 0: f.flush(); print(n, f"{time.time()-t0:.0f}s", stat, flush=True)
f.close(); print("finished", n, stat, f"{time.time()-t0:.0f}s", flush=True)
