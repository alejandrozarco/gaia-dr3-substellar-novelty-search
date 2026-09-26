# Zoom check of H-alpha, H-beta, He I 5877/4472/6680 regions of Gaia DR3 5208047381438507520 (XCSAO shift undone) and the
# depth baseline: mean depth in 6-A windows at 400 random positions that avoid NIST C II lines (rel. int. >= 30) by > 8 A.
import json, numpy as np
exec(open("spec_lines.py").read().split("vels = np.arange")[0])   # loads w, f, cont, depth, edep, L, C
rng = np.random.default_rng(1)
cii = np.array([x[0] for x in L["C II"] if x[1] >= 30])
vm = json.load(open("spec_lines.json"))["v_mean"]
cand = rng.uniform(3900, 7400, 4000); cand = [x for x in cand if np.min(np.abs(cii * (1 + vm / C) - x)) > 8][:400]
base = []
for mu in cand:
    sel = np.abs(w - mu) < 3; base.append(np.sum(depth[sel] / edep[sel] ** 2) / np.sum(1 / edep[sel] ** 2))
base = np.array(base); print(f"baseline mean depth at {len(base)} random C II-free windows: median {np.median(base):+.3f}, 16-84% {np.percentile(base,16):+.3f}..{np.percentile(base,84):+.3f}, 99% {np.percentile(base,99):+.3f}, max {base.max():+.3f}")
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
fig, ax = plt.subplots(1, 5, figsize=(18, 3.6))
for a, (lo, hi, nm, rest) in zip(ax, [(6530, 6610, "H-alpha", [6564.632]), (4830, 4900, "H-beta", [4862.691]), (5850, 5910, "He I 5877", [5877.25]), (4440, 4500, "He I 4472", [4472.735]), (6650, 6800, "He I 6680", [6679.99])]):
    s = (w > lo) & (w < hi); a.plot(w[s], f[s] / cont[s], "k", lw=0.9, drawstyle="steps-mid")
    for lam, I in L["C II"]:
        if lo < lam * (1 + vm / C) < hi and I >= 30: a.axvline(lam * (1 + vm / C), color="m", lw=0.8, alpha=0.7)
    for lam in rest: a.axvline(lam * (1 + vm / C), color="b", ls="--"); a.axvline(lam, color="b", ls=":", alpha=0.5)
    a.set_title(f"{nm} (blue dashed at {vm:+.0f} km/s; magenta C II)", fontsize=8); a.set_ylim(0.55, 1.15)
plt.tight_layout(); plt.savefig("fig_zoom_H_He.png", dpi=90)
for nm, lo, hi in [("Ha", 6555, 6575), ("Hb", 4855, 4872), ("HeI5877", 5872, 5885)]:
    s = (w > lo) & (w < hi); print(nm, " ".join(f"{a:.1f}:{b:.2f}" for a, b in zip(w[s], (f / cont)[s])))
