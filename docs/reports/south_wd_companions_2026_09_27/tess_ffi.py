"""TESS FFI cutouts (7x7 px): 2x2 central aperture minus median-of-outer-ring background per cadence, quality 0; per-sector Lomb-Scargle
2-60 c/d after removing a 1-day running median; joint periodogram of all sectors (per-sector normalised) and value at the Gaia frequency."""
import sys, glob, numpy as np, matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
from astropy.io import fits; from astropy.timeseries import LombScargle; from scipy.ndimage import median_filter
g, fg = sys.argv[1], float(sys.argv[2]); fs = sorted(glob.glob(f"tess/{g}/*astrocut.fits")); fr = np.linspace(2, 60, 300000)
T, Y = [], []; fig, ax = plt.subplots(len(fs) + 1, 1, figsize=(10, 1.6 * (len(fs) + 1)))
for a, f in zip(ax, fs):
    h = fits.open(f); d = h[1].data; t = d["TIME"]; F = d["FLUX"]; q = d["QUALITY"]
    ok = (q == 0) & np.isfinite(t) & np.all(np.isfinite(F.reshape(len(F), -1)), axis=1); t, F = t[ok], F[ok]
    ring = np.ones((7, 7), bool); ring[1:6, 1:6] = False; bkg = np.median(F[:, ring], axis=1); ap = F[:, 2:5, 2:5].sum(axis=(1, 2)) - 9 * bkg
    dt = np.median(np.diff(t)); w = max(int(1.0 / dt) | 1, 3); y = ap - median_filter(ap, w, mode="nearest"); y = y / np.std(y)
    cl = np.abs(y) < 5; t, y = t[cl], y[cl]; p = LombScargle(t, y).power(fr); k = np.argmax(p); j = np.argmin(np.abs(fr - fg))
    print(f"{f.split('/')[-1][:14]}: n {len(t)}, cadence {dt*1440:.1f} min, top {fr[k]:.4f} c/d (power {p[k]:.4f}, FAP {LombScargle(t, y).false_alarm_probability(p[k]):.1e}); power at Gaia f {p[j]:.4f}")
    a.plot(fr, p, "k", lw=.3); a.axvline(fg, color="r", lw=.5, alpha=.5); a.set_xlim(2, 60); T.append(t); Y.append(y)
t = np.concatenate(T); y = np.concatenate(Y); ls = LombScargle(t, y); fz = np.linspace(fg - 0.2, fg + 0.2, 40001); pz = ls.power(fz); pa = ls.power(fr)
k = np.argmax(pa); print(f"joint: top {fr[k]:.5f} c/d (power {pa[k]:.5f}, FAP {ls.false_alarm_probability(pa[k]):.1e}); best within 0.2 of Gaia: {fz[np.argmax(pz)]:.5f} (power {pz.max():.5f})")
ax[-1].plot(fr, pa, "k", lw=.3); ax[-1].axvline(fg, color="r", lw=.5, alpha=.5); ax[-1].set_xlim(2, 60); ax[-1].set_title("joint", fontsize=7)
plt.tight_layout(); plt.savefig(f"tess_{g}.png", dpi=70)
