"""Persistent store of SDSS-V DR20 mwmVisit files (Astra 0.8.1) for the white-dwarf sample in targets.csv.
Raw FITS are kept unaltered under visit/<xx>/<yy>/ (xx, yy = the last four digits of sdss_id split as in the SAS tree); an index
(index.csv: sdss_id, n_boss_visits, telescopes, mjds, snrs, status) is appended as files land. Resumable: existing files of
plausible size are skipped. Usage: python build_store.py [--workers 6]"""
import os, sys, csv, time, argparse, requests, threading
from concurrent.futures import ThreadPoolExecutor, as_completed
import numpy as np, pandas as pd
from astropy.io import fits
ap = argparse.ArgumentParser(); ap.add_argument("--workers", type=int, default=6); A = ap.parse_args()
D = os.path.dirname(os.path.abspath(__file__)); SAS = "https://data.sdss.org/sas/dr20/spectro/astra/0.8.1/spectra/visit"
T = pd.read_csv(os.path.join(D, "targets.csv"), dtype={"sdss_id": str})
IDX = os.path.join(D, "index.csv"); done = set(pd.read_csv(IDX, dtype={"sdss_id": str}).sdss_id) if os.path.exists(IDX) else set()
todo = [s for s in T.sdss_id if s not in done]; print("targets", len(T), "done", len(done), "to do", len(todo), flush=True)
lock = threading.Lock(); tl = threading.local()
def path(sid): return os.path.join(D, "visit", sid[-4:-2], sid[-2:], f"mwmVisit-0.8.1-{sid}.fits")
def fetch(sid):
    p = path(sid); os.makedirs(os.path.dirname(p), exist_ok=True)
    if os.path.exists(p) and os.path.getsize(p) > 20000: return sid, "cached"
    if not hasattr(tl, "s"): tl.s = requests.Session(); tl.s.headers["User-Agent"] = "sdssv-wd-store"
    for k in range(4):
        try:
            r = tl.s.get(f"{SAS}/{sid[-4:-2]}/{sid[-2:]}/mwmVisit-0.8.1-{sid}.fits", timeout=180)
            if r.status_code == 200 and len(r.content) > 20000:
                tmp = p + ".part"; open(tmp, "wb").write(r.content); os.replace(tmp, p); return sid, "ok"
            if r.status_code == 404: return sid, "404"
        except Exception: pass
        time.sleep(5 * (k + 1))
    return sid, "fail"
def summarize(sid):
    p = path(sid)
    try:
        with fits.open(p) as h:
            tel, mj, sn = [], [], []
            for i in (1, 2):
                if i < len(h) and h[i].data is not None and len(h[i].data):
                    for r in h[i].data: tel.append(h[i].name.split("/")[1]); mj.append(int(r["mjd"])); sn.append(round(float(r["snr"]), 1))
        return dict(n_boss_visits=len(mj), telescopes="/".join(sorted(set(tel))), mjds="/".join(map(str, mj)), snrs="/".join(map(str, sn)))
    except Exception as ex:
        return dict(n_boss_visits=-1, telescopes="", mjds="", snrs=f"ERR {type(ex).__name__}")
new = not os.path.exists(IDX); f = open(IDX, "a", newline=""); w = csv.writer(f)
if new: w.writerow(["sdss_id", "n_boss_visits", "telescopes", "mjds", "snrs", "status"])
t0 = time.time(); n = 0; stat = {}
with ThreadPoolExecutor(A.workers) as ex:
    futs = [ex.submit(fetch, s) for s in todo]
    for fu in as_completed(futs):
        sid, st = fu.result(); stat[st] = stat.get(st, 0) + 1
        row = summarize(sid) if st in ("ok", "cached") else dict(n_boss_visits=0, telescopes="", mjds="", snrs="")
        with lock: w.writerow([sid, row["n_boss_visits"], row["telescopes"], row["mjds"], row["snrs"], st]); n += 1
        if n % 250 == 0: f.flush(); print(n, "done", f"{time.time() - t0:.0f} s", stat, flush=True)
f.close(); print("finished", n, stat, f"{time.time() - t0:.0f} s")
