import sys, io, gzip, requests, numpy as np, matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
from astropy.io import fits
sys.path.insert(0, "/tmp/hotdq/lane_daq"); import carbon_screen as cs
from scipy.ndimage import percentile_filter, gaussian_filter1d
ob, v0, lab = sys.argv[1], float(sys.argv[2]), sys.argv[3]
raw = requests.get(f"https://www.lamost.org/dr11/v1.1/spectrum/fits/{ob}", timeout=120).content
if len(raw) < 5000: raw = requests.get(f"https://www.lamost.org/dr11/v2.0/spectrum/fits/{ob}", timeout=120).content
d = fits.open(io.BytesIO(gzip.decompress(raw) if raw[:2] == b"\x1f\x8b" else raw))[1].data[0]
w = np.array(d["WAVELENGTH"]); f = np.array(d["FLUX"]); ok = (np.array(d["IVAR"]) > 0) & (d["ANDMASK"] == 0)
fg = np.interp(cs.grid, w[ok], f[ok]); n = int(round(np.log10(1 + 150 / 5000) / 6e-5)); nf = gaussian_filter1d(fg / gaussian_filter1d(percentile_filter(fg, 85, size=n), n / 3), 1.0)
fig = plt.figure(figsize=(15, 9)); gs = fig.add_gridspec(3, 4); ax = fig.add_subplot(gs[0, :]); ax.plot(cs.grid, nf, "k", lw=0.6)
for sp, col in (("C I", "tab:red"), ("C II", "tab:blue"), ("He I", "tab:orange")):
    for lam in cs.LINES[sp]: ax.axvline(lam * (1 + v0 / cs.C), color=col, lw=0.6, alpha=0.6)
ax.set_xlim(3850, 9000); ax.set_ylim(0.3, 1.25); ax.set_title(f"{lab} LAMOST obsid {ob}; C I red, C II blue, He I orange at {v0:+.0f} km/s")
for i, (a, b) in enumerate([(3880, 4130), (4200, 4500), (4650, 5100), (5100, 5420), (5800, 6100), (6480, 6700), (7050, 7300), (8250, 8400)]):
    x = fig.add_subplot(gs[1 + i // 4, i % 4]); m = (cs.grid > a) & (cs.grid < b); x.plot(cs.grid[m], nf[m], "k", lw=0.8)
    for sp, col in (("C I", "tab:red"), ("C II", "tab:blue"), ("He I", "tab:orange")):
        for lam in cs.LINES[sp]:
            if a < lam * (1 + v0 / cs.C) < b: x.axvline(lam * (1 + v0 / cs.C), color=col, lw=0.7)
    x.set_xlim(a, b)
fig.tight_layout(); fig.savefig(f"lvet_{ob}.png", dpi=70); print(f"lvet_{ob}.png")
