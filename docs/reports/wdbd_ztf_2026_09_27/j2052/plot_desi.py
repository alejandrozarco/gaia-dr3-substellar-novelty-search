import numpy as np, matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
from scipy.ndimage import gaussian_filter1d
d = np.load("desi_dr1.npz"); w, f, iv = d["w"], d["f"], d["iv"]; ok = iv > 0
fig, ax = plt.subplots(4, 1, figsize=(12, 11))
ax[0].plot(w[ok], gaussian_filter1d(f[ok], 3), "k", lw=.5); ax[0].set_title("DESI DR1 39627705435554416 (WDJ2052-0324)"); ax[0].set_ylim(0, None)
for a, (lo, hi, lab) in zip(ax[1:], [(6480, 6650, "H-alpha"), (4800, 4920, "H-beta"), (7000, 9800, "red: TiO / Na I / K I?")]):
    k = ok & (w > lo) & (w < hi); a.plot(w[k], gaussian_filter1d(f[k], 1 if hi - lo < 500 else 4), "k", lw=.6); a.set_title(lab, fontsize=8)
    for l in (6564.6, 4862.7, 8185, 8197, 7667, 7701):
        if lo < l < hi: a.axvline(l, color="r", lw=.5)
plt.tight_layout(); plt.savefig("desi.png", dpi=70)
k = ok & (np.abs(w - 6564.6) < 8); print("H-alpha core min/median around:", np.round(np.median(f[ok & (np.abs(w - 6564.6) < 60) & (np.abs(w - 6564.6) > 30)]), 3), np.round(f[k], 2))
print("S/N ~", np.median(f[ok & (w > 5000) & (w < 5500)] * np.sqrt(iv[ok & (w > 5000) & (w < 5500)])))
