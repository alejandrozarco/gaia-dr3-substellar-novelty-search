"""Consistency test for ZTF detections: light curves detrended by subtracting the median of each (oid, filter, 60-day block);
Lomb-Scargle top peak (0.5-50 c/d, 1/2/3 c/d +-0.03 masked) recomputed for g only, r only, first half and second half of the
time span. A detection passes if the original frequency (or its 1-day aliases f+-1, f+-2 excluded) is recovered within
0.002 c/d as the top peak in at least 3 of the 4 subsets."""
import sys, numpy as np, pandas as pd
from astropy.timeseries import LombScargle
import jestin_ztf as J
def lc(g):
    d = pd.read_csv(f"ztf/{g}.csv"); d = d[(d.catflags == 0) & (d.magerr < 0.25)]
    t, y, e, b = [], [], [], []
    for (o, f), s in d.groupby(["oid", "filtercode"]):
        if len(s) < 15: continue
        fl = 10 ** (-0.4 * (s.mag - np.median(s.mag))) - 1; blk = (s.hjd // 60).values; fl = fl.values.copy()
        for k in np.unique(blk):
            m = blk == k; fl[m] -= np.median(fl[m])
        t += list(s.hjd); y += list(fl); e += list(0.921 * s.magerr * (fl + 1)); b += [f] * len(s)
    return map(np.array, (t, y, e, b))
def top(t, y, e):
    if len(t) < 40: return np.nan
    p = LombScargle(t, y, e).power(J.FR); p[~J.MASK] = 0; return J.FR[np.argmax(p)]
rows = []
for g, f0 in zip(sys.argv[1::2], map(float, sys.argv[2::2])):
    t, y, e, b = lc(g); mid = np.median(t)
    ft = top(t, y, e); sub = dict(g=top(t[b == "zg"], y[b == "zg"], e[b == "zg"]), r=top(t[b == "zr"], y[b == "zr"], e[b == "zr"]),
        h1=top(t[t < mid], y[t < mid], e[t < mid]), h2=top(t[t >= mid], y[t >= mid], e[t >= mid]))
    ok = sum(abs(v - f0) < 0.002 for v in sub.values() if np.isfinite(v))
    rows.append(dict(GaiaDR3=g, f0=f0, f_detrended=round(ft, 5), **{k: round(v, 5) for k, v in sub.items()}, n_agree=ok, detrended_same=abs(ft - f0) < 0.002))
print(pd.DataFrame(rows).to_string(index=False))
