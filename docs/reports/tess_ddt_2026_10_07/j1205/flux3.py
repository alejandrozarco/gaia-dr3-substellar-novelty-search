import warnings; warnings.filterwarnings('ignore')
from phot import load
from flux import G
import numpy as np
for s in [64,99,100,101]:
    t,fl,tc,x,y,w=load(s); im=np.nanmedian(fl,axis=0); ny,nx=im.shape
    yy,xx=np.mgrid[:ny,:nx]; gx,gy=w.all_world2pix(np.array(G['RA_ICRS']),np.array(G['DE_ICRS']),0)
    bk=np.percentile(im,15)
    out=[]
    for sid in [6130942326140307712,6130941952486578048,6130942227364487424,6130942154341722880]:
        i=int(np.where(G['Source']==sid)[0][0]); r=np.hypot(xx-gx[i],yy-gy[i])
        out.append(f"G{G['Gmag'][i]:.2f}(RP{G['RPmag'][i]:.2f}) at ({gx[i]:.1f},{gy[i]:.1f}): r<1.5 sum-bkg={(im[r<=1.5]-bk).sum():.0f} peakpix={im[r<=1].max()-bk:.0f}")
    print(f'S{s} bkg15={bk:.0f} | '+' | '.join(out))
