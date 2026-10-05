import warnings; warnings.filterwarnings('ignore')
import numpy as np
from astropy.table import Table, vstack
from astroquery.vizier import Vizier
from astropy.coordinates import SkyCoord
import astropy.units as u
up=Table.read('nuvctrl_upload.csv')
v=Vizier(columns=['_q','RAJ2000','DEJ2000','NUVmag','e_NUVmag','FUVmag','e_FUVmag','Nexpt','Fexpt','+_r'],row_limit=-1,timeout=300)
out=[]
for k in range(0,len(up),400):
    ch=up[k:k+400]
    for att in range(3):
        try:
            r=v.query_region(SkyCoord(ch['ra'],ch['dec'],unit='deg'),radius=4*u.arcsec,catalog='II/335/galex_ais'); break
        except Exception as e: print('retry',k,str(e)[:80]); r=None
    if r is None or len(r)==0: continue
    t=r[0]; t['gid']=ch['gid'][t['_q']-1]; t['G']=ch['G'][t['_q']-1]; t['BR']=ch['BR'][t['_q']-1]; t['TeffH']=ch['TeffH'][t['_q']-1]; t['loggH']=ch['loggH'][t['_q']-1]
    out.append(t); print(k,len(t))
T=vstack(out); print('total',len(T),T.colnames); T.write('nuvctrl_guvcat.ecsv',overwrite=True)
