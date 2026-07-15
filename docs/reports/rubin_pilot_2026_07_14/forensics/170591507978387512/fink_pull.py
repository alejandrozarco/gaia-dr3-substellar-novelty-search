import requests, json, pandas as pd
B = "https://api.lsst.fink-portal.org"
r = requests.post(B + "/api/v1/objects", json={"diaObjectId": "170591507978387512", "output-format": "json", "withupperlim": "True"}, timeout=90)
print("objects:", r.status_code)
d = r.json()
print("n rows:", len(d))
df = pd.DataFrame(d)
df.to_csv("/tmp/rubin_pilot/forensics/170591507978387512/fink_alert_raw.csv", index=False)
cols = sorted(df.columns.tolist())
print(json.dumps(cols))
# show key photometry columns
for c in ["i:midpointMjdTai","i:band","i:psfFlux","i:psfFluxErr","i:ra","i:dec","i:diaSourceId","d:tag"]:
    if c in df.columns: print(c, "OK")
