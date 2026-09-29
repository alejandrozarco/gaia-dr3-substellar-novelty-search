"""Blind spectral-anomaly search over the SDSS-V DR20 white-dwarf coadd store (2026-09-29).
Each coadd (4648 px, 3567-10399 A) is rebinned x2, restricted to 3700-9200 A, sky/telluric windows masked (5570-5585, 6295-6305,
6860-6960, 7590-7700, 8900-9200 A telluric/sky), and normalised by its median flux in 4000-7000 A. Objects with coadd S/N >= 8.
A weighted PCA basis (K components) is learned on a random training half; every object is reconstructed by a weighted least-squares
fit to that basis, and scored by (a) reduced chi^2 with a 3% systematic floor, (b) the largest |mean residual| in any 30-A window
(localised features), both expressed as robust z against objects of similar S/N. The top of each ranking is written out.
Output: scores.csv (sdss_id, gaia, cls, snr, chi2r, z_chi2, win_max, z_win, win_center), and residual arrays for the top 300."""
import os, glob, numpy as np, pandas as pd, time
S = os.path.expanduser("~/claude_projects/spectra_store/sdssv_dr20"); H = os.path.dirname(os.path.abspath(__file__)); K = int(os.environ.get("K", 12))
g = np.load(f"{S}/coadd_grid.npy"); gb = 0.5 * (g[0::2][:len(g)//2] + g[1::2][:len(g)//2])
T = pd.read_csv(f"{S}/targets.csv", dtype=str, low_memory=False).set_index("sdss_id")
keep = (gb > 3700) & (gb < 9200)
for a, b in ((5570, 5585), (6295, 6305), (6860, 6960), (7590, 7700)): keep &= ~((gb > a) & (gb < b))
lam = gb[keep]; norm_win = (lam > 4000) & (lam < 7000)
ids, F, W, snr = [], [], [], []; t0 = time.time()
for fpath in glob.glob(f"{S}/coadd_store/*/*.npz"):
    d = np.load(fpath); s = float(np.atleast_1d(d["snr"]).max())
    if s < 8: continue
    f = d["f"][: 2 * (len(g)//2)].reshape(-1, 2); iv = d["iv"][: 2 * (len(g)//2)].reshape(-1, 2)
    fb = np.where(iv.sum(1) > 0, (f * iv).sum(1) / np.where(iv.sum(1) > 0, iv.sum(1), 1), np.nan); ivb = iv.sum(1)
    fb, ivb = fb[keep], ivb[keep]
    med = np.nanmedian(fb[norm_win])
    if not np.isfinite(med) or med <= 0: continue
    ids.append(os.path.basename(fpath)[:-4]); F.append((fb / med).astype(np.float32)); W.append((ivb * med**2).astype(np.float32)); snr.append(s)
F = np.array(F); W = np.array(W); snr = np.array(snr); print(len(ids), "spectra loaded", f"{time.time()-t0:.0f}s", flush=True)
bad = ~np.isfinite(F) | (W <= 0); F[bad] = 0; W[bad] = 0
# systematic floor: effective weight 1/(1/w + (0.03 f)^2)
We = np.where(W > 0, 1.0 / (1.0 / np.where(W > 0, W, 1) + (0.03 * np.clip(np.abs(F), 0.05, None))**2), 0).astype(np.float32)
rng = np.random.default_rng(1); tr = rng.random(len(ids)) < 0.5
# training: fill masked pixels with the column median, then SVD on mean-subtracted spectra (weights ignored in the basis)
Ft = F[tr].copy(); colmed = np.median(np.where(W[tr] > 0, Ft, np.nan), axis=0); colmed = np.where(np.isfinite(colmed), colmed, 1.0)
Ft = np.where(W[tr] > 0, Ft, colmed); mu = Ft.mean(0); U, Sv, Vt = np.linalg.svd(Ft - mu, full_matrices=False); B = Vt[:K]
print("basis done; variance explained by", K, "components:", round(float((Sv[:K]**2).sum() / (Sv**2).sum()), 4), flush=True)
chi2r = np.zeros(len(ids)); winmax = np.zeros(len(ids)); wincen = np.zeros(len(ids)); R = np.zeros_like(F)
nw = max(1, int(round(30 / np.median(np.diff(lam)))))
for i in range(len(ids)):
    w = We[i]; x = F[i] - mu; A = (B * w).T; c = np.linalg.lstsq(A.T @ B.T if False else (B * w) @ B.T, (B * w) @ x, rcond=None)[0]
    r = x - c @ B; R[i] = r; m = w > 0
    chi2r[i] = float((r[m]**2 * w[m]).sum() / max(m.sum() - K, 1))
    rr = np.where(m, r, 0); cnt = np.convolve(m.astype(float), np.ones(nw), "same"); sm = np.convolve(rr, np.ones(nw), "same") / np.where(cnt > 0, cnt, 1)
    sm[cnt < 0.6 * nw] = 0; k = int(np.argmax(np.abs(sm))); winmax[i] = sm[k]; wincen[i] = lam[k]
def rz(v, s, bins=np.array([8, 12, 18, 25, 35, 50, 80, 1e9])):
    out = np.full(len(v), np.nan); b = np.digitize(s, bins)
    for k in np.unique(b):
        m = b == k; med = np.median(v[m]); mad = 1.4826 * np.median(np.abs(v[m] - med)); out[m] = (v[m] - med) / (mad if mad > 0 else 1)
    return out
D = pd.DataFrame(dict(sdss_id=ids, snr=snr, chi2r=chi2r, win_max=winmax, win_center=wincen))
D["gaia"] = T.gaia_dr3_source_id.reindex(D.sdss_id).values; D["cls"] = T.classification.reindex(D.sdss_id).values
D["G"] = pd.to_numeric(T.g_mag.reindex(D.sdss_id).values, errors="coerce"); D["bprp"] = pd.to_numeric(T.bprp.reindex(D.sdss_id).values, errors="coerce"); D["MG"] = pd.to_numeric(T.MG.reindex(D.sdss_id).values, errors="coerce")
D["z_chi2"] = rz(np.log10(D.chi2r.values), D.snr.values); D["z_win"] = rz(np.abs(D.win_max.values), D.snr.values)
D.to_csv(os.path.join(H, "scores.csv"), index=False)
top = D.sort_values("z_chi2", ascending=False).head(300).index.union(D.sort_values("z_win", ascending=False).head(300).index)
np.savez_compressed(os.path.join(H, "top_residuals.npz"), idx=np.array(top), ids=np.array(ids)[top], lam=lam, F=F[top], R=R[top], mu=mu)
print("done", len(D), "scored;", "z_chi2>10:", int((D.z_chi2 > 10).sum()), " z_win>10:", int((D.z_win > 10).sum()), flush=True)
