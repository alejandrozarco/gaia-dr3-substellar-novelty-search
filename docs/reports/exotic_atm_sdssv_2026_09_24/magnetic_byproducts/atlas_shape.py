# ATLAS light-curve shape at the Gaia position of 6021870154194477312: frequency refinement with error, 2f harmonic, amplitude per 2-3 yr block,
# fractional amplitude using Gaia-synthesised SDSS g, r, i (Gaia WD DR3 catalogue J/A+A/674/A33: 17.74, 18.12, 18.54 AB; c ~ (g+r)/2, o ~ (r+i)/2 in flux).
import numpy as np
from astropy.time import Time
from astropy.coordinates import SkyCoord, EarthLocation
import astropy.units as u
L = [l for l in open("atlas_6021_gaiapos.txt").read().splitlines() if l.strip()]
hdr = L[0].lstrip("#").split(); R = [dict(zip(hdr, l.split())) for l in L[1:]]
ok = [x for x in R if float(x["duJy"]) > 0 and float(x["err"]) == 0 and float(x["chi/N"]) < 10]
geo = EarthLocation.of_site("greenwich"); c0 = SkyCoord(244.7254259862617 * u.deg, -35.90743853686 * u.deg)
fl = lambda m: 3631e6 * 10 ** (-0.4 * m); ref = dict(c=(fl(17.74) + fl(18.12)) / 2, o=(fl(18.12) + fl(18.54)) / 2)
T, Y, E, B = [], [], [], []
for b in ("o", "c"):
    s = [x for x in ok if x["F"] == b]; med = np.median([float(x["duJy"]) for x in s]); s = [x for x in s if float(x["duJy"]) < 3 * med]
    mjd = np.array([float(x["MJD"]) for x in s]); f = np.array([float(x["uJy"]) for x in s]); e = np.array([float(x["duJy"]) for x in s])
    season = np.floor((mjd - 57000) / 365.25 + 0.3).astype(int)
    for sv in np.unique(season): f[season == sv] -= np.median(f[season == sv])
    clip = np.abs(f) < 5 * 1.4826 * np.median(np.abs(f)) + 3 * np.median(e)
    tt = Time(mjd[clip], format="mjd", scale="utc"); t = (tt.tdb + tt.light_travel_time(c0, location=geo)).jd
    T += list(t); Y += list(f[clip] / ref[b]); E += list(e[clip] / ref[b]); B += [b] * clip.sum()
T, Y, E, B = map(np.array, (T, Y, E, B)); W = 1 / E ** 2
def fit(fr, sel, harm=1):
    t = T[sel]; cols = [np.ones_like(t)] + ([(B[sel] == "c").astype(float)] if len(set(B[sel])) > 1 else [])
    for h in range(1, harm + 1): cols += [np.sin(2*np.pi*h*fr*t), np.cos(2*np.pi*h*fr*t)]
    X = np.vstack(cols).T; w = W[sel]; A = X.T @ (X * w[:, None]); bb = np.linalg.solve(A, X.T @ (w * Y[sel])); C = np.linalg.inv(A)
    chi2 = np.sum(w * (Y[sel] - X @ bb) ** 2); return bb, C, chi2
al = np.ones(len(T), bool); fr = np.arange(13.9296, 13.9300, 2e-7); chi = np.array([fit(f, al)[2] for f in fr]); k = np.argmin(chi)
dof = al.sum() - 4; s2 = chi[k] / dof; ok1 = chi <= chi[k] + s2
print(f"best f {fr[k]:.7f} c/d, 1-sigma range (delta chi2 = reduced chi2 {s2:.2f}) {fr[ok1].min():.7f}-{fr[ok1].max():.7f}; P = {1440/fr[k]:.4f} min")
f1 = fr[k]
for b in ("c", "o"):
    sel = B == b; bb, C, _ = fit(f1, sel, harm=2)
    a1 = np.hypot(bb[1], bb[2]); a2 = np.hypot(bb[3], bb[4]); ea = np.sqrt(s2 * (C[1, 1] + C[2, 2]) / 2); ea2 = np.sqrt(s2 * (C[3, 3] + C[4, 4]) / 2)
    print(f"{b}: n {sel.sum()}, amp 1f {100*a1:.2f} +- {100*ea:.2f} %, 2f {100*a2:.2f} +- {100*ea2:.2f} %, phase1 {np.degrees(np.arctan2(bb[2], bb[1])) % 360:.0f} deg")
for lo, hi in [(57000, 58100), (58100, 59200), (59200, 60300), (60300, 61400)]:
    sel = (T - 2400000.5 >= lo) & (T - 2400000.5 < hi)
    if sel.sum() < 50: continue
    bb, C, _ = fit(f1, sel)
    print(f"MJD {lo}-{hi}: n {sel.sum()}, amp {100*np.hypot(bb[2], bb[3]):.2f} +- {100*np.sqrt(s2*(C[2,2]+C[3,3])/2):.2f} %, phase {np.degrees(np.arctan2(bb[3], bb[2])) % 360:.0f} deg")
