import numpy as np, pandas as pd, time
from astropy.timeseries import LombScargle
rng=np.random.default_rng(2)
d=pd.read_csv("atlas_fp.txt",sep=r"\s+"); d.columns=[c.lstrip("#") for c in d.columns]
print("total",len(d),d.F.value_counts().to_dict(),"MJD %.0f-%.0f"%(d.MJD.min(),d.MJD.max()))
STAR={"c":3631e6*10**(-0.4*19.34),"o":3631e6*10**(-0.4*19.23)}  # expected star flux from PS1 g/r/i (uJy); ATLAS uJy are difference fluxes
for f in ["c","o"]:
    x=d[(d.F==f)&(d.err==0)&(d.duJy>0)&(d.duJy<120)&(d["chi/N"]<5)&(d.mag5sig>17.5)].copy()
    # sigma clip 5 sigma on flux
    med=np.median(x.uJy); x=x[abs(x.uJy-med)<5*x.duJy]
    w=1/x.duJy**2; mu=np.sum(w*x.uJy)/w.sum(); emu=1/np.sqrt(w.sum())
    chi=np.sum(((x.uJy-mu)/x.duJy)**2)/(len(x)-1)
    print(f,"N %d wmean %.1f+-%.1f uJy (diff flux; star ~%.0f uJy) med err %.0f uJy rms %.0f chi2r %.2f"%(len(x),mu,emu,STAR[f],x.duJy.median(),x.uJy.std(),chi))
    x.to_csv(f"atlas_clean_{f}.csv",index=False)
    x["season"]=np.floor((x.MJD-57000+120)/365.25).astype(int)
    x["uJy"]=x.uJy-x.groupby("season").uJy.transform("median")  # remove secular difference-flux drift (PM vs template)
    print("  after per-season median subtraction: rms %.1f chi2r %.2f"%(x.uJy.std(),np.sum((x.uJy/x.duJy)**2)/(len(x)-1)))
    t=x.MJD.values; y=x.uJy.values; e=x.duJy.values
    T=t.max()-t.min(); df=1/(3*T); fr=np.arange(0.1,300,df)
    P=LombScargle(t,y,e).power(fr,method="fast",assume_regular_frequency=True); k=np.argmax(P)
    mp=LombScargle(t,y,e).model_parameters(fr[k]); A=np.hypot(mp[1],mp[2])
    NP=50; mx=np.empty(NP); t0=time.time()
    for i in range(NP):
        pi_=rng.permutation(len(y)); mx[i]=LombScargle(t,y[pi_],e[pi_]).power(fr,method="fast",assume_regular_frequency=True).max()
    thr=np.quantile(mx,0.99)
    print("  nfreq %d best f %.5f c/d (P %.4f h) power %.4f semi-amp %.1f uJy (%.1f%% of mean) permFAP %.3f thr99 %.4f (%.0fs)"%(len(fr),fr[k],24/fr[k],P[k],A,100*A/STAR[f],(np.sum(mx>=P[k])+1)/(NP+1),thr,time.time()-t0))
    for frac in [0.03,0.05,0.08]:
        ok=0; N=20
        for i in range(N):
            fi=10**rng.uniform(-1,np.log10(300)); ph=rng.uniform(0,2*np.pi)
            yi=y+frac*STAR[f]*np.sin(2*np.pi*fi*t+ph)
            Pi=LombScargle(t,yi,e).power(fr,method="fast",assume_regular_frequency=True); kk=np.argmax(Pi)
            ok+=(Pi[kk]>thr) and abs(fr[kk]-fi)<3*df
        print("   inj semi-amp %.0f%% of flux: %d/%d"%(100*frac,ok,N))
