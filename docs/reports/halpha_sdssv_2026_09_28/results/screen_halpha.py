"""Stage 2 of the H-alpha screen: neighbour-template subtraction and matched filters.
For every extracted object (halpha_store), a photospheric template is the median normalised coadd of its 40 nearest neighbours in
BP-RP (|dBP-RP| < 0.2, coadd S/N > 8, same class group: DA-like / non-H / WD+MS / CV, self excluded). Residuals r = n - template for the
coadd and each visit. Channels: narrow (Gaussian sigma 1.5, 3, 6 A; -600..+600 km/s) and broad (sigma 3, 6, 10, 15 A; -3000..+3000 km/s),
z = sum(w r T)/sqrt(sum(w T^2)). Per object: z_coadd, z_max (visits), EW per visit at the coadd velocity, chi2 of EW variability,
template quality (number of neighbours, template scatter at H-alpha). --inject EW adds a Gaussian emission (sigma 3 A) at H-alpha to
every spectrum before the residual. Usage: python screen_halpha.py --out screen.csv [--inject EW] [--limit N] [--ids a,b]"""
import os, glob, argparse, warnings, numpy as np, pandas as pd
warnings.filterwarnings("ignore")
ap = argparse.ArgumentParser(); ap.add_argument("--out", required=True); ap.add_argument("--inject", type=float, default=0.0); ap.add_argument("--limit", type=int, default=0); ap.add_argument("--ids", default=""); A = ap.parse_args()
D = os.path.dirname(os.path.abspath(__file__)); C = 299792.458; HA = 6564.61; W = np.load(os.path.join(D, "halpha_store_grid.npy")); dl = np.gradient(W)
T = pd.read_csv(os.path.join(D, "targets.csv"), dtype={"sdss_id": str, "gaia_dr3_source_id": str}).set_index("sdss_id")
def group(c):
    c = str(c)
    if "CV" in c: return "CV"
    if "MS" in c: return "MS"
    if "DA" in c: return "DA"
    return "nonH"
VEL = np.arange(-600, 601, 25.0); TM = {s: np.exp(-0.5 * ((W[None, :] - HA * (1 + VEL / C)[:, None]) / s) ** 2) for s in (1.5, 3.0, 6.0)}
VELB = np.arange(-3000, 3001, 50.0); TMB = {s: np.exp(-0.5 * ((W[None, :] - HA * (1 + VELB / C)[:, None]) / s) ** 2) for s in (3.0, 6.0, 10.0, 15.0)}
def matched(r, e, tm, vel):
    w = np.where(np.isfinite(e), 1 / e ** 2, 0); d = np.where(np.isfinite(e), r, 0.0); best = (-np.inf, 0.0, 0.0)
    for s, Tm in tm.items():
        num = (Tm * (w * d)[None, :]).sum(1); den = np.sqrt((Tm ** 2 * w[None, :]).sum(1)); z = num / np.where(den > 0, den, np.inf); k = int(np.argmax(z))
        if z[k] > best[0]: best = (float(z[k]), float(vel[k]), s)
    return best
def ew(r, e, v, width=10.0):
    lam = HA * (1 + v / C); m = (np.abs(W - lam) < width) & np.isfinite(e); return float((r[m] * dl[m]).sum()), float(np.sqrt(((e[m] * dl[m]) ** 2).sum()))
def npix(r, e, v, width=10.0):
    lam = HA * (1 + v / C); m = (np.abs(W - lam) < width) & np.isfinite(e); return int(((r / e)[m] > 1.5).sum())
CORE = np.abs(W - HA) < 60
# load coadds
files = sorted(glob.glob(os.path.join(D, "halpha_store", "*", "*.npz"))); ids_all = [os.path.basename(f)[:-4] for f in files]
NC, EC, META = {}, {}, []
for f, sid in zip(files, ids_all):
    d = np.load(f)
    if "empty" in d.files or sid not in T.index: continue
    NC[sid] = d["n_c"].astype(float); EC[sid] = d["e_c"].astype(float); m = T.loc[sid]
    META.append(dict(sdss_id=sid, grp=group(m.classification), bprp=float(m.bprp) if np.isfinite(m.bprp) else np.nan, snr_c=float(np.nanmedian(1 / EC[sid][np.isfinite(EC[sid])]))))
META = pd.DataFrame(META).set_index("sdss_id"); print("coadds loaded", len(META), META.grp.value_counts().to_dict(), flush=True)
ap_sys = float(os.environ.get("HA_SYS", "0.15"))  # template systematic: fraction of the neighbour scatter added per pixel in quadrature
SHIFTS = (-2, -1, 0, 1, 2)  # pixel shifts of the template (1 px = 1e-4 dex = 69 km/s)
def template(sid):
    """Two neighbour templates (bluer and redder halves of the 40 nearest in BP-RP) and their scatter."""
    m = META.loc[sid]; pool = META[(META.grp == m.grp) & (META.index != sid) & (META.snr_c > 8) & np.isfinite(META.bprp)]
    if not np.isfinite(m.bprp) or len(pool) < 10: return None, 0, np.nan
    pool = pool.assign(d=(pool.bprp - m.bprp).abs()); pool = pool[pool.d < 0.2].nsmallest(40, "d").sort_values("bprp")
    if len(pool) < 10: return None, len(pool), np.nan
    S = np.array([NC[s] for s in pool.index]); h = len(S) // 2; fsys = ap_sys if m.grp == "DA" else ap_sys / 3
    t1, t2 = np.nanmedian(S[:h], 0), np.nanmedian(S[h:], 0); sc = np.nanstd(S, 0) / np.sqrt(len(S)) + fsys * np.nanmedian(np.nanstd(S[:, CORE], 0))
    return (t1, t2, len(pool)), len(pool), sc
