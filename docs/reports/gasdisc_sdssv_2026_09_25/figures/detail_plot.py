"""Detail plot of stored regions for emission candidates: python detail_plot.py out.png sid1 sid2 ..."""
import sys, numpy as np, matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt, pandas as pd
from scipy.ndimage import gaussian_filter1d
GRID = 10 ** np.arange(np.log10(3850), np.log10(9250), 6e-5)
REG = [(3880, 4000, "Ca II H/K", [3934.78, 3969.59]), (4780, 4940, "H-beta", [4862.68]), (4990, 5200, "Fe II 5018/5169, Mg I", [5019.8, 5170.5, 5174.1, 5185.0]),
       (6400, 6750, "H-alpha, He I 6678", [6564.61, 6679.99]), (7740, 7810, "O I 7774", [7773.4, 7775.4, 7776.6]), (8250, 8950, "O I 8446, Ca II triplet", [8448.7, 8500.35, 8544.44, 8664.52])]
lab = pd.read_csv("sw_all.csv", dtype=str).set_index("sdss_id")
ids = sys.argv[2:]; fig, ax = plt.subplots(len(ids), len(REG), figsize=(20, 2.6 * len(ids)), gridspec_kw=dict(width_ratios=[1, 1, 1.4, 1.6, 0.6, 3]))
ax = np.atleast_2d(ax)
for i, sid in enumerate(ids):
    d = np.load(f"store/{sid[-2:]}/{sid}.npz")
    for j, (a, b, nm, L) in enumerate(REG):
        m = (GRID > a) & (GRID < b); w = GRID[m]; f = d[f"f_{a}"].astype(float); iv = d[f"iv_{a}"].astype(float); ok = iv > 0
        if ok.sum() < 10: continue
        p = np.polyfit(w[ok], f[ok], 1); y = gaussian_filter1d(np.where(ok, f / np.polyval(p, w), 1), 1.2)
        ax[i, j].plot(w, y, "k", lw=0.7)
        for l in L: ax[i, j].axvline(l, color="r", lw=0.5, alpha=0.6)
        if i == 0: ax[i, j].set_title(nm, fontsize=8)
    r = lab.loc[sid]; ax[i, 0].set_ylabel(f"{r.gaia_dr3_source_id}\n{r.classification} G {float(r.g_mag):.1f}", fontsize=7)
plt.tight_layout(); plt.savefig(sys.argv[1], dpi=75)
