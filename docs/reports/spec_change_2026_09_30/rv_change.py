"""SUPERSEDED by rv_fit.py (linear interpolation of the shifted spectrum biases the velocity by up to ~half a pixel); outputs not kept.
Cross-epoch radial-velocity change (v2: free linear tilt per trial velocity, narrower cores, H-gamma added) of white-dwarf Balmer cores (2026-09-30).
Pairs: every two spectra with S/N >= 8 of the same Gaia DR3 source in the SDSS/BOSS DR17 and DESI DR1 white-dwarf stores
(as spec_change.py). Native wavelength grids (SDSS log grid 69 km/s per pixel; DESI 1.6 A).
Per line (H-alpha 6562.8, H-beta 4861.3 A, air -> vacuum: 6564.6, 4862.7 A): a local linear continuum from the medians of
[-70,-45] and [+45,+70] A normalises the spectrum; the core window is +-28 A (H-alpha) and +-20 A (H-beta). A line is usable in a
spectrum when the core depth (1 - min of 5-pixel smoothed flux) exceeds 5 times its noise.
Shift: b (the lower-S/N spectrum) is shifted by v on a grid of -900..900 km/s (5 km/s steps), interpolated onto a's pixels,
and chi^2 = sum((a - b_v)^2 / (sa^2 + sb_v^2)) over the core window; the minimum is refined by a parabola; sigma_v from
delta chi^2 = 1 after scaling chi^2 by its reduced value (if > 1). dv = v(a) - v(b) ... reported as v_shift (b must be shifted by
v to match a, so the star's velocity in a minus that in b is +v).
SDSS vs DESI zero-point: the median shift over all SDSS-DESI pairs is reported and subtracted for those pairs.
Output: results/rv_pairs.csv."""
import os, glob, numpy as np, pandas as pd
H = os.path.dirname(os.path.abspath(__file__)); ST = os.path.expanduser("~/claude_projects/spectra_store"); OUT = os.path.join(H, "results")
C = 299792.458; LINES = {"Ha": (6564.61, 18), "Hb": (4862.68, 14), "Hg": (4341.69, 12)}
gs = np.load(os.path.join(ST, "sdss_dr17_wd", "grid.npy")); gd = np.load(os.path.join(ST, "desi_dr1_wd", "grid.npy"))
M = pd.read_csv(os.path.join(ST, "sdss_dr17_wd", "matches.csv"), dtype={"gaia": str}).drop_duplicates("sparcl_id")
Ct = pd.read_csv(os.path.join(ST, "desi_dr1_wd", "class_table.csv"), dtype={"edr3id": str}); d2g = dict(zip(Ct.DESIID.astype(np.int64), Ct.edr3id))
cnt = pd.concat([M.gaia, Ct.edr3id]).value_counts(); multi = set(cnt[cnt >= 2].index)
def cut(g, f, iv):
    out = {}
    for k, (l0, hw) in LINES.items():
        m = (g > l0 - 75) & (g < l0 + 75)
        w, F, I = g[m], f[m].astype(float), np.clip(iv[m].astype(float), 0, None)
        c1 = (w > l0 - 70) & (w < l0 - 45) & (I > 0); c2 = (w > l0 + 45) & (w < l0 + 70) & (I > 0)
        if c1.sum() < 5 or c2.sum() < 5: continue
        y1, y2 = np.median(F[c1]), np.median(F[c2]); x1, x2 = np.median(w[c1]), np.median(w[c2])
        cont = y1 + (y2 - y1) * (w - x1) / (x2 - x1)
        if not (np.all(cont > 0)): continue
        n = F / cont; s = np.where(I > 0, 1 / np.sqrt(np.where(I > 0, I, 1)) / cont, np.inf); core = np.abs(w - l0) < hw
        sm = np.convolve(n, np.ones(5) / 5, "same"); good = core & np.isfinite(s)
        if good.sum() < 10: continue
        depth = 1 - np.min(sm[good]); noise = np.median(s[good]) / np.sqrt(5)
        if depth > 5 * noise: out[k] = (w, n, s, core)
    return out
