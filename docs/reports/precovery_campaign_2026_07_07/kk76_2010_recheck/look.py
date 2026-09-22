import warnings,sys,math; warnings.filterwarnings("ignore"); sys.path.insert(0,"/tmp")
import numpy as np
from astropy.io import fits
from astropy.wcs import WCS
from astropy.stats import sigma_clipped_stats
from scipy import ndimage
from astropy.time import Time
from kk76_hz import hz
FR=["ib2k52cvq_flc","ib2k52cwq_flc","ib2k52cxq_flc","ib2k52cyq_flc","ib2k52czq_flt","ib2k52d0q_flt","ib2k52d2q_flt","ib2k52d3q_flt"]
res={}
for fr in FR:
    h=fits.open(fr+".fits"); p=h[0].header; s=h["SCI",1].header
    tmid=(p["EXPSTART"]+p["EXPEND"])/2
    (_,ra,de),=hz([f"{Time(tmid,format='mjd',scale='utc').jd:.6f}"])
    w=WCS(s,h); x,y=[float(v) for v in w.world_to_pixel_values(ra,de)]
    sci=h["SCI",1].data.astype(float); dq=h["DQ",1].data
    scale=abs(w.proj_plane_pixel_scales()[0].value)*3600
    R=int(round(3.0/scale))   # search within 3 arcsec
    xi,yi=int(round(x)),int(round(y))
    ny,nx=sci.shape
    y0,y1=max(0,yi-R),min(ny,yi+R+1); x0,x1=max(0,xi-R),min(nx,xi+R+1)
    st=sci[y0:y1,x0:x1].copy(); bad=(dq[y0:y1,x0:x1]&(4|8|16|32|256|512))!=0
    mean,med,sd=sigma_clipped_stats(st[~bad],sigma=3)
    sm=ndimage.gaussian_filter(np.where(bad,med,st)-med,1.2 if scale<0.1 else 0.8)
    _,_,sds=sigma_clipped_stats(sm,sigma=3)
    lab,n=ndimage.label(sm>4*sds)
    cands=[]
    for k in range(1,n+1):
        yy,xx=np.where(lab==k)
        if len(yy)<3: continue
        wgt=sm[yy,xx]; cy=(yy*wgt).sum()/wgt.sum()+y0; cx=(xx*wgt).sum()/wgt.sum()+x0
        snr=sm[yy,xx].max()/sds
        d=math.hypot((cx-x),(cy-y))*scale
        rr,dd=[float(v) for v in w.pixel_to_world_values(cx,cy)]
        cands.append((d,snr,cx,cy,rr,dd,len(yy)))
    cands.sort()
    res[fr]=dict(ra=ra,de=de,x=x,y=y,scale=scale,cands=cands,wcsname=s.get("WCSNAME","?"),filt=p.get("FILTER","?"),tmid=tmid,inside=(0<=x<nx and 0<=y<ny))
    print(f"{fr}  {p.get('FILTER'):6s} WCSNAME={s.get('WCSNAME','?')}")
    print(f"   predicted pixel ({x:.1f},{y:.1f}) of {nx}x{ny}  scale {scale:.3f}in/px  inside={res[fr]['inside']}")
    for c in cands[:4]: print(f"   source {c[0]:5.2f}in from prediction  S/N~{c[1]:5.1f}  px({c[2]:.1f},{c[3]:.1f})  npix {c[6]}  RA/Dec ({c[4]:.6f},{c[5]:+.6f})")
    if not cands: print("   no >4-sigma source within 3in")
import pickle; pickle.dump(res,open("look.pkl","wb"))
