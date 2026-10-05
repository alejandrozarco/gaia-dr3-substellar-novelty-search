import io, requests, pandas as pd, numpy as np, datetime
from astropy.table import Table
def now(): return datetime.datetime.now(datetime.UTC).strftime('%Y-%m-%dT%H:%M:%SZ')
t=pd.read_csv('targets.csv')
def vot(df):
    b=io.BytesIO(); Table.from_pandas(df).write(b,format='votable'); b.seek(0); return b
def tap(url,q,df,fmt='csv'):
    r=requests.post(url,data=dict(REQUEST='doQuery',LANG='ADQL',FORMAT=fmt,QUERY=q,UPLOAD='u,param:u'),files={'u':('u.xml',vot(df),'application/x-votable+xml')},timeout=900)
    print(url,r.status_code,len(r.text)); r.raise_for_status(); return pd.read_csv(io.StringIO(r.text))
# ---- SIMBAD 10" with control AM Her
U=pd.concat([t[['Name','RAdeg','DEdeg']],pd.DataFrame([dict(Name='CTRL_AMHer',RAdeg=274.05458,DEdeg=49.86778)])]).rename(columns={'Name':'name','RAdeg':'ra','DEdeg':'dec'})
ts=now()
q="""SELECT u.name, b.main_id, b.otype, DISTANCE(POINT('ICRS',b.ra,b.dec),POINT('ICRS',u.ra,u.dec))*3600 AS sep
FROM TAP_UPLOAD.u AS u JOIN basic AS b ON 1=CONTAINS(POINT('ICRS',b.ra,b.dec),CIRCLE('ICRS',u.ra,u.dec,10/3600.))"""
s=tap('https://simbad.cds.unistra.fr/simbad/sim-tap/sync',q,U)
print('SIMBAD control:',s[s.name=='CTRL_AMHer'][['main_id','otype','sep']].values.tolist())
s['simbad_ts']=ts; s.to_csv('simbad10.csv',index=False)
# ---- Gaia DR3 neighbours within 3" + DSC + own astrometry ; control: Gaia DR3 id of AM Her region
U=t[['Name','RAdeg','DEdeg','Source']].rename(columns={'Name':'name','RAdeg':'ra','DEdeg':'dec','Source':'sid'})
q="""SELECT u.name, u.sid, g.source_id, g.phot_g_mean_mag, g.bp_rp, g.parallax, g.parallax_over_error,
DISTANCE(POINT('ICRS',g.ra,g.dec),POINT('ICRS',u.ra,u.dec))*3600 AS sep
FROM TAP_UPLOAD.u AS u JOIN gaiadr3.gaia_source AS g ON 1=CONTAINS(POINT('ICRS',g.ra,g.dec),CIRCLE('ICRS',u.ra,u.dec,3/3600.))"""
n=tap('https://gea.esac.esa.int/tap-server/tap/sync',q,U)
n.to_csv('gaia_nb3.csv',index=False)
print('own source found:',(n.source_id==n.sid).sum(),'/',len(t))
q="""SELECT u.name, a.source_id, a.classprob_dsc_combmod_quasar AS p_qso, a.classprob_dsc_combmod_galaxy AS p_gal, a.classprob_dsc_combmod_star AS p_star,
g.pmra, g.pmdec, g.pmra_error, g.pmdec_error, g.parallax, g.parallax_error, g.ruwe, g.phot_bp_rp_excess_factor, g.ipd_frac_multi_peak, g.in_qso_candidates, g.in_galaxy_candidates, g.l, g.b
FROM TAP_UPLOAD.u AS u JOIN gaiadr3.gaia_source AS g ON g.source_id=u.sid LEFT JOIN gaiadr3.astrophysical_parameters AS a ON a.source_id=u.sid"""
d=tap('https://gea.esac.esa.int/tap-server/tap/sync',q,U); d.to_csv('gaia_dsc.csv',index=False); print('dsc rows',len(d))
# ---- AllWISE 3" via VizieR TAP
q="""SELECT u.name, w.AllWISE, w.W1mag, w.W2mag, w.W3mag, w.W4mag, w.Jmag, w.Hmag, w.Kmag, w.ccf, w.qph,
DISTANCE(POINT('ICRS',w.RAJ2000,w.DEJ2000),POINT('ICRS',u.ra,u.dec))*3600 AS sep
FROM TAP_UPLOAD.u AS u JOIN "II/328/allwise" AS w ON 1=CONTAINS(POINT('ICRS',w.RAJ2000,w.DEJ2000),CIRCLE('ICRS',u.ra,u.dec,3/3600.))"""
U2=pd.concat([U[['name','ra','dec']],pd.DataFrame([dict(name='CTRL_AMHer',ra=274.05458,dec=49.86778)])])
w=tap('https://tapvizier.cds.unistra.fr/TAPVizieR/tap/sync',q,U2); w.to_csv('allwise3.csv',index=False)
print('WISE control:',w[w.name=='CTRL_AMHer'].values.tolist(),'matched',w.name.nunique()-1)
