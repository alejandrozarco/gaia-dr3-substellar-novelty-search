"""ATLAS forced photometry periodogram: cuts duJy > 0, err == 0, chi/N < 10, |uJy| outliers 5 sigma clipped; per filter and season
the median is subtracted; fractional flux relative to the median total flux estimated from the Gaia G mag (ATLAS c/o ~ G).
Lomb-Scargle 0.05-50 c/d on c and o jointly (separate offsets via per-filter mean subtraction); top peaks and FAP; per-filter amplitude."""
import sys, numpy as np, pandas as pd
from astropy.timeseries import LombScargle
f, G = sys.argv[1], float(sys.argv[2])
d = pd.read_csv(f, sep=r"\s+"); d.columns = [c.lstrip("#") for c in d.columns]
d = d[(d.duJy > 0) & (d.err == 0) & (d["chi/N"] < 10)].copy()
ref = 3631e6 * 10 ** (-0.4 * G)  # uJy
t, y, e, fl = [], [], [], []
for (flt, seas), s in d.groupby([d.F, np.floor((d.MJD - 57000) / 365.25)]):
    if len(s) < 10: continue
    yy = s.uJy - np.median(s.uJy); k = np.abs(yy) < 5 * 1.4826 * np.median(np.abs(yy)); s = s[k]; yy = yy[k]
    t += list(s.MJD); y += list(yy / ref); e += list(s.duJy / ref); fl += list(s.F)
t, y, e, fl = map(np.array, (t, y, e, fl)); print(len(t), "points; median error", round(float(np.median(e)) * 100, 2), "%")
fr = np.arange(0.05, 50, 0.0002); ls = LombScargle(t, y, e); p = ls.power(fr); order = np.argsort(p)[::-1]; peaks = []
for i in order:
    if all(abs(fr[i] - q) > 0.005 for q in peaks): peaks.append(fr[i])
    if len(peaks) == 6: break
print("top peaks (c/d):", [round(x, 4) for x in peaks], "FAP best", f"{ls.false_alarm_probability(p.max(), minimum_frequency=0.05, maximum_frequency=50):.2g}")
f0 = peaks[0]
for band in ("c", "o"):
    m = fl == band
    if m.sum() < 20: continue
    X = np.vstack([np.ones(m.sum()), np.cos(2 * np.pi * f0 * t[m]), np.sin(2 * np.pi * f0 * t[m])]).T
    c = np.linalg.lstsq(X / e[m][:, None], y[m] / e[m], rcond=None)[0]; cov = np.linalg.inv((X / e[m][:, None]).T @ (X / e[m][:, None]))
    print(f"  {band}: n={m.sum()} semi-amplitude at {f0:.4f} c/d = {100*np.hypot(c[1], c[2]):.2f} ± {100*np.sqrt(cov[1,1]):.2f} %")
