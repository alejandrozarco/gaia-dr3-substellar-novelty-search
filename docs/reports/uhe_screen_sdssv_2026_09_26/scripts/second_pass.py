import os, sys, numpy as np, pandas as pd
from concurrent.futures import ThreadPoolExecutor
sys.path.insert(0, os.path.expanduser("~/claude_projects/sdssv-white-dwarfs-2026/scripts")); import sdssv
U = os.path.dirname(os.path.abspath(__file__)); POS = [4495, 4941, 5280, 5665]
def ew(w, f, iv, l, hw=12):
    m = (((w > l - hw - 30) & (w < l - hw - 3)) | ((w > l + hw + 3) & (w < l + hw + 30))) & (iv > 0) & np.isfinite(f); k = (np.abs(w - l) < hw) & (iv > 0) & np.isfinite(f)
    if m.sum() < 8 or k.sum() < 8: return np.nan, np.nan
    p = np.polyfit(w[m], f[m], 1, w=np.sqrt(iv[m])); c = np.polyval(p, w); dw = np.gradient(w)[k]
    return float(np.sum((1 - f[k] / c[k]) * dw)), float(np.sqrt(np.sum((np.sqrt(1 / iv[k]) / c[k] * dw) ** 2)))
def one(sid):
    path = os.path.join(sdssv.CACHE, f"mwmVisit-0.8.1-{sid}.fits"); existed = os.path.exists(path)
    try:
        vs = sdssv.visits(sid); use = [v for v in vs if v["in_stack"]] or vs; w, f, iv = sdssv.coadd(use)[:3]; d = dict(sdss_id=sid)
        for l in POS: e, s = ew(w, f, iv, l); d[f"e{l}"] = e; d[f"s{l}"] = s
        # control positions
        for l in (5100, 5480, 5740): e, s = ew(w, f, iv, l); d[f"c{l}"] = e
        return d
    except Exception as ex:
        return dict(sdss_id=sid, err=str(ex)[:60])
    finally:
        if not existed and os.path.exists(path): os.remove(path)
L = pd.read_csv(sys.argv[1], dtype={"sdss_id": str})
with ThreadPoolExecutor(6) as ex: rows = list(ex.map(one, L.sdss_id))
R = L.merge(pd.DataFrame(rows), on="sdss_id"); R.to_csv(sys.argv[2], index=False)
pd.set_option("display.width", 250)
print(R[["sdss_id", "gaia_dr3_source_id", "classification", "snr", "g_mag", "f5280", "e5280", "e5665", "s5665", "e4495", "e4941", "c5100", "c5480", "c5740"]].round(2).to_string(index=False))
