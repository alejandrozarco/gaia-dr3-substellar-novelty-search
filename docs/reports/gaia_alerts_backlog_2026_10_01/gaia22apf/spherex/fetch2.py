import time, numpy as np, warnings, os, sys, concurrent.futures as cf
warnings.filterwarnings('ignore')
from astropy.io import fits
from astropy.wcs import WCS
from astropy.coordinates import SkyCoord
from astropy.table import Table
import pyvo
import logging; logging.getLogger('astropy').setLevel(logging.ERROR)
name,ra,dec=sys.argv[1],float(sys.argv[2]),float(sys.argv[3])
od=f'ctrl/{name}'; os.makedirs(od+'/cut',exist_ok=True)
s=pyvo.dal.TAPService("https://irsa.ipac.caltech.edu/TAP")
q=f"""SELECT a.uri, p.energy_bandpassname, p.time_bounds_lower FROM spherex.artifact a JOIN spherex.plane p ON a.planeid=p.planeid
WHERE 1=CONTAINS(POINT('ICRS',{ra},{dec}),p.poly) ORDER BY p.time_bounds_lower"""
t=s.search(q).to_table(); t=t[[('/qr2/' in u) for u in t['uri']]]
t.write(od+'/frames.ecsv',overwrite=True); print(name,len(t),flush=True)
c=SkyCoord(ra,dec,unit='deg'); H=20
def get(uri):
    out=od+'/cut/'+os.path.basename(uri).replace('.fits','.npz')
    if os.path.exists(out): return 'skip'
    url='s3://nasa-irsa-spherex/'+uri.split('ibe/data/spherex/')[1]
    for att in range(4):
        try:
            with fits.open(url,use_fsspec=True,fsspec_kwargs={'anon':True,'default_block_size':2**16}) as h:
                hdr=h['IMAGE'].header; ph=h[0].header
                x,y=WCS(hdr).world_to_pixel(c); xi,yi=int(round(float(x))),int(round(float(y)))
                y0=max(yi-H,0); y1=min(yi+H+1,2040); x0=max(xi-H,0); x1=min(xi+H+1,2040)
                sl=(slice(y0,y1),slice(x0,x1))
                d=dict(im=h['IMAGE'].section[sl],fl=h['FLAGS'].section[sl],va=h['VARIANCE'].section[sl],zo=h['ZODI'].section[sl],
                       x0=x0,y0=y0,hdr=hdr.tostring(),phdr=ph.tostring())
            np.savez_compressed(out,**d); return 'ok'
        except Exception as e:
            err=repr(e); time.sleep(5*(att+1))
    return 'FAIL '+err
with cf.ThreadPoolExecutor(8) as ex:
    res=list(ex.map(get,t['uri']))
import collections; print(name,collections.Counter([r[:4] for r in res]),flush=True)
