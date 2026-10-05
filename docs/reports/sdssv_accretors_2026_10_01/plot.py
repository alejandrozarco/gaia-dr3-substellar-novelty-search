"""Contact plot per spec-lite file: full spectrum (smoothed) + zooms 4800-4900/4650-4720, 5850-5900, 6520-6610 (vacuum A)."""
import os, sys, numpy as np, pandas as pd, matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
from astropy.io import fits
D = os.path.dirname(os.path.abspath(__file__))
def plot(fn, title, out):
    with fits.open(os.path.join(D, "spec", fn)) as h:
        d = h[1].data; w = 10 ** d["LOGLAM"]; f = d["FLUX"]; iv = d["IVAR"]; m = d["MODEL"]
    good = iv > 0
    fig = plt.figure(figsize=(14, 6)); ax = fig.add_axes([0.05, 0.55, 0.92, 0.38])
    k = np.ones(5) / 5; fs = np.convolve(np.where(good, f, np.nan), k, "same")
    ax.plot(w, fs, "k", lw=0.6); ax.plot(w, m, "r", lw=0.5, alpha=0.6)
    lo, hi = np.nanpercentile(fs[good], [1, 99.5]); ax.set_ylim(min(0, lo), hi * 1.1); ax.set_title(title, fontsize=8)
    for lw_ in (4687, 4863, 5877, 6565, 6680, 7067, 5008): ax.axvline(lw_, color="b", lw=0.3)
    for i, (a, b, ls) in enumerate(((4300, 4520, [4342, 4473]), (4640, 4900, [4687, 4863]), (5840, 5910, [5877]), (6480, 6720, [6565, 6680]))):
        x = fig.add_axes([0.05 + i * 0.235, 0.07, 0.21, 0.38]); s = (w > a) & (w < b) & good
        x.plot(w[s], f[s], "k", lw=0.7); [x.axvline(l, color="b", lw=0.4) for l in ls]; x.tick_params(labelsize=6)
    fig.savefig(out, dpi=70); plt.close(fig)
if __name__ == "__main__":
    V = pd.read_csv(sys.argv[1], dtype={"gaia": str}); od = sys.argv[2]; os.makedirs(od, exist_ok=True)
    for i, r in enumerate(V.itertuples()):
        t = f"{i} {r.fname} G={r.g_mag:.2f} bprp={r.bp_rp:.2f} plx={r.plx:.2f}+-{r.e_plx:.2f} {r.firstcarton} Ha={r.Ha:.0f} Hb={r.Hb:.0f} HeI={r.HeI5877:.1f} HeII={r.HeII4687:.1f} sn={r.sn:.1f}"
        plot(r.fname, t, os.path.join(od, f"{i:03d}_{r.fname[:-5]}.png"))
