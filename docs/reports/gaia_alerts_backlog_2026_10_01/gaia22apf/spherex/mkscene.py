import sys, numpy as np, warnings; warnings.filterwarnings('ignore')
from astroquery.vizier import Vizier
from astropy.coordinates import SkyCoord
from astropy.table import Table
import astropy.units as u
name,ra,dec=sys.argv[1],float(sys.argv[2]),float(sys.argv[3])
c0=SkyCoord(ra,dec,unit='deg')
V=Vizier(columns=['**','+_r'],row_limit=-1)
def q(cat):
    import time
    for a in range(5):
        try:
            r=V.query_region(c0,radius=80*u.arcsec,catalog=cat)
            return r[0] if len(r) else None
        except Exception as e: print(cat,'retry',e); time.sleep(10)
    return None
ug=q('II/316/gps6'); tm=q('II/246/out'); g=q('I/355/gaiadr3')
rows=[]
if ug is not None and len(ug)>0:
    K=np.array(ug['Kmag1'].filled(np.nan),float); cu=SkyCoord(ug['RAICRS'],ug['DEICRS'],unit='deg')
    for i in range(len(ug)): rows.append((str(ug['UGPS'][i]),float(ug['RAICRS'][i]),float(ug['DEICRS'][i]),K[i]))
else: cu=SkyCoord([],[],unit='deg')
if tm is not None:
    ct=SkyCoord(tm['RAJ2000'],tm['DEJ2000'],unit='deg')
    for i in range(len(tm)):
        if len(cu)==0 or np.min(ct[i].separation(cu).arcsec)>1.5:
            rows.append(('2M'+str(tm['2MASS'][i]),float(tm['RAJ2000'][i]),float(tm['DEJ2000'][i]),float(tm['Kmag'][i])))
t=Table(rows=rows,names=['name','ra','dec','K'])
cs=SkyCoord(t['ra'],t['dec'],unit='deg'); r=cs.separation(c0).arcsec
i0=int(np.argmin(r)); print('target match',t['name'][i0],r[i0],t['K'][i0])
order=[i0]+[i for i in np.argsort(r) if i!=i0 and r[i]>1.0]
t=t[order]; t['name'][0]='target'
# Gaia positions
pm=lambda col: np.nan_to_num(np.array(g[col].filled(0),float))
dt=2025.8-2016.0
gra=np.array(g['RA_ICRS'])+pm('pmRA')*dt/3.6e6/np.cos(np.radians(np.array(g['DE_ICRS']))); gde=np.array(g['DE_ICRS'])+pm('pmDE')*dt/3.6e6
idx,sep,_=SkyCoord(t['ra'],t['dec'],unit='deg').match_to_catalog_sky(SkyCoord(gra,gde,unit='deg'))
m=sep.arcsec<1.0
t['gaia']=np.where(m,np.array(g['Source'])[idx],0); t['ra']=np.where(m,gra[idx],t['ra']); t['dec']=np.where(m,gde[idx],t['dec'])
t['Gmag']=np.where(m,np.array(g['Gmag'].filled(np.nan))[idx],np.nan)
t.write(f'ctrl/{name}/scene.ecsv',overwrite=True); print(name,len(t),'gaia',m.sum()); print(t[:6])
