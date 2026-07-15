import requests, io, pandas as pd, numpy as np
RA, DEC = 313.22651, -14.84044
OD = "/tmp/rubin_pilot/forensics/170591507978387512/"

# mean object table within 10"
r = requests.get("https://catalogs.mast.stsci.edu/api/v0.1/panstarrs/dr2/mean.csv",
    params={"ra": RA, "dec": DEC, "radius": 10/3600.0,
            "columns": "objID,raMean,decMean,nDetections,ng,nr,ni,nz,ny,gMeanPSFMag,rMeanPSFMag,iMeanPSFMag,zMeanPSFMag,yMeanPSFMag,qualityFlag",
            "pagesize": 100}, timeout=120)
print("PS1 mean:", r.status_code)
if r.status_code==200 and r.text.strip():
    pm = pd.read_csv(io.StringIO(r.text)); pm.to_csv(OD+"ps1_mean.csv", index=False)
    pm["sep_as"] = np.hypot((pm.raMean-RA)*np.cos(np.radians(DEC)), pm.decMean-DEC)*3600
    print(pm.sort_values("sep_as").to_string(index=False))
else:
    print("no mean rows")

# ALL detections within 15" -> noise floor census
r2 = requests.get("https://catalogs.mast.stsci.edu/api/v0.1/panstarrs/dr2/detection.csv",
    params={"ra": RA, "dec": DEC, "radius": 15/3600.0,
            "columns": "obsTime,filterID,psfFlux,psfFluxErr,psfQfPerfect,infoFlag,infoFlag2,infoFlag3,ra,dec",
            "pagesize": 2000}, timeout=180)
if r2.status_code==200 and r2.text.strip():
    det = pd.read_csv(io.StringIO(r2.text)); det.to_csv(OD+"ps1_det15.csv", index=False)
    det["sep_as"] = np.hypot((det.ra-RA)*np.cos(np.radians(DEC)), det.dec-DEC)*3600
    det["mag"] = -2.5*np.log10(det.psfFlux/3631.0)
    print("n detections within 15\":", len(det))
    print(det.sort_values("sep_as")[["obsTime","filterID","mag","psfQfPerfect","sep_as","infoFlag"]].head(30).to_string(index=False))
else:
    print("det15 err")
