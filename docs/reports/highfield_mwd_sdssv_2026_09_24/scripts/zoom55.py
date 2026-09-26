import numpy as np, spec as S
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
from scipy.ndimage import gaussian_filter1d
sid = 55606833
V = [v for v in S.load_visits(sid) if v["snr"] >= 8]
fig, axs = plt.subplots(3, 1, figsize=(14, 9))
rngs = [(6000, 7500), (7400, 8800), (3800, 5300)]
MARK = {"TiO heads (M dwarf)": [6159, 6651, 7054, 7589, 7666, 8432], "CaH": [6382, 6750], "Na I 8183/95, K I": [8183, 8195, 7665, 7699], "Ha stationary 7090 (59 MG), 7453 (117 MG), 5830 (230 MG)": [7090, 7453, 5830]}
cols = ["tab:orange", "tab:brown", "tab:purple", "tab:red"]
for a, (lo, hi) in zip(axs, rngs):
    for k, v in enumerate(V):
        c = S.continuum(v["lam"], v["flux"], v["ivar"]); m = (v["lam"] > lo) & (v["lam"] < hi) & np.isfinite(c)
        a.plot(v["lam"][m], gaussian_filter1d(v["flux"] / c, 1.5)[m] - 0.15 * k, lw=0.7, label=f"MJD {v['mjd']} S/N {v['snr']:.0f}")
    for (lab, ls), col in zip(MARK.items(), cols):
        for l in ls:
            if lo < l < hi: a.axvline(l * 1.000276, color=col, lw=0.8, alpha=0.7)
    a.set_xlim(lo, hi); a.set_ylim(0.45, 1.2)
axs[0].legend(fontsize=7); axs[0].set_title("55606833 / Gaia DR3 545633955251654016: per-visit spectra (XCSAO undone). orange TiO heads, brown CaH, purple Na I/K I, red H-alpha stationary components", fontsize=8, loc="left")
plt.tight_layout(); plt.savefig("plots/zoom_55606833.png", dpi=80)
