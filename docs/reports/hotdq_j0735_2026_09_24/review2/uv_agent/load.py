import numpy as np
from astropy.io import fits
R="/tmp/hotdq/review2/raw/"
def load(fn, seg=None, good=True):
    d=fits.open(R+fn)[1].data
    out={}
    for r in d:
        w=r["WAVELENGTH"].astype(float); f=r["FLUX"].astype(float); e=r["ERROR"].astype(float); q=r["DQ_WGT"].astype(float); dq=r["DQ"]
        g=r["GROSS"].astype(float); b=r["BACKGROUND"].astype(float); n=r["NET"].astype(float)
        out[r["SEGMENT"]]=dict(w=w,f=f,e=e,q=q,dq=dq,gross=g,bkg=b,net=n)
    return out
def binspec(w,f,e,q,n=6):
    m=len(w)//n*n
    W=w[:m].reshape(-1,n).mean(1)
    ok=(q[:m]>0)&(e[:m]>0)
    F=np.where(ok,f[:m],0).reshape(-1,n).sum(1)/np.maximum(ok.reshape(-1,n).sum(1),1)
    E=np.sqrt(np.where(ok,e[:m]**2,0).reshape(-1,n).sum(1))/np.maximum(ok.reshape(-1,n).sum(1),1)
    frac=ok.reshape(-1,n).mean(1)
    return W,F,E,frac
