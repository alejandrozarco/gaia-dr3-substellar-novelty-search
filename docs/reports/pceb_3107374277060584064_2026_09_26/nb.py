"""ZTF light curves of the hot WD Gaia DR3 3107374277060584064 and of its 4.1" neighbour Gaia DR3 3107374272762041856 (G 16.17);
Lomb-Scargle of each, fold at the WD's peak. Output: printed, nb_fold.png"""
import io, requests, numpy as np, pandas as pd, matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
from astropy.timeseries import LombScargle
def ztf(ra, dec, rad=0.0005):
    r = requests.get("https://irsa.ipac.caltech.edu/cgi-bin/ZTF/nph_light_curves", params=dict(POS=f"CIRCLE {ra} {dec} {rad}", BANDNAME="g,r,i", FORMAT="csv"), timeout=300)
    d = pd.read_csv(io.StringIO(r.text)); return d[(d.catflags == 0) & (d.magerr < 0.25)]
out = {}
for name, ra, dec in (("WD", 101.158714, -0.764028), ("F8 neighbour", 101.15864164532, -0.76287948859)):
    d = ztf(ra, dec); d.to_csv(f"ztf_{name.split()[0]}.csv", index=False); out[name] = d
    print(name, {f"{f}:{o}": len(s) for (o, f), s in d.groupby(["oid", "filtercode"])})
    for (o, f), s in d.groupby(["oid", "filtercode"]):
        if len(s) < 20: continue
        fl = 10 ** (-0.4 * (s.mag - s.mag.median())) - 1
        fr = np.arange(0.05, 20, 0.0002); ls = LombScargle(s.hjd, fl, s.magerr); p = ls.power(fr)
        k = np.argsort(p)[::-1][:1]; p0 = ls.power(1.68666)
        print(f"  {f} {o} n={len(s)} med={s.mag.median():.3f} rms={100*fl.std():.2f}% best {fr[k[0]]:.5f} c/d pow {p[k[0]]:.3f}; power at 1.68666 = {p0:.3f} (FAP {ls.false_alarm_probability(p0):.1e})")
P = 1 / 1.68666
fig, ax = plt.subplots(1, 2, figsize=(10, 4), sharey=True)
for a, (name, d) in zip(ax, out.items()):
    for (o, f), s in d.groupby(["oid", "filtercode"]):
        if len(s) < 20: continue
        fl = 10 ** (-0.4 * (s.mag - s.mag.median())) - 1; ph = (s.hjd / P) % 1
        a.errorbar(np.r_[ph, ph + 1], np.r_[fl, fl], np.r_[s.magerr, s.magerr] * 0.92, fmt=".", ms=3, label=f"{f}", alpha=.6)
    a.set_title(f"{name}: ZTF folded at P = {24*P:.3f} h"); a.set_xlabel("phase"); a.legend()
ax[0].set_ylabel("relative flux - 1"); plt.tight_layout(); plt.savefig("nb_fold.png", dpi=90)
