import warnings; warnings.filterwarnings('ignore')
import numpy as np, json
from astropy.table import Table
from astroquery.vizier import Vizier
from astropy.coordinates import SkyCoord
import astropy.units as u
m=Table.read('galex_mast_5arcmin.ecsv'); m=m[m['survey']=='GII']
c0=SkyCoord(211.7934,55.1577,unit='deg')
gv=Vizier(columns=['Source','RA_ICRS','DE_ICRS','pmRA','pmDE','Gmag','BP-RP'],row_limit=-1).query_region(c0,radius=6*u.arcmin,catalog='I/355/gaiadr3')[0]
dt=2008.27-2016.0
ra=gv['RA_ICRS']+np.nan_to_num(gv['pmRA'])*dt/3.6e6/np.cos(np.radians(gv['DE_ICRS'])); de=gv['DE_ICRS']+np.nan_to_num(gv['pmDE'])*dt/3.6e6
gc=SkyCoord(ra,de,unit='deg'); mc=SkyCoord(m['ra'],m['dec'],unit='deg')
idx,d2,_=mc.match_to_catalog_sky(gc)
ok=d2.arcsec<5
dra=np.array(((m['ra']-ra[idx])*np.cos(np.radians(55.16))*3600)[ok]); dde=np.array(((m['dec']-de[idx])*3600)[ok])
nm=np.array(m['nuv_mag'])[ok]
print('matches <5":',ok.sum(),' median dRA %.2f dDec %.2f; rms %.2f %.2f'%(np.median(dra),np.median(dde),np.std(dra),np.std(dde)))
f=(nm>21)&(nm<22.5)
print('NUV 21-22.5: n=%d, sep median %.2f, 90pct %.2f'%(f.sum(),np.median(np.hypot(dra,dde)[f]),np.percentile(np.hypot(dra,dde)[f],90)))
# FUV depth
fu=np.array(m['fuv_mag'].filled(np.nan)); fe=np.array(m['fuv_magerr'].filled(np.nan))
good=np.isfinite(fu)&(fe>0)
print('FUV detections in 5 arcmin:',good.sum(), 'faintest', np.nanmax(fu[good]) if good.sum() else None)
if good.sum()>5:
    for lo,hi in [(0.15,0.25),(0.25,0.4)]:
        s=(fe>lo)&(fe<hi); print(' FUV mags with err %.2f-%.2f: median %.2f n=%d'%(lo,hi,np.nanmedian(fu[s]),s.sum()))
nu=np.array(m['nuv_mag'].filled(np.nan)); ne=np.array(m['nuv_magerr'].filled(np.nan))
s=(ne>0.15)&(ne<0.25); print(' NUV mags with err 0.15-0.25: median %.2f n=%d'%(np.nanmedian(nu[s]),s.sum()))
