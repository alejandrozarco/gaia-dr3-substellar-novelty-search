import sys, numpy as np, warnings; warnings.filterwarnings('ignore')
from astropy.table import Table
from astroquery.vizier import Vizier
from astropy.coordinates import SkyCoord
import astropy.units as u
ecsv,ra,dec=sys.argv[1],float(sys.argv[2]),float(sys.argv[3])
T=Table.read(ecsv); G=(T['qc']==1)&(T['clip']==0)
c=SkyCoord(ra,dec,unit='deg'); V=Vizier(columns=['**'],row_limit=5)
tm=V.query_region(c,radius=2*u.arcsec,catalog='II/246/out')[0][0]
try: aw=V.query_region(c,radius=3*u.arcsec,catalog='II/328/allwise')[0][0]
except Exception: aw=None
bands=[('J',1.11,1.39,1594.,tm['Jmag']),('H',1.50,1.80,1024.,tm['Hmag']),('Ks',2.00,2.31,666.7,tm['Kmag'])]
if aw is not None: bands+=[('W1',2.8,3.9,309.54,aw['W1mag']),('W2',4.0,5.0,171.79,aw['W2mag'])]
for b,lo,hi,zp,mag in bands:
    m=G&(T['wave']>=lo)&(T['wave']<hi)
    ref=zp*1e6*10**(-0.4*float(mag))
    if m.sum()<2: print(f"  {b:3s} mag={float(mag):6.3f} ref={ref:8.0f}  SPHEREx: n={m.sum()}"); continue
    f=np.array(T['flux'][m]); med=np.median(f); er=1.2533*1.4826*np.median(np.abs(f-med))/np.sqrt(m.sum())
    print(f"  {b:3s} mag={float(mag):6.3f} ref={ref:8.0f} uJy  SPHEREx={med:8.0f}+-{er:5.0f} (n={m.sum():3d}) ratio={med/ref:.3f}")
