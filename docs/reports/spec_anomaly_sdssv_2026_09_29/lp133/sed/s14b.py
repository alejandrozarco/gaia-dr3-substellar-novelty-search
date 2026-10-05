import warnings; warnings.filterwarnings('ignore')
import numpy as np
from astropy.table import Table
from astroquery.vizier import Vizier
from astropy.coordinates import SkyCoord
import astropy.units as u
m=Table.read('galex_mast_5arcmin.ecsv'); m=m[m['survey']=='GII']
gv=Vizier(columns=['Source','RA_ICRS','DE_ICRS','pmRA','pmDE','Gmag'],row_limit=-1).query_region(SkyCoord(211.7934,55.1577,unit='deg'),radius=6*u.arcmin,catalog='I/355/gaiadr3')[0]
dt=2008.27-2016.0
R=np.array(gv['RA_ICRS'],float); D=np.array(gv['DE_ICRS'],float)
pr=np.array(gv['pmRA'].filled(0),float); pd=np.array(gv['pmDE'].filled(0),float)
ra=R+pr*dt/3.6e6/np.cos(np.radians(D)); de=D+pd*dt/3.6e6
mr=np.array(m['ra'],float); md=np.array(m['dec'],float)
gc=SkyCoord(ra,de,unit='deg'); mc=SkyCoord(mr,md,unit='deg')
idx,d2,_=mc.match_to_catalog_sky(gc)
for rad in [3,5]:
    ok=d2.arcsec<rad
    dra=(mr-ra[idx])[ok]*np.cos(np.radians(55.16))*3600; dde=(md-de[idx])[ok]*3600
    print(rad,'n=',ok.sum(),'median dRA %.2f dDec %.2f; MAD-rms %.2f %.2f'%(np.median(dra),np.median(dde),1.48*np.median(abs(dra-np.median(dra))),1.48*np.median(abs(dde-np.median(dde)))))
