"""Independent-line check of H-alpha RV candidates: per SDSS-V visit (sdssv.visits: XCSAO shift removed for in_stack visits),
velocity of H-alpha, H-beta and H-gamma separately against the star's own coadd (each line: linear continuum from +-2500 to
+-3500 km/s windows; chi2 over |v| < 1500 km/s; shifts -700..+700 km/s, 5 km/s, parabola refinement). Output rv_multi.csv."""
import os
import sys, numpy as np, pandas as pd
sys.path.insert(0, os.path.expanduser("~/claude_projects/sdssv-white-dwarfs-2026/scripts")); import sdssv
C = 299792.458; LINES = {"Ha": 6564.61, "Hb": 4862.68, "Hg": 4341.69}; S = np.arange(-700, 701, 5.0)
def seg(w, f, iv, l):
    v = (w / l - 1) * C; m = (np.abs(v) < 3500) & (iv > 0) & np.isfinite(f); v, f, iv = v[m], f[m], iv[m]
    c = (np.abs(v) > 2500)
    if c.sum() < 6: return None
    p = np.polyfit(v[c], f[c], 1, w=np.sqrt(iv[c])); cc = np.polyval(p, v)
    if np.median(cc) <= 0: return None
    return v, f / cc, iv * cc ** 2
rows = []
for sid in sys.argv[1:]:
    try: vs = [v for v in sdssv.visits(sid) if ((v["ivar"] > 0) & np.isfinite(v["flux"])).sum() > 1000]
    except Exception as ex: print(sid, "HOLE"); continue
    w, f, iv = sdssv.coadd(vs)[:3]
    for name, l in LINES.items():
        T = seg(w, f, iv, l)
        if T is None: continue
        tv, tf, _ = T
        for v in vs:
            X = seg(v["wave"], v["flux"], v["ivar"], l)
            if X is None: continue
            xv, xf, xi = X; m = np.abs(xv) < 1500
            if m.sum() < 20: continue
            chi = np.array([np.sum((xf[m] - np.interp(xv[m] - s, tv, tf)) ** 2 * xi[m]) for s in S]); i = int(np.argmin(chi)); dof = m.sum() - 1
            if 0 < i < len(S) - 1:
                a, b, _ = np.polyfit(S[i - 1:i + 2], chi[i - 1:i + 2], 2); best = -b / (2 * a) if a > 0 else S[i]; e = np.sqrt(max(chi[i] / dof, 1) / a) if a > 0 else np.nan
            else: best, e = S[i], np.nan
            rows.append(dict(sdss_id=sid, mjd=v["mjd"], in_stack=v["in_stack"], xcsao=round(v["xcsao_v"], 1), line=name, rv=round(best, 1), e_rv=round(e, 1), snr=round(v["snr"], 1)))
out = pd.DataFrame(rows); out.to_csv("rv_multi.csv", index=False)
p = out.pivot_table(index=["sdss_id", "mjd", "in_stack", "xcsao"], columns="line", values="rv").reset_index()
pd.set_option("display.width", 200); print(p.to_string())
