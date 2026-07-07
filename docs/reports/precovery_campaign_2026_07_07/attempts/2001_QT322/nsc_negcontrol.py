import warnings; warnings.filterwarnings('ignore')
import urllib.request, urllib.parse, json, csv, io, numpy as np, time
TAP="https://datalab.noirlab.edu/tap/sync"
def tap(q,retries=4):
    for k in range(retries):
        try:
            data=urllib.parse.urlencode({"REQUEST":"doQuery","LANG":"ADQL","FORMAT":"csv","QUERY":q}).encode()
            req=urllib.request.Request(TAP,data=data); r=urllib.request.urlopen(req,timeout=100); return r.read().decode()
        except Exception as e:
            if k==retries-1: raise
            time.sleep(4)
def nsc_box(ra,dec,dr,mjd_lo,mjd_hi):
    q=(f"SELECT ra,dec,mjd,mag_auto,filter FROM nsc_dr2.meas "
       f"WHERE ra BETWEEN {ra-dr/np.cos(np.radians(dec)):.5f} AND {ra+dr/np.cos(np.radians(dec)):.5f} "
       f"AND dec BETWEEN {dec-dr:.5f} AND {dec+dr:.5f} AND mjd BETWEEN {mjd_lo} AND {mjd_hi}")
    out=tap(q)
    if "ERROR" in out[:300]: return None
    rr=list(csv.reader(io.StringIO(out)))
    return [dict(zip(rr[0],row)) for row in rr[1:]]

res=json.load(open("nsc_decam_results.json"))
log=[]
real_total=0; ctrl_total=0
for mjd,d in sorted(res.items()):
    p=d["pred"]; dr=max(3*p["smaa"]/3600.0,0.006)
    nreal=len(d["inb"]); real_total+=nreal
    # control at +1 deg dec
    try:
        cd=nsc_box(p["ra"],p["dec"]+1.0,dr,float(mjd)-0.6,float(mjd)+0.6)
    except Exception as e:
        log.append(f"MJD{mjd}: ctrl FAILED {str(e)[:40]}"); continue
    time.sleep(1.0)
    if cd is None: log.append(f"MJD{mjd}: ctrl err"); continue
    nin=0
    for x in cd:
        rr=float(x["ra"]); dd=float(x["dec"])
        dra=(rr-p["ra"])*3600*np.cos(np.radians(p["dec"]+1.0)); ddec=(dd-(p["dec"]+1.0))*3600
        if np.hypot(dra,ddec)<3*p["smaa"]: nin+=1
    ctrl_total+=nin
    log.append(f"MJD{mjd}: real_in3sig={nreal}  control_in3sig={nin}")
log.append(f"TOTAL: real={real_total} control={ctrl_total}")
open("nsc_negcontrol.log","w").write("\n".join(log))
print("\n".join(log))
