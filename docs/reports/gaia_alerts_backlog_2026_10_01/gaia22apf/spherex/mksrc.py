import numpy as np
from astropy.table import Table, vstack
from astropy.coordinates import SkyCoord
import astropy.units as u
u_=Table.read('field_ugps.ecsv'); tm=Table.read('field_tmass.ecsv')
c0=SkyCoord(305.66064,39.19732,unit='deg')
g=Table.read('field_gaia.ecsv'); g.sort('_r')
rows=[('target',float(g['RA_ICRS'][0]),float(g['DE_ICRS'][0]),15.19)]
cu=SkyCoord(u_['RAICRS'],u_['DEICRS'],unit='deg')
K=np.array(u_['Kmag1'].filled(np.nan) if hasattr(u_['Kmag1'],'filled') else u_['Kmag1'],float)
r=cu.separation(c0).arcsec
for i in np.argsort(r):
    if r[i]<1.0: continue
    if r[i]>75: continue
    if (K[i]<16.5) or (r[i]<9 and K[i]<18.5) or not np.isfinite(K[i]):
        rows.append((str(u_['UGPS'][i]),float(u_['RAICRS'][i]),float(u_['DEICRS'][i]),K[i]))
# 2MASS sources with no UGPS within 1.5" (saturated in UGPS)
ct=SkyCoord(tm['RAJ2000'],tm['DEJ2000'],unit='deg')
for i in range(len(tm)):
    if ct[i].separation(c0).arcsec>75: continue
    if np.min(ct[i].separation(cu).arcsec)>1.5 and tm['Kmag'][i]<16.5:
        rows.append(('2M'+str(tm['2MASS'][i]),float(tm['RAJ2000'][i]),float(tm['DEJ2000'][i]),float(tm['Kmag'][i])))
t=Table(rows=rows,names=['name','ra','dec','K'])
t.write('scene_sources.ecsv',overwrite=True)
print(len(t)); print(t[:12])
# refine positions with Gaia DR3 propagated to 2025.8
g=Table.read('field_gaia.ecsv')
pmra=np.nan_to_num(np.array(g['pmRA'].filled(0) if hasattr(g['pmRA'],'filled') else g['pmRA'],float))
pmde=np.nan_to_num(np.array(g['pmDE'].filled(0) if hasattr(g['pmDE'],'filled') else g['pmDE'],float))
dt=2025.8-2016.0
gra=np.array(g['RA_ICRS'])+pmra*dt/3.6e6/np.cos(np.radians(np.array(g['DE_ICRS']))); gde=np.array(g['DE_ICRS'])+pmde*dt/3.6e6
cg=SkyCoord(gra,gde,unit='deg'); cs=SkyCoord(t['ra'],t['dec'],unit='deg')
idx,sep,_=cs.match_to_catalog_sky(cg)
m=sep.arcsec<1.0
t['gaia']=np.where(m,np.array(g['Source'])[idx],0)
t['ra']=np.where(m,gra[idx],t['ra']); t['dec']=np.where(m,gde[idx],t['dec'])
t['Gmag']=np.where(m,np.array(g['Gmag'])[idx],np.nan)
t.write('scene_sources.ecsv',overwrite=True); print('gaia-matched',m.sum(),'of',len(t)); print(t[:8])
