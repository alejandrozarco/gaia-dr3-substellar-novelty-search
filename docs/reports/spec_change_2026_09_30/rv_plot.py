"""Line-core plots for radial-velocity candidates (2026-09-30): every spectrum of the star in the SDSS DR17 / DESI DR1 stores,
normalised by a linear continuum at +-(45-70) A, H-alpha, H-beta, H-gamma in velocity space, with the rv_fit.py centre of each
spectrum marked. Usage: python rv_plot.py <gaia> [...] -> results/rv_<gaia>.png"""
import os, sys, glob, numpy as np, pandas as pd, matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
H = os.path.dirname(os.path.abspath(__file__)); ST = os.path.expanduser("~/claude_projects/spectra_store"); C = 299792.458
L = {"Ha": 6564.61, "Hb": 4862.68, "Hg": 4341.69}; F = pd.read_csv(os.path.join(H, "results", "rv_fit_spectra.csv"), dtype={"gaia": str})
gs = np.load(os.path.join(ST, "sdss_dr17_wd", "grid.npy")); gd = np.load(os.path.join(ST, "desi_dr1_wd", "grid.npy"))
for g in sys.argv[1:]:
    S = F[F.gaia == g]; spec = {}
    for fn in sorted(glob.glob(os.path.join(ST, "sdss_dr17_wd", "chunks", "*.npz"))):
        d = np.load(fn, allow_pickle=True)
        for s_, gg, f, iv in zip(d["sparcl_id"], d["gaia"], d["f"], d["iv"]):
            if str(gg) == g: spec["S:" + str(s_)] = (gs, f)
    Ct = pd.read_csv(os.path.join(ST, "desi_dr1_wd", "class_table.csv"), dtype={"edr3id": str}); tids = set(Ct[Ct.edr3id == g].DESIID.astype(np.int64))
    for fn in sorted(glob.glob(os.path.join(ST, "desi_dr1_wd", "chunks", "*.npz"))):
        d = np.load(fn, allow_pickle=True)
        for t, f, iv in zip(d["targetid"], d["f"], d["iv"]):
            if int(t) in tids: spec[f"D:{int(t)}"] = (gd, f)
    fig, ax = plt.subplots(1, 3, figsize=(15, 4))
    for k, (ln, l0) in enumerate(L.items()):
        for lab, (w, f) in spec.items():
            m = (w > l0 - 75) & (w < l0 + 75); x, y = w[m], np.asarray(f, float)[m]
            c1 = (x > l0 - 70) & (x < l0 - 45); c2 = (x > l0 + 45) & (x < l0 + 70)
            if c1.sum() < 3 or c2.sum() < 3: continue
            cont = np.median(y[c1]) + (np.median(y[c2]) - np.median(y[c1])) * (x - np.median(x[c1])) / (np.median(x[c2]) - np.median(x[c1]))
            ln_ = ax[k].plot(C * (x / l0 - 1), np.convolve(y / cont, np.ones(3) / 3, "same"), lw=0.8, label=f"{lab[:12]} S/N {S[S.spec == lab].sn.values[0]:.0f}" if (S.spec == lab).any() else lab[:12])
            r = S[S.spec == lab]
            if len(r) and np.isfinite(r[f"mu_{ln}"].values[0]): ax[k].axvline(C * (r[f"mu_{ln}"].values[0] / l0 - 1), color=ln_[0].get_color(), ls="--", lw=0.8)
        ax[k].set_xlim(-2500, 2500); ax[k].set_title(ln); ax[k].set_xlabel("km/s")
    ax[0].legend(fontsize=7); fig.suptitle(f"Gaia DR3 {g}"); plt.tight_layout(); plt.savefig(os.path.join(H, "results", f"rv_{g}.png"), dpi=70); plt.close()
    print(g, list(spec))
