# VarWISE J105943.85-274050.1 = Gaia DR3 5456743064671253632: alias audit (requested by the external review, 2026-09-23).
# NEOWISE W1 detections (j0753_lc.csv), times converted to BJD_TDB. For each candidate frequency: Fourier-series template with K harmonics
# (flux space), per-visit mean and amplitude scale free, COMMON phase. Leave-one-visit-out: fit on all other visits, predict the held-out
# visit with only its mean and amplitude scale refit (no phase freedom). Score = total held-out chi2. Also injection test at the preferred
# frequency with the real timestamps: how often does the audit pick the right alias?
import numpy as np
from astropy.time import Time
from astropy.coordinates import SkyCoord, EarthLocation
import astropy.units as u
d = np.genfromtxt("../data/j1059_neowise_lc.csv", delimiter=",", skip_header=1, names=True)
c0 = SkyCoord(164.9328012 * u.deg, -27.6805609 * u.deg)
t = Time(d["mjd"], format="mjd", scale="utc", location=EarthLocation.from_geocentric(0, 0, 0, unit="m")); bjd = (t.tdb + t.light_travel_time(c0)).jd   # spacecraft ~ geocentre
F = 10 ** (-0.4 * (d["w1mpro"] - 15.0)); eF = F * d["w1sigmpro"] / 1.0857
o = np.argsort(bjd); bjd, F, eF = bjd[o], F[o], eF[o]
vis = np.cumsum(np.r_[0, np.diff(bjd) > 60]); V = np.unique(vis)
f0 = 1 / 0.12105221; yr = 365.25
from astropy.timeseries import LombScargle
_f = np.linspace(0.5, 40, 2000000); _p = LombScargle(bjd, F, eF).power(_f); _pk = []
for _j in np.argsort(_p)[::-1]:
    if all(abs(_f[_j] - s) > 0.004 for s in _pk): _pk.append(_f[_j])
    if len(_pk) == 6: break
print("LS top peaks (P d, power):", [(round(1 / s, 7), round(float(_p[np.argmin(abs(_f - s))]), 3)) for s in _pk])
fb = f0 + 2 / yr
cands = {f"Pb = P+2/yr ({1/fb:.7f} d)": fb, "Pb + 1/yr": fb + 1 / yr, "Pb - 1/yr": fb - 1 / yr, "Pb + 2/yr": fb + 2 / yr, "Pb - 2/yr (old P)": fb - 2 / yr,
         "Pb + 3/yr": fb + 3 / yr, "Pb - 3/yr": fb - 3 / yr, "Pb + 4/yr": fb + 4 / yr, "Pb - 4/yr": fb - 4 / yr, "Pb + 1/d": fb + 1.0027, "Pb - 1/d": fb - 1.0027,
         "15.237 - fb": 15.237 - fb, "2*15.237 - fb": 2 * 15.237 - fb}
K = 4
def design(tt, f, sid, scale=None):
    cols = []
    for v in np.unique(sid):
        cols.append((sid == v).astype(float))
    ph = 2 * np.pi * f * tt
    H = np.vstack([fn(k * ph) for k in range(1, K + 1) for fn in (np.cos, np.sin)]).T
    if scale is not None: H = H * scale[:, None]
    return np.hstack([np.vstack(cols).T, H])
def fit(tt, y, e, f, sid):
    # two-step: global template with per-visit means; then per-visit amplitude scale; then refit template with scales
    X = design(tt, f, sid); w = 1 / e
    b, *_ = np.linalg.lstsq(X * w[:, None], y * w, rcond=None)
    nv = len(np.unique(sid)); tmpl = X[:, nv:] @ b[nv:]
    scale = np.ones_like(y)
    for v in np.unique(sid):
        m = sid == v; A = np.vstack([np.ones(m.sum()), tmpl[m]]).T
        s, *_ = np.linalg.lstsq(A * w[m][:, None], y[m] * w[m], rcond=None); scale[m] = max(s[1], 0.05)
    X2 = design(tt, f, sid, scale); b2, *_ = np.linalg.lstsq(X2 * w[:, None], y * w, rcond=None)
    return b2[nv:]
