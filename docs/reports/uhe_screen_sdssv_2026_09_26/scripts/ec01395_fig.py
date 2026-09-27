import os, sys, numpy as np, pandas as pd, warnings, matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt; warnings.filterwarnings("ignore")
sys.path.insert(0, os.path.expanduser("~/claude_projects/sdssv-white-dwarfs-2026/scripts")); import sdssv
from scipy.ndimage import gaussian_filter1d, median_filter
from astropy.timeseries import LombScargle
from astroquery.mast import Tesscut
from astropy.coordinates import SkyCoord
from astropy.wcs import WCS
U = os.path.dirname(os.path.abspath(__file__)); F0 = 2.0229; RA, DEC = 25.28903, -64.61908
fig = plt.figure(figsize=(15, 8.5))
# spectra
R = [(4600, 4740, "4655 feature / He II 4686"), (5170, 5400, "5243 / 5280 features"), (6480, 6650, "H-alpha")]
rows = []
for sid, lab in [("92169356", "EC 01395-6452"), ("59101580", "WDJ0706+6133 (known DA UHE)"), ("74510696", "J0814+0225 (normal hot DAO)")]:
    vs = sdssv.visits(sid)
    if sid == "92169356":
        for v in vs: rows.append((f"{lab} MJD {v['mjd']}", v["wave"], v["flux"], v["ivar"], "C3"))
    use = [v for v in vs if v["in_stack"]] or vs; w, f, iv = sdssv.coadd(use)[:3]; rows.append((lab + (" coadd" if sid == "92169356" else ""), w, f, iv, "C3" if sid == "92169356" else ("C0" if sid == "59101580" else "0.4")))
for j, (a, b, n) in enumerate(R):
    ax = fig.add_axes([0.05 + j * 0.155, 0.08, 0.14, 0.85])
    for i, (lab, w, f, iv, col) in enumerate(rows):
        ok = (iv > 0) & np.isfinite(f) & (w > a - 60) & (w < b + 60); ww, ff = w[ok], f[ok]; c = median_filter(ff, 151, mode="nearest"); k = (ww > a) & (ww < b)
        ax.plot(ww[k], gaussian_filter1d(ff[k] / c[k], 1.5) - 0.13 * i, color=col, lw=.8)
        if j == 0: ax.text(a + 2, 1.035 - 0.13 * i, lab, fontsize=6.5, color=col)
    for l in [4655, 4687.0, 5243, 5280, 6564.6]:
        if a < l < b: ax.axvline(l, color="k", lw=.4, ls=":")
    ax.set_title(n, fontsize=8); ax.set_yticks([]); ax.tick_params(labelsize=7); ax.set_xlabel("vacuum wavelength (Å)", fontsize=7)
# ATLAS
d = pd.read_csv(f"{U}/atlas/EC01395-6452.txt", sep=r"\s+"); d.columns = [c.lstrip("#") for c in d.columns]; d = d[(d.duJy > 0) & (d.err == 0) & (d["chi/N"] < 10)]
ref = 3631e6 * 10 ** (-0.4 * 16.53); ax = fig.add_axes([0.53, 0.56, 0.44, 0.38])
for flt, col in (("c", "C0"), ("o", "C1")):
    s = d[d.F == flt].copy(); s["y"] = np.nan
    for _, g in s.groupby(np.floor((s.MJD - 57000) / 365.25)):
        s.loc[g.index, "y"] = (g.uJy - np.median(g.uJy)) / ref
    s = s[np.abs(s.y) < 0.2]; ph = ((s.MJD - 60000) * F0) % 1; e = np.linspace(0, 1, 21); cc = (e[1:] + e[:-1]) / 2
    m = [np.median(s.y[(ph >= e[i]) & (ph < e[i + 1])]) for i in range(20)]
    ax.plot(np.r_[cc, cc + 1], np.r_[m, m], "o-", color=col, ms=4, label=f"ATLAS {flt} ({len(s)} points, 20 bins)")
ax.set_ylabel("fractional flux"); ax.set_xlabel(f"phase (P = {24 / F0:.3f} h)"); ax.legend(fontsize=7); ax.set_title("EC 01395-6452: ATLAS 2015-2026 folded on 2.0229 c/d", fontsize=8)
# TESS
c = SkyCoord(RA, DEC, unit="deg"); T, Y = [], []
for sec in (68, 69, 96):
    h = Tesscut.get_cutouts(coordinates=c, size=11, sector=sec)[0]; dd = h[1].data; x, y = WCS(h[2].header).world_to_pixel(c); xi, yi = int(round(float(x))), int(round(float(y)))
    q = dd["QUALITY"] == 0; fl = dd["FLUX"][q]; t = dd["TIME"][q]; yy, xx = np.mgrid[0:fl.shape[1], 0:fl.shape[2]]
    bg = np.nanmedian(fl[:, (np.abs(xx - xi) > 2) | (np.abs(yy - yi) > 2)], axis=1); ap = (np.abs(xx - xi) <= 1) & (np.abs(yy - yi) <= 1)
    lc = np.nansum(fl[:, ap], axis=1) - bg * ap.sum(); ok = np.isfinite(lc); t, lc = t[ok], lc[ok]; r = lc / np.median(lc) - 1; r = r - median_filter(r, size=int(1 / np.median(np.diff(t))) | 1, mode="nearest")
    s = 1.4826 * np.median(np.abs(r)); m = np.abs(r) < 5 * s; T += list(t[m]); Y += list(r[m])
T, Y = np.array(T), np.array(Y); fr = np.arange(0.2, 10, 0.0005); p = LombScargle(T, Y).power(fr)
ax2 = fig.add_axes([0.53, 0.08, 0.2, 0.36]); ax2.plot(fr, p, "k", lw=.6); ax2.axvline(F0, color="C3", lw=.6, ls=":"); ax2.set_xlabel("frequency (c/d)", fontsize=8); ax2.set_title("TESS sectors 68, 69, 96: periodogram", fontsize=8); ax2.tick_params(labelsize=7)
ax3 = fig.add_axes([0.77, 0.08, 0.2, 0.36]); ph = ((T + 2457000 - 2460000) * F0) % 1; e = np.linspace(0, 1, 21); cc = (e[1:] + e[:-1]) / 2
m = [np.median(Y[(ph >= e[i]) & (ph < e[i + 1])]) for i in range(20)]; ax3.plot(np.r_[cc, cc + 1], np.r_[m, m], "o-", color="C2", ms=4)
ax3.set_xlabel("phase", fontsize=8); ax3.set_title("TESS folded (aperture flux, 20 bins)", fontsize=8); ax3.tick_params(labelsize=7)
plt.savefig(f"{U}/ec01395_uhe.png", dpi=100)
