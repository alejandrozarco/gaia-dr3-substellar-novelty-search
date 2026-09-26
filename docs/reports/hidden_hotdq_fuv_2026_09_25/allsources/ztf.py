import requests, io, pandas as pd
ra,dec=312.82994747,-16.29705
url="https://irsa.ipac.caltech.edu/cgi-bin/ZTF/nph_light_curves"
for attempt in range(3):
    try:
        r=requests.get(url,params=dict(POS=f"CIRCLE {ra} {dec} 0.0006",BANDNAME="g,r,i",FORMAT="csv"),timeout=240)
        df=pd.read_csv(io.StringIO(r.text)); df.to_csv("ztf_J2051.csv",index=False)
        print("ZTF rows",len(df), df.groupby(["oid","filtercode"]).size().to_dict() if len(df) else ""); break
    except Exception as e: print("ZTF attempt",attempt,repr(e)[:150])