def score(f, y=F):
    tot = 0.0
    for v in V:
        tr = vis != v; te = vis == v
        if te.sum() < 5: continue
        coef = fit(bjd[tr], y[tr], eF[tr], f, vis[tr])
        ph = 2 * np.pi * f * bjd[te]
        H = np.vstack([fn(k * ph) for k in range(1, K + 1) for fn in (np.cos, np.sin)]).T; tmpl = H @ coef
        A = np.vstack([np.ones(te.sum()), tmpl]).T; w = 1 / eF[te]
        s, *_ = np.linalg.lstsq(A * w[:, None], y[te] * w, rcond=None)
        r = (y[te] - A @ s) * w; tot += float(r @ r)
    return tot
res = {k: score(f) for k, f in cands.items()}
best = min(res, key=res.get)
print(f"W1 detections {len(F)}, visits {len(V)}; leave-one-visit-out held-out chi2 (lower is better; K={K} harmonics):")
for k, v in sorted(res.items(), key=lambda kv: kv[1]):
    print(f"   {k:38s} chi2 {v:9.1f}   delta vs best {v - res[best]:+8.1f}")
# 2P test: template at f0/2 with 2K harmonics (nests the P template) -- does extra odd/even freedom predict held-out visits better?
K0 = K; K = 2 * K0; s2p = score(fb / 2); K = K0
K = 3 * K0; s3p = score(fb / 3); K = K0
print(f"   3P = VarWISE 0.363 d ({3*K0} harmonics at f0/3)   chi2 {s3p:9.1f}   delta vs P {s3p - res[f'Pb = P+2/yr ({1/fb:.7f} d)']:+8.1f}")
print(f"   2P (odd/even freedom, {2*K0} harmonics at f0/2)   chi2 {s2p:9.1f}   delta vs P {s2p - res[f'Pb = P+2/yr ({1/fb:.7f} d)']:+8.1f}")
# injection: noise-only resampling around the best-fit P model (residual bootstrap within visits), rescored for P and the two close aliases
rng = np.random.default_rng(3)
coef = fit(bjd, F, eF, fb, vis)
ph = 2 * np.pi * fb * bjd; H = np.vstack([fn(k * ph) for k in range(1, K + 1) for fn in (np.cos, np.sin)]).T; tm = H @ coef
model = np.empty_like(F)
for v in V:
    m = vis == v; A = np.vstack([np.ones(m.sum()), tm[m]]).T; w = 1 / eF[m]; s, *_ = np.linalg.lstsq(A * w[:, None], F[m] * w, rcond=None); model[m] = A @ s
resid = F - model; wins = {"Pb": 0, "Pb-2/yr": 0, "Pb+2/yr": 0, "Pb-1/yr": 0}
for it in range(40):
    y = model.copy()
    for v in V:
        m = np.where(vis == v)[0]; y[m] += rng.choice(resid[m], len(m), replace=True)
    sc = {"Pb": score(fb, y), "Pb-2/yr": score(fb - 2 / yr, y), "Pb+2/yr": score(fb + 2 / yr, y), "Pb-1/yr": score(fb - 1 / yr, y)}
    wins[min(sc, key=sc.get)] += 1
print("injection (true Pb, 40 residual-bootstrap realisations): audit picks", wins)

grid = fb + np.linspace(-2e-4, 2e-4, 41)
sc = np.array([score(f) for f in grid]); j = int(np.argmin(sc))
ok = sc < sc[j] + 1.0
print(f"refined: P = {1/grid[j]:.8f} d (held-out chi2 {sc[j]:.1f}); frequencies within delta chi2 < 1: {1/grid[ok].max():.8f} - {1/grid[ok].min():.8f} d")
