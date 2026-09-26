"""Stack continuum-normalised Ca II triplet regions (observed frame) of faint vs bright WD-locus DAs to expose sky-subtraction residuals."""
import numpy as np, pandas as pd, matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt, sys
sys.path.insert(0, "."); from pass2 import norm, WC, XC, WIN
t = pd.read_csv("p2_test.csv", dtype={"sdss_id": str}); t = t[(t.grp == "H") & t.plx_ok]
out = {}
for lab, sel in (("faint G>18", t.G > 18), ("mid 17-18", (t.G > 17) & (t.G <= 18)), ("bright G<16.5", t.G < 16.5)):
    S = []
    for sid in t[sel].sdss_id:
        d = np.load(f"store/{sid[-2:]}/{sid}.npz"); a = norm(d["f_8250"].astype(float), d["iv_8250"].astype(float), XC, WIN)
        if a is not None: S.append(a[0])
    out[lab] = (np.nanmedian(np.array(S), axis=0), np.nanmean(np.clip(np.array(S), 0, 2), axis=0), len(S))
fig, ax = plt.subplots(figsize=(12, 4))
for i, (lab, (md, mn, n)) in enumerate(out.items()): ax.plot(WC, md + 0.1 * i, lw=0.8, label=f"{lab} median n={n}")
for l in [8500.35, 8544.44, 8664.52]: ax.axvline(l, color="r", lw=0.4)
for l in [8507.4, 8551.2, 8667.5]: ax.axvline(l, color="b", lw=0.4, ls=":")
ax.legend(fontsize=7); ax.set_xlim(8330, 8830); plt.tight_layout(); plt.savefig("skystack.png", dpi=85)
