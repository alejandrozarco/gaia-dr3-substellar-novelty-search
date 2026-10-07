import warnings; warnings.filterwarnings('ignore')
from astropy.io import fits; from astropy.wcs import WCS; import numpy as np
from astropy.timeseries import LombScargle
from scipy.ndimage import median_filter
RA,DE=181.49607080347943,-47.52715459823487
def load(s):
    h=fits.open(f'cut_s{s}.fits'); d=h[1].data; w=WCS(h[2].header)
    x,y=w.all_world2pix(RA,DE,0)
    q=(d['QUALITY']==0)&np.isfinite(d['TIME'])&np.all(np.isfinite(d['FLUX'].reshape(len(d),-1)),axis=1)
    return d['TIME'][q],d['FLUX'][q],d['TIMECORR'][q],float(x),float(y),w
def detrend(t,f,dt):
    br=np.r_[0,np.where(np.diff(t)>0.5)[0]+1,len(t)]; fd=np.empty_like(f); w=max(5,int(0.5*86400/dt)|1)
    for a,b in zip(br[:-1],br[1:]): fd[a:b]=f[a:b]-median_filter(f[a:b],size=min(w,b-a),mode='nearest')
    return fd
def lc(s,rad=1.5):
    t,fl,tc,x,y,w=load(s); ny,nx=fl.shape[1:]
    yy,xx=np.mgrid[:ny,:nx]; r=np.hypot(xx-x,yy-y); ap=r<=rad; ann=(r>=4)&(r<=7)
    bk=np.nanmedian(fl[:,ann],axis=1); f=np.nansum(fl[:,ap],axis=1)-ap.sum()*bk
    dt=np.median(np.diff(t))*86400; fd=detrend(t,f,dt); mean=np.nanmedian(f)
    k=np.isfinite(fd)&(np.abs(fd)<5*1.4826*np.nanmedian(np.abs(fd)))
    return t[k],fd[k]/mean,tc[k],mean,dt
if __name__=='__main__':
    out={}
    for s in [10,64,99,100,101]:
        for rad in [1.0,1.5,2.0]:
            t,f,tc,mean,dt=lc(s,rad); nyq=43200/dt
            fr=np.arange(5,min(nyq,216)-0.01,0.002) ; ls=LombScargle(t,f); p=ls.power(fr,method='fast')
            j=np.argmax(p); A=lambda z: 100*np.hypot(*ls.model_parameters(z)[1:3])
            snr=lambda z: A(z)/(100*np.sqrt(np.pi/len(t))*np.std(f))  # amp / mean-noise-amp
            print(f'S{s} r={rad} n={len(t)} rms={100*np.std(f):.2f}% top {fr[j]:.3f} c/d A={A(fr[j]):.3f}% SNR={snr(fr[j]):.1f}', ' | '.join(f'{z}:A={A(z):.3f}%' for z in [203.4,206.76]),flush=True)
            if rad==1.5: np.save(f'lc_s{s}.npy',np.array([t,f,tc]))
