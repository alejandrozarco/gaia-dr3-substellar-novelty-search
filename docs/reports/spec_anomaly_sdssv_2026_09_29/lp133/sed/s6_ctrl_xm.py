import warnings; warnings.filterwarnings('ignore')
import pyvo, numpy as np
from astropy.table import Table
svc=pyvo.dal.TAPService('https://archive.cefca.es/catalogues/vo/tap/jplus-dr3')
s=Table.read('gf21_ctrl_pool.ecsv')
dt=2017.4-2016.0
ra=np.array(s['RA_ICRS'])+np.nan_to_num(np.array(s['pmRA']))*dt/3.6e6/np.cos(np.radians(s['DE_ICRS']))
de=np.array(s['DE_ICRS'])+np.nan_to_num(np.array(s['pmDE']))*dt/3.6e6
up=Table({'gid':np.array(s['GaiaEDR3']).astype(np.int64),'ra':ra,'dec':de})
q="""SELECT u.gid, u.ra AS ura, u.dec AS udec, o.tile_id, o.number, o.alpha_j2000, o.delta_j2000, o.class_star, o.flags, o.mask_flags,
p.mag_aper_cor_3_0, p.mag_err_aper_3_0, p.mag_aper_cor_6_0, p.mag_err_aper_6_0
FROM TAP_UPLOAD.pool u JOIN jplus.MagABDualObj o ON 1=CONTAINS(POINT('ICRS',o.alpha_j2000,o.delta_j2000),CIRCLE('ICRS',u.ra,u.dec,0.0005))
JOIN jplus.MagABDualPointSources p ON p.tile_id=o.tile_id AND p.number=o.number"""
try:
    job=svc.submit_job(q,uploads={'pool':up}); job.run(); job.wait(timeout=900)
    print(job.phase)
    t=job.fetch_result().to_table()
except Exception as e:
    print('async failed',type(e).__name__,str(e)[:300])
    t=svc.search(q,uploads={'pool':up}).to_table()
print(len(t), len(set(t['gid'])))
t.write('jplus_ctrl_raw.ecsv',overwrite=True)
