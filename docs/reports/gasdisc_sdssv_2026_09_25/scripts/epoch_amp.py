"""Per-epoch amplitude of the SDSS-V coadd Ca II triplet emission profile: python epoch_amp.py sdss_id lab
Template T = coadd normalised flux - 1 within +-1100 km/s of the three lines (zero elsewhere, 1-pixel smoothed). Each epoch is
normalised the same way (quadratic continuum over 8330-8830 with the windows masked), resampled onto the SDSS-V grid, and
A is the weighted least-squares scale of T (A = 1: same strength as the coadd). Also a null: A at the template shifted +-3000 km/s."""
import sys, glob, numpy as np
from scipy.ndimage import gaussian_filter1d
C = 299792.458; CAT = [8500.35, 8544.44, 8664.52]; sid, lab = sys.argv[1], sys.argv[2]
GRID = 10 ** np.arange(np.log10(3850), np.log10(9250), 6e-5); m = (GRID > 8250) & (GRID < 8950); W = GRID[m]
win = np.zeros(len(W), bool)
for l in CAT: win |= np.abs(W / l - 1) * C < 1100
def norm(w, f, iv):
    f = np.asarray(f, float); iv = np.asarray(iv, float); sel = (w > 8330) & (w < 8830) & (iv > 0) & np.isfinite(f); use = sel.copy()
    for l in CAT + [8448.7]: use &= np.abs(w / l - 1) * C > 1100
    for _ in range(3):
        p = np.polyfit(w[use], f[use], 2, w=np.sqrt(iv[use])); P = np.polyval(p, w); use &= np.abs((f - P) * np.sqrt(iv)) < 3
    n = np.interp(W, w[sel], (f / P)[sel], left=np.nan, right=np.nan); v = np.interp(W, w[sel], (iv * P ** 2)[sel], left=0, right=0)
    # resampling onto a coarser/finer grid: scale ivar by pixel-size ratio
    v *= np.median(np.diff(W)) / np.median(np.diff(w[sel])) if len(w[sel]) > 1 else 1
    return n, np.where(np.isfinite(n), v, 0)
d = np.load(f"store/{sid[-2:]}/{sid}.npz"); nc, vc = norm(W, d["f_8250"], d["iv_8250"])
T = np.where(win, gaussian_filter1d(np.nan_to_num(nc - 1), 1), 0.0)
def amp(n, v, TT):
    ok = (v > 0) & np.isfinite(n) & (np.abs(W - 8590) < 240); y = n - 1
    A = np.sum(v[ok] * TT[ok] * y[ok]) / np.sum(v[ok] * TT[ok] ** 2); e = 1 / np.sqrt(np.sum(v[ok] * TT[ok] ** 2)); return A, e
def shift(TT, dv): return np.interp(W, W * (1 + dv / C), TT, left=0, right=0)
rows = [("SDSS-V coadd", nc, vc)] + [(f"SDSS-V MJD {d['mjd'][k]}",) + norm(W, d["vf_8250"][k], d["viv_8250"][k]) for k in range(len(d["mjd"]))]
for fn in sorted(glob.glob(f"desi_{lab}_*.npz")):
    q = np.load(fn); rows.append((fn,) + norm(q["w"], q["f"], q["iv"]))
for name, n, v in rows:
    A, e = amp(n, v, T); nulls = [amp(n, v, shift(T, dv))[0] / amp(n, v, shift(T, dv))[1] for dv in (-3000, 3000)]
    print(f"{name:28s} A = {A:5.2f} +- {e:4.2f}  ({A/e:5.1f} sigma)   null sigmas {nulls[0]:5.1f} {nulls[1]:5.1f}")