spec = {}
for fn in sorted(glob.glob(os.path.join(ST, "sdss_dr17_wd", "chunks", "*.npz"))):
    d = np.load(fn, allow_pickle=True)
    for s_, gg, f, iv in zip(d["sparcl_id"], d["gaia"], d["f"], d["iv"]):
        gg = str(gg)
        if gg not in multi or any(x[0] == "S:" + str(s_) for x in spec.get(gg, [])): continue
        sw = (gs > 4500) & (gs < 5500); sn = float(np.nanmedian(f[sw] * np.sqrt(np.clip(iv[sw], 0, None))))
        if not sn >= 8: continue
        L = cut(gs, f, iv)
        if L: spec.setdefault(gg, []).append(("S:" + str(s_), sn, L))
for fn in sorted(glob.glob(os.path.join(ST, "desi_dr1_wd", "chunks", "*.npz"))):
    d = np.load(fn, allow_pickle=True)
    for t, f, iv in zip(d["targetid"], d["f"], d["iv"]):
        gg = d2g.get(int(t))
        if gg is None or gg not in multi: continue
        sw = (gd > 4500) & (gd < 5500); sn = float(np.nanmedian(f[sw] * np.sqrt(np.clip(iv[sw], 0, None))))
        if not sn >= 8: continue
        L = cut(gd, f, iv)
        if L: spec.setdefault(gg, []).append(("D:" + str(int(t)), sn, L))
vg = np.arange(-900, 901, 5.0)
def shift(A, B):
    # for each trial v: a = (p0 + p1*(w - l0)) * b_v, (p0, p1) by weighted least squares, so continuum tilts between epochs cancel
    wa, na, sa, core = A; wb, nb, sb, _ = B; ok = core & np.isfinite(sa); chi = np.full(len(vg), np.nan); npx = ok.sum()
    fin = np.isfinite(sb); x = wa[ok] - wa[ok].mean(); y = na[ok]
    for i, v in enumerate(vg):
        wbs = wb * (1 + v / C); bi = np.interp(wa[ok], wbs[fin], nb[fin]); si = np.interp(wa[ok], wbs[fin], sb[fin])
        w = 1 / (sa[ok]**2 + si**2); X = np.vstack([bi, bi * x]).T; A_ = X.T @ (X * w[:, None]); p = np.linalg.solve(A_, X.T @ (w * y))
        chi[i] = np.sum(w * (y - X @ p)**2)
    j = int(np.nanargmin(chi))
    if j in (0, len(vg) - 1): return np.nan, np.nan, np.nan
    y0, y1, y2 = chi[j - 1], chi[j], chi[j + 1]; den = y0 - 2 * y1 + y2
    if den <= 0: return np.nan, np.nan, np.nan
    v = vg[j] + 5 * 0.5 * (y0 - y2) / den; red = max(1.0, y1 / max(npx - 3, 1)); sig = np.sqrt(2 * 25 / den * red)
    return v, sig, y1 / max(npx - 3, 1)
rows = []
for gg, v in spec.items():
    for i in range(len(v)):
        for j in range(i + 1, len(v)):
            A, B = (v[i], v[j]) if v[i][1] >= v[j][1] else (v[j], v[i]); r = dict(gaia=gg, a=A[0], b=B[0], sn_a=A[1], sn_b=B[1])
            for k in LINES:
                if k in A[2] and k in B[2]: r[f"v_{k}"], r[f"e_{k}"], r[f"chi_{k}"] = shift(A[2][k], B[2][k])
            rows.append(r)
P = pd.DataFrame(rows); P["kind"] = P.a.str[0] + P.b.str[0]
for k in LINES:
    mix = P.kind.isin(["SD", "DS"]); zp = {}
    for kd in ("SD", "DS", "SS", "DD"): zp[kd] = float(np.nanmedian(P.loc[P.kind == kd, f"v_{k}"]))
    print(k, "median shift by pair kind (km/s):", {a: round(b, 1) for a, b in zp.items()}, flush=True)
    P[f"vc_{k}"] = P[f"v_{k}"] - P.kind.map(zp)
for k in LINES: P[f"z_{k}"] = P[f"vc_{k}"] / P[f"e_{k}"]
P.to_csv(os.path.join(OUT, "rv_pairs_v2.csv"), index=False); print(len(P), "pairs;", P.v_Ha.notna().sum(), "with H-alpha,", P.v_Hb.notna().sum(), "with H-beta", flush=True)
both = P.dropna(subset=["vc_Ha", "vc_Hb"])
print("pairs with both lines:", len(both), "; |z|>5 in both lines with the same sign:", int(((both.z_Ha.abs() > 5) & (both.z_Hb.abs() > 5) & (np.sign(both.vc_Ha) == np.sign(both.vc_Hb))).sum()), flush=True)
