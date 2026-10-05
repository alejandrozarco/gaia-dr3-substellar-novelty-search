import warnings; warnings.filterwarnings('ignore')
import pyvo, numpy as np, time
from astropy.table import Table, vstack
from concurrent.futures import ThreadPoolExecutor
svc=pyvo.dal.TAPService('https://archive.cefca.es/catalogues/vo/tap/jplus-dr3')
s=Table.read('gf21_ctrl_infoot.ecsv')
dt=2017.4-2016.0
def one(i):
    r=s[i]
    pmra=0 if np.ma.is_masked(r['pmRA']) else float(r['pmRA']); pmde=0 if np.ma.is_masked(r['pmDE']) else float(r['pmDE'])
    ra=float(r['RA_ICRS'])+pmra*dt/3.6e6/np.cos(np.radians(float(r['DE_ICRS']))); de=float(r['DE_ICRS'])+pmde*dt/3.6e6
    q=f"""SELECT o.tile_id,o.number,o.alpha_j2000,o.delta_j2000,o.class_star,o.flags,o.mask_flags,p.mag_aper_cor_3_0,p.mag_err_aper_3_0,p.mag_aper_cor_6_0,p.mag_err_aper_6_0
    FROM jplus.MagABDualObj o JOIN jplus.MagABDualPointSources p ON p.tile_id=o.tile_id AND p.number=o.number
    WHERE 1=CONTAINS(POINT('ICRS',o.alpha_j2000,o.delta_j2000),CIRCLE('ICRS',{ra},{de},0.0006))"""
    for k in range(3):
        try:
            t=svc.search(q).to_table()
            rows=[]
            for x in t:
                sep=3600*np.hypot((x['alpha_j2000']-ra)*np.cos(np.radians(de)),x['delta_j2000']-de)
                rows.append(dict(gid=int(r['GaiaEDR3']),sep=sep,tile_id=int(x['tile_id']),number=int(x['number']),class_star=float(x['class_star']),
                    flags=np.array(x['flags'],float),mask_flags=np.array(x['mask_flags'],float),
                    m3=np.array(x['mag_aper_cor_3_0'],float),e3=np.array(x['mag_err_aper_3_0'],float),
                    m6=np.array(x['mag_aper_cor_6_0'],float),e6=np.array(x['mag_err_aper_6_0'],float)))
            return ('ok',rows)
        except Exception as e:
            err=str(e)[:100]; time.sleep(2)
    return ('fail',err)
t0=time.time()
with ThreadPoolExecutor(8) as ex: res=list(ex.map(one,range(len(s))))
nf=sum(1 for r in res if r[0]=='fail'); rows=[x for r in res if r[0]=='ok' for x in r[1]]
print('queries',len(res),'failed',nf,'matched rows',len(rows),'unique WDs',len(set(x['gid'] for x in rows)),'time %.0fs'%(time.time()-t0))
import pickle; pickle.dump(rows,open('jplus_ctrl_rows.pkl','wb'))
