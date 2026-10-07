"""SkyBoT (I41, 20" cone) at the first positive detection of each night for stationary screen1 objects (2026-10-07).
Name-safe parse (separation = 5th field from right). Positive control first: a fast mover from screen1. Output: skybot_all2.csv"""
import pandas as pd, numpy as np, requests, time
from concurrent.futures import ThreadPoolExecutor
S=pd.read_csv("screen1.csv"); S=S[(S.rms_as<0.6)&(S.rate_ash<0.3)&(S.span_h>0.5)]
D=pd.read_csv("dets_all.csv"); D=D[D.isdiffpos.astype(str).isin(["1","t","True"])]
U="https://ssp.imcce.fr/webservices/skybot/api/conesearch.php"
def sb(ep,ra,de):
    for k in range(3):
        try:
            q=requests.get(U,params={"-ep":ep+2400000.5,"-ra":ra,"-dec":de,"-rd":20/3600,"-mime":"text","-output":"basic","-loc":"I41","-filter":"0","-objFilter":"111","-refsys":"EQJ2000","-from":"hobby"},timeout=120); x=q.text
            if q.status_code==204: return (np.inf,"none204")
            if "# Flag: 1" in x:
                L=[l.split("|") for l in x.splitlines() if l and not l.startswith("#")]; return min((float(f[-5]),"|".join(f[1:-10]).strip()) for f in L)
            if "# Flag: 0" in x: return (np.inf,"none")
        except Exception: pass
        time.sleep(5)
    return (np.nan,"HOLE")
def per(o):
    d=D[D.oid==o].sort_values("mjd"); nn=d.groupby(np.floor(d.mjd)).head(1)
    return o,"; ".join(f"{r.mjd:.2f}:{s[1]}@{s[0]}" for r in nn.itertuples() for s in [sb(r.mjd,r.ra,r.dec)])
F=pd.read_csv("screen1.csv").sort_values("rate_ash"); c=F[(F.rate_ash>5)&(F.rate_ash<60)].iloc[0]
print("control",c.oid,c.rate_ash,per(c.oid),flush=True)
with ThreadPoolExecutor(4) as ex: R=dict(ex.map(per,S.oid))
S["skybot"]=S.oid.map(R); S.to_csv("skybot_all2.csv",index=False); print(S[["oid","skybot"]].to_string())
