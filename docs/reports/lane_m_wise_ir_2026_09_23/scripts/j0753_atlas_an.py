# VarWISE J075330.99-004209.7 = Gaia DR3 3082614748370926848: ATLAS forced photometry (difference-image flux uJy; raw file from
# job queued 2026-09-23), folded on the WISE ephemeris. Question: optical amplitude at P = 0.1053647 d and its phase relative to W1.
import json, numpy as np
from astropy.time import Time
from astropy.coordinates import SkyCoord, EarthLocation
import astropy.units as u
P = 0.1053647
c0 = SkyCoord(118.37915 * u.deg, -0.70268 * u.deg); geo = EarthLocation.from_geocentric(0, 0, 0, unit="m")
def bjd(mjd):
    t = Time(mjd, format="mjd", scale="utc", location=geo); return (t.tdb + t.light_travel_time(c0)).jd
# W1 template (flux) phase reference from NEOWISE detections
d = np.genfromtxt("../data/j0753_neowise_lc.csv", delimiter=",", skip_header=1, names=True)
tw = bjd(d["mjd"]); Fw = 10 ** (-0.4 * (d["w1mpro"] - 15.0)); phw = (tw / P) % 1
def harm(ph, K=4): return np.vstack([np.ones_like(ph)] + [fn(2 * np.pi * k * ph) for k in range(1, K + 1) for fn in (np.cos, np.sin)]).T
bw, *_ = np.linalg.lstsq(harm(phw), Fw, rcond=None)
grid = np.linspace(0, 1, 1000, endpoint=False); tw_g = harm(grid) @ bw
ph_wmax, ph_wmin = grid[np.argmax(tw_g)], grid[np.argmin(tw_g)]
shape = lambda ph: (harm(ph) @ bw - tw_g.mean()) / (tw_g.max() - tw_g.min())   # W1 template, zero mean, unit peak-to-peak
print(f"W1 template: maximum at phase {ph_wmax:.3f}, minimum at {ph_wmin:.3f}")
lines = [l for l in open("../data/j0753_atlas_forcedphot_raw.txt").read().splitlines() if l.strip()]
hdr = lines[0].lstrip("#").split(); rows = [dict(zip(hdr, l.split())) for l in lines[1:]]
ok = [x for x in rows if float(x["duJy"]) > 0 and float(x["err"]) == 0 and float(x["chi/N"]) < 10]
med = {b: np.median([float(x["duJy"]) for x in ok if x["F"] == b]) for b in ("c", "o")}
ok = [x for x in ok if float(x["duJy"]) < 3 * med[x["F"]]]
res = {"object": "VarWISE J075330.99-004209.7 = Gaia DR3 3082614748370926848", "P": P, "W1_max_phase": float(ph_wmax), "W1_min_phase": float(ph_wmin)}
rng = np.random.default_rng(9)
for b, fstar in (("o", 3631e6 * 10 ** (-0.4 * 19.62)), ("c", 3631e6 * 10 ** (-0.4 * 20.55))):   # approx. total flux: o ~ (r+i)/2 PS1, c ~ (g+r)/2
    s = [x for x in ok if x["F"] == b]
    t = bjd(np.array([float(x["MJD"]) for x in s])); f = np.array([float(x["uJy"]) for x in s]); e = np.array([float(x["duJy"]) for x in s])
    f = f - np.median(f); ph = (t / P) % 1
    clip = np.abs(f) < 5 * 1.4826 * np.median(np.abs(f)) + 3 * np.median(e); t, f, e, ph = t[clip], f[clip], e[clip], ph[clip]
    w = 1 / e
    # (1) free sinusoid at P
    X = np.vstack([np.ones_like(ph), np.cos(2 * np.pi * ph), np.sin(2 * np.pi * ph)]).T
    bb, *_ = np.linalg.lstsq(X * w[:, None], f * w, rcond=None); A = 2 * np.hypot(bb[1], bb[2]); ph_max = (np.arctan2(bb[2], bb[1]) / (2 * np.pi)) % 1
    boot = []
    for _ in range(1000):
        i = rng.integers(0, len(f), len(f)); b2, *_ = np.linalg.lstsq(X[i] * w[i][:, None], f[i] * w[i], rcond=None); boot.append(2 * np.hypot(b2[1], b2[2]))
    perm = []
    for _ in range(500):
        pp = rng.permutation(ph); Xp = np.vstack([np.ones_like(pp), np.cos(2 * np.pi * pp), np.sin(2 * np.pi * pp)]).T
        b3, *_ = np.linalg.lstsq(Xp * w[:, None], f * w, rcond=None); perm.append(2 * np.hypot(b3[1], b3[2]))
    # (2) W1-shaped template: optical flux = c + s * shape(phase)  (s = peak-to-peak in uJy, phase locked to W1)
    Xs = np.vstack([np.ones_like(ph), shape(ph)]).T
    bs, *_ = np.linalg.lstsq(Xs * w[:, None], f * w, rcond=None); Cs = np.linalg.inv((Xs * w[:, None]).T @ (Xs * w[:, None]))
    r = (f - Xs @ bs) * w; sc = np.sqrt(max(r @ r / max(len(f) - 2, 1), 1)); es = np.sqrt(Cs[1, 1]) * sc
    edges = np.linspace(0, 1, 11); binned = [float(np.median(f[(ph >= lo) & (ph < hi)])) for lo, hi in zip(edges[:-1], edges[1:])]
    out = dict(n=int(len(f)), median_err_uJy=float(np.median(e)), star_flux_uJy_approx=float(fstar),
               sin_full_amp_uJy=float(A), sin_full_amp_frac=float(A / fstar), sin_boot_16_84=[float(np.percentile(boot, 16)), float(np.percentile(boot, 84))],
               sin_perm_p=float(np.mean(np.array(perm) >= A)), sin_phase_of_max=float(ph_max),
               W1shape_p2p_uJy=float(bs[1]), W1shape_err_uJy=float(es), W1shape_frac=float(bs[1] / fstar), binned_median_uJy=binned)
    res[b] = out
    print(f"ATLAS {b}: n={len(f)}, median err {np.median(e):.1f} uJy (star ~{fstar:.0f} uJy). Free sinusoid full amp {A:.1f} uJy ({A/fstar:.2f} of star; "
          f"boot 16-84% {np.percentile(boot,16):.1f}-{np.percentile(boot,84):.1f}; permutation p {np.mean(np.array(perm) >= A):.3f}); max at phase {ph_max:.3f}. "
          f"W1-shaped fit: peak-to-peak {bs[1]:.1f} +- {es:.1f} uJy ({bs[1]/fstar:.2f} of star)")
    print("   binned medians (10 phase bins, uJy):", " ".join(f"{v:.1f}" for v in binned))
json.dump(res, open("j0753_atlas.json", "w"), indent=1)
