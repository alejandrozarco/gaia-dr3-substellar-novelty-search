# Download TESS SPOC 120-s light curves (lc.fits) and K2 LCs from MAST (public) for all stars that have them.
import json, os, sys, time
from astroquery.mast import Observations
import numpy as np
M = json.load(open("data/mast_timeseries.json"))
os.makedirs("tess", exist_ok=True); os.makedirs("k2", exist_ok=True)
log = open("logs/tess_download.log", "a")
for sid, L in M.items():
    if L == "HOLE" or not L: continue
    obsids = sorted(set(x["obsid"] for x in L if (x["coll"] == "TESS" and x["prov"] == "SPOC" and x["exp"] == 120.0) or x["coll"] == "K2"))
    if not obsids: continue
    obs = Observations.query_criteria(obs_id=obsids)
    prods = Observations.get_product_list(obs)
    sel = [p for p in prods if (str(p["productSubGroupDescription"]) in ("LC", "LLC", "SLC")) and str(p["productFilename"]).endswith(".fits")]
    for p in sel:
        fn = str(p["productFilename"])
        coll = "k2" if "ktwo" in fn or "hlsp" in fn else "tess"
        dest = f"{coll}/{sid}_{fn}"
        if os.path.exists(dest): continue
        for attempt in range(3):
            try:
                r = Observations.download_file(p["dataURI"], local_path=dest)
                break
            except Exception as e:
                print(sid, fn, "EXC", repr(e)[:150]); time.sleep(5); r = None
        ok = os.path.exists(dest)
        msg = f"{sid} {fn} {'OK' if ok else 'HOLE'} {os.path.getsize(dest) if ok else 0}"
        print(msg, flush=True); log.write(msg + "\n"); log.flush()
