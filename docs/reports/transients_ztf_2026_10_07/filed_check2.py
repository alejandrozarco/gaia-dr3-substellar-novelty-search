"""Re-brightening/classification check of all 14 filed ZTF objects since MJD 61318 (2026-10-05). Output: filed_check.txt"""
import requests, pandas as pd, time
A="https://api.alerce.online/ztf/v1"; F={1:"g",2:"r",3:"i"}; out=[]
ids="absimmf abwacec abtpoev abwqsgt abtoqyd abycxez abyalli abxpksn abxwnlk abxwpty abzajhy abzlyby abygbnu abzbudn".split()
def g(u):
    for k in range(4):
        try:
            r=requests.get(u,timeout=60)
            if r.ok: return r.json()
        except Exception: pass
        time.sleep(5)
for i in ids:
    o="ZTF26"+i; ob=g(f"{A}/objects/{o}"); d=g(f"{A}/objects/{o}/detections"); n=g(f"{A}/objects/{o}/non_detections")
    if ob is None or d is None: out.append(o+" HOLE"); continue
    d=pd.DataFrame(d).sort_values("mjd"); d=d[d.isdiffpos.astype(str).isin(["1","t","True"])]; rec=d[d.mjd>=61318]
    n=pd.DataFrame(n) if n else pd.DataFrame(columns=["mjd","fid","diffmaglim"]); ln=n[n.mjd>=61318].sort_values("mjd")
    s=f"{o} ra {ob['meanra']:.5f} dec {ob['meandec']:.5f} ndet {len(d)} peak {d.magpsf.min():.2f} last det MJD {d.mjd.max():.2f} {F[int(d.iloc[-1].fid)]} {d.iloc[-1].magpsf:.2f}; dets>=61318: "+"; ".join(f"{r.mjd:.2f}{F[int(r.fid)]}{r.magpsf:.2f}" for r in rec.itertuples())
    s+=" | nondets>=61318: "+(" ".join(f"{r.mjd:.2f}{F[int(r.fid)]}>{r.diffmaglim:.1f}" for r in ln.itertuples()) or "none")
    out.append(s); print(s,flush=True)
open("filed_check.txt","w").write("\n".join(out)+"\n")
