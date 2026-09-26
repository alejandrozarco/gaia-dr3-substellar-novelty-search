"""Plot a DESI DR1 spectrum (SPARCL, by TARGETID) around C I / C II lines at a given velocity. Usage: python desi_vet.py <targetid> <v_kms> <label>"""
import sys, numpy as np, warnings, matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
warnings.filterwarnings("ignore")
sys.path.insert(0, "/tmp/hotdq/lane_daq"); import carbon_screen as cs
from scipy.ndimage import percentile_filter, gaussian_filter1d
from sparcl.client import SparclClient
tid, v0, label = int(sys.argv[1]), float(sys.argv[2]), sys.argv[3]
rec = SparclClient().retrieve_by_specid([tid], include=["flux", "ivar", "wavelength", "mask"], dataset_list=["DESI-DR1"]).records[0]
w = np.array(rec["wavelength"]); f = np.array(rec["flux"]); iv = np.array(rec["ivar"]) * (np.array(rec["mask"]) == 0); ok = iv > 0
fg = np.interp(cs.grid, w[ok], f[ok])
n = int(round(np.log10(1 + 150 / 5000) / 6e-5)); nf = gaussian_filter1d(fg / gaussian_filter1d(percentile_filter(fg, 85, size=n), n / 3), 1.0)
fig = plt.figure(figsize=(15, 10)); gs = fig.add_gridspec(3, 4); ax = fig.add_subplot(gs[0, :]); ax.plot(cs.grid, nf, "k", lw=0.6)
for sp, col in (("C I", "tab:red"), ("C II", "tab:blue")):
    for lam in cs.LINES[sp]: ax.axvline(lam * (1 + v0 / cs.C), color=col, lw=0.6, alpha=0.6)
for b in cs.BALMER: ax.axvline(b, color="tab:green", ls=":", lw=0.8)
ax.set_xlim(3850, 9200); ax.set_ylim(0.3, 1.25); ax.set_title(f"{label} DESI DR1 TARGETID {tid}; carbon lines at {v0:+.0f} km/s")
for i, (a, b) in enumerate([(3880, 4130), (4200, 4420), (4700, 5100), (5100, 5420), (5950, 6100), (6480, 6680), (7050, 7300), (8250, 8400)]):
    x = fig.add_subplot(gs[1 + i // 4, i % 4]); m = (cs.grid > a) & (cs.grid < b); x.plot(cs.grid[m], nf[m], "k", lw=0.8)
    for sp, col in (("C I", "tab:red"), ("C II", "tab:blue")):
        for lam in cs.LINES[sp]:
            if a < lam * (1 + v0 / cs.C) < b: x.axvline(lam * (1 + v0 / cs.C), color=col, lw=0.7)
    for bb in cs.BALMER:
        if a < bb < b: x.axvline(bb, color="tab:green", ls=":")
    x.set_xlim(a, b)
fig.tight_layout(); fig.savefig(f"dvet_{tid}.png", dpi=75); print(f"dvet_{tid}.png")
