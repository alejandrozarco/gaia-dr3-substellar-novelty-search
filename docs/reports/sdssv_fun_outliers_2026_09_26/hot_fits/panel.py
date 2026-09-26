import os
import sys, numpy as np, matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
sys.path.insert(0, os.path.expanduser("~/claude_projects/sdssv-white-dwarfs-2026/scripts")); import sdssv
from scipy.ndimage import median_filter
S = [("102043792", "J1740 O(He) 140kK lit"), ("92431667", "PN Lo 1 118kK lit"), ("100568930", "0958-1758"), ("74510696", "J0814+0225"), ("80998734", "4036084504408126976"),
     ("73346836", "J0550-1554"), ("99327334", "J0629-4158"), ("109787602", "J1906-7558")]
R = [(4000, 4200), (4280, 4400), (4440, 4580), (4640, 4740), (4800, 4960), (5360, 5460), (5840, 5920), (6500, 6630)]
fig, ax = plt.subplots(len(S), len(R), figsize=(20, 2.0 * len(S)))
for i, (sid, lab) in enumerate(S):
    vs = sdssv.visits(sid); vs = [v for v in vs if v["in_stack"]] or vs; w, f, iv = sdssv.coadd(vs)[:3]
    ok = (iv > 0) & np.isfinite(f); w, f = w[ok], f[ok]; cont = median_filter(f, 301, mode="nearest")
    for j, (a, b) in enumerate(R):
        s = (w > a) & (w < b); ax[i, j].plot(w[s], np.convolve(f[s] / cont[s], np.ones(3) / 3, "same"), "k", lw=.6)
        for l in [4027.3, 4102.9, 4341.7, 4472.7, 4542.8, 4687.0, 4862.7, 4923.3, 5413.0, 5877.3, 6564.6, 4945.9]:
            if a < l < b: ax[i, j].axvline(l, color="r", lw=.4, alpha=.5)
        ax[i, j].tick_params(labelsize=6)
    ax[i, 0].set_ylabel(f"{sid}\n{lab}", fontsize=7)
plt.tight_layout(); plt.savefig("panel.png", dpi=60)
