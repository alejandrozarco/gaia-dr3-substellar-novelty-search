"""Per season and per ATLAS unit: amplitude and phase of a sinusoid at a fixed frequency; also residual vs time of night."""
import sys, numpy as np, pandas as pd
f, G, f0 = sys.argv[1], float(sys.argv[2]), float(sys.argv[3])
d = pd.read_csv(f, sep=r"\s+"); d.columns = [c.lstrip("#") for c in d.columns]; d = d[(d.duJy > 0) & (d.err == 0) & (d["chi/N"] < 10)].copy()
ref = 3631e6 * 10 ** (-0.4 * G); d["seas"] = np.floor((d.MJD - 57000) / 365.25); d["y"] = np.nan
for k, g in d.groupby(["F", "seas"]): d.loc[g.index, "y"] = (g.uJy - np.median(g.uJy)) / ref
d = d[np.abs(d.y) < 5 * 1.4826 * np.nanmedian(np.abs(d.y))]; d["e"] = d.duJy / ref
def fit(s):
    X = np.vstack([np.ones(len(s)), np.cos(2 * np.pi * f0 * s.MJD), np.sin(2 * np.pi * f0 * s.MJD)]).T
    c = np.linalg.lstsq(X / s.e.values[:, None], s.y.values / s.e.values, rcond=None)[0]; cov = np.linalg.inv((X / s.e.values[:, None]).T @ (X / s.e.values[:, None]))
    return 100 * np.hypot(c[1], c[2]), 100 * np.sqrt(cov[1, 1]), np.degrees(np.arctan2(c[2], c[1])) % 360
print("unit column values:", d.Obs.str[:3].value_counts().to_dict())
for key, g in d.groupby([d.Obs.str[:3], "F"]):
    if len(g) < 40: continue
    a, e, ph = fit(g); print(f"unit {key[0]} {key[1]}: n={len(g)} amp {a:.2f}±{e:.2f}% phase {ph:.0f}")
for key, g in d.groupby(["seas"]):
    if len(g) < 60: continue
    a, e, ph = fit(g); print(f"season {int(key[0]) if isinstance(key, tuple) else int(key)}: n={len(g)} amp {a:.2f}±{e:.2f}% phase {ph:.0f}")
