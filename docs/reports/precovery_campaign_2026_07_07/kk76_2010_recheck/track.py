import warnings,sys,math,pickle; warnings.filterwarnings("ignore"); sys.path.insert(0,"/tmp")
import numpy as np, matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
from astropy.io import fits
from astropy.wcs import WCS
from astropy.stats import sigma_clipped_stats
from scipy import ndimage
from astropy.time import Time
from kk76_hz import hz
FR=["ib2k52cvq_flc","ib2k52cwq_flc","ib2k52cxq_flc","ib2k52cyq_flc","ib2k52czq_flt","ib2k52d0q_flt","ib2k52d2q_flt","ib2k52d3q_flt"]
W1=(260.003933,-22.876038)                     # F606W candidate at epoch 1 (cvq)
hdr={fr:fits.open(fr+".fits") for fr in FR}
tm={fr:(hdr[fr][0].header["EXPSTART"]+hdr[fr][0].header["EXPEND"])/2 for fr in FR}
pred={fr:hz([f"{Time(tm[fr],format='mjd',scale='utc').jd:.6f}"])[0] for fr in FR}
cd=math.cos(math.radians(W1[1]))
off=(W1[0]-pred[FR[0]][1], W1[1]-pred[FR[0]][2])      # constant along-track offset
print(f"implied offset from refined orbit: ({off[0]*cd*3600:+.2f}, {off[1]*3600:+.2f}) arcsec  = {math.hypot(off[0]*cd*3600,off[1]*3600):.2f}in")
fig,axs=plt.subplots(2,8,figsize=(22,6))
for k,fr in enumerate(FR):
    h=hdr[fr]; w=WCS(h["SCI",1].header,h); d=h["SCI",1].data.astype(float); dq=h["DQ",1].data
    ny,nx=d.shape; _,med,sd=sigma_clipped_stats(d[(dq&(4|16|32|256|512))==0],sigma=3)
    scale=abs(w.proj_plane_pixel_scales()[0].value)*3600
    tra=pred[fr][1]+off[0]; tde=pred[fr][2]+off[1]                  # track position at this frame
    x,y=[float(v) for v in w.world_to_pixel_values(tra,tde)]
    xo,yo=[float(v) for v in w.world_to_pixel_values(*W1)]          # the epoch-1 spot (a star would stay here)
    def meas(x,y):
        if not (3<x<nx-4 and 3<y<ny-4): return None
        r=max(2,int(round(0.12/scale)))
        st=d[int(y)-r:int(y)+r+1,int(x)-r:int(x)+r+1]-med
        return st.sum()/(sd*math.sqrt(st.size))
    s_track=meas(x,y); s_old=meas(xo,yo)
    moved=math.hypot((tra-W1[0])*cd*3600,(tde-W1[1])*3600)
    print(f"{fr} {h[0].header['FILTER']:6s} t={Time(tm[fr],format='mjd').iso[11:19]}  track px ({x:6.1f},{y:6.1f}) "
          f"inside={'Y' if 3<x<nx-4 and 3<y<ny-4 else 'N'}  S/N AT TRACK {('%.1f'%s_track) if s_track is not None else 'off-frame':>9}   "
          f"S/N at epoch-1 spot {('%.1f'%s_old) if s_old is not None else 'off-frame':>9}  (track has moved {moved:.2f}in)")
    for row,(cx,cy) in enumerate(((x,y),(xo,yo))):
        hh=int(round(1.2/scale)); cxi,cyi=int(round(cx)),int(round(cy))
        if 0<=cxi-hh and cxi+hh<nx and 0<=cyi-hh and cyi+hh<ny:
            cut=d[cyi-hh:cyi+hh+1,cxi-hh:cxi+hh+1]-med
            axs[row,k].imshow(cut,origin="lower",cmap="gray",vmin=-2*sd,vmax=8*sd)
        axs[row,k].set_xticks([]); axs[row,k].set_yticks([])
    axs[0,k].set_title(f"{h[0].header['FILTER']} {Time(tm[fr],format='mjd').iso[11:16]}",fontsize=9)
axs[0,0].set_ylabel("AT TRACK",fontsize=10); axs[1,0].set_ylabel("at 14:15 spot",fontsize=10)
fig.suptitle("Candidate KK76 track through all 8 WFC3 frames (top: predicted track position; bottom: where it was at 14:15 — a star would stay there)",fontsize=11)
fig.tight_layout(); fig.savefig("kk76_track.png",dpi=90); print("saved kk76_track.png")
