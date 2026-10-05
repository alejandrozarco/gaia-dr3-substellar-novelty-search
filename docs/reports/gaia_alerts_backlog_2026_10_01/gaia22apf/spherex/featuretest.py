"""Spectral feature indices on per-frame SPHEREx fluxes, per epoch and all-epoch (each epoch normalised).
Index = F(feature window) / continuum interpolated (power law in log-log) between two side windows."""
import numpy as np, sys
from astropy.table import Table
IDX={'H2O_1.4':((1.20,1.30),(1.38,1.50),(1.60,1.70)),
     'H2O_1.9':((1.68,1.78),(1.85,2.00),(2.08,2.22)),
     'CO_2.3' :((2.08,2.22),(2.29,2.42),None),          # ratio to blue side only (extrapolated flat in Fnu*lam^a, a from 1.68-2.22)
     'Hpeak'  :((1.50,1.58),(1.66,1.76),(2.00,2.08)),   # >1 = peaked ("triangular") H band
     'ice_3.0':((2.45,2.75),(2.95,3.20),(3.45,3.80)),
     'CO2_4.27':((4.14,4.22),(4.24,4.31),(4.34,4.42)),
     'CO_4.67':((4.50,4.60),(4.62,4.72),(4.78,4.90))}
def wmean(w,f,e,lo,hi):
    m=(w>=lo)&(w<hi)
    if m.sum()<1: return np.nan,np.nan,0
    ww=1/e[m]**2; mu=np.sum(f[m]*ww)/ww.sum(); er=1/np.sqrt(ww.sum())
    if m.sum()>=3: er=max(er,1.2533*1.4826*np.median(np.abs(f[m]-np.median(f[m])))/np.sqrt(m.sum()))
    return mu,er,int(m.sum())
def index(w,f,e,spec,nboot=400,rng=np.random.default_rng(1)):
    b,c,r=spec
    def calc(ff):
        fb,_,nb=wmean(w,ff,e,*b); fc,_,nc=wmean(w,ff,e,*c)
        lb,lc=np.mean(b),np.mean(c)
        if r is None:
            # slope from 1.68-1.78 to 2.08-2.22
            f1,_,_=wmean(w,ff,e,1.68,1.78); a=np.log(fb/f1)/np.log(np.mean(b)/1.73) if f1>0 and fb>0 else 0
            cont=fb*(lc/lb)**a
        else:
            fr,_,nr=wmean(w,ff,e,*r); lr=np.mean(r)
            if not(fb>0 and fr>0): return np.nan
            a=np.log(fr/fb)/np.log(lr/lb); cont=fb*(lc/lb)**a
        return fc/cont
    v=calc(f)
    # bootstrap on noise
    bs=[calc(f+rng.normal(0,e)) for _ in range(nboot)]
    n=[wmean(w,f,e,*x)[2] for x in (b,c,r) if x is not None]
    return v,np.nanstd(bs),n
if __name__=='__main__':
    T=Table.read(sys.argv[1]); G=(T['qc']==1)&(T['clip']==0)
    print('index     | ep0 2025-04/05 | ep1 2025-10 | ep2 2026-05/06 | pooled (only meaningful if non-variable)')
    w=np.array(T['wave']); f=np.array(T['flux']); e=np.array(T['eflux_tot']).copy(); ep=np.array(T['epoch'])
    if '--emp' in sys.argv:
        # empirical per-frame error: rms about a quadratic (in log wavelength) per epoch x detector (includes real structure -> conservative), floor 3%
        for E in range(3):
            for d in range(1,7):
                m=np.where(G&(ep==E)&(np.array(T['det'])==d))[0]
                if len(m)<6: continue
                p=np.polyfit(np.log(w[m]),f[m],2); r=f[m]-np.polyval(p,np.log(w[m]))
                rms=np.std(r)*np.sqrt(len(m)/(len(m)-3))
                e[m]=np.sqrt(rms**2+(0.03*f[m])**2)
    for k,spec in IDX.items():
        s=[]
        for E in range(4):
            m=G&(ep==E) if E<3 else G.copy()
            v,er,n=index(w[m],f[m],e[m],spec)
            s.append(f"{v:5.2f}+-{er:4.2f} n={n}" if np.isfinite(v) else f"   --       n={n}")
        print(f"{k:9s} | "+" | ".join(s))
