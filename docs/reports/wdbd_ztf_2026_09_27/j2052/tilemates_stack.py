"""Median residual around H-alpha of the tile-mates on tile 20836 / petal 8 (galaxies and QSOs with no strong line redshifted into
6540-6600 A), compared with J2052's emission (centre 6568.75 A vacuum, barycentric)."""
import numpy as np, matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
D = np.load("tilemates_ha.npy", allow_pickle=True).item(); G = np.arange(6500, 6640, 0.8)
LINES = [3727.4, 4102.9, 4341.7, 4862.7, 4960.3, 5008.2, 6549.9, 6564.6, 6585.3, 6718.3, 6732.7]
R, n_ex = [], 0
for k, s in D.items():
    if k == "39627705435554416" or s["t"] not in ("GALAXY", "QSO"): continue
    z = s["z"]
    if any(6530 < l * (1 + z) < 6610 for l in LINES): n_ex += 1; continue
    w, f, iv = s["w"], s["f"], s["iv"]; ok = iv > 0
    side = ok & (((w > 6500) & (w < 6550)) | ((w > 6585) & (w < 6640)))
    if side.sum() < 40: continue
    p = np.polyfit(w[side], f[side], 1); c = np.polyval(p, w)
    if np.median(c[ok]) <= 0: continue
    noise = np.std((f / c)[side]); R.append(np.interp(G, w, (f / c - 1) / noise))   # residual in units of the local noise
R = np.array(R); med = np.median(R, 0); mad = 1.4826 * np.median(np.abs(R - med), 0) / np.sqrt(len(R))
print(len(R), "spectra stacked;", n_ex, "excluded (lines in window)")
for lo, hi in ((6562, 6567), (6566.5, 6571), (6550, 6555), (6575, 6580)):
    m = (G >= lo) & (G <= hi); print(f"{lo}-{hi} A: median residual {np.mean(med[m]):+.3f} sigma_noise (stack error {np.mean(mad[m]):.3f})")
plt.figure(figsize=(9, 3)); plt.plot(G, med, "k"); plt.fill_between(G, med - mad, med + mad, color="0.8"); plt.axvline(6564.6 * (1 + 27.3 / 299792.458), color="b", lw=.6); plt.axvline(6568.75, color="r", lw=.6)
plt.title(f"tile 20836 petal 8: median of {len(R)} galaxy/QSO residuals (blue: H-alpha at rest + barycentric; red: J2052 emission)", fontsize=7)
plt.tight_layout(); plt.savefig("tilemates_stack.png", dpi=80)
