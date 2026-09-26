# J2159+5102 ZTF follow-up checks: (1) per-season periodograms (50-85 c/d), incl. the 2020 season of the Vincent+2020 run
# (2020-08-07); (2) injection-recovery of coherent sinusoids over a grid of amplitude x phase x frequency, through the same
# normalisation; recovered = highest 50-85 c/d peak within 0.01 c/d of the injected frequency with Baluev FAP < 1e-3;
# (3) spectral window (periodogram of the sampling), to test whether the r-band 48.00 c/d (1800 s) peak is a sampling alias.
import numpy as np, csv
from astropy.time import Time
from astropy.coordinates import SkyCoord, EarthLocation
import astropy.units as u
from astropy.timeseries import LombScargle
rows = list(csv.DictReader(open("ztf.csv"))); c0 = SkyCoord(329.82166 * u.deg, 51.04911 * u.deg); geo = EarthLocation.from_geocentric(0, 0, 0, unit="m")
def bjd(mjd): t = Time(mjd, format="mjd", scale="utc", location=geo); return (t.tdb + t.light_travel_time(c0)).jd
D = {}
for band in ("zg", "zr"):
    R = [r for r in rows if r["filtercode"] == band and int(r["catflags"]) == 0 and float(r["magerr"]) < 0.1]
    mjd = np.array([float(r["mjd"]) for r in R]); m = np.array([float(r["mag"]) for r in R]); e = np.array([float(r["magerr"]) for r in R])
    key = np.array([f"{r['field']}_{r['ccdid']}_{r['qid']}" for r in R]); f = 10 ** (-0.4 * m); ef = f * e / 1.0857
    for k in np.unique(key): s = np.median(f[key == k]); f[key == k] /= s; ef[key == k] /= s
    ok = np.abs(f - 1) < 5 * 1.4826 * np.median(np.abs(f - 1)); D[band] = (bjd(mjd[ok]), f[ok], ef[ok], mjd[ok])
fr = np.arange(50, 85, 5e-5)
print("(1) per season, 50-85 c/d")
for band, (t, f, e, mjd) in D.items():
    yr = np.floor(Time(mjd, format="mjd").decimalyear).astype(int)
    for y in np.unique(yr):
        m = yr == y
        if m.sum() < 25: continue
        ls = LombScargle(t[m], f[m], e[m]); p = ls.power(fr, method="fast"); i = np.argmax(p)
        print(f"   {band} {y}: n {m.sum():4d} max power {p[i]:.3f} at {86400/fr[i]:.1f} s, FAP {ls.false_alarm_probability(p[i], minimum_frequency=50, maximum_frequency=85, method='baluev'):.2g}")
print("(2) injection-recovery (coherent sinusoid), fraction recovered over 8 phases x 5 frequencies")
rng = np.random.default_rng(3)
for band, (t, f, e, mjd) in D.items():
    for A in (0.003, 0.005, 0.008, 0.012):
        rec = 0; n = 0
        for f0 in np.linspace(60, 75, 5):
            for ph in np.linspace(0, 2 * np.pi, 8, endpoint=False):
                y = f + A * np.sin(2 * np.pi * f0 * t + ph); ls = LombScargle(t, y, e); p = ls.power(fr, method="fast"); i = np.argmax(p)
                n += 1; rec += (abs(fr[i] - f0) < 0.01) and ls.false_alarm_probability(p[i], minimum_frequency=50, maximum_frequency=85, method="baluev") < 1e-3
        print(f"   {band} A = {A*100:.1f}%: recovered {rec}/{n}")
print("(3) spectral window: top peaks of the sampling periodogram (constant signal) 5-300 c/d")
for band, (t, f, e, mjd) in D.items():
    fw = np.arange(5, 300, 1e-4); W = LombScargle(t, np.ones_like(t), fit_mean=False, center_data=False).power(fw, method="fast")
    top = np.argsort(W)[::-1]; pk = []
    for i in top:
        if all(abs(fw[i] - q) > 0.05 for q in pk): pk.append(fw[i])
        if len(pk) == 6: break
    print(f"   {band}: window peaks (c/d): {[round(x, 3) for x in pk]}; window power at 48.00 c/d = {W[np.argmin(abs(fw-47.997))]:.3f}")
