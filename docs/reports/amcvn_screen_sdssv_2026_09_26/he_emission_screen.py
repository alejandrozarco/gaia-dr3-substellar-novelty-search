"""Screen of SDSS-V DR20 SnowWhite objects with classes containing CV, DB or DO for helium emission without hydrogen emission
(AM CVn-type spectra). Spectrum: coadd of the in-stack mwmVisit spectra (all visits if none in stack; sdssv.py).
Equivalent widths (vacuum A, positive = absorption) against a linear continuum from side bands:
  HeI4473 4462-4484 (4430-4455, 4495-4520); HeII4686 4675-4698 (4640-4665, 4705-4730); HeI5877 5864-5890 (5820-5855, 5905-5940);
  HeI6680 6668-6692 (6620-6650, 6710-6740); Ha 6545-6584 (6480-6520, 6610-6640); Hb 4848-4877 (4800-4830, 4895-4925).
Per visit: HeI5877 and Ha. Region cuts 4400-4950 and 5800-6750 A stored per object.
python he_emission_screen.py <sample.csv> <out_dir> [n_workers]"""
import os, sys, numpy as np, pandas as pd
from concurrent.futures import ThreadPoolExecutor
sys.path.insert(0, os.path.expanduser("~/claude_projects/sdssv-white-dwarfs-2026/scripts")); import sdssv
FEAT = {"HeI4473": (4462, 4484, [(4430, 4455), (4495, 4520)]), "HeII4686": (4675, 4698, [(4640, 4665), (4705, 4730)]),
        "HeI5877": (5864, 5890, [(5820, 5855), (5905, 5940)]), "HeI6680": (6668, 6692, [(6620, 6650), (6710, 6740)]),
        "Ha": (6545, 6584, [(6480, 6520), (6610, 6640)]), "Hb": (4848, 4877, [(4800, 4830), (4895, 4925)])}
def ew(w, f, iv, a, b, cs):
    m = np.zeros_like(w, bool)
    for c0, c1 in cs: m |= (w > c0) & (w < c1)
    m &= (iv > 0) & np.isfinite(f); k = (w > a) & (w < b) & (iv > 0) & np.isfinite(f)
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
        use = [v for v in vs if v["in_stack"]] or vs; w, f, iv = sdssv.coadd(use)[:3]; d = dict(sdss_id=sid, status="ok", n_visits=len(vs), n_used=len(use))
        for k, (a, b, cs) in FEAT.items():
            e, s = ew(w, f, iv, a, b, cs); d[k] = round(e, 2) if np.isfinite(e) else np.nan; d[k + "_e"] = round(s, 2) if np.isfinite(s) else np.nan
        pv = []
        for v in vs:
            e1, _ = ew(v["wave"], v["flux"], v["ivar"], *FEAT["HeI5877"]); e2, _ = ew(v["wave"], v["flux"], v["ivar"], *FEAT["Ha"]); pv.append(f"{v['mjd']}:{e1:.1f}:{e2:.1f}")
        d["visits_HeI5877_Ha"] = " ".join(pv)
        ok = (iv > 0) & np.isfinite(f); keep = ok & (((w > 4400) & (w < 4950)) | ((w > 5800) & (w < 6750)))
        np.savez_compressed(os.path.join(out, "cuts", f"{sid}.npz"), w=w[keep], f=f[keep], iv=iv[keep]); return d
    finally:
        if not existed and os.path.exists(path): os.remove(path)
if __name__ == "__main__":
    S = pd.read_csv(sys.argv[1], dtype={"sdss_id": str}); out = sys.argv[2]; nw = int(sys.argv[3]) if len(sys.argv) > 3 else 6
    os.makedirs(os.path.join(out, "cuts"), exist_ok=True); rf = os.path.join(out, "he_screen.csv")
    done = set(pd.read_csv(rf, dtype={"sdss_id": str}).sdss_id) if os.path.exists(rf) else set()
    todo = [s for s in S.sdss_id if s not in done]; print(len(todo), "to do", flush=True); rows = []
    with ThreadPoolExecutor(nw) as ex:
        for i, d in enumerate(ex.map(lambda s: one(s, out), todo)):
            rows.append(d)
            if (i + 1) % 50 == 0 or i + 1 == len(todo):
                pd.DataFrame(rows).to_csv(rf, mode="a", header=not os.path.exists(rf), index=False); rows = []; print(i + 1, "done", flush=True)
