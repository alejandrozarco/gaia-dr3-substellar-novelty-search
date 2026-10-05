import io, requests, pandas as pd, numpy as np
from astropy.table import Table
t=pd.read_csv('targets.csv')
def vot(df):
    b=io.BytesIO(); Table.from_pandas(df).write(b,format='votable'); b.seek(0); return b
def tap(q,df):
    r=requests.post('https://tapvizier.cds.unistra.fr/TAPVizieR/tap/sync',data=dict(REQUEST='doQuery',LANG='ADQL',FORMAT='csv',QUERY=q,UPLOAD='u,param:u'),files={'u':('u.xml',vot(df),'application/x-votable+xml')},timeout=900)
    print(r.status_code,len(r.text),flush=True); r.raise_for_status(); return pd.read_csv(io.StringIO(r.text))
C=pd.DataFrame([dict(name='CTRL_AMHer',ra=274.05458,dec=49.86778)])
U=pd.concat([t[['Name','RAdeg','DEdeg']].rename(columns={'Name':'name','RAdeg':'ra','DEdeg':'dec'}),C])
q="""SELECT u.name, g.Source, g.Gmag, g."BP-RP", g.Plx, g.e_Plx, g.pmRA, g.e_pmRA, g.pmDE, g.e_pmDE, g.RUWE, g.PQSO, g.PGal, g.QSO, g.Gal, g.GLON, g.GLAT,
DISTANCE(POINT('ICRS',g.RA_ICRS,g.DE_ICRS),POINT('ICRS',u.ra,u.dec))*3600 AS sep
FROM TAP_UPLOAD.u AS u JOIN "I/355/gaiadr3" AS g ON 1=CONTAINS(POINT('ICRS',g.RA_ICRS,g.DE_ICRS),CIRCLE('ICRS',u.ra,u.dec,3/3600.))"""
n=tap(q,U); n.to_csv('gaia_nb3.csv',index=False)
print('control AM Her:',n[n.name=='CTRL_AMHer'][['Source','Gmag','sep']].values.tolist())
print('own source found:',sum(int(s) in set(n.Source) for s in t.Source),'/',len(t))
q="""SELECT u.name, w.AllWISE, w.W1mag, w.W2mag, w.W3mag, w.W4mag, w.Jmag, w.Hmag, w.Kmag, w.ccf, w.qph,
DISTANCE(POINT('ICRS',w.RAJ2000,w.DEJ2000),POINT('ICRS',u.ra,u.dec))*3600 AS sep
FROM TAP_UPLOAD.u AS u JOIN "II/328/allwise" AS w ON 1=CONTAINS(POINT('ICRS',w.RAJ2000,w.DEJ2000),CIRCLE('ICRS',u.ra,u.dec,3/3600.))"""
w=tap(q,U); w.to_csv('allwise3.csv',index=False)
print('WISE control:',w[w.name=='CTRL_AMHer'][['AllWISE','W1mag','W2mag']].values.tolist(),'matched',w.name.nunique()-1)
