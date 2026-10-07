"""Survivors after SkyBoT first-epoch screen (2026-10-05): stationary (screen1 cls stat + stat_add) objects with no known asteroid
within 15" at the first epoch (or empty 0.3-deg cone), plus pair-only objects with no known asteroid. Then SkyBoT at EVERY
detection night (first det of each night; 20" cone; name-safe parse: d = 5th field from the right). Output: survivors.csv"""
import pandas as pd, numpy as np, requests, json, time
from concurrent.futures import ThreadPoolExecutor
S=pd.concat([pd.read_csv("screen1.csv"),pd.read_csv("stat_add.csv").assign(cls="stat")]).drop_duplicates("oid").set_index("oid")
K=pd.concat([pd.read_csv("skybot.csv"),pd.read_csv("skybot_add.csv")]); W=pd.concat([pd.read_csv("skybot_wide.csv"),pd.read_csv("skybot_wide_add.csv")])
bad=set(K[(K.n_known.astype(str)!="HOLE")].oid)|set(W[(W.status=="ok")&(W.nearest_as<15)].oid)|{"ZTF26abynkwf"}
hole=set(W[W.status=="HOLE"].oid)
cand=[o for o in S.index if S.loc[o,"cls"] in ("stat","pair") and o not in bad and (o in set(K.oid))]
J=json.load(open("fresh_all.json")); T={x["objectId"]:x["tns_name"] for x in J["tns"]}
D=pd.read_csv("dets_all.csv"); D=D[D.isdiffpos.astype(str).isin(["1","t","True"])]
U="https://ssp.imcce.fr/webservices/skybot/api/conesearch.php"
def sb(ep,ra,de):
    for k in range(3):
        try:
            x=requests.get(U,params={"-ep":ep+2400000.5,"-ra":ra,"-dec":de,"-rd":20/3600,"-mime":"text","-output":"basic","-loc":"I41","-filter":"0","-objFilter":"111","-refsys":"EQJ2000","-from":"hobby"},timeout=120).text
            if "# Flag: 1" in x:
                L=[l.split("|") for l in x.splitlines() if l and not l.startswith("#")]; return min((float(f[-5]),"|".join(f[1:-10]).strip()) for f in L)
            if "# Flag: 0" in x or x.strip()=="" : return (np.inf,"none")
        except Exception: pass
        time.sleep(5)
    return (np.nan,"HOLE")
def per(o):
    d=D[D.oid==o].sort_values("mjd"); nn=d.groupby(np.floor(d.mjd)).head(1); res=[]
    for r in nn.itertuples(): s=sb(r.mjd,r.ra,r.dec); res.append(f"{r.mjd:.2f}:{s[1]}@{s[0]}")
    return o,"; ".join(res)
with ThreadPoolExecutor(6) as ex: R=dict(ex.map(per,cand))
O=S.loc[cand].reset_index()[["oid","cls","ra","dec","npos","nights","span_h","sep_as","mag_first","fid_first","first","distnr_med","drb_med"]]
O["tns_lasair"]=O.oid.map(T); O["skybot_all_nights"]=O.oid.map(R); O["wide_hole"]=O.oid.isin(hole)
O.to_csv("survivors.csv",index=False); pd.set_option("display.width",250); print(O.drop(columns=["ra","dec"]).to_string())
