import warnings; warnings.filterwarnings('ignore')
from phot import load
import numpy as np
from astropy.table import Table
G=Table.read('gaia120.csv'); G=G[G['Gmag']<19]
from scipy.special import erf
def prf(xx,yy,px,py,sg):  # pixel-integrated gaussian
    ex=0.5*(erf((xx+0.5-px)/(np.sqrt(2)*sg))-erf((xx-0.5-px)/(np.sqrt(2)*sg)))
    ey=0.5*(erf((yy+0.5-py)/(np.sqrt(2)*sg))-erf((yy-0.5-py)/(np.sqrt(2)*sg)))
    return ex*ey
for s in [64,99,100,101]:
    t,fl,tc,x,y,w=load(s); im=np.nanmedian(fl,axis=0); ny,nx=im.shape
    yy,xx=np.mgrid[:ny,:nx]; gx,gy=w.all_world2pix(np.array(G['RA_ICRS']),np.array(G['DE_ICRS']),0)
    best=None
    for sg in np.arange(0.5,1.6,0.05):
      for dx in np.arange(-0.6,0.61,0.1):
        for dy in np.arange(-0.6,0.61,0.1):
          cols=[np.ones(nx*ny)]; idx=[]
          for i in range(len(G)):
            if -2<gx[i]<nx+1 and -2<gy[i]<ny+1: cols.append(prf(xx,yy,gx[i]+dx,gy[i]+dy,sg).ravel()); idx.append(i)
          A=np.array(cols).T; c,res,_,_=np.linalg.lstsq(A,im.ravel(),rcond=None); r=((im.ravel()-A@c)**2).sum()
          if best is None or r<best[0]: best=(r,sg,dx,dy,c,idx)
    r,sg,dx,dy,c,idx=best; it=idx.index(int(np.where(G['Source']==6130942326140307712)[0][0]))
    print(f'S{s} best sigma={sg:.2f} shift=({dx:.1f},{dy:.1f}) bkg={c[0]:.0f}  target flux={c[1+it]:.0f} e/s; brightest fits:', ', '.join(f"G{G['Gmag'][i]:.1f}:{c[1+k]:.0f}" for k,i in enumerate(idx) if G['Gmag'][i]<15.3))
