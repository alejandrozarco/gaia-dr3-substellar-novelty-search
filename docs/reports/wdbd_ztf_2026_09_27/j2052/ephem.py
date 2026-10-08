"""WDJ2052-0324 ephemeris from ZTF (g+r, per oid/filter normalised) and TESS S55/S81 (120 s): frequency by LS refinement,
time of maximum light (sinusoid + harmonic fit, phase of the fitted maximum), bootstrap errors. Times in BJD_TDB (ZTF mjd = exposure start in UTC,
+ exptime/2, barycentred at Palomar; the hjd column is HJD_UTC, about 70 s = 0.012 cycles earlier)."""
import glob, numpy as np, pandas as pd
from astropy.io import fits; from astropy.timeseries import LombScargle
d = pd.read_csv("ztf_6914922055508553984.csv"); d = d[(d.catflags == 0) & (d.magerr < 0.25)]
t, y, e = [], [], []
for (o, f), s in d.groupby(["oid", "filtercode"]):
    if len(s) < 15: continue
    from astropy.time import Time as _T; from astropy.coordinates import SkyCoord as _C, EarthLocation as _E; import astropy.units as _u
    _tm = _T(s.mjd.values + s.exptime.values / 2 / 86400, format="mjd", scale="utc", location=_E.from_geodetic(-116.8597 * _u.deg, 33.3563 * _u.deg, 1712 * _u.m))
    fl = 10 ** (-0.4 * (s.mag - np.median(s.mag))) - 1; t += list((_tm.tdb + _tm.light_travel_time(_C(np.median(s.ra) * _u.deg, np.median(s.dec) * _u.deg))).jd); y += list(fl - fl.mean()); e += list(0.921 * s.magerr * (fl + 1))
t, y, e = map(np.array, (t, y, e))
for f in glob.glob("tess/mastDownload/TESS/*-s/*lc.fits"):
    h = fits.open(f)[1].data; q = (h["QUALITY"] == 0) & np.isfinite(h["PDCSAP_FLUX"]); tt = h["TIME"][q] + 2457000; yy = h["PDCSAP_FLUX"][q]; yy = yy / np.median(yy) - 1
    ee = h["PDCSAP_FLUX_ERR"][q] / np.median(h["PDCSAP_FLUX"][q]); t = np.r_[t, tt]; y = np.r_[y, yy * 0.07 / 0.104]; e = np.r_[e, ee * 0.07 / 0.104]
fr = np.linspace(14.7380, 14.7390, 20001); p = LombScargle(t, y, e).power(fr); f0 = fr[np.argmax(p)]
def fit(t, y, e, f0):
    X = np.vstack([np.ones_like(t), np.cos(2*np.pi*f0*t), np.sin(2*np.pi*f0*t), np.cos(4*np.pi*f0*t), np.sin(4*np.pi*f0*t)]).T
    c = np.linalg.lstsq(X / e[:, None], y / e, rcond=None)[0]; ph = np.linspace(0, 1, 20001)
    m = c[1] * np.cos(2*np.pi*ph) + c[2] * np.sin(2*np.pi*ph) + c[3] * np.cos(4*np.pi*ph) + c[4] * np.sin(4*np.pi*ph); return ph[np.argmax(m)]
T0ref = 2459358.0; tt = t - T0ref; phmax = fit(tt, y, e, f0); Tmax = T0ref + phmax / f0
rng = np.random.default_rng(1); fs, Ts = [], []
for k in range(200):
    i = rng.integers(0, len(t), len(t)); pp = LombScargle(t[i], y[i], e[i]).power(fr); fb = fr[np.argmax(pp)]; fs.append(fb); Ts.append(T0ref + fit(tt[i], y[i], e[i], fb) / fb)
print(f"f = {f0:.7f} +- {np.std(fs):.7f} c/d; P = {1440/f0:.4f} min; T_max(BJD) = {Tmax:.5f} +- {np.std(Ts):.5f} (n {len(t)})")
from astropy.time import Time; from astropy.coordinates import SkyCoord, EarthLocation; import astropy.units as u
c = SkyCoord(313.2053162263806, -3.4054752822694088, unit="deg"); kp = EarthLocation.of_site("kitt peak")
tm = Time(59358.45897361, format="mjd", scale="utc", location=kp); bjd = (tm.tdb + tm.light_travel_time(c)).jd
bc = c.radial_velocity_correction(obstime=Time(59358.45897361, format="mjd", scale="utc"), location=kp).to(u.km / u.s).value
ph = ((bjd - Tmax) * f0) % 1; eph = np.hypot(np.std(Ts) * f0, abs(bjd - Tmax) * np.std(fs))
print(f"DESI exposure mid (mean_mjd 59358.45897, 494 s): BJD {bjd:.5f}; photometric phase {ph:.3f} +- {eph:.3f} (0 = maximum light); barycentric correction {bc:.1f} km/s")
