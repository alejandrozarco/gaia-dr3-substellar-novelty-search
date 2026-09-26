"""H-alpha emission and visit-to-visit variability screen of the stored SDSS-V DR20 white-dwarf spectra (store/ from gasdisc_screen.py).
Region 6400-6750 A (log grid 6e-5 dex). Continuum: straight line through the medians of 6405-6440 and 6700-6745 A.
Emission: n = f/cont, smoothed with a 2-pixel Gaussian; e_n from ivar (smoothed in quadrature, /sqrt(n_eff));
emis_sig = max over 6450-6690 A of (n - 1) / e_n for runs of >= 3 consecutive pixels above 1 + 3 e_n (the run minimum), and
emis_wl, emis_amp at that run. Only flux ABOVE the continuum counts, so ordinary Balmer absorption cannot mimic it.
Variability (objects with >= 2 visits of S/N >= 8 in the region): per-visit EW over 6524-6604 A (+-40 A around H-alpha, emission positive)
with errors; chi2_ew / dof about the weighted mean; and pair_chi2: the largest reduced chi2 of the difference of two normalised
visit profiles over 6500-6630 A. Output halpha_screen.csv."""
import os, glob, numpy as np, pandas as pd
from scipy.ndimage import gaussian_filter1d
GRID = 10 ** np.arange(np.log10(3850), np.log10(9250), 6e-5); m = (GRID > 6400) & (GRID < 6750); W = GRID[m]
L = (W > 6405) & (W < 6440); R = (W > 6700) & (W < 6745); E = (W > 6450) & (W < 6690); CORE = np.abs(W - 6564.6) < 40; PR = (W > 6500) & (W < 6630)
dl = np.gradient(W)
def norm(f, iv):
    ok = (iv > 0) & np.isfinite(f)
    if ok[L].sum() < 5 or ok[R].sum() < 5 or ok.sum() < 150: return None
    yl, yr = np.median(f[L & ok]), np.median(f[R & ok]); xl, xr = np.median(W[L & ok]), np.median(W[R & ok])
    cont = yl + (yr - yl) * (W - xl) / (xr - xl)
    if np.any(cont <= 0): return None
    n = np.where(ok, f / cont, np.nan); e = np.where(ok, 1 / np.sqrt(np.where(ok, iv, 1)) / cont, np.nan)
    return n, e, ok
def emission(n, e, ok):
    ns = gaussian_filter1d(np.nan_to_num(n, nan=1.0), 2); es = np.sqrt(gaussian_filter1d(np.nan_to_num(e, nan=1e3) ** 2, 2)) / np.sqrt(2 * np.sqrt(np.pi) * 2)
    z = (ns - 1) / es; best = (0.0, np.nan, np.nan); run = []
    for i in np.where(E)[0]:
        if z[i] > 3 and ok[i]: run.append(i)
        else:
            if len(run) >= 3:
                zm = float(np.min(z[run])); k = run[int(np.argmax(z[run]))]
                if zm > best[0]: best = (zm, float(W[k]), float(ns[k] - 1))
            run = []
    return best
rows = []
for fn in glob.glob("store/*/*.npz"):
    sid = os.path.basename(fn)[:-4]; d = np.load(fn); row = dict(sdss_id=sid)
    c = norm(d["f_6400"].astype(float), d["iv_6400"].astype(float))
    if c is None: continue
    n, e, ok = c; row["snr_ha"] = round(float(np.nanmedian(1 / e[L | R])), 1)
    row["emis_sig"], row["emis_wl"], row["emis_amp"] = [round(x, 3) if np.isfinite(x) else x for x in emission(n, e, ok)]
    vis = []
    for vf, viv, mj in zip(d["vf_6400"], d["viv_6400"], d["mjd"]):
        cv = norm(vf.astype(float), viv.astype(float))
        if cv is None: continue
        nv, ev, okv = cv
        if np.nanmedian(1 / ev[L | R]) < 8 or okv[CORE].sum() < CORE.sum() * 0.9: continue
        ew = float(np.nansum(((nv - 1) * dl)[CORE])); eew = float(np.sqrt(np.nansum((ev * dl)[CORE] ** 2))); vis.append((mj, ew, eew, nv, ev))
    row["n_vis_good"] = len(vis)
    if len(vis) >= 2:
        ews = np.array([v[1] for v in vis]); ees = np.array([v[2] for v in vis]); w = 1 / ees ** 2; mu = np.sum(w * ews) / np.sum(w)
        row["ew_core_mean"] = round(mu, 2); row["ew_core_range"] = round(float(ews.max() - ews.min()), 2)
        row["chi2_ew"] = round(float(np.sum(w * (ews - mu) ** 2) / (len(vis) - 1)), 2)
        best = 0.0
        for i in range(len(vis)):
            for j in range(i + 1, len(vis)):
                a, b = vis[i], vis[j]; okp = PR & np.isfinite(a[3]) & np.isfinite(b[3])
                if okp.sum() < 50: continue
                x = np.sum((a[3][okp] - b[3][okp]) ** 2 / (a[4][okp] ** 2 + b[4][okp] ** 2)) / okp.sum(); best = max(best, x)
        row["pair_chi2"] = round(float(best), 2); row["mjds"] = "/".join(str(v[0]) for v in vis); row["ews"] = "/".join(f"{v[1]:.1f}" for v in vis)
    rows.append(row)
pd.DataFrame(rows).to_csv("halpha_screen.csv", index=False); print(len(rows), "objects")
