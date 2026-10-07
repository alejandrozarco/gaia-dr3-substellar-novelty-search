import warnings; warnings.filterwarnings('ignore')
from astroquery.vizier import Vizier
from astropy.coordinates import SkyCoord
import astropy.units as u
c=SkyCoord(181.49607080347943,-47.52715459823487,unit='deg')
V=Vizier(columns=['**'],row_limit=50)
r=V.query_region(c,radius=5*u.arcsec)
print(len(r),'tables')
for k in r.keys(): print(k, len(r[k]))
for cat in ['J/A+A/662/A40','J/A+A/621/A38']:
    rr=V.query_region(c,radius=5*u.arcsec,catalog=cat)
    for k in rr.keys():
        print('==',k); t=rr[k]
        for col in t.colnames: print('  ',col,t[col][0])
