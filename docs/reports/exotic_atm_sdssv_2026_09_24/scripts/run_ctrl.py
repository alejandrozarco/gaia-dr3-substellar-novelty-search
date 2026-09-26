import sys, os, numpy as np, pandas as pd
sys.path.insert(0, "/tmp/fanout/exotic_atm/scripts"); from common import best_star; from emis2 import metric_ctrl
r = pd.read_csv(sys.argv[1]); vals = []
for s in r.sdss_id:
    fn = f"/tmp/fanout/exotic_atm/spec/mwmStar-0.8.1-{s}.fits"
    if not os.path.exists(fn): fn = f"/tmp/mwd/spec/mwmStar-0.8.1-{s}.fits"
    try:
        hdu, w, f, iv, snr = best_star(fn); vals.append(metric_ctrl(w, f, iv))
    except Exception: vals.append(np.nan)
r["ctrl_sig"] = vals; r.to_csv(sys.argv[1], index=False); print("ok")
