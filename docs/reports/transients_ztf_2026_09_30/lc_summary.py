"""Compact ALeRCE light-curve summary for a list of ZTF objects (2026-09-30): all ZTF ids within 2 arcsec, per-id first/last
detection, number of detections, brightest and faintest magpsf per filter, deepest pre-first-detection limit, and the number of
separate outburst episodes (detections grouped with gaps > 20 d). Usage: python lc_summary.py oid:ra:dec [...]"""
import sys, requests, time, pandas as pd, numpy as np
A = "https://api.alerce.online/ztf/v1"
def get(u, p=None):
    for k in range(3):
        try:
            r = requests.get(u, params=p, timeout=90)
            if r.ok: return r.json()
        except Exception: time.sleep(5)
    return None
for arg in sys.argv[1:]:
    o, ra, de = arg.split(":"); cone = get(f"{A}/objects", dict(ra=float(ra), dec=float(de), radius=2, page_size=20)) or {}
    ids = [i["oid"] for i in cone.get("items", [])] or [o]; out = []
    for i in ids:
        d = get(f"{A}/objects/{i}/detections"); n = get(f"{A}/objects/{i}/non_detections")
        if not d: out.append(f"{i}: no detections"); continue
        d = pd.DataFrame(d).sort_values("mjd"); d = d[d.isdiffpos.astype(str).isin(["1", "t", "True"])]
        if not len(d): out.append(f"{i}: only negative"); continue
        ep = (np.diff(d.mjd.values) > 20).sum() + 1; f = {1: "g", 2: "r", 3: "i"}
        mm = "; ".join(f"{f[k]} {x.magpsf.min():.2f}-{x.magpsf.max():.2f} (n{len(x)})" for k, x in d.groupby("fid"))
        pre = ""
        if n:
            n = pd.DataFrame(n); b = n[n.mjd < d.mjd.min()]
            if len(b): pre = f"; deepest limit before first det {b.diffmaglim.max():.2f} (last {d.mjd.min() - b.mjd.max():.1f} d before)"
        out.append(f"{i}: MJD {d.mjd.min():.1f}-{d.mjd.max():.1f}, {len(d)} det, {ep} episode(s); {mm}{pre}")
    print(o, "|", " || ".join(out), flush=True)
