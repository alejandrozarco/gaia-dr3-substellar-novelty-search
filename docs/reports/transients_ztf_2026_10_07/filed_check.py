"""Re-brightening check of our 11 filed objects (2026-10-05): ALeRCE detections since MJD 61313 for the 10 ZTF ids, and an
ALeRCE 3-arcsec cone at AT 2026adjg (Rubin object). Output: filed_check.txt"""
import requests, pandas as pd
A="https://api.alerce.online/ztf/v1"; F={1:"g",2:"r",3:"i"}
ids="absimmf abwacec abtpoev abwqsgt abtoqyd abycxez abyalli abxpksn abxwnlk abxwpty".split(); out=[]
for i in ids:
    o="ZTF26"+i; ob=requests.get(f"{A}/objects/{o}",timeout=60).json(); d=pd.DataFrame(requests.get(f"{A}/objects/{o}/detections",timeout=60).json()).sort_values("mjd")
    n=pd.DataFrame(requests.get(f"{A}/objects/{o}/non_detections",timeout=60).json())
    d=d[d.isdiffpos.astype(str).isin(["1","t","True"])]; pk=d.magpsf.min(); rec=d[d.mjd>=61313]
    ln = n[n.mjd>=61313].sort_values("mjd") if len(n) else n
    s=f"{o} ra {ob['meanra']:.5f} dec {ob['meandec']:.5f} ndet {len(d)} peak {pk:.2f} last det MJD {d.mjd.max():.2f} {F[int(d.iloc[-1].fid)]} {d.iloc[-1].magpsf:.2f}; dets since 61313: "+"; ".join(f"{r.mjd:.2f}{F[int(r.fid)]}{r.magpsf:.2f}" for r in rec.itertuples())
    s+= " | nondets since 61313: "+(" ".join(f"{r.mjd:.2f}{F[int(r.fid)]}>{r.diffmaglim:.1f}" for r in ln.itertuples()) if len(ln) else "none")
    out.append(s); print(s,flush=True)
c=requests.get(f"{A}/objects",params=dict(ra=332.391258,dec=-14.869900,radius=3,page_size=20),timeout=60).json()
s="AT2026adjg cone 3as: "+str([(x['oid'],x['firstmjd'],x['lastmjd'],x['ndet']) for x in c.get('items',[])]); out.append(s); print(s)
open("filed_check.txt","w").write("\n".join(out)+"\n")
