# VarWISE J105943.85-274050.1 = Gaia DR3 5456743064671253632: ZTF DR amplitude at the corrected WISE period (BJD_TDB).
import io, csv, subprocess, time, numpy as np
from astropy.time import Time
from astropy.coordinates import SkyCoord, EarthLocation
import astropy.units as u
RA0, DE0, PMRA, PMDE = 164.93280120834928, -27.680560897461646, -49.95604041580538, -12.373514177220297
url = f"https://irsa.ipac.caltech.edu/cgi-bin/ZTF/nph_light_curves?POS=CIRCLE%20{RA0 + PMRA*4/3.6e6/np.cos(np.radians(DE0))}%20{DE0 + PMDE*4/3.6e6}%200.000833&BANDNAME=g,r,i&FORMAT=CSV"
for k in range(5):
    q = subprocess.run(["curl", "-sL", "--max-time", "600", url], capture_output=True, text=True).stdout
    if q.startswith("oid"): break
    time.sleep(30 * (k + 1))
Z = [z for z in csv.DictReader(io.StringIO(q)) if z.get("catflags") == "0" and z.get("sharp") and abs(float(z["sharp"])) < 0.5]
c0 = SkyCoord(RA0 * u.deg, DE0 * u.deg); pal = EarthLocation.of_site("Palomar")
rng = np.random.default_rng(5)
for b in ("zr", "zg"):
    s = [z for z in Z if z["filtercode"] == b]
    if len(s) < 15: continue
    t = Time(np.array([float(z["mjd"]) for z in s]), format="mjd", scale="utc", location=pal); bj = (t.tdb + t.light_travel_time(c0)).jd
    m = np.array([float(z["mag"]) for z in s]); e = np.array([float(z["magerr"]) for z in s]); o = np.array([z["oid"] for z in s])
    for oo in set(o): m[o == oo] -= np.median(m[o == oo])
    for lab, P in (("corrected P 0.12097159", 0.12097159), ("old P 0.12105221", 0.12105221)):
        X = np.vstack([np.ones_like(bj), np.cos(2 * np.pi * bj / P), np.sin(2 * np.pi * bj / P)]).T; w = 1 / e
        bb, *_ = np.linalg.lstsq(X * w[:, None], m * w, rcond=None); A = 2 * np.hypot(bb[1], bb[2])
        boot = []
        for _ in range(2000):
            i = rng.integers(0, len(m), len(m)); b2, *_ = np.linalg.lstsq(X[i] * w[i][:, None], m[i] * w[i], rcond=None); boot.append(2 * np.hypot(b2[1], b2[2]))
        # injection-calibrated 95% upper limit: add a sinusoid of amplitude a at random phase, find a where recovery exceeds observed in 95%
        print(f"{b} n={len(m)} {lab}: full amplitude {A:.3f} mag (bootstrap 16-84% {np.percentile(boot,16):.3f}-{np.percentile(boot,84):.3f}, 95% {np.percentile(boot,95):.3f}); rms {m.std():.3f}, median err {np.median(e):.3f}")
