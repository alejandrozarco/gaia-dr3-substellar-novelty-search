"""WDJ094809.07-280038.55 (TIC 875311151): TESS SPOC 120-s PDCSAP light curves (sectors 35, 62, 89); quality 0; 5-sigma clip; no further detrending.
Lomb-Scargle 0.2-10 c/d per sector and combined; semi-amplitude at the Gaia+ZTF frequency 2.169994 c/d. CROWDSAP from the header."""
import os, numpy as np, warnings; warnings.filterwarnings("ignore")
from astropy.io import fits; from astroquery.mast import Observations; from astropy.timeseries import LombScargle
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
F0 = 2.169994; C = "cache"; os.makedirs(C, exist_ok=True)
o = Observations.query_criteria(target_name="875311151", obs_collection="TESS", dataproduct_type="timeseries"); o = o[o["t_exptime"] == 120]
pl = Observations.get_product_list(o); pl = pl[[x.endswith("_lc.fits") and "fast" not in x for x in pl["productFilename"]]]
paths = Observations.download_products(pl, download_dir=C)["Local Path"]; FR = np.linspace(0.2, 10, 200000); T, Y = [], []
fig, ax = plt.subplots(1, 2, figsize=(13, 3.6))
for p in sorted(paths):
    h = fits.open(p); d = h[1].data; q = (d["QUALITY"] == 0) & np.isfinite(d["PDCSAP_FLUX"]); t = d["TIME"][q] + 2457000.0; f = d["PDCSAP_FLUX"][q]; y = f / np.nanmedian(f) - 1
    s = 1.4826 * np.median(np.abs(y)); k = np.abs(y) < 5 * s; t, y = t[k], y[k]; ls = LombScargle(t, y); pw = ls.power(FR); i = np.argmax(pw)
    X = np.vstack([np.sin(2 * np.pi * F0 * t), np.cos(2 * np.pi * F0 * t), np.ones_like(t)]).T; c = np.linalg.lstsq(X, y, rcond=None)[0]; r = y - X @ c
    ea = np.std(r) * np.sqrt(2 / len(t)); w = np.abs(FR - F0) < 0.05
    print(f"S{h[0].header['SECTOR']}: n {len(t)}, CROWDSAP {h[1].header.get('CROWDSAP')}, point rms {100 * np.std(y):.1f}%, peak {FR[i]:.4f} c/d FAP {ls.false_alarm_probability(pw[i], minimum_frequency=0.2, maximum_frequency=10):.2g}, "
          f"near Gaia {FR[w][np.argmax(pw[w])]:.4f} FAP {ls.false_alarm_probability(pw[w].max(), minimum_frequency=0.2, maximum_frequency=10):.2g}, semi-amp at F0 {100 * np.hypot(c[0], c[1]):.2f} +- {100 * ea:.2f}%")
    T.append(t); Y.append(y)
t, y = np.concatenate(T), np.concatenate(Y); ls = LombScargle(t, y); pw = ls.power(FR); i = np.argmax(pw); w = np.abs(FR - F0) < 0.02
print(f"ALL: peak {FR[i]:.5f} c/d FAP {ls.false_alarm_probability(pw[i], minimum_frequency=0.2, maximum_frequency=10):.2g}; near Gaia {FR[w][np.argmax(pw[w])]:.5f} FAP {ls.false_alarm_probability(pw[w].max(), minimum_frequency=0.2, maximum_frequency=10):.2g}")
ax[0].plot(FR, pw, "k", lw=.5); ax[0].axvline(F0, color="b", ls=":"); ax[0].set_xlabel("frequency (c/d)")
ph = ((t - 2459000.0) * F0) % 1; bn = np.linspace(0, 1, 21); ax[1].plot((bn[:-1] + bn[1:]) / 2, [np.mean(y[(ph >= a) & (ph < b)]) for a, b in zip(bn[:-1], bn[1:])], "ko")
ax[1].set_xlabel(f"phase (f = {F0} c/d)"); ax[1].set_ylabel("PDCSAP relative flux"); fig.suptitle("TIC 875311151 = WDJ094809.07-280038.55, TESS 120 s", fontsize=9); plt.tight_layout(); plt.savefig("j0948_tess_spoc.png", dpi=90)
