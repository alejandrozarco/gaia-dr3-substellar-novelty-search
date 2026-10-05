import numpy as np, pandas as pd
from scipy.optimize import brentq
pd.set_option('display.width',320); pd.set_option('display.max_colwidth',45)
d=pd.read_csv('joker_dense.csv'); j=pd.read_csv('joker_lite2.csv.gz',dtype={'gaia':str}); g=pd.read_csv('gate_out.csv',dtype={'gaia':str})
m=d.merge(j[['sdss_id','gaia','ns5','n17','base_d','span','teff','logg']],on='sdss_id').merge(g.drop(columns=['sdss_id']),on='gaia',how='left')
fallback=np.where(m.logg<3.5,1.2,((m.teff/5772)**2).clip(0.3,2.0))
m["mass_flame"]=pd.to_numeric(m.mass_flame,errors="coerce"); m["M1"]=m.mass_flame.fillna(pd.Series(fallback,index=m.index)); m['M1_src']=np.where(m.mass_flame.notna(),'FLAME','heur')
def m2(f,M1):
    f=float(f); M1=float(M1)
    if not np.isfinite(f) or f<=0: return np.nan
    return brentq(lambda x: x**3/(M1+x)**2-f,1e-4,1e4)
m['M2min_lo']=[m2(f,M) for f,M in zip(m.f_lo,m.M1)]; m['M2min_best']=[m2(f,M) for f,M in zip(m.f_best,m.M1)]
m['ratio']=m.M2min_lo/m.M1
m.to_csv('ranked_all.csv',index=False)
cols=['gaia','n','ns5','n17','base_d','span','teff','logg','chi2r_min','n_win','Pwin_min','Pwin_max','P_best','K_best','e_best','f_lo','f_best','M1','M1_src','M2min_lo','M2min_best','ratio','ruwe','phot_g_mean_mag','parallax_over_error']
print(m.sort_values('ratio',ascending=False)[cols].round(3).head(40).to_string())
