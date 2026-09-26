# ZTF (2018-2025) + NEOWISE (2010-2024) joint ephemeris for J1526; phase of optical vs IR maxima (both on BJD_TDB)
import io, csv, json, subprocess, numpy as np
from astropy.time import Time
from astropy.coordinates import SkyCoord, EarthLocation
import astropy.units as u
from astropy.timeseries import LombScargle
RA, DE = 231.5620, -11.2245
c = SkyCoord(RA*u.deg, DE*u.deg)
# ZTF light curve by position (2.5 arcsec), clean epochs
url = (f"https://irsa.ipac.caltech.edu/cgi-bin/ZTF/nph_light_curves?POS=CIRCLE%20{RA}%20{DE}%200.000694&BANDNAME=g,r,i&BAD_CATFLAGS_MASK=32768&FORMAT=CSV")
q = subprocess.run(["curl", "-sL", "--max-time", "600", url], capture_output=True, text=True).stdout
assert q.startswith("oid"), q[:200]
Z = [x for x in csv.DictReader(io.StringIO(q)) if x["catflags"] == "0" and abs(float(x["sharp"])) < 0.5]
zt = np.array([float(x["mjd"]) for x in Z]); zm = np.array([float(x["mag"]) for x in Z]); ze = np.array([float(x["magerr"]) for x in Z]); zb = np.array([x["filtercode"] for x in Z])
zo = np.array([x["oid"] for x in Z])
for o in set(zo): zm[zo == o] -= np.median(zm[zo == o])
def bjd(mjd, site):
    t = Time(mjd, format="mjd", scale="utc", location=site) if site is not None else Time(mjd, format="mjd", scale="utc")
    return (t.tdb + t.light_travel_time(c, kind="barycentric", location=site) if site is not None else t.tdb + t.light_travel_time(c, kind="barycentric", location=EarthLocation.from_geocentric(0, 0, 0, unit=u.m))).jd
palomar = EarthLocation.of_site("Palomar")
zB = bjd(zt, palomar)
W = json.load(open("neowise.json"))["J1526"]
wt = np.array(W["t"]); wm = np.array(W["m"]); we = np.array(W["e"])
wB = bjd(wt, None)  # geocentre (WISE in LEO: <0.03 s error)
wm = wm - np.median(wm)
print(f"ZTF clean epochs: g {np.sum(zb=='zg')}, r {np.sum(zb=='zr')}, i {np.sum(zb=='zi')}; span {zt.min():.0f}-{zt.max():.0f}; WISE {len(wt)} epochs {wt.min():.0f}-{wt.max():.0f}")
def fit2(t, m, e, f):
    X = np.column_stack([np.ones_like(t), np.sin(2*np.pi*f*t), np.cos(2*np.pi*f*t), np.sin(4*np.pi*f*t), np.cos(4*np.pi*f*t)])
    w = 1 / e**2; A = X.T @ (X * w[:, None]); b = X.T @ (m * w); p = np.linalg.solve(A, b); r = m - X @ p
    return p, float(np.sum(r**2 * w))
# joint frequency scan: sum of chi2 over bands (each band its own 2-harmonic shape), ZTF + W1
f0 = 1 / 0.09379696
fr = f0 + np.linspace(-2e-5, 2e-5, 4001)
T0 = 2459000.0
sets = [(zB[zb == b] - T0, zm[zb == b], ze[zb == b]) for b in ("zg", "zr", "zi")] + [(wB - T0, wm, we)]
chi = np.array([sum(fit2(t, m, e, f)[1] for t, m, e in sets) for f in fr])
k = int(np.argmin(chi)); fb = fr[k]
# 1-sigma from delta chi2 = 1 after rescaling chi2 to reduced = 1
dof = sum(len(s[0]) for s in sets) - 5 * len(sets) - 1
scale = chi[k] / dof
ok = fr[(chi - chi[k]) / scale <= 1.0]
print(f"joint best P = {1/fb:.9f} d  (+{1/ok.min()-1/fb:.2e} / -{1/fb-1/ok.max():.2e}); reduced chi2 {scale:.2f}")
chiZ = np.array([sum(fit2(t, m, e, f)[1] for t, m, e in sets[:3]) for f in fr]); chiW = np.array([fit2(*sets[3], f)[1] for f in fr])
print(f"ZTF-only best P = {1/fr[np.argmin(chiZ)]:.9f} d; WISE-only best P = {1/fr[np.argmin(chiW)]:.9f} d")
# phase of maximum light (min magnitude) per band at the joint period
for name, (t, m, e) in zip(("g", "r", "i", "W1"), sets):
    p, _ = fit2(t, m, e, fb)
    ph = np.linspace(0, 1, 1000, endpoint=False)
    model = p[0] + p[1]*np.sin(2*np.pi*ph) + p[2]*np.cos(2*np.pi*ph) + p[3]*np.sin(4*np.pi*ph) + p[4]*np.cos(4*np.pi*ph)
    print(f"  {name}: max light at phase {ph[np.argmin(model)]:.3f}, min light at {ph[np.argmax(model)]:.3f}, model peak-to-peak {model.max()-model.min():.3f} mag")
json.dump(dict(P=1/fb, T0=T0, note="phase 0 = BJD_TDB 2459000.0"), open("j1526_ephem.json", "w"))
