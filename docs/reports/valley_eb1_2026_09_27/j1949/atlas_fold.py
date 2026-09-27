"""ATLAS forced photometry of WDJ194901.41+673005.59 (atlas_fp_J1949.txt, requested 2026-09-27) on the adopted Gaia+TESS ephemeris
(f = 22.6130201 c/d, maximum at BJD_TDB 2459000.00061; sdssv-white-dwarfs-2026 tables/irradiated_companions.csv).
Difference fluxes (uJy) only. Cuts: duJy > 0, chi/N < 3, mag5sig > 17.5, |uJy - season median| < 5 robust sigma. Per filter and season
(gaps > 60 d) the median is removed. Times: MJD -> BJD_TDB. Semi-amplitude of the fundamental (fit with first harmonic) in uJy and as a fraction of
the mean flux (c: mean of Pan-STARRS g, r fluxes = 205 uJy; o: mean of r, i = 183 uJy). Phase of maximum per filter and per epoch block."""
import numpy as np, pandas as pd, warnings; warnings.filterwarnings("ignore")
from astropy.time import Time; from astropy.coordinates import SkyCoord, EarthLocation; import astropy.units as u
from astropy.timeseries import LombScargle
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
F0, T0 = 22.6130201, 2459000.00061; MEAN = {"c": 205.0, "o": 183.0}
d = pd.read_csv("atlas_fp_J1949.txt", sep=r"\s+"); d.columns = [c.lstrip("#") for c in d.columns]
n0 = len(d); d = d[(d.duJy > 0) & (d["chi/N"] < 3) & (d.mag5sig > 17.5)].copy()
c = SkyCoord(297.25575940, 67.50155413, unit="deg"); t = Time(d.MJD.values, format="mjd", scale="utc", location=EarthLocation.of_site("greenwich"))
d["bjd"] = (t.tdb + t.light_travel_time(c)).jd; d["y"] = np.nan
for b in "co":
    m = d.F == b; tt = d.loc[m, "bjd"].values; br = np.r_[0, np.where(np.diff(tt) > 60)[0] + 1, m.sum()]; idx = d.index[m]
    for a, e in zip(br[:-1], br[1:]):
        ii = idx[a:e]; v = d.loc[ii, "uJy"]; d.loc[ii, "y"] = v - v.median()
    s = 1.4826 * np.median(np.abs(d.loc[m, "y"])); d.loc[m & (np.abs(d.y) > 5 * s), "y"] = np.nan
d = d[np.isfinite(d.y)]; print(n0, "rows,", len(d), "after cuts:", d.F.value_counts().to_dict())
def fit(t, y, e):
    X = np.vstack([np.ones_like(t)] + [fn(2 * np.pi * k * F0 * (t - T0)) for k in (1, 2) for fn in (np.cos, np.sin)]).T
    W = X / e[:, None]; cc = np.linalg.lstsq(W, y / e, rcond=None)[0]; chi = np.sum(((y - X @ cc) / e) ** 2) / (len(t) - 5); cov = np.linalg.inv(W.T @ W) * max(chi, 1)
    a = np.hypot(cc[1], cc[2]); ea = np.sqrt((cc[1] ** 2 * cov[1, 1] + cc[2] ** 2 * cov[2, 2])) / a; ph = (np.arctan2(cc[2], cc[1]) / (2 * np.pi)) % 1
    eph = ea / a / (2 * np.pi); a2 = np.hypot(cc[3], cc[4]); return a, ea, (ph + 0.5) % 1 - 0.5, eph, a2, chi
rows = []; FR = np.linspace(5, 50, 900000)
fig, ax = plt.subplots(1, 3, figsize=(15, 3.8))
for b, col in (("c", "tab:cyan"), ("o", "tab:orange")):
    x = d[d.F == b]; tt, y, e = x.bjd.values, x.y.values, x.duJy.values
    ls = LombScargle(tt, y, e); p = ls.power(FR); k = np.argmax(p)
    a, ea, ph, eph, a2, chi = fit(tt, y, e)
    rows.append(dict(block="all", band=b, n=len(tt), f_peak=round(FR[k], 5), fap=float(f"{ls.false_alarm_probability(p[k], minimum_frequency=5, maximum_frequency=50):.2g}"),
                     amp_uJy=round(a, 1), e_amp=round(ea, 1), amp_frac_pct=round(100 * a / MEAN[b], 1), e_frac=round(100 * ea / MEAN[b], 1), phase_max=round(ph, 3), e_phase=round(eph, 3), harm2_ratio=round(a2 / a, 2), chi2r=round(chi, 2)))
    for lo, hi in ((2015, 2019), (2019, 2022), (2022, 2027)):
        yr = Time(tt, format="jd").decimalyear; m = (yr >= lo) & (yr < hi)
        if m.sum() > 100:
            a, ea, ph, eph, a2, chi = fit(tt[m], y[m], e[m]); rows.append(dict(block=f"{lo}-{hi}", band=b, n=int(m.sum()), amp_uJy=round(a, 1), e_amp=round(ea, 1), amp_frac_pct=round(100 * a / MEAN[b], 1), e_frac=round(100 * ea / MEAN[b], 1), phase_max=round(ph, 3), e_phase=round(eph, 3)))
    ax[0].plot(FR, p, lw=.4, color=col, label=b); phs = ((tt - T0) * F0) % 1; bn = np.linspace(0, 1, 21); axx = ax[1 if b == "c" else 2]
    mb = [np.average(y[(phs >= u0) & (phs < u1)], weights=1 / e[(phs >= u0) & (phs < u1)] ** 2) for u0, u1 in zip(bn[:-1], bn[1:])]
    eb = [1 / np.sqrt(np.sum(1 / e[(phs >= u0) & (phs < u1)] ** 2)) for u0, u1 in zip(bn[:-1], bn[1:])]
    for sh in (0, 1): axx.errorbar((bn[:-1] + bn[1:]) / 2 + sh, np.array(mb) / MEAN[b], np.array(eb) / MEAN[b], fmt="o", color=col)
    axx.axhline(0, color="k", lw=.5); axx.set_xlabel(f"phase (ATLAS {b}; 0 = Gaia/TESS maximum)"); axx.set_ylabel("difference flux / mean flux")
ax[0].axvline(F0, color="k", ls=":", lw=.8); ax[0].set_xlabel("frequency (c/d)"); ax[0].legend()
fig.suptitle("WDJ194901.41+673005.59, ATLAS forced photometry 2015-2026", fontsize=9); plt.tight_layout(); plt.savefig("atlas_fold.png", dpi=90)
R = pd.DataFrame(rows); R.to_csv("atlas_fold.csv", index=False); print(R.to_string(index=False))
