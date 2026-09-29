"""Stage 1 of the H-alpha screen: per object, the normalised 6400-6750 A region of every BOSS visit (XCSAO shift undone for in-stack
visits) and of the inverse-variance coadd, on a 1e-4 dex grid, normalised by a straight line through the side-band medians
(6405-6440, 6700-6745 A). Saved to halpha_store/<xx>/<sdss_id>.npz: W (once, grid.npy), n (nvis x N), e (nvis x N), n_c, e_c, mjd,
snr. Incremental: objects with a FITS file and no npz. Usage: python extract_halpha.py [--loop]  (--loop: repeat every 10 min until
build_store.log says finished)"""
import os, sys, time, argparse, warnings, numpy as np, pandas as pd
from astropy.io import fits
warnings.filterwarnings("ignore")
ap = argparse.ArgumentParser(); ap.add_argument("--loop", action="store_true"); A = ap.parse_args()
D = os.path.dirname(os.path.abspath(__file__)); C = 299792.458; HA = 6564.61
W = 10 ** np.arange(np.log10(6400), np.log10(6750), 1e-4); np.save(os.path.join(D, "halpha_store_grid.npy"), W)
L = (W > 6405) & (W < 6440); R = (W > 6700) & (W < 6745); CORE = np.abs(W - HA) < 120
T = pd.read_csv(os.path.join(D, "targets.csv"), dtype={"sdss_id": str})
def path(sid): return os.path.join(D, "visit", sid[-4:-2], sid[-2:], f"mwmVisit-0.8.1-{sid}.fits")
def opath(sid): return os.path.join(D, "halpha_store", sid[-2:], f"{sid}.npz")
def visits(sid):
    out = []
    with fits.open(path(sid)) as h:
        for i in (1, 2):
            if i >= len(h) or h[i].data is None or len(h[i].data) == 0: continue
            hd = h[i].header; wg = 10 ** (hd["CRVAL"] + hd["CDELT"] * np.arange(hd["NPIXELS"]))
            for r in h[i].data:
                v = float(r["xcsao_v_rad"]); ins = bool(r["in_stack"]); w = wg * (1 + v / C) if (ins and np.isfinite(v)) else wg
                f = np.array(r["flux"], float); iv = np.array(r["ivar"], float); m = (w > 6390) & (w < 6760); ok = m & (iv > 0) & np.isfinite(f)
                if ok.sum() < 150: continue
                out.append(dict(mjd=int(r["mjd"]), snr=float(r["snr"]), f=np.interp(W, w[ok], f[ok]), iv=np.interp(W, w[ok], iv[ok], left=0, right=0)))
    return out
def normalise(f, iv):
    ok = iv > 0
    if ok[L].sum() < 5 or ok[R].sum() < 5: return None
    yl, yr = np.median(f[L & ok]), np.median(f[R & ok]); xl, xr = np.median(W[L & ok]), np.median(W[R & ok])
    if yl <= 0 or yr <= 0: return None
    cont = yl + (yr - yl) * (W - xl) / (xr - xl)
    if np.any(cont[CORE] <= 0): return None
    n = f / cont; e = np.where(ok, 1 / np.sqrt(np.where(ok, iv, 1e-12)) / cont, np.inf); return n.astype(np.float32), e.astype(np.float32)
def run_once():
    todo = [s for s in T.sdss_id if os.path.exists(path(s)) and os.path.getsize(path(s)) > 20000 and not os.path.exists(opath(s))]
    n = 0; t0 = time.time()
    for sid in todo:
        try: vs = visits(sid)
        except Exception: continue
        N, E, M, S = [], [], [], []; num = np.zeros(len(W)); den = np.zeros(len(W))
        for v in vs:
            c = normalise(v["f"], v["iv"])
            if c is None: continue
            nn, ee = c; N.append(nn); E.append(ee); M.append(v["mjd"]); S.append(v["snr"]); w = np.where(np.isfinite(ee), 1 / ee.astype(float) ** 2, 0); num += w * np.where(np.isfinite(ee), nn, 1); den += w
        os.makedirs(os.path.dirname(opath(sid)), exist_ok=True)
        if not N: np.savez_compressed(opath(sid), empty=True); continue
        n_c = np.where(den > 0, num / np.where(den > 0, den, 1), 1.0); e_c = np.where(den > 0, 1 / np.sqrt(np.where(den > 0, den, 1)), np.inf)
        np.savez_compressed(opath(sid), n=np.array(N), e=np.array(E), n_c=n_c.astype(np.float32), e_c=e_c.astype(np.float32), mjd=np.array(M), snr=np.array(S, np.float32)); n += 1
    print(f"extracted {n} of {len(todo)} in {time.time() - t0:.0f} s", flush=True); return len(todo)
while True:
    run_once()
    if not A.loop: break
    if os.path.exists(os.path.join(D, "build_store.log")) and "finished" in open(os.path.join(D, "build_store.log")).read(): run_once(); print("builder finished; final extraction done"); break
    time.sleep(600)
