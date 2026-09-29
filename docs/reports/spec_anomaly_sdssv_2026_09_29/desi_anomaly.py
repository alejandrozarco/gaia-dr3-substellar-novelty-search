"""Blind spectral-anomaly search over the DESI DR1 white-dwarf store (2026-09-29); the DESI counterpart of spec_anomaly_v2.py
(SDSS-V), which found the CH band in LP 133-754.
Spectra with S/N >= 10 (median f*sqrt(ivar), 4500-5500 A); range 3800-8800 A; sky lines, telluric bands and the DESI camera
joins (5740-5820, 7500-7640 A) masked; normalised by the median flux in 4000-7000 A; 3% systematic floor.
Weighted PCA basis (K=20, larger than SDSS-V's 12 because the table mixes many WD types) from a random training half; each
spectrum is reconstructed with isolated-spike masking, and scored by the most significant mean residual in 30-A and 80-A
windows (H-alpha +-25 A excluded), as a robust z within S/N bins. No visit-persistence test is possible (coadds only), so
candidates need visual inspection. Output: anomaly_scores.csv (all), anomaly_top.csv (top 300 with class, Gaia id, Teff)."""
import os, glob, numpy as np, pandas as pd
H = os.path.dirname(os.path.abspath(__file__)); K = int(os.environ.get("K", 20))
g = np.load(os.path.join(H, "grid.npy"))
keep = (g > 3800) & (g < 8800)
for a, b in ((5570, 5585), (5740, 5820), (6295, 6305), (6860, 6960), (7500, 7640), (8280, 8330)): keep &= ~((g > a) & (g < b))
lam = g[keep]; nw = (lam > 4000) & (lam < 7000); sn_win = (g > 4500) & (g < 5500)
ids, FF, WW, snr = [], [], [], []
for fn in sorted(glob.glob(os.path.join(H, "chunks", "*.npz"))):
    d = np.load(fn)
    for t, f, iv in zip(d["targetid"], d["f"], d["iv"]):
        s = float(np.nanmedian(f[sn_win] * np.sqrt(iv[sn_win])))
        if not s >= 10: continue
        F = f[keep].astype(float); W = iv[keep].astype(float); med = np.nanmedian(F[nw])
        if not np.isfinite(med) or med <= 0: continue
        F = F / med; W = W * med**2; bad = ~np.isfinite(F) | (W <= 0); F[bad] = 0; W[bad] = 0
        W = np.where(W > 0, 1.0 / (1.0 / np.where(W > 0, W, 1) + (0.03 * np.clip(np.abs(F), 0.05, None))**2), 0)
        ids.append(int(t)); FF.append(F.astype(np.float32)); WW.append(W.astype(np.float32)); snr.append(s)
FF = np.array(FF); WW = np.array(WW); snr = np.array(snr); print(len(ids), "spectra with S/N >= 10", flush=True)
rng = np.random.default_rng(3); tr = rng.random(len(ids)) < 0.5
Ft = FF[tr].copy(); cm = np.median(np.where(WW[tr] > 0, Ft, np.nan), axis=0); cm = np.where(np.isfinite(cm), cm, 1.0)
Ft = np.where(WW[tr] > 0, Ft, cm); mu = Ft.mean(0); _, Sv, Vt = np.linalg.svd(Ft - mu, full_matrices=False); B = Vt[:K]
print("basis: variance explained", round(float((Sv[:K]**2).sum() / (Sv**2).sum()), 4), flush=True)
def fit(F, W):
    w = W.copy()
    for it in range(3):
        c = np.linalg.lstsq((B * w) @ B.T, (B * w) @ (F - mu), rcond=None)[0]; r = F - mu - c @ B
        hot = np.abs(r * np.sqrt(w)) > 5
        iso = hot & ~(np.roll(hot, 1) & np.roll(hot, -1)) & ~(np.roll(hot, 2) & np.roll(hot, 1) & np.roll(hot, -1))
        if not iso.any(): break
        w = np.where(iso, 0, w)
    return r, w
def windows(r, w, width):
    n = max(1, int(round(width / np.median(np.diff(lam))))); m = (w > 0).astype(float)
    cnt = np.convolve(m, np.ones(n), "same"); sm = np.convolve(np.where(w > 0, r, 0), np.ones(n), "same") / np.where(cnt > 0, cnt, 1)
    ev = np.sqrt(np.convolve(np.where(w > 0, 1 / np.where(w > 0, w, 1), 0), np.ones(n), "same")) / np.where(cnt > 0, cnt, 1)
    sm[cnt < 0.6 * n] = 0; sm[np.abs(lam - 6564.6) < 25] = 0; return sm, ev
rows = []; R = {}
for i in range(len(ids)):
    r, w = fit(FF[i], WW[i]); rec = dict(targetid=ids[i], snr=snr[i], chi2r=float((r[w > 0]**2 * w[w > 0]).sum() / max((w > 0).sum() - K, 1)))
    for width in (30, 80):
        sm, ev = windows(r, w, width); k = int(np.argmax(np.abs(sm)))
        rec[f"win{width}"] = float(sm[k]); rec[f"win{width}_c"] = float(lam[k]); rec[f"win{width}_sig"] = float(abs(sm[k]) / ev[k]) if ev[k] > 0 else 0
    rows.append(rec)
D = pd.DataFrame(rows)
for col in ("win30_sig", "win80_sig", "chi2r"):
    b = np.digitize(D.snr, [10, 15, 20, 30, 50, 80, 1e9]); z = np.zeros(len(D))
    for k in np.unique(b):
        m = b == k; v = np.log10(D.loc[m, col].clip(lower=1e-3)); med = v.median(); mad = 1.4826 * (v - med).abs().median(); z[m] = (v - med) / (mad or 1)
    D["z_" + col] = z
D["z_best"] = D[["z_win30_sig", "z_win80_sig"]].max(1); D["best_width"] = np.where(D.z_win30_sig >= D.z_win80_sig, 30, 80)
D["best_center"] = np.where(D.best_width == 30, D.win30_c, D.win80_c); D["best_res"] = np.where(D.best_width == 30, D.win30, D.win80)
C = pd.read_csv(os.path.join(H, "class_table.csv"), dtype=str); C.columns = [c.replace("#", "") for c in C.columns]; C["targetid"] = C.DESIID.astype(np.int64)
D = D.merge(C[["targetid", "Name", "edr3id", "CLASS", "Pwd", "G", "bp_rp", "MG", "Teff", "Log_g"]].drop_duplicates("targetid"), on="targetid", how="left")
D.to_csv(os.path.join(H, "anomaly_scores.csv"), index=False)
top = D.sort_values("z_best", ascending=False).head(300); top.to_csv(os.path.join(H, "anomaly_top.csv"), index=False)
sel = [ids.index(t) for t in top.targetid]
np.savez_compressed(os.path.join(H, "anomaly_top_spectra.npz"), targetid=np.array(top.targetid), lam=lam, F=FF[sel], W=WW[sel], mu=mu, B=B)
print("done", len(D), "scored; z_best > 8:", int((D.z_best > 8).sum()), flush=True)
