"""Eclipse search in TESS 20-s PDCSAP light curves: fold on the known frequency (refined per object), 300 phase bins; report the deepest
bin relative to the local (+-0.05 phase) median in units of its error, after subtracting a 2-harmonic sinusoid."""
import sys, glob, numpy as np, matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
from astropy.io import fits; from astropy.timeseries import LombScargle
pat, f0, out = sys.argv[1], float(sys.argv[2]), sys.argv[3]; T, Y, E = [], [], []
for f in sorted(glob.glob(pat)):
    d = fits.open(f)[1].data; q = (d["QUALITY"] == 0) & np.isfinite(d["PDCSAP_FLUX"]); t = d["TIME"][q]; y = d["PDCSAP_FLUX"][q]; e = d["PDCSAP_FLUX_ERR"][q]
    m = np.median(y); T.append(t); Y.append(y / m - 1); E.append(e / m)
t, y, e = map(np.concatenate, (T, Y, E)); fr = np.linspace(f0 - 0.002, f0 + 0.002, 4001); f = fr[np.argmax(LombScargle(t, y, e).power(fr))]
X = np.vstack([np.ones_like(t)] + [fn(2 * np.pi * k * f * t) for k in (1, 2) for fn in (np.sin, np.cos)]).T; c = np.linalg.lstsq(X / e[:, None], y / e, rcond=None)[0]; r = y - X @ c
ph = (t * f) % 1; nb = 300; b = np.floor(ph * nb).astype(int); mb = np.array([np.mean(r[b == k]) for k in range(nb)]); sb = np.array([np.std(r[b == k]) / np.sqrt((b == k).sum()) for k in range(nb)])
z = mb / sb; k = np.argmin(z); print(f"{out}: f {f:.6f}, n {len(t)}, bin width {1440/f/nb:.2f} min, bin error ~{100*np.median(sb):.2f}%, deepest bin {100*mb[k]:+.2f}% ({z[k]:.1f} sigma) at phase {(k+.5)/nb:.3f}; rms of bin z {np.std(z):.2f}")
plt.figure(figsize=(10, 3)); plt.errorbar((np.arange(nb) + .5) / nb, 100 * mb, 100 * sb, fmt="k.", ms=2); plt.ylabel("residual %"); plt.title(out, fontsize=8); plt.tight_layout(); plt.savefig(out + "_eclipse.png", dpi=70)
