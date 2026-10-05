import pandas as pd, numpy as np, matplotlib, sys, glob, os; matplotlib.use('Agg'); import matplotlib.pyplot as plt
names=sys.argv[1:] or [os.path.basename(f)[:-4] for f in sorted(glob.glob('atlas/*.csv'))]
fig,ax=plt.subplots(len(names),1,figsize=(14,2.8*len(names))); ax=np.atleast_1d(ax)
for a,n in zip(ax,names):
    d=pd.read_csv(f'atlas/{n}.csv',sep=r'\s+'); d.columns=[c.lstrip('#') for c in d.columns]
    d=d[(d.duJy>0)&(d.duJy<2000)&(d['chi/N']<10)&(d.err==0)]
    d['night']=np.floor(d.MJD)
    nb=d.groupby(['night','F']).apply(lambda x: pd.Series(dict(mjd=x.MJD.mean(),f=np.average(x.uJy,weights=1/x.duJy**2),e=1/np.sqrt(np.sum(1/x.duJy**2)),n=len(x))),include_groups=False).reset_index()
    nb.to_csv(f'atlas/{n}_nightly.csv',index=False)
    for F,c in (('o','orange'),('c','c')):
        x=nb[nb.F==F]; a.errorbar(x.mjd,x.f,x.e,fmt='.',color=c,ms=3,lw=0.3)
        if len(x)>5:
            q=x[x.e<x.e.median()*2]; print(n,F,'nights',len(x),'median uJy %.0f, p1 %.0f, p99 %.0f, max %.0f'%(q.f.median(),q.f.quantile(.01),q.f.quantile(.99),q.f.max()),'n>5sig above med:',int(((q.f-q.f.median())/q.e>5).sum()))
    a.set_title(n+' ATLAS forced phot (diff flux uJy, nightly)',fontsize=8); a.set_xlim(57000,61050)
    ax2=a.twinx()
    g=pd.read_csv(f'glc/{n}.csv',skiprows=1); g.columns=['d','jd','m']; g['m']=pd.to_numeric(g.m,errors='coerce'); g=g.dropna()
    ax2.plot(g.jd-2400000.5,g.m,'k+',ms=4); ax2.invert_yaxis()
plt.tight_layout(); plt.savefig('atlas_'+('_'.join(names) if len(names)<4 else 'all')+'.png',dpi=55)
