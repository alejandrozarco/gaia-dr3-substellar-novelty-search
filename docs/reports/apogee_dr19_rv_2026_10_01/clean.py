import numpy as np, pandas as pd, itertools
from roche import solve, rl
A=pd.read_csv('agg_m2min.csv.gz',dtype={'gaia':str}).set_index('sdss_id')
v=pd.read_csv('visits_sel.csv.gz',dtype={'gaia_dr3_source_id':str})
REJ=sum(1<<b for b in [3,4,9,16,17,18,19,20,21,22])
v['ok']=(v.v_rad>-999)&(v.e_v_rel>0)&(v.e_v_rel<2)&((v.spectrum_flags.fillna(0).astype(np.int64)&REJ)==0)&(v.v_rad.abs()<500)&(v.doppler_rchi2>0)
v['dx']=(v.xcorr_v_rad-v.v_rad)
v['ok']&=(v.dx.abs()<5)
rows=[]
for sid,g in v.groupby('sdss_id'):
    g=g[g.ok]; 
    if len(g)>0: g=g[g.doppler_rchi2<max(10,5*g.doppler_rchi2.median())]
    if len(g)<3 or (g.release=='sdss5').sum()<1: continue
    rv=g.v_rad.values; sp=rv.max()-rv.min()
    loo=min((np.delete(rv,i).max()-np.delete(rv,i).min()) for i in range(len(rv)))
    a=A.loc[sid]
    m2,P=solve(loo/2,a.M1,a.R1); m2f,P2=solve(sp/2,a.M1,a.R1)
    # shortest time between the two visits that define the robust span, and max |dV/dt|
    t=g.mjd.values; o=np.argsort(t); dvdt=np.max(np.abs(np.diff(rv[o]))/np.maximum(np.diff(t[o]),0.5)) if len(t)>1 else np.nan
    rows.append(dict(sdss_id=sid,gaia=a.gaia,n_clean=len(g),ns5=(g.release=='sdss5').sum(),n17=(g.release=='dr17').sum(),base_d=t.max()-t.min(),
        span_clean=sp,span_loo=loo,emax=g.e_v_rel.max(),rchi2_med=g.doppler_rchi2.median(),teff=g.doppler_teff.median(),logg=g.doppler_logg.median(),
        teff_sd=g.doppler_teff.std(),ncomp_max=g.n_components.max(),fwhm_ratio=(g.ccfwhm/g.autofwhm).median(),dvdt_max=dvdt,
        R1=a.R1,M1=a.M1,MG=a.MG,g=a.g,bp_rp=a.bp-a.rp,plx=a.plx,e_plx=a.e_plx,ra=a.ra,dec=a.dec,M2_min_loo=m2,P_roche_d=P,M2_min_full=m2f))
r=pd.DataFrame(rows); r['ratio']=r.M2_min_loo/r.M1
r.to_csv('clean_m2.csv.gz',index=False)
print('stars with >=3 clean visits:',len(r))
q=r[(r.ratio>1)]
print('M2_min(loo)>M1:',len(q),' new-only',(q.n17==0).sum())
q2=q[(q.teff.between(3500,7000))&(q.ncomp_max<=1)&(q.fwhm_ratio<1.5)]
print('… & Teff 3500-7000 & no SB2 & fwhm ok:',len(q2))
pd.set_option('display.width',250)
print(q2.sort_values('ratio',ascending=False)[['gaia','n_clean','ns5','n17','base_d','span_clean','span_loo','teff','logg','R1','M1','M2_min_loo','P_roche_d','rchi2_med','fwhm_ratio','g','bp_rp','MG']].head(60).round(2).to_string())
