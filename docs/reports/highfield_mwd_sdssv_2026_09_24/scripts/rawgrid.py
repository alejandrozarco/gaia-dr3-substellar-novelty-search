# Raw (flux-calibrated) spectra of candidates, smoothed, with the fitted continuum overplotted, to judge whether broad
# "troughs" are genuine or normalisation artefacts. usage: python rawgrid.py <candfile> <out-prefix>
import sys, numpy as np, pandas as pd, spec as S
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
from scipy.ndimage import gaussian_filter1d
X = pd.read_csv("cands_info.csv")
rows = list(X.itertuples())
for k in range(0, len(rows), 10):
    fig, axs = plt.subplots(5, 2, figsize=(18, 13)); 
    for a, r in zip(axs.flat, rows[k:k + 10]):
        s = S.load_star(r.sid); lam, f, iv = s["lam"], s["flux"], s["ivar"]; c = S.continuum(lam, f, iv)
        m = (lam > 3600) & (lam < 10000) & (iv > 0)
        a.plot(lam[m], gaussian_filter1d(f, 3)[m], "k", lw=0.5); a.plot(lam, c, "r", lw=0.8)
        a.plot(lam[m], gaussian_filter1d(s["nmf"] * s["cont"], 3)[m] if np.nanmax(s["cont"]) > 0 else np.zeros(m.sum()), "c", lw=0.5, alpha=0.6)
        top = np.nanpercentile(gaussian_filter1d(f, 3)[m], 99.5); a.set_ylim(min(0, np.nanpercentile(f[m], 1)), top * 1.25)
        a.set_title(f"{r.sid} G{r.gaia} | {r.cls} S/N {r.snr} | G {r.G:.1f} MG {r.MG} | {r.note} | MWDD {r.mwdd}", fontsize=8, loc="left")
        for l0 in (6564.61, 4862.68, 4341.69, 4102.89): a.axvline(l0, color="tab:blue", ls=":", lw=0.6)
        a.tick_params(labelsize=7)
    plt.tight_layout(); plt.savefig(f"plots/{sys.argv[1]}_{k // 10}.png", dpi=70); plt.close(fig)
print("ok")
