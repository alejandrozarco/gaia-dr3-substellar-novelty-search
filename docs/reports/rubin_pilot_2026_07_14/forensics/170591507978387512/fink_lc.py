import requests, json, pandas as pd, numpy as np
B = "https://api.lsst.fink-portal.org"
OD = "/tmp/rubin_pilot/forensics/170591507978387512/"

# per-source lightcurve
r = requests.post(B + "/api/v1/sources", json={"diaObjectId": "170591507978387512", "output-format": "json"}, timeout=90)
print("sources:", r.status_code)
src = pd.DataFrame(r.json())
src.to_csv(OD + "fink_sources_raw.csv", index=False)
print("sources cols:", sorted(src.columns.tolist()))
print("n sources:", len(src))

# Fink-side forced photometry
r2 = requests.post(B + "/api/v1/fp", json={"diaObjectId": "170591507978387512", "output-format": "json"}, timeout=90)
print("fp:", r2.status_code)
try:
    fp = pd.DataFrame(r2.json())
    fp.to_csv(OD + "fink_fp_raw.csv", index=False)
    print("fp cols:", sorted(fp.columns.tolist()))
    print("n fp:", len(fp))
except Exception as e:
    print("fp parse fail", r2.text[:200])
