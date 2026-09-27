"""DESI DR1 spectra of WDJ080026.64+633414.85 (DOA, 78 kK) and WDJ171743.52+515840.07 (DA, 65 kK): UHE windows (4495, 4655, 5280, 5665, 6060 A)
and He II 4686 / 5411, normalised by a 150-A running median; Gaia HRD position vs the Reindl+2021 UHE box (-0.71 <= (BP-RP)0 <= -0.37, 7.19 <= M_G0 <= 8.43)."""
import numpy as np, matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
from scipy.ndimage import median_filter, gaussian_filter1d
S = [("39633426852088069", "WDJ0800+6334 DOA"), ("39633279405524397", "WDJ1717+5158 DA")]; R = [(4440, 4560), (4600, 4740), (5180, 5460), (5580, 5750), (5980, 6120)]
fig, ax = plt.subplots(2, len(R), figsize=(16, 5))
for i, (k, lab) in enumerate(S):
    d = np.load(f"desi_{k}.npz"); w, f, iv = d["w"], d["f"], d["iv"]; ok = iv > 0; w, f = w[ok], f[ok]; c = median_filter(f, 187, mode="nearest"); n = gaussian_filter1d(f / c, 2)
    for j, (lo, hi) in enumerate(R):
        m = (w > lo) & (w < hi); ax[i, j].plot(w[m], n[m], "k", lw=.6); ax[i, j].set_ylim(0.85, 1.08)
        for l in (4495, 4655, 4686, 5243, 5280, 5411.5, 5665, 6060):
            if lo < l < hi: ax[i, j].axvline(l, color="r", lw=.5)
    ax[i, 0].set_ylabel(lab, fontsize=7)
plt.tight_layout(); plt.savefig("hotvar_desi.png", dpi=70)
