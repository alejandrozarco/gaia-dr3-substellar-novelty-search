"""Plot stored CaT (8250-8950 A) and H-alpha regions for a list of sdss_ids: python plot_cat.py out.png sid1 sid2 ..."""
import sys, numpy as np, matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt, pandas as pd
from scipy.ndimage import gaussian_filter1d
GRID = 10 ** np.arange(np.log10(3850), np.log10(9250), 6e-5)
CAT = [8500.35, 8544.44, 8664.52]; OI = [8448.7, 7774.1]
lab = pd.read_csv("sw_all.csv", dtype=str).set_index("sdss_id")
ids = sys.argv[2:]; fig, ax = plt.subplots(len(ids), 2, figsize=(13, 2.1 * len(ids)), gridspec_kw=dict(width_ratios=[2, 1]))
ax = np.atleast_2d(ax)
for i, sid in enumerate(ids):
    d = np.load(f"store/{sid[-2:]}/{sid}.npz")
    for j, (a, b) in enumerate([(8250, 8950), (6400, 6750)]):
        m = (GRID > a) & (GRID < b); w = GRID[m]; f = d[f"f_{a}"]; iv = d[f"iv_{a}"]; ok = iv > 0
        fs = gaussian_filter1d(np.where(ok, f, np.nanmedian(f[ok])), 1.5)
        ax[i, j].plot(w, fs / np.nanmedian(fs[ok]), "k", lw=0.7)
        for L in (CAT + [8448.7] if j == 0 else [6564.61]): ax[i, j].axvline(L, color="r", lw=0.5, alpha=0.5)
        if d[f"vf_{a}"].shape[0] > 1:
            for vf in d[f"vf_{a}"]:
                vs = gaussian_filter1d(np.nan_to_num(vf), 2); ax[i, j].plot(w, vs / np.nanmedian(vs) , lw=0.4, alpha=0.4)
        ax[i, j].set_ylim(0.6, 1.6 if j == 0 else 1.5)
    r = lab.loc[sid]; ax[i, 0].set_title(f"{sid} Gaia {r.gaia_dr3_source_id} {r.classification} Teff {float(r.teff):.0f} S/N {float(r.snr):.0f} G {float(r.g_mag):.2f}", fontsize=8)
plt.tight_layout(); plt.savefig(sys.argv[1], dpi=90)
