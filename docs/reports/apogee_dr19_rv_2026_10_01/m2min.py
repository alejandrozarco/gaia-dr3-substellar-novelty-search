"""Roche-limit minimum companion mass from APOGEE RV span (SDSS-V DR20 = DR19 APOGEE visits, CAS mwm_apogee_allvisit).
K >= span/2 (any orbit). P >= P_roche(M1,R1,q) (primary inside its Roche lobe, Eggleton 1983). f(M)=P K^3/(2 pi G) rises with P,
so M2_min solves M2^3/(M1+M2)^2 = P_roche(M2) K^3/(2 pi G) with sin i = 1. R1 from Gaia G, distance, BC_G(Teff) (Andrae+2018), A_G=2.74 E(B-V).
M1 = g R1^2/G from Doppler logg, clipped to [0.5, 4] Msun; also M2_min with M1 fixed at 0.8 (conservative low)."""
import numpy as np, pandas as pd
G=6.674e-11; Ms=1.989e30; Rs=6.957e8
d=pd.read_csv('agg_ge3_s5.csv.gz',dtype={'gaia':str})
T=d.teff.clip(3300,8000)
x=T-5772
a=[6e-02,6.731e-05,-6.647e-08,2.859e-11,-7.197e-15]; b=[1.749,1.977e-03,3.737e-07,-8.966e-11,-4.183e-14]
bc=np.where(T>=4000,sum(c*x**i for i,c in enumerate(a)),sum(c*x**i for i,c in enumerate(b)))
ebv=d.ebv.where((d.ebv>=0)&(d.ebv<5),0.0)
dist=d.dist.where(d.dist>0, 1000/d.plx.where(d.plx>0))
MG=d.g-5*np.log10(dist)+5-2.74*ebv
L=10**(-0.4*(MG+bc-4.74))
R1=np.sqrt(L)*(5772/T)**2
M1=(10**d.logg.clip(-1,5.5)*1e-2*(R1*Rs)**2/G/Ms).clip(0.5,4)
def rl(q): q3=q**(1/3); return 0.49*q3**2/(0.6*q3**2+np.log(1+q3))
def solve(K,M1,R1):
    if not (np.isfinite(K) and np.isfinite(M1) and np.isfinite(R1)) or K<=0: return np.nan,np.nan
    lo,hi=1e-4,1e3
    def gfun(M2):
        a=R1*Rs/rl(M1/M2); P=2*np.pi*np.sqrt(a**3/(G*(M1+M2)*Ms))
        f=P*(K*1e3)**3/(2*np.pi*G)/Ms
        return M2**3/(M1+M2)**2-f, P/86400
    for _ in range(80):
        m=np.sqrt(lo*hi)
        if gfun(m)[0]>0: hi=m
        else: lo=m
    return hi, gfun(hi)[1]
K=d.span/2
res=[solve(k,m,r) for k,m,r in zip(K,M1,R1)]
d['K_min']=K; d['R1']=R1; d['M1']=M1; d['MG']=MG
d['M2_min']=[r[0] for r in res]; d['P_roche_d']=[r[1] for r in res]
d['M2_min_M1fix08']=[solve(k,0.8,r)[0] for k,r in zip(K,R1)]
d['sig_span']=d.span/np.sqrt(2*(d.emax**2+0.15**2))
d.to_csv('agg_m2min.csv.gz',index=False)
for c in [10,20,40]: print('span>',c, (d.span>c).sum(), ' new-only', ((d.span>c)&(d.n17==0)).sum())
s=d[(d.M2_min>d.M1)&(d.span>10)]
print('M2_min>M1 & span>10:',len(s),' new-only',(s.n17==0).sum())
print(s.sort_values('M2_min',ascending=False)[['gaia','n','ns5','n17','span','teff','logg','R1','M1','M2_min','P_roche_d','ncomp_max','rchi2max','g']].head(30).to_string())
