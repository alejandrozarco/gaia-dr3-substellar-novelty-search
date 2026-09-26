# Parallel (4 threads, shared HTTP session) polite download of mwmStar/mwmVisit files; failures logged as HOLES.
import sys, csv, time, os, requests, threading
from concurrent.futures import ThreadPoolExecutor
BASE = "/tmp/fanout/exotic_atm"; SAS = "https://data.sdss.org/sas/dr20/spectro/astra/0.8.1/spectra"
ids = [r["sdss_id"] for r in csv.DictReader(open(sys.argv[1]))]
kind = sys.argv[2] if len(sys.argv) > 2 else "star"
nthr = int(sys.argv[3]) if len(sys.argv) > 3 else 4
tl = threading.local()
def sess():
    if not hasattr(tl, "s"): tl.s = requests.Session()
    return tl.s
def one(sid):
    sid = str(sid); pre = "mwmStar" if kind == "star" else "mwmVisit"
    fn = f"{BASE}/{'spec' if kind=='star' else 'visit'}/{pre}-0.8.1-{sid}.fits"
    if os.path.exists(fn) and os.path.getsize(fn) > 1000: return sid, "cached"
    if os.path.exists(f"/tmp/mwd/spec/{pre}-0.8.1-{sid}.fits"): return sid, "cached_mwd"
    url = f"{SAS}/{kind}/{sid[-4:-2]}/{sid[-2:]}/{pre}-0.8.1-{sid}.fits"; err = None
    for k in range(3):
        try:
            r = sess().get(url, timeout=120)
            if r.status_code == 200 and len(r.content) > 1000:
                tmp = fn + ".part"; open(tmp, "wb").write(r.content); os.replace(tmp, fn); return sid, "ok"
            err = f"HTTP {r.status_code}"
            if r.status_code == 404: break
        except Exception as e: err = str(e)[:80]
        time.sleep(2 + 3 * k)
    return sid, "HOLE " + str(err)
log = open(sys.argv[1].replace(".csv", f"_{kind}_dl.log"), "w"); t0 = time.time(); n = 0; bad = 0
with ThreadPoolExecutor(nthr) as ex:
    for sid, st in ex.map(one, ids):
        n += 1
        if st.startswith("HOLE"): bad += 1; log.write(f"{sid} {st}\n"); log.flush()
        if n % 200 == 0: print(n, bad, round(time.time() - t0), flush=True)
print("done", n, "holes", bad, round(time.time() - t0), flush=True); log.write(f"done n={n} holes={bad}\n"); log.close()
