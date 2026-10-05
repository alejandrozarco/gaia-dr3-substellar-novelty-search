import json, numpy as np
from astropy.coordinates import SkyCoord
import astropy.units as u
r=json.load(open('gaia_row.json'))
sun=np.array([11.1,12.24,7.25])
# AVR Aumer & Binney 2009
P={'U':(41.899,0.001,0.307),'V':(28.823,0.715,0.430),'W':(23.381,0.001,0.445)}
def sig(t,k):
    v10,t1,b=P[k]; return v10*((t+t1)/(10+t1))**b
g=SkyCoord(ra=r['ra']*u.deg,dec=r['dec']*u.deg).galactic
l,b=np.radians(g.l.deg),np.radians(g.b.deg)
er=np.array([np.cos(b)*np.cos(l),np.cos(b)*np.sin(l),np.sin(b)])
el=np.array([-np.sin(l),np.cos(l),0])
eb=np.array([-np.sin(b)*np.cos(l),-np.sin(b)*np.sin(l),np.cos(b)])
# observed heliocentric tangential velocity components in (l,b)
c=SkyCoord(ra=r['ra']*u.deg,dec=r['dec']*u.deg,distance=1000/r['parallax']*u.pc,pm_ra_cosdec=r['pmra']*u.mas/u.yr,pm_dec=r['pmdec']*u.mas/u.yr,radial_velocity=0*u.km/u.s).galactic
k=4.74047/r['parallax']
vl=k*c.pm_l_cosb.value; vb=k*c.pm_b.value
print('v_l, v_b helio = %.2f %.2f km/s'%(vl,vb))
ages=np.linspace(0.05,13.5,1000)
def loglik(t,use_rv=None):
    s=np.array([sig(t,'U'),sig(t,'V'),sig(t,'W')])
    mean=np.array([0,-s[0]**2/80.,0])-sun
    S=np.diag(s**2)
    if use_rv is None:
        Pm=np.vstack([el,eb]); obs=np.array([vl,vb]); E=np.diag([0.1**2,0.1**2])
    else:
        rv,erv=use_rv
        Pm=np.vstack([el,eb,er]); obs=np.array([vl,vb,rv]); E=np.diag([0.1**2,0.1**2,erv**2])
    m=Pm@mean; C=Pm@S@Pm.T+E; d=obs-m
    return -0.5*d@np.linalg.solve(C,d)-0.5*np.log(np.linalg.det(C))
for lab,rv in [('tangential only',None),('+RV 15+-30 (grav-redshift-corrected, coarse)',(15,30))]:
    L=np.array([loglik(t,rv) for t in ages]); p=np.exp(L-L.max()); p/=p.sum()
    cdf=np.cumsum(p)
    q=[ages[np.searchsorted(cdf,x)] for x in (0.16,0.5,0.84)]
    print('%s: kinematic age posterior (flat 0-13.5 Gyr) median %.1f [%.1f, %.1f] Gyr; mode %.1f; P(t<4.3)=%.2f'%(lab,q[1],q[0],q[2],ages[p.argmax()],p[ages<4.3].sum()))
# p-value: fraction of stars of age T with v_tan >= observed at this position
rng=np.random.default_rng(0)
vt_obs=np.hypot(vl,vb)
for T in [1,2,4.2,6,8,10]:
    s=np.array([sig(T,'U'),sig(T,'V'),sig(T,'W')])
    v=rng.normal(np.array([0,-s[0]**2/80,0])-sun,s,(200000,3))
    vt=np.hypot(v@el,v@eb)
    print('age %.1f Gyr: sigma_tot %.1f; P(v_tan>=%.1f)=%.3f; median v_tan %.1f'%(T,np.linalg.norm(s),vt_obs,(vt>=vt_obs).mean(),np.median(vt)))
