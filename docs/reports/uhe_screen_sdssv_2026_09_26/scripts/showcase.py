import os, sys, numpy as np, pandas as pd, matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
sys.path.insert(0, os.path.expanduser("~/claude_projects/sdssv-white-dwarfs-2026/scripts")); import sdssv
from scipy.ndimage import median_filter, gaussian_filter1d
W = os.path.dirname(os.path.abspath(__file__))
S = [("100568930", "WDJ0958-1758 (this star)", "C3"), ("59101580", "WDJ0706+6133 (known DA UHE)", "C0"), ("63039439", "HS 2115+1148 (known DAO UHE)", "C0"),
     ("63152641", "WDJ2101+1356 (known DAO UHE)", "C0"), ("74510696", "SDSS J0814+0225 (normal hot DAO)", "0.4"), ("92431667", "PN Lo 1 (normal, 118 kK)", "0.4")]
fig = plt.figure(figsize=(13, 6.5)); a = fig.add_axes([0.06, 0.1, 0.4, 0.85])
for i, (sid, lab, col) in enumerate(S):
    vs = sdssv.visits(sid); vs = [v for v in vs if v["in_stack"]] or vs; w, f, iv = sdssv.coadd(vs)[:3]; ok = (iv > 0) & np.isfinite(f); w, f = w[ok], f[ok]
    k = (w > 5150) & (w < 5420); c = median_filter(f, 401, mode="nearest"); y = gaussian_filter1d(f[k] / c[k], 1.5)
    a.plot(w[k], y - 0.12 * i, color=col, lw=0.9); a.text(5155, 1.035 - 0.12 * i, lab, fontsize=8, color=col)
a.axvspan(5262, 5310, color="gold", alpha=0.25); a.set_xlabel("vacuum wavelength (Å)"); a.set_yticks([]); a.set_title("SDSS-V spectra around the 5285 Å UHE feature (shaded)", fontsize=9)
z = pd.read_csv(f"{W}/ztf.csv"); z = z[(z.catflags == 0) & (z.magerr < 0.25)]; f0 = float(open(f"{W}/f0.txt").read())
b = fig.add_axes([0.55, 0.1, 0.42, 0.85])
for band, col in (("zg", "C2"), ("zr", "C3")):
    s = z[z.filtercode == band]; fl = 10 ** (-0.4 * (s.mag - np.median(s.mag))) - 1; ph = ((s.hjd - 2459000.0) * f0) % 1
    b.plot(np.r_[ph, ph + 1], np.r_[fl, fl], ".", ms=3, alpha=0.35, color=col)
    e = np.linspace(0, 1, 16); m = [np.median(fl[(ph >= e[j]) & (ph < e[j + 1])]) for j in range(15)]; cc = (e[1:] + e[:-1]) / 2
    b.plot(np.r_[cc, cc + 1], np.r_[m, m], "o-", color=col, label=f"ZTF {band[1]} (binned)")
b.set_ylim(-0.2, 0.2); b.set_xlabel(f"phase (P = {1/f0:.4f} d)"); b.set_ylabel("fractional flux"); b.legend(fontsize=8); b.set_title("WDJ0958-1758: ZTF 2018-2025 folded on the Gaia/ZTF period", fontsize=9)
plt.savefig(f"{W}/wdj0958_uhe.png", dpi=110)
