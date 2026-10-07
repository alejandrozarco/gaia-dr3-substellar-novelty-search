import warnings; warnings.filterwarnings('ignore')
from pixmap import pixlcs
from phot import load
import numpy as np
for s in [64,99,100,101]:
    t,F,im,x,y,w,ny,nx=pixlcs(s)
    T,fl,tc,_,_,_=load(s)
    tcm=np.interp(t,T,tc)
    yy,xx=np.mgrid[:ny,:nx]; r=np.hypot(xx-x,yy-y).ravel()
    L=F[:,r<=1.5].sum(1)
    np.save(f'ap_s{s}.npy',np.array([t,L,tcm]))
    print(s,len(t),'TIMECORR range (s)',(tcm.max()-tcm.min())*86400, 'rms',L.std())
