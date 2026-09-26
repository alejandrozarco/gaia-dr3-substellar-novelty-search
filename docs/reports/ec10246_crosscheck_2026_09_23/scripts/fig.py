# Figure: TIC 193092806 (EC 10246-2707), TESS sector 100. (a) 20-s data vs 20-min bins over one day;
# (b) 20-s data folded on P = 0.1185079936 d (primary at phase 0, secondary at 0.5).
import glob, numpy as np, matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
from astropy.io import fits
P = 0.1185079936; T0 = 4074.69092
def load(pat):
    f = glob.glob(pat)[0]; d = fits.getdata(f, 1)
    ok = np.isfinite(d["TIME"]) & np.isfinite(d["PDCSAP_FLUX"]) & (d["QUALITY"] == 0)
    first = d["TIME"][np.isfinite(d["TIME"])][0]
    return d["TIME"][ok], d["PDCSAP_FLUX"][ok] / np.nanmedian(d["PDCSAP_FLUX"][ok]), first
t, f, tfirst = load("mastDownload/TESS/*s0100*-s/*s_lc.fits")
tf, ff, _ = load("mastDownload/TESS/*s0100*a_fast/*lc.fits")
bw = 20 / 1440.; e = np.arange(tfirst, t[-1] + bw, bw); k = np.digitize(t, e) - 1
u = np.unique(k); tb = np.array([t[k == j].mean() for j in u]); fb = np.array([f[k == j].mean() for j in u])
fig, ax = plt.subplots(2, 1, figsize=(10, 7.5))
w = (tf - tfirst > 0.62) & (tf - tfirst < 1.85); wb = (tb - tfirst > 0.62) & (tb - tfirst < 1.85)
ax[0].plot(tf[w] - tfirst, ff[w], ".", ms=1.5, color="goldenrod", label="20-s cadence")
ax[0].plot(tb[wb] - tfirst, fb[wb], "o-", ms=3.5, lw=0.8, color="k", label="20-min bins")
for n in range(int((tfirst + 0.62 - T0) / P) - 1, int((tfirst + 1.85 - T0) / P) + 2):
    x = T0 + n * P - tfirst
    if 0.62 < x < 1.85: ax[0].axvline(x, color="tab:blue", lw=0.5, alpha=0.5)
ax[0].set_xlabel(f"days after the first cadence of the sector-100 file (BTJD {tfirst:.4f})"); ax[0].set_ylabel("relative flux")
ax[0].set_title("TIC 193092806 = EC 10246-2707, TESS sector 100: every primary eclipse is identical at 20 s; in 20-min bins\n"
                "they alternate between one bin (deeper) and two bins (shallower, ~20 min wider) because P = 8.53 bins", fontsize=10)
ax[0].legend(loc="lower right", fontsize=8)
ph = (((tf - T0) / P + 0.25) % 1) - 0.25
ax[1].plot(ph, ff, ",", color="goldenrod", alpha=0.4)
edges = np.linspace(-0.25, 0.75, 301); m = 0.5 * (edges[1:] + edges[:-1])
v = [np.median(ff[(ph >= edges[i]) & (ph < edges[i + 1])]) for i in range(300)]
ax[1].plot(m, v, "k-", lw=1)
ax[1].set_xlim(-0.25, 0.75); ax[1].set_ylim(0.45, 1.2)
ax[1].set_xlabel(f"orbital phase (P = {P} d, primary mid-eclipse BTJD {T0})"); ax[1].set_ylabel("relative flux")
ax[1].annotate("primary eclipse (sdB occulted)\ndepth 0.40 (normalised flux), FWHM 9.7 min", (0.0, 0.55), (0.08, 0.5), fontsize=8, arrowprops=dict(arrowstyle="->"))
ax[1].annotate("secondary eclipse (irradiated M dwarf occulted)\ndepth 0.12 below the fitted reflection hump, FWHM 10 min", (0.5, 1.02), (0.12, 1.12), fontsize=8, arrowprops=dict(arrowstyle="->"))
plt.tight_layout(); plt.savefig("ec10246_s100_binning.png", dpi=130)
print("saved")
