# Small-multiples figure: detrended ZTF combined (black) and g (green) / r (red) periodograms for every ZTF star, with the
# Baluev FAP=1e-3 level of the combined series and the systematics mask shaded; controls marked.
import json, glob, os, sys
import numpy as np
sys.path.insert(0, os.path.dirname(__file__))
from permnull_inject import sys_mask
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
os.chdir("/tmp/fanout/rotation")
T = json.load(open("data/targets.json")); C = json.load(open("data/controls.json"))
order = [r["source_id"] for r in T] + [r["source_id"] for r in C]
meta = {r["source_id"]: r for r in T + C}
sids = [s for s in order if os.path.exists(f"results/{s}_pgram.npz")]
n = len(sids); ncol = 3; nrow = (n + ncol - 1) // ncol
fig, axs = plt.subplots(nrow, ncol, figsize=(17, 2.3 * nrow), squeeze=False)
for k, sid in enumerate(sids):
    a = axs[k // ncol, k % ncol]
    z = np.load(f"results/{sid}_pgram.npz"); res = json.load(open(f"results/{sid}.json"))
    for lab, col, lw in (("zg", "g", 0.4), ("zr", "r", 0.4), ("comb", "k", 0.5)):
        if lab + "_f" in z:
            a.plot(z[lab + "_f"], z[lab + "_p"], color=col, lw=lw, alpha=0.8 if lab == "comb" else 0.5)
    a.axhline(res["pgram"]["comb"]["power_thr_fap1e3"], color="b", ls="--", lw=0.7)
    fx = z["comb_f"]; m = sys_mask(fx)
    a.fill_between(fx, 0, 1, where=m, color="0.85", transform=a.get_xaxis_transform(), zorder=0)
    a.set_xscale("log"); a.set_xlim(0.05, 300)
    ymax = max(res["pgram"]["comb"]["power_thr_fap1e3"] * 1.6, np.max(z["comb_p"][~m]) * 1.15)
    a.set_ylim(0, ymax)
    grp = meta[sid].get("group", "")
    tag = {"pos_ctrl": "POS CTRL", "neg_ctrl": "NEG CTRL"}.get(grp, "")
    b = res["pgram"]["comb"]["top"][0]
    a.set_title(f"{sid} {meta[sid].get('name','')[:22]} G={res['G']:.1f} {tag}", fontsize=7.5)
    a.tick_params(labelsize=6)
for k in range(n, nrow * ncol):
    axs[k // ncol, k % ncol].axis("off")
fig.suptitle("ZTF DR24 (limitmag/airmass-detrended) LS periodograms 0.05-300 c/d: black = g+r+i combined, green = g, red = r; "
             "blue dashed = Baluev FAP 1e-3 (combined); grey = systematics mask (k x day, +-lunar, +-1/yr sidebands, f<0.1)", fontsize=9)
fig.tight_layout(rect=(0, 0, 1, 0.985)); fig.savefig("plots/ZTF_periodogram_grid.png", dpi=80)
print("wrote plots/ZTF_periodogram_grid.png", n)
