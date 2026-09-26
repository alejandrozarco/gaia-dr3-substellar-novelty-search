"""Figure: Ca II triplet of one object at every epoch (SDSS-V visits binned by season, SPARCL archival spectra), 4 A bins."""
import sys, glob, numpy as np, matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
sys.argv = [sys.argv[0]] + sys.argv[1:]
from epoch_amp import norm, W, CAT, C
sid, lab, title = sys.argv[1], sys.argv[2], sys.argv[3]
d = np.load(f"store/{sid[-2:]}/{sid}.npz")
labels = eval(sys.argv[4]) if len(sys.argv) > 4 else {}
rows = [(f"SDSS-V coadd ({len(d['mjd'])} visits {min(d['mjd'])}-{max(d['mjd'])})",) + norm(W, d["f_8250"], d["iv_8250"])]
for k in range(len(d["mjd"])): rows.append((f"SDSS-V MJD {d['mjd'][k]}",) + norm(W, d["vf_8250"][k], d["viv_8250"][k]))
for fn in sorted(glob.glob(f"desi_{lab}_*.npz")): rows.append((labels.get(fn, fn),) + norm(*[np.load(fn)[x] for x in ("w", "f", "iv")]))
e = np.arange(8340, 8830, 4.0); c = 0.5 * (e[1:] + e[:-1])
fig, ax = plt.subplots(figsize=(10, 1.5 + 0.55 * len(rows)))
for i, (name, n, v) in enumerate(rows):
    k = np.digitize(W, e) - 1; ok = (k >= 0) & (k < len(c)) & (v > 0) & np.isfinite(n)
    num = np.bincount(k[ok], (n * v)[ok], len(c)); den = np.bincount(k[ok], v[ok], len(c))
    y = np.where(den > 0, num / np.where(den > 0, den, 1), np.nan); off = -0.45 * i
    ax.plot(c, y + off, color="k" if i == 0 else f"C{i % 10}", lw=1.0 if i == 0 else 0.8, drawstyle="steps-mid"); ax.text(8835, 1 + off, name, fontsize=7, va="center")
for l in CAT: ax.axvline(l, color="r", lw=0.5, alpha=0.6)
ax.set_xlim(8340, 8830); ax.set_xlabel("vacuum wavelength (A)"); ax.set_ylabel("normalised flux + offset"); ax.set_title(title, fontsize=9)
plt.subplots_adjust(right=0.72); plt.savefig(f"epochs_{lab}.png", dpi=90)
