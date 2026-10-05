import warnings; warnings.filterwarnings('ignore')
import numpy as np, json
from astropy.table import Table
from astroquery.mast import Observations
from astropy.time import Time
g=json.load(open('gaia.json'))
def pos(ep):
    dt=ep-2016.0
    return g['RA_ICRS']+g['pmRA']*dt/3.6e6/np.cos(np.radians(g['DE_ICRS'])), g['DE_ICRS']+g['pmDE']*dt/3.6e6
m=Table.read('galex_mast_5arcmin.ecsv'); m.sort('distance_arcmin')
for r in m[:4]:
    print({k:r[k] for k in ['distance_arcmin','objID','survey','ra','dec','nuv_mag','nuv_magerr','fuv_mag','nuv_flux','nuv_fluxerr','nuv_artifact','fuv_artifact','nuv_exptime','fuv_exptime','fov_radius','nuv_flux_aper_7']})
o=Observations.query_criteria(obs_id='3125113449827270656')
for r in o: print(r['obs_id'],r['filters'],r['t_min'],Time(r['t_min'],format='mjd').decimalyear,r['t_max'])
ep=Time(o['t_min'][0],format='mjd').decimalyear
wr,wd=pos(ep)
nb=(211.792,55.157)
ls=Table.read('ls_ls_dr9_tractor_n.ecsv')
for r in ls:
    print('LS src', r['ra'],r['dec'],r['type'],'sep from WD@%.2f: %.2f"'%(ep,3600*np.hypot((r['ra']-wr)*np.cos(np.radians(wd)),r['dec']-wd)), 'from GALEX src: %.2f"'%(3600*np.hypot((r['ra']-m[0]['ra'])*np.cos(np.radians(wd)),r['dec']-m[0]['dec'])), 'g_nmgy',round(float(r['flux_g']),3))
print('GALEX src offset from WD@%.2f: dRA*cos=%.2f" dDec=%.2f"'%(ep,(m[0]['ra']-wr)*np.cos(np.radians(wd))*3600,(m[0]['dec']-wd)*3600))
