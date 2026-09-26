"""For RV candidates: compare each visit's measured H-alpha velocity with that visit's XCSAO velocity and in_stack flag (mwmVisit)."""
import os
import sys, numpy as np, pandas as pd
sys.path.insert(0, os.path.expanduser("~/claude_projects/sdssv-white-dwarfs-2026/scripts")); import sdssv
from astropy.io import fits
v = pd.read_csv("visit_rv.csv", dtype={"sdss_id": str}); c = pd.read_csv("rv_candidates.csv", dtype={"sdss_id": str})
rows = []
for sid in c.sdss_id.head(int(sys.argv[1])):
    try: h = fits.open(sdssv.fetch(sid, "visit"))
    except Exception as ex: print(sid, "HOLE"); continue
    meta = []
    for i in (1, 2):
        if h[i].data is None or len(h[i].data) == 0: continue
        for r in h[i].data: meta.append((int(r["mjd"]), bool(r["in_stack"]), float(r["xcsao_v_rad"]), float(r["snr"])))
    vv = v[v.sdss_id == sid]
    for _, r in vv.iterrows():
        m = [x for x in meta if x[0] == r.mjd]
        for x in m: rows.append(dict(sdss_id=sid, mjd=r.mjd, rv=r.rv, e_rv=r.e_rv, in_stack=x[1], xcsao=round(x[2], 1), snr=round(x[3], 1)))
out = pd.DataFrame(rows); out.to_csv("xcsao_check.csv", index=False)
for sid, g in out.groupby("sdss_id", sort=False):
    print(sid, " | ".join(f"{r.mjd}:{r.rv:+.0f}({'S' if r.in_stack else 'n'},x{r.xcsao:+.0f})" for _, r in g.iterrows()))
