import warnings,math; warnings.filterwarnings("ignore")
import numpy as np
from astropy.io import fits
from astropy.wcs import WCS
from astropy.stats import sigma_clipped_stats
from scipy import ndimage
def cat(fr):
    h=fits.open(fr+".fits"); w=WCS(h["SCI",1].header,h); d=h["SCI",1].data.astype(float); dq=h["DQ",1].data
    good=(dq&(4|16|32|256|512))==0; _,med,sd=sigma_clipped_stats(d[good],sigma=3)
    sm=ndimage.gaussian_filter(np.where(good,d,med)-med,1.3); _,_,sds=sigma_clipped_stats(sm,sigma=3)
    lab,n=ndimage.label(sm>6*sds); out=[]
    for k in range(1,n+1):
        y,x=np.where(lab==k)
        if len(y)<8: continue
        v=sm[y,x]; cx=(x*v).sum()/v.sum(); cy=(y*v).sum()/v.sum()
        ra,de=[float(t) for t in w.pixel_to_world_values(cx,cy)]
        out.append((ra,de,v.max()/sds))
    return np.array(out),w,d.shape
C={fr:cat(fr) for fr in ["ib2k52cvq_flc","ib2k52cwq_flc","ib2k52cxq_flc","ib2k52cyq_flc"]}
dec0=-22.874; cd=math.cos(math.radians(dec0))
def infoot(ra,de):   # inside ALL four frames (with 10 px margin)
    for fr,(_,w,(ny,nx)) in C.items():
        x,y=w.world_to_pixel_values(ra,de)
        if not (10<x<nx-10 and 10<y<ny-10): return False
    return True
def match(a,b,tol):
    out=[]
    for r in a:
        dd=np.hypot((b[:,0]-r[0])*cd*3600,(b[:,1]-r[1])*3600)
        out.append(dd.min()<tol)
    return np.array(out)
e1a,e1b=C["ib2k52cvq_flc"][0],C["ib2k52cwq_flc"][0]; e2a,e2b=C["ib2k52cxq_flc"][0],C["ib2k52cyq_flc"][0]
E1=e1a[match(e1a,e1b,0.10)]          # epoch 1, confirmed in BOTH filters
E2=e2a[match(e2a,e2b,0.10)]          # epoch 2, confirmed in BOTH filters
E1=np.array([r for r in E1 if infoot(r[0],r[1])]); E2=np.array([r for r in E2 if infoot(r[0],r[1])])
dis=E1[~match(E1,np.vstack([e2a,e2b]),0.20)]    # gone from BOTH epoch-2 frames
app=E2[~match(E2,np.vstack([e1a,e1b]),0.20)]    # absent from BOTH epoch-1 frames
print(f"two-filter-confirmed sources in the 4-frame overlap: epoch1 {len(E1)}, epoch2 {len(E2)}")
print(f"DISAPPEARING (in both 14:15 filters, in neither 15:15 filter): {len(dis)}")
for r in dis: print(f"    RA {r[0]:.6f} Dec {r[1]:+.6f}  S/N {r[2]:.0f}")
print(f"APPEARING (in both 15:15 filters, in neither 14:15 filter): {len(app)}")
for r in app: print(f"    RA {r[0]:.6f} Dec {r[1]:+.6f}  S/N {r[2]:.0f}")
print("\npairings (disappear -> appear), displacement vs predicted 1-hr motion (+0.872, -0.011) arcsec:")
for a in dis:
    for b in app:
        dx=(b[0]-a[0])*cd*3600; dy=(b[1]-a[1])*3600
        print(f"    ({a[0]:.6f},{a[1]:+.6f}) -> ({b[0]:.6f},{b[1]:+.6f}) : ({dx:+.3f},{dy:+.3f})in, |v|={math.hypot(dx,dy):.3f}in/hr, "
              f"PA diff {math.degrees(math.atan2(dy,dx)-math.atan2(-0.011,0.872)):+.1f}deg, S/N {a[2]:.0f}->{b[2]:.0f}")
