import sys, numpy as np, matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
import carbon_screen as cs
from scipy.ndimage import percentile_filter, gaussian_filter1d
sid, v0, label = sys.argv[1], float(sys.argv[2]), sys.argv[3] if len(sys.argv) > 3 else ""
vis = cs.load(sid)
num = np.nansum([v["f"] * v["iv"] for v in vis], axis=0); den = np.sum([v["iv"] for v in vis], axis=0)
f = np.where(den > 0, num / np.where(den > 0, den, 1), np.nan)
def norm(f):
    m = np.isfinite(f); ff = np.interp(np.arange(len(cs.grid)), np.where(m)[0], f[m])
    npix = int(round(np.log10(1 + 150 / 5000) / 6e-5)); cont = gaussian_filter1d(percentile_filter(ff, 85, size=npix), npix / 3)
    return gaussian_filter1d(ff / cont, 1.0)
zooms = [(3880, 4130), (4200, 4420), (4700, 5100), (5100, 5420), (5950, 6100), (6480, 6680), (7050, 7300), (8250, 8400)]
fig = plt.figure(figsize=(15, 10)); gs = fig.add_gridspec(3, 4)
ax = fig.add_subplot(gs[0, :]); n = norm(f); ax.plot(cs.grid, n, "k-", lw=0.6)
for sp, col in (("C I", "tab:red"), ("C II", "tab:blue")):
    for lam in cs.LINES[sp]: ax.axvline(lam * (1 + v0 / cs.C), color=col, lw=0.6, alpha=0.6)
for b in cs.BALMER: ax.axvline(b, color="tab:green", ls=":", lw=0.8)
ax.set_xlim(3850, 9200); ax.set_ylim(0.3, 1.25); ax.set_title(f"{label} sdss_id {sid}  coadd of {len(vis)} visits; carbon lines at {v0:+.0f} km/s (red C I, blue C II, green Balmer)")
for i, (a, b) in enumerate(zooms):
    axz = fig.add_subplot(gs[1 + i // 4, i % 4]); m = (cs.grid > a) & (cs.grid < b)
    axz.plot(cs.grid[m], n[m], "k-", lw=0.8)
    for k, v in enumerate(vis):
        nv = norm(v["f"]); axz.plot(cs.grid[m], nv[m] + 0.25 * (k + 1), lw=0.5, alpha=0.7)
    for sp, col in (("C I", "tab:red"), ("C II", "tab:blue")):
        for lam in cs.LINES[sp]:
            x = lam * (1 + v0 / cs.C)
            if a < x < b: axz.axvline(x, color=col, lw=0.7)
    for bb in cs.BALMER:
        if a < bb < b: axz.axvline(bb, color="tab:green", ls=":", lw=0.8)
    axz.set_xlim(a, b)
fig.tight_layout(); fig.savefig(f"vet_{sid}.png", dpi=80); print(f"vet_{sid}.png")
