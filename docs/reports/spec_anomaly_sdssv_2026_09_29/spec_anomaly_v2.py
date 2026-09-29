"""Blind spectral-anomaly search v2 over the SDSS-V DR20 white-dwarf coadd store (2026-09-29).
v1 found mostly instrument effects: single-pixel spikes surviving the coadd, blue/red camera-join steps near 5900-6400 A, sky residuals.
v2: coadd S/N >= 12; range 3900-8800 A; sky/telluric windows masked; weighted PCA basis (K=12) from a random training half;
iterative reconstruction that masks isolated spikes (|r| sqrt(w) > 5 with width <= 2 px); features scored in 30-A and 80-A windows
(robust z vs objects of similar S/N). The top 400 by window score (excluding +-25 A around H-alpha, whose emission is covered by the
H-alpha screen) are then re-measured in every individual visit (raw mwmVisit, the Astra velocity shift undone for in_stack visits):
each visit is normalised, rebinned to the coadd grid, fitted with the same basis, and its mean residual in the same window measured.
verdict: 'persistent' = >= 2 visits with |res|/err > 3 and the same sign as the coadd; 'single-visit' = only one usable visit;
'not persistent' otherwise. Output: v2_scores.csv, v2_candidates.csv."""
import os, glob, numpy as np, pandas as pd, time
from astropy.io import fits
S = os.path.expanduser("~/claude_projects/spectra_store/sdssv_dr20"); H = os.path.dirname(os.path.abspath(__file__)); K = 12; C = 299792.458
g = np.load(f"{S}/coadd_grid.npy"); n2 = len(g) // 2; gb = 0.5 * (g[0:2*n2:2] + g[1:2*n2:2])
T = pd.read_csv(f"{S}/targets.csv", dtype=str, low_memory=False).set_index("sdss_id")
keep = (gb > 3900) & (gb < 8800)
for a, b in ((5570, 5585), (6295, 6305), (6860, 6960), (7590, 7700), (8280, 8330)): keep &= ~((gb > a) & (gb < b))
lam = gb[keep]; nw = (lam > 4000) & (lam < 7000)
def prep(f, iv):
    f = f[:2*n2].reshape(-1, 2); iv = iv[:2*n2].reshape(-1, 2); s = iv.sum(1)
    fb = np.where(s > 0, (f * iv).sum(1) / np.where(s > 0, s, 1), np.nan)[keep]; ivb = s[keep]
    med = np.nanmedian(fb[nw])
    if not np.isfinite(med) or med <= 0: return None, None
    F = fb / med; W = ivb * med**2; bad = ~np.isfinite(F) | (W <= 0); F[bad] = 0; W[bad] = 0
    W = np.where(W > 0, 1.0 / (1.0 / np.where(W > 0, W, 1) + (0.03 * np.clip(np.abs(F), 0.05, None))**2), 0); return F, W
ids, FF, WW, snr = [], [], [], []
for fp in glob.glob(f"{S}/coadd_store/*/*.npz"):
    d = np.load(fp); s = float(np.atleast_1d(d["snr"]).max())
    if s < 12: continue
    F, W = prep(d["f"], d["iv"])
    if F is None: continue
    ids.append(os.path.basename(fp)[:-4]); FF.append(F.astype(np.float32)); WW.append(W.astype(np.float32)); snr.append(s)
FF = np.array(FF); WW = np.array(WW); snr = np.array(snr); print(len(ids), "spectra", flush=True)
rng = np.random.default_rng(2); tr = rng.random(len(ids)) < 0.5
Ft = FF[tr].copy(); cm = np.median(np.where(WW[tr] > 0, Ft, np.nan), axis=0); cm = np.where(np.isfinite(cm), cm, 1.0)
Ft = np.where(WW[tr] > 0, Ft, cm); mu = Ft.mean(0); _, Sv, Vt = np.linalg.svd(Ft - mu, full_matrices=False); B = Vt[:K]
def fit(F, W):
    w = W.copy()
    for it in range(3):
        c = np.linalg.lstsq((B * w) @ B.T, (B * w) @ (F - mu), rcond=None)[0]; r = F - mu - c @ B
        z = r * np.sqrt(w); hot = np.abs(z) > 5
        iso = hot & ~(np.roll(hot, 1) & np.roll(hot, -1)) & ~(np.roll(hot, 2) & np.roll(hot, 1) & np.roll(hot, -1))
        if not iso.any(): break
        w = np.where(iso, 0, w)
    return r, w
