import numpy as np, pandas as pd, time
from astropy.timeseries import LombScargle
rng=np.random.default_rng(1)
z=pd.read_csv("ztf_raw.csv"); z=z[(z.catflags==0)]
p=pd.read_csv("ps1_det.csv"); p=p[(p.psfFlux>0)&(p.psfQfPerfect>0.9)]
p["mag"]=-2.5*np.log10(p.psfFlux)+8.9; p["err"]=1.0857*p.psfFluxErr/p.psfFlux
print("PS1 i points:"); print(p[p.filterID==3][["obsTime","mag","err"]].sort_values("mag").to_string())
# ZTF stats
print("ZTF zr N",len(z),"med %.3f std %.3f MADrms %.3f mederr %.3f"%(z.mag.median(),z.mag.std(),1.4826*np.median(abs(z.mag-z.mag.median())),z.magerr.median()))
w=1/z.magerr**2; mu=np.sum(w*z.mag)/w.sum(); print("chi2r %.2f"%(np.sum(((z.mag-mu)/z.magerr)**2)/(len(z)-1)))
# combined: ZTF r + PS1 grizy (band-mean subtracted, y excluded? keep grizy)
sets={"ZTF_r":(z.hjd.values-2400000.5,z.mag.values-z.mag.median(),z.magerr.values)}
cb=[sets["ZTF_r"]]
for f in [1,2,3,4]:
    g=p[p.filterID==f]; cb.append((g.obsTime.values,(g.mag-g.mag.median()).values,g.err.values))
sets["ZTF_r+PS1_griz"]=tuple(np.concatenate(x) for x in zip(*cb))
fmin,fmax=0.1,300.
for name,(t,y,e) in sets.items():
    T=t.max()-t.min(); df=1/(3*T); f=np.arange(fmin,fmax,df); print(name,"N",len(t),"T %.0f d nfreq %d"%(T,len(f)))
    ls=LombScargle(t,y,e); P=ls.power(f,method="fast",assume_regular_frequency=True)
    k=np.argmax(P); fb=f[k]
    # amplitude of best-fit sinusoid
    mdl=ls.model_parameters(fb); A=np.hypot(mdl[1],mdl[2])
    t0=time.time(); NP=(200 if name=="ZTF_r" else 100); mx=np.empty(NP)
    for i in range(NP):
        pi_=rng.permutation(len(y)); mx[i]=LombScargle(t,y[pi_],e[pi_]).power(f,method="fast",assume_regular_frequency=True).max()
    # note: permute y and e together
    fap=(np.sum(mx>=P[k])+1)/(NP+1); thr99=np.quantile(mx,0.99)
    print("  best f %.5f c/d (P=%.4f h) power %.3f semi-amp %.3f mag  permFAP %.3f  99%%thr %.3f  (%.0fs)"%(fb,24/fb,P[k],A,fap,thr99,time.time()-t0))
    # top 5 peaks
    idx=np.argsort(P)[::-1][:2000]; seen=[]
    for j in idx:
        if all(abs(f[j]-s)>0.01 for s in seen): seen.append(f[j])
        if len(seen)==5: break
    print("  top peaks c/d:",[round(s,4) for s in seen])
    # injection-recovery: detection = peak power > thr99 and |f_rec - f_inj| < 3*df or alias? require within 3 df
    for amp in ([0.03,0.05,0.08,0.12,0.2] if name=="ZTF_r" else [0.03,0.05,0.08]):
        ok=0; N=(40 if name=="ZTF_r" else 20)
        for i in range(N):
            fi=10**rng.uniform(np.log10(fmin),np.log10(fmax)); ph=rng.uniform(0,2*np.pi)
            yi=y+amp*np.sin(2*np.pi*fi*t+ph)
            Pi=LombScargle(t,yi,e).power(f,method="fast",assume_regular_frequency=True); kk=np.argmax(Pi)
            ok+= (Pi[kk]>thr99) and abs(f[kk]-fi)<3*df
        print("   inj semi-amp %.2f: recovered %d/%d"%(amp,ok,N))
