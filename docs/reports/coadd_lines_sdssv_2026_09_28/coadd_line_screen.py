"""Multi-line screen of the full coadds (coadd_store): He II 4686 and 5412 (DAO), He I 4471, 5876 and 6678 (DAB / helium in DA),
and the UHE features at 4500, 5290, 5673 and 6068 A. For each object and line, the +-150 A window is normalised by a straight line
through the medians of the outer 40 A on each side; a photospheric template is the median normalised window of the 40 nearest
neighbours in BP-RP (same class group: DA / non-H / WD+MS / CV, |dBP-RP| < 0.2, coadd S/N > 8, self excluded), fitted as
1 + a (t_blue - 1) + b (t_red - 1) over pixel shifts +-2 for the DA group (plain median otherwise), with residuals inside +-25 A of the
line excluded from the fit so a real line cannot steer it. Matched filters on the residual: Gaussian absorption (sigma 2, 4, 8 A) and
emission (same), velocities -400..+400 km/s (UHE lines +-1500 km/s, they can be shifted and broad); z = sum(w r T)/sqrt(sum(w T^2)),
negative for absorption. Errors: quadrature sum of the coadd error and 0.15 (DA) / 0.05 (other) times the neighbour scatter.
Output: one row per object with z_abs/z_em per line, the line EW (A) at the best velocity, coadd S/N per window, class group.
Usage: python coadd_line_screen.py --out coadd_lines.csv [--limit N] [--ids a,b]"""
import os, glob, argparse, warnings, numpy as np, pandas as pd
warnings.filterwarnings("ignore")
ap = argparse.ArgumentParser(); ap.add_argument("--out", required=True); ap.add_argument("--limit", type=int, default=0); ap.add_argument("--ids", default=""); A = ap.parse_args()
D = os.path.dirname(os.path.abspath(__file__)); C = 299792.458; G = np.load(os.path.join(D, "coadd_grid.npy"))
T = pd.read_csv(os.path.join(D, "targets.csv"), dtype={"sdss_id": str, "gaia_dr3_source_id": str}).set_index("sdss_id")
LINES = {"HeII4686": (4687.0, 400), "HeII5412": (5413.0, 400), "HeI4471": (4472.7, 400), "HeI5876": (5877.2, 400), "HeI6678": (6679.9, 400),
         "UHE4500": (4500.0, 1500), "UHE5290": (5290.0, 1500), "UHE5673": (5673.0, 1500), "UHE6068": (6068.0, 1500)}
def group(c):
    c = str(c)
    if "CV" in c: return "CV"
    if "MS" in c: return "MS"
    if "DA" in c: return "DA"
    return "nonH"
files = sorted(glob.glob(os.path.join(D, "coadd_store", "*", "*.npz"))); ids_all = [os.path.basename(f)[:-4] for f in files]
# load all coadds' line windows (normalised) into memory: dict line -> array (nobj x npix)
WIN = {}; IDX = {}
for k, (lam, vmax) in LINES.items():
    m = np.abs(G - lam) < 150; IDX[k] = m; WIN[k] = {}
META = []; NORM = {k: [] for k in LINES}; ERR = {k: [] for k in LINES}; keep = []
for f, sid in zip(files, ids_all):
    if sid not in T.index: continue
    d = np.load(f); fl = d["f"].astype(float); iv = d["iv"].astype(float); ok = (iv > 0) & np.isfinite(fl); row = []; rows_ok = True; tmpn = {}; tmpe = {}
    for k, (lam, vmax) in LINES.items():
        m = IDX[k]; w = G[m]; y = fl[m]; e = np.where(ok[m], 1 / np.sqrt(np.where(ok[m], iv[m], 1e-12)), np.inf)
        L = (w < lam - 110); R = (w > lam + 110); okm = ok[m]
        if (okm & L).sum() < 5 or (okm & R).sum() < 5: tmpn[k] = None; continue
        yl, yr = np.median(y[okm & L]), np.median(y[okm & R]); xl, xr = np.median(w[okm & L]), np.median(w[okm & R])
        if yl <= 0 or yr <= 0: tmpn[k] = None; continue
        cont = yl + (yr - yl) * (w - xl) / (xr - xl); tmpn[k] = (y / cont).astype(np.float32); tmpe[k] = (e / cont).astype(np.float32)
    keep.append(sid); m_ = T.loc[sid]; META.append(dict(sdss_id=sid, grp=group(m_.classification), bprp=float(m_.bprp) if np.isfinite(m_.bprp) else np.nan, snr=float(np.nanmedian(d["snr"])) if len(d["snr"]) else np.nan))
    for k in LINES:
        NORM[k].append(tmpn.get(k) if tmpn.get(k) is not None else np.full(int(IDX[k].sum()), np.nan, np.float32)); ERR[k].append(tmpe.get(k) if tmpn.get(k) is not None else np.full(int(IDX[k].sum()), np.inf, np.float32))
