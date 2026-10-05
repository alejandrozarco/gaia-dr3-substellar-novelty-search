# Chance-alignment control with CDS xMatch: Culpan hotsd positions real vs shifted (Dec +-1', +2', RA +1'/cosd) against eRASS:3 main (vizier:J/A+A/712/A171/erass3-m), r<15".
from astroquery.xmatch import XMatch
from astroquery.vizier import Vizier
from astropy.table import Table
import astropy.units as u, numpy as np, time
v=Vizier(columns=['GaiaEDR3','RA_ICRS','DE_ICRS','GLON'],row_limit=-1); v.TIMEOUT=600
h=v.get_catalogs('J/A+A/662/A40/hotsd')[0]; print('culpan rows',len(h))
h.write('culpan_hotsd_min.ecsv',overwrite=True)
out={}
for lab,dra,dde in [('real',0,0),('dec+1m',0,1/60),('dec-1m',0,-1/60),('dec+2m',0,2/60),('ra+1m',1/60,0)]:
    t=Table({'id':h['GaiaEDR3'],'ra':(h['RA_ICRS']+dra/np.cos(np.radians(h['DE_ICRS'])))%360,'dec':h['DE_ICRS']+dde})
    t0=time.time()
    r=XMatch.query(cat1=t,cat2='vizier:J/A+A/712/A171/erass3-m',max_distance=15*u.arcsec,colRA1='ra',colDec1='dec')
    r.write(f's02_ctrl_{lab}.ecsv',overwrite=True)
    s=np.array(r['angDist']); n1=len(np.unique(r['id']))
    print(lab,'rows',len(r),'uniq',n1,'<3":',(s<3).sum(),'<5":',(s<5).sum(),'<10":',(s<10).sum(),'<15":',(s<15).sum(),f'{time.time()-t0:.0f}s',flush=True)
