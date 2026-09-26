"""Phase plots for the 8 pilot candidates: every band, per-OID median normalisation,
fold at the pipeline period and at twice it (odd/even eclipse check)."""
import json, csv, io, math, subprocess, time
import numpy as np
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from astropy.timeseries import BoxLeastSquares
A = "/private/tmp/claude-501/-Users-USER-claude-projects/5bae4473-7497-4a6b-8bf6-3ecc9abd4295/scratchpad/arev"
R = [json.loads(l) for l in open(f"{A}/results.jsonl")]
C = [r for r in R if r.get("status") == "CANDIDATE"]
def fetch(ra, dec):
    u = ("https://irsa.ipac.caltech.edu/cgi-bin/ZTF/nph_light_curves?"
         f"POS=CIRCLE%20{ra:.6f}%20{dec:.6f}%20{3/3600:.6f}&BAD_CATFLAGS_MASK=32768&FORMAT=CSV")
    for k in range(4):
        p = subprocess.run(["curl", "-sL", "--max-time", "120", u], capture_output=True, text=True)
        if p.returncode == 0 and "oid" in p.stdout:
            rows = list(csv.DictReader(io.StringIO(p.stdout))); cd = math.cos(math.radians(dec))
            return [r for r in rows if math.hypot((float(r["ra"]) - ra) * cd, float(r["dec"]) - dec) * 3600 < 2.0]
        time.sleep(4 * (k + 1))
    raise RuntimeError("IRSA fetch failed")
def good(r):
    try:
        return (r["catflags"] == "0" and abs(float(r["sharp"])) < 0.5 and float(r["chi"]) < 3.0
                and float(r["mag"]) < float(r["limitmag"]) - 0.3)
    except Exception:
        return False
cache = {}
fig, axes = plt.subplots(len(C), 2, figsize=(13, 2.6 * len(C)))
for i, r in enumerate(C):
    rows = [x for x in fetch(r["ra"], r["dec"]) if good(x)]
    cache[r["source_id"]] = rows
    P = r["P"]
    # epoch of primary minimum from BLS at the fixed period, on the pipeline's band
    b0 = r["band"]
    v = [x for x in rows if x["filtercode"] == b0]
    t = np.array([float(x["mjd"]) for x in v]); m = np.array([float(x["mag"]) for x in v])
    oid = np.array([x["oid"] for x in v])
    for o in set(oid): m[oid == o] -= np.median(m[oid == o])
    fl = 10 ** (-0.4 * m)
    bls = BoxLeastSquares(t, fl); res = bls.power(np.array([P]), np.array([0.012, 0.025, 0.05, 0.09]), objective="snr")
    t0 = float(res.transit_time[0])
    r["t0_mjd"] = t0
    for j, (PP, lab) in enumerate(((P, "P"), (2 * P, "2P"))):
        ax = axes[i, j]
        for band, col in (("zg", "tab:green"), ("zr", "tab:red"), ("zi", "tab:purple")):
            vb = [x for x in rows if x["filtercode"] == band]
            if not vb: continue
            tb = np.array([float(x["mjd"]) for x in vb]); mb = np.array([float(x["mag"]) for x in vb])
            ob = np.array([x["oid"] for x in vb])
            for o in set(ob): mb[ob == o] -= np.median(mb[ob == o])
            ph = ((tb - t0) / PP + 0.25) % 1.0 - 0.25
            ax.plot(ph, mb, ".", ms=2, color=col, alpha=0.5, label=f"{band} ({len(vb)})")
            ax.plot(ph + 1, mb, ".", ms=2, color=col, alpha=0.15)
        ax.set_xlim(-0.25, 1.25); ax.invert_yaxis()
        lo = min(-0.15, -3 * r["scatter"]); ax.set_ylim(max(0.6, 1.5 * r["depth"] + 0.1), lo)
        ax.set_title(f"{r['source_id']}  fold at {lab} = {PP:.6f} d", fontsize=8)
        if j == 0: ax.legend(fontsize=6, loc="lower left")
        ax.tick_params(labelsize=7)
fig.tight_layout(); fig.savefig(f"{A}/pilot_candidates_folds.png", dpi=110)
json.dump({k: v for k, v in cache.items()}, open(f"{A}/lc_cache.json", "w"))
json.dump({r["source_id"]: r["t0_mjd"] for r in C}, open(f"{A}/t0.json", "w"))
print("saved", f"{A}/pilot_candidates_folds.png")
