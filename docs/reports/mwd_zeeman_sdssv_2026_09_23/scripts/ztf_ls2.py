# Follow-up: Vincent+2020's 1286 s comes from one 1.7-h run (frequency resolution ~14 c/d), so search 50-85 c/d; also global FAP of the
# top peaks and a joint g+r periodogram (bands normalised separately). Amplitude upper limit = 99th percentile of fitted amplitudes
# over the 50-85 c/d window (a coherent 1.2% signal would stand out).
import numpy as np, csv
from astropy.time import Time
from astropy.coordinates import SkyCoord, EarthLocation
import astropy.units as u
from astropy.timeseries import LombScargle
rows = list(csv.DictReader(open("ztf.csv"))); c0 = SkyCoord(329.82166 * u.deg, 51.04911 * u.deg); geo = EarthLocation.from_geocentric(0, 0, 0, unit="m")
def bjd(mjd): t = Time(mjd, format="mjd", scale="utc", location=geo); return (t.tdb + t.light_travel_time(c0)).jd
T, F, E, Bn = [], [], [], []
for band in ("zg", "zr"):
    R = [r for r in rows if r["filtercode"] == band and int(r["catflags"]) == 0 and float(r["magerr"]) < 0.1]
    mjd = np.array([float(r["mjd"]) for r in R]); m = np.array([float(r["mag"]) for r in R]); e = np.array([float(r["magerr"]) for r in R])
    key = np.array([f"{r['field']}_{r['ccdid']}_{r['qid']}" for r in R]); f = 10 ** (-0.4 * m); ef = f * e / 1.0857
    for k in np.unique(key): s = np.median(f[key == k]); f[key == k] /= s; ef[key == k] /= s
    ok = np.abs(f - 1) < 5 * 1.4826 * np.median(np.abs(f - 1)); T.append(bjd(mjd[ok])); F.append(f[ok]); E.append(ef[ok]); Bn.append(np.full(ok.sum(), band))
    print(band, "n", ok.sum(), "median err %.3f" % np.median(ef[ok]), "rms %.3f" % np.std(f[ok]))
for lab, t, f, e in (("g", T[0], F[0], E[0]), ("r", T[1], F[1], E[1]), ("g+r", np.concatenate(T), np.concatenate(F), np.concatenate(E))):
    fr = np.arange(50, 85, 2e-5); ls = LombScargle(t, f, e); p = ls.power(fr, method="fast"); i = np.argmax(p)
    fap = ls.false_alarm_probability(p[i], minimum_frequency=50, maximum_frequency=85, method="baluev")
    # amplitude at the best peak and the distribution of amplitudes over the window (every 200th frequency)
    def amp(fq):
        X = np.vstack([np.ones_like(t), np.sin(2 * np.pi * fq * t), np.cos(2 * np.pi * fq * t)]).T
        b, *_ = np.linalg.lstsq(X / e[:, None], f / e, rcond=None); return np.hypot(b[1], b[2])
    As = np.array([amp(q) for q in fr[::400]])
    print(f"{lab}: 50-85 c/d max power {p[i]:.4f} at {fr[i]:.5f} c/d ({86400/fr[i]:.1f} s), amp {amp(fr[i])*100:.2f}%, FAP {fap:.2g}; "
          f"window amplitudes median {np.median(As)*100:.2f}%, 99th pct {np.percentile(As,99)*100:.2f}%")
    fr2 = np.arange(5, 300, 2e-5); p2 = ls.power(fr2, method="fast"); j = np.argmax(p2)
    print(f"      global 5-300 c/d max power {p2[j]:.4f} at {fr2[j]:.5f} c/d ({86400/fr2[j]:.1f} s), FAP {ls.false_alarm_probability(p2[j], minimum_frequency=5, maximum_frequency=300, method='baluev'):.2g}")
    # injection: add a coherent 1.2% sinusoid at 1286 s and re-measure
    finj = f + 0.012 * np.sin(2 * np.pi * (86400 / 1286.0) * t + 0.7); lsi = LombScargle(t, finj, e); pi_ = lsi.power(fr, method="fast"); k = np.argmax(pi_)
    print(f"      injection 1.2% @1286 s: recovered max power {pi_[k]:.4f} at {86400/fr[k]:.1f} s, FAP {lsi.false_alarm_probability(pi_[k], minimum_frequency=50, maximum_frequency=85, method='baluev'):.2g}")
