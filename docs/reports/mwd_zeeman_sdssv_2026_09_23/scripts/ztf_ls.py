# J2159+5102 (Gaia DR3 1980205739970324224): ZTF DR light curve periodogram, testing the 1286-s signal that Vincent+2020 reported
# as ZZ Ceti pulsation (Table 2: P 1286 s, amplitude 1.2%, FAP < 0.1%). Coherent over 2018-2025 => rotation-like; absent => fine.
# BJD_TDB times; clean catflags == 0; flux relative to per-band (and per field/ccd/quadrant) median; LS 5-300 c/d.
import numpy as np, csv, json
from astropy.time import Time
from astropy.coordinates import SkyCoord, EarthLocation
import astropy.units as u
from astropy.timeseries import LombScargle
rows = list(csv.DictReader(open("ztf.csv")))
c0 = SkyCoord(329.82166 * u.deg, 51.04911 * u.deg); geo = EarthLocation.from_geocentric(0, 0, 0, unit="m")
def bjd(mjd): t = Time(mjd, format="mjd", scale="utc", location=geo); return (t.tdb + t.light_travel_time(c0)).jd
out = {}
allt, allf, alle = [], [], []
for band in ("zg", "zr", "zi"):
    R = [r for r in rows if r["filtercode"] == band and int(r["catflags"]) == 0 and float(r["magerr"]) < 0.1]
    if len(R) < 30: continue
    mjd = np.array([float(r["mjd"]) for r in R]); m = np.array([float(r["mag"]) for r in R]); e = np.array([float(r["magerr"]) for r in R])
    key = np.array([f"{r['field']}_{r['ccdid']}_{r['qid']}" for r in R])
    f = 10 ** (-0.4 * m); ef = f * e / 1.0857
    for k in np.unique(key): f[key == k] /= np.median(f[key == k]); ef[key == k] /= 1.0
    ef = ef / np.median(10 ** (-0.4 * m))
    # 5-sigma clip
    ok = np.abs(f - 1) < 5 * 1.4826 * np.median(np.abs(f - 1)); t = bjd(mjd[ok]); f, ef = f[ok], ef[ok]
    freq = np.arange(5, 300, 2e-5)
    ls = LombScargle(t, f, ef); p = ls.power(freq, method="fast")
    top = np.argsort(p)[::-1]; peaks = []
    for i in top:
        if all(abs(freq[i] - q[0]) > 0.02 for q in peaks): peaks.append((freq[i], p[i]))
        if len(peaks) == 8: break
    f0 = 86400 / 1286.0; w = np.abs(freq - f0) < 1.0; i0 = np.argmax(np.where(w, p, 0))
    amp = np.sqrt(4 * p[i0] * np.var(f) / 1) if False else None
    # amplitude at the best frequency near 1286 s via a sinusoid fit
    X = np.vstack([np.ones_like(t), np.sin(2 * np.pi * freq[i0] * t), np.cos(2 * np.pi * freq[i0] * t)]).T
    b, *_ = np.linalg.lstsq(X / ef[:, None], f / ef, rcond=None); A = np.hypot(b[1], b[2])
    fap = ls.false_alarm_probability(p[i0], minimum_frequency=5, maximum_frequency=300, method="baluev")
    out[band] = dict(n=int(len(t)), span_d=float(t.max() - t.min()), top_peaks=[(float(a), float(b_)) for a, b_ in peaks],
                     near1286=dict(freq=float(freq[i0]), P_s=float(86400 / freq[i0]), power=float(p[i0]), amp_frac=float(A), fap_baluev=float(fap)))
    print(band, "n", len(t), f"span {t.max()-t.min():.0f} d | top peaks (c/d, P s, power):", [(round(a, 4), round(86400 / a, 1), round(b_, 4)) for a, b_ in peaks[:5]])
    print(f"   best within +-1 c/d of 1286 s: f {freq[i0]:.5f} c/d = {86400/freq[i0]:.2f} s, power {p[i0]:.4f}, amplitude {A*100:.2f}%, Baluev FAP {fap:.2e}")
    allt.append(t); allf.append(f); alle.append(ef)
json.dump(out, open("ztf_ls.json", "w"), indent=1)
