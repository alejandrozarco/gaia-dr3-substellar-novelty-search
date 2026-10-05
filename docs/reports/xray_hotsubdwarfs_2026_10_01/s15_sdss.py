# SDSS DR20 spAll cone (3") for the 39 gate survivors; probe RR Pic must return a spectrum.
import requests, io, numpy as np, pandas as pd
from astropy.table import Table
U='https://skyserver.sdss.org/dr20/SkyServerWS/SearchTools/SqlSearch'
def q(s):
    r=requests.get(U,params={'cmd':s,'format':'csv'},timeout=180); r.raise_for_status()
    txt=r.text.split('\n',1)[1] if r.text.startswith('#Table') else r.text
    return pd.read_csv(io.StringIO(txt)) if txt.strip() else pd.DataFrame()
pr=q("SELECT s.specobjid FROM fGetNearbySpAllEq(98.9003,-62.6401,0.05) n JOIN spAll s ON s.specobjid=n.specobjid"); print('probe RR Pic rows',len(pr)); assert len(pr)>0
M=Table.read('s07_props.ecsv'); S=M[~M['known_cv'].astype(bool)]
rows=[]
for r in S:
    d=q(f"SELECT n.distance, s.specobjid, s.field, s.mjd, s.catalogid, s.class, s.subclass, s.sn_median_all, s.xcsao_rv, s.programname, s.firstcarton FROM fGetNearbySpAllEq({float(r['ra_1'])},{float(r['dec_1'])},0.05) n JOIN spAll s ON s.specobjid=n.specobjid")
    print(r['GaiaEDR3'], len(d), d[['field','mjd','class','subclass','sn_median_all','firstcarton']].to_string(index=False,header=False) if len(d) else '', flush=True)
    for _,x in d.iterrows(): rows.append(dict(gid=int(r['GaiaEDR3']),**{k:str(v) for k,v in x.items()}))
pd.DataFrame(rows).to_csv('sdss/s15_dr20_spall.csv',index=False)
