"""Screen of hot SDSS-V DR20 white dwarfs for ultra-high-excitation (UHE) absorption features.
Sample: SnowWhite (snow_white_boss_star) objects with BP-RP < -0.40, or classification containing DO/DAO/PG1159/O(H)/sdO/He, or
Teff >= 45 kK; S/N > 8; excluding MS/CV/QSO/STAR classes (sample.csv). Spectrum: coadd of the in-stack mwmVisit spectra (XCSAO shift
removed; sdssv.py). Equivalent widths (vacuum A) against a linear continuum fitted to side bands:
  f5280: 5262-5310 (continuum 5190-5235, 5330-5390); f5243: 5234-5256 (5190-5228, 5330-5390); f4655: 4640-4668 (4600-4630, 4705-4730);
  f6068: 6045-6090 (5990-6035, 6105-6140); controls c5480: 5452-5500 (5380-5435, 5525-5580) and c5100: 5075-5123 (5010-5060, 5140-5185).
Per visit: f5280. Region cuts (4600-4740, 5150-5420, 5950-6300 A) are stored per object for inspection.
python uhe_screen.py <sample.csv> <out_dir> [n_workers]"""
import os, sys, numpy as np, pandas as pd
from concurrent.futures import ThreadPoolExecutor
sys.path.insert(0, os.path.expanduser("~/claude_projects/sdssv-white-dwarfs-2026/scripts")); import sdssv
FEAT = {"f5280": (5262, 5310, [(5190, 5235), (5330, 5390)]), "f5243": (5234, 5256, [(5190, 5228), (5330, 5390)]),
        "f4655": (4640, 4668, [(4600, 4630), (4705, 4730)]), "f6068": (6045, 6090, [(5990, 6035), (6105, 6140)]),
        "c5480": (5452, 5500, [(5380, 5435), (5525, 5580)]), "c5100": (5075, 5123, [(5010, 5060), (5140, 5185)])}
def ew(w, f, iv, a, b, cs):
    m = np.zeros_like(w, bool)
    for c0, c1 in cs: m |= (w > c0) & (w < c1)
    m &= (iv > 0) & np.isfinite(f)
    k = (w > a) & (w < b) & (iv > 0) & np.isfinite(f)
    if m.sum() < 10 or k.sum() < 10: return np.nan, np.nan
    p = np.polyfit(w[m], f[m], 1, w=np.sqrt(iv[m])); c = np.polyval(p, w)
    if np.median(c[k]) <= 0: return np.nan, np.nan
    dw = np.gradient(w)[k]; return float(np.sum((1 - f[k] / c[k]) * dw)), float(np.sqrt(np.sum((np.sqrt(1 / iv[k]) / c[k] * dw) ** 2)))
def one(sid, out):
    path = os.path.join(sdssv.CACHE, f"mwmVisit-0.8.1-{sid}.fits"); existed = os.path.exists(path)
    try:
        vs = sdssv.visits(sid)
    except Exception as e:
        return dict(sdss_id=sid, status=f"fail {str(e)[:60]}")
    try:
        use = [v for v in vs if v["in_stack"]] or vs; w, f, iv = sdssv.coadd(use)[:3]
        d = dict(sdss_id=sid, status="ok", n_visits=len(vs), n_used=len(use))
        for k, (a, b, cs) in FEAT.items():
            e, s = ew(w, f, iv, a, b, cs); d[k] = round(e, 3) if np.isfinite(e) else np.nan; d[k + "_e"] = round(s, 3) if np.isfinite(s) else np.nan
        pv = []
        for v in use:
            e, s = ew(v["wave"], v["flux"], v["ivar"], *FEAT["f5280"]); pv.append(f"{v['mjd']}:{e:.2f}:{s:.2f}")
        d["f5280_visits"] = " ".join(pv)
        ok = (iv > 0) & np.isfinite(f); keep = ok & (((w > 4600) & (w < 4740)) | ((w > 5150) & (w < 5420)) | ((w > 5950) & (w < 6300)))
        np.savez_compressed(os.path.join(out, "cuts", f"{sid}.npz"), w=w[keep], f=f[keep], iv=iv[keep])
        return d
    finally:
        if not existed and os.path.exists(path): os.remove(path)
if __name__ == "__main__":
    S = pd.read_csv(sys.argv[1], dtype={"sdss_id": str}); out = sys.argv[2]; nw = int(sys.argv[3]) if len(sys.argv) > 3 else 4
    os.makedirs(os.path.join(out, "cuts"), exist_ok=True); res_f = os.path.join(out, "uhe_screen.csv")
    done = set(pd.read_csv(res_f, dtype={"sdss_id": str}).sdss_id) if os.path.exists(res_f) else set()
    todo = [s for s in S.sdss_id if s not in done]; print(len(todo), "to do", flush=True); rows = []
    with ThreadPoolExecutor(nw) as ex:
        for i, d in enumerate(ex.map(lambda s: one(s, out), todo)):
            rows.append(d)
            if (i + 1) % 50 == 0 or i + 1 == len(todo):
                pd.DataFrame(rows).to_csv(res_f, mode="a", header=not os.path.exists(res_f), index=False); rows = []; print(i + 1, "done", flush=True)
