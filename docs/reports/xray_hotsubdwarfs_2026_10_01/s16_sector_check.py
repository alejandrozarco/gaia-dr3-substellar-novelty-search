# Per-sector check of a TESS frequency: amplitude S/N at f in each sector, and each sector's own top peak (0.7-40 c/d). Also a phase-folded plot.
import sys, glob, numpy as np, warnings; warnings.filterwarnings('ignore')
from astropy.io import fits; from astropy.wcs import WCS; from astropy.coordinates import SkyCoord; from astropy.timeseries import LombScargle
from astropy.table import Table
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
from s09_tess import clean
gid=int(sys.argv[1]); f0=float(sys.argv[2])
M=Table.read('s07_props.ecsv'); r=M[M['GaiaEDR3']==gid][0]; c=SkyCoord(float(r['ra_1']),float(r['dec_1']),unit='deg')
T,Y=[],[]
for p in sorted(glob.glob(f'tess/cache_{gid}_s*.fits')):
    h=fits.open(p); d=h[1].data; x,y=WCS(h[2].header).world_to_pixel(c); xi,yi=int(round(float(x))),int(round(float(y)))
    q=(d['QUALITY']==0)&np.isfinite(d['TIME']); fl=d['FLUX'][q]; t=d['TIME'][q]
    yy,xx=np.mgrid[0:fl.shape[1],0:fl.shape[2]]; ap=(np.abs(xx-xi)<=1)&(np.abs(yy-yi)<=1); ring=(np.abs(xx-xi)>2)|(np.abs(yy-yi)>2)
    bk=np.nanmedian(fl[:,ring],axis=1); lc=np.nansum(fl[:,ap],axis=1)-bk*ap.sum(); med=np.nanmedian(lc)
    ok,yv=clean(t,lc/med-1); t,yv=t[ok&np.isfinite(yv)],yv[ok&np.isfinite(yv)]
    if len(t)<200: continue
    dt=np.median(np.diff(t)); F=np.arange(0.7,min(40,0.45/dt),0.002); ls=LombScargle(t,yv,normalization='psd'); A=np.sqrt(4*ls.power(F)/len(t))
    k0=np.argmin(np.abs(F-f0)); w=np.abs(F-f0)<1; kk=np.argmax(A)
    print(p.split('_')[-1], 'cad %.0fs'%(dt*86400), 'n',len(t),'amp@f0 %.3f%% S/N %.1f'%(100*A[max(k0-5,0):k0+5].max(), A[max(k0-5,0):k0+5].max()/np.median(A[w])), '| sector top f=%.4f (P=%.3f h) amp %.3f%% S/N %.1f'%(F[kk],24/F[kk],100*A[kk],A[kk]/np.median(A[np.abs(F-F[kk])<1])), 'rms %.2f%%'%(100*np.std(yv)))
    T.append(t);Y.append(yv)
t,y=np.concatenate(T),np.concatenate(Y); ph=(t*f0)%1; bn=np.linspace(0,1,21); mb=[np.median(y[(ph>=a)&(ph<b)]) for a,b in zip(bn[:-1],bn[1:])]
plt.figure(figsize=(6,3.5)); plt.plot(ph,y,',',color='0.75'); plt.plot((bn[:-1]+bn[1:])/2,mb,'ko'); plt.ylim(np.percentile(y,2),np.percentile(y,98)); plt.title(f'{gid} f={f0} c/d (P={24/f0:.3f} h)',fontsize=8); plt.savefig(f'tess/fold_{gid}.png',dpi=80)
