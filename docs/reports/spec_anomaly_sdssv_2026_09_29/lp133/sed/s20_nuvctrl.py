import warnings; warnings.filterwarnings('ignore')
import numpy as np
from astropy.table import Table
from astroquery.xmatch import XMatch
import astropy.units as u
from astroquery.vizier import Vizier
# wider pool: GF21 with TeffH 6200-7300, G<19.5, Pwd>0.75, all sky
v=Vizier(columns=['GaiaEDR3','RA_ICRS','DE_ICRS','pmRA','pmDE','Gmag','BPmag','RPmag','TeffH','loggH','MassH','Pwd'],row_limit=-1,timeout=600)
p=v.query_constraints(catalog='J/MNRAS/508/3877/maincat',Gmag='<19.3',Pwd='>0.75',TeffH='6200..7300')[0]
print('pool',len(p))
dt=2007.0-2016.0
ra=np.array(p['RA_ICRS'],float)+np.array(p['pmRA'].filled(0),float)*dt/3.6e6/np.cos(np.radians(np.array(p['DE_ICRS'],float)))
de=np.array(p['DE_ICRS'],float)+np.array(p['pmDE'].filled(0),float)*dt/3.6e6
up=Table({'gid':np.array(p['GaiaEDR3']).astype(np.int64),'ra':ra,'dec':de,'G':np.array(p['Gmag'],float),'BR':np.array(p['BPmag']-p['RPmag'],float),'TeffH':np.array(p['TeffH'],float),'loggH':np.array(p['loggH'],float)})
up.write('nuvctrl_upload.csv',overwrite=True,format='csv')
x=XMatch.query(cat1=open('nuvctrl_upload.csv'),cat2='vizier:II/335/galex_ais',max_distance=4*u.arcsec,colRA1='ra',colDec1='dec')
print('xmatch rows',len(x)); print(x.colnames)
x.write('nuvctrl_guvcat.ecsv',overwrite=True)
