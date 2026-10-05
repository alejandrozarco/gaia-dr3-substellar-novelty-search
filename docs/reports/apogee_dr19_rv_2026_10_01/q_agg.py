import requests, io, pandas as pd, sys
CAS="https://skyserver.sdss.org/dr20/SkyServerWS/SearchTools/SqlSearch"
good="v_rad > -999 and e_v_rel>0 and e_v_rel<2"
sql=f"""SELECT sdss_id, max(gaia_dr3_source_id) gaia, count(*) n, sum(case when release='sdss5' then 1 else 0 end) ns5,
sum(case when release='dr17' then 1 else 0 end) n17, max(v_rad)-min(v_rad) span, stdev(v_rad) sd, avg(v_rad) vmean, avg(e_v_rel) emean, max(e_v_rel) emax,
min(mjd) mjd0, max(mjd) mjd1, max(n_components) ncomp_max, avg(doppler_teff) teff, avg(doppler_logg) logg, avg(doppler_rchi2) rchi2, max(doppler_rchi2) rchi2max,
max(spectrum_flags) fl_max, avg(plx) plx, avg(e_plx) e_plx, avg(g_mag) g, avg(bp_mag) bp, avg(rp_mag) rp, avg(ra) ra, avg(dec) dec, avg(r_med_geo) dist, avg(ebv) ebv, avg(h_mag) h
FROM mwm_apogee_allvisit WHERE {good} GROUP BY sdss_id
HAVING count(*)>=3 and sum(case when release='sdss5' then 1 else 0 end)>=1"""
r=requests.get(CAS,params=dict(cmd=sql,format="csv"),timeout=1500)
t=r.text; print(r.status_code, t[:200] if not t.startswith('#Table') else '')
df=pd.read_csv(io.StringIO(t.split('\n',1)[1]),dtype={'gaia':str})
df.to_csv('agg_ge3_s5.csv.gz',index=False); print(len(df)); print(df.describe().T[['count','50%','max']])
