# Run the Balmer-emission screen over all downloaded mwmStar files of the DAHe screen sample; output one row per sdss_id.
import sys, csv, os, json, numpy as np, pandas as pd
sys.path.insert(0, "/tmp/fanout/exotic_atm/scripts"); from common import best_star, load_star; from emis import screen
ids = [r["sdss_id"] for r in csv.DictReader(open("/tmp/fanout/exotic_atm/screen_dahe_all.csv"))]
rows = []; miss = 0
for s in ids:
    fn = f"/tmp/fanout/exotic_atm/spec/mwmStar-0.8.1-{s}.fits"
    if not os.path.exists(fn):
        fn2 = f"/tmp/mwd/spec/mwmStar-0.8.1-{s}.fits"
        if os.path.exists(fn2): fn = fn2
        else: miss += 1; rows.append(dict(sdss_id=int(s), status="MISSING")); continue
    try:
        b = best_star(fn)
        if b is None: rows.append(dict(sdss_id=int(s), status="EMPTY")); continue
        hdu, w, f, iv, snr = b
        a, h = screen(w, f, iv)
        rows.append(dict(sdss_id=int(s), status="ok", hdu=hdu, snr_file=snr, sigHa=a["sig"], ewHa=a["ew"], npkHa=a["npk"], lamHa=a["lam_pk"], noiseHa=a["noise"],
                         pkHa=json.dumps(a["peaks"]), sigHb=h["sig"], ewHb=h["ew"], npkHb=h["npk"], lamHb=h["lam_pk"], pkHb=json.dumps(h["peaks"])))
    except Exception as e:
        rows.append(dict(sdss_id=int(s), status="ERR " + str(e)[:60]))
pd.DataFrame(rows).to_csv("/tmp/fanout/exotic_atm/screen_dahe_results.csv", index=False)
print("rows", len(rows), "missing", miss)
