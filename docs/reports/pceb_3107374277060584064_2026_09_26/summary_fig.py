"""Summary figure for Gaia DR3 3107374277060584064 with the joint CoRoT+ZTF ephemeris (max light BMJD 59300.28308 + 0.59288695 E):
CoRoT folds (3 runs, 30-min bins), ZTF g/r, Gaia DR3 G epoch photometry (VizieR I/355/epphot, TimeG + 55197 = MJD), SDSS-V emission
velocities (visit_phase_rv.csv) with a fit v = gamma - K sin(2 pi phase) (phase 0 = max light = companion behind the WD).
Output: pceb_summary.png, rv_fit.txt"""
import glob, numpy as np, pandas as pd, matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
from astropy.io import fits
from scipy.ndimage import median_filter
from astroquery.vizier import Vizier
import astropy.units as u
from astropy.coordinates import SkyCoord
T0, P = 59300.28308, 0.59288695
ph = lambda t: ((t - T0) / P) % 1
fig, ax = plt.subplots(2, 2, figsize=(11, 8))
for f, lab in zip(sorted(glob.glob("corot/*.fits")), ["2007 Feb-Apr", "2007 Oct-2008 Mar", "2012 Jan-Mar"]):
    d = fits.open(f)["BAR"].data; ok = (d["STATUS"] == 0) & (d["WHITEFLUX"] > 0)
    t = d["DATEBARTT"][ok].astype(float) + 51544.5; y = d["WHITEFLUX"][ok].astype(float); o = np.argsort(t); t, y = t[o], y[o]; y = y / np.median(y) - 1
    r = y - median_filter(y, size=int(3 / np.median(np.diff(t))) | 1, mode="nearest")
    b = np.linspace(0, 1, 41); p = ph(t); m = [np.median(r[(p >= b[j]) & (p < b[j + 1])]) for j in range(40)]
    ax[0, 0].plot(np.r_[b[:-1], b[:-1] + 1] + 0.0125, np.r_[m, m] , "-o", ms=2, label=f"CoRoT {lab}")
ax[0, 0].set_title("CoRoT white light (blend with G = 16.2 star 4.1\" away)"); ax[0, 0].set_ylabel("relative flux - 1"); ax[0, 0].legend(fontsize=7); ax[0, 0].set_xlabel("phase")
z = pd.read_csv("ztf_WD.csv")
for bnd, c in (("zg", "tab:green"), ("zr", "tab:red")):
    s = z[z.filtercode == bnd]; fl = 10 ** (-0.4 * (s.mag - s.mag.median())) - 1; p = ph(s.hjd.values - 2400000.5)
    ax[0, 1].errorbar(np.r_[p, p + 1], np.r_[fl, fl], np.r_[s.magerr, s.magerr] * 0.92, fmt=".", color=c, ms=3, alpha=.6, label=f"ZTF {bnd[1]}")
V = Vizier(columns=["**"], row_limit=-1); g = V.query_region(SkyCoord(101.158714 * u.deg, -0.764028 * u.deg), radius=2 * u.arcsec, catalog="I/355/epphot")[0]
g = g[(np.asarray(g["Source"]).astype(str) == "3107374277060584064")]
tg = np.asarray(g["TimeG"], float) + 55197.0; fg = np.asarray(g["FG"], float); ok = np.isfinite(tg) & np.isfinite(fg) & (fg > 0)
fg = fg[ok] / np.median(fg[ok]) - 1; pg = ph(tg[ok])
ax[0, 1].plot(np.r_[pg, pg + 1], np.r_[fg, fg], "ks", ms=4, mfc="none", label=f"Gaia G ({ok.sum()})")
ax[0, 1].set_title("ZTF and Gaia DR3 (this star alone)"); ax[0, 1].legend(fontsize=7); ax[0, 1].set_xlabel("phase")
rv = pd.read_csv("visit_phase_rv.csv"); rv["p"] = ph(rv.t_mid)
out = []
for col, c, mk in (("CaT", "tab:blue", "o"), ("Ha", "tab:red", "s")):
    s = rv[(rv[f"{col}_amp_snr"] > 5)]
    X = np.vstack([np.ones(len(s)), -np.sin(2 * np.pi * s.p)]).T; w = 1 / s[f"{col}_ev"].values
    cc, *_ = np.linalg.lstsq(X * w[:, None], s[f"{col}_v"].values * w, rcond=None); res = s[f"{col}_v"].values - X @ cc
    out.append(f"{col}: gamma {cc[0]:.0f} km/s, K {cc[1]:.0f} km/s from {len(s)} visits; residuals {np.round(res).astype(int).tolist()} km/s (errors {s[f'{col}_ev'].astype(int).tolist()})")
    ax[1, 0].errorbar(np.r_[s.p, s.p + 1], np.r_[s[f"{col}_v"], s[f"{col}_v"]], np.r_[s[f"{col}_ev"], s[f"{col}_ev"]], fmt=mk, color=c, label=f"{col} emission")
    xx = np.linspace(0, 2, 200); ax[1, 0].plot(xx, cc[0] - cc[1] * np.sin(2 * np.pi * xx), color=c, lw=.8)
nd = rv[rv.CaT_amp_snr <= 5]
for _, r in nd.iterrows(): ax[1, 0].axvline(r.p, color="grey", ls=":"); ax[1, 0].axvline(r.p + 1, color="grey", ls=":")
ax[1, 0].set_title("SDSS-V emission velocity (dotted: visit without emission)"); ax[1, 0].set_xlabel("phase (0 = maximum light)"); ax[1, 0].set_ylabel("km/s"); ax[1, 0].legend(fontsize=7)
ax[1, 1].axis("off"); ax[1, 1].text(0, 0.95, "Gaia DR3 3107374277060584064\nG = 17.27, parallax 1.82 +- 0.09 mas (550 pc)\nM_G = 8.57, BP-RP = -0.35\nSDSS-V: He II 4686 absorption, weak Balmer;\nH-alpha, H-beta, Ca II triplet emission moving\nP = 0.59288695 d (14.2293 h), CoRoT 2007-2012 + ZTF 2019-2024\n\n" + "\n".join(out), va="top", fontsize=8, family="monospace")
plt.tight_layout(); plt.savefig("pceb_summary.png", dpi=90); open("rv_fit.txt", "w").write("\n".join(out) + "\n"); print("\n".join(out))
