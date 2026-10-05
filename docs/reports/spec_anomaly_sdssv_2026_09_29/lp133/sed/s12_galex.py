import warnings; warnings.filterwarnings('ignore')
import numpy as np, json
from astroquery.mast import Observations, Catalogs
from astroquery.vizier import Vizier
from astropy.coordinates import SkyCoord
import astropy.units as u
g=json.load(open('gaia.json'))
dt=2007.0-2016.0
ra=g['RA_ICRS']+g['pmRA']*dt/3.6e6/np.cos(np.radians(g['DE_ICRS'])); de=g['DE_ICRS']+g['pmDE']*dt/3.6e6
c=SkyCoord(ra,de,unit='deg')
print('pos2007',ra,de)
o=Observations.query_region(c,radius=0.62*u.deg)
o=o[o['obs_collection']=='GALEX']
print('GALEX obs within 0.62 deg:',len(o))
seen=set()
for r in o:
    k=(r['obs_id'],r['filters'])
    if k in seen: continue
    seen.add(k)
    cc=SkyCoord(r['s_ra'],r['s_dec'],unit='deg')
    print(r['obs_id'],r['filters'],r['project'] if 'project' in o.colnames else '',r['t_exptime'],'tile-centre offset %.3f deg'%cc.separation(c).deg, r['target_name'])
for rad in [5,60]:
    v=Vizier(columns=['**','+_r'],row_limit=-1)
    for cid in ['II/335','II/312']:
        rr=v.query_region(c,radius=rad*u.arcsec if rad<10 else rad*u.arcsec,catalog=cid)
        print(cid,rad,'arcsec ->',[(k,len(rr[k])) for k in rr.keys()])
rr=Vizier(columns=['**','+_r'],row_limit=-1).query_region(c,radius=5*u.arcmin,catalog='II/335')
for k in rr.keys():
    t=rr[k]; print(k,len(t)); print([x for x in t.colnames][:40])
    t.sort('_r'); print(t[:8][[x for x in t.colnames if x in ('_r','RAJ2000','DEJ2000','FUVmag','e_FUVmag','NUVmag','e_NUVmag','Fexpt','Nexpt','fexptime','nexptime','FUVexp','NUVexp')]])
try:
    m=Catalogs.query_region(c,radius=0.003*u.deg,catalog='Galex')
    print('MAST Galex cat within 10.8":',len(m))
    for r in m: print(r['distance_arcmin']*60,r['fuv_mag'],r['nuv_mag'],r['fuv_exptime'] if 'fuv_exptime' in m.colnames else '',r['nuv_exptime'] if 'nuv_exptime' in m.colnames else '')
    m2=Catalogs.query_region(c,radius=0.08*u.deg,catalog='Galex')
    print('MAST Galex cat within 4.8 arcmin:',len(m2), 'cols',m2.colnames[:50])
    import collections
    print('survey', collections.Counter(list(m2['survey'])) if 'survey' in m2.colnames else '')
    print('nuv_exptime', np.unique(np.array(m2['nuv_exptime']))[:10], 'fuv_exptime', np.unique(np.array(m2['fuv_exptime']))[:10])
    m2.write('galex_mast_5arcmin.ecsv',overwrite=True)
except Exception as e: print('MAST cat ERR',e)
