"""ZTF DR light curve check of a gas-disc white dwarf: seasonal medians, dips (runs of low points), Lomb-Scargle.
python ztf_gas.py <gaia> <ra> <dec>"""
import sys, requests, io, pandas as pd, numpy as np, matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
from astropy.timeseries import LombScargle
g, ra, dec = sys.argv[1], float(sys.argv[2]), float(sys.argv[3])
for k in range(3):
    r = requests.get("https://irsa.ipac.caltech.edu/cgi-bin/ZTF/nph_light_curves", params=dict(POS=f"CIRCLE {ra} {dec} 0.0005", BANDNAME="g,r,i", FORMAT="csv"), timeout=300)
    if r.status_code == 200 and r.text.startswith("oid"): break
else: sys.exit("HOLE: IRSA query failed")
df = pd.read_csv(io.StringIO(r.text)); df.to_csv(f"ztf_{g}.csv", index=False)
print("rows", len(df), df.groupby(["oid", "filtercode"]).size().to_dict())
df = df[(df.catflags == 0) & (df.magerr < 0.25)]
fig, ax = plt.subplots(2, 1, figsize=(11, 6)); parts = []
for (o, f), s in df.groupby(["oid", "filtercode"]):
    if len(s) < 20: continue
    med = np.median(s.mag); fl = 10 ** (-0.4 * (s.mag - med)); e = 0.921 * s.magerr * fl; z = (fl - 1) / e
    yr = 2000 + (s.mjd - 51544.5) / 365.25; seas = np.floor(yr + 0.3)
    sm = s.assign(fl=fl, e=e, z=z, seas=seas).groupby("seas").agg(n=("fl", "size"), med=("fl", "median"), err=("e", lambda x: 1.2533 * np.median(x) / np.sqrt(len(x))))
    print(f, o, len(s), "median mag", round(med, 3), "rms%", round(100 * np.std(fl), 2), "err%", round(100 * np.median(e), 2))
    print("  seasonal median flux (%):", {int(k): (round(100 * (v.med - 1), 2), round(100 * v.err, 2), int(v.n)) for k, v in sm.iterrows()})
    low = z < -3; print("  points < -3 sigma:", int(low.sum()), "of", len(z), "expected ~", round(0.00135 * len(z), 1), "| < -4 sigma:", int((z < -4).sum()))
    if low.sum(): print("   low-point MJDs:", [round(x, 3) for x in s.mjd[low].values[:15]])
    col = dict(zg="g", zr="r", zi="k")[f]
    ax[0].errorbar(yr, fl - 1, e, fmt=".", ms=2, color=col, alpha=0.4, elinewidth=0.3)
    ax[0].errorbar(sm.index + 0.5, sm.med - 1, sm.err, fmt="s", ms=5, color=col, label=f"{f} seasonal median")
    parts.append(pd.DataFrame(dict(t=s.hjd.values, f=fl.values - 1, e=e.values)))
ax[0].set_ylim(-0.4, 0.4); ax[0].axhline(0, color="0.5", lw=0.5); ax[0].set_xlabel("year"); ax[0].set_ylabel("fractional flux"); ax[0].legend(fontsize=7)
d = pd.concat(parts); fr = np.arange(0.02, 300, 0.1 / (d.t.max() - d.t.min())); ls = LombScargle(d.t, d.f, d.e); p = ls.power(fr, method="fast")
ax[1].plot(fr, p, "k", lw=0.3); ax[1].set_xscale("log"); ax[1].set_xlabel("frequency (c/d)"); ax[1].set_ylabel("LS power")
seen = []
for i in np.argsort(p)[::-1]:
    if all(abs(fr[i] - s) > 0.01 for s in seen): seen.append(fr[i])
    if len(seen) == 5: break
for f in seen:
    pw = ls.power(f); print(f"f {f:.5f} c/d P {24/f:.4f} h amp~{100*np.sqrt(4*pw*np.var(d.f)):.2f}% FAP {ls.false_alarm_probability(pw, minimum_frequency=0.02, maximum_frequency=300, method='baluev'):.2e}")
ax[0].set_title(f"Gaia DR3 {g}: ZTF (catflags 0)", fontsize=9); plt.tight_layout(); plt.savefig(f"ztf_{g}.png", dpi=90)
