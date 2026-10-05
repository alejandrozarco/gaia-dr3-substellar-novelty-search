"""Dense re-sampling (2^22 prior samples in 2^18 chunks) for the f_lo>0.1 stars of joker_lite2; same prior/jitter/clean as joker_lite2.
f_lo = min f(M) over samples with chi2 < chi2_min + 9*max(1, chi2_min/dof); also posterior (rejection) percentiles."""
import numpy as np, pandas as pd, multiprocessing as mp, sys
from joker_lite2 import clean, G, Ms
NCH=16; CH=2**18
def run(args):
    sid,g=args; g=clean(g); g=g.sort_values('jd'); t=g.jd.values-2459000.0; y=g.v_rad.values
    y=y-np.average(y,weights=1/(g.e_v_rel.values**2+0.09))
    lg=np.nanmedian(g.doppler_logg); s=0.3 if lg>3.5 else (0.7 if lg>2.5 else 1.5); w=1/(g.e_v_rel.values**2+s**2)
    rng=np.random.default_rng(int(sid)%2**31); keep=[]
    for c in range(NCH):
        P=np.exp(rng.uniform(np.log(0.3),np.log(5000),CH)); e=np.clip(rng.beta(0.867,3.03,CH),0,0.9); om=rng.uniform(0,2*np.pi,CH); M0=rng.uniform(0,2*np.pi,CH)
        Mn=(2*np.pi*t[None,:]/P[:,None]+M0[:,None])%(2*np.pi); E=Mn.copy()
        for _ in range(12): E=E-(E-e[:,None]*np.sin(E)-Mn)/(1-e[:,None]*np.cos(E))
        nu=2*np.arctan2(np.sqrt(1+e)[:,None]*np.sin(E/2),np.sqrt(1-e)[:,None]*np.cos(E/2))
        X=np.cos(om[:,None]+nu)+e[:,None]*np.cos(om)[:,None]
        Sw=w.sum(); Sx=(w*X).sum(1); Sxx=(w*X*X).sum(1); Sy=(w*y).sum(); Sxy=(w*X*y).sum(1); Syy=(w*y*y).sum()
        det=Sw*Sxx-Sx**2; okd=np.abs(det)>1e-12*Sw*Sw; det=np.where(okd,det,1.0)
        K=(Sw*Sxy-Sx*Sy)/det; v0=(Sy-K*Sx)/Sw
        chi2=Syy-2*K*Sxy-2*v0*Sy+K*K*Sxx+2*K*v0*Sx+v0*v0*Sw
        chi2=np.where(okd&(np.abs(K)<400)&np.isfinite(chi2),chi2,np.inf)
        o=np.argsort(chi2)[:4000]; keep.append(pd.DataFrame(dict(P=P[o],e=e[o],K=np.abs(K[o]),chi2=chi2[o])))
    k=pd.concat(keep,ignore_index=True); cmin=k.chi2.min(); c2r=max(1.0,cmin/max(len(y)-3,1))
    k['f']=k.P*86400*(k.K*1e3)**3*(1-k.e**2)**1.5/(2*np.pi*G)/Ms
    win=k[k.chi2<cmin+9*c2r]; lo=win.loc[win.f.idxmin()]
    acc=k[np.random.default_rng(1).uniform(size=len(k))<np.exp(-(k.chi2-cmin)/(2*c2r))]
    b=k.loc[k.chi2.idxmin()]
    return dict(sdss_id=sid,n=len(y),chi2r_min=cmin/max(len(y)-3,1),n_win=len(win),n_acc=len(acc),P_best=b.P,K_best=b.K,e_best=b.e,f_best=b.f,
        f_lo=lo.f,P_flo=lo.P,K_flo=lo.K,e_flo=lo.e,Pwin_min=win.P.min(),Pwin_max=win.P.max(),f_acc1=np.percentile(acc.f,1),f_acc50=np.percentile(acc.f,50),
        P_acc1=np.percentile(acc.P,1),P_acc99=np.percentile(acc.P,99),sat=len(win)>=4000*0.9)
if __name__=='__main__':
    r=pd.read_csv('joker_lite2.csv.gz'); ids=set(r[r.f_lo>0.1].sdss_id)
    v=pd.concat([pd.read_csv(x,dtype={'gaia_dr3_source_id':str}) for x in ['visits_sel.csv.gz','visits_sel2.csv.gz']]).drop_duplicates()
    groups=[x for x in v.groupby('sdss_id') if x[0] in ids]; print(len(groups),flush=True)
    with mp.Pool(8) as pool: res=list(pool.imap_unordered(run,groups))
    pd.DataFrame(res).to_csv('joker_dense.csv',index=False); print('done')
