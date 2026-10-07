import warnings; warnings.filterwarnings('ignore')
from astroquery.simbad import Simbad
from astropy.coordinates import SkyCoord
import astropy.units as u
# control
s=Simbad(); s.add_votable_fields('otype','sp','ids')
print('CONTROL',s.query_object('AM Her')[['main_id','otype']] if s.query_object('AM Her') is not None else 'FAIL')
c=SkyCoord(181.49607080347943,-47.52715459823487,unit='deg')
r=s.query_region(c,radius=30*u.arcsec); print(r)
for row in (r or []):
    print('IDS',row['ids'])
from astroquery.simbad import Simbad as S2
q=f"""SELECT b.main_id, h.bibcode FROM basic b JOIN has_ref h ON h.oidref=b.oid WHERE CONTAINS(POINT('ICRS',b.ra,b.dec),CIRCLE('ICRS',181.49607,-47.52715,0.003))=1"""
print(S2.query_tap(q))
