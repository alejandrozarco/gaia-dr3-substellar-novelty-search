"""Blind spectral-anomaly search over the SDSS/BOSS DR17 white-dwarf store (2026-09-29); same method as the DESI and SDSS-V
searches. Spectra with S/N >= 10 (median f*sqrt(ivar), 4500-5500 A); range 3850-8800 A; sky lines, telluric bands and the
spectrograph dichroic region (5800-6100 A) masked; normalised by the median flux in 4000-7000 A; 3% systematic floor.
Weighted PCA basis (K=20) from a random training half of the specprimary spectra; isolated-spike masking; the most significant
mean residual in 30-A and 80-A windows (H-alpha +-25 A excluded), as a robust z within S/N bins.
Persistence: for white dwarfs with more than one spectrum, the residual in the same window is measured in every spectrum of
that star (S/N >= 5); 'persistent' = at least 2 spectra with |res|/err > 3 and the same sign.
Output: anomaly_scores.csv, anomaly_top.csv (top 400 with class and persistence), anomaly_top_spectra.npz."""
import os, glob, numpy as np, pandas as pd
H = os.path.dirname(os.path.abspath(__file__)); K = int(os.environ.get("K", 20))
g = np.load(os.path.join(H, "grid.npy"))
keep = (g > 3850) & (g < 8800)
for a, b in ((5570, 5585), (5800, 6100), (6295, 6305), (6860, 6960), (7590, 7700), (8280, 8330)): keep &= ~((g > a) & (g < b))
lam = g[keep]; nw = (lam > 4000) & (lam < 7000); sn_win = (g > 4500) & (g < 5500)
def prep(f, iv):
    F = f[keep].astype(float); W = iv[keep].astype(float); med = np.nanmedian(F[nw])
    if not np.isfinite(med) or med <= 0: return None, None
    F = F / med; W = W * med**2; bad = ~np.isfinite(F) | (W <= 0); F[bad] = 0; W[bad] = 0
    W = np.where(W > 0, 1.0 / (1.0 / np.where(W > 0, W, 1) + (0.03 * np.clip(np.abs(F), 0.05, None))**2), 0); return F, W
X = pd.read_csv(os.path.join(H, "matches.csv"), dtype={"gaia": str}).drop_duplicates("sparcl_id").set_index("sparcl_id")  # the GF21 table has one row per spectrum, so matches repeat
sid, gai, FF, WW, snr = [], [], [], [], []; seen = set()
for fn in sorted(glob.glob(os.path.join(H, "chunks", "*.npz"))):
    d = np.load(fn)
    for s_, gg, f, iv in zip(d["sparcl_id"], d["gaia"], d["f"], d["iv"]):
        if s_ in seen: continue
        seen.add(s_)
        s = float(np.nanmedian(f[sn_win] * np.sqrt(np.clip(iv[sn_win], 0, None))))
        if not s >= 5: continue
        F, W = prep(f, iv)
        if F is None: continue
        sid.append(str(s_)); gai.append(str(gg)); FF.append(F.astype(np.float32)); WW.append(W.astype(np.float32)); snr.append(s)
FF = np.array(FF); WW = np.array(WW); snr = np.array(snr); sid = np.array(sid); gai = np.array(gai)
prim = np.array([bool(X.prim.get(s, True)) for s in sid]); print(len(sid), "spectra with S/N >= 5;", int((snr >= 10).sum()), "with S/N >= 10", flush=True)
rng = np.random.default_rng(4); tr = (rng.random(len(sid)) < 0.5) & prim & (snr >= 10)
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
rows = []; main = np.where((snr >= 10) & prim)[0]
for i in main:
    r, w = fit(FF[i], WW[i]); rec = dict(sparcl_id=sid[i], gaia=gai[i], snr=snr[i])
    for width in (30, 80):
        sm, ev = windows(r, w, width); k = int(np.argmax(np.abs(sm)))
        rec[f"win{width}"] = float(sm[k]); rec[f"win{width}_c"] = float(lam[k]); rec[f"win{width}_sig"] = float(abs(sm[k]) / ev[k]) if ev[k] > 0 else 0
    rows.append(rec)
D = pd.DataFrame(rows)
for col in ("win30_sig", "win80_sig"):
    b = np.digitize(D.snr, [10, 15, 20, 30, 50, 80, 1e9]); z = np.zeros(len(D))
    for k in np.unique(b):
        m = b == k; v = np.log10(D.loc[m, col].clip(lower=1e-3)); med = v.median(); mad = 1.4826 * (v - med).abs().median(); z[m] = (v - med) / (mad or 1)
    D["z_" + col] = z
D["z_best"] = D[["z_win30_sig", "z_win80_sig"]].max(1); D["best_width"] = np.where(D.z_win30_sig >= D.z_win80_sig, 30, 80)
D["best_center"] = np.where(D.best_width == 30, D.win30_c, D.win80_c); D["best_res"] = np.where(D.best_width == 30, D.win30, D.win80)
W_ = pd.read_csv(os.path.join(H, "gf21_sdssspec.csv"), dtype={"GaiaEDR3": str}).drop_duplicates("GaiaEDR3").set_index("GaiaEDR3")
for col in ("WDJname", "specClass", "Sp", "Gmag", "TeffH", "loggH", "MassH", "Pwd"): D[col] = W_[col].reindex(D.gaia).values
D.to_csv(os.path.join(H, "anomaly_scores.csv"), index=False)
top = D.sort_values("z_best", ascending=False).head(400).copy(); pers = []
for _, t in top.iterrows():
    idx = np.where((gai == t.gaia) & (sid != t.sparcl_id))[0]; res = []
    for j in idx:
        r, w = fit(FF[j], WW[j]); sm, ev = windows(r, w, int(t.best_width)); k = int(np.argmin(np.abs(lam - t.best_center)))
        if ev[k] > 0: res.append((float(sm[k]), float(ev[k])))
    agree = sum(1 for a, e in res if abs(a) / e > 3 and np.sign(a) == np.sign(t.best_res))
    pers.append(dict(n_other=len(res), n_agree=agree, verdict="single spectrum" if not res else ("persistent" if agree >= 1 else "not persistent"),
                     others="; ".join(f"{a:+.3f}+-{e:.3f}" for a, e in res)))
top = pd.concat([top.reset_index(drop=True), pd.DataFrame(pers)], axis=1); top.to_csv(os.path.join(H, "anomaly_top.csv"), index=False)
sel = [int(np.where(sid == s)[0][0]) for s in top.sparcl_id]
np.savez_compressed(os.path.join(H, "anomaly_top_spectra.npz"), sparcl_id=np.array(top.sparcl_id), lam=lam, F=FF[sel], W=WW[sel], mu=mu, B=B)
print("done", len(D), "scored;", top.verdict.value_counts().to_dict(), flush=True)
