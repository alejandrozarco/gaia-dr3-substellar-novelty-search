"""ALeRCE science/template/difference PNG stamps (avro.alerce.online/get_stamp) for the first and last stamp-bearing detection
of each candidate (2026-10-05); downloads threaded, composition with PIL only (pyplot is not thread-safe). Failed stamps = grey
HOLE tile. Output: stamps/<oid>.png (rows = first/last epoch; cols sci/ref/diff, label strip on top)"""
import sys, requests, io, time, pandas as pd
from PIL import Image, ImageDraw
from concurrent.futures import ThreadPoolExecutor
def get(url,p):
    for k in range(4):
        try:
            r=requests.get(url,params=p,timeout=90)
            if r.ok: return r
        except Exception: pass
        time.sleep(5*(k+1))
def one(o):
    d=pd.DataFrame(get(f"https://api.alerce.online/ztf/v1/objects/{o}/detections",None).json()).sort_values("mjd"); d=d[d.has_stamp==True]
    E=list((d.iloc[[0,-1]] if len(d)>1 else d).itertuples()); S=126; M=Image.new("RGB",(3*S,len(E)*(S+14)),"white"); D=ImageDraw.Draw(M); hole=0
    for i,c in enumerate(E):
        D.text((2,i*(S+14)),f"{o[5:]} MJD{c.mjd:.2f} f{c.fid} {c.magpsf:.2f}",fill="black")
        for j,t in enumerate(("science","template","difference")):
            r=get("https://avro.alerce.online/get_stamp",dict(oid=o,candid=str(c.candid),type=t,format="png"))
            if r is not None and "image" in r.headers.get("content-type",""): im=Image.open(io.BytesIO(r.content)).convert("RGB").resize((S-4,S-4))
            else: im=Image.new("RGB",(S-4,S-4),"grey"); hole+=1
            M.paste(im,(j*S+2,i*(S+14)+14))
    M.save(f"stamps/{o}.png"); return o,hole
with ThreadPoolExecutor(4) as ex:
    for o,h in ex.map(one,sys.argv[1:]): print(o,"holes",h,flush=True)
