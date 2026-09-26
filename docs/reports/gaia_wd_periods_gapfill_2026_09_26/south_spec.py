"""SDSS-V visits of 5 southern periodic hot white dwarfs (Gaia GLS, VSX periods): H-alpha, H-beta, He II 4686 and Ca II 8544 per visit."""
import os
import sys, numpy as np, matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
sys.path.insert(0, os.path.expanduser("~/claude_projects/sdssv-white-dwarfs-2026/scripts")); import sdssv
from scipy.ndimage import gaussian_filter1d
C = 299792.458
S = [("4844023064578952320", "93071386"), ("5909859644796090624", "104192853"), ("4846154678323893248", "93083451"), ("5892465542676716544", "103950707"), ("3471231910527986432", "78010298")]
L = [("He II 4686", 4687.0), ("H-beta", 4862.7), ("H-alpha", 6564.6), ("Ca II 8544", 8544.4)]
fig, ax = plt.subplots(len(S), 4, figsize=(14, 3.2 * len(S)))
for i, (g, sid) in enumerate(S):
    try: vs = sdssv.visits(sid)
    except Exception as ex: ax[i, 0].set_title(f"{g} HOLE {type(ex).__name__}"); continue
    for j, (n, l) in enumerate(L):
        for k, v in enumerate(vs):
            vel = (v["wave"] / l - 1) * C; m = (np.abs(vel) < 2500) & (v["ivar"] > 0)
            if m.sum() < 20: continue
            y = v["flux"][m] / np.median(v["flux"][m]); ax[i, j].plot(vel[m], gaussian_filter1d(y, 1.5) + 0.4 * k, lw=.7)
        ax[i, j].axvline(0, color="grey", lw=.4); ax[i, j].set_title(f"{g} {n} ({len(vs)} visits)", fontsize=8)
plt.tight_layout(); plt.savefig("south_spec.png", dpi=70)
