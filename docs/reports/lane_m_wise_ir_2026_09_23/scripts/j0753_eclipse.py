# J0753 (Gaia DR3 3082614748370926848): test for a narrow eclipse near phase 0.575 in ATLAS o and c (season-detrended difference flux).
# Model: 2-harmonic baseline at P plus a box-shaped dip (centre, full width, depth) scanned on a grid; significance by delta chi2 against
# the baseline and by a permutation null (phases shuffled); consistency across halves of the data (2015-2020 vs 2021-2026).
import numpy as np
from astropy.time import Time
from astropy.coordinates import SkyCoord, EarthLocation
import astropy.units as u
P = 0.1053647; c0 = SkyCoord(118.37915 * u.deg, -0.70268 * u.deg); geo = EarthLocation.from_geocentric(0, 0, 0, unit="m")
def bjd(mjd):
    t = Time(mjd, format="mjd", scale="utc", location=geo); return (t.tdb + t.light_travel_time(c0)).jd
lines = [l for l in open("../data/j0753_atlas_forcedphot_raw.txt").read().splitlines() if l.strip()]; hdr = lines[0].lstrip("#").split(); rows = [dict(zip(hdr, l.split())) for l in lines[1:]]
ok = [x for x in rows if float(x["duJy"]) > 0 and float(x["err"]) == 0 and float(x["chi/N"]) < 10]
med = {b: np.median([float(x["duJy"]) for x in ok if x["F"] == b]) for b in ("c", "o")}; ok = [x for x in ok if float(x["duJy"]) < 3 * med[x["F"]]]
rng = np.random.default_rng(12)
def prep(b):
    s = [x for x in ok if x["F"] == b]; mjd = np.array([float(x["MJD"]) for x in s]); f = np.array([float(x["uJy"]) for x in s]); e = np.array([float(x["duJy"]) for x in s])
    season = np.floor((mjd - 57000) / 365.25 + 0.3).astype(int)
    for sv in np.unique(season): f[season == sv] -= np.median(f[season == sv])
    clip = np.abs(f) < 5 * 1.4826 * np.median(np.abs(f)) + 3 * np.median(e)
    return mjd[clip], (bjd(mjd[clip]) / P) % 1, f[clip], e[clip]
def base(ph, K=2): return np.vstack([np.ones_like(ph)] + [fn(2 * np.pi * k * ph) for k in range(1, K + 1) for fn in (np.cos, np.sin)]).T
def scan(ph, f, e, centres=np.linspace(0, 1, 200, endpoint=False), widths=(0.02, 0.03, 0.04, 0.06, 0.08)):
    w = 1 / e; X0 = base(ph); b0, *_ = np.linalg.lstsq(X0 * w[:, None], f * w, rcond=None); r0 = (f - X0 @ b0) * w; chi0 = r0 @ r0
    best = (0, None)
    for c in centres:
        for wd in widths:
            box = (np.abs(((ph - c + 0.5) % 1) - 0.5) < wd / 2).astype(float)
            if box.sum() < 10: continue
            X = np.hstack([X0, -box[:, None]]); b, *_ = np.linalg.lstsq(X * w[:, None], f * w, rcond=None)
            if b[-1] <= 0: continue
            r = (f - X @ b) * w; d = chi0 - r @ r
            if d > best[0]: best = (d, (c, wd, b[-1], int(box.sum())))
    return best
out = {}
for b in ("o", "c"):
    mjd, ph, f, e = prep(b)
    d, (c, wd, depth, n) = scan(ph, f, e)
    fstar = 3631e6 * 10 ** (-0.4 * (19.62 if b == "o" else 20.55))
    null = []
    for _ in range(200):
        dd, _p = scan(rng.permutation(ph), f, e, centres=np.linspace(0, 1, 50, endpoint=False), widths=(0.02, 0.04, 0.06))
        null.append(dd)
    halves = []
    for lab, m in (("<=2020", mjd < 59215), (">2020", mjd >= 59215)):
        w = 1 / e[m]; X0 = base(ph[m]); box = (np.abs(((ph[m] - c + 0.5) % 1) - 0.5) < wd / 2).astype(float)
        X = np.hstack([X0, -box[:, None]]); bb, *_ = np.linalg.lstsq(X * w[:, None], f[m] * w, rcond=None)
        C = np.linalg.inv((X * w[:, None]).T @ (X * w[:, None])); r = (f[m] - X @ bb) * w; s = np.sqrt(max(r @ r / max(m.sum() - X.shape[1], 1), 1))
        halves.append((lab, float(bb[-1]), float(np.sqrt(C[-1, -1]) * s), int(box.sum())))
    print(f"ATLAS {b}: best dip centre {c:.3f}, full width {wd:.2f} ({wd*P*1440:.0f} min), depth {depth:.1f} uJy = {depth/fstar:.2f} of the star, n in dip {n}; "
          f"delta chi2 {d:.1f} vs permutation null (coarser scan) 95/99/max {np.percentile(null,95):.1f}/{np.percentile(null,99):.1f}/{max(null):.1f}")
    print("   depth by half:", "; ".join(f"{l_}: {v_:.1f} +- {e_:.1f} uJy (n={n_})" for l_, v_, e_, n_ in halves))
    out[b] = dict(centre=float(c), width=float(wd), depth_uJy=float(depth), depth_frac=float(depth / fstar), dchi2=float(d), null_99=float(np.percentile(null, 99)), halves=halves)
import json; json.dump(out, open("j0753_eclipse.json", "w"), indent=1)
