"""Detail plot for DESI candidates from the store: Ca II triplet (normalised, 2 A bins), H-alpha region and O I 7774 (linear continuum).
python desi_detail.py out.png targetid ..."""
import os
import sys, numpy as np, pandas as pd, matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
from scipy.ndimage import gaussian_filter1d
sys.path.insert(0, os.path.expanduser("~/claude_projects/sdssv-white-dwarfs-2026/scripts"))
from gas_disc_screen import GRID, norm, XC, WIN, WC
c = pd.read_csv("desi_candidates_swan.csv", dtype={"targetid": str}).set_index("targetid")
ids = sys.argv[2:]; fig, ax = plt.subplots(len(ids), 3, figsize=(15, 2.3 * len(ids)), gridspec_kw=dict(width_ratios=[2, 1.2, 0.7])); ax = np.atleast_2d(ax)
for i, t in enumerate(ids):
    d = np.load(f"store/{t[-2:]}/{t}.npz"); n, v = norm(d["f_8250"].astype(float), d["iv_8250"].astype(float), XC, WIN)
    e = np.arange(8420, 8722, 2.0); cc = 0.5 * (e[1:] + e[:-1]); k = np.digitize(WC, e) - 1; ok = (k >= 0) & (k < len(cc)) & (v > 0) & np.isfinite(n)
    y = np.bincount(k[ok], (n * v)[ok], len(cc)) / np.maximum(np.bincount(k[ok], v[ok], len(cc)), 1e-30); ax[i, 0].plot(cc, y, "k", drawstyle="steps-mid", lw=0.8)
    for l in (8448.7, 8500.35, 8544.44, 8664.52): ax[i, 0].axvline(l, color="r", lw=0.4)
    r = c.loc[t]; ax[i, 0].set_ylabel(f"{r['name'][:10]}\n{r.specType} {float(r.TEFF):.0f}K", fontsize=7)
    for j, (a, b, lines) in enumerate(((6400, 6750, (6564.61,)), (7740, 7810, (7773.4, 7775.4, 7776.6))), start=1):
        m = (GRID > a) & (GRID < b); w = GRID[m]; f = d[f"f_{a}"].astype(float); iv = d[f"iv_{a}"].astype(float); okk = (iv > 0) & np.isfinite(f)
        if okk.sum() < 10: continue
        p = np.polyfit(w[okk], f[okk], 1); ax[i, j].plot(w, gaussian_filter1d(np.where(okk, f / np.polyval(p, w), 1), 1.5), "k", lw=0.7)
        for l in lines: ax[i, j].axvline(l, color="r", lw=0.4)
plt.tight_layout(); plt.savefig(sys.argv[1], dpi=75)
