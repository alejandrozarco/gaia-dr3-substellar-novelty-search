import json, numpy as np
import astropy.units as u
from astropy.coordinates import SkyCoord, Galactocentric, ICRS, Galactic, CartesianDifferential
r=json.load(open('gaia_row.json'))
rng=np.random.default_rng(42); N=20000
m=np.array([r['parallax'],r['pmra'],r['pmdec']])
s=np.array([r['parallax_error'],r['pmra_error'],r['pmdec_error']])
C=np.diag(s**2)
C[0,1]=C[1,0]=r['parallax_pmra_corr']*s[0]*s[1]
C[0,2]=C[2,0]=r['parallax_pmdec_corr']*s[0]*s[2]
C[1,2]=C[2,1]=r['pmra_pmdec_corr']*s[1]*s[2]
S=rng.multivariate_normal(m,C,N)
plx,pmra,pmdec=S.T
mu=np.hypot(pmra,pmdec); vt=4.74047*mu/plx
print('mu=%.2f mas/yr  vtan=%.2f +- %.2f km/s  d=%.2f pc'%(np.hypot(m[1],m[2]),np.median(vt),vt.std(),1000/m[0]))
def uvw(rv):
    c=SkyCoord(ra=np.full(len(plx),r['ra'])*u.deg,dec=np.full(len(plx),r['dec'])*u.deg,distance=(1000/plx)*u.pc,
               pm_ra_cosdec=pmra*u.mas/u.yr,pm_dec=pmdec*u.mas/u.yr,radial_velocity=rv*u.km/u.s,frame='icrs')
    g=c.galactic; v=g.velocity.d_xyz.to(u.km/u.s).value  # heliocentric U (to GC), V, W
    return v, c
out={}
# LSR correction Schoenrich+2010
sun=np.array([11.1,12.24,7.25])
for label,rvmu,rvsig in [('RV0pm50',0,50),('RVgrav',15,30)]:
    rv=rng.normal(rvmu,rvsig,N)
    v,c=uvw(rv)
    U,V,W=v+sun[:,None]   # LSR frame
    # Bensby+2014 probabilities (LSR)
    def f(U,V,W,su,sv,sw,va): return 1/((2*np.pi)**1.5*su*sv*sw)*np.exp(-U**2/(2*su**2)-(V-va)**2/(2*sv**2)-W**2/(2*sw**2))
    D=0.85*f(U,V,W,35,20,16,0); TD=0.09*f(U,V,W,67,38,35,-46); H=0.0015*f(U,V,W,160,90,90,-220)
    tot=D+TD+H
    pD,pTD,pH=D/tot,TD/tot,H/tot
    TDD=TD/D
    vtot=np.sqrt(U**2+V**2+W**2)
    q=lambda x:'%.1f [%.1f,%.1f]'%tuple(np.percentile(x,[50,16,84]))
    print('\n==',label)
    for n,x in [('U_LSR',U),('V_LSR',V),('W_LSR',W),('|W|',abs(W)),('v_tot_LSR',vtot),('P_thin',pD),('P_thick',pTD),('P_halo',pH)]:
        print(n,q(x))
    print('TD/D median %.3f; frac(TD/D>1)=%.3f frac(TD/D>2)=%.3f; frac(TD/D<0.1)=%.3f'%(np.median(TDD),(TDD>1).mean(),(TDD>2).mean(),(TDD<0.1).mean()))
    print('mean probs D/TD/H: %.3f %.3f %.3f'%(pD.mean(),pTD.mean(),pH.mean()))
    np.save(f'uvw_{label}.npy',np.vstack([U,V,W,rv,plx,pmra,pmdec]))
# nominal UVW with RV=0 (heliocentric)
v,c=uvw(np.zeros(N)); print('\nhelio UVW RV=0 median',np.median(v,axis=1))
# RV partial derivatives: direction of line of sight in UVW
g=SkyCoord(ra=r['ra']*u.deg,dec=r['dec']*u.deg).galactic
l,b=np.radians(g.l.deg),np.radians(g.b.deg)
print('LOS unit (U,V,W):',np.cos(b)*np.cos(l),np.cos(b)*np.sin(l),np.sin(b))
