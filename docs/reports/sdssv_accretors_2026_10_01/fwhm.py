"""Halpha emission width: FWHM from the half-maximum crossing of the continuum-subtracted, 3-pixel-smoothed profile
(6535-6595 vacuum A, continuum from measure.py side bands). Also Hbeta FWHM likewise."""
import os, numpy as np, pandas as pd
from astropy.io import fits
D=os.path.dirname(os.path.abspath(__file__))
def fw(w,f,iv,a,b,cs):
    m=np.zeros_like(w,bool)
    for c0,c1 in cs: m|=(w>c0)&(w<c1)
    m&=iv>0; k=(w>a)&(w<b)&(iv>0)
    if m.sum()<8 or k.sum()<6: return np.nan
    p=np.polyfit(w[m],f[m],1); y=np.convolve(f-np.polyval(p,w),np.ones(3)/3,'same')[k]; x=w[k]
    i=np.argmax(y); h=y[i]/2
    if y[i]<=0: return np.nan
    l=i
    while l>0 and y[l]>h: l-=1
    r=i
    while r<len(y)-1 and y[r]>h: r+=1
    return float(x[r]-x[l])
def run(fn):
    with fits.open(os.path.join(D,"spec",fn)) as h:
        d=h[1].data; w=10**d["LOGLAM"].astype(float); f=d["FLUX"].astype(float); iv=d["IVAR"].astype(float)
    return fw(w,f,iv,6535,6595,[(6470,6510),(6620,6660)]), fw(w,f,iv,4832,4894,[(4780,4820),(4905,4935)])
if __name__=="__main__":
    import sys
    V=pd.read_csv(sys.argv[1]); r=[run(f) for f in V.fname]; V['fwhm_Ha']=[x[0] for x in r]; V['fwhm_Hb']=[x[1] for x in r]
    V.to_csv(sys.argv[2],index=False)
