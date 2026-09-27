"""ZTF (IRSA light-curve service, 1.5", catflags=0, magerr<0.25): per filter LS 0.05-30 c/d, top peaks, joint peak, per-filter amplitude at the joint peak (fractional flux)."""
import sys, io, requests, numpy as np, pandas as pd
from astropy.timeseries import LombScargle
name, ra, dec = sys.argv[1], float(sys.argv[2]), float(sys.argv[3])
for k in range(3):
    r = requests.get("https://irsa.ipac.caltech.edu/cgi-bin/ZTF/nph_light_curves", params=dict(POS=f"CIRCLE {ra} {dec} 0.00042", BANDNAME="g,r,i", FORMAT="csv"), timeout=300)
    if r.status_code == 200 and r.text.startswith("oid"): break
else: sys.exit(f"{name}: IRSA query failed")
d = pd.read_csv(io.StringIO(r.text)); d = d[(d.catflags == 0) & (d.magerr < 0.25)]; open(f"ztf_{name}.csv", "w").write(r.text)
T, Y, E, B = [], [], [], []
for (o, f), s in d.groupby(["oid", "filtercode"]):
    if len(s) < 30: continue
    med = np.median(s.mag); fl = 10 ** (-0.4 * (s.mag - med)) - 1; e = 0.921 * s.magerr * (fl + 1)
    fr = np.arange(0.05, 30, 0.0002); p = LombScargle(s.hjd, fl, e).power(fr); k = np.argsort(p)[::-1]; pk = []
    for i in k:
        if all(abs(fr[i] - q) > 0.01 for q in pk): pk.append(fr[i])
        if len(pk) == 3: break
    print(f"{name} {f} n={len(s)} rms {100*np.std(fl):.1f}% top {[round(q, 4) for q in pk]}")
    T += list(s.hjd); Y += list(fl - np.mean(fl)); E += list(e); B += [f] * len(s)
if T:
    T, Y, E, B = map(np.array, (T, Y, E, B)); fr = np.arange(0.05, 30, 0.00005); ls = LombScargle(T, Y, E); p = ls.power(fr); f0 = fr[np.argmax(p)]
    print(f"{name} joint peak {f0:.5f} c/d (P = {24/f0:.3f} h) FAP {ls.false_alarm_probability(p.max(), minimum_frequency=0.05, maximum_frequency=30):.2g}")
    for b in np.unique(B):
        m = B == b; X = np.vstack([np.ones(m.sum()), np.cos(2*np.pi*f0*T[m]), np.sin(2*np.pi*f0*T[m])]).T
        c = np.linalg.lstsq(X / E[m][:, None], Y[m] / E[m], rcond=None)[0]; cov = np.linalg.inv((X / E[m][:, None]).T @ (X / E[m][:, None]))
        print(f"   {b}: semi-amplitude {100*np.hypot(c[1], c[2]):.2f} ± {100*np.sqrt(cov[1,1]):.2f} %")
