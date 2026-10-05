import warnings; warnings.filterwarnings('ignore')
from astroquery.vizier import Vizier
from astropy.coordinates import SkyCoord
import astropy.units as u, numpy as np
c=SkyCoord(305.66064,39.19732,unit='deg')
V=Vizier(columns=['**','+_r'],row_limit=-1)
for cat,name in [('I/355/gaiadr3','gaia'),('II/316/gps6','ugps'),('II/246/out','tmass'),('II/328/allwise','allwise'),('II/368/sstsl2','sstsl2'),('II/365/catwise','catwise')]:
    try:
        r=V.query_region(c,radius=150*u.arcsec,catalog=cat)
        t=r[0]; t.write(f'field_{name}.ecsv',overwrite=True); print(name,len(t))
    except Exception as e: print(name,'ERR',e)
