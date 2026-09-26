"""Vetting plot for an emission candidate: per-visit and coadd Ca II triplet line profiles in velocity, H-alpha region, and
the stored coadd regions. python vet_gas.py <sdss_id> <out.png>"""
import sys, numpy as np, matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt, pandas as pd
from scipy.ndimage import gaussian_filter1d
GRID = 10 ** np.arange(np.log10(3850), np.log10(9250), 6e-5); C = 299792.458
CAT = [8500.35, 8544.44, 8664.52]; sid = sys.argv[1]; d = np.load(f"store/{sid[-2:]}/{sid}.npz")
lab = pd.read_csv("sw_all.csv", dtype=str).set_index("sdss_id").loc[sid]
def reg(a, b): m = (GRID > a) & (GRID < b); return GRID[m]
wc = reg(8250, 8950); wh = reg(6400, 6750)
def nrm(w, f, iv, excl):
    ok = (iv > 0) & np.isfinite(f); use = ok.copy()
    for lo, hi in excl: use &= ~((w > lo) & (w < hi))
    p = np.polyfit(w[use], f[use], 2, w=np.sqrt(iv[use])); return np.where(ok, f / np.polyval(p, w), np.nan)
exc = [(l - 32, l + 32) for l in CAT] + [(8420, 8475)]
nv = d["vf_8250"].shape[0]; fig = plt.figure(figsize=(14, 3 + 1.1 * max(nv, 3)))
gs = fig.add_gridspec(2, 4, height_ratios=[1, 1.3])
ax0 = fig.add_subplot(gs[0, :3]); ax1 = fig.add_subplot(gs[0, 3])
fc = nrm(wc, d["f_8250"], d["iv_8250"], exc); ax0.plot(wc, gaussian_filter1d(np.nan_to_num(fc, nan=1), 1), "k", lw=0.8)
for l in CAT + [8448.7]: ax0.axvline(l, color="r", lw=0.4)
ax0.set_title(f"{sid} Gaia {lab.gaia_dr3_source_id} {lab.classification} G {float(lab.g_mag):.2f} Teff {float(lab.teff):.0f} logg {float(lab.logg):.2f} nvis {nv}", fontsize=9)
fh = nrm(wh, d["f_6400"], d["iv_6400"], [(6500, 6630)]); ax1.plot((wh / 6564.61 - 1) * C, gaussian_filter1d(np.nan_to_num(fh, nan=1), 1), "k", lw=0.8)
ax1.set_xlim(-3000, 3000); ax1.set_title("H-alpha coadd (km/s)", fontsize=8)
axs = [fig.add_subplot(gs[1, j]) for j in range(4)]
off = 0
for k in range(nv):
    f = d["vf_8250"][k]; iv = d["viv_8250"][k]
    if (iv > 0).sum() < 100: continue
    n = nrm(wc, f, iv, exc); ns = gaussian_filter1d(np.nan_to_num(n, nan=1), 1.5)
    for j, l in enumerate(CAT): axs[j].plot((wc / l - 1) * C, ns + 0.5 * off, lw=0.7)
    fv = d["vf_6400"][k]; ivh = d["viv_6400"][k]
    if (ivh > 0).sum() > 100:
        nh = nrm(wh, fv, ivh, [(6500, 6630)]); axs[3].plot((wh / 6564.61 - 1) * C, gaussian_filter1d(np.nan_to_num(nh, nan=1), 1.5) + 0.5 * off, lw=0.7)
    for a in axs: a.text(1200, 1.15 + 0.5 * off, str(d["mjd"][k]), fontsize=6)
    off += 1
for j, a in enumerate(axs):
    a.set_xlim(-1500, 1500); a.axvline(0, color="grey", lw=0.4); a.set_title(["Ca 8500", "Ca 8544", "Ca 8665", "H-alpha"][j] + " per visit (km/s)", fontsize=8)
plt.tight_layout(); plt.savefig(sys.argv[2], dpi=85)
