"""Multi-epoch spectral-change search for white dwarfs (2026-09-30).
Input: the SDSS/BOSS DR17 white-dwarf store (~/claude_projects/spectra_store/sdss_dr17_wd; 42,178 unique spectra of 31,975 GF21 white
dwarfs) and the DESI DR1 white-dwarf class-table store (~/claude_projects/spectra_store/desi_dr1_wd; 44,417 coadds). Every star with
two or more spectra (SDSS repeats, SDSS vs DESI, several DESI target ids) gives pairs; every pair of spectra with S/N >= 8
(median f*sqrt(ivar), 4500-5500 A) is compared.
Per spectrum: positive isolated spikes (> 6 sigma above a 9-pixel running median) are masked, then the spectrum is rebinned
(inverse-variance weighted) onto a common 4-A grid over 3850-8800 A. Masked: 5570-5585 (sky), 5740-6100 (DESI camera join and SDSS
dichroic), 6295-6305 (sky), 6860-6960 and 7590-7700 (telluric), 7500-7640 (DESI camera join), 8280-8330 A.
Per pair (a = higher S/N): the flux ratio a/b is fitted with a degree-7 Legendre polynomial in wavelength (weighted, 3 iterations
of 4-sigma clipping), so that flux-calibration differences cancel; diff = a - r*b with sigma^2 = 1/iv_a + r^2/iv_b +
(0.02 a)^2. The mean diff in sliding windows of 32 A and 80 A (step = half width) gives z per window. Because some windows are
systematically noisy (calibration edges, sky residuals), z is divided by the robust scatter (1.4826 MAD) of that window's z over
all pairs. Score = max |z_norm|; the window and sign are kept.
Output: results/pairs.csv (all pairs), results/top.csv (top 300), results/top_spectra.npz (binned spectra of the top 300; not kept in the repository)."""
import os, glob, numpy as np, pandas as pd
from scipy.ndimage import median_filter
from numpy.polynomial import legendre as L
H = os.path.dirname(os.path.abspath(__file__)); ST = os.path.expanduser("~/claude_projects/spectra_store"); OUT = os.path.join(H, "results")
edges = np.arange(3850, 8804, 4.0); cen = 0.5 * (edges[1:] + edges[:-1]); nb = len(cen)
mask = np.ones(nb, bool)
for a, b in ((5570, 5585), (5740, 6100), (6295, 6305), (6860, 6960), (7590, 7700), (7500, 7640), (8280, 8330)): mask &= ~((cen > a) & (cen < b))
def binner(g):
    i = np.digitize(g, edges) - 1; ok = (i >= 0) & (i < nb); return i, ok
gs = np.load(os.path.join(ST, "sdss_dr17_wd", "grid.npy")); gd = np.load(os.path.join(ST, "desi_dr1_wd", "grid.npy"))
BS, BD = binner(gs), binner(gd); snS = (gs > 4500) & (gs < 5500); snD = (gd > 4500) & (gd < 5500)
def prep(f, iv, B, snw):
    f = np.asarray(f, float); iv = np.clip(np.asarray(iv, float), 0, None); iv[~np.isfinite(f)] = 0; f = np.where(np.isfinite(f), f, 0)
    sn = float(np.nanmedian(f[snw] * np.sqrt(iv[snw])))
    if not sn >= 8: return None
    m = median_filter(f, 9); sp = (f - m) * np.sqrt(iv) > 6; iv[sp] = 0
    i, ok = B; w = np.bincount(i[ok], iv[ok], nb); s = np.bincount(i[ok], (f * iv)[ok], nb)
    F = np.where(w > 0, s / np.where(w > 0, w, 1), 0); W = np.where(mask, w, 0); return F.astype(np.float32), W.astype(np.float32), sn
# --- which stars have >= 2 spectra
M = pd.read_csv(os.path.join(ST, "sdss_dr17_wd", "matches.csv"), dtype={"gaia": str}).drop_duplicates("sparcl_id")
C = pd.read_csv(os.path.join(ST, "desi_dr1_wd", "class_table.csv"), dtype={"edr3id": str})
d2g = dict(zip(C.DESIID.astype(np.int64), C.edr3id)); cls = dict(zip(C.edr3id, C.CLASS))
cnt = pd.concat([M.gaia, C.edr3id]).value_counts(); multi = set(cnt[cnt >= 2].index); print("stars with >= 2 spectra:", len(multi), flush=True)
spec = {}   # gaia -> list of (label, F, W, sn)
for fn in sorted(glob.glob(os.path.join(ST, "sdss_dr17_wd", "chunks", "*.npz"))):
    d = np.load(fn, allow_pickle=True)
    for s_, gg, f, iv in zip(d["sparcl_id"], d["gaia"], d["f"], d["iv"]):
        gg = str(gg)
        if gg not in multi or any(x[0] == "S:" + str(s_) for x in spec.get(gg, [])): continue
        r = prep(f, iv, BS, snS)
        if r: spec.setdefault(gg, []).append(("S:" + str(s_),) + r)
