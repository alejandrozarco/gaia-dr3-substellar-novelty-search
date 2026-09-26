"""Targeted ZTF test of Gaia DR3 GLS frequencies (todo2.csv): IRSA light curves (2 arcsec, catflags 0, magerr < 0.25) saved to
ztf/<id>.csv; fractional flux per oid/band; GLS 0.05-50 c/d; power and rank at the best frequency within +-0.01 c/d of f_gaia;
Baluev FAP there. Failed queries print HOLE. One line per star to ztf_check2.out."""
import io, os, time, requests, numpy as np, pandas as pd, sys
from astropy.timeseries import LombScargle
U = pd.read_csv("todo2.csv", dtype={"source_id": str})
done = set(l.split(":")[0].split()[0] for l in open("ztf_check2.out")) if os.path.exists("ztf_check2.out") else set()
out = open("ztf_check2.out", "a")
for r in U.itertuples():
    i = r.source_id
    if i in done: continue
    p = f"ztf/{i}.csv"
    try:
        if not os.path.exists(p):
            q = requests.get("https://irsa.ipac.caltech.edu/cgi-bin/ZTF/nph_light_curves", params=dict(POS=f"CIRCLE {r.ra} {r.dec} 0.000556", BANDNAME="g,r", FORMAT="csv"), timeout=600)
            if not q.text.startswith("oid"): raise IOError("non-CSV reply")
            open(p, "w").write(q.text)
        d = pd.read_csv(p); d = d[(d.catflags == 0) & (d.magerr < 0.25)]
    except Exception as ex:
        out.write(f"{i}: HOLE {type(ex).__name__}\n"); out.flush(); continue
    T, Y, E = [], [], []
    for (oid, band), s in d.groupby(["oid", "filtercode"]):
        if len(s) < 20: continue
        f = 10 ** (-0.4 * (s.mag.values - np.median(s.mag))) - 1; T += list(s.hjd.values); Y += list(f); E += list(0.921 * s.magerr.values)
    if len(T) < 40:
        out.write(f"{i}: too few ZTF points ({len(T)})\n"); out.flush(); continue
    T, Y, E = map(np.array, (T, Y, E)); fg = r.gls_freq_g_fov
    fr = np.arange(0.05, 50, 0.2 / (T.max() - T.min())); ls = LombScargle(T, Y, E); P = ls.power(fr); k = np.argmax(P)
    w = np.abs(fr - fg) < 0.01; j = np.argmax(P[w]); fw = fr[w][j]; rank = int(np.sum(P > P[w][j]))
    fap = ls.false_alarm_probability(P[w][j], minimum_frequency=0.05, maximum_frequency=50, method="baluev")
    out.write(f"{i}: n {len(T)}; top {fr[k]:.5f}; gaia {fg:.5f}; near {fw:.5f} rank {rank} FAP {fap:.2g}\n"); out.flush()
    time.sleep(2)
