"""ATLAS forced photometry check of two hot WDs at their Gaia GLS frequencies (difference flux uJy; duJy>0, chi/N<3, mag5sig>17.5,
season medians removed, 5-sigma clip). LS 0.05-5 c/d; amplitude at the Gaia frequency per band."""
import numpy as np, pandas as pd, warnings; warnings.filterwarnings("ignore")
from astropy.timeseries import LombScargle
T = {"2311285729210966144": 0.9064, "3365371721281530880": 1.1899}
for gid, fg in T.items():
    d = pd.read_csv(f"atlas/{gid}.txt", sep=r"\s+"); d.columns = [c.lstrip("#") for c in d.columns]
    d = d[(d.duJy > 0) & (d["chi/N"] < 3) & (d.mag5sig > 17.5)].copy(); d["y"] = np.nan
    for b in "co":
        m = d.F == b; t = d.MJD[m].values; br = np.r_[0, np.where(np.diff(t) > 60)[0] + 1, m.sum()]; idx = d.index[m]
        for a, e in zip(br[:-1], br[1:]):
            ii = idx[a:e]; d.loc[ii, "y"] = d.loc[ii, "uJy"] - d.loc[ii, "uJy"].median()
        s = 1.4826 * np.median(np.abs(d.loc[m, "y"])); d.loc[m & (np.abs(d.y) > 5 * s), "y"] = np.nan
    d = d[np.isfinite(d.y)]; FR = np.linspace(0.05, 5, 400000); print("=====", gid, "N", len(d), d.F.value_counts().to_dict())
    for b in "co":
        x = d[d.F == b]; t, y, e = x.MJD.values, x.y.values, x.duJy.values
        ls = LombScargle(t, y, e); p = ls.power(FR); k = np.argmax(p); w = np.abs(FR - fg) < 0.01; kk = np.argmax(p * w)
        X = np.vstack([np.sin(2 * np.pi * FR[kk] * t), np.cos(2 * np.pi * FR[kk] * t), np.ones_like(t)]).T
        c = np.linalg.lstsq(X / e[:, None], y / e, rcond=None)[0]; cov = np.linalg.inv((X / e[:, None]).T @ (X / e[:, None]))
        a = np.hypot(c[0], c[1]); ea = np.sqrt((cov[0, 0] + cov[1, 1]) / 2)
        print(f"  {b}: n {len(t)}, peak {FR[k]:.5f} c/d (P {24/FR[k]:.3f} h) FAP {ls.false_alarm_probability(p[k], minimum_frequency=0.05, maximum_frequency=5):.2g}; "
              f"near Gaia {FR[kk]:.5f} FAP {ls.false_alarm_probability(p[kk], minimum_frequency=0.05, maximum_frequency=5):.2g}, amp {a:.1f} +- {ea:.1f} uJy")
