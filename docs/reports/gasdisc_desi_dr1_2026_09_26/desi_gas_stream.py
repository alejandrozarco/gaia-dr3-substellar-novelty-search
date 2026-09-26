"""Store DESI DR1 white-dwarf spectra (Amorim+2026 class file, 44,417 TARGETIDs) for the Ca II triplet emission screen.
SPARCL retrieve_by_specid (DESI-DR1), batches of 200; flux and ivar (mask != 0 -> ivar 0) interpolated onto the SDSS-V screen log
grid (3850-9250 A, 6e-5 dex) and stored over 6400-6750, 7740-7810, 8250-8950 A (and 3880-4000 A) in store/<last2>/<targetid>.npz.
Batches that fail after 3 tries are logged as HOLE lines in stream.log and retried at the end."""
import sys, os, time, numpy as np, pandas as pd, warnings
warnings.filterwarnings("ignore")
from sparcl.client import SparclClient
GRID = 10 ** np.arange(np.log10(3850), np.log10(9250), 6e-5)
REG = [(3880, 4000), (6400, 6750), (7740, 7810), (8250, 8950)]
a = pd.read_csv("/tmp/mwd/desi/DESI_CLASS_FINAL.txt", sep=r"\s+", dtype={"DESIID": str, "edr3id": str})
ids = a.DESIID.tolist(); first = "39627901678653625"   # WD 0856+048 positive control first and last
ids = [first] + [i for i in ids if i != first] + [first]
have = {f[:-4] for d in os.listdir("store") for f in os.listdir(f"store/{d}")} if os.path.exists("store") else set()
todo = [i for i in ids if i not in have] + ([first] if first in have else [])
print("to do", len(todo), flush=True)
c = SparclClient(read_timeout=900)
def save(rec):
    t = str(rec["specid"]); w = np.array(rec["wavelength"], float); f = np.array(rec["flux"], float)
    iv = np.array(rec["ivar"], float) * (np.array(rec["mask"]) == 0); ok = (iv > 0) & np.isfinite(f)
    if ok.sum() < 1000: return "BADSPEC"
    d = {}
    for lo, hi in REG:
        m = (GRID > lo) & (GRID < hi)
        d[f"f_{lo}"] = np.interp(GRID[m], w[ok], f[ok], left=np.nan, right=np.nan).astype(np.float32)
        d[f"iv_{lo}"] = np.interp(GRID[m], w[ok], iv[ok], left=0, right=0).astype(np.float32) * (np.median(np.diff(GRID[m])) / np.median(np.diff(w)))
    os.makedirs(f"store/{t[-2:]}", exist_ok=True); np.savez_compressed(f"store/{t[-2:]}/{t}.npz", **d); return "OK"
holes = []
def batch(chunk):
    for k in range(3):
        try:
            r = c.retrieve_by_specid([int(x) for x in chunk], include=["specid", "flux", "ivar", "wavelength", "mask"], dataset_list=["DESI-DR1"], limit=2000)
            got = {}
            for rec in r.records: got.setdefault(str(rec["specid"]), rec)
            return got
        except Exception as e:
            print("retrieve error", str(e)[:120], flush=True); time.sleep(30 * (k + 1))
    return None
t0 = time.time(); n = 0; stat = {}
for i in range(0, len(todo), 200):
    chunk = todo[i:i + 200]; got = batch(chunk)
    if got is None: holes.append(chunk); print("HOLE batch", i, flush=True); continue
    for t in chunk:
        s = save(got[t]) if t in got else "MISSING"; stat[s] = stat.get(s, 0) + 1
    n += len(chunk); print(f"{time.strftime('%H:%M:%S')} {n}/{len(todo)} {stat} {time.time()-t0:.0f}s", flush=True)
for chunk in holes:
    got = batch(chunk)
    if got is None: print("HOLE_FINAL", chunk[0], len(chunk), flush=True); continue
    for t in chunk:
        s = save(got[t]) if t in got else "MISSING"; stat[s] = stat.get(s, 0) + 1
print("positive control stored:", os.path.exists(f"store/{first[-2:]}/{first}.npz"), stat, flush=True)
print("DESI_STREAM_DONE", flush=True)
