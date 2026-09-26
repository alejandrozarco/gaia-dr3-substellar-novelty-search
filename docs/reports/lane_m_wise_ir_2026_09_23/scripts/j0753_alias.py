# VarWISE J075330.99-004209.7 = Gaia DR3 3082614748370926848: alias audit (requested by the external review, 2026-09-23).
# NEOWISE W1 detections (j0753_lc.csv), times converted to BJD_TDB. For each candidate frequency: Fourier-series template with K harmonics
# (flux space), per-visit mean and amplitude scale free, COMMON phase. Leave-one-visit-out: fit on all other visits, predict the held-out
# visit with only its mean and amplitude scale refit (no phase freedom). Score = total held-out chi2. Also injection test at the preferred
# frequency with the real timestamps: how often does the audit pick the right alias?
import numpy as np
from astropy.time import Time
from astropy.coordinates import SkyCoord, EarthLocation
import astropy.units as u
d = np.genfromtxt("../data/j0753_neowise_lc.csv", delimiter=",", skip_header=1, names=True)
c0 = SkyCoord(118.37915 * u.deg, -0.70268 * u.deg)
t = Time(d["mjd"], format="mjd", scale="utc", location=EarthLocation.from_geocentric(0, 0, 0, unit="m")); bjd = (t.tdb + t.light_travel_time(c0)).jd   # spacecraft ~ geocentre
F = 10 ** (-0.4 * (d["w1mpro"] - 15.0)); eF = F * d["w1sigmpro"] / 1.0857
o = np.argsort(bjd); bjd, F, eF = bjd[o], F[o], eF[o]
vis = np.cumsum(np.r_[0, np.diff(bjd) > 60]); V = np.unique(vis)
f0 = 1 / 0.1053647; yr = 365.25
cands = {"P (0.1053647 d)": f0, "40.5-d alias (0.1056394 d)": 1 / 0.1056394, "VarWISE (0.105425 d)": 1 / 0.105425,
         "P + 1/yr": f0 + 1 / yr, "P - 1/yr": f0 - 1 / yr, "P + 2/yr": f0 + 2 / yr, "P - 2/yr": f0 - 2 / yr,
         "P + 1/d": f0 + 1.0027, "P - 1/d": f0 - 1.0027, "15.237 - f0 (WISE-orbit reflection)": 15.237 - f0, "2*15.237 - f0": 2 * 15.237 - f0}
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
K0 = K; K = 2 * K0; s2p = score(f0 / 2); K = K0
print(f"   2P (odd/even freedom, {2*K0} harmonics at f0/2)   chi2 {s2p:9.1f}   delta vs P {s2p - res['P (0.1053647 d)']:+8.1f}")
# injection: noise-only resampling around the best-fit P model (residual bootstrap within visits), rescored for P and the two close aliases
rng = np.random.default_rng(3)
coef = fit(bjd, F, eF, f0, vis)
ph = 2 * np.pi * f0 * bjd; H = np.vstack([fn(k * ph) for k in range(1, K + 1) for fn in (np.cos, np.sin)]).T; tm = H @ coef
model = np.empty_like(F)
for v in V:
    m = vis == v; A = np.vstack([np.ones(m.sum()), tm[m]]).T; w = 1 / eF[m]; s, *_ = np.linalg.lstsq(A * w[:, None], F[m] * w, rcond=None); model[m] = A @ s
resid = F - model; wins = {"P": 0, "40.5-d alias": 0, "VarWISE": 0}
for it in range(40):
    y = model.copy()
    for v in V:
        m = np.where(vis == v)[0]; y[m] += rng.choice(resid[m], len(m), replace=True)
    sc = {"P": score(f0, y), "40.5-d alias": score(1 / 0.1056394, y), "VarWISE": score(1 / 0.105425, y)}
    wins[min(sc, key=sc.get)] += 1
print("injection (true P, 40 residual-bootstrap realisations): audit picks", wins)
