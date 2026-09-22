import warnings,sys,math,pickle; warnings.filterwarnings("ignore"); sys.path.insert(0,"/tmp")
import numpy as np
from astropy.io import fits
from astropy.wcs import WCS
from scipy import ndimage
from astropy.stats import sigma_clipped_stats
R=pickle.load(open("look.pkl","rb"))
def load(fr):
    h=fits.open(fr+".fits"); s=h["SCI",1]; w=WCS(s.header,h); d=s.data.astype(float); dq=h["DQ",1].data
    d[(dq&(4|16|32|256|512))!=0]=np.nan; return d,w
peaks={}
for a,b,filt in (("ib2k52cvq_flc","ib2k52cxq_flc","F606W"),("ib2k52cwq_flc","ib2k52cyq_flc","F814W")):
    A,wa=load(a); B,wb=load(b); ny,nx=A.shape; yy,xx=np.mgrid[0:ny,0:nx]
    rr,dd=wa.pixel_to_world_values(xx,yy); bx,by=wb.world_to_pixel_values(rr,dd)
    valid=(bx>2)&(bx<nx-3)&(by>2)&(by<ny-3)
    Bi=ndimage.map_coordinates(np.nan_to_num(B,nan=np.nanmedian(B)),[by,bx],order=1,mode="constant",cval=np.nan)
    _,ma,_=sigma_clipped_stats(A[np.isfinite(A)]); _,mb,_=sigma_clipped_stats(Bi[np.isfinite(Bi)])
    D=np.where(valid,(A-ma)-(Bi-mb),0.0); Ds=ndimage.gaussian_filter(np.nan_to_num(D),1.5)
    _,_,sd=sigma_clipped_stats(Ds[valid],sigma=3)
    def find(sign):
        lab,n=ndimage.label(sign*Ds>5*sd); out=[]
        for k in range(1,n+1):
            y_,x_=np.where(lab==k)
            if len(y_)<6: continue      # smoothed PSF footprint; excludes single-pixel junk
            v=sign*Ds[y_,x_]; cx=(x_*v).sum()/v.sum(); cy=(y_*v).sum()/v.sum()
            elong=np.ptp(x_)+np.ptp(y_)
            out.append((cx,cy,v.max()/sd,len(y_),elong))
        return out
    pos,neg=find(+1),find(-1)
    x1,y1=R[a]["x"],R[a]["y"]; x2,y2=[float(v) for v in wa.world_to_pixel_values(R[b]["ra"],R[b]["de"])]
    vx,vy=x2-x1,y2-y1
    pairs=[]
    for p in pos:
        for q in neg:
            if math.hypot((q[0]-p[0])-vx,(q[1]-p[1])-vy)<3.0: pairs.append((p,q))
    peaks[filt]=(pos,neg,pairs,(vx,vy),wa)
    print(f"{filt}: {len(pos)} positive / {len(neg)} negative blobs >5sigma over the whole overlap; "
          f"pairs matching the predicted 1-hr motion vector ({vx:+.1f},{vy:+.1f}) px within 3 px: {len(pairs)}")
    for p,q in pairs[:6]:
        ra,de=[float(v) for v in wa.pixel_to_world_values(p[0],p[1])]
        print(f"     + ({p[0]:.1f},{p[1]:.1f}) S/N {p[2]:.1f} npix {p[3]} | - ({q[0]:.1f},{q[1]:.1f}) S/N {q[2]:.1f}  -> RA/Dec ({ra:.6f},{de:+.6f})  {math.hypot(p[0]-x1,p[1]-y1)*0.0396:.1f}in from refined prediction")
# cross-filter consistency: a real object appears as the SAME pair in both filters (positions within 3 px in world coords)
f6,f8=peaks["F606W"],peaks["F814W"]
both=[]
for p,q in f6[2]:
    r6=f6[4].pixel_to_world_values(p[0],p[1])
    for p8,q8 in f8[2]:
        r8=f8[4].pixel_to_world_values(p8[0],p8[1])
        sep=math.hypot((r6[0]-r8[0])*math.cos(math.radians(r6[1]))*3600,(r6[1]-r8[1])*3600)
        if sep<0.15: both.append((p,q,p8,q8,sep))
print(f"\nPAIRS PRESENT IN BOTH FILTERS (real mover signature): {len(both)}")
for p,q,p8,q8,sep in both: print(f"   F606W S/N {p[2]:.1f}/{q[2]:.1f}  F814W S/N {p8[2]:.1f}/{q8[2]:.1f}  cross-filter sep {sep:.3f}in  at F606W px ({p[0]:.1f},{p[1]:.1f})")
