"""Re-analyse cached TESScut cutouts: per-sector detrend (quadratic per orbit), combined amplitude spectrum 0.7-40 c/d (below Nyquist of the coarsest cadence).
Report top peaks with amplitude S/N (amp / median amp in +-1 c/d), background amplitude at the same frequency, and Gaia neighbours within 42" (dilution).
Peak accepted if S/N>=5 and background S/N<3."""
import glob, json, os, sys, numpy as np, warnings; warnings.filterwarnings('ignore')
from astropy.io import fits; from astropy.wcs import WCS; from astropy.coordinates import SkyCoord; from astropy.timeseries import LombScargle
from astropy.table import Table
sys.path.insert(0,'.'); from s09_tess import clean
M=Table.read('s07_props.ecsv'); pos={int(r['GaiaEDR3']):(float(r['ra_1']),float(r['dec_1']),float(r['phot_g_mean_mag'])) for r in M}
def amp_spec(t,y,F):
    ls=LombScargle(t,y,normalization='psd'); p=ls.power(F); return np.sqrt(4*p/len(t))
out={}
for gid in sorted(set(int(os.path.basename(f).split('_')[1]) for f in glob.glob('tess/cache_*_s*.fits'))):
    ra,de,G=pos[gid]; c=SkyCoord(ra,de,unit='deg'); T,Y,B=[],[],[]; secs=[]
    for p in sorted(glob.glob(f'tess/cache_{gid}_s*.fits')):
        h=fits.open(p); d=h[1].data; x,y=WCS(h[2].header).world_to_pixel(c); xi,yi=int(round(float(x))),int(round(float(y)))
        q=(d['QUALITY']==0)&np.isfinite(d['TIME']); fl=d['FLUX'][q]; t=d['TIME'][q]
        yy,xx=np.mgrid[0:fl.shape[1],0:fl.shape[2]]; ap=(np.abs(xx-xi)<=1)&(np.abs(yy-yi)<=1); ring=(np.abs(xx-xi)>2)|(np.abs(yy-yi)>2)
        bk=np.nanmedian(fl[:,ring],axis=1); lc=np.nansum(fl[:,ap],axis=1)-bk*ap.sum(); med=np.nanmedian(lc)
        if not np.isfinite(med) or med<=0: continue
        ok1,yv=clean(t,lc/med-1); ok2,bv=clean(t,bk*ap.sum()/med); ok=ok1&ok2&np.isfinite(yv)&np.isfinite(bv)
        if ok.sum()<200: continue
        T.append(t[ok]);Y.append(yv[ok]);B.append(bv[ok]); secs.append(int(p.split('_s')[-1].split('.')[0]))
    if not T: out[gid]=dict(sectors=[]); continue
    t,y,b=map(np.concatenate,(T,Y,B)); dt=max(np.median(np.diff(tt)) for tt in T); fmax=min(40,0.45/dt)
    F=np.arange(0.7,fmax,0.1/(t.max()-t.min()) if t.max()-t.min()<60 else 0.002)
    A=amp_spec(t,y,F); AB=amp_spec(t,b,F)
    peaks=[]; Ac=A.copy()
    for _ in range(3):
        k=np.argmax(Ac); w=np.abs(F-F[k])<1.0; noise=np.median(A[w]); kb=np.abs(F-F[k])<0.01
        peaks.append(dict(f=round(F[k],5),P_h=round(24/F[k],4),amp_pct=round(100*A[k],3),snr=round(A[k]/noise,1),bkg_snr=round(AB[kb].max()/np.median(AB[w]),1)))
        Ac[np.abs(F-F[k])<0.05]=0
    out[gid]=dict(sectors=secs,n=len(t),G=G,rms_pct=round(100*np.std(y),2),peaks=peaks)
    print(gid,secs,'G=%.1f'%G,'rms=%.2f%%'%(100*np.std(y)),[(p['P_h'],p['amp_pct'],p['snr'],p['bkg_snr']) for p in peaks],flush=True)
json.dump(out,open('tess/s14_post.json','w'),indent=1)
