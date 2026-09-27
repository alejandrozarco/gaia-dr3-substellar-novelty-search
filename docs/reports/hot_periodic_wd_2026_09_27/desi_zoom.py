import numpy as np, glob, matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
from scipy.ndimage import median_filter, gaussian_filter1d
L = {"H": [3970.1, 4101.7, 4340.5, 4861.3, 6562.8], "HeI": [4026.2, 4387.9, 4471.5, 4713.1, 4921.9, 5015.7, 5875.6, 6678.2, 7065.2], "HeII": [4541.6, 4685.7, 5411.5, 6560.1]}
C = {"H": "r", "HeI": "b", "HeII": "g"}; R = [(3850, 4150), (4300, 4750), (4800, 5100), (5350, 5450), (5800, 5950), (6450, 6720), (7000, 7120)]
for gid in ("3842377248804727168", "3230486971974872192"):
    fs = sorted(glob.glob(f"desi_{gid}_*.npz")); fig, ax = plt.subplots(len(fs), len(R), figsize=(18, 2.6 * len(fs)), squeeze=False)
    for i, p in enumerate(fs):
        d = np.load(p); w, f, iv = d["w"], d["f"], d["iv"]; ok = iv > 0; w, f = w[ok], f[ok]; n = gaussian_filter1d(f / median_filter(f, 401, mode="nearest"), 1.5)
        for j, (lo, hi) in enumerate(R):
            m = (w > lo) & (w < hi); ax[i, j].plot(w[m], n[m], "k", lw=.6); ax[i, j].set_ylim(0.8, 1.1)
            for k, ls in L.items():
                for l in ls:
                    if lo < l < hi: ax[i, j].axvline(l, color=C[k], lw=.6, alpha=.6)
        ax[i, 0].set_ylabel(p.split("_")[-1][:-4], fontsize=6)
    fig.suptitle(f"Gaia DR3 {gid}: red H, blue He I, green He II", fontsize=9); plt.tight_layout(); plt.savefig(f"zoom_{gid}.png", dpi=70)
