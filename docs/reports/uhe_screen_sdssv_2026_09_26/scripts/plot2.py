import os, sys, numpy as np, matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
sys.path.insert(0, os.path.expanduser("~/claude_projects/sdssv-white-dwarfs-2026/scripts")); import sdssv
from scipy.ndimage import gaussian_filter1d, median_filter
U = os.path.dirname(os.path.abspath(__file__))
S = [(s, n) for s, n in [(a.split(":")[0], a.split(":")[1]) for a in sys.argv[1:]]]
R = [(4440, 4560, "4495"), (4880, 5000, "4941"), (5180, 5380, "5243 / 5280"), (5580, 5750, "5665")]
fig, ax = plt.subplots(len(S), len(R), figsize=(15, 1.7 * len(S)))
for i, (sid, lab) in enumerate(S):
    vs = sdssv.visits(sid); use = [v for v in vs if v["in_stack"]] or vs; w, f, iv = sdssv.coadd(use)[:3]; ok = (iv > 0) & np.isfinite(f); w, f = w[ok], f[ok]
    c = median_filter(f, 251, mode="nearest")
    for j, (a, b, n) in enumerate(R):
        k = (w > a) & (w < b); ax[i, j].plot(w[k], gaussian_filter1d(f[k] / c[k], 1.5), "k", lw=.6); ax[i, j].set_ylim(0.85, 1.08)
        for l in (4495, 4941, 5243, 5280, 5665): 
            if a < l < b: ax[i, j].axvline(l, color="r", lw=.5, alpha=.6)
        ax[i, j].tick_params(labelsize=6); ax[i, j].set_yticks([])
        if i == 0: ax[i, j].set_title(n, fontsize=8)
    ax[i, 0].set_ylabel(f"{lab}\n({sid}, {len(use)} vis)", fontsize=6, rotation=0, ha="right")
plt.tight_layout(); plt.savefig(f"{U}/second_pass.png", dpi=65)
