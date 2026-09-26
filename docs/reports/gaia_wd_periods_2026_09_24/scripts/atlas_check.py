import sys, numpy as np, pandas as pd
from astropy.timeseries import LombScargle
exec(open("atlas_broad.py").read().split("fr = np.arange")[0])
f0s = [float(x) for x in sys.argv[5].split(",")]
def peak(dd, f0, w=0.003):
    l = LombScargle(dd.bjd, dd.y, dd.e); ff = np.linspace(f0 - w, f0 + w, 301); pp = l.power(ff); k = np.argmax(pp)
    fap = l.false_alarm_probability(pp[k], minimum_frequency=0.05, maximum_frequency=100, method="baluev")
    # amplitude by least squares at ff[k]
    tt = dd.bjd.values; yy = dd.y.values; X = np.c_[np.sin(2*np.pi*ff[k]*tt), np.cos(2*np.pi*ff[k]*tt), np.ones(len(dd))]; W = 1/dd.e.values**2
    beta = np.linalg.solve(X.T @ (X*W[:,None]), X.T @ (W*yy)); A = np.hypot(beta[0], beta[1])
    return ff[k], A*100, fap
mid = np.median(d.bjd)
for f0 in f0s:
    print(f"f0 {f0}:")
    for lab, dd in (("all", d), ("first half", d[d.bjd < mid]), ("second half", d[d.bjd >= mid]), ("o", d[d.F == "o"]), ("c", d[d.F == "c"])):
        f, A, fap = peak(dd, f0); print(f"   {lab:12s} n {len(dd):5d}  f {f:.5f}  amp {A:.2f}%  FAP {fap:.1e}")
# nightly bins, LS < 2 c/d
d["night"] = np.floor(d.bjd - 0.5)
nb = d.groupby("night").apply(lambda g: pd.Series(dict(bjd=np.average(g.bjd), y=np.average(g.y, weights=1/g.e**2), e=1/np.sqrt(np.sum(1/g.e**2)), n=len(g)))).reset_index()
nb = nb[nb.n >= 3]
l = LombScargle(nb.bjd, nb.y, nb.e); ff = np.arange(0.02, 0.49, 0.1/(nb.bjd.max()-nb.bjd.min())); pp = l.power(ff)
top = np.argsort(pp)[::-1][:3]
print("nightly bins", len(nb), "top:", [(round(ff[k],5), round(float(l.false_alarm_probability(pp[k], minimum_frequency=0.02, maximum_frequency=0.49, method='baluev')),4)) for k in top])
