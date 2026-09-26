import numpy as np, pandas as pd
from astropy.timeseries import LombScargle
d = pd.read_csv("phot_r2.5.csv"); d = d[d.band.isin(["G", "R"]) & np.isfinite(d.rel)]
parts = []
for (b, night), g in d.groupby([d.band, np.floor(d.bjd - 0.5)]):
    r = g.rel / np.median(g.rel); e = g.e_rel / np.median(g.rel); ok = np.abs(r - 1) < 5 * 1.4826 * np.median(np.abs(r - 1))
    parts.append(pd.DataFrame(dict(t=g.bjd[ok], y=r[ok] - 1, e=e[ok])))
x = pd.concat(parts); print("points", len(x), "median err %", round(100 * np.median(x.e), 1), "rms %", round(100 * np.std(x.y), 1))
fr = np.arange(12, 700, 0.05); ls = LombScargle(x.t, x.y, x.e); p = ls.power(fr); k = np.argmax(p)
print(f"top {fr[k]:.2f} c/d (P {1440/fr[k]:.1f} min) FAP {ls.false_alarm_probability(p[k], minimum_frequency=12, maximum_frequency=700, method='baluev'):.2f}")
rng = np.random.default_rng(3)
for A in (0.05, 0.10, 0.15, 0.20):
    res = []
    for Pm in (3, 10, 30, 60, 120):
        f = 1440 / Pm; n = 0
        for i in range(20):
            yy = x.y + A * np.sin(2 * np.pi * f * x.t + rng.uniform(0, 6.283)); l = LombScargle(x.t, yy, x.e)
            ff = np.linspace(f * 0.995, f * 1.005, 101); pp = l.power(ff).max()
            n += l.false_alarm_probability(pp, minimum_frequency=12, maximum_frequency=700, method="baluev") < 1e-3
        res.append(f"{Pm}min:{n}/20")
    print(f"injected {int(100*A)}%:", " ".join(res))
