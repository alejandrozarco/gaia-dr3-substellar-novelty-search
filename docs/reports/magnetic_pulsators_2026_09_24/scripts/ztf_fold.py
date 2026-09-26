import sys, csv, json, numpy as np
from astropy.time import Time
from astropy.coordinates import SkyCoord, EarthLocation
import astropy.units as u
from astropy.timeseries import LombScargle
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
fn, ra, dec, f0, out, title = sys.argv[1], float(sys.argv[2]), float(sys.argv[3]), float(sys.argv[4]), sys.argv[5], sys.argv[6]
rows = list(csv.DictReader(open(fn)))
c0 = SkyCoord(ra * u.deg, dec * u.deg); geo = EarthLocation.from_geocentric(0, 0, 0, unit='m')
def bjd(mjd): t = Time(mjd, format='mjd', scale='utc', location=geo); return (t.tdb + t.light_travel_time(c0)).jd
fig, axs = plt.subplots(2, 3, figsize=(15, 7))
for k, (band, col) in enumerate((('zg', 'tab:green'), ('zr', 'tab:red'))):
    R = [r for r in rows if r['filtercode'] == band and int(r['catflags']) == 0 and float(r['magerr']) < 0.2]
    mjd = np.array([float(r['mjd']) for r in R]); m = np.array([float(r['mag']) for r in R]); e = np.array([float(r['magerr']) for r in R])
    key = np.array([f"{r['field']}_{r['ccdid']}_{r['qid']}" for r in R]); f = 10 ** (-0.4 * m); ef = f * e / 1.0857
    for kk in np.unique(key): s = np.median(f[key == kk]); f[key == kk] /= s; ef[key == kk] /= s
    ok = np.abs(f - 1) < 5 * 1.4826 * np.median(np.abs(f - 1)); t = bjd(mjd[ok]); f = f[ok]; ef = ef[ok]
    fr = np.arange(2, 400, 1e-4); ls = LombScargle(t, f, ef); p = ls.power(fr, method='fast')
    axs[k, 0].plot(fr, p, color=col, lw=0.4); axs[k, 0].set_xlabel('frequency (c/d)'); axs[k, 0].set_title(f'{band} LS 2-400 c/d; n={len(t)}', fontsize=8)
    for h in (0.5, 1, 2, 3): axs[k, 0].axvline(f0 * h, color='k', ls=':', lw=0.5)
    for j, (ff, lab) in enumerate(((f0, 'P'), (f0 / 2, '2P'))):
        ph = (t * ff) % 1; o = np.argsort(ph)
        bins = np.linspace(0, 1, 21); idx = np.digitize(ph, bins)
        fb = [np.median(f[idx == q]) for q in range(1, 21)]; eb = [1.2533 * np.std(f[idx == q]) / np.sqrt(max(1, (idx == q).sum())) for q in range(1, 21)]
        xb = 0.5 * (bins[1:] + bins[:-1])
        a = axs[k, 1 + j]; a.plot(ph, f, '.', color='0.7', ms=2); a.plot(ph + 1, f, '.', color='0.7', ms=2)
        a.errorbar(np.r_[xb, xb + 1], np.r_[fb, fb], yerr=np.r_[eb, eb], fmt='o', color=col, ms=3)
        a.set_ylim(0.8, 1.2); a.set_title(f'{band} folded on {lab} = {86400 / ff:.3f} s', fontsize=8); a.set_xlabel('phase')
fig.suptitle(title, fontsize=9); plt.tight_layout(); plt.savefig(out, dpi=80)
