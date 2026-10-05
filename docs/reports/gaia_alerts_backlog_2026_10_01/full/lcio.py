import pandas as pd, numpy as np, os
def gaia(n):
    d=pd.read_csv(f'../glc/{n}.csv',skiprows=1); d.columns=['date','jd','mag']; d['mag']=pd.to_numeric(d.mag,errors='coerce'); d=d.dropna()
    d['mjd']=d.jd-2400000.5; return d
def ztf(n,ra,dec,rmax=1.5):
    f=f'ztf/{n}.csv'
    if not os.path.exists(f): return None
    z=pd.read_csv(f)
    g=z.groupby('oid').agg(ra=('ra','median'),dec=('dec','median'))
    g['sep']=3600*np.hypot((g.ra-ra)*np.cos(np.radians(dec)),g.dec-dec)
    ok=g.index[g.sep<rmax]
    z=z[z.oid.isin(ok)&(z.catflags==0)&(z.magerr<0.3)]
    return z
def atlas(n,binned=True):
    f=f'atlas/{n}.csv'
    if not os.path.exists(f): return None
    a=pd.read_csv(f,sep=r'\s+'); a.columns=[c.lstrip('#') for c in a.columns]
    a=a.rename(columns={'chi/N':'chiN'}); a=a[(a.duJy>0)&(a.duJy<300)&(a.err==0)]
    if not binned: return a
    a['night']=np.floor(a.MJD).astype(int)
    def w(x):
        wt=1/x.duJy**2; return pd.Series(dict(MJD=x.MJD.mean(),uJy=np.sum(wt*x.uJy)/wt.sum(),duJy=1/np.sqrt(wt.sum()),n=len(x)))
    return a.groupby(['F','night']).apply(w).reset_index()
