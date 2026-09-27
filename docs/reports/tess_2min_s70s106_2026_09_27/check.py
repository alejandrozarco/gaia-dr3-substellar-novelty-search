"""ZTF attribution check for TESS sweep candidates: fetch the star's own ZTF light curve (1.5"), report the top masked peak and
the power/semi-amplitude at the TESS frequency. Usage: python check.py <gaia> <ra> <dec> <f_tess> [label]"""
import io, sys, time, requests, warnings; warnings.filterwarnings("ignore")
import numpy as np, pandas as pd
from astropy.timeseries import LombScargle
gid, ra, dec, F0 = sys.argv[1], float(sys.argv[2]), float(sys.argv[3]), float(sys.argv[4]); lab = sys.argv[5] if len(sys.argv) > 5 else gid
d = None
for k in range(3):
    try:
        r = requests.get("https://irsa.ipac.caltech.edu/cgi-bin/ZTF/nph_light_curves", params=dict(POS=f"CIRCLE {ra} {dec} 0.00042", BANDNAME="g,r", FORMAT="csv"), timeout=300)
        if r.ok and r.text.count("\n") > 3: d = pd.read_csv(io.StringIO(r.text)); break
    except Exception as ex: print(lab, "retry", k, str(ex)[:40]); time.sleep(15)
if d is None or len(d) < 50: print(gid, lab, "ZTF EMPTY/short", 0 if d is None else len(d)); sys.exit()
d = d[(d.catflags == 0) & (d.magerr < 0.25)]; d.to_csv(f"ztf_{gid}.csv", index=False)
print("=====", gid, lab, len(d), d.filtercode.value_counts().to_dict())
for b in ("zg", "zr"):
    x = d[d.filtercode == b]
    if len(x) < 40: continue
    t, y, e = x.mjd.values, 10 ** (-0.4 * (x.mag.values - np.median(x.mag))) - 1, 0.921 * x.magerr.values
    FR = np.linspace(0.5, 50, 400000); ls = LombScargle(t, y, e); p = ls.power(FR)
    mask = np.ones_like(FR, bool)
    for n in (1, 2, 3): mask &= np.abs(FR - n) > 0.03
    for fq in (F0, 2 * F0, F0 / 2): mask2 = np.abs(FR - fq) < 0.01
    k = np.argmax(np.where(mask, p, 0)); w = (np.abs(FR - F0) < 0.01) | (np.abs(FR - 2 * F0) < 0.01) | (np.abs(FR - F0 / 2) < 0.01); kk = np.argmax(p * w)
    X = np.vstack([np.sin(2 * np.pi * FR[kk] * t), np.cos(2 * np.pi * FR[kk] * t), np.ones_like(t)]).T
    c = np.linalg.lstsq(X / e[:, None], y / e, rcond=None)[0]; cov = np.linalg.inv((X / e[:, None]).T @ (X / e[:, None]))
    a, ea = np.hypot(c[0], c[1]), np.sqrt((cov[0, 0] + cov[1, 1]) / 2)
    print(f"  {b}: n {len(t)}, top {FR[k]:.5f} (P {24/FR[k]:.4f} h) FAP {ls.false_alarm_probability(p[k], minimum_frequency=0.5, maximum_frequency=50):.2g}; at TESS f/2f/f half: {FR[kk]:.5f} FAP {ls.false_alarm_probability(p[kk], minimum_frequency=0.5, maximum_frequency=50):.2g}, semi-amp {100*a:.2f} +- {100*ea:.2f}%")
