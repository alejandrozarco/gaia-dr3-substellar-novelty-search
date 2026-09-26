# Fetch one DESI DR1 coadd spectrum (B,R,Z) by targetid from the healpix coadd file using HTTP range reads (fsspec), save as npz.
import sys, numpy as np
from astropy.io import fits
def get(targetid, survey, program, healpix, out):
    url = f'https://data.desi.lbl.gov/public/dr1/spectro/redux/iron/healpix/{survey}/{program}/{healpix // 100}/{healpix}/coadd-{survey}-{program}-{healpix}.fits'
    with fits.open(url, use_fsspec=True, fsspec_kwargs={'block_size': 1 << 20}) as h:
        tid = h['FIBERMAP'].data['TARGETID']
        rows = np.where(tid == int(targetid))[0]
        if len(rows) == 0: raise RuntimeError('targetid not in coadd')
        i = int(rows[0]); d = {}
        for arm in ('B', 'R', 'Z'):
            d[arm + '_WAVE'] = np.array(h[arm + '_WAVELENGTH'].data, float)
            d[arm + '_FLUX'] = np.array(h[arm + '_FLUX'].section[i, :], float)
            d[arm + '_IVAR'] = np.array(h[arm + '_IVAR'].section[i, :], float)
        np.savez(out, **d)
    return out
if __name__ == '__main__':
    print(get(sys.argv[1], sys.argv[2], sys.argv[3], int(sys.argv[4]), sys.argv[5]))
