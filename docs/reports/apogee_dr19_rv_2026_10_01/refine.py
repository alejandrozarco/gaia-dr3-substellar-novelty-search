"""Multi-start Keplerian least squares (scipy) for lead stars; reports global best fit and the minimum f(M) among local optima
with chi2 < chi2_best + 9*max(1,chi2r_best). Separate gamma per release (dr17 vs sdss5) tested as variant B (zero-point check)."""
import numpy as np, pandas as pd, warnings; warnings.filterwarnings('ignore')
from scipy.optimize import least_squares
from joker_lite2 import clean, G, Ms
leads=['3915652143948425856','4159330274608577536','4154660751826105600','922653915433718528','573803404498815488','1455086202072140672',
       '956826251492879616','1547746273191378688','1332966434872717824','1607932955581396224','3608447113383815552','3633066969731521536']
v=pd.concat([pd.read_csv(x,dtype={'gaia_dr3_source_id':str}) for x in ['visits_sel.csv.gz','visits_sel2.csv.gz']]).drop_duplicates()
def kep(t,P,e,om,M0):
    M=(2*np.pi*t/P+M0)%(2*np.pi); E=M.copy()
    for _ in range(30): E=E-(E-e*np.sin(E)-M)/(1-e*np.cos(E))
    nu=2*np.arctan2(np.sqrt(1+e)*np.sin(E/2),np.sqrt(1-e)*np.cos(E/2)); return np.cos(om+nu)+e*np.cos(om)
rows=[]
for gid in leads:
    g=clean(v[v.gaia_dr3_source_id==gid]).sort_values('jd'); t=g.jd.values-2459000; y=g.v_rad.values
    lg=np.nanmedian(g.doppler_logg); s=0.3 if lg>3.5 else (0.7 if lg>2.5 else 1.5); sig=np.sqrt(g.e_v_rel.values**2+s**2)
    s5=(g.release=='sdss5').values.astype(float)
    for variant in ('A','B'):
        sols=[]
        for P0 in np.exp(np.linspace(np.log(1),np.log(5000),60)):
            for e0 in (0.1,0.5):
                for om0 in (0.5,2.5,4.5):
                    p0=[np.log(P0),np.arctanh(e0*2-1),om0,1.0,(y.max()-y.min())/2,y.mean(),0.0]
                    def res(p):
                        P=np.exp(p[0]); e=(np.tanh(p[1])+1)/2*0.95
                        mod=p[4]*kep(t,P,e,p[2],p[3])+p[5]+(p[6]*s5 if variant=='B' else 0)
                        return (y-mod)/sig
                    try: r=least_squares(res,p0,max_nfev=400)
                    except Exception: continue
                    P=np.exp(r.x[0]); e=(np.tanh(r.x[1])+1)/2*0.95; K=abs(r.x[4]); chi2=2*r.cost
                    sols.append((chi2,P,e,K,P*86400*(K*1e3)**3*(1-e**2)**1.5/(2*np.pi*G)/Ms,r.x[6] if variant=='B' else 0))
        S=pd.DataFrame(sols,columns=['chi2','P','e','K','f','dzp']); b=S.loc[S.chi2.idxmin()]; npar=6 if variant=='A' else 7
        c2r=max(1,b.chi2/max(len(y)-npar,1)); W=S[S.chi2<b.chi2+9*c2r]
        rows.append(dict(gaia=gid,variant=variant,n=len(y),chi2r=b.chi2/max(len(y)-npar,1),P=b.P,e=b.e,K=b.K,f_best=b.f,dzp=b.dzp,f_lo=W.f.min(),P_at_flo=W.loc[W.f.idxmin(),'P'],n_opt_in_win=len(W)))
    print(pd.DataFrame(rows[-2:]).round(3).to_string(index=False),flush=True)
pd.DataFrame(rows).to_csv('refine.csv',index=False)
