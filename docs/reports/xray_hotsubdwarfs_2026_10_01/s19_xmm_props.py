import numpy as np, requests, io, os, time, pandas as pd
from astropy.table import Table
from astroquery.vizier import Vizier
from astropy.coordinates import SkyCoord
import astropy.units as u
L=[5499736649371768192,3538467600619474560,6036173121152663296,5509063772151101568,1261473641918003456,6184268987981207552,4658465363442588928,2309702230603610112,4877263019073081600,6629012851481331712,1239210116298387712,3068744791442939904,6498464296863190528,1351960566961750656,2130941976600291456,6083701538482073216,4289043058639757440,4778709187671383040]
g=Table.read('xmm/s13_good.ecsv'); gx={int(r['u_gid']):r for r in g}
ids=','.join(map(str,L))
q=f"SELECT s.source_id,s.ra,s.dec,s.phot_g_mean_mag,s.bp_rp,s.parallax,s.parallax_error,s.ruwe,d.r_med_geo FROM gaiadr3.gaia_source s LEFT JOIN external.gaiaedr3_distance d ON d.source_id=s.source_id WHERE s.source_id IN ({ids})"
r=requests.get('https://gea.esac.esa.int/tap-server/tap/sync',params=dict(REQUEST='doQuery',LANG='ADQL',FORMAT='csv',QUERY=q),timeout=300); G=pd.read_csv(io.StringIO(r.text)).set_index('source_id')
v=Vizier(columns=['Jmag','Hmag','Kmag','W1mag','W2mag','_r'],row_limit=1)
H={"Authorization":"Bearer "+open(os.path.expanduser("~/.config/ads/token")).read().strip()}
sim=Table.read('xmm/sim_tmp.ecsv') if os.path.exists('xmm/sim_tmp.ecsv') else None
for i in L:
    x=gx[i]; s=G.loc[i]; d=s['r_med_geo']; Lx=4*np.pi*(d*3.086e18)**2*x['x_ep_flux']
    c=SkyCoord(s['ra'],s['dec'],unit='deg'); J=W1=Hm=np.nan
    try:
        t=v.query_region(c,radius=3*u.arcsec,catalog='II/246/out'); J=float(t[0]['Jmag'][0]); Hm=float(t[0]['Hmag'][0])
    except Exception: pass
    try:
        t=v.query_region(c,radius=3*u.arcsec,catalog='II/328/allwise'); W1=float(t[0]['W1mag'][0])
    except Exception: pass
    MG=s['phot_g_mean_mag']-5*np.log10(d/10); Lb=3.828e33*10**(-0.4*(MG-2.9-4.74))
    print(i,x['u_lst'],'G=%.2f BR=%.2f d=%.0f ruwe=%.2f Fx(0.2-12)=%.1e ML=%.0f sep=%.1f logLx=%.1f logLx/Lbol(sdB BC)=%.1f G-J=%.2f J-H=%.2f G-W1=%.2f'%(s['phot_g_mean_mag'],s['bp_rp'],d,s['ruwe'],x['x_ep_flux'],x['x_ep_det_ml'],x['sep'],np.log10(Lx),np.log10(Lx/Lb),s['phot_g_mean_mag']-J,J-Hm,s['phot_g_mean_mag']-W1),'var',x['x_var_flag'],flush=True)
