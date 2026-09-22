import warnings; warnings.filterwarnings("ignore")
import numpy as np, json, subprocess, urllib.parse, csv, io, math, time
from astropy.timeseries import LombScargle
RA,DEC=223.46949,49.94663
q=(f"SELECT source_id,ra,dec,phot_g_mean_mag,bp_rp,DISTANCE(POINT('ICRS',ra,dec),POINT('ICRS',{RA},{DEC}))*3600 AS sep "
   f"FROM gaiadr3.gaia_source WHERE 1=CONTAINS(POINT('ICRS',ra,dec),CIRCLE('ICRS',{RA},{DEC},63./3600.)) ORDER BY phot_g_mean_mag")
u="https://gea.esac.esa.int/tap-server/tap/sync?REQUEST=doQuery&LANG=ADQL&FORMAT=json&QUERY="+urllib.parse.quote(q)
g=json.loads(subprocess.run(["curl","-sL","--max-time","90",u],capture_output=True,text=True).stdout)["data"]
print(f"{len(g)} Gaia sources within 63in (3 TESS pixels) of TYC 3477-27-1\n")
def ztf(ra,dec):
    uu=("https://irsa.ipac.caltech.edu/cgi-bin/ZTF/nph_light_curves?"
        f"POS=CIRCLE%20{ra:.6f}%20{dec:.6f}%20{3/3600:.6f}&BAD_CATFLAGS_MASK=32768&FORMAT=CSV")
    for k in range(4):
        p=subprocess.run(["curl","-sL","--max-time","120",uu],capture_output=True,text=True)
        if p.returncode==0 and "oid" in p.stdout:
            rows=list(csv.DictReader(io.StringIO(p.stdout))); cd=math.cos(math.radians(dec))
            return [r for r in rows if math.hypot((float(r["ra"])-ra)*cd,float(r["dec"])-dec)*3600<2.0]
        time.sleep(3*(k+1))
    return None
P2,P1=0.33880,0.67759
print(f"{'sep':>6} {'G':>6} {'BP-RP':>6}  {'band':4} {'n':>5}  {'best P (d)':>11} {'pw':>6}  {'pw@0.3388':>9} {'amp@0.3388 (mag)':>16}")
for sid,ra,dec,G,br,sep in g:
    if G is None or G>20.5: continue
    rows=ztf(ra,dec); time.sleep(0.5)
    if rows is None: print(f"{sep:6.1f} {G:6.2f}  ZTF QUERY_FAILED"); continue
    best=None
    for b in ("zr","zg"):
        v=[r for r in rows if r["filtercode"]==b and r["catflags"]=="0"]
        if len(v)<60: continue
        t=np.array([float(r["mjd"]) for r in v]); m=np.array([float(r["mag"]) for r in v]); e=np.array([float(r["magerr"]) for r in v])
        fr=np.linspace(1/5.0,1/0.1,40000); ls=LombScargle(t,m,e); pw=ls.power(fr)
        k=np.argmin(abs(fr-1/P2)); pwP=pw[max(0,k-8):k+8].max()
        mdl=ls.model(np.linspace(0,P2,200)+t[0],1/P2); amp=(mdl.max()-mdl.min())/2
        rec=(b,len(v),1/fr[np.argmax(pw)],pw.max(),pwP,amp)
        if best is None or rec[4]>best[4]: best=rec
    if best is None: print(f"{sep:6.1f} {G:6.2f} {br if br else float('nan'):6.2f}  -- <60 clean ZTF epochs ({len(rows)} rows; target near ZTF saturation if G<~12.5)"); continue
    b,n,pb,pwmax,pwP,amp=best
    flag="  <<< CARRIES THE 0.3388-d SIGNAL" if pwP>0.2 else ""
    print(f"{sep:6.1f} {G:6.2f} {br if br else float('nan'):6.2f}  {b:4} {n:5d}  {pb:11.5f} {pwmax:6.3f}  {pwP:9.3f} {amp:16.3f}{flag}")
