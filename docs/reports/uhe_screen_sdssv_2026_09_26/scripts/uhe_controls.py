import os, sys, numpy as np, pandas as pd
sys.path.insert(0, os.path.expanduser("~/claude_projects/sdssv-white-dwarfs-2026/scripts")); import sdssv
W = os.path.dirname(os.path.abspath(__file__))
R = pd.read_csv(f"{W}/uhe_known_gaia.csv", dtype={"gaia": str}); sw = sdssv.snowwhite([g for g in R.gaia.dropna()])
sw = sw.rename(columns={c: c for c in sw.columns}); gcol = [c for c in sw.columns if "gaia" in c.lower() or "source" in c.lower()][0]
sw[gcol] = sw[gcol].astype(str); M = R.merge(sw, left_on="gaia", right_on=gcol)
FEAT = {"f5285": (5262, 5310, [(5190, 5245), (5330, 5390)]), "f6068": (6045, 6090, [(5990, 6035), (6105, 6140)]), "f4655": (4640, 4668, [(4600, 4630), (4705, 4730)]),
        "ctrl5480": (5452, 5500, [(5380, 5435), (5525, 5580)]), "ctrl5100": (5075, 5123, [(5010, 5060), (5140, 5185)])}
def ew(w, f, iv, a, b, cs):
    m = np.zeros_like(w, bool)
    for c0, c1 in cs: m |= (w > c0) & (w < c1)
    m &= (iv > 0) & np.isfinite(f)
    if m.sum() < 10: return np.nan, np.nan
    p = np.polyfit(w[m], f[m], 1, w=np.sqrt(iv[m])); c = np.polyval(p, w); k = (w > a) & (w < b) & (iv > 0) & np.isfinite(f); dw = np.gradient(w)[k]
    return np.sum((1 - f[k] / c[k]) * dw), np.sqrt(np.sum((np.sqrt(1 / iv[k]) / c[k] * dw) ** 2))
rows = []
extra = pd.DataFrame([dict(name="WDJ095852.35-175833.41 (target)", sp="target", sdss_id="100568930")])
sid_col = [c for c in M.columns if c.lower() == "sdss_id"][0]
cls_col = [c for c in M.columns if "class" in c.lower()][0]
todo = [(r["name"], r["sp"], str(r[sid_col]), r[cls_col]) for _, r in M.iterrows()] + [("WDJ095852.35-175833.41", "target", "100568930", "DA")]
for n, sp, sid, cl in todo:
    vs = sdssv.visits(sid); vs = [v for v in vs if v["in_stack"]] or vs; w, f, iv = sdssv.coadd(vs)[:3]
    d = dict(name=n, lit=sp, sdss_id=sid, snowwhite=cl, snr=round(float(np.nanmedian([v["snr"] for v in vs])), 1))
    for k, (a, b, cs) in FEAT.items():
        e, s = ew(w, f, iv, a, b, cs); d[k] = round(e, 2); d[k + "_e"] = round(s, 2)
    rows.append(d); print(d, flush=True)
pd.DataFrame(rows).to_csv(f"{W}/uhe_controls.csv", index=False)
