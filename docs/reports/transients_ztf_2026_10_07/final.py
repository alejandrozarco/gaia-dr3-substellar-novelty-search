"""Final file-ready rows (2026-10-07) for TNS-unreported survivors: ALeRCE first/second positive detection, last non-detection before first, sexagesimal mean position; TNS check time from tns_check_main.csv. Output: final_table.txt"""
import requests, pandas as pd
from astropy.time import Time; from astropy.coordinates import SkyCoord; import astropy.units as u
A="https://api.alerce.online/ztf/v1"; F={1:"g",2:"r",3:"i"}; t=lambda m: Time(m,format="mjd").iso[:19]
T=pd.read_csv("tns_check_main.csv").set_index("oid")
out=[]
for o in "abznozb abzhizd abzwbww academn acaaglg abznrxy acaegqm acaddjo acaddnd".split():
    o="ZTF26"+o; ob=requests.get(f"{A}/objects/{o}",timeout=60).json(); d=pd.DataFrame(requests.get(f"{A}/objects/{o}/detections",timeout=60).json()).sort_values("mjd")
    n=pd.DataFrame(requests.get(f"{A}/objects/{o}/non_detections",timeout=60).json()); d=d[d.isdiffpos.astype(str).isin(["1","t","True"])]
    s=SkyCoord(ob["meanra"]*u.deg,ob["meandec"]*u.deg).to_string("hmsdms",sep=":",precision=2); a,b=d.iloc[0],d.iloc[1]
    ln=n[n.mjd<a.mjd].sort_values("mjd").iloc[-1] if len(n) and (n.mjd<a.mjd).any() else None
    out.append(f"{o} | {s} | {t(a.mjd)} ZTF-{F[int(a.fid)]} {a.magpsf:.2f}±{a.sigmapsf:.2f} | {t(b.mjd)} ZTF-{F[int(b.fid)]} {b.magpsf:.2f}±{b.sigmapsf:.2f} | "+(f"{t(ln.mjd)} ZTF-{F[int(ln.fid)]} >{ln.diffmaglim:.2f}" if ln is not None else "none in 30-d alert history")+f" | ndet {len(d)} last {t(d.mjd.max())[:16]} {F[int(d.iloc[-1].fid)]} {d.iloc[-1].magpsf:.2f} | TNS none {T.loc[o,'checked_utc']}")
open("final_table.txt","w").write("\n".join(out)+"\n"); print("\n".join(out))
