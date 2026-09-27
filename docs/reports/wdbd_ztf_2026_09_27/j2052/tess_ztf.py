"""WDJ2052-0324: TESS SPOC PDCSAP (S55 120 s; S81 120 s and 20 s) and ZTF periodograms and folds."""
import glob, numpy as np, pandas as pd, matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
from astropy.io import fits; from astropy.timeseries import LombScargle
fs = sorted(glob.glob("tess/mastDownload/TESS/*/*lc.fits")); fig, ax = plt.subplots(2, 3, figsize=(15, 7)); F0 = 14.7385
res = {}
for i, f in enumerate(fs):
    h = fits.open(f); d = h[1].data; hd = h[1].header; q = (d["QUALITY"] == 0) & np.isfinite(d["PDCSAP_FLUX"])
    t, y, e = d["TIME"][q], d["PDCSAP_FLUX"][q], d["PDCSAP_FLUX_ERR"][q]; y0 = np.nanmedian(y); y, e = y / y0 - 1, e / y0
    fr = np.linspace(1, 60 if "fast" not in f else 200, 400000); ls = LombScargle(t, y, e); p = ls.power(fr); k = np.argmax(p); fb = fr[k]
    X = np.vstack([np.ones_like(t), np.sin(2*np.pi*fb*t), np.cos(2*np.pi*fb*t), np.sin(4*np.pi*fb*t), np.cos(4*np.pi*fb*t)]).T; c = np.linalg.lstsq(X / e[:, None], y / e, rcond=None)[0]
    lab = f.split("/")[-1][:40]; A = np.hypot(c[1], c[2]); A2 = np.hypot(c[3], c[4])
    print(f"{lab}: sector {hd.get('SECTOR', h[0].header.get('SECTOR'))}, n {len(t)}, CROWDSAP {hd.get('CROWDSAP')}, FLFRCSAP {hd.get('FLFRCSAP')}, top {fb:.5f} c/d (P {1440/fb:.2f} min), FAP {ls.false_alarm_probability(p[k]):.1e}, A1 {100*A:.2f}%, A2 {100*A2:.2f}%, median err/pt {100*np.median(e):.1f}%")
    ax[0, i].plot(fr, p, "k", lw=.4); ax[0, i].axvline(F0, color="r", lw=.5, alpha=.5); ax[0, i].set_title(lab, fontsize=7); ax[0, i].set_xlim(0, 60)
    ph = ((t - 3000) * fb) % 1; nb = 40; bb = np.floor(ph * nb).astype(int); m = [np.mean(y[bb == j]) for j in range(nb)]; se = [np.std(y[bb == j]) / np.sqrt((bb == j).sum()) for j in range(nb)]
    ax[1, i].errorbar((np.arange(nb) + .5) / nb, m, se, fmt="k.", ms=3); ax[1, i].errorbar((np.arange(nb) + .5) / nb + 1, m, se, fmt="k.", ms=3)
plt.tight_layout(); plt.savefig("tess.png", dpi=70)