for fn in sorted(glob.glob(os.path.join(ST, "desi_dr1_wd", "chunks", "*.npz"))):
    d = np.load(fn, allow_pickle=True)
    for t, f, iv in zip(d["targetid"], d["f"], d["iv"]):
        gg = d2g.get(int(t))
        if gg is None or gg not in multi: continue
        r = prep(f, iv, BD, snD)
        if r: spec.setdefault(gg, []).append(("D:" + str(int(t)),) + r)
print("stars with >= 2 usable spectra:", sum(len(v) >= 2 for v in spec.values()), flush=True)
x = (cen - cen.mean()) / (cen.max() - cen.mean())
def wins(width):
    st = np.arange(cen[0], cen[-1] - width, width / 2); return [(a, a + width) for a in st]
WIN = wins(32) + wins(80); WI = [np.where((cen >= a) & (cen < b))[0] for a, b in WIN]
rows, Z = [], []
for gg, v in spec.items():
    if len(v) < 2: continue
    for i in range(len(v)):
        for j in range(i + 1, len(v)):
            A, B_ = (v[i], v[j]) if v[i][3] >= v[j][3] else (v[j], v[i])
            Fa, Wa, Fb, Wb = A[1], A[2], B_[1], B_[2]; ok = (Wa > 0) & (Wb > 0) & (Fb > 0.02 * np.median(Fb[Wb > 0]))
            if ok.sum() < 300: continue
            rat = Fa / np.where(Fb != 0, Fb, 1); wr = 1 / (1 / Wa + rat**2 / Wb) * Fb**2; use = ok.copy()
            for it in range(3):
                c = L.legfit(x[use], rat[use], 7, w=np.sqrt(wr[use])); r = L.legval(x, c); res = (rat - r) * np.sqrt(wr)
                use = ok & (np.abs(res) < 4 * max(1.0, 1.4826 * np.median(np.abs(res[ok]))))
            diff = Fa - r * Fb; var = 1 / np.where(Wa > 0, Wa, np.inf) + r**2 / np.where(Wb > 0, Wb, np.inf) + (0.02 * Fa)**2
            z = np.full(len(WI), np.nan); med = np.median(np.abs(Fa[ok]))
            for k, ii in enumerate(WI):
                ii = ii[ok[ii]]
                if len(ii) >= 4: z[k] = diff[ii].sum() / np.sqrt(var[ii].sum())
            rows.append(dict(gaia=gg, a=A[0], b=B_[0], sn_a=A[3], sn_b=B_[3], cls=cls.get(gg, ""))); Z.append(z.astype(np.float32))
Z = np.array(Z); scale = 1.4826 * np.nanmedian(np.abs(Z - np.nanmedian(Z, 0)), 0); Zn = Z / scale
P = pd.DataFrame(rows); k = np.nanargmax(np.abs(np.nan_to_num(Zn)), 1)
P["score"] = np.abs(Zn[np.arange(len(P)), k]); P["sign"] = np.sign(Zn[np.arange(len(P)), k]); P["win_lo"] = [WIN[i][0] for i in k]; P["win_hi"] = [WIN[i][1] for i in k]
P["n_win_gt5"] = (np.abs(np.nan_to_num(Zn)) > 5).sum(1)
P = P.sort_values("score", ascending=False); P.to_csv(os.path.join(OUT, "pairs.csv"), index=False)
T = P.head(300); T.to_csv(os.path.join(OUT, "top.csv"), index=False); print(len(P), "pairs;", (P.score > 8).sum(), "with score > 8", flush=True)
sv = {}
for n, r in enumerate(T.itertuples()):
    v = {x[0]: x for x in spec[r.gaia]}; sv[f"a{n}"] = np.vstack([v[r.a][1], v[r.a][2]]); sv[f"b{n}"] = np.vstack([v[r.b][1], v[r.b][2]])
np.savez_compressed(os.path.join(OUT, "top_spectra.npz"), cen=cen, **sv); print("done", flush=True)
