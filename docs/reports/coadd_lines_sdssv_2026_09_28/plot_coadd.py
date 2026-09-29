"""Full-range coadd plots from coadd_store with line markers. Usage: python plot_coadd.py id1,id2,... [outdir]"""
import os, sys, numpy as np, matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
from scipy.ndimage import gaussian_filter1d
D = os.path.dirname(os.path.abspath(__file__)); G = np.load(os.path.join(D, "coadd_grid.npy")); out = sys.argv[2] if len(sys.argv) > 2 else os.path.join(D, "plots_coadd"); os.makedirs(out, exist_ok=True)
LINES = {"Hd": 4102.9, "Hg": 4341.7, "HeI4471": 4472.7, "HeII4686": 4687.0, "Hb": 4862.7, "HeI5016": 5017.1, "HeII5412": 5413.0, "HeI5876": 5877.2, "NaD": 5893.0, "Ha": 6564.6, "HeI6678": 6679.9, "HeI7065": 7067.1, "CaT": 8544.4}
import pandas as pd; T = pd.read_csv(os.path.join(D, "targets.csv"), dtype={"sdss_id": str}).set_index("sdss_id")
for sid in sys.argv[1].split(","):
    p = os.path.join(D, "coadd_store", sid[-2:], f"{sid}.npz")
    if not os.path.exists(p): print("no coadd", sid); continue
    d = np.load(p); f = d["f"].astype(float); iv = d["iv"].astype(float); ok = (iv > 0) & np.isfinite(f)
    fig, ax = plt.subplots(2, 1, figsize=(12, 7)); ax[0].plot(G[ok], gaussian_filter1d(f[ok], 1.5), "k", lw=0.6); ax[0].set_xlim(3700, 9300); ax[0].set_ylabel("flux")
    ax[0].set_title(f"sdss_id {sid}  Gaia DR3 {T.loc[sid].gaia_dr3_source_id if sid in T.index else ''}  {T.loc[sid].classification if sid in T.index else ''}  G {T.loc[sid].g_mag if sid in T.index else ''}  n_vis {int(d['n_vis'])}  S/N {np.nanmedian(d['snr']):.0f}", fontsize=9)
    for k, lam in LINES.items(): ax[0].axvline(lam, color="C3" if "He" in k else "C0", lw=0.4, alpha=0.6); ax[0].text(lam, ax[0].get_ylim()[1] * 0.97, k, rotation=90, fontsize=6, va="top")
    m = ok & (G > 4300) & (G < 5100); ax[1].plot(G[m], gaussian_filter1d(f[m], 1.0), "k", lw=0.7); ax[1].set_xlim(4300, 5100); ax[1].set_xlabel("wavelength (A)"); ax[1].set_ylabel("flux (4300-5100)")
    for k, lam in LINES.items():
        if 4300 < lam < 5100: ax[1].axvline(lam, color="C3" if "He" in k else "C0", lw=0.4, alpha=0.6)
    fig.tight_layout(); fig.savefig(os.path.join(out, f"{sid}.png"), dpi=100); plt.close(fig); print("plot", sid)
