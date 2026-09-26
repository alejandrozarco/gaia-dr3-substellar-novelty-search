"""Per-exposure radial velocities from the BOSS pipeline spec-full files (SDSS-V DR20, run2d v6_2_1, spectra/daily/full), which are
independent of the Astra XCSAO shifts. For each star: template = inverse-variance coadd of the COADD extensions of all its visits on
a common log-wavelength grid; for each exposure extension (MJD_EXP_*): velocities of H-alpha, H-beta and H-gamma against the template
(linear continuum from 2500-3500 km/s; chi2 over |v| < 1500 km/s; shifts -700..+700 km/s, 5 km/s, parabola refinement); consensus =
mean of the lines that agree with their median within max(3 sigma, 40 km/s), if at least two. Exposure time = TAI-BEG + EXPTIME/2.
python exp_rv.py <visits.csv> <out.csv> [sdss_id ...]"""
import sys, os, subprocess, numpy as np, pandas as pd
from astropy.io import fits
C = 299792.458; LINES = {"Ha": 6564.61, "Hb": 4862.68, "Hg": 4341.69}; S = np.arange(-700, 701, 5.0)
BASE = "https://data.sdss.org/sas/dr20/spectro/boss/redux/v6_2_1/spectra/daily/full"; D = "/tmp/hotdq/lane_fun/specfull"
V = pd.read_csv(sys.argv[1], dtype={"sdss_id": str}); ids = sys.argv[3:] or V.sdss_id.unique().tolist()
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
rows = []
for sid in ids:
    vv = V[V.sdss_id == sid]; files = [(r, get(r)) for _, r in vv.iterrows()]; files = [(r, p) for r, p in files if p]
    grid = 10 ** np.arange(np.log10(3600), np.log10(10300), 1e-4); num = np.zeros_like(grid); den = np.zeros_like(grid)
    for r, p in files:
        d = fits.open(p)["COADD"].data; w = 10 ** d["LOGLAM"]; iv = d["IVAR"] * (d["AND_MASK"] == 0)
        fi = np.interp(grid, w, d["FLUX"], left=np.nan, right=np.nan); ii = np.interp(grid, w, iv, left=0, right=0); ok = np.isfinite(fi) & (ii > 0)
        num[ok] += fi[ok] * ii[ok]; den[ok] += ii[ok]
    tf = np.where(den > 0, num / np.where(den > 0, den, 1), np.nan); T = {n: seg(grid, tf, den, l) for n, l in LINES.items()}
    for r, p in files:
        h = fits.open(p)
        for x in h:
            if not x.name.startswith("MJD_EXP"): continue
            d = x.data; w = 10 ** d["LOGLAM"]; iv = d["IVAR"] * (d["AND_MASK"] == 0); t = (x.header["TAI-BEG"] + x.header["EXPTIME"] / 2) / 86400 + 2400000.5
            res = {}
            for n, l in LINES.items():
                if T[n] is None: continue
                X = seg(w, d["FLUX"], iv, l)
                if X is None: continue
                xv, xf, xi = X; m = np.abs(xv) < 1500
                if m.sum() < 20: continue
                tv, tfl, _ = T[n]; chi = np.array([np.sum((xf[m] - np.interp(xv[m] - s, tv, tfl)) ** 2 * xi[m]) for s in S]); i = int(np.argmin(chi))
                if 0 < i < len(S) - 1:
                    a, b, _ = np.polyfit(S[i - 1:i + 2], chi[i - 1:i + 2], 2); res[n] = (-b / (2 * a), np.sqrt(max(chi[i] / (m.sum() - 1), 1) / a)) if a > 0 else (np.nan, np.nan)
            vals = [(n, v, e) for n, (v, e) in res.items() if np.isfinite(v)]; cons = np.nan; ce = np.nan; nl = 0
            if len(vals) >= 2:
                med = np.median([v for _, v, _ in vals]); ok = [(v, e) for _, v, e in vals if abs(v - med) <= max(3 * e, 40)]
                if len(ok) >= 2:
                    vs_ = np.array(ok); cons = vs_[:, 0].mean(); nl = len(ok); ce = max(vs_[:, 0].std(ddof=1) / np.sqrt(nl), np.median(vs_[:, 1]) / np.sqrt(nl), 8)
            rows.append(dict(sdss_id=sid, mjd=int(r.mjd), fieldid=int(r.fieldid), in_stack=r.in_stack, exp=x.name, bjd=round(t, 5), **{f"v_{n}": round(v, 1) for n, (v, e) in res.items()},
                             **{f"e_{n}": round(e, 1) for n, (v, e) in res.items()}, v=round(cons, 1) if np.isfinite(cons) else np.nan, e=round(ce, 1) if np.isfinite(ce) else np.nan, n_lines=nl))
    print(sid, "done", flush=True)
pd.DataFrame(rows).to_csv(sys.argv[2], index=False); print("DONE")
