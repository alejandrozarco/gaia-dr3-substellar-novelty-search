import warnings; warnings.filterwarnings('ignore')
import numpy as np, json
from astroquery.vizier import Vizier
from astropy.coordinates import SkyCoord
import astropy.units as u
g=json.load(open('gaia.json'))
RA0,DE0,PMRA,PMDE=g['RA_ICRS'],g['DE_ICRS'],g['pmRA'],g['pmDE']
def pos(ep):
    dt=ep-2016.0
    return RA0+PMRA*dt/3.6e6/np.cos(np.radians(DE0)), DE0+PMDE*dt/3.6e6
cats={'GALEX_GUVcat':'II/335','GALEX_AIS_DR5':'II/312','SDSS_DR16':'V/154','PS1':'II/349','2MASS':'II/246','UKIDSS_LAS':'II/319','CatWISE2020':'II/365','unWISE':'II/363','AllWISE':'II/328'}
v=Vizier(columns=['**','+_r'],row_limit=-1)
c=SkyCoord(*pos(2008.0),unit='deg')
out={}
for k,cid in cats.items():
    try:
        r=v.query_region(c,radius=20*u.arcsec,catalog=cid)
    except Exception as e:
        print(k,'ERR',e); continue
    print('==',k,cid,'tables:',r.keys())
    for tn in r.keys():
        t=r[tn]
        print('  ',tn,len(t),'rows; cols:',t.colnames[:60])
        t.write(f'viz_{k}_{tn.replace("/","_")}.ecsv',overwrite=True)
