import warnings,sys,math,pickle; warnings.filterwarnings("ignore"); sys.path.insert(0,"/tmp")
import numpy as np, matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
from astropy.io import fits
from astropy.wcs import WCS
from scipy import ndimage
from astropy.stats import sigma_clipped_stats
R=pickle.load(open("look.pkl","rb"))
def load(fr):
    h=fits.open(fr+".fits"); s=h["SCI",1]; w=WCS(s.header,h)
    d=s.data.astype(float); dq=h["DQ",1].data
    d[(dq&(4|16|32|256|512))!=0]=np.nan
    return d,w
out={}
fig,ax=plt.subplots(2,3,figsize=(15,10))
for row,(a,b,filt) in enumerate((("ib2k52cvq_flc","ib2k52cxq_flc","F606W"),("ib2k52cwq_flc","ib2k52cyq_flc","F814W"))):
    A,wa=load(a); B,wb=load(b)
    ny,nx=A.shape; yy,xx=np.mgrid[0:ny,0:nx]
    rr,dd=wa.pixel_to_world_values(xx,yy)            # world coords of A's pixels
    bx,by=wb.world_to_pixel_values(rr,dd)             # where they fall in B
    Bi=ndimage.map_coordinates(np.nan_to_num(B,nan=np.nanmedian(B)),[by,bx],order=1,mode="constant",cval=np.nan)
    _,ma,_=sigma_clipped_stats(A[np.isfinite(A)]); _,mb,_=sigma_clipped_stats(Bi[np.isfinite(Bi)])
    D=(A-ma)-(Bi-mb)
    _,_,sd=sigma_clipped_stats(D[np.isfinite(D)],sigma=3)
    Ds=ndimage.gaussian_filter(np.nan_to_num(D),1.2)
    _,_,sds=sigma_clipped_stats(Ds,sigma=3)
    # predicted positions of BOTH epochs expressed in A's pixel grid
    p1=R[a]; p2=R[b]
    x1,y1=p1["x"],p1["y"]
    x2,y2=[float(v) for v in wa.world_to_pixel_values(p2["ra"],p2["de"])]
    def peak(x,y,sign,rad=12):
        xi,yi=int(round(x)),int(round(y))
        st=Ds[yi-rad:yi+rad+1,xi-rad:xi+rad+1]*sign
        j=np.unravel_index(np.nanargmax(st),st.shape)
        return st[j]/sds, xi-rad+j[1], yi-rad+j[0]
    s1,px1,py1=peak(x1,y1,+1); s2,px2,py2=peak(x2,y2,-1)
    sep_obs=math.hypot(px2-px1,py2-py1); sep_pred=math.hypot(x2-x1,y2-y1)
    out[filt]=(s1,px1,py1,s2,px2,py2,sep_obs,sep_pred,x1,y1,x2,y2)
    print(f"{filt}: diff = {a[:9]} (14:15) - {b[:9]} (15:15), aligned via HSC-tied WCS")
    print(f"   predicted: epoch-1 at A-pixel ({x1:.1f},{y1:.1f}), epoch-2 at ({x2:.1f},{y2:.1f}); predicted separation {sep_pred:.1f} px = {sep_pred*0.0396:.3f}in")
    print(f"   POSITIVE peak within 12px of epoch-1 prediction: S/N {s1:5.1f} at ({px1},{py1})  [{math.hypot(px1-x1,py1-y1)*0.0396:.2f}in from pred]")
    print(f"   NEGATIVE peak within 12px of epoch-2 prediction: S/N {s2:5.1f} at ({px2},{py2})  [{math.hypot(px2-x2,py2-y2)*0.0396:.2f}in from pred]")
    print(f"   observed +/- separation {sep_obs:.1f} px = {sep_obs*0.0396:.3f}in   (vs predicted {sep_pred*0.0396:.3f}in)")
    cx,cy=int((x1+x2)/2),int((y1+y2)/2); h=45
    for col,(img,title) in enumerate(((A-ma,f"{filt} 14:15 ({a[:9]})"),(Bi-mb,f"{filt} 15:15 aligned ({b[:9]})"),(Ds,f"{filt} DIFFERENCE (smoothed)"))):
        cut=img[cy-h:cy+h,cx-h:cx+h]
        v=np.nanpercentile(np.abs(cut),99) if col==2 else np.nanpercentile(cut,99.5)
        ax[row,col].imshow(cut,origin="lower",cmap="gray" if col<2 else "RdBu_r",vmin=(-v if col==2 else -0.1*v),vmax=v)
        for (xx_,yy_,c) in ((x1,y1,"lime"),(x2,y2,"orange")):
            ax[row,col].add_patch(plt.Circle((xx_-(cx-h),yy_-(cy-h)),6,fill=False,ec=c,lw=1.5))
        ax[row,col].set_title(title,fontsize=10); ax[row,col].set_xticks([]); ax[row,col].set_yticks([])
fig.suptitle("(88268) 2001 KK76 in HST/WFC3 2010-03-13 — refined-orbit prediction: green = 14:15, orange = 15:15\nright column: epoch difference (stars cancel; a real mover = red at green, blue at orange)",fontsize=11)
fig.tight_layout(); fig.savefig("kk76_2010_diff.png",dpi=110)
pickle.dump(out,open("diff.pkl","wb")); print("\nsaved kk76_2010_diff.png")
