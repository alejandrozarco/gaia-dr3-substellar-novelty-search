import os
import pandas as pd, numpy as np, json, gzip
t=pd.read_csv('targets.csv'); P='../glc/'
# faint state from alert LC (95th percentile), bright state 5th pct
def lc(n):
    d=pd.read_csv(f'{P}{n}.csv',skiprows=1); d.columns=['date','jd','mag']; d['mag']=pd.to_numeric(d.mag,errors='coerce'); return d.dropna()
fs=[];bs=[]
for n in t.Name: m=lc(n).mag; fs.append(np.percentile(m,95)); bs.append(np.percentile(m,5))
t['faint95']=fs; t['bright05']=bs
# (a) VSX
v=pd.read_csv('vsx_full.csv'); v['vsx_le5']=v.vsx.fillna('[]').apply(lambda s:[x for x in json.loads(s or '[]') if x[2]<=5])
t=t.merge(v[['Name','vsx_ts','vsx_status','vsx','vsx_le5']],on='Name')
t['g_vsx']=np.where(t.vsx_status=='FAIL','HOLE',np.where(t.vsx_le5.str.len()>0,'FAIL','pass'))
# (b) microlensing lists
m=pd.read_csv('ml_lists.csv').fillna(''); t=t.merge(m,on='Name'); t['g_ml']=np.where(t.ml_all!='','FAIL','pass')
# (c) SIMBAD 10"
s=pd.read_csv('simbad10.csv'); s['name']=s.name.str.strip(); s=s[s.name!='CTRL_AMHer'].sort_values('sep')
S=s.groupby('name').apply(lambda x:'; '.join(f'{a} [{o}] {d:.1f}"' for a,o,d in zip(x.main_id,x.otype,x.sep))).rename('simbad10')
S2=s[s.sep<=2].groupby('name').apply(lambda x:'; '.join(f'{a} [{o}]' for a,o in zip(x.main_id,x.otype))).rename('simbad_le2')
t=t.join(S,on='Name').join(S2,on='Name'); t['simbad_ts']=s.simbad_ts.iloc[0]
# SIMBAD id <=2" with a variable/YSO/ml/CV otype = known; plain star/IR id = not a classification
known_ot=('Y*O','Y*-','Or*','TT*','Ae*','CV*','No*','DN*','Mi*','LP*','V*','Pl','EB*','SN','RCB','X','Be*','LM*','Ce*','RR*','QSO','AGN','G','Sy','Bla')
def simgate(r):
    if not isinstance(r.simbad_le2,str): return 'pass'
    ots=[x.rsplit('[',1)[1].rstrip(']') for x in r.simbad_le2.split('; ')]
    return 'FAIL' if any(o.startswith(k) for o in ots for k in known_ot) else 'pass(id only)'
t['g_simbad']=t.apply(simgate,axis=1)
# (d) neighbours
g=pd.read_csv('gaia_nb3.csv',dtype={'Source':'int64'}); g=g[g.name!='CTRL_AMHer']
for c in [c for c in g.columns[1:] if c!='Source']: g[c]=pd.to_numeric(g[c],errors='coerce')
nb=[];own=[]
for r in t.itertuples():
    x=g[g.name==r.Name]; o=x[x.Source==r.Source]; own.append(len(o))
    y=x[(x.Source!=r.Source)&(x.Gmag<r.faint95)]
    nb.append('; '.join(f'{int(a)} G={b:.2f} r={c:.2f}"' for a,b,c in zip(y.Source,y.Gmag,y._r)))
t['own_found']=own; t['nb_brighter3']=nb; t['g_blend']=np.where(t.nb_brighter3!='','FLAG','pass')
# (e) id lists
R=os.path.expanduser('~/claude_projects/gaia-recovered-2026-05-27/data/external_catalogs/recent_id_lists/')
sch=set(int(l) for l in open(R+'schwope2026_erass1_new_cvs_arXiv2607.28066_gaia_ids.txt') if l.strip().isdigit())
sw=pd.read_csv(R+'swan2026_desi_dr1_wd_catalogue_arXiv2609.04314.csv.gz',usecols=['designation','specType'])
swid=dict(zip(sw.designation.str.replace(r'Gaia DR[23] ','',regex=True).astype('int64'),sw.specType))
t['idlist']=[('Schwope2026' if s in sch else '')+(f'Swan2026:{swid[s]}' if s in swid else '') for s in t.Source]
t['g_idlist']=np.where(t.idlist!='','FAIL','pass')
print('id-list sizes',len(sch),len(swid),'; control: first Schwope id present in set',next(iter(sch)) in sch)
# (f) quasar
o=g.merge(t[['Name','Source']],left_on=['name','Source'],right_on=['Name','Source'])
o['pmsig2']=np.hypot(o.pmRA/o.e_pmRA,o.pmDE/o.e_pmDE); o['plxsig']=o.Plx/o.e_Plx
t=t.merge(o[['Name','PQSO','PGal','QSO','Gal','pmsig2','plxsig']],on='Name',how='left')
t['g_qso']=np.where((t.PQSO>0.5)|(t.PGal>0.5)|((t.plxsig<3)&(t.pmsig2<5)),'FAIL',np.where(t.QSO==1,'pass(qso-cand flag)','pass'))
# WISE
w=pd.read_csv('allwise3.csv'); w[['W1mag','W2mag','W3mag','W4mag','Jmag','Hmag','Kmag']]=w[['W1mag','W2mag','W3mag','W4mag','Jmag','Hmag','Kmag']].apply(pd.to_numeric,errors='coerce'); w=w[w.name!='CTRL_AMHer'].sort_values('_r').drop_duplicates('name')
t=t.merge(w.drop(columns='_r').rename(columns={'name':'Name'}),on='Name',how='left')
t['W1-W2']=t.W1mag-t.W2mag; t['W2-W3']=t.W2mag-t.W3mag
from astropy.coordinates import SkyCoord; import astropy.units as u
c=SkyCoord(t.RAdeg.values*u.deg,t.DEdeg.values*u.deg); t['l']=c.galactic.l.deg; t['b']=c.galactic.b.deg
G=['g_vsx','g_ml','g_simbad','g_idlist','g_qso','g_blend']
for k in G: print(k,t[k].value_counts().to_dict())
hard=['g_vsx','g_ml','g_simbad','g_idlist','g_qso']
t['survive']=~t[hard].isin(['FAIL']).any(axis=1)&~t[hard].isin(['HOLE']).any(axis=1)
print('survive hard gates',t.survive.sum(),' of which blend-flag',(t.survive&(t.g_blend=='FLAG')).sum())
print('own source found in 3" cone', (t.own_found>0).sum())
t.to_csv('gates.csv',index=False)
print(t[~t.survive][['Name']+hard+['simbad_le2','ml_all','idlist']].to_string())