META = pd.DataFrame(META).set_index("sdss_id"); NORM = {k: np.array(v) for k, v in NORM.items()}; ERR = {k: np.array(v) for k, v in ERR.items()}; POS = {s: i for i, s in enumerate(keep)}
print("coadds loaded", len(META), META.grp.value_counts().to_dict(), flush=True)
def neighbours(sid):
    m = META.loc[sid]; pool = META[(META.grp == m.grp) & (META.index != sid) & (META.snr > 8) & np.isfinite(META.bprp)]
    if not np.isfinite(m.bprp) or len(pool) < 10: return None
    pool = pool.assign(d=(pool.bprp - m.bprp).abs()); pool = pool[pool.d < 0.2].nsmallest(40, "d").sort_values("bprp")
    return list(pool.index) if len(pool) >= 10 else None
def fit_template(n, e, t1, t2, w, lam, do_fit):
    if not do_fit: return (t1 + t2) / 2
    ok = np.isfinite(e) & np.isfinite(n); w0 = np.where(ok, 1 / e ** 2, 0); near = np.abs(w - lam) < 25; best = (np.inf, None)
    for sh in (-2, -1, 0, 1, 2):
        x1 = np.roll(t1, sh) - 1; x2 = np.roll(t2, sh) - 1; X = np.vstack([x1, x2]).T; y = np.nan_to_num(n - 1); wt = np.where(near, 0.0, w0)
        Aw = X * wt[:, None]; cf = np.linalg.lstsq(Aw.T @ X + 1e-4 * np.eye(2), Aw.T @ y, rcond=None)[0]; model = 1 + X @ cf; chi2 = float((wt * (np.nan_to_num(n) - model) ** 2).sum())
        if chi2 < best[0]: best = (chi2, model)
    return best[1]
def matched(r, e, w, lam, vmax):
    vel = np.arange(-vmax, vmax + 1, 25.0); wgt = np.where(np.isfinite(e), 1 / e ** 2, 0); d = np.where(np.isfinite(e) & np.isfinite(r), r, 0.0); out = {}
    for s in (2.0, 4.0, 8.0):
        Tm = np.exp(-0.5 * ((w[None, :] - lam * (1 + vel / C)[:, None]) / s) ** 2); num = (Tm * (wgt * d)[None, :]).sum(1); den = np.sqrt((Tm ** 2 * wgt[None, :]).sum(1)); z = num / np.where(den > 0, den, np.inf)
        ka, ke = int(np.argmin(z)), int(np.argmax(z)); out[s] = (float(z[ka]), float(vel[ka]), float(z[ke]), float(vel[ke]))
    sa = min(out, key=lambda s: out[s][0]); se = max(out, key=lambda s: out[s][2])
    return out[sa][0], out[sa][1], sa, out[se][2], out[se][3], se
ids = A.ids.split(",") if A.ids else list(META.index)
done = set(pd.read_csv(A.out, dtype={"sdss_id": str}).sdss_id) if os.path.exists(A.out) and not A.ids else set()
ids = [s for s in ids if s not in done and s in META.index]; ids = ids[:A.limit] if A.limit else ids; print("to screen", len(ids), flush=True)
rows = []
for j, sid in enumerate(ids):
    nb = neighbours(sid); m = T.loc[sid]; rec = dict(sdss_id=sid, gaia=m.gaia_dr3_source_id, cls=m.classification, grp=META.loc[sid].grp, G=m.g_mag, bprp=m.bprp, MG=m.MG, snr=round(META.loc[sid].snr, 1), n_tmpl=(len(nb) if nb else 0))
    if nb is None: rec["status"] = "no_template"; rows.append(rec); continue
    p = POS[sid]; nbi = [POS[s] for s in nb]; h = len(nbi) // 2; fsys = 0.15 if META.loc[sid].grp == "DA" else 0.05
    for k, (lam, vmax) in LINES.items():
        w = G[IDX[k]]; n = NORM[k][p].astype(float); e = ERR[k][p].astype(float)
        if not np.isfinite(n).any(): continue
        S = NORM[k][nbi].astype(float); t1 = np.nanmedian(S[:h], 0); t2 = np.nanmedian(S[h:], 0); sc = np.nanmedian(np.nanstd(S[:, np.abs(w - lam) < 60], 0))
        if not (np.isfinite(t1).all() and np.isfinite(t2).all()): continue
        model = fit_template(n, e, t1, t2, w, lam, META.loc[sid].grp == "DA"); r = n - model; ee = np.sqrt(e ** 2 + (fsys * sc) ** 2)
        za, va, sa, ze, ve, se = matched(r, ee, w, lam, vmax)
        core = (np.abs(w - lam * (1 + va / C)) < 3 * sa) & np.isfinite(r); ew = float((-r[core] * np.gradient(w)[core]).sum()) if core.any() else np.nan
        rec.update({f"{k}_zabs": round(za, 2), f"{k}_vabs": va, f"{k}_sabs": sa, f"{k}_ew": round(ew, 3), f"{k}_zem": round(ze, 2), f"{k}_vem": ve, f"{k}_snr": round(float(np.nanmedian(1 / e[np.isfinite(e)])), 1) if np.isfinite(e).any() else np.nan})
    rec["status"] = "ok"; rows.append(rec)
    if (j + 1) % 2000 == 0: pd.DataFrame(rows).to_csv(A.out, mode="a", header=not os.path.exists(A.out), index=False); rows = []; print(j + 1, "screened", flush=True)
if rows: pd.DataFrame(rows).to_csv(A.out, mode="a", header=not os.path.exists(A.out), index=False)
print("done")
