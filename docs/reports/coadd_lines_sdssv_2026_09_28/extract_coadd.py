"""Full-range coadds from the raw mwmVisit store: for every object, the inverse-variance coadd of all BOSS visits (in-stack visits
shifted back to the observed frame by undoing the Astra XCSAO velocity; all visits on the native 1e-4 dex grid CRVAL 3.5523,
4648 pixels) -> coadd_store/<xx>/<sdss_id>.npz with f (float32), iv (float32), n_vis, mjds, snr, plus grid.npy. Incremental."""
import os, glob, time, numpy as np, pandas as pd, warnings
from astropy.io import fits
warnings.filterwarnings("ignore")
D = os.path.dirname(os.path.abspath(__file__)); C = 299792.458
GRID = 10 ** (3.5523 + 1e-4 * np.arange(4648)); np.save(os.path.join(D, "coadd_grid.npy"), GRID)
T = pd.read_csv(os.path.join(D, "targets.csv"), dtype={"sdss_id": str})
def path(sid): return os.path.join(D, "visit", sid[-4:-2], sid[-2:], f"mwmVisit-0.8.1-{sid}.fits")
def opath(sid): return os.path.join(D, "coadd_store", sid[-2:], f"{sid}.npz")
todo = [s for s in T.sdss_id if os.path.exists(path(s)) and not os.path.exists(opath(s))]; print("to do", len(todo), flush=True); t0 = time.time(); n = 0
for sid in todo:
    num = np.zeros(len(GRID)); den = np.zeros(len(GRID)); mj, sn = [], []
    try:
        with fits.open(path(sid), memmap=False) as h:
            for i in (1, 2):
                if i >= len(h) or h[i].data is None or len(h[i].data) == 0: continue
                hd = h[i].header; wg = 10 ** (hd["CRVAL"] + hd["CDELT"] * np.arange(hd["NPIXELS"]))
                for r in h[i].data:
                    v = float(r["xcsao_v_rad"]); ins = bool(r["in_stack"]); w = wg * (1 + v / C) if (ins and np.isfinite(v)) else wg
                    f = np.array(r["flux"], float); iv = np.array(r["ivar"], float); ok = (iv > 0) & np.isfinite(f)
                    if ok.sum() < 1000: continue
                    fi = np.interp(GRID, w[ok], f[ok], left=np.nan, right=np.nan); ii = np.interp(GRID, w[ok], iv[ok], left=0, right=0); ii[~np.isfinite(fi)] = 0; fi[~np.isfinite(fi)] = 0
                    num += ii * fi; den += ii; mj.append(int(r["mjd"])); sn.append(float(r["snr"]))
    except Exception: continue
    os.makedirs(os.path.dirname(opath(sid)), exist_ok=True)
    f = np.where(den > 0, num / np.where(den > 0, den, 1), np.nan).astype(np.float32); np.savez_compressed(opath(sid), f=f, iv=den.astype(np.float32), n_vis=len(mj), mjds=np.array(mj), snr=np.array(sn, np.float32)); n += 1
    if n % 5000 == 0: print(n, f"{time.time() - t0:.0f} s", flush=True)
print("done", n, f"{time.time() - t0:.0f} s")
