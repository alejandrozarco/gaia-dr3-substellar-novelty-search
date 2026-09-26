import os, subprocess, numpy as np
from astropy.io import fits
C = 299792.458; LINES = {"Ha": 6564.61, "Hb": 4862.68, "Hg": 4341.69}; S = np.arange(-700, 701, 5.0)
BASE = "https://data.sdss.org/sas/dr20/spectro/boss/redux/v6_2_1/spectra/daily/full"; D = "/tmp/hotdq/lane_fun/specfull"
def get(r):
    f = f"{int(r.fieldid):06d}"; name = f"spec-{f}-{int(r.mjd)}-{int(r.catalogid)}.fits"; p = os.path.join(D, name)
    if not os.path.exists(p) or os.path.getsize(p) < 10000:
        subprocess.run(["curl", "-s", "-m", "300", "-o", p, f"{BASE}/{f[:3]}XXX/{f}/{int(r.mjd)}/{name}"])
    return p if os.path.exists(p) and os.path.getsize(p) > 10000 else None
def seg(w, f, iv, l):
    v = (w / l - 1) * C; m = (np.abs(v) < 3500) & (iv > 0) & np.isfinite(f); v, f, iv = v[m], f[m], iv[m]; c = np.abs(v) > 2500
    if c.sum() < 6: return None
    p = np.polyfit(v[c], f[c], 1, w=np.sqrt(iv[c])); cc = np.polyval(p, v)
    return (v, f / cc, iv * cc ** 2) if np.median(cc) > 0 else None
def template(vv):
    grid = 10 ** np.arange(np.log10(3600), np.log10(10300), 1e-4); num = np.zeros_like(grid); den = np.zeros_like(grid)
    for _, r in vv.iterrows():
        p = get(r)
        if not p: continue
        d = fits.open(p)["COADD"].data; w = 10 ** d["LOGLAM"]; iv = d["IVAR"] * (d["AND_MASK"] == 0)
        fi = np.interp(grid, w, d["FLUX"], left=np.nan, right=np.nan); ii = np.interp(grid, w, iv, left=0, right=0); ok = np.isfinite(fi) & (ii > 0)
        num[ok] += fi[ok] * ii[ok]; den[ok] += ii[ok]
    tf = np.where(den > 0, num / np.where(den > 0, den, 1), np.nan); return {n: seg(grid, tf, den, l) for n, l in LINES.items()}
def lines(w, f, iv, T):
    res = {}
    for n, l in LINES.items():
        if T.get(n) is None: continue
        X = seg(w, f, iv, l)
        if X is None: continue
        xv, xf, xi = X; m = np.abs(xv) < 1500
        if m.sum() < 20: continue
        tv, tfl, _ = T[n]; chi = np.array([np.sum((xf[m] - np.interp(xv[m] - s, tv, tfl)) ** 2 * xi[m]) for s in S]); i = int(np.argmin(chi))
        if 0 < i < len(S) - 1:
            a, b, _ = np.polyfit(S[i - 1:i + 2], chi[i - 1:i + 2], 2)
            if a > 0: res[n] = (-b / (2 * a), np.sqrt(max(chi[i] / (m.sum() - 1), 1) / a))
    return res
def consensus(res):
    vals = [(v, e) for v, e in res.values() if np.isfinite(v)]
    if len(vals) < 2: return np.nan, np.nan, 0
    med = np.median([v for v, _ in vals]); ok = np.array([(v, e) for v, e in vals if abs(v - med) <= max(3 * e, 40)])
    if len(ok) < 2: return np.nan, np.nan, 0
    n = len(ok); return round(ok[:, 0].mean(), 1), round(max(ok[:, 0].std(ddof=1) / np.sqrt(n), np.median(ok[:, 1]) / np.sqrt(n), 8), 1), n
