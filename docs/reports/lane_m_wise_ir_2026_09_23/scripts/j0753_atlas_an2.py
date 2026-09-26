# J0753 (Gaia DR3 3082614748370926848) ATLAS: per-season detrended, 2-harmonic fit at P = 0.1053647 d, permutation significance,
# binned light curve with errors. Complements j0753_atlas_an.py.
import numpy as np
from astropy.time import Time
from astropy.coordinates import SkyCoord, EarthLocation
import astropy.units as u
P = 0.1053647; c0 = SkyCoord(118.37915 * u.deg, -0.70268 * u.deg); geo = EarthLocation.from_geocentric(0, 0, 0, unit="m")
def bjd(mjd):
    t = Time(mjd, format="mjd", scale="utc", location=geo); return (t.tdb + t.light_travel_time(c0)).jd
lines = [l for l in open("../data/j0753_atlas_forcedphot_raw.txt").read().splitlines() if l.strip()]
hdr = lines[0].lstrip("#").split(); rows = [dict(zip(hdr, l.split())) for l in lines[1:]]
ok = [x for x in rows if float(x["duJy"]) > 0 and float(x["err"]) == 0 and float(x["chi/N"]) < 10]
med = {b: np.median([float(x["duJy"]) for x in ok if x["F"] == b]) for b in ("c", "o")}
ok = [x for x in ok if float(x["duJy"]) < 3 * med[x["F"]]]
rng = np.random.default_rng(4)
for b, fstar in (("o", 3631e6 * 10 ** (-0.4 * 19.62)), ("c", 3631e6 * 10 ** (-0.4 * 20.55))):
    s = [x for x in ok if x["F"] == b]
    mjd = np.array([float(x["MJD"]) for x in s]); f = np.array([float(x["uJy"]) for x in s]); e = np.array([float(x["duJy"]) for x in s])
    t = bjd(mjd); ph = (t / P) % 1
    season = np.floor((mjd - 57000) / 365.25 + 0.3).astype(int)            # observing seasons (target at RA 118: season break ~ June)
    for sv in np.unique(season):
        m = season == sv; f[m] -= np.median(f[m])
    clip = np.abs(f) < 5 * 1.4826 * np.median(np.abs(f)) + 3 * np.median(e); f, e, ph, season = f[clip], e[clip], ph[clip], season[clip]
    w = 1 / e
    def fit(pp, K):
        X = np.vstack([np.ones_like(pp)] + [fn(2 * np.pi * k * pp) for k in range(1, K + 1) for fn in (np.cos, np.sin)]).T
        bb, *_ = np.linalg.lstsq(X * w[:, None], f * w, rcond=None); r = (f - X @ bb) * w
        return bb, float(r @ r), X
    b0, chi0, _ = fit(ph, 0)
    b2, chi2, X2 = fit(ph, 2)
    d = chi0 - chi2
    perm = []
    for _ in range(1000):
        pp = rng.permutation(ph); _, c2, _ = fit(pp, 2); perm.append(chi0 - c2)
    grid = np.linspace(0, 1, 200); Xg = np.vstack([np.ones_like(grid)] + [fn(2 * np.pi * k * grid) for k in range(1, 3) for fn in (np.cos, np.sin)]).T
    mod = Xg @ b2; p2p = mod.max() - mod.min()
    boot = []
    for _ in range(500):
        i = rng.integers(0, len(f), len(f)); Xi = X2[i]; bb, *_ = np.linalg.lstsq(Xi * w[i][:, None], f[i] * w[i], rcond=None); m_ = Xg @ bb; boot.append(m_.max() - m_.min())
    edges = np.linspace(0, 1, 11)
    bins = []
    for lo, hi in zip(edges[:-1], edges[1:]):
        m = (ph >= lo) & (ph < hi); bins.append((np.average(f[m], weights=w[m] ** 2), 1 / np.sqrt(np.sum(w[m] ** 2)), m.sum()))
    print(f"ATLAS {b}: n={len(f)}, {len(np.unique(season))} seasons detrended; 2-harmonic model delta chi2 {d:.1f} (permutation p {np.mean(np.array(perm) >= d):.3f}; "
          f"perm 99th pct {np.percentile(perm, 99):.1f}); model peak-to-peak {p2p:.1f} uJy = {p2p/fstar:.2f} of the star (~{-2.5*np.log10(1 - p2p/fstar/2) + 2.5*np.log10(1 + p2p/fstar/2):.2f} mag); "
          f"bootstrap 16-84% {np.percentile(boot,16):.1f}-{np.percentile(boot,84):.1f} uJy; model maxima at phase {grid[np.argmax(mod)]:.2f}, minima at {grid[np.argmin(mod)]:.2f}")
    print("   weighted bin means (uJy +- err):", " ".join(f"{m_:+.1f}({e_:.1f})" for m_, e_, n_ in bins))
