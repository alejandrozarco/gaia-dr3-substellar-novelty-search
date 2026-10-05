import os
import numpy as np, pandas as pd, sys
from astropy.timeseries import LombScargle
W='.'
d=pd.read_csv(f'{W}/c1_lc_clean_full.csv')
def rs(x): x=np.asarray(x); x=x[np.isfinite(x)]; return 1.4826*np.median(np.abs(x-np.median(x)))
excl=set(int(a) for a in sys.argv[1:])  # outburst nights to exclude
d['night']=np.floor(d.mjd).astype(int)
d=d[~d.night.isin(excl)]
# 5-sigma clip per filter on robust scale, subtract per-filter median
parts=[]
for f in ['zg','zr']:
    s=d[d['filter']==f].copy(); yy=s.C1_flux-s.base; r=rs(yy)
    s=s[np.abs(yy)<5*r].copy(); s['y']=s.C1_flux-s.base
    for c in ['ring180_f','ring90_f','ring270_f','KIC_f']:
        s[c]=s[c]-s.groupby('season')[c].transform('median')
    parts.append(s)
q=pd.concat(parts); t=q.mjd.values; y=q.y.values; e=q.C1_err.values
print('quiescent N:',len(q),dict(q['filter'].value_counts()))
fmin,fmax=0.1,50.0  # c/d : 29 min .. 10 d
rng=np.random.default_rng(42)
def ls_peak(t,y,e):
    L=LombScargle(t,y,e); f,p=L.autopower(minimum_frequency=fmin,maximum_frequency=fmax,samples_per_peak=5,method='fast')
    return f,p
f,p=ls_peak(t,y,e); i=np.argmax(p)
order=np.argsort(p)[::-1]
print(f'grid {len(f)} freqs; top peak f={f[i]:.6f} c/d P={24/f[i]:.4f} h power={p[i]:.4f}')
# top 8 distinct peaks
top=[];
for j in order:
    if all(abs(f[j]-f[k])>0.01 for k in top): top.append(j)
    if len(top)>=8: break
for j in top: print(f'  f={f[j]:.5f} P={24/f[j]:8.4f} h  pow={p[j]:.4f}')
NS=int(100)
mx=np.array([ls_peak(t,rng.permutation(y) if True else y,e)[1].max() for _ in range(NS)])
# shuffle y together with e
fap=(mx>=p[i]).mean()
p01=np.quantile(mx,0.99); p05=np.quantile(mx,0.95)
print(f'shuffle FAP ({NS} shuffles): {fap:.3f}; 1%-threshold power {p01:.4f}, 5% {p05:.4f}')
# per-filter too
for fl in ['zg','zr']:
    s=q['filter']==fl; ff,pp=ls_peak(t[s],y[s],e[s]); k=np.argmax(pp)
    mxf=np.array([ls_peak(t[s],rng.permutation(y[s]),e[s])[1].max() for _ in range(40)])
    print(f'{fl}: N={s.sum()} peak P={24/ff[k]:.4f} h pow={pp[k]:.4f}; shuffle FAP(60)={(mxf>=pp[k]).mean():.3f} (40 shuffles)')
# controls through same LS (KIC ring) to see systematics peaks
for c in ['ring180_f','ring90_f','ring270_f','KIC_f']:
    yy=[]; 
    for fl in ['zg','zr']:
        s=(q['filter']==fl).values; yy.append(q[c].values[s]-np.median(q[c].values[s]))
    yc=np.empty(len(q)); 
    yc[(q['filter']=='zg').values]=yy[0]; yc[(q['filter']=='zr').values]=yy[1]
    ff,pp=ls_peak(t,yc,e); k=np.argmax(pp); print(f'control {c}: peak P={24/ff[k]:.4f} h pow={pp[k]:.4f}')
# injection-recovery
print('\ninjection-recovery (sinusoid semi-amplitude A uJy; recovered = peak within 0.5% of f_inj and power > 1% shuffle threshold):')
res=[]
for A in [10,20,30,50,80]:
    for band,(lo,hi) in {'P 0.5-2 h':(12,48),'P 2-6 h':(4,12),'P 6 h-2 d':(0.5,4)}.items():
        ok=0; N=15
        for _ in range(N):
            fi=np.exp(rng.uniform(np.log(lo),np.log(hi))); ph=rng.uniform(0,2*np.pi)
            yi=y+A*np.sin(2*np.pi*fi*t+ph)
            ff,pp=ls_peak(t,yi,e); k=np.argmax(pp)
            if abs(ff[k]-fi)/fi<0.005 and pp[k]>p01: ok+=1
        res.append((A,band,ok/N)); print(f'  A={A:3d} uJy {band:10s}: {ok}/{N}')
pd.DataFrame(res,columns=['A_uJy','band','recovery']).to_csv(f'{W}/injection_recovery.csv',index=False)
