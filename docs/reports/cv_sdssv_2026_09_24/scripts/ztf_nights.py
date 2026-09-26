# Intra-night ZTF light curves: nights with >= N points in a band; plot mag vs hours; LS per night for short periods.
import sys, pandas as pd, numpy as np, json
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
from astropy.timeseries import LombScargle
g = sys.argv[1]; nmin = int(sys.argv[2]) if len(sys.argv) > 2 else 15
d = pd.read_csv(f"/tmp/fanout/cv/ztf/{g}_clean.csv")
d["night"] = np.floor(d.bjd_tdb - 0.5).astype(int)
grp = d.groupby(["night", "filtercode"]).size().reset_index(name="n")
grp = grp[grp.n >= nmin].sort_values("n", ascending=False)
print(grp.head(12).to_string())
sel = grp.head(8)
fig, axes = plt.subplots(len(sel), 1, figsize=(10, 2.2 * len(sel)), squeeze=False)
res = []
for ax, (_, r) in zip(axes[:, 0], sel.iterrows()):
    s = d[(d.night == r.night) & (d.filtercode == r.filtercode)].sort_values("bjd_tdb")
    t = (s.bjd_tdb - s.bjd_tdb.min()) * 24
    ax.errorbar(t, s.mag, s.magerr, fmt="o", ms=3, color="g" if r.filtercode == "zg" else "r")
    ax.invert_yaxis(); ax.set_title(f"{g} night {r.night} {r.filtercode} N={r.n} span={t.max():.2f} h", fontsize=8)
    if t.max() > 1.0 and len(s) >= 15:
        ls = LombScargle(s.bjd_tdb, s.mag, s.magerr); f, p = ls.autopower(minimum_frequency=24 / (t.max()), maximum_frequency=24 / 0.1, samples_per_peak=20)
        i = np.argmax(p); res.append(dict(night=int(r.night), band=r.filtercode, n=int(r.n), span_h=round(float(t.max()), 2), amp=round(float(s.mag.max() - s.mag.min()), 2),
                                          best_P_h=round(float(24 / f[i]), 3), power=round(float(p[i]), 3), fap=float(ls.false_alarm_probability(p[i]))))
axes[-1, 0].set_xlabel("hours")
fig.tight_layout(); fig.savefig(f"/tmp/fanout/cv/plots/ztf_nights_{g}.png", dpi=85)
print(json.dumps(res, indent=0))
