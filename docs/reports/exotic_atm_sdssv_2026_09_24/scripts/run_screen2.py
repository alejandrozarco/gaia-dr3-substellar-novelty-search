import sys, csv, os, json, numpy as np, pandas as pd
sys.path.insert(0, "/tmp/fanout/exotic_atm/scripts"); from common import best_star; from emis2 import metric
ids = [r["sdss_id"] for r in csv.DictReader(open(sys.argv[1]))]
rows = []
for s in ids:
    fn = f"/tmp/fanout/exotic_atm/spec/mwmStar-0.8.1-{s}.fits"
    if not os.path.exists(fn):
        fn = f"/tmp/mwd/spec/mwmStar-0.8.1-{s}.fits"
        if not os.path.exists(fn): rows.append(dict(sdss_id=int(s), status="MISSING")); continue
    try:
        b = best_star(fn)
        if b is None: rows.append(dict(sdss_id=int(s), status="EMPTY")); continue
        hdu, w, f, iv, snr = b; m = metric(w, f, iv)
        m["top_Ha"] = json.dumps(m["top_Ha"]); m["top_Hb"] = json.dumps(m["top_Hb"])
        rows.append(dict(sdss_id=int(s), status="ok", hdu=hdu, snr_file=snr, **m))
    except Exception as e: rows.append(dict(sdss_id=int(s), status="ERR " + str(e)[:60]))
pd.DataFrame(rows).to_csv(sys.argv[2], index=False); print("rows", len(rows))
