import warnings; warnings.filterwarnings('ignore')
from phot import load
from flux import prf, G
import numpy as np
TID=6130942326140307712
for s in [64,99,100,101]:
    t,fl,tc,x,y,w=load(s); im=np.nanmedian(fl,axis=0); ny,nx=im.shape
    yy,xx=np.mgrid[:ny,:nx]; gx,gy=w.all_world2pix(np.array(G['RA_ICRS']),np.array(G['DE_ICRS']),0)
    box=(np.abs(xx-x)<=3.5)&(np.abs(yy-y)<=3.5)
    ins=[i for i in range(len(G)) if abs(gx[i]-x)<=5 and abs(gy[i]-y)<=5]
    best=None
    for sg in np.arange(0.6,1.4,0.05):
      for dx in np.arange(-0.5,0.51,0.1):
        for dy in np.arange(-0.5,0.51,0.1):
          A=np.array([np.ones(box.sum())]+[prf(xx,yy,gx[i]+dx,gy[i]+dy,sg)[box] for i in ins]).T
          c,_,_,_=np.linalg.lstsq(A,im[box],rcond=None); r=((im[box]-A@c)**2).sum()
          if best is None or r<best[0]: best=(r,sg,dx,dy,c)
    r,sg,dx,dy,c=best
    d={int(G['Source'][i]):(G['Gmag'][i],G['sep'][i],c[1+k]) for k,i in enumerate(ins)}
    print(f'S{s} sigma={sg:.2f} shift=({dx:.1f},{dy:.1f}) bkg={c[0]:.0f} rms resid={np.sqrt(r/box.sum()):.1f}; target={d[TID][2]:.0f} e/s;', '; '.join(f'G{v[0]:.2f}@{v[1]:.0f}":{v[2]:.0f}' for k,v in sorted(d.items(),key=lambda kv:kv[1][0]) if v[0]<17.6))
