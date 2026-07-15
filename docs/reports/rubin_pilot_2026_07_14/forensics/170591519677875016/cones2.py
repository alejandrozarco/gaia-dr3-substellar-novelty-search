import requests, json
RA, DEC = 306.74802, -11.81856
out = {}
# PS1 DR2 mean objects within 10"
try:
    r = requests.get("https://catalogs.mast.stsci.edu/api/v0.1/panstarrs/dr2/mean.csv",
        params={"ra": RA, "dec": DEC, "radius": 0.002778,
                "columns": "objID,raMean,decMean,nDetections,gMeanPSFMag,rMeanPSFMag,iMeanPSFMag,zMeanPSFMag,yMeanPSFMag,iMeanPSFMagStd,ng,nr,ni,nz,ny"},
        timeout=90)
    print("--- PS1 mean [", r.status_code, "] ---"); print(r.text[:3000])
    out["ps1_mean"] = {"status": r.status_code, "csv": r.text[:20000]}
except Exception as e:
    print("PS1 failed:", e); out["ps1_mean"]={"error":str(e)}

# IRSA: CatWISE2020 within 15"
for cat, name in [("catwise_2020","catwise"), ("unwise_2019","unwise")]:
    try:
        r = requests.get("https://irsa.ipac.caltech.edu/TAP/sync",
            params={"QUERY": f"SELECT * FROM {cat} WHERE CONTAINS(POINT('ICRS',ra,dec),CIRCLE('ICRS',{RA},{DEC},0.004167))=1",
                    "FORMAT":"CSV"}, timeout=120)
        txt = r.text
        print(f"--- {name} [{r.status_code}] ---")
        lines = txt.splitlines()
        print("\n".join(lines[:1]))
        print(f"nrows={max(0,len(lines)-1)}")
        out[name] = {"status": r.status_code, "csv": txt[:30000]}
    except Exception as e:
        print(f"{name} failed:", e); out[name]={"error":str(e)}
json.dump(out, open("/tmp/rubin_pilot/forensics/170591519677875016/cones2.json","w"), indent=1)
