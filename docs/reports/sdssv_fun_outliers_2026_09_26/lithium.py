"""Lane 3: Li I 6707.8 A (air; vacuum 6709.6) absorption in SDSS-V coadds (lane_gasdisc/store f_6400). Normalisation: straight line
through 6690-6700 and 6718-6730 A. Depth = weighted mean of (1 - n) within +-4 A of 6709.6; error from ivar. Also Ca I 6573 (vacuum
6574.6; same measurement with 6555-6562/6585-6595 continuum, only meaningful where H-alpha is weak) for context. Control windows at
6700.0 and 6722.0 A (+-4 A) give the depth distribution of featureless spectra. Output lithium.csv sorted by significance."""
import os, glob, numpy as np, pandas as pd
GRID = 10 ** np.arange(np.log10(3850), np.log10(9250), 6e-5); W = GRID[(GRID > 6400) & (GRID < 6750)]
def depth(f, iv, c0, c1, lam, half=4.0):
    ok = (iv > 0) & np.isfinite(f); m = ok & (((W > c0[0]) & (W < c0[1])) | ((W > c1[0]) & (W < c1[1])))
    if m.sum() < 8: return np.nan, np.nan
    p = np.polyfit(W[m], f[m], 1, w=np.sqrt(iv[m])); c = np.polyval(p, W)
    if np.median(c[m]) <= 0: return np.nan, np.nan
    n, ivn = f / c, iv * c ** 2; w = ok & (np.abs(W - lam) < half)
    if w.sum() < 5: return np.nan, np.nan
    d = np.sum((1 - n[w]) * ivn[w]) / np.sum(ivn[w]); e = 1 / np.sqrt(np.sum(ivn[w])); return d, e
sw = pd.read_csv("/tmp/hotdq/lane_gasdisc/sw_all.csv", dtype=str).drop_duplicates("sdss_id").set_index("sdss_id")
rows = []
for fn in sorted(glob.glob("/tmp/hotdq/lane_gasdisc/store/*/*.npz")):
    sid = os.path.basename(fn)[:-4]; d = np.load(fn); f, iv = d["f_6400"].astype(float), d["iv_6400"].astype(float)
    li, eli = depth(f, iv, (6690, 6700), (6718, 6730), 6709.6)
    c1, ec1 = depth(f, iv, (6685, 6694), (6705, 6715), 6700.0)
    c2, ec2 = depth(f, iv, (6712, 6718), (6728, 6740), 6722.0)
    ca, eca = depth(f, iv, (6555, 6562), (6585, 6595), 6574.6)
    rows.append(dict(sdss_id=sid, li_depth=li, e_li=eli, li_sig=li / eli if eli else np.nan, ctrl1_sig=c1 / ec1 if ec1 else np.nan, ctrl2_sig=c2 / ec2 if ec2 else np.nan,
                     cai_depth=ca, cai_sig=ca / eca if eca else np.nan))
t = pd.DataFrame(rows); t["gaia"] = t.sdss_id.map(sw.gaia_dr3_source_id); t["cls"] = t.sdss_id.map(sw.classification); t["teff"] = t.sdss_id.map(sw.teff); t["G"] = t.sdss_id.map(sw.g_mag)
t.sort_values("li_sig", ascending=False).to_csv("lithium.csv", index=False); print("DONE", len(t))
