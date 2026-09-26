"""Lanes 1+2 on the stored SDSS-V visits (lane_gasdisc/store, 6400-6750 A per visit, XCSAO shift removed for in_stack visits):
per visit, (a) H-alpha velocity relative to the star's own coadd: both normalised by a line through 6405-6440 and 6700-6745 A,
chi2 of visit vs shifted coadd over |v| < 1500 km/s from H-alpha, shifts -600..+600 km/s in 5 km/s steps, parabola refinement,
error from delta chi2 = 1 (chi2 scaled to dof if > 1); (b) equivalent widths of H-alpha (|v| < 1500 km/s) and He I 6679.99
(|v| < 900 km/s) on the same normalisation. Visits with S/N < 5 (stored vsnr) skipped; stars with >= 2 usable visits.
Output visit_rv.csv (one row per visit) and star_rv.csv (per star: n, weighted-mean RV, chi2 of constant RV, max |dRV| and its
significance, chi2 of constant H-alpha and He I EWs)."""
import os, glob, numpy as np, pandas as pd
C = 299792.458; GRID = 10 ** np.arange(np.log10(3850), np.log10(9250), 6e-5); W = GRID[(GRID > 6400) & (GRID < 6750)]
HA, HE = 6564.61, 6679.99
cont = ((W > 6405) & (W < 6440)) | ((W > 6700) & (W < 6745))
vha = (W / HA - 1) * C; core = np.abs(vha) < 1500; he = np.abs((W / HE - 1) * C) < 900
dl = np.gradient(W); shifts = np.arange(-600, 601, 5.0)
sw = pd.read_csv("/tmp/hotdq/lane_gasdisc/sw_all.csv", dtype=str).drop_duplicates("sdss_id").set_index("sdss_id")
def norm(f, iv):
    ok = (iv > 0) & np.isfinite(f); m = ok & cont
    if m.sum() < 20: return None
    p = np.polyfit(W[m], f[m], 1, w=np.sqrt(iv[m])); c = np.polyval(p, W)
    if np.median(c[m]) <= 0: return None
    return np.where(ok, f / c, np.nan), np.where(ok, iv * c ** 2, 0.0)
vrows, srows = [], []
files = sorted(glob.glob("/tmp/hotdq/lane_gasdisc/store/*/*.npz"))
for k, fn in enumerate(files):
    sid = os.path.basename(fn)[:-4]; d = np.load(fn)
    if d["vf_6400"].shape[0] < 2: continue
    cn = norm(d["f_6400"].astype(float), d["iv_6400"].astype(float))
    if cn is None: continue
    tn, tiv = cn; tn = np.nan_to_num(tn, nan=1.0)
    rv = []
    for j in range(d["vf_6400"].shape[0]):
        if d["vsnr"][j] < 5: continue
        vn = norm(d["vf_6400"][j].astype(float), d["viv_6400"][j].astype(float))
        if vn is None: continue
        n, iv = vn; m = core & (iv > 0) & np.isfinite(n)
        if m.sum() < 50: continue
        chi = np.array([np.sum((n[m] - np.interp(W[m], W * (1 + s / C), tn)) ** 2 * iv[m]) for s in shifts])
        i = int(np.argmin(chi)); dof = m.sum() - 1; sc = max(chi[i] / dof, 1.0)
        if 0 < i < len(shifts) - 1:
            a, b, c_ = np.polyfit(shifts[i - 1:i + 2], chi[i - 1:i + 2], 2); best = -b / (2 * a) if a > 0 else shifts[i]; e = np.sqrt(sc / a) if a > 0 else np.nan
        else:
            best, e = shifts[i], np.nan
        ok = (iv > 0) & np.isfinite(n)
        ew_ha = float(np.sum(((1 - n) * dl)[core & ok])); e_ha = float(np.sqrt(np.sum((dl ** 2 / iv)[core & ok & (iv > 0)])))
        ew_he = float(np.sum(((1 - n) * dl)[he & ok])); e_he = float(np.sqrt(np.sum((dl ** 2 / iv)[he & ok & (iv > 0)])))
        rv.append((int(d["mjd"][j]), float(d["vsnr"][j]), best, e, chi[i] / dof, ew_ha, e_ha, ew_he, e_he))
        vrows.append(dict(sdss_id=sid, mjd=int(d["mjd"][j]), vsnr=round(float(d["vsnr"][j]), 1), rv=round(best, 1), e_rv=round(e, 1) if np.isfinite(e) else np.nan,
                          chi2r=round(chi[i] / dof, 2), ew_ha=round(ew_ha, 2), e_ew_ha=round(e_ha, 2), ew_he=round(ew_he, 2), e_ew_he=round(e_he, 2)))
    if len(rv) < 2: continue
    r = np.array(rv, float); ok = np.isfinite(r[:, 3]) & (r[:, 3] > 0)
    out = dict(sdss_id=sid, gaia=sw.loc[sid, "gaia_dr3_source_id"] if sid in sw.index else "", cls=sw.loc[sid, "classification"] if sid in sw.index else "", n=len(r))
    if ok.sum() >= 2:
        v, e = r[ok, 2], r[ok, 3]; w = 1 / e ** 2; mu = np.sum(w * v) / np.sum(w); chi2 = float(np.sum(w * (v - mu) ** 2))
        ii, jj = np.argmax(v), np.argmin(v)
        out.update(n_rv=int(ok.sum()), rv_mean=round(mu, 1), rv_chi2=round(chi2, 1), drv_max=round(v[ii] - v[jj], 1), drv_sig=round((v[ii] - v[jj]) / np.hypot(e[ii], e[jj]), 1), med_erv=round(float(np.median(e)), 1))
    for key, col, ecol in (("ha", 5, 6), ("he", 7, 8)):
        x, ex = r[:, col], r[:, ecol]; g = ex > 0
        if g.sum() >= 2:
            ww = 1 / ex[g] ** 2; mu = np.sum(ww * x[g]) / np.sum(ww)
            out[f"ew_{key}_mean"] = round(mu, 2); out[f"ew_{key}_chi2r"] = round(float(np.sum(ww * (x[g] - mu) ** 2)) / (g.sum() - 1), 2)
            out[f"ew_{key}_range"] = round(float(x[g].max() - x[g].min()), 2)
    srows.append(out)
    if k % 5000 == 0: print(k, len(srows), flush=True)
pd.DataFrame(vrows).to_csv("visit_rv.csv", index=False); pd.DataFrame(srows).to_csv("star_rv.csv", index=False); print("DONE", len(srows), flush=True)
