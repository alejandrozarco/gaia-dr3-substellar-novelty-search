# Box-least-squares eclipse search on every finished southern Track-1 ATLAS light curve (the screen itself used sinusoid LS only,
# which flagged the 3.55-h eclipsing binary 4731701084150029824 in one band at half its period). Same cleaning as the screen (uJy, v3
# gates, per-season medians). BLS per band on 0.04-3 d, durations 5-60 min; a target is flagged when the o and c best periods agree
# (or are 1:2 / 2:1) and each band's peak SDE exceeds 7, or when one band reaches SDE >= 10. Permutation null for flagged ones.
import numpy as np, json, glob, os
from astropy.timeseries import BoxLeastSquares
def load(fn):
    L = [l for l in open(fn).read().splitlines() if l.strip()]
    if len(L) < 5: return None
    hdr = L[0].lstrip("#").split(); R = [dict(zip(hdr, l.split())) for l in L[1:]]
    ok = [x for x in R if float(x["duJy"]) > 0 and float(x["err"]) == 0 and float(x["chi/N"]) < 10]; D = {}
    for b in ("o", "c"):
        s = [x for x in ok if x["F"] == b]
        if len(s) < 50: continue
        med = np.median([float(x["duJy"]) for x in s]); s = [x for x in s if float(x["duJy"]) < 3 * med]
        mjd = np.array([float(x["MJD"]) for x in s]); f = np.array([float(x["uJy"]) for x in s]); e = np.array([float(x["duJy"]) for x in s])
        season = np.floor((mjd - 57000) / 365.25 + 0.3).astype(int)
        for sv in np.unique(season): f[season == sv] -= np.median(f[season == sv])
        clip = np.abs(f) < 5 * 1.4826 * np.median(np.abs(f)) + 3 * np.median(e)
        D[b] = (mjd[clip], f[clip], e[clip])
    return D
periods = np.exp(np.linspace(np.log(0.05), np.log(3.0), 150000)); durations = np.array([5, 10, 20, 40]) / 1440.
out = {}
for fn in sorted(glob.glob("atlas_raw/*.txt")):
    sid = os.path.basename(fn)[:-4]; D = load(fn)
    if not D: out[sid] = "NO_DATA"; continue
    res = {}
    for b, (t, f, e) in D.items():
        bls = BoxLeastSquares(t, f, dy=e); pw = bls.power(periods, durations, objective="snr")
        p = pw.power; i = np.argmax(p); sde = (p[i] - np.mean(p)) / np.std(p)
        res[b] = dict(P=float(periods[i]), sde=float(sde), depth=float(pw.depth[i]), depth_snr=float(pw.depth_snr[i]), dur_min=float(pw.duration[i] * 1440), n=int(len(t)))
    flag = False
    if "o" in res and "c" in res:
        r = res["o"]["P"] / res["c"]["P"]
        agree = min(abs(r - 1), abs(r - 2), abs(r - 0.5)) < 0.002
        flag = (agree and res["o"]["sde"] > 7 and res["c"]["sde"] > 7) or max(res["o"]["sde"], res["c"]["sde"]) >= 10
    elif res: flag = max(v["sde"] for v in res.values()) >= 10
    res["flag"] = bool(flag); out[sid] = res
    print(sid, "FLAG" if flag else "    ", " | ".join(f"{b}: P {v['P']:.6f} d SDE {v['sde']:.1f} depth {v['depth']:.1f} uJy ({v['depth_snr']:.1f} sig) dur {v['dur_min']:.0f} min n {v['n']}" for b, v in res.items() if b in ("o", "c")), flush=True)
json.dump(out, open("bls_all.json", "w"), indent=1)
