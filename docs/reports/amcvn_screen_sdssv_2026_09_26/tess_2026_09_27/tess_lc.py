"""CRTS J2054-5418: TESS FFI cutout light curves (11x11 px). Aperture = central 3x3 px; background = median of the outer ring, per cadence.
Outburst test: any stretch of >= 6 cadences with aperture excess > 5 sigma above the sector median, centred on the target pixel."""
import glob, numpy as np, matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
from astropy.io import fits
fs = sorted(glob.glob("tess-s*_astrocut.fits")); fig, ax = plt.subplots(len(fs), 1, figsize=(11, 2.0 * len(fs)))
for a, f in zip(ax, fs):
    h = fits.open(f); d = h[1].data; t = d["TIME"]; F = d["FLUX"]; q = d["QUALITY"]
    ok = (q == 0) & np.isfinite(t) & np.all(np.isfinite(F.reshape(len(F), -1)), axis=1); t, F = t[ok], F[ok]
    ring = np.ones((11, 11), bool); ring[2:9, 2:9] = False
    bkg = np.median(F[:, ring], axis=1); ap = F[:, 4:7, 4:7].sum(axis=(1, 2)) - 9 * bkg
    med = np.median(ap); rms = 1.4826 * np.median(np.abs(ap - med)); z = (ap - med) / rms
    # runs of high z
    hi = z > 5; runs = []; i = 0
    while i < len(hi):
        if hi[i]:
            j = i
            while j < len(hi) and hi[j]: j += 1
            if j - i >= 6: runs.append((t[i], t[j - 1], j - i, z[i:j].max()))
            i = j
        else: i += 1
    sec = h[0].header.get("SECTOR"); dt = np.median(np.diff(t)) * 1440
    print(f"S{sec}: BTJD {t.min():.2f}-{t.max():.2f} (MJD {t.min()+57000-0.5:.1f}-{t.max()+57000-0.5:.1f}), cadence {dt:.1f} min, n {len(t)}, median ap {med:.1f} e/s, robust rms {rms:.1f}, runs>5sig(>=6 cad): {runs[:5]}")
    a.plot(t, ap, "k.", ms=1); a.set_ylabel(f"S{sec} e/s", fontsize=7)
plt.tight_layout(); plt.savefig("tess_lc.png", dpi=70)
