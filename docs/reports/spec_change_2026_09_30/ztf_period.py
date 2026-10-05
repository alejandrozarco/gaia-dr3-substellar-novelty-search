"""ZTF data-release photometry (IRSA, 1.5 arcsec, catflags 0, magerr < 0.3) of a radial-velocity candidate and a Lomb-Scargle
search 0.5-100 c/d on g+r combined (per-filter medians removed); FAP from 300 shuffles within filter (2026-09-30).
Usage: python ztf_period.py <name> <ra> <dec> -> results/ztf_<name>.csv and printed top peaks."""
import sys, io, os, requests, numpy as np, pandas as pd
from astropy.timeseries import LombScargle
H = os.path.dirname(os.path.abspath(__file__)); nm, ra, de = sys.argv[1], float(sys.argv[2]), float(sys.argv[3]); rng = np.random.default_rng(5)
q = requests.get("https://irsa.ipac.caltech.edu/cgi-bin/ZTF/nph_light_curves", params=dict(POS=f"CIRCLE {ra} {de} 0.00042", BANDNAME="g,r", FORMAT="csv"), timeout=300)
d = pd.read_csv(io.StringIO(q.text)); d.to_csv(os.path.join(H, "results", f"ztf_{nm}.csv"), index=False)
d = d[(d.catflags == 0) & (d.magerr < 0.3)]; parts = []
for b in ("zg", "zr"):
    x = d[d.filtercode == b]
    if len(x) == 0: continue
    x = x[x.oid == x.oid.value_counts().index[0]]; x = x.assign(y=x.mag - x.mag.median()); parts.append(x); print(nm, b, len(x), "points, median %.2f, rms %.3f" % (x.mag.median(), x.y.std()))
D = pd.concat(parts); t, y, e = D.hjd.values, D.y.values, D.magerr.values; fr = np.linspace(0.5, 100, 400000)
p = LombScargle(t, y, e).power(fr); top = []; 
for i in np.argsort(p)[::-1]:
    if all(abs(fr[i] - f) > 0.01 for f in top): top.append(fr[i])
    if len(top) == 5: break
mx = []
for s in range(300):
    yy = y.copy()
    for b in ("zg", "zr"):
        ii = np.where(D.filtercode.values == b)[0]; yy[ii] = rng.permutation(yy[ii])
    mx.append(LombScargle(t, yy, e).power(fr[::8]).max())
for f in top: pw = p[np.argmin(abs(fr - f))]; print("  f %.5f c/d  P %.4f h  power %.4f  FAP %.3f" % (f, 24 / f, pw, (np.sum(np.array(mx) >= pw) + 1) / 301))
