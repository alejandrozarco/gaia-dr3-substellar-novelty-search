# ZTF DR light curves (IRSA API, 2" radius, catflags == 0) for northern lane candidates; GLS 0.05-50 c/d and amplitude near the Gaia frequency.
import io, requests, numpy as np, pandas as pd, sys
from astropy.timeseries import LombScargle
U = pd.read_csv("unconfirmed.csv", dtype={"source_id": str}).set_index("source_id")
for i in sys.argv[1:]:
    r = U.loc[i]; url = f"https://irsa.ipac.caltech.edu/cgi-bin/ZTF/nph_light_curves?POS=CIRCLE%20{r.ra}%20{r.dec}%200.000556&BANDNAME=g,r&FORMAT=CSV"
    try: d = pd.read_csv(io.StringIO(requests.get(url, timeout=400).text)); d = d[d.catflags == 0]
    except Exception as ex: print(i, "HOLE: ZTF query failed", str(ex)[:80], flush=True); continue
    if len(d) < 30: print(i, "ZTF points", len(d)); continue
    T, Y, E = [], [], []
    for (oid, band), s in d.groupby(["oid", "filtercode"]):
        if len(s) < 20: continue
        f = 10 ** (-0.4 * (s.mag.values - np.median(s.mag))) - 1; e = 0.921 * s.magerr.values
        T += list(s.hjd.values); Y += list(f); E += list(e)
    T, Y, E = map(np.array, (T, Y, E)); fg = r.gls_freq_g_fov
    fr = np.arange(0.05, 50, 0.2 / (T.max() - T.min())); ls = LombScargle(T, Y, E); P = ls.power(fr); k = np.argmax(P)
    w = np.abs(fr - fg) < 0.01; j = np.argmax(P[w]); fw = fr[w][j]
    X = np.vstack([np.ones_like(T), np.sin(2*np.pi*fw*T), np.cos(2*np.pi*fw*T)]).T; W = 1/E**2; p = np.linalg.solve(X.T @ (X*W[:, None]), X.T @ (W*Y)); C = np.linalg.inv(X.T @ (X*W[:, None])); c2 = max(np.sum(W*(Y-X@p)**2)/(len(T)-3), 1)
    rank = int(np.sum(P > P[w][j]))
    print(f"{i}: n {len(T)}; top {fr[k]:.5f} c/d (FAP {ls.false_alarm_probability(P[k], minimum_frequency=0.05, maximum_frequency=50, method='baluev'):.2g}); near Gaia {fg:.5f}: {fw:.5f} amp {100*np.hypot(p[1],p[2]):.2f} +- {100*np.sqrt(c2*(C[1,1]+C[2,2])/2):.2f} %, power rank {rank}", flush=True)
