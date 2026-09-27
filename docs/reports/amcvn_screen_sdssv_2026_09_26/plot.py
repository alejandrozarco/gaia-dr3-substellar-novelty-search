import os, sys, numpy as np, matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
sys.path.insert(0, os.path.expanduser("~/claude_projects/sdssv-white-dwarfs-2026/scripts")); import sdssv
from scipy.ndimage import gaussian_filter1d
A = os.path.dirname(os.path.abspath(__file__))
S = [("110632288", "CRTS J205436.5-541810 (dwarf nova)"), ("106348567", "ASASSN-21hc (known AM CVn)"), ("101617994", "SDSS J0903-0133 (known AM CVn)"),
     ("86029022", "GALEX J193134.7-140446"), ("95661684", "Gaia DR3 5254269858168675456")]
fig, ax = plt.subplots(len(S), 1, figsize=(15, 2.3 * len(S)))
for a, (sid, lab) in zip(ax, S):
    vs = sdssv.visits(sid); use = [v for v in vs if v["in_stack"]] or vs; w, f, iv = sdssv.coadd(use)[:3]; ok = (iv > 0) & np.isfinite(f) & (w > 3700) & (w < 9200)
    a.plot(w[ok], gaussian_filter1d(f[ok], 2), "k", lw=.5); a.set_xlim(3700, 9200)
    top = np.nanpercentile(gaussian_filter1d(f[ok], 2), 99.5); a.set_ylim(0, top * 1.1)
    for l, n in [(4472.7, "HeI"), (4923.3, "HeI"), (5017.1, "HeI"), (5877.3, "HeI"), (6680.0, "HeI"), (7067.1, "HeI"), (4687.0, "HeII"), (6564.6, "Ha"), (4862.7, "Hb"), (4341.7, "Hg"), (8544.4, "CaII")]:
        a.axvline(l, color="r" if "He" in n else "b", lw=.5, alpha=.4)
    a.text(3750, top, f"{lab} ({sid}), {len(vs)} visits", fontsize=8, va="top"); a.tick_params(labelsize=7)
plt.tight_layout(); plt.savefig(f"{A}/amcvn_cands.png", dpi=65)
