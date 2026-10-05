import time, numpy as np, warnings; warnings.filterwarnings('ignore')
from astropy.io import fits
from astropy.wcs import WCS
from astropy.coordinates import SkyCoord
t0=time.time()
url='s3://nasa-irsa-spherex/qr2/level2/2025W18_1B/l2b-v20-2025-241/1/level2_2025W18_1B_0011_1D1_spx_l2b-v20-2025-241.fits'
with fits.open(url,use_fsspec=True,fsspec_kwargs={'anon':True,'default_block_size':2**16}) as h:
    hdr=h['IMAGE'].header
    w=WCS(hdr)
    x,y=w.world_to_pixel(SkyCoord(305.66064,39.19732,unit='deg'))
    print(x,y)
    xi,yi=int(round(float(x))),int(round(float(y)))
    sl=(slice(yi-20,yi+21),slice(xi-20,xi+21))
    im=h['IMAGE'].section[sl]; fl=h['FLAGS'].section[sl]; va=h['VARIANCE'].section[sl]; zo=h['ZODI'].section[sl]
    print(im.shape, np.nanmedian(im), np.nanmedian(zo), time.time()-t0)
    print(repr(h['FLAGS'].header['MP*']))
    print({k:hdr.get(k) for k in ['DETECTOR','PSF_FWHM','BUNIT','MJD-OBS','MJD-AVG','DATE-OBS','EXPTIME','VERSION']})
print(time.time()-t0)
