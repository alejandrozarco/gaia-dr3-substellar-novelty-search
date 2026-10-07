import numpy as np, warnings; warnings.filterwarnings('ignore')
from astropy.timeseries import LombScargle
rng=np.random.default_rng(3)
D={s:np.load(f'ap_s{s}.npy') for s in [99,100,101]}
t=np.concatenate([D[s][0] for s in D]); y=np.concatenate([D[s][1] for s in D]); sec=np.concatenate([np.full(len(D[s][0]),s) for s in D])
F={'sub':[203.40222,206.75370],'super':[228.57084,225.21990]}
def pmax(tt,yy,f,hw=0.004):
    fr=np.arange(f-hw,f+hw,0.00002); return LombScargle(tt,yy).power(fr).max()
def persector(tt,yy,ss,fs):
    out={}
    for s in D:
        m=ss==s; X=np.c_[[np.sin(2*np.pi*f*tt[m]) for f in fs]+[np.cos(2*np.pi*f*tt[m]) for f in fs]+[np.ones(m.sum())]].T
        out[s]=np.linalg.lstsq(X,yy[m],rcond=None)[0]
    return out
obs=[pmax(t,y,F['sub'][i])/pmax(t,y,F['super'][i]) for i in range(2)]
print('observed ratios sub/super: 203/228 %.2f  206/225 %.2f'%tuple(obs))
sig=np.std(y)
for hyp in ['sub','super']:
    fs=F[hyp]; C=persector(t,y,sec,fs); R=[]
    for k in range(40):
        ys=rng.normal(0,sig,len(t))
        for s in D:
            m=sec==s; c=C[s]
            for i,f in enumerate(fs): ys[m]+=c[i]*np.sin(2*np.pi*f*t[m])+c[2+i]*np.cos(2*np.pi*f*t[m])
        R.append([pmax(t,ys,F['sub'][i])/pmax(t,ys,F['super'][i]) for i in range(2)])
    R=np.array(R)
    print(f'hyp={hyp} (per-sector amp/phase as observed): ratio203/228 med {np.median(R[:,0]):.2f} 5-95% [{np.percentile(R[:,0],5):.2f},{np.percentile(R[:,0],95):.2f}] ; ratio206/225 med {np.median(R[:,1]):.2f} [{np.percentile(R[:,1],5):.2f},{np.percentile(R[:,1],95):.2f}]',flush=True)
