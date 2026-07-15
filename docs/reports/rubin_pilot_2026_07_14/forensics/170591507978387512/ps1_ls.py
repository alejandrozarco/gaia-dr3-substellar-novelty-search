import requests, io, pandas as pd, numpy as np
RA, DEC = 313.22651, -14.84044
OD = "/tmp/rubin_pilot/forensics/170591507978387512/"

# PS1 DR2 stack objects within 10"
r = requests.get("https://catalogs.mast.stsci.edu/api/v0.1/panstarrs/dr2/stack.csv",
    params={"ra": RA, "dec": DEC, "radius": 10/3600.0,
            "columns": "objID,raStack,decStack,gPSFMag,rPSFMag,iPSFMag,zPSFMag,yPSFMag,iKronMag,primaryDetection",
            "pagesize": 50}, timeout=120)
print("PS1 stack:", r.status_code)
if r.status_code == 200 and len(r.text.strip()):
    ps = pd.read_csv(io.StringIO(r.text))
    ps.to_csv(OD+"ps1_stack.csv", index=False)
    print(ps.to_string(index=False))
else:
    print("no rows / err:", r.text[:200])

# PS1 DR2 detections (individual epochs) within 3"
r2 = requests.get("https://catalogs.mast.stsci.edu/api/v0.1/panstarrs/dr2/detection.csv",
    params={"ra": RA, "dec": DEC, "radius": 3/3600.0,
            "columns": "obsTime,filterID,psfFlux,psfFluxErr,infoFlag,raMean,decMean", "pagesize": 500}, timeout=120)
print("PS1 detections:", r2.status_code)
if r2.status_code == 200 and len(r2.text.strip()):
    pdet = pd.read_csv(io.StringIO(r2.text))
    pdet.to_csv(OD+"ps1_detections.csv", index=False)
    print("n det:", len(pdet))
    if len(pdet): print(pdet.head(20).to_string(index=False))
else:
    print("no rows / err:", r2.text[:200])
