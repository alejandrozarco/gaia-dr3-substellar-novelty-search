import warnings; warnings.filterwarnings('ignore')
import pyvo, numpy as np
svc=pyvo.dal.TAPService('https://archive.cefca.es/catalogues/vo/tap/jplus-dr3')
F=['r','g','i','z','u','J0378','J0395','J0410','J0430','J0515','J0660','J0861']
t=svc.search("SELECT p.*, e.ebv, e.ax FROM jplus.MagABDualPointSources p JOIN jplus.MWExtinction e ON p.tile_id=e.tile_id AND p.number=e.number WHERE p.tile_id=95126 AND p.number=20949").to_table()
for c in t.colnames:
    v=np.array(t[c][0],dtype=float)
    print(c, dict(zip(F,np.round(v,3))) if v.size==12 else v)
d=svc.search("SELECT * FROM jplus.DuplicatedMagABDualObj WHERE 1=CONTAINS(POINT('ICRS',alpha_j2000,delta_j2000),CIRCLE('ICRS',211.79315,55.15827,0.0008))").to_table()
print('duplicates:',len(d)); 
for r in d: print(r['tile_id'],r['number'], np.round(np.array(r['mag_aper3_worstpsf'],float),3))
ti=svc.search("SELECT tile_id,filter_id,name,observation_dates,fwhmg,depth3arc5s,aper_cor_6_0,aper_cor_3_0 FROM jplus.TileImage WHERE ref_tile_id=95126 ORDER BY filter_id").to_table()
for r in ti: print(r['filter_id'],r['name'],str(r['observation_dates'])[:120],r['fwhmg'],r['depth3arc5s'],r['aper_cor_6_0'],r['aper_cor_3_0'])
