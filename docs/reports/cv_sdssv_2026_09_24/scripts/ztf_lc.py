# ZTF light curve for one position (IRSA nph_light_curves, 2.2" = 0.0006 deg cone, g/r/i). Analysis in flux space: catflags==0,
# flux = 10**(-0.4*(mag - magzp)) is not available here, so we convert PSF mag to flux with a common zero point (relative flux),
# normalise per (field, ccdid, qid, filter), convert MJD to BJD_TDB (astropy, geocentre location as in the brief).
# Outputs ztf/<gaia>.csv (raw) and a summary dict (amplitude, outbursts, Lomb-Scargle top periods) printed as JSON.
# Usage: python ztf_lc.py <gaia_id> <ra_2016> <dec_2016> [pmra pmdec]
import sys, io, json, numpy as np, pandas as pd, requests, warnings, time
warnings.filterwarnings("ignore")
from astropy.time import Time
from astropy.coordinates import SkyCoord, EarthLocation
import astropy.units as u
from astropy.timeseries import LombScargle

gid, ra, dec = sys.argv[1], float(sys.argv[2]), float(sys.argv[3])
pmra = float(sys.argv[4]) if len(sys.argv) > 4 else 0.0; pmde = float(sys.argv[5]) if len(sys.argv) > 5 else 0.0
# ZTF epoch ~2020: move position from 2016.0 to 2020.5
dt = 4.5
ra_z = ra + pmra * dt / 3.6e6 / np.cos(np.radians(dec)); de_z = dec + pmde * dt / 3.6e6
url = f"https://irsa.ipac.caltech.edu/cgi-bin/ZTF/nph_light_curves?POS=CIRCLE%20{ra_z:.6f}%20{de_z:.6f}%200.0006&BANDNAME=g,r,i&FORMAT=csv"
txt = None
for k in range(3):
    try:
        r = requests.get(url, timeout=180)
        if r.status_code == 200 and r.text.startswith("oid"):
            txt = r.text; break
        err = f"HTTP {r.status_code} {r.text[:100]!r}"
    except Exception as e:
        err = str(e)
    time.sleep(5)
summ = dict(gaia=gid, url=url)
if txt is None:
    summ["status"] = "HOLE " + err; print(json.dumps(summ)); sys.exit(0)
d = pd.read_csv(io.StringIO(txt))
d.to_csv(f"/tmp/fanout/cv/ztf/{gid}.csv", index=False)
summ["n_raw"] = len(d)
if len(d) == 0:
    summ["status"] = "EMPTY (0 rows; position may be outside ZTF or too faint)"; print(json.dumps(summ)); sys.exit(0)
d = d[d.catflags == 0].copy()
summ["n_good"] = len(d); summ["oids"] = int(d.oid.nunique()) if len(d) else 0
if len(d) < 10:
    summ["status"] = "FEW"; print(json.dumps(summ)); sys.exit(0)
t = Time(d.mjd.values, format="mjd", scale="utc", location=EarthLocation.from_geocentric(0, 0, 0, unit=u.m))
c = SkyCoord(ra * u.deg, dec * u.deg)
d["bjd_tdb"] = (t.tdb + t.light_travel_time(c, kind="barycentric")).jd
d["flux"] = 10 ** (-0.4 * (d.mag - 25.0)); d["eflux"] = d.flux * d.magerr * np.log(10) / 2.5
d["grp"] = d.field.astype(str) + "_" + d.ccdid.astype(str) + "_" + d.qid.astype(str) + "_" + d.filtercode
d["nflux"] = d.flux / d.groupby("grp").flux.transform("median"); d["neflux"] = d.eflux / d.groupby("grp").flux.transform("median")
d.to_csv(f"/tmp/fanout/cv/ztf/{gid}_clean.csv", index=False)
out = {}
for f in ("zg", "zr", "zi"):
    s = d[d.filtercode == f]
    if len(s) < 10: continue
    med = float(np.median(s.mag)); p5, p95 = np.percentile(s.mag, [5, 95])
    # outbursts: >= 3 points brighter than median by > 1 mag (flux ratio > 2.5)
    nb = int((s.nflux > 2.5).sum()); nfaint = int((s.nflux < 0.4).sum())
    ls = LombScargle(s.bjd_tdb, s.nflux, s.neflux)
    fr, pw = ls.autopower(minimum_frequency=1 / 20.0, maximum_frequency=30.0, samples_per_peak=10)
    top = np.argsort(pw)[::-1]
    peaks = []
    for i in top:
        if all(abs(fr[i] - fr[j]) > 0.02 for j in peaks):
            peaks.append(i)
        if len(peaks) >= 3: break
    out[f] = dict(n=len(s), med_mag=round(med, 2), p5_p95=[round(p5, 2), round(p95, 2)], rms_nflux=round(float(np.std(s.nflux)), 3),
                  median_err=round(float(np.median(s.neflux)), 3), n_bright_gt1mag=nb, n_faint_gt1mag=nfaint,
                  mjd_range=[round(float(s.mjd.min()), 1), round(float(s.mjd.max()), 1)],
                  ls_top=[(round(1 / fr[i] * 24, 4), round(float(pw[i]), 3)) for i in peaks],
                  fap_top=float(ls.false_alarm_probability(pw[peaks[0]])) if peaks else None)
summ["bands"] = out; summ["status"] = "OK"
print(json.dumps(summ))
