import pandas as pd, requests, io
from astropy.table import Table
s=pd.read_csv('g2_novsxviz.csv')
# include a positive control: SS Cyg
t=Table.from_pandas(pd.concat([s[['Name','RAdeg','DEdeg']], pd.DataFrame([dict(Name='CTRL_SSCyg',RAdeg=325.67854,DEdeg=43.58617)])]))
t.rename_columns(['Name','RAdeg','DEdeg'],['name','ra','dec'])
b=io.BytesIO(); t.write(b,format='votable'); b.seek(0)
q="""SELECT u.name, b.main_id, b.otype, DISTANCE(POINT('ICRS',b.ra,b.dec),POINT('ICRS',u.ra,u.dec))*3600 AS sep
FROM TAP_UPLOAD.u AS u JOIN basic AS b ON 1=CONTAINS(POINT('ICRS',b.ra,b.dec),CIRCLE('ICRS',u.ra,u.dec,5/3600.))"""
r=requests.post('https://simbad.cds.unistra.fr/simbad/sim-tap/sync',data=dict(request='doQuery',lang='adql',format='csv',query=q,upload='u,param:u'),files={'u':('u.xml',b,'application/x-votable+xml')},timeout=600)
print(r.status_code); open('simbad5.csv','w').write(r.text)
d=pd.read_csv('simbad5.csv'); print(len(d), d.name.nunique(), 'control:', d[d.name=='CTRL_SSCyg'].values.tolist())
d=d.sort_values('sep').drop_duplicates('name'); print(d.otype.value_counts().head(30))
