import requests, io, time, pandas as pd
CAS="https://skyserver.sdss.org/dr20/SkyServerWS/SearchTools/SqlSearch"
d=pd.read_csv('agg_m2min.csv.gz',dtype={'gaia':str})
s=d[(d.span>20)&~d.sdss_id.isin(pd.read_csv("visits_sel.csv.gz").sdss_id.unique())]
ids=s.sdss_id.astype(int).astype(str).tolist(); print('stars',len(ids),flush=True)
cols="sdss_id, gaia_dr3_source_id, release, telescope, field, fiber, mjd, jd, v_rad, v_rel, e_v_rel, bc, spectrum_flags, doppler_teff, doppler_logg, doppler_fe_h, doppler_rchi2, doppler_flags, xcorr_v_rad, xcorr_e_v_rel, ccfwhm, autofwhm, n_components"
out=[];holes=[]
for i in range(0,len(ids),300):
    sql=f"SELECT {cols} FROM mwm_apogee_allvisit WHERE sdss_id IN ({','.join(ids[i:i+300])})"
    ok=False
    for k in range(4):
        try:
            r=requests.get(CAS,params=dict(cmd=sql,format="csv"),timeout=600)
            if r.status_code==200 and r.text.startswith('#Table'):
                out.append(pd.read_csv(io.StringIO(r.text.split('\n',1)[1]),dtype={'gaia_dr3_source_id':str})); ok=True; break
        except Exception as e: pass
        time.sleep(5+5*k)
    if not ok: holes.append(i); print('HOLE',i,flush=True)
v=pd.concat(out); v.to_csv('visits_sel2.csv.gz',index=False)
print('rows',len(v),'stars',v.sdss_id.nunique(),'holes',holes)
