# ZTF Lomb-Scargle for a single object: flux, catflags==0, per field/ccd/quadrant normalisation, BJD_TDB, 5-sigma clipping.
import sys, csv, json, numpy as np
from astropy.time import Time
from astropy.coordinates import SkyCoord, EarthLocation
import astropy.units as u
from astropy.timeseries import LombScargle
fn, ra, dec, fmin, fmax = sys.argv[1], float(sys.argv[2]), float(sys.argv[3]), float(sys.argv[4]), float(sys.argv[5])
rows = list(csv.DictReader(open(fn)))
c0 = SkyCoord(ra * u.deg, dec * u.deg); geo = EarthLocation.from_geocentric(0, 0, 0, unit='m')
def bjd(mjd):
    t = Time(mjd, format='mjd', scale='utc', location=geo); return (t.tdb + t.light_travel_time(c0)).jd
res = {}
allt, allf, alle = [], [], []
for band in ('zg', 'zr'):
    R = [r for r in rows if r['filtercode'] == band and int(r['catflags']) == 0 and float(r['magerr']) < 0.2]
    if len(R) < 30: continue
    mjd = np.array([float(r['mjd']) for r in R]); m = np.array([float(r['mag']) for r in R]); e = np.array([float(r['magerr']) for r in R])
    key = np.array([f"{r['field']}_{r['ccdid']}_{r['qid']}" for r in R]); f = 10 ** (-0.4 * m); ef = f * e / 1.0857
    for k in np.unique(key):
        s = np.median(f[key == k]); f[key == k] /= s; ef[key == k] /= s
    ok = np.abs(f - 1) < 5 * 1.4826 * np.median(np.abs(f - 1))
    t = bjd(mjd[ok]); f = f[ok]; ef = ef[ok]
    fr = np.arange(fmin, fmax, 2e-5 if fmax < 100 else 5e-5)
    ls = LombScargle(t, f, ef); p = ls.power(fr, method='fast'); i = np.argmax(p)
    fap = ls.false_alarm_probability(p[i], minimum_frequency=fmin, maximum_frequency=fmax, method='baluev')
    # amplitude of best sinusoid
    mdl = ls.model(t, fr[i]); amp = (mdl.max() - mdl.min()) / 2
    top = np.argsort(p)[::-1]; pk = []
    for j in top:
        if all(abs(fr[j] - q) > 0.01 for q in pk): pk.append(fr[j])
        if len(pk) == 5: break
    res[band] = dict(n=int(ok.sum()), span_d=float(t.max() - t.min()), best_f=float(fr[i]), best_P_s=float(86400 / fr[i]), power=float(p[i]), fap=float(fap), semi_amp=float(amp),
                     top_f=[round(x, 5) for x in pk])
    allt.append(t); allf.append(f); alle.append(ef)
print(json.dumps(res, indent=1))
