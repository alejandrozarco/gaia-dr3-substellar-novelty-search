import warnings,sys; warnings.filterwarnings('ignore')
from phot import *
from astropy.table import Table
G=Table.read('gaia120.csv'); G=G[G['Gmag']<17.6]
def pixlcs(s):
    t,fl,tc,x,y,w=load(s); dt=np.median(np.diff(t))*86400
    n,ny,nx=fl.shape; F=fl.reshape(n,-1).copy()
    br=np.r_[0,np.where(np.diff(t)>0.5)[0]+1,n]; W=max(5,int(0.5*86400/dt)|1)
    for a,b in zip(br[:-1],br[1:]): F[a:b]-=median_filter(F[a:b],size=(min(W,b-a),1),mode='nearest')
    # clip on total
    tot=F.sum(1); k=np.abs(tot)<5*1.4826*np.median(np.abs(tot))
    return t[k],F[k],np.nanmedian(fl,axis=0),x,y,w,ny,nx
def fit(t,Y,f):
    X=np.c_[np.sin(2*np.pi*f*t),np.cos(2*np.pi*f*t),np.ones_like(t)]
    c,res,_,_=np.linalg.lstsq(X,Y,rcond=None); r=Y-X@c; sig=np.sqrt((r**2).sum(0)/(len(t)-3))*np.sqrt(2/len(t))
    return c[0]+1j*c[1],sig
def main():
  pass
if __name__=="__main__":
 s=int(sys.argv[1]); f0=float(sys.argv[2])
 t,F,im,x,y,w,ny,nx=pixlcs(s)
 yy,xx=np.mgrid[:ny,:nx]; r=np.hypot(xx-x,yy-y).ravel()
 # refine freq on optimal-ish aperture: pixels within 1.5 pix
 sel=r<=1.5; ls=LombScargle(t,F[:,sel].sum(1)); fr=np.arange(f0-0.08,f0+0.08,0.0005); p=ls.power(fr); fb=fr[p.argmax()]
 z,sig=fit(t,F,fb); ph=np.angle(z[np.argmax(np.abs(z)*sel)])
 proj=(z*np.exp(-1j*ph)).real  # signed amplitude in phase with peak pixel
 A=proj.reshape(ny,nx); S=sig.reshape(ny,nx)
 np.set_printoptions(linewidth=250,precision=1,suppress=True)
 print(f'S{s} f={fb:.4f}  target pix x={x:.2f} y={y:.2f}')
 print('signed amp/sigma map (rows=y):'); print((A/S)[max(0,int(y)-4):int(y)+5, max(0,int(x)-4):int(x)+5])
 print('mean image:'); print(im[max(0,int(y)-4):int(y)+5, max(0,int(x)-4):int(x)+5])
 # PSF model: gaussian sigma from fitting the mean image? use sigma grid; fit amplitude map with single source at each Gaia star / free position
 gx,gy=w.all_world2pix(np.array(G['RA_ICRS']),np.array(G['DE_ICRS']),0)
 def chi2_at(px,py,sg):
     m=np.exp(-((xx-px)**2+(yy-py)**2)/(2*sg**2)).ravel(); wts=1/sig**2
     a=(m*proj*wts).sum()/(m*m*wts).sum(); return ((proj-a*m)**2*wts).sum(),a
 for sg in [0.75,1.0]:
     res=[]
     for i in range(len(G)):
         if not(0<=gx[i]<nx and 0<=gy[i]<ny): continue
         c2,a=chi2_at(gx[i],gy[i],sg); res.append((c2,G['Source'][i],G['sep'][i],G['Gmag'][i],gx[i],gy[i],a))
     res.sort()
     print(f' sigma={sg}: chi2 for single-source at Gaia positions (best 5):')
     for c2,sid,sep,gm,px,py,a in res[:5]: print(f'   chi2={c2:.1f} {sid} sep={sep:.1f}" G={gm:.2f} at ({px:.2f},{py:.2f}) amp={a:.2f}')
     # free fit
     best=min(((chi2_at(px,py,sg)[0],px,py) for px in np.arange(x-3,x+3,0.05) for py in np.arange(y-3,y+3,0.05)))
     print(f'   free-position best chi2={best[0]:.1f} at ({best[1]:.2f},{best[2]:.2f}) offset from target {21*np.hypot(best[1]-x,best[2]-y):.1f}" ; null chi2={((proj/sig)**2).sum():.1f} npix={len(proj)}')
