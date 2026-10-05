import json, numpy as np
import astropy.units as u
from astropy.coordinates import SkyCoord, Galactocentric
G=4.30091e-6  # kpc (km/s)^2 / Msun
Mb,ab=0.5e10,0.5; Md,ad,bd=6.8e10,3.0,0.28; rs=16.0
def acc_parts(x,y,z,Mh):
    R2=x*x+y*y; r=np.sqrt(R2+z*z)
    # Hernquist bulge
    fb=-G*Mb/(r*(r+ab)**2)
    ax=fb*x; ay=fb*y; az=fb*z
    # MN disk
    B=np.sqrt(z*z+bd*bd); D=(R2+(ad+B)**2)**1.5
    ax+=-G*Md*x/D; ay+=-G*Md*y/D; az+=-G*Md*z*(ad+B)/(B*D)
    # NFW: M(r)=Mh*(ln(1+r/rs)-r/(r+rs))
    Mr=Mh*(np.log(1+r/rs)-r/(r+rs)); fh=-G*Mr/r**3
    ax+=fh*x; ay+=fh*y; az+=fh*z
    return ax,ay,az
def pot(R,z,Mh):
    r=np.sqrt(R*R+z*z)
    return -G*Mb/(r+ab) - G*Md/np.sqrt(R*R+(ad+np.sqrt(z*z+bd*bd))**2) - G*Mh*np.log(1+r/rs)/r
R0=8.122
# tune Mh so vc(R0)=229 km/s (Eilers+2019)
def vc(R,Mh):
    ax,_,_=acc_parts(np.array([R]),np.array([0.]),np.array([0.]),Mh); return np.sqrt(-ax[0]*R)
from scipy.optimize import brentq
Mh=brentq(lambda M: vc(R0,M)-229.0,1e10,1e13)
print('Mh(NFW scale mass)=%.3g, vc(R0)=%.1f'%(Mh,vc(R0,Mh)))
r=json.load(open('gaia_row.json'))
res={}
for label in ['RV0pm50','RVgrav']:
    U,V,W,rv,plx,pmra,pmdec=np.load(f'uvw_{label}.npy')[:, :3000]
    c=SkyCoord(ra=np.full(len(plx),r['ra'])*u.deg,dec=np.full(len(plx),r['dec'])*u.deg,distance=(1000/plx)*u.pc,
               pm_ra_cosdec=pmra*u.mas/u.yr,pm_dec=pmdec*u.mas/u.yr,radial_velocity=rv*u.km/u.s)
    gc=c.transform_to(Galactocentric(galcen_distance=R0*u.kpc,z_sun=20.8*u.pc,galcen_v_sun=[11.1,229.0+12.24,7.25]*u.km/u.s))
    x,y,z=[a.to(u.kpc).value for a in (gc.x,gc.y,gc.z)]
    vx,vy,vz=[a.to(u.km/u.s).value for a in (gc.v_x,gc.v_y,gc.v_z)]
    kms2kpcGyr=1.0227
    vx,vy,vz=vx*kms2kpcGyr,vy*kms2kpcGyr,vz*kms2kpcGyr
    dt=0.0005; nstep=int(3.0/dt)  # 3 Gyr
    zmax=np.zeros_like(x); Rmin=np.full_like(x,1e9); Rmax=np.zeros_like(x)
    k2=kms2kpcGyr**2
    ax,ay,az=acc_parts(x,y,z,Mh)
    for i in range(nstep):
        vx+=0.5*dt*ax*k2; vy+=0.5*dt*ay*k2; vz+=0.5*dt*az*k2
        x+=dt*vx; y+=dt*vy; z+=dt*vz
        ax,ay,az=acc_parts(x,y,z,Mh)
        vx+=0.5*dt*ax*k2; vy+=0.5*dt*ay*k2; vz+=0.5*dt*az*k2
        R=np.hypot(x,y); zmax=np.maximum(zmax,abs(z)); Rmin=np.minimum(Rmin,R); Rmax=np.maximum(Rmax,R)
    ecc=(Rmax-Rmin)/(Rmax+Rmin)
    # vertical action (adiabatic, at present R, from W LSR-frame vz)
    R_now=np.hypot(*[a.to(u.kpc).value for a in (gc.x,gc.y)])
    z_now=gc.z.to(u.kpc).value; vz_now=gc.v_z.to(u.km/u.s).value
    Jz=np.zeros(len(R_now))
    for j in range(len(R_now)):
        Ez=0.5*vz_now[j]**2+pot(R_now[j],z_now[j],Mh)-pot(R_now[j],0,Mh)
        zz=np.linspace(0,3,30001); dP=pot(R_now[j],zz,Mh)-pot(R_now[j],0,Mh)
        ok=dP<Ez
        Jz[j]=(2/np.pi)*np.trapezoid(np.sqrt(np.clip(2*(Ez-dP[ok]),0,None)),zz[ok])  # kpc km/s
    q=lambda a:'%.3f [%.3f,%.3f]'%tuple(np.percentile(a,[50,16,84]))
    print('\n==',label,'N=',len(x))
    print('zmax kpc',q(zmax)); print('Rmin',q(Rmin)); print('Rmax',q(Rmax)); print('ecc',q(ecc)); print('Jz kpc km/s',q(Jz))
    print('frac zmax>1 kpc %.3f; >0.5 kpc %.3f'%((zmax>1).mean(),(zmax>0.5).mean()))
    np.save(f'orbit_{label}.npy',np.vstack([zmax,Rmin,Rmax,ecc,Jz]))
