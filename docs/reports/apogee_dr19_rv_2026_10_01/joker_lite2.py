"""Joker-style rejection sampling (Price-Whelan+2017 approach, simplified: profile likelihood over K, v0) on cleaned APOGEE visits
(SDSS-V DR20 CAS mwm_apogee_allvisit; release dr17 + sdss5/apred 1.3). Prior: lnP U[ln 0.3, ln 5000] d, e ~ Beta(0.867,3.03) clipped 0.9,
omega, M0 uniform. Jitter s added in quadrature: 0.3 km/s (logg>3.5), 0.7 (2.5-3.5), 1.5 (<2.5). Output: posterior percentiles of P, K, e, f(M)."""
import numpy as np, pandas as pd, multiprocessing as mp
G=6.674e-11; Ms=1.989e30
NS=2**17; rng=np.random.default_rng(42)
lnP=rng.uniform(np.log(0.3),np.log(5000),NS); P=np.exp(lnP); e=np.clip(rng.beta(0.867,3.03,NS),0,0.9)
om=rng.uniform(0,2*np.pi,NS); M0=rng.uniform(0,2*np.pi,NS)
REJ=sum(1<<b for b in [3,4,9,16,17,18,19,20,21,22])
def clean(g):
    ok=(g.v_rad>-999)&(g.e_v_rel>0)&(g.e_v_rel<2)&((g.spectrum_flags.fillna(0).astype(np.int64)&REJ)==0)&(g.v_rad.abs()<500)&(g.doppler_rchi2>0)&((g.xcorr_v_rad-g.v_rad).abs()<5)
    g=g[ok]
    if len(g): g=g[g.doppler_rchi2<max(10,5*g.doppler_rchi2.median())]
    return g
def run(args):
    try: return run0(args)
    except Exception as ex: return dict(sdss_id=args[0],fail=repr(ex)[:80])
def run0(args):
    sid,g=args
    g=clean(g)
    if len(g)<3 or (g.release=='sdss5').sum()<1: return None
    g=g.sort_values('jd'); t=g.jd.values-2459000.0; y=g.v_rad.values; y=y-np.average(y,weights=1/(g.e_v_rel.values**2+0.09))
    lg=np.nanmedian(g.doppler_logg); s=0.3 if lg>3.5 else (0.7 if lg>2.5 else 1.5)
    w=1/(g.e_v_rel.values**2+s**2)
    Mn=(2*np.pi*t[None,:]/P[:,None]+M0[:,None])%(2*np.pi); E=Mn.copy()
    for _ in range(12): E=E-(E-e[:,None]*np.sin(E)-Mn)/(1-e[:,None]*np.cos(E))
    nu=2*np.arctan2(np.sqrt(1+e)[:,None]*np.sin(E/2),np.sqrt(1-e)[:,None]*np.cos(E/2))
    X=np.cos(om[:,None]+nu)+e[:,None]*np.cos(om)[:,None]
    Sw=w.sum(); Sx=(w*X).sum(1); Sxx=(w*X*X).sum(1); Sy=(w*y).sum(); Sxy=(w*X*y).sum(1); Syy=(w*y*y).sum()
    det=Sw*Sxx-Sx**2; det=np.where(np.abs(det)<1e-12,1e-12,det)
    K=(Sw*Sxy-Sx*Sy)/det; v0=(Sy-K*Sx)/Sw
    chi2=Syy-2*K*Sxy-2*v0*Sy+K*K*Sxx+2*K*v0*Sx+v0*v0*Sw
    bad=(np.abs(K)>400)|(np.abs(det)<=1e-12*Sw*Sw); chi2=np.where(bad|~np.isfinite(chi2),np.inf,chi2)
    if not np.isfinite(chi2.min()): return dict(sdss_id=sid,gaia=str(g.gaia_dr3_source_id.iloc[0]),n=len(g),fail='no_finite_sample')
    c0=np.sum(w*(y-np.sum(w*y)/Sw)**2)
    acc=np.random.default_rng(int(sid)%2**31).uniform(size=NS)<np.exp(-(chi2-chi2.min())/2)
    Ka=np.abs(K[acc]); Pa=P[acc]; ea=e[acc]
    f=Pa*86400*(Ka*1e3)**3*(1-ea**2)**1.5/(2*np.pi*G)/Ms
    c2r=max(1.0,chi2.min()/max(len(y)-3,1)); win=chi2<chi2.min()+9*c2r
    fw=P[win]*86400*(np.abs(K[win])*1e3)**3*(1-e[win]**2)**1.5/(2*np.pi*G)/Ms
    i_lo=np.argmin(fw); Plo=P[win][i_lo]; Klo=abs(K[win][i_lo])
    q=lambda a,p: float(np.percentile(a,p))
    return dict(sdss_id=sid,gaia=str(g.gaia_dr3_source_id.iloc[0]),n=len(g),ns5=int((g.release=='sdss5').sum()),n17=int((g.release=='dr17').sum()),
        base_d=t.max()-t.min(),span=y.max()-y.min(),jit=s,logg=lg,teff=float(np.nanmedian(g.doppler_teff)),ncomp_max=g.n_components.max(),
        fwhm_ratio=float(np.nanmedian(g.ccfwhm/g.autofwhm)),chi2_const=c0,chi2_min=float(chi2.min()),n_acc=int(acc.sum()),
        P_1=q(Pa,1),P_50=q(Pa,50),P_99=q(Pa,99),K_1=q(Ka,1),K_50=q(Ka,50),e_50=q(ea,50),f_1=q(f,1),f_5=q(f,5),f_50=q(f,50),f_lo=float(fw.min()),P_at_flo=float(Plo),K_at_flo=float(Klo),n_win=int(win.sum()),Pwin_min=float(P[win].min()),Pwin_max=float(P[win].max()))
if __name__=='__main__':
    v=pd.concat([pd.read_csv(x,dtype={'gaia_dr3_source_id':str}) for x in ['visits_sel.csv.gz','visits_sel2.csv.gz']]).drop_duplicates()
    ids=set(pd.read_csv('rerun_ids.csv').sdss_id); groups=[x for x in v.groupby('sdss_id') if x[0] in ids]
    with mp.Pool(8) as pool: res=[r for r in pool.imap_unordered(run,groups,chunksize=8) if r is not None]
    r=pd.DataFrame(res); r.to_csv('joker_lite2.csv.gz',index=False)
    print(len(groups),'stars in;',len(r),'with >=3 clean visits incl. SDSS-V')
    print((r.f_lo>0.25).sum(),'f_lo>0.25;',(r.f_lo>0.5).sum(),'f_lo>0.5');print((r.f_1>0.25).sum(),'with f_1pct>0.25;',(r.f_1>0.5).sum(),'>0.5;',(r.f_1>1).sum(),'>1')
