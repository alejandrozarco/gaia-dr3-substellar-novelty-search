# Flickering index per TESS sector: rms of the detrended LC binned to 30 min vs rms expected from point-to-point white noise (p2p/sqrt(Nbin)).
# ratio >> 1 means correlated variability on 0.5-12 h scales (flickering or periodic). Same for the background aperture as a systematics check.
import glob, numpy as np, warnings, sys; warnings.filterwarnings('ignore')
from astropy.io import fits; from astropy.wcs import WCS; from astropy.coordinates import SkyCoord
from astropy.table import Table
from s09_tess import clean
M=Table.read('s07_props.ecsv')
ids=[int(x) for x in sys.argv[1:]]
for gid in ids:
    r=M[M['GaiaEDR3']==gid][0]; c=SkyCoord(float(r['ra_1']),float(r['dec_1']),unit='deg'); out=[]
    for p in sorted(glob.glob(f'tess/cache_{gid}_s*.fits')):
        h=fits.open(p); d=h[1].data; x,y=WCS(h[2].header).world_to_pixel(c); xi,yi=int(round(float(x))),int(round(float(y)))
        q=(d['QUALITY']==0)&np.isfinite(d['TIME']); fl=d['FLUX'][q]; t=d['TIME'][q]
        yy,xx=np.mgrid[0:fl.shape[1],0:fl.shape[2]]; ap=(np.abs(xx-xi)<=1)&(np.abs(yy-yi)<=1); ring=(np.abs(xx-xi)>2)|(np.abs(yy-yi)>2)
        bk=np.nanmedian(fl[:,ring],axis=1); lc=np.nansum(fl[:,ap],axis=1)-bk*ap.sum(); med=np.nanmedian(lc)
        if not med>0: continue
        ok,yv=clean(t,lc/med-1); okb,bv=clean(t,bk*ap.sum()/med); m=ok&okb&np.isfinite(yv)&np.isfinite(bv); t,yv,bv=t[m],yv[m],bv[m]
        if len(t)<500: continue
        dt=np.median(np.diff(t)); nb=max(1,int(round(1/48/dt)))
        def idx(v):
            p2p=np.median(np.abs(np.diff(v)))*1.4826/np.sqrt(2); n=len(v)//nb*nb; b=v[:n].reshape(-1,nb).mean(1); return np.std(b)/(p2p/np.sqrt(nb)), p2p
        fi,p2p=idx(yv); fb,_=idx(bv)
        out.append(f"s{p.split('_s')[-1][:-5]}:{fi:.1f}/{fb:.1f}(p2p {100*p2p:.1f}%)")
    print(gid, str(r['simbad'])[:22], 'G=%.1f'%r['phot_g_mean_mag'], ' '.join(out))
