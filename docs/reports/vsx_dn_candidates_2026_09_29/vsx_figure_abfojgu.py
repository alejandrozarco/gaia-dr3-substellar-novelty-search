"""VSX supporting figure for Gaia DR3 5182404743053707904 = ZTF24abfojgu (2026-09-29): long-term light curve (Pan-STARRS1 DR2
detections, ZTF data release catflags 0, ZTF alerts) and the 76.344-min fold of the detrended data (10-d leave-one-out running
median, as abfojgu_highstate.py) in quiescence and in the bright state."""
import numpy as np, pandas as pd, os, matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
from astropy.time import Time
H = os.path.dirname(os.path.abspath(__file__)); os.environ["WIN"] = "10"
exec(open(os.path.join(H, "abfojgu_highstate.py")).read().split("fr = np.linspace")[0])
ps = pd.read_csv(os.path.join(H, "ps1_abfojgu.csv"))
fig = plt.figure(figsize=(10, 7)); ax = fig.add_subplot(2, 1, 1)
for band, c in (("g", "tab:green"), ("r", "tab:red")):
    x = ps[ps.band == band]; ax.plot(x.obsTime, x.mag, "s", ms=4, color=c, mfc="none", label=f"Pan-STARRS1 {band}")
for fc, c, lab in (("zg", "tab:green", "g"), ("zr", "tab:red", "r")):
    x = d[d.filtercode == fc]; ax.plot(x.mjd, x.mag, ".", ms=3, color=c, alpha=0.6, label=f"ZTF DR {lab}")
    y = a[a.fid == (1 if fc == "zg" else 2)]; ax.plot(y.mjd, y.magpsf_corr, "x", ms=4, color=c, alpha=0.8, label=f"ZTF alerts {lab}")
ax.axvline(60578.5, color="k", lw=0.6, ls="--"); ax.invert_yaxis(); ax.set_xlabel("MJD"); ax.set_ylabel("magnitude")
ax.set_title("Gaia DR3 5182404743053707904 = ZTF24abfojgu: brightening on 2024-09-24/27 (dashed line)", fontsize=10); ax.legend(fontsize=7, ncol=3)
f0 = 18.861971
for k, state in enumerate(("low", "high")):
    D = dataset(state); t, y = D.t.values, D.res.values; ax = fig.add_subplot(2, 2, 3 + k); ph = ((t - 2460000.0) * f0) % 1
    for f, c in (("zg", "tab:green"), ("zr", "tab:red")):
        i = D.f.values == f; ax.plot(np.r_[ph[i], ph[i] + 1], np.r_[y[i], y[i]], ".", ms=3, color=c, alpha=0.5)
    ed = np.linspace(0, 1, 11); cen = (ed[:-1] + ed[1:]) / 2; mb = [np.median(y[(ph >= ed[j]) & (ph < ed[j + 1])]) for j in range(10)]
    ax.plot(np.r_[cen, cen + 1], np.r_[mb, mb], "ko-", ms=4); ax.invert_yaxis(); ax.set_ylim(0.9, -0.9)
    ax.set_xlabel("phase (P = 76.344 min, T0 = BJD 2460000.0)"); ax.set_ylabel("detrended mag")
    ax.set_title(("quiescence (before 2024-09-24)" if state == "low" else "bright state (after 2024-09-27)") + f", n = {len(t)}", fontsize=9)
plt.tight_layout(); plt.savefig(os.path.join(H, "vsx_ZTF24abfojgu.png"), dpi=90); print("saved")
