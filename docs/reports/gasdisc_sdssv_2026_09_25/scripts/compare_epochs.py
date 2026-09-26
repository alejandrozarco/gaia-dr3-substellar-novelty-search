"""Compare Ca II triplet region across SDSS-V coadd and SPARCL spectra (desi_<lab>_<k>.npz): python compare_epochs.py sdss_id lab"""
import sys, glob, numpy as np, matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
from scipy.ndimage import gaussian_filter1d
C = 299792.458; CAT = [8500.35, 8544.44, 8664.52]; sid, lab = sys.argv[1], sys.argv[2]
GRID = 10 ** np.arange(np.log10(3850), np.log10(9250), 6e-5)
def norm(w, f, iv):
    m = (w > 8330) & (w < 8830) & (iv > 0) & np.isfinite(f); use = m.copy()
    for l in CAT + [8448.7]: use &= np.abs(w / l - 1) * C > 1100
    for _ in range(3):
        p = np.polyfit(w[use], f[use], 2, w=np.sqrt(iv[use])); P = np.polyval(p, w); use &= np.abs((f - P) * np.sqrt(iv)) < 3
    return w[m], f[m] / P[m], iv[m] * P[m] ** 2
def rebin(w, y, iv, step=2.0):
    e = np.arange(8330, 8830 + step, step); c = 0.5 * (e[1:] + e[:-1]); k = np.digitize(w, e) - 1
    num = np.bincount(k[(k >= 0) & (k < len(c))], (y * iv)[(k >= 0) & (k < len(c))], len(c)); den = np.bincount(k[(k >= 0) & (k < len(c))], iv[(k >= 0) & (k < len(c))], len(c))
    return c, np.where(den > 0, num / np.where(den > 0, den, 1), np.nan), den
d = np.load(f"store/{sid[-2:]}/{sid}.npz"); m = (GRID > 8250) & (GRID < 8950)
sets = [("SDSS-V coadd", GRID[m], d["f_8250"], d["iv_8250"])]
for k in range(len(d["vf_8250"])): sets.append((f"SDSS-V {d['mjd'][k]}", GRID[m], d["vf_8250"][k], d["viv_8250"][k]))
for fn in sorted(glob.glob(f"desi_{lab}_*.npz")):
    q = np.load(fn); sets.append((fn.replace(".npz", ""), q["w"], q["f"], q["iv"]))
fig, ax = plt.subplots(1, 1, figsize=(11, 1.2 + 0.9 * len(sets)))
for i, (name, w, f, iv) in enumerate(sets):
    ww, y, wy = norm(w, np.asarray(f, float), np.asarray(iv, float)); c, yb, wb = rebin(ww, y, wy, 3.0)
    snr = np.nanmedian(np.sqrt(wb)); ax.plot(c, yb - 0.6 * i, lw=0.9); ax.text(8335, 1.15 - 0.6 * i, f"{name} S/N/3A {snr:.0f}", fontsize=7)
for l in CAT: ax.axvline(l, color="r", lw=0.4)
ax.set_xlim(8330, 8830); ax.set_title(f"{sid} Ca II triplet, continuum-normalised, 3 A bins (offset)"); plt.tight_layout(); plt.savefig(f"epochs_{lab}.png", dpi=85)
