# Gaussian-PRF crowding estimate from TIC neighbours (sigma 0.8 px, 21 arcsec/px), averaged over sub-pixel positions/orientations.
# Validated against SPOC CROWDSAP for TIC 450781262 (S90 0.008, S99 0.021) and TIC 13565279 (S99 0.011).
import numpy as np, json
from astroquery.mast import Catalogs
import astropy.units as u
from astropy.coordinates import SkyCoord
from scipy.special import erf
T=json.load(open('rn/add_coords.json'))
tics={'WDJ1118':450781262,'Gaia19apf':333015737,'Gaia24deb':13565279}
rng=np.random.default_rng(1)
def pixfrac(dx,dy,ix,iy,s=0.8):
    fx=0.5*(erf((ix+0.5-dx)/(s*np.sqrt(2)))-erf((ix-0.5-dx)/(s*np.sqrt(2))))
    fy=0.5*(erf((iy+0.5-dy)/(s*np.sqrt(2)))-erf((iy-0.5-dy)/(s*np.sqrt(2))))
    return fx*fy
for k,tic in tics.items():
    c=SkyCoord(*T[k],unit='deg')
    t=Catalogs.query_region(c,radius=180*u.arcsec,catalog='TIC')
    t=t[np.isfinite(t['Tmag'])]
    me=t[t['ID']==str(tic)][0]
    sc=SkyCoord(t['ra'],t['dec'],unit='deg'); sep=c.separation(sc).arcsec; pa=c.position_angle(sc).rad
    flux=15000*10**(-0.4*(np.array(t['Tmag'])-10)); isme=np.array(t['ID'])==str(tic)
    res={}
    for nap in [1,2,4,6]:
        cr=[];ff=[]
        for trial in range(200):
            rot=rng.uniform(0,2*np.pi); ox,oy=rng.uniform(-0.5,0.5,2)
            x=ox+sep/21*np.sin(pa+rot); y=oy+sep/21*np.cos(pa+rot)
            grid=[(i,j) for i in range(-3,4) for j in range(-3,4)]
            tf=np.array([pixfrac(ox,oy,i,j) for i,j in grid])
            order=np.argsort(-tf)[:nap]
            ft=sum(flux[isme][0]*tf[o] for o in order)
            fc=sum((flux[~isme]*pixfrac(x[~isme],y[~isme],*grid[o])).sum() for o in order)
            cr.append(ft/(ft+fc)); ff.append(ft/flux[isme][0])
        res[nap]=(np.median(cr),np.median(ff))
    near=sorted(zip(sep[~isme],np.array(t['Tmag'])[~isme]))[:4]
    print(k,tic,'T %.2f'%me['Tmag'],' '.join('ap%d: crowd %.3f flfr %.2f'%(n,a,b) for n,(a,b) in res.items()),'| nearest',[(round(s,1),round(m,2)) for s,m in near])
