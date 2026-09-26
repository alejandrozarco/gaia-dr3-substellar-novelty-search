# Fold at P and 2P with fine bins; depths of the two half-cycle dips at 2P (odd/even eclipses) per band; wider box widths at P.
import numpy as np, json
exec(open("j0353_eclipse.py").read().split("P0 = 0.0739348;")[0])
P = 0.07393480; T0 = 2460670.38343
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
fig, axs = plt.subplots(2, 2, figsize=(11, 6))
for j, b in enumerate(("o", "c")):
    d = D[b]
    for i, (per, lab) in enumerate(((P, "P"), (2 * P, "2P"))):
        ph = ((d["t"] - T0) / per + 0.25) % 1; nb = 40 if lab == "P" else 80; ed = np.linspace(0, 1, nb + 1); w = 1 / d["e"] ** 2
        mb = np.array([np.sum(d["f"][(ph >= ed[k]) & (ph < ed[k + 1])] * w[(ph >= ed[k]) & (ph < ed[k + 1])]) / np.sum(w[(ph >= ed[k]) & (ph < ed[k + 1])]) for k in range(nb)])
        eb = np.array([1 / np.sqrt(np.sum(w[(ph >= ed[k]) & (ph < ed[k + 1])])) for k in range(nb)])
        a = axs[j, i]; a.errorbar((ed[:-1] + ed[1:]) / 2, mb, eb, fmt="o", ms=3, color="k"); a.axhline(0, color="0.6", lw=0.6)
        a.set_title(f"ATLAS {b}, fold at {lab} = {per*24:.4f} h (mid-dip at phase 0.25)", fontsize=8)
    # odd/even depths at 2P: dips at phase 0.25 and 0.75 in the 2P fold
    ph2 = ((d["t"] - T0) / (2 * P) + 0.25) % 1; w = 1 / d["e"] ** 2
    for c in (0.25, 0.75):
        for hw in (0.02, 0.03):
            inb = np.abs(ph2 - c) < hw; out = (np.abs(ph2 - 0.25) > 0.08) & (np.abs(ph2 - 0.75) > 0.08)
            dep = np.sum(d["f"][inb] * w[inb]) / np.sum(w[inb]) - np.sum(d["f"][out] * w[out]) / np.sum(w[out]); err = 1 / np.sqrt(np.sum(w[inb]))
            print(f"{b} 2P-fold dip at phase {c}: half-width {hw} ({hw*2*P*1440:.1f} min each side): depth {dep:.1f} +- {err:.1f} uJy (n {inb.sum()})")
plt.tight_layout(); plt.savefig("j0353_folds.png", dpi=90)
