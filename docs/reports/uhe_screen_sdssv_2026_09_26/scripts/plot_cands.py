import os, numpy as np, pandas as pd, matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
from scipy.ndimage import median_filter, gaussian_filter1d
U = os.path.dirname(os.path.abspath(__file__)); C = pd.read_csv(f"{U}/candidates.csv", dtype={"sdss_id": str})
ids = [s for s in C.sdss_id if s not in ("59101580", "63039439")] + ["59101580", "63039439", "74510696"]
lab = {"59101580": "known DA UHE WDJ0706+6133", "63039439": "known DAO UHE HS 2115+1148", "74510696": "normal hot DAO J0814+0225"}
R = [(4600, 4740, "4655 / He II 4686"), (5150, 5420, "5243 / 5280"), (5950, 6300, "6068 / 6200")]
fig, ax = plt.subplots(len(ids), 3, figsize=(15, 1.55 * len(ids)))
for i, s in enumerate(ids):
    p = f"{U}/cuts/{s}.npz"
    if not os.path.exists(p): continue
    d = np.load(p); w, f = d["w"], d["f"]
    for j, (a, b, n) in enumerate(R):
        k = (w > a) & (w < b)
        if k.sum() < 20: continue
        y = f[k]; c = median_filter(y, 151, mode="nearest"); ax[i, j].plot(w[k], gaussian_filter1d(y / c, 1.5), "k", lw=.6); ax[i, j].set_ylim(0.8, 1.1)
        for l in [4655, 4687.0, 5243, 5280, 6068, 6200]:
            if a < l < b: ax[i, j].axvline(l, color="r", lw=.4, alpha=.5)
        ax[i, j].tick_params(labelsize=6); ax[i, j].set_yticks([])
        if i == 0: ax[i, j].set_title(n, fontsize=8)
    r = C[C.sdss_id == s]
    t = lab.get(s, f"{s} {r.classification.iloc[0]} S/N {r.snr.iloc[0]:.0f} G {r.g_mag.iloc[0]:.1f}" if len(r) else s)
    ax[i, 0].set_ylabel(t, fontsize=6, rotation=0, ha="right")
plt.tight_layout(); plt.savefig(f"{U}/cands.png", dpi=70)
