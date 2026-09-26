# Fine-grid BLS on all finished southern Track-1 ATLAS light curves (control 4731701084150029824 recovered at 0.14787 d in o and c).
# Uniform frequency grid 1-20 c/d, df 2.5e-5; durations 5-40 min; robust SDE = (peak - median)/(1.4826 MAD). Flag: o and c top
# periods agree within 0.1% (or 1:2, 2:1) with robust SDE >= 8 in both, or robust SDE >= 15 in one band with >= 500 points.
import numpy as np, json, glob, os
exec(open("bls_all.py").read().split("periods = ")[0])
from astropy.timeseries import BoxLeastSquares
freq = np.arange(1.0, 20.0, 2.5e-5); periods = 1 / freq; durations = np.array([5, 10, 20, 40]) / 1440.
out = {}
for fn in sorted(glob.glob("atlas_raw/*.txt")):
    sid = os.path.basename(fn)[:-4]; D = load(fn)
    if not D: out[sid] = "NO_DATA"; print(sid, "NO_DATA", flush=True); continue
    res = {}
    for b, (t, f, e) in D.items():
        if len(t) < 100: continue
        pw = BoxLeastSquares(t, f, dy=e).power(periods, durations, objective="likelihood"); p = pw.power; i = np.argmax(p)
        sde = (p[i] - np.median(p)) / (1.4826 * np.median(np.abs(p - np.median(p))))
        res[b] = dict(P=float(periods[i]), sde=float(sde), depth=float(pw.depth[i]), depth_snr=float(pw.depth_snr[i]), dur_min=float(pw.duration[i] * 1440), n=int(len(t)))
    flag = False
    if "o" in res and "c" in res:
        r = res["o"]["P"] / res["c"]["P"]; agree = min(abs(r - 1), abs(r - 2) / 2, abs(r - 0.5) / 0.5) < 0.001
        flag = (agree and min(res["o"]["sde"], res["c"]["sde"]) >= 8)
    flag = flag or any(v["sde"] >= 15 and v["n"] >= 500 for v in res.values())
    res["flag"] = bool(flag); out[sid] = res
    print(sid, "FLAG" if flag else "    ", " | ".join(f"{b}: P {v['P']:.7f} SDE {v['sde']:.1f} depth {v['depth']:.1f} ({v['depth_snr']:.1f} sig) dur {v['dur_min']:.0f} n {v['n']}" for b, v in res.items() if b in ("o", "c")), flush=True)
    json.dump(out, open("bls_all2.json", "w"), indent=1)
print("BLS2_DONE")
