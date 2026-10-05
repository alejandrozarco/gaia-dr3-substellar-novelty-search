import pandas as pd, numpy as np, matplotlib, sys; matplotlib.use('Agg'); import matplotlib.pyplot as plt
s=pd.read_csv(sys.argv[1]); out=sys.argv[2]
n=len(s); fig,ax=plt.subplots(int(np.ceil(n/4)),4,figsize=(18,2.6*np.ceil(n/4))); ax=ax.ravel()
for a,r in zip(ax,s.itertuples()):
    d=pd.read_csv(f'glc/{r.Name}.csv',skiprows=1); d.columns=['date','jd','mag']; d['mag']=pd.to_numeric(d.mag,errors='coerce'); d=d.dropna()
    a.plot(d.jd-2450000,d.mag,'k.',ms=3)
    try:
        z=pd.read_csv(f'ztf/{r.Name}.csv')
        for b,c in (('zg','g'),('zr','r')):
            x=z[z.filtercode==b]; a.plot(x.mjd+0.5-50000,x.mag,'.',color=c,ms=1.5,alpha=0.6)
    except Exception: pass
    a.invert_yaxis(); a.set_title(f'{r.Name} {str(r.Comment)[:40]}',fontsize=7)
plt.tight_layout(); plt.savefig(out,dpi=60)