def windows(r, w, width):
    n = max(1, int(round(width / np.median(np.diff(lam))))); m = (w > 0).astype(float)
    cnt = np.convolve(m, np.ones(n), "same"); sm = np.convolve(np.where(w > 0, r, 0), np.ones(n), "same") / np.where(cnt > 0, cnt, 1)
    ev = np.sqrt(np.convolve(np.where(w > 0, 1 / np.where(w > 0, w, 1), 0), np.ones(n), "same")) / np.where(cnt > 0, cnt, 1)
    sm[cnt < 0.6 * n] = 0; excl = np.abs(lam - 6564.6) < 25; sm[excl] = 0; return sm, ev
rows = []
for i in range(len(ids)):
    r, w = fit(FF[i], WW[i]); rec = dict(sdss_id=ids[i], snr=snr[i], chi2r=float((r[w > 0]**2 * w[w > 0]).sum() / max((w > 0).sum() - K, 1)))
    for width in (30, 80):
        sm, ev = windows(r, w, width); k = int(np.argmax(np.abs(sm))); rec[f"win{width}"] = float(sm[k]); rec[f"win{width}_c"] = float(lam[k]); rec[f"win{width}_sig"] = float(abs(sm[k]) / ev[k]) if ev[k] > 0 else 0
    rows.append(rec)
D = pd.DataFrame(rows)
for c_ in ("sig30", "sig80"):
    col = "win30_sig" if c_ == "sig30" else "win80_sig"; b = np.digitize(D.snr, [12, 18, 25, 35, 50, 80, 1e9]); z = np.zeros(len(D))
    for k in np.unique(b):
        m = b == k; v = np.log10(D.loc[m, col].clip(lower=1e-3)); med = v.median(); mad = 1.4826 * (v - med).abs().median(); z[m] = (v - med) / (mad or 1)
    D["z_" + c_] = z
D["z_best"] = D[["z_sig30", "z_sig80"]].max(1); D["best_width"] = np.where(D.z_sig30 >= D.z_sig80, 30, 80)
D["best_center"] = np.where(D.best_width == 30, D.win30_c, D.win80_c); D["best_res"] = np.where(D.best_width == 30, D.win30, D.win80)
for col, src in (("gaia", "gaia_dr3_source_id"), ("cls", "classification"), ("G", "g_mag"), ("MG", "MG"), ("bprp", "bprp")): D[col] = T[src].reindex(D.sdss_id).values
D.to_csv(os.path.join(H, "v2_scores.csv"), index=False); print("scored", flush=True)
# visit persistence for the top 400
top = D.sort_values("z_best", ascending=False).head(400); out = []
for _, t in top.iterrows():
    s = t.sdss_id; p = f"{S}/visit/{s[-4:-2]}/{s[-2:]}/mwmVisit-0.8.1-{s}.fits"; res = []
    try: h = fits.open(p)
    except Exception: out.append(dict(sdss_id=s, n_vis=0, verdict="no visit file")); continue
    for hi in (1, 2):
        if h[hi].data is None or len(h[hi].data) == 0: continue
        hd = h[hi].header; wg = 10 ** (hd["CRVAL"] + hd["CDELT"] * np.arange(hd["NPIXELS"]))
        for v in h[hi].data:
            vr = float(v["xcsao_v_rad"]); w0 = wg * (1 + vr / C) if (bool(v["in_stack"]) and np.isfinite(vr)) else wg
            f = np.interp(g, w0, np.array(v["flux"], float), left=np.nan, right=np.nan); iv = np.interp(g, w0, np.array(v["ivar"], float), left=0, right=0)
            F, W = prep(f, iv)
            if F is None or (W > 0).sum() < 0.5 * len(W): continue
            r, w = fit(F, W); sm, ev = windows(r, w, int(t.best_width)); k = int(np.argmin(np.abs(lam - t.best_center)))
            if ev[k] > 0: res.append((int(v["mjd"]), float(sm[k]), float(ev[k])))
    nv = len(res); agree = sum(1 for _, a, e in res if abs(a) / e > 3 and np.sign(a) == np.sign(t.best_res))
    verdict = "single-visit" if nv <= 1 else ("persistent" if agree >= 2 else "not persistent")
    out.append(dict(sdss_id=s, n_vis=nv, n_agree=agree, verdict=verdict, visits="; ".join(f"{m}:{a:+.3f}+-{e:.3f}" for m, a, e in res)))
V = top.merge(pd.DataFrame(out), on="sdss_id"); V.to_csv(os.path.join(H, "v2_candidates.csv"), index=False)
print("done;", V.verdict.value_counts().to_dict(), flush=True)
