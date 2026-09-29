"""Vet outburst candidates (cand_repeat.csv + cand_single.csv): Gaia Alerts (3 arcsec), CRTS CVs (Drake+2014 J/MNRAS/441/1186),
Coppejans outburst catalogue (J/MNRAS/456/4441), Gaia DR3 variability class, and a TNS cone (10 arcsec, one request per 3 s; a failed
request is recorded as HOLE). Adds Gaia HR position. Output: vetted.csv."""
import pandas as pd, numpy as np, time, io, requests
from astropy.table import Table
import astropy.units as u
from astroquery.xmatch import XMatch
C = pd.concat([pd.read_csv("cand_repeat.csv").assign(kind="repeat"), pd.read_csv("cand_single.csv").assign(kind="single")]).reset_index(drop=True)
C["key"] = np.arange(len(C)); T = Table.from_pandas(C[["key", "meanra", "meandec"]])
def xm(cat, r):
    try:
        x = XMatch.query(cat1=T, cat2=cat, max_distance=r * u.arcsec, colRA1="meanra", colDec1="meandec").to_pandas().sort_values("angDist").drop_duplicates("key")
        x["key"] = x.key.astype(int); return x.set_index("key")
    except Exception as e: print("HOLE", cat, type(e).__name__); return None
for tag, cat in (("crts", "vizier:J/MNRAS/441/1186/table1"), ("coppejans", "vizier:J/MNRAS/456/4441/catalog"), ("vclass", "vizier:I/358/vclassre")):
    x = xm(cat, 3)
    if x is None: C[f"in_{tag}"] = "HOLE"; continue
    C[f"in_{tag}"] = C.key.isin(x.index)
    if tag == "vclass": C["gaia_vclass"] = x.Class.reindex(C.key).values if "Class" in x else np.nan
A = pd.read_csv("gaia_alerts.csv"); A.columns = [c.strip().lstrip("#") for c in A.columns]
ra, de = A.RaDeg.values, A.DecDeg.values; ga = []
for r in C.itertuples():
    d = np.hypot((ra - r.meanra) * np.cos(np.radians(r.meandec)), de - r.meandec) * 3600; k = d.argmin()
    ga.append(f"{A.Name.iloc[k]} {A.Class.iloc[k]} {str(A.Comment.iloc[k])[:60]}" if d[k] < 3 else "")
C["gaia_alert"] = ga
import os
tn = []
if os.environ.get("SKIP_TNS"): tn = ["NOT_RUN"] * len(C)
else:
    for r in C.itertuples():
        res = "HOLE"
        for a in range(4):
            try:
                q = requests.get("https://www.wis-tns.org/search", params=dict(ra=r.meanra, decl=r.meandec, radius=10, coords_unit="arcsec", format="csv"), headers={"User-Agent": "Mozilla/5.0 (literature check)"}, timeout=60)
                if q.status_code == 429: time.sleep(300); continue
                if q.ok and q.text.startswith('"ID"'):
                    d = pd.read_csv(io.StringIO(q.text)); res = "; ".join(f"{x.Name} {x['Obj. Type']}" for _, x in d.iterrows()); break
            except Exception: time.sleep(30)
        tn.append(res); time.sleep(20)
C["tns"] = tn
C.to_csv("vetted.csv", index=False)
print(len(C), "candidates;", "Gaia alert:", (C.gaia_alert != "").sum(), "TNS:", ((C.tns != "") & (C.tns != "HOLE")).sum(), "TNS holes:", (C.tns == "HOLE").sum(),
      "CRTS:", (C.in_crts == True).sum(), "Coppejans:", (C.in_coppejans == True).sum())
