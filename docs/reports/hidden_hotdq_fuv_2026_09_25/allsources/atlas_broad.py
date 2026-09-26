"""Broad ATLAS period search for a white dwarf without a prior frequency.
Cuts as confirm.py: duJy > 0, err == 0, chi/N < 10; per-filter, per-season median of the difference flux subtracted, divided by the Gaia G flux; 5-sigma clip; BJD_TDB
(geocentric); Lomb-Scargle 0.05-100 c/d on fractional flux (o and c combined); Baluev FAP; injection-recovery of 1-3% sinusoids."""
import sys, numpy as np, pandas as pd
from astropy.time import Time
from astropy.coordinates import SkyCoord, EarthLocation
from astropy.timeseries import LombScargle
import astropy.units as u
sid, ra, dec, G = sys.argv[1], float(sys.argv[2]), float(sys.argv[3]), float(sys.argv[4])
REF = 3631e6 * 10 ** (-0.4 * G)  # uJy: ATLAS uJy is difference flux, normalise by the Gaia G flux (as confirm.py)
GEO = EarthLocation.from_geocentric(0, 0, 0, unit="m"); c0 = SkyCoord(ra * u.deg, dec * u.deg)
L = [l for l in open(f"atlas_{sid}.txt").read().splitlines() if l.strip()]; hdr = L[0].lstrip("#").split()
R = pd.DataFrame([dict(zip(hdr, l.split())) for l in L[1:]])
for c in ("MJD", "uJy", "duJy", "err", "chi/N"): R[c] = pd.to_numeric(R[c], errors="coerce")
R = R[(R.duJy > 0) & (R.err == 0) & (R["chi/N"] < 10)]
parts = []
for b, g in R.groupby("F"):
    g = g.copy(); g["season"] = np.floor((g.MJD - 57000) / 365.25)
    for s, h in g.groupby("season"):
        if len(h) < 20: continue
        y = (h.uJy - np.median(h.uJy)) / REF; e = h.duJy / REF
        mad = 1.4826 * np.median(np.abs(y - np.median(y))); k = np.abs(y - np.median(y)) < 5 * mad
        parts.append(pd.DataFrame(dict(t=h.MJD[k], y=y[k], e=e[k], F=b)))
d = pd.concat(parts)
t = Time(d.t.values + 2400000.5, format="jd", scale="utc", location=GEO)
bjd = (t.tdb + t.light_travel_time(c0, kind="barycentric")).jd
d["bjd"] = bjd
print(sid, "n", len(d), {b: int((d.F == b).sum()) for b in d.F.unique()}, "median err %", round(100 * np.median(d.e), 2), "rms %", round(100 * np.std(d.y), 2))
fr = np.arange(0.05, 100, 0.1 / (d.bjd.max() - d.bjd.min()))
ls = LombScargle(d.bjd, d.y, d.e); p = ls.power(fr, method="fast")
seen = []
for i in np.argsort(p)[::-1]:
    if all(abs(fr[i] - s) > 0.02 for s in seen): seen.append(fr[i])
    if len(seen) == 6: break
for f in seen:
    pw = ls.power(f); fap = ls.false_alarm_probability(pw, minimum_frequency=0.05, maximum_frequency=100, method="baluev")
    print(f"  f {f:.5f} c/d  P {24/f:.4f} h  amp~{100*np.sqrt(4*pw*np.var(d.y)):.2f}%  FAP {fap:.2e}")
rng = np.random.default_rng(2)
for A in (0.01, 0.02, 0.03):
    rec = []
    for P_h in (0.1, 0.5, 2, 6, 24, 72):
        f = 24 / P_h; n = 0
        for k in range(10):
            yy = d.y + A * np.sin(2 * np.pi * f * d.bjd + rng.uniform(0, 6.283))
            l = LombScargle(d.bjd, yy, d.e); ff = np.linspace(f * 0.999, f * 1.001, 101); pp = l.power(ff).max()
            n += l.false_alarm_probability(pp, minimum_frequency=0.05, maximum_frequency=100, method="baluev") < 1e-3
        rec.append(f"{P_h}h:{n}/10")
    print(f"  injected {100*A:.0f}%:", " ".join(rec))
