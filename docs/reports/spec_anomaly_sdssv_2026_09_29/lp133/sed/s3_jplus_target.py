import warnings; warnings.filterwarnings('ignore')
import pyvo, numpy as np
svc=pyvo.dal.TAPService('https://archive.cefca.es/catalogues/vo/tap/jplus-dr3')
f=svc.search('SELECT * FROM jplus.Filter').to_table()
print(f)
q="""SELECT m.tile_id,m.number,m.alpha_j2000,m.delta_j2000,m.class_star,m.flags,m.mask_flags,m.fwhm_world,
m.mag_psfcor,m.mag_err_psfcor,m.mag_aper3_worstpsf,m.mag_err_aper3_worstpsf,m.mag_auto,m.mag_err_auto,m.mag_aper_6_0,m.mag_err_aper_6_0
FROM jplus.MagABDualObj m WHERE 1=CONTAINS(POINT('ICRS',m.alpha_j2000,m.delta_j2000),CIRCLE('ICRS',211.7925,55.1590,0.006))"""
t=svc.search(q).to_table()
print(len(t))
for r in t:
    print(r['tile_id'],r['number'],r['alpha_j2000'],r['delta_j2000'],r['class_star'])
    for c in ['mag_psfcor','mag_err_psfcor','mag_aper3_worstpsf','mag_err_aper3_worstpsf','mag_aper_6_0','flags','mask_flags']:
        print('  ',c,np.round(np.array(r[c],dtype=float),3))
t.write('jplus_target_raw.ecsv',overwrite=True)
tt=svc.search("SELECT * FROM jplus.TileImage WHERE tile_id IN (%s)"%','.join(str(x) for x in set(t['tile_id']))).to_table() if len(t) else None
if tt is not None: print(tt.colnames); print(tt[[c for c in tt.colnames if c in ('tile_id','filter_id','date_obs','name','ref_tile_id')]])
