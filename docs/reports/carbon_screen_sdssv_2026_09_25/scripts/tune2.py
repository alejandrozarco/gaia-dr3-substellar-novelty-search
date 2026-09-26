import numpy as np, pandas as pd, os
import carbon_screen as cs
from scipy.ndimage import percentile_filter, gaussian_filter1d
s = pd.read_csv("daq_sample.csv", dtype={"sdss_id": str, "gaia_dr3_source_id": str})
have = [r for r in s.itertuples() if os.path.exists(f"/tmp/fanout/exotic_atm/visit/mwmVisit-0.8.1-{r.sdss_id}.fits")]
cache = {}
for r in have:
    v = cs.load(r.sdss_id)
    if not v: continue
    num = np.nansum([x["f"] * x["iv"] for x in v], axis=0); den = np.sum([x["iv"] for x in v], axis=0)
    cache[r.sdss_id] = (np.where(den > 0, num / np.where(den > 0, den, 1), np.nan), den, r.is_control)
LIN = dict(cs.LINES); LIN["C"] = LIN["C I"] + LIN["C II"]
def prep(f, iv, win, pct):
    m = np.isfinite(f) & (iv > 0)
    ff = np.interp(np.arange(len(cs.grid)), np.where(m)[0], f[m])
    npix = int(round(np.log10(1 + win / 5000) / 6e-5))
    cont = gaussian_filter1d(percentile_filter(ff, pct, size=npix), npix / 3)
    d = 1 - ff / cont; w = iv * cont ** 2; good = m.copy()
    for a, b in cs.MASK: good &= ~((cs.grid > a) & (cs.grid < b))
    w = np.where(good, w, 0); w = np.minimum(w, np.percentile(w[good], 90)); d[~good] = 0
    return d, w
def mf(d, w, T):
    num = T @ (w * d); den = (T ** 2) @ w
    return num / np.sqrt(den)
def run(win, pct, fw, vlo=-200, vhi=400):
    sig = fw / 2.3548; TT = {}
    for sp, L in LIN.items():
        T = np.zeros((len(cs.vels), len(cs.grid)))
        for lam in L: T += np.exp(-0.5 * ((cs.grid[None, :] - lam * (1 + cs.vels / cs.C)[:, None]) / sig) ** 2)
        TT[sp] = T
    inw = (cs.vels >= vlo) & (cs.vels <= vhi); far = (cs.vels < vlo - 400) | (cs.vels > vhi + 400)
    res = []
    for sid, (f, iv, isc) in cache.items():
        d, w = prep(f, iv, win, pct); row = dict(sid=sid, ctrl=isc)
        for sp in ("C I", "C II", "C", "He I"):
            z = mf(d, w, TT[sp]); med = np.median(z[far]); mad = 1.4826 * np.median(np.abs(z[far] - med))
            c = (z - med) / mad; k = np.argmax(np.where(inw, c, -99))
            row[sp] = c[k]; row[sp + "_v"] = cs.vels[k]
        res.append(row)
    d = pd.DataFrame(res); bg = d[~d.ctrl]
    print(f"win {win} pct {pct} fwhm {fw}: bg n={len(bg)} C p95={np.percentile(bg['C'],95):.1f} p99={np.percentile(bg['C'],99):.1f} max={bg['C'].max():.1f} | CI p99 {np.percentile(bg['C I'],99):.1f} CII p99 {np.percentile(bg['C II'],99):.1f}")
    for r in d[d.ctrl].itertuples(): print(f"   ctrl {r.sid}: C {r.C:.1f} @{r.C_v:.0f}  C I {getattr(r,'_4'):.1f}  C II {getattr(r,'_6'):.1f}")
    return d
for cfg in [(25, 80, 5), (60, 85, 6), (120, 85, 8)]:
    d = run(*cfg)
d.sort_values("C", ascending=False).head(12).to_csv("tune2_top.csv", index=False)
print(d.sort_values("C", ascending=False).head(12)[["sid","ctrl","C","C_v","C I","C II","He I"]].to_string())
