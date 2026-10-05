import warnings; warnings.filterwarnings('ignore')
import pyvo, numpy as np
from astropy.table import Table
from astropy.coordinates import SkyCoord
import astropy.units as u
svc=pyvo.dal.TAPService('https://archive.cefca.es/catalogues/vo/tap/jplus-dr3')
ti=svc.search("SELECT tile_id,ra,dec FROM jplus.TileImage WHERE filter_id=9",maxrec=100000).to_table()
print('J0430 tiles:',len(ti))
ti.write('jplus_tiles_j0430.ecsv',overwrite=True)
s=Table.read('gf21_ctrl_pool.ecsv')
c=SkyCoord(s['RA_ICRS'],s['DE_ICRS'],unit='deg'); tc=SkyCoord(ti['ra'],ti['dec'],unit='deg')
idx,d2,_=c.match_to_catalog_sky(tc)
# tiles are ~1.4x1.4 deg; accept within square half-width 0.7
dra=np.abs(((np.array(s['RA_ICRS'])-np.array(ti['ra'])[idx]+180)%360-180)*np.cos(np.radians(s['DE_ICRS'])))
dde=np.abs(np.array(s['DE_ICRS'])-np.array(ti['dec'])[idx])
ok=(d2.deg<1.0)&(dra<0.72)&(dde<0.72)
print('pool in footprint (approx):',ok.sum())
s[ok].write('gf21_ctrl_infoot.ecsv',overwrite=True)