def fit_template(n, e, tt):
    """Best linear combination 1 + a (t1-1) + b (t2-1) over pixel shifts; returns the model and the fitted residual."""
    t1, t2 = tt[0], tt[1]
    if tt[2] < 30: return (t1 + t2) / 2  # few neighbours: plain median template, no fit
    ok = np.isfinite(e); w0 = np.where(ok, 1 / e ** 2, 0); best = (np.inf, None); near = np.abs(W - HA) < 80
    for sh in SHIFTS:
        x1 = np.roll(t1, sh) - 1; x2 = np.roll(t2, sh) - 1; X = np.vstack([x1, x2]).T; y = n - 1; w = w0.copy()
        for it in range(2):
            Aw = X * w[:, None]; cf = np.linalg.lstsq(Aw.T @ X + 1e-4 * np.eye(2), Aw.T @ y, rcond=None)[0]; model = 1 + X @ cf
            up = ((n - model) / e > 2.5) & near & ok  # upward deviations near H-alpha (candidate emission) do not steer the fit
            if it == 0: w = np.where(up, 0.0, w0)
        chi2 = float((w0 * ~up * (n - model) ** 2).sum())
        if chi2 < best[0]: best = (chi2, model)
    return best[1]
ids = A.ids.split(",") if A.ids else list(META.index)
done = set(pd.read_csv(A.out, dtype={"sdss_id": str}).sdss_id) if os.path.exists(A.out) and not A.ids else set()
ids = [s for s in ids if s not in done and s in META.index]; ids = ids[:A.limit] if A.limit else ids; print("to screen", len(ids), flush=True)
INJ = A.inject / (np.sqrt(2 * np.pi) * 3.0) * np.exp(-0.5 * ((W - HA) / 3.0) ** 2) if A.inject > 0 else 0.0
rows = []
for k, sid in enumerate(ids):
    tm, nn, sc = template(sid); m = T.loc[sid]
    if tm is None: rows.append(dict(sdss_id=sid, gaia=m.gaia_dr3_source_id, cls=m.classification, grp=META.loc[sid].grp, status=f"no_template({nn})")); continue
    d = np.load(os.path.join(D, "halpha_store", sid[-2:], f"{sid}.npz")); n_c = NC[sid] + INJ; e_c0 = EC[sid]; model = fit_template(n_c, e_c0, tm); r_c = n_c - model
    e_c = np.sqrt(e_c0 ** 2 + sc ** 2)
    zc, vc, sgc = matched(r_c, e_c, TM, VEL); zbc, vbc, sbc = matched(r_c, e_c, TMB, VELB); ewc, eewc = ew(r_c, e_c, vc); npc = npix(r_c, e_c, vc)
    zs, zbs, ews, eews, vs = [], [], [], [], []
    for i in range(len(d["mjd"])):
        n_i = d["n"][i].astype(float) + INJ; e_i0 = d["e"][i].astype(float); r_i = n_i - fit_template(n_i, e_i0, tm); e_i = np.sqrt(e_i0 ** 2 + sc ** 2)
        z, v, s = matched(r_i, e_i, TM, VEL); zb, vb, sb = matched(r_i, e_i, TMB, VELB); w_, we_ = ew(r_i, e_i, vc); zs.append(z); zbs.append(zb); ews.append(w_); eews.append(we_); vs.append(v)
    ews = np.array(ews); eews = np.array(eews); wm = (ews / eews ** 2).sum() / (1 / eews ** 2).sum(); chi2 = float((((ews - wm) / eews) ** 2).sum() / (len(ews) - 1)) if len(ews) > 1 else np.nan
    rows.append(dict(sdss_id=sid, gaia=m.gaia_dr3_source_id, cls=m.classification, grp=META.loc[sid].grp, G=m.g_mag, bprp=m.bprp, MG=m.MG, nvis=len(zs), snr_c=round(META.loc[sid].snr_c, 1), n_tmpl=nn, tmpl_scatter=round(float(np.nanmedian(sc[CORE])), 4),
                     z_coadd=round(zc, 2), v_coadd=vc, sig_coadd=sgc, npx_coadd=npc, ew_coadd=round(ewc, 3), e_ew_coadd=round(eewc, 3), zb_coadd=round(zbc, 2), vb_coadd=vbc, sb_coadd=sbc,
                     z_max=round(max(zs), 2), n_vis_z3=int(sum(z > 3 for z in zs)), zb_max=round(max(zbs), 2), z_visits="/".join(f"{z:.1f}" for z in zs), zb_visits="/".join(f"{z:.1f}" for z in zbs), v_visits="/".join(f"{v:.0f}" for v in vs),
                     ew_visits="/".join(f"{x:.2f}" for x in ews), e_ew_visits="/".join(f"{x:.2f}" for x in eews), chi2_ew=round(chi2, 2) if np.isfinite(chi2) else np.nan, mjds="/".join(map(str, d["mjd"])), status="ok"))
    if (k + 1) % 1000 == 0: pd.DataFrame(rows).to_csv(A.out, mode="a", header=not os.path.exists(A.out), index=False); rows = []; print(k + 1, "screened", flush=True)
if rows: pd.DataFrame(rows).to_csv(A.out, mode="a", header=not os.path.exists(A.out), index=False)
print("done")
