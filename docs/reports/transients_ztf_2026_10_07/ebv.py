"""IRSA DUST E(B-V) (SFD98 and SF11) per candidate; control: a high-extinction position (l=0,b=-5). Output: ebv.csv"""
import sys, pandas as pd
from astroquery.ipac.irsa.irsa_dust import IrsaDust; import astropy.coordinates as c, astropy.units as u
rows=[]
for a in ["control:270.9:-31.0"]+sys.argv[1:]:
    n,ra,de=a.split(":")
    try:
        t=IrsaDust.get_query_table(c.SkyCoord(float(ra)*u.deg,float(de)*u.deg),section="ebv")
        rows.append(dict(oid=n,ebv_sfd=float(t["ext SFD ref"][0]),ebv_sf11=float(t["ext SandF ref"][0])))
    except Exception as ex: rows.append(dict(oid=n,ebv_sfd="HOLE",ebv_sf11=repr(ex)[:80]))
    print(rows[-1],flush=True)
pd.DataFrame(rows).to_csv("ebv.csv",index=False)
