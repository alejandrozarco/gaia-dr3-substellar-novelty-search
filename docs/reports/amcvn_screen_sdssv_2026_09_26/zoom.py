import os, sys, numpy as np, matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
sys.path.insert(0, os.path.expanduser("~/claude_projects/sdssv-white-dwarfs-2026/scripts")); import sdssv
from scipy.ndimage import gaussian_filter1d
A = os.path.dirname(os.path.abspath(__file__))
R = [(4400, 4550, "He I 4471"), (4820, 5060, "Hb / He I 4922, 5016"), (5820, 5940, "He I 5876"), (6500, 6740, "Ha / He I 6678"), (7000, 7130, "He I 7065")]
rows = []
for sid, lab in [("110632288", "CRTS J2054-5418"), ("106348567", "ASASSN-21hc (AM CVn)")]:
    vs = sdssv.visits(sid); w, f, iv = sdssv.coadd(vs)[:3]; rows.append((lab + " coadd", w, f, iv))
    for v in vs: rows.append((f"{lab} MJD {v['mjd']} in_stack={v['in_stack']} snr {v['snr']:.1f}", v["wave"], v["flux"], v["ivar"]))
fig, ax = plt.subplots(len(rows), len(R), figsize=(18, 1.8 * len(rows)))
for i, (lab, w, f, iv) in enumerate(rows):
    ok = (iv > 0) & np.isfinite(f)
    for j, (a, b, n) in enumerate(R):
        k = ok & (w > a) & (w < b)
        if k.sum() < 10: continue
        y = gaussian_filter1d(f[k], 1.5); ax[i, j].plot(w[k], y, "k", lw=.6)
        for l in [4472.7, 4862.7, 4923.3, 5017.1, 5877.3, 6564.6, 6680.0, 7067.1]:
            if a < l < b: ax[i, j].axvline(l, color="b" if l in (4862.7, 6564.6) else "r", lw=.5, alpha=.5)
        ax[i, j].tick_params(labelsize=6); ax[i, j].set_yticks([])
        if i == 0: ax[i, j].set_title(n, fontsize=8)
    ax[i, 0].set_ylabel(lab, fontsize=6, rotation=0, ha="right")
plt.tight_layout(); plt.savefig(f"{A}/crts2054_zoom.png", dpi=70)
