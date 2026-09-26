"""Lane 4: the weirdest SDSS-V white-dwarf spectra. Coadds stored in lane_gasdisc/store (regions 3880-4000, 4780-4940, 4990-5200,
5820-5940, 6400-6750, 7740-7810, 8250-8950 A on the 6e-5 dex grid). Each region divided by its median; spectra with median
per-pixel S/N > 8 kept. PCA (40 components, fitted on the filled normalised spectra) and 30 nearest neighbours in PCA space.
Uniqueness = the smallest reduced chi2 against the 10 nearest neighbours, over all pixels, with the combined variance of both spectra
(chi2 = sum (x - y)^2 / (sx^2 + sy^2), each neighbour scaled per region by a weighted least-squares factor). The region that contributes
most to that chi2 is recorded. Output weird.csv (all kept spectra) sorted by uniqueness."""
import os, glob, numpy as np, pandas as pd
from sklearn.decomposition import PCA
from scipy.spatial import cKDTree
REG = ["3880", "4780", "4990", "5820", "6400", "7740", "8250"]
if not os.path.exists("coadd_F.npy"):
    files = sorted(glob.glob("/tmp/hotdq/lane_gasdisc/store/*/*.npz")); ids, F, IV = [], [], []
    for k, fn in enumerate(files):
        d = np.load(fn); ids.append(os.path.basename(fn)[:-4])
        F.append(np.concatenate([d[f"f_{r}"] for r in REG])); IV.append(np.concatenate([d[f"iv_{r}"] for r in REG]))
        if k % 10000 == 0: print("load", k, flush=True)
    np.save("coadd_F.npy", np.array(F, np.float32)); np.save("coadd_IV.npy", np.array(IV, np.float32)); pd.Series(ids).to_csv("coadd_ids.csv", index=False)
F = np.load("coadd_F.npy").astype(np.float64); IV = np.load("coadd_IV.npy").astype(np.float64); ids = pd.read_csv("coadd_ids.csv", dtype=str).iloc[:, 0].values
d0 = np.load(glob.glob("/tmp/hotdq/lane_gasdisc/store/*/*.npz")[0]); lens = [len(d0[f"f_{r}"]) for r in REG]; edges = np.r_[0, np.cumsum(lens)]
ok = np.isfinite(F) & (IV > 0); F = np.where(ok, F, np.nan); IV = np.where(ok, IV, 0)
for a, b in zip(edges[:-1], edges[1:]):
    med = np.nanmedian(F[:, a:b], axis=1); med = np.where(med > 0, med, np.nan)
    F[:, a:b] /= med[:, None]; IV[:, a:b] *= med[:, None] ** 2
snr = np.nanmedian(np.where(IV > 0, np.sqrt(IV) * np.abs(F), np.nan), axis=1)
keep = np.isfinite(snr) & (snr > 8) & (np.mean(IV > 0, axis=1) > 0.8); print("kept", keep.sum(), "of", len(ids), flush=True)
F, IV, ids, snr = F[keep], IV[keep], ids[keep], snr[keep]
from scipy.ndimage import median_filter
for a, b in zip(edges[:-1], edges[1:]):
    blk = np.where(np.isfinite(F[:, a:b]) & (IV[:, a:b] > 0), F[:, a:b], np.nan); fill = np.where(np.isnan(blk), np.nanmedian(blk, axis=1)[:, None], blk)
    F[:, a:b] = np.where(np.isnan(blk), np.nan, median_filter(fill, size=(1, 5)))
Ff = np.where(np.isfinite(F) & (IV > 0), F, 1.0); Ff = np.clip(Ff, -1, 5)
Z = PCA(40, random_state=1).fit_transform(Ff); tree = cKDTree(Z); _, NB = tree.query(Z, k=31)
var = np.where(IV > 0, 1 / np.where(IV > 0, IV, 1), np.inf)
best = np.zeros(len(ids)); breg = np.empty(len(ids), object); bnb = np.empty(len(ids), object)
for i in range(len(ids)):
    x, vx = F[i], var[i]; res = []
    for j in NB[i, 1:11]:
        y, vy = F[j].copy(), var[j]; m = np.isfinite(x) & np.isfinite(y) & np.isfinite(vx) & np.isfinite(vy)
        chi_parts = []
        for a, b in zip(edges[:-1], edges[1:]):
            mm = m[a:b]
            if mm.sum() < 10: chi_parts.append((0.0, 0)); continue
            xa, ya, va = x[a:b][mm], y[a:b][mm], (vx[a:b] + vy[a:b])[mm]
            s = np.sum(xa * ya / va) / np.sum(ya * ya / va); rr = np.clip(np.abs(xa - s * ya) / np.sqrt(va), 0, 4); chi_parts.append((float(np.sum(rr ** 2)), int(mm.sum())))
        tot = sum(c for c, _ in chi_parts) / max(sum(n for _, n in chi_parts), 1)
        res.append((tot, j, max(range(len(REG)), key=lambda q: chi_parts[q][0])))
    t, j, q = min(res); best[i] = t; breg[i] = REG[q]; bnb[i] = ids[j]
    if i % 5000 == 0: print("score", i, flush=True)
sw = pd.read_csv("/tmp/hotdq/lane_gasdisc/sw_all.csv", dtype=str).drop_duplicates("sdss_id").set_index("sdss_id")
out = pd.DataFrame(dict(sdss_id=ids, snr=np.round(snr, 1), uniqueness=np.round(best, 2), worst_region=breg, nearest=bnb))
out["gaia"] = out.sdss_id.map(sw.gaia_dr3_source_id); out["cls"] = out.sdss_id.map(sw.classification); out["G"] = out.sdss_id.map(sw.g_mag)
out.sort_values("uniqueness", ascending=False).to_csv("weird_rob.csv", index=False); print("DONE", flush=True)
