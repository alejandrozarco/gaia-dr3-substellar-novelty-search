import warnings; warnings.filterwarnings('ignore')
import urllib.request, urllib.parse, json, csv, io, numpy as np, time, sys
from astroquery.jplhorizons import Horizons
import collections

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

att=json.load(open("attributable_footprints.json"))
decam=[x for x in att if x["tel"]=="CTIO-4m/DECam"]
nights=collections.defaultdict(list)
for x in decam: nights[int(x["mjd"])].append(x)
ranked=sorted(nights.items(), key=lambda kv: min(f["smaa"] for f in kv[1]))
target_nights=[m for m,_ in ranked[:14]]

jds=[nights[m][0]["jd"] for m in target_nights]
obj=Horizons(id='2001 QT322', location='W84', epochs=jds)
eph=obj.ephemerides(quantities='1,3,9,36,37')
predn={}
for i,mjd in enumerate(target_nights):
    row=eph[i]
    predn[mjd]={"ra":float(row['RA']),"dec":float(row['DEC']),"V":float(row['V']),
                "smaa":float(row['SMAA_3sigma']),"smia":float(row['SMIA_3sigma']),
                "rra":float(row['RA_rate']),"rdec":float(row['DEC_rate'])}
time.sleep(1.1)

results={}; log=[]
for mjd in target_nights:
    p=predn[mjd]; dr=max(3*p["smaa"]/3600.0,0.006)
    try:
        dets=nsc_box(p["ra"],p["dec"],dr,mjd-0.6,mjd+0.6)
    except Exception as e:
        log.append(f"MJD{mjd}: FAILED {str(e)[:50]}"); continue
    time.sleep(1.0)
    if dets is None: log.append(f"MJD{mjd}: query err"); continue
    inb=[]
    for d in dets:
        rr=float(d["ra"]); dd=float(d["dec"])
        dra=(rr-p["ra"])*3600*np.cos(np.radians(p["dec"])); ddec=(dd-p["dec"])*3600
        sep=np.hypot(dra,ddec)
        if sep<3*p["smaa"]:
            inb.append({"mjd":float(d["mjd"]),"ra":rr,"dec":dd,"filter":d["filter"],"mag":float(d["mag_auto"]),
                        "sep":round(sep,2),"dra":round(dra,2),"ddec":round(ddec,2)})
    # motion test
    motion_ok=False; best_resid=None
    for a in inb:
        for b in inb:
            dt=(b["mjd"]-a["mjd"])*24
            if dt<=0.01: continue
            odra=(b["ra"]-a["ra"])*3600*np.cos(np.radians(p["dec"])); oddec=(b["dec"]-a["dec"])*3600
            resid=np.hypot(odra-p["rra"]*dt, oddec-p["rdec"]*dt)
            if best_resid is None or resid<best_resid: best_resid=resid
            if resid<1.5: motion_ok=True
    results[mjd]={"pred":p,"ndet":len(dets),"inb":inb,"motion_ok":motion_ok,"best_resid":best_resid}
    log.append(f"MJD{mjd}: V={p['V']:.2f} SMAA={p['smaa']:.2f}\" ndet={len(dets)} n_in3sig={len(inb)} motion_ok={motion_ok} best_resid={None if best_resid is None else round(best_resid,2)}")

json.dump(results, open("nsc_decam_results.json","w"), default=str)
open("nsc_search.log","w").write("\n".join(log))
print("DONE\n"+"\n".join(log))
