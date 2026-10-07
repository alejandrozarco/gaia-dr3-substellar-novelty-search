import numpy as np, warnings; warnings.filterwarnings('ignore')
from astropy.timeseries import LombScargle
rng=np.random.default_rng(2)
D={s:np.load(f'ap_s{s}.npy') for s in [99,100,101]}
t=np.concatenate([D[s][0] for s in D]); y=np.concatenate([D[s][1] for s in D]); sec=np.concatenate([np.full(len(D[s][0]),s) for s in D])
def grid(tt,yy,lo,hi,st=0.0002):
    fr=np.arange(lo,hi,st); return fr,LombScargle(tt,yy).power(fr)
print('Top peaks in combined S99-101 BJD, window 195-237 c/d:')
fr,p=grid(t,y,195,237); o=np.argsort(p)[::-1]; got=[]
for j in o:
    if all(abs(fr[j]-g)>0.05 for g in got): got.append(fr[j]); print(f'  {fr[j]:.4f} c/d  P={p[j]:.5f}  mirror={432-fr[j]:.4f}')
    if len(got)==8: break
# per-sector phases at fixed freq for each hypothesis
def phases(f):
    out=[]
    for s in D:
        tt,yy=D[s][0],D[s][1]; X=np.c_[np.sin(2*np.pi*f*tt),np.cos(2*np.pi*f*tt),np.ones_like(tt)]
        c=np.linalg.lstsq(X,yy,rcond=None)[0]; r=yy-X@c; e=np.std(r)*np.sqrt(2/len(tt))
        out.append(f'S{s}: A={np.hypot(c[0],c[1]):.3f}+-{e:.3f} ph={np.degrees(np.arctan2(c[1],c[0]))%360:.0f}+-{np.degrees(e/np.hypot(c[0],c[1])):.0f}')
    return ' | '.join(out)
for f in [203.4022,228.5708,206.7536,225.2198]:
    fr,p=grid(t,y,f-0.01,f+0.01,0.00002); fb=fr[p.argmax()]; print(f'f={fb:.5f} P={p.max():.5f}  ', phases(fb))
# two-frequency simulation with per-sector random phase (incoherent) to see the ratio expected
for truth in ['sub','super']:
  for coh in [True,False]:
    r=[]
    for k in range(40):
        ys=rng.normal(0,np.std(y),len(t))
        for fs,amp in [(203.4022,0.45),(206.7536,0.38)]:
            ft=fs if truth=='sub' else 432-fs
            ph=rng.uniform(0,2*np.pi,4)
            for i,s in enumerate(D):
                m=sec==s; ys[m]+=amp*np.sin(2*np.pi*ft*t[m]+(ph[0] if coh else ph[i]))
        a=[grid(t,ys,f-0.02,f+0.02,0.0002)[1].max() for f in [203.4022,228.5708,206.7536,225.2198]]
        r.append((a[0]/a[1],a[2]/a[3]))
    r=np.array(r); print(f'sim truth={truth} coherent={coh}: ratio203/228 med {np.median(r[:,0]):.2f} [{np.percentile(r[:,0],5):.2f},{np.percentile(r[:,0],95):.2f}]  ratio206/225 med {np.median(r[:,1]):.2f} [{np.percentile(r[:,1],5):.2f},{np.percentile(r[:,1],95):.2f}]',flush=True)
