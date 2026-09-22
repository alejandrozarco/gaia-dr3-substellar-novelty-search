import warnings,pickle,math; warnings.filterwarnings("ignore")
import numpy as np, lightkurve as lk
from astropy.coordinates import SkyCoord
from scipy.optimize import least_squares
P,t,f,e=pickle.load(open("fold.pkl","rb"))
# ---- ephemeris: phase of the deeper minimum ----
nb=400; ph=((t-t[0])/P)%1.0
prof=np.array([np.median(f[(ph>=k/nb)&(ph<(k+1)/nb)]) for k in range(nb)])
T0=t[0]+(np.argmin(prof)+0.5)/nb*P
print(f"ephemeris: P = {P:.6f} d, T0(primary) = BTJD {T0:.5f}")
# ================= TEST 1: difference-image centroid (S76 + S77, 158 s FFI cutouts) =================
c=SkyCoord(223.46949,49.94663,unit="deg")
offs=[]
for sec in (76,77):
    tpf=lk.search_tesscut(c,sector=sec)[0].download(cutout_size=13)
    fl=tpf.flux.value; tt=tpf.time.value; ok=np.isfinite(fl).all(axis=(1,2))&np.isfinite(tt); fl,tt=fl[ok],tt[ok]
    phs=((tt-T0)/P)%1.0
    ine=(np.abs(((phs+0.5)%1)-0.5)<0.018)|(np.abs(phs-0.5)<0.018)
    oot=(np.abs(phs-0.25)<0.06)|(np.abs(phs-0.75)<0.06)
    Iin,Iout=np.nanmean(fl[ine],axis=0),np.nanmean(fl[oot],axis=0)
    D=Iout-Iin
    xw,yw=[float(v) for v in tpf.wcs.world_to_pixel(c)]
    def cen(img,x0,y0,r=2.5):
        yy,xx=np.mgrid[0:img.shape[0],0:img.shape[1]]; m=np.hypot(xx-x0,yy-y0)<=r
        w=np.clip(img-np.nanmedian(img),0,None)*m; return (w*xx).sum()/w.sum(),(w*yy).sum()/w.sum()
    cx_o,cy_o=cen(Iout,xw,yw); cx_d,cy_d=cen(D,xw,yw)
    # bootstrap the difference-image centroid over cadences
    rng=np.random.default_rng(sec); bx=[]
    iin,iout=np.where(ine)[0],np.where(oot)[0]
    for _ in range(300):
        Db=np.nanmean(fl[rng.choice(iout,len(iout))],axis=0)-np.nanmean(fl[rng.choice(iin,len(iin))],axis=0)
        bx.append(cen(Db,xw,yw))
    bx=np.array(bx); sx,sy=bx.std(axis=0)
    dpx=math.hypot(cx_d-cx_o,cy_d-cy_o)
    print(f"S{sec}: {ine.sum()} in-eclipse / {oot.sum()} out-of-eclipse cadences; eclipse depth in difference image "
          f"{D[int(round(yw)),int(round(xw))]/Iout[int(round(yw)),int(round(xw))]*100:.2f}% at the target pixel")
    print(f"     difference-image centroid vs target centroid: offset {dpx:.3f} px = {dpx*21:.1f}in "
          f"(bootstrap 1-sigma {math.hypot(sx,sy):.3f} px = {math.hypot(sx,sy)*21:.1f}in)  -> {dpx/max(math.hypot(sx,sy),1e-6):.1f} sigma")
    offs.append(dpx*21)
# ================= TEST 2: eclipse geometry (trapezoid fit to the fold) =================
phc=((t-T0)/P+0.5)%1.0-0.5
def trap(p,x,c0):
    d,T14,T23,c=p; x=np.abs(x-c); h14,h23=T14/2,max(T23,1e-4)/2
    y=np.zeros_like(x); y[x<=h23]=d; m=(x>h23)&(x<h14)
    if h14>h23: y[m]=d*(h14-x[m])/(h14-h23)
    return 1-y
geo={}
for lab,c0 in (("primary",0.0),("secondary",0.5)):
    x=((phc-c0+0.5)%1)-0.5; m=np.abs(x)<0.15
    # local normalisation to the adjacent out-of-eclipse level
    base=np.median(f[m][np.abs(x[m])>0.09])
    r=least_squares(lambda p:(trap(p,x[m],0)-f[m]/base)/e[m],[0.03,0.10,0.02,0.0],bounds=([0,0.01,0,-0.02],[0.2,0.3,0.25,0.02]))
    d,T14,T23,cc=r.x; geo[lab]=(d,T14,T23)
    print(f"{lab:9s}: depth {d*100:.2f}%  T14 = {T14:.4f} phase = {T14*P*24:.2f} h   T23 = {T23:.4f} phase  (flat bottom {'YES' if T23>0.2*T14 else 'no - V/U-shaped'})")
T14=np.mean([geo[k][1] for k in geo])
for Mp in (1.0,1.2,1.4):
    a=(Mp*(P/365.25)**2)**(1/3)*215.03
    print(f"   if M_pair = {Mp} Msun: a = {a:.2f} Rsun;  (R1+R2) >= pi*a*T14 = {math.pi*a*T14:.2f} Rsun (edge-on) -> each ~{math.pi*a*T14/2:.2f} Rsun")
pickle.dump((P,T0),open("eph.pkl","wb"))
