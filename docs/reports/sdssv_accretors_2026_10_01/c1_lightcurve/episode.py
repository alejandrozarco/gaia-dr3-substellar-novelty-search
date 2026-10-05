import os
"""Episode (multi-night) brightening test: C1 vs ring controls at the same separation from KIC 6773282."""
import numpy as np, pandas as pd
W='.'
d=pd.read_csv(f'{W}/c1_lc_clean_full.csv')
def rs(x): x=np.asarray(x); x=x[np.isfinite(x)]; return 1.4826*np.median(np.abs(x-np.median(x)))
series={'C1':'C1o2'}
for az in [90,120,150,180,210,240,270]: series[f'ring{az}']=f'ring{az}'
d['season']=np.floor(2018+(d.jd-2458119.5)/365.25).astype(int)
res={}
for nm,c in series.items():
    f=d[c+'_f'].values; es=d[c+'_e'].values*np.sqrt(np.clip(d[c+'_chi'].values,1,None))
    # per-filter error scale so that pulls vs per-filter-season median have unit robust std (same recipe for all series)
    base=d.assign(v=f).groupby(['filter','season']).v.transform('median').values
    e=es.copy()
    for fl in ['zg','zr']:
        s=(d['filter']==fl).values; k=rs((f[s]-base[s])/es[s]); e[s]=es[s]*k
    y=f-base
    nights=np.unique(np.floor(d.mjd.values))
    rows=[]
    for n in nights:
        w=(d.mjd.values>=n-4)&(d.mjd.values<n+5)&np.isfinite(y)&np.isfinite(e)
        if w.sum()<2: continue
        # require >=2 distinct nights in window
        if len(np.unique(np.floor(d.mjd.values[w])))<2: continue
        wt=e[w]**-2; m=np.sum(wt*y[w])/wt.sum(); er=wt.sum()**-0.5
        rows.append((n,m,er,m/er,w.sum()))
    r=pd.DataFrame(rows,columns=['night','mean','err','sig','n'])
    res[nm]=r
    print(f'{nm:8s} windows={len(r)}  max sig={r.sig.max():5.1f} at MJD {r.night[r.sig.idxmax()]:.0f} (mean {r["mean"][r.sig.idxmax()]:.0f} uJy)  min sig={r.sig.min():5.1f}  N(sig>5)={(r.sig>5).sum()}  N(sig<-5)={(r.sig<-5).sum()}')
r=res['C1']; print('\nC1 windows with sig>4:'); print(r[r.sig>4].round(1).to_string())
pd.concat({k:v for k,v in res.items()}).to_csv(f'{W}/episode_windows.csv')
