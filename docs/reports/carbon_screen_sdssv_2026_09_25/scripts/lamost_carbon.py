"""Carbon template test (carbon_screen2 method) on the LAMOST DR10 LRS spectrum of 883885440381808000 (obsid 8002245, 2011-11-24),
and a side-by-side plot with the SDSS-V visit (sdss_id 57623143, 2025)."""
import sys, numpy as np, matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
from astropy.io import fits
sys.path.insert(0, "/tmp/hotdq/lane_daq")
import carbon_screen as cs, carbon_screen2 as c2
from scipy.ndimage import percentile_filter, gaussian_filter1d
h = fits.open("spec-55890-GAC_106N28_M1_sp02-245.fits.gz"); d = h[1].data[0]
w = np.array(d["WAVELENGTH"], float); f = np.array(d["FLUX"], float); iv = np.array(d["IVAR"], float)
ok = (iv > 0) & np.isfinite(f) & (d["ANDMASK"] == 0)
fg = np.interp(cs.grid, w[ok], f[ok], left=np.nan, right=np.nan); ivg = np.interp(cs.grid, w[ok], iv[ok], left=0, right=0)
p = c2.prep(fg, ivg)
for sp in ("C", "C I", "C II", "He I"):
    c = c2.contrast(*p, sp); k = int(np.argmax(np.where(c2.INW, c, -99))); kk = int(np.argmax(c))
    print(f"LAMOST {sp:5s}: contrast {c[k]:.2f} at {cs.vels[k]:+.0f} km/s (prior window); global max {c[kk]:.2f} at {cs.vels[kk]:+.0f}")
# fixed velocity (SDSS-V value +110 km/s)
k0 = int(np.argmin(np.abs(cs.vels - 110)))
for sp in ("C", "C I", "C II"): print(f"LAMOST {sp} contrast at SDSS-V velocity +110: {c2.contrast(*p, sp)[k0]:.2f}")
vis = cs.load("57623143"); s = vis[0]
def norm(f):
    m = np.isfinite(f); ff = np.interp(np.arange(len(cs.grid)), np.where(m)[0], f[m])
    npix = int(round(np.log10(1 + 150 / 5000) / 6e-5)); cont = gaussian_filter1d(percentile_filter(ff, 85, size=npix), npix / 3)
    return gaussian_filter1d(ff / cont, 1.2)
nl, ns = norm(fg), norm(s["f"])
zooms = [(3880, 4130), (4200, 4420), (4700, 5100), (5100, 5420), (5850, 6100), (6480, 6680), (7050, 7300), (8250, 8400)]
fig, axs = plt.subplots(2, 4, figsize=(15, 7))
for ax, (a, b) in zip(axs.flat, zooms):
    m = (cs.grid > a) & (cs.grid < b)
    ax.plot(cs.grid[m], ns[m], "k-", lw=0.8, label="SDSS-V 2025"); ax.plot(cs.grid[m], nl[m] + 0.3, "tab:purple", lw=0.8, label="LAMOST 2011 (+0.3)")
    for sp, col in (("C I", "tab:red"), ("C II", "tab:blue")):
        for lam in cs.LINES[sp]:
            x = lam * (1 + 110 / cs.C)
            if a < x < b: ax.axvline(x, color=col, lw=0.7)
    for bb in cs.BALMER:
        if a < bb < b: ax.axvline(bb, color="tab:green", ls=":", lw=0.8)
    ax.set_xlim(a, b)
axs.flat[0].legend(fontsize=7); fig.suptitle("Gaia DR3 883885440381808000: SDSS-V (2025) and LAMOST (2011); C I red, C II blue at +110 km/s, Balmer green")
fig.tight_layout(); fig.savefig("lamost_vs_sdssv_883885440381808000.png", dpi=80); print("saved")
