# ATLAS forced photometry (difference fluxes, uJy) for Gaia DR3 6021870154194477312 and a Lomb-Scargle check of the TESS S65 signal
# (13.9342 c/d = 1.722 h). Token read from ~/.config/atlas/token (never printed). Cuts: duJy > 0, err == 0, chi/N < 10, duJy < 3 x median;
# per-season median subtracted; BJD_TDB; 5-sigma clip. Permutation null (200 shuffles of flux-error pairs within band) of the power at
# 13.9342 c/d and of the maximum over 0.5-50 c/d.
import os, time, io, json, requests, numpy as np, pandas as pd
from astropy.timeseries import LombScargle
from astropy.time import Time
from astropy.coordinates import SkyCoord, EarthLocation
import astropy.units as u
BASE = "https://fallingstar-data.com/forcedphot"
H = {"Authorization": "Token " + open(os.path.expanduser("~/.config/atlas/token")).read().strip(), "Accept": "application/json"}
ra, de = 244.72542, -35.90761
if not os.path.exists("atlas_6021.txt"):
    url = None
    for k in range(6):
        r = requests.post(f"{BASE}/queue/", headers=H, data={"ra": ra, "dec": de, "mjd_min": 57000.0, "send_email": False}, timeout=60)
        if r.status_code == 201: url = r.json()["url"]; break
        time.sleep(30)
    txt = None
    for k in range(180):
        j = requests.get(url, headers=H, timeout=60).json()
        if j.get("finishtimestamp"):
            txt = requests.get(j["result_url"], headers=H, timeout=120).text if j.get("result_url") else ""; requests.delete(url, headers=H, timeout=60); break
        time.sleep(10)
    open("atlas_6021.txt", "w").write(txt or "")
L = [l for l in open("atlas_6021.txt").read().splitlines() if l.strip()]
hdr = L[0].lstrip("#").split(); R = [dict(zip(hdr, l.split())) for l in L[1:]]
ok = [x for x in R if float(x["duJy"]) > 0 and float(x["err"]) == 0 and float(x["chi/N"]) < 10]
geo = EarthLocation.from_geocentric(0, 0, 0, unit="m"); c0 = SkyCoord(ra * u.deg, de * u.deg); D = {}
for b in ("o", "c"):
    s = [x for x in ok if x["F"] == b]
    if not s: continue
    med = np.median([float(x["duJy"]) for x in s]); s = [x for x in s if float(x["duJy"]) < 3 * med]
    mjd = np.array([float(x["MJD"]) for x in s]); f = np.array([float(x["uJy"]) for x in s]); e = np.array([float(x["duJy"]) for x in s])
    season = np.floor((mjd - 57000) / 365.25 + 0.3).astype(int)
    for sv in np.unique(season): f[season == sv] -= np.median(f[season == sv])
    clip = np.abs(f) < 5 * 1.4826 * np.median(np.abs(f)) + 3 * np.median(e)
    t = Time(mjd[clip], format="mjd", scale="utc", location=geo); D[b] = ((t.tdb + t.light_travel_time(c0)).jd, f[clip], e[clip])
    print(f"band {b}: n {clip.sum()}, median err {np.median(e):.1f} uJy, rms {np.std(f[clip]):.1f} uJy")
ref = [x for x in R if x["F"] == "o"][:1]
t = np.concatenate([D[b][0] for b in D]); y = np.concatenate([D[b][1] for b in D]); e = np.concatenate([D[b][2] for b in D])
f0 = 13.9342; fr = np.arange(0.5, 50, 0.05 / (t.max() - t.min()))
ls = LombScargle(t, y, e); P = ls.power(fr, method="fast"); p0 = LombScargle(t, y, e).power(np.array([f0]))[0]; k = np.argmax(P)
X = np.vstack([np.ones_like(t), np.sin(2 * np.pi * f0 * t), np.cos(2 * np.pi * f0 * t)]).T; W = 1 / e ** 2
b_ = np.linalg.solve(X.T @ (X * W[:, None]), X.T @ (W * y)); C = np.linalg.inv(X.T @ (X * W[:, None])); A = np.hypot(b_[1], b_[2]); eA = np.sqrt((C[1, 1] + C[2, 2]) / 2)
rng = np.random.default_rng(5); n0, nmax = [], []
for it in range(200):
    yy, ee = y.copy(), e.copy()
    for b in D:
        m = np.isin(t, D[b][0]); idx = rng.permutation(m.sum()); yy[m] = y[m][idx]; ee[m] = e[m][idx]
    l2 = LombScargle(t, yy, ee); n0.append(l2.power(np.array([f0]))[0])
    if it < 50: nmax.append(l2.power(fr, method="fast").max())
print(f"combined n {len(t)}, span {t.max()-t.min():.0f} d; power at {f0} c/d: {p0:.4f} (permutation p = {np.mean(np.array(n0) >= p0):.3f}); sinusoid amplitude {A:.1f} +- {eA:.1f} uJy")
print(f"highest peak 0.5-50 c/d: {fr[k]:.4f} c/d ({24/fr[k]:.3f} h) power {P[k]:.4f}; permutation max-power 99th pct {np.percentile(nmax, 99):.4f}")
