import numpy as np,warnings; warnings.filterwarnings('ignore')
from astropy.coordinates import SkyCoord
from astroquery.mast import Tesscut
c=SkyCoord(181.49607080347943,-47.52715459823487,unit='deg')
t=Tesscut.get_sectors(coordinates=c); print(t,flush=True)
for s in sorted(set(int(x) for x in t['sector'])):
    for i in range(3):
        try:
            h=Tesscut.get_cutouts(coordinates=c,size=15,sector=s)[0]; h.writeto(f'j1205/cut_s{s}.fits',overwrite=True); print(s,'ok',h[1].data.shape,flush=True); break
        except Exception as e: print(s,'err',e,flush=True)
