import warnings,sys,math,pickle; warnings.filterwarnings("ignore"); sys.path.insert(0,"/tmp")
import numpy as np, subprocess, urllib.parse
from astropy.io import fits
from astropy.wcs import WCS
from astropy.stats import sigma_clipped_stats
from scipy import ndimage
from astropy.time import Time
from kk76_hz import hz
IR=["ib2k52czq_flt","ib2k52d0q_flt","ib2k52d2q_flt","ib2k52d3q_flt"]
cats=[]; tm=[]
for fr in IR:
    h=fits.open(fr+".fits"); p=h[0].header; w=WCS(h["SCI",1].header,h)
    d=h["SCI",1].data.astype(float); dq=h["DQ",1].data
    good=(dq&(4|16|32|256|512))==0
    _,med,sd=sigma_clipped_stats(d[good],sigma=3)
    sm=ndimage.gaussian_filter(np.where(good,d,med)-med,1.0); _,_,sds=sigma_clipped_stats(sm,sigma=3)
    lab,n=ndimage.label(sm>6*sds)
    rows=[]
    for k in range(1,n+1):
        yy,xx=np.where(lab==k)
        if len(yy)<3 or len(yy)>400: continue
        wt=sm[yy,xx]; cx=(xx*wt).sum()/wt.sum(); cy=(yy*wt).sum()/wt.sum()
        if cx<8 or cy<8 or cx>1005 or cy>1005: continue
        ra,de=[float(v) for v in w.pixel_to_world_values(cx,cy)]
        rows.append((ra,de,sm[yy,xx].max()/sds))
    cats.append(np.array(rows)); tm.append((p["EXPSTART"]+p["EXPEND"])/2)
    print(f"{fr} {p['FILTER']}: {len(rows)} sources >6 sigma")
# predicted motion vector (arcsec on sky) over the IR sequence, from the refined orbit
jd=[Time(t,format="mjd",scale="utc").jd for t in tm]
pr=hz([f"{j:.6f}" for j in jd])
ra0,de0=pr[0][1],pr[0][2]; cd=math.cos(math.radians(de0))
pv=[((r-ra0)*cd*3600,(d-de0)*3600) for _,r,d in pr]
print("predicted offsets along the IR sequence (arcsec):",[f"({a:+.3f},{b:+.3f})" for a,b in pv])
# match: for each source in frame 0, find partners in frames 1..3 near (pos + predicted offset) and require them NOT static
def near(cat,ra,de,tol):
    dd=np.hypot((cat[:,0]-ra)*cd*3600,(cat[:,1]-de)*3600); j=np.argmin(dd); return (j,dd[j]) if dd[j]<tol else (None,dd[j])
movers=[]
for i,(ra,de,s) in enumerate(cats[0]):
    ok=True; recs=[(ra,de,s)]; static_hits=0
    for k in (1,2,3):
        exp_ra=ra+pv[k][0]/3600/cd; exp_de=de+pv[k][1]/3600
        j,dist=near(cats[k],exp_ra,exp_de,0.12)          # moved as predicted, within 0.12"
        js,dists=near(cats[k],ra,de,0.06)                  # still at the ORIGINAL spot?
        if js is not None: static_hits+=1
        if j is None: ok=False; break
        recs.append(tuple(cats[k][j]))
    if ok and static_hits<=1: movers.append((recs,s))
print(f"\nsources in frame 0 that MOVE with the predicted vector through all 4 IR frames (and are not static): {len(movers)}")
for recs,s in movers[:10]:
    r0=recs[0]; off=((r0[0]-ra0)*cd*3600,(r0[1]-de0)*3600)
    print(f"   start RA/Dec ({r0[0]:.6f},{r0[1]:+.6f})  S/N~{s:.0f}  offset from refined-orbit prediction ({off[0]:+.1f},{off[1]:+.1f})in = {math.hypot(*off):.1f}in")
# JPL arc-only orbit prediction for comparison
u=("https://ssd.jpl.nasa.gov/api/horizons.api?format=text&COMMAND='88268;'&OBJ_DATA=NO&MAKE_EPHEM=YES&EPHEM_TYPE=OBSERVER"
   f"&CENTER='500@-48'&TLIST='{jd[0]:.6f}'&TLIST_TYPE=JD&QUANTITIES='1'&ANG_FORMAT=DEG&EXTRA_PREC=YES&CSV_FORMAT=YES")
o=subprocess.run(["curl","-sL","--max-time","90",u],capture_output=True,text=True).stdout
if "$$SOE" in o:
    f=[x.strip() for x in o.split("$$SOE")[1].split("$$EOE")[0].strip().split(",")]
    jr,jdd=float(f[3]),float(f[4])
    print(f"\nJPL (current MPC orbit) prediction at IR frame 0: ({jr:.6f},{jdd:+.6f}) -> {(jr-ra0)*cd*3600:+.1f},{(jdd-de0)*3600:+.1f}in from ours")
pickle.dump((cats,tm,pv,movers),open("irmove.pkl","wb"))
