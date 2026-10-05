import numpy as np, glob, sxphot as S
from astropy.table import Table
from astropy.coordinates import SkyCoord
from scipy.optimize import minimize
t=Table.read('scene_sources.ecsv')
c0=SkyCoord(305.66064,39.19732,unit='deg'); r=SkyCoord(t['ra'],t['dec'],unit='deg').separation(c0).arcsec
sel=(r<1)|((t['K']<15.0)&(r<60))|((t['K']<16.0)&(r<15))
src=t[sel]; ib=list(src['name']).index('J202237.40+391159.3')
fs=sorted(glob.glob('cut/*.npz'))
dets=np.array([S.load(f)['hdr']['DETECTOR'] for f in fs])
orig_zone=S.zone_psf
def make_zone(tf):
    def z(c,xp,yp):
        tt=c['epsf']; i=np.argmin((tt['XCENTER']-xp)**2+(tt['YCENTER']-yp)**2)
        a=np.array(tt['EPSF'][i]).reshape(33,33)
        return S.EPSF(tf(a)), int(i), float(tt['NEFF_MEAN'][i])
    return z
tfs={'id':lambda a:a,'flipx':lambda a:a[:,::-1],'flipy':lambda a:a[::-1,:],'T':lambda a:a.T}
for d in range(1,7):
    idx=np.where(dets==d)[0][:6]
    out={}
    for k,tf in tfs.items():
        S.zone_psf=make_zone(tf); cs=[]
        for i in idx:
            fr=S.load(fs[i])
            f=lambda p: S.fit_frame(fr,src,itarget=ib,rfit=3.0,shift=tuple(p))['chi2r']
            m=minimize(f,[0,0],method='Nelder-Mead',options=dict(xatol=0.02,fatol=0.01,maxiter=60))
            cs.append((m.fun,m.x[0],m.x[1]))
        cs=np.array(cs); out[k]=cs
        print(d,k,'median chi2r %.2f'%np.median(cs[:,0]),'shifts',np.round(cs[:,1],2),np.round(cs[:,2],2),flush=True)
S.zone_psf=orig_zone
