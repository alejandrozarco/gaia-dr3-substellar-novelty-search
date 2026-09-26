# Download SPOC 120-s target pixel files for given (sid, sector) pairs from MAST (public)
import sys, json, os
from astroquery.mast import Observations
M = json.load(open("data/mast_timeseries.json"))
pairs = [a.split(":") for a in sys.argv[1:]]
for sid, sec in pairs:
    obsids = [x["obsid"] for x in M[sid] if x["coll"] == "TESS" and x["exp"] == 120.0 and x["seq"] == sec]
    if not obsids: print(sid, sec, "no 120-s obs"); continue
    obs = Observations.query_criteria(obs_id=obsids)
    prods = Observations.get_product_list(obs)
    sel = [p for p in prods if str(p["productSubGroupDescription"]) == "TP" and str(p["productFilename"]).endswith("_tp.fits")]
    for p in sel:
        dest = f"tpf/{sid}_{p['productFilename']}"
        if not os.path.exists(dest):
            Observations.download_file(p["dataURI"], local_path=dest)
        print(sid, sec, dest, os.path.getsize(dest) if os.path.exists(dest) else "HOLE")
