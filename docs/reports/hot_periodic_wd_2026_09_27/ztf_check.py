"""ZTF DR light curves (IRSA nph_light_curves, 1.5" radius, catflags = 0) of Gaia periods of 5-32 h. Per band: Lomb-Scargle 0.2-5 c/d, highest peak,
power and semi-amplitude at the Gaia frequency (+-0.01 c/d), g/r amplitude ratio at the combined-band best frequency near the Gaia value.
A reply with fewer than 20 rows is reported as EMPTY (not a null). Usage: python ztf_check.py <gaia_dr3> <ra> <dec> <gaia_freq_cd>"""
import sys, io, numpy as np, pandas as pd, requests, warnings; warnings.filterwarnings("ignore")
from astropy.timeseries import LombScargle
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
gid, ra, dec, fg = sys.argv[1], float(sys.argv[2]), float(sys.argv[3]), float(sys.argv[4])
r = requests.get("https://irsa.ipac.caltech.edu/cgi-bin/ZTF/nph_light_curves", params=dict(POS=f"CIRCLE {ra} {dec} 0.00042", BANDNAME="g,r", FORMAT="csv"), timeout=300)
d = pd.read_csv(io.StringIO(r.text)) if r.ok and r.text.count("\n") > 1 else pd.DataFrame()
if len(d) < 20: print(gid, "EMPTY", len(d)); sys.exit()
d = d[d.catflags == 0]; d.to_csv(f"ztf_{gid}.csv", index=False); FR = np.linspace(0.2, 5, 400000); res = {}
fig, ax = plt.subplots(1, 3, figsize=(15, 3.5))
for b, col in (("zg", "g"), ("zr", "r")):
    x = d[d.filtercode == b]
    if len(x) < 30: continue
    t, m, e = x.mjd.values, x.mag.values, x.magerr.values; y = 10 ** (-0.4 * (m - np.median(m))) - 1
    ls = LombScargle(t, y, e); p = ls.power(FR); k = np.argmax(p); w = np.abs(FR - fg) < 0.01; kk = np.argmax(p * w)
    X = np.vstack([np.sin(2 * np.pi * FR[kk] * t), np.cos(2 * np.pi * FR[kk] * t), np.ones_like(t)]).T; c = np.linalg.lstsq(X / e[:, None], y / e, rcond=None)[0]
    res[col] = dict(n=len(t), f_peak=round(FR[k], 5), P_peak_h=round(24 / FR[k], 4), fap_peak=float(f"{ls.false_alarm_probability(p[k], minimum_frequency=0.2, maximum_frequency=5):.2g}"),
                    f_near_gaia=round(FR[kk], 5), fap_near_gaia=float(f"{ls.false_alarm_probability(p[kk], minimum_frequency=0.2, maximum_frequency=5):.2g}"), amp_pct=round(100 * np.hypot(c[0], c[1]), 2))
    ax[0].plot(FR, p, lw=.5, color=col, label=col); ph = (t * FR[kk]) % 1; ax[1 if col == "g" else 2].errorbar(ph, y, e, fmt=".", ms=2, color=col, alpha=.3)
    bn = np.linspace(0, 1, 21); ax[1 if col == "g" else 2].plot((bn[:-1] + bn[1:]) / 2, [np.median(y[(ph >= a) & (ph < b2)]) for a, b2 in zip(bn[:-1], bn[1:])], "ko")
    ax[1 if col == "g" else 2].set_ylim(np.percentile(y, 2), np.percentile(y, 98)); ax[1 if col == "g" else 2].set_xlabel(f"phase ({col}, f = {FR[kk]:.5f} c/d)")
ax[0].axvline(fg, color="k", ls=":"); ax[0].legend(); ax[0].set_xlabel("frequency (c/d)"); fig.suptitle(f"Gaia DR3 {gid}, ZTF", fontsize=9); plt.tight_layout(); plt.savefig(f"ztf_{gid}.png", dpi=90)
print(gid, res)
