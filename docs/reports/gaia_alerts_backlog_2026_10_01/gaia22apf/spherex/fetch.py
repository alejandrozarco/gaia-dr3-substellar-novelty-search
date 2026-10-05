import time, numpy as np, warnings, os, sys, concurrent.futures as cf
warnings.filterwarnings('ignore')
from astropy.io import fits
from astropy.wcs import WCS
from astropy.coordinates import SkyCoord
from astropy.table import Table
import logging; logging.getLogger('astropy').setLevel(logging.ERROR)
t=Table.read('tap_frames.ecsv')
c=SkyCoord(305.66064,39.19732,unit='deg')
H=20
def get(uri):
    out='cut/'+os.path.basename(uri).replace('.fits','.npz')
    if os.path.exists(out): return 'skip'
    url='s3://nasa-irsa-spherex/'+uri.split('ibe/data/spherex/')[1]
    for att in range(4):
        try:
            with fits.open(url,use_fsspec=True,fsspec_kwargs={'anon':True,'default_block_size':2**16}) as h:
                hdr=h['IMAGE'].header; ph=h[0].header
                w=WCS(hdr)
                x,y=w.world_to_pixel(c); xi,yi=int(round(float(x))),int(round(float(y)))
                ny,nx=hdr['NAXIS2'],hdr['NAXIS1']
                y0=max(yi-H,0); y1=min(yi+H+1,ny); x0=max(xi-H,0); x1=min(xi+H+1,nx)
                sl=(slice(y0,y1),slice(x0,x1))
                d=dict(im=h['IMAGE'].section[sl],fl=h['FLAGS'].section[sl],va=h['VARIANCE'].section[sl],zo=h['ZODI'].section[sl],
                       x0=x0,y0=y0,hdr=hdr.tostring(),phdr=ph.tostring(),flhdr=h['FLAGS'].header.tostring())
            np.savez_compressed(out,**d); return 'ok'
        except Exception as e:
            err=repr(e); time.sleep(5*(att+1))
    return 'FAIL '+err
t0=time.time()
with cf.ThreadPoolExecutor(8) as ex:
    for uri,r in zip(t['uri'],ex.map(get,t['uri'])):
        print(r,uri,round(time.time()-t0),flush=True)
