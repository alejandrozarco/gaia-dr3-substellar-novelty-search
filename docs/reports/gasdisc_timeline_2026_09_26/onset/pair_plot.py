"""SDSS-V visits vs DESI/SDSS spectra (SPARCL) in the Ca II triplet region, GE.norm normalisation, for given sdss_id/gaia pairs.
python pair_plot.py <out.png> <name:gaia:sdss_id> ..."""
import os
import sys, numpy as np, matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
sys.path.insert(0, os.path.expanduser("~/claude_projects/sdssv-white-dwarfs-2026/scripts")); import gas_disc_epochs as GE
sys.path.insert(0, "/tmp/hotdq/lane_gastime"); import gas_disc_timeline as TL
from scipy.ndimage import gaussian_filter1d
items = [a.split(":") for a in sys.argv[2:]]; pos = TL.gaia_pos([g for _, g, _ in items])
fig, ax = plt.subplots(len(items), 2, figsize=(13, 4 * len(items)), squeeze=False)
for i, (n, g, sid) in enumerate(items):
    ra, dec = float(pos.loc[g].ra), float(pos.loc[g].dec)
    co, per = GE.sdssv_spectra(sid)
    for _k in range(5):
        try: sp = GE.sparcl_spectra(ra, dec); break
        except Exception: import time; time.sleep(20); sp = []
    for k, s in enumerate(sorted(per + sp, key=lambda s: s["mjd"])):
        nn, v = GE.norm(s["w"], s["f"], s["iv"]); ok = (v > 0) & np.isfinite(nn)
        if ok.sum() < 100: continue
        ew, e, _, _ = GE.measure(nn, v, np.zeros(len(GE.W)))
        m = ok & (GE.W > 8440) & (GE.W < 8720)
        ax[i, 0].plot(GE.W[m], gaussian_filter1d(nn[m], 2) + 0.25 * k, lw=.7); ax[i, 0].text(8722, 1 + 0.25 * k, f"{s['dataset'][:12]} {s['date']} {ew:.1f}+-{e:.1f}", fontsize=6)
    for l in GE.CAT: ax[i, 0].axvline(l, color="r", lw=.4)
    ax[i, 0].set_title(f"{n} (Gaia DR3 {g})", fontsize=9); ax[i, 0].set_xlim(8440, 8800)
    # H-alpha region of the SDSS-V coadd
    nn = co["f"]; w = co["w"]; m = (w > 6450) & (w < 6680) & (co["iv"] > 0)
    ax[i, 1].plot(w[m], gaussian_filter1d(nn[m] / np.median(nn[m]), 2), "k", lw=.7); ax[i, 1].axvline(6564.6, color="r", lw=.4); ax[i, 1].set_title("SDSS-V coadd H-alpha", fontsize=9)
plt.tight_layout(); plt.savefig(sys.argv[1], dpi=80)
