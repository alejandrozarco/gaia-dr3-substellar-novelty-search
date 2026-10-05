import warnings; warnings.filterwarnings('ignore')
import numpy as np, json
from astropy.table import Table
from astropy.time import Time
g=json.load(open('gaia.json'))
RA0,DE0,PMRA,PMDE=g['RA_ICRS'],g['DE_ICRS'],g['pmRA'],g['pmDE']
def pos(ep):
    dt=ep-2016.0
    return RA0+PMRA*dt/3.6e6/np.cos(np.radians(DE0)), DE0+PMDE*dt/3.6e6
def sep(ra,de,ep):
    r,d=pos(ep); return 3600*np.hypot((ra-r)*np.cos(np.radians(DE0)),de-d)
def show(fn,racol,decol,epfun,cols):
    t=Table.read(fn)
    for row in t:
        ep=epfun(row); s=sep(row[racol],row[decol],ep)
        print(f'  sep={s:6.2f}" ep={ep:.2f} r0={row["_r"]:.1f}', {c:(None if np.ma.is_masked(row[c]) else (round(float(row[c]),3) if isinstance(row[c],(float,np.floating)) else row[c])) for c in cols})
print('SDSS DR16'); show('viz_SDSS_DR16_V_154_sdss16.ecsv','RA_ICRS','DE_ICRS',lambda r: Time(r['MJD'] if 'MJD' in r.colnames else r['ObsDate'],format='mjd' if 'MJD' in r.colnames else 'decimalyear').decimalyear if ('MJD' in r.colnames or 'ObsDate' in r.colnames) else 2003.0,['objID','class','mode','clean','upmag','e_upmag','gpmag','e_gpmag','rpmag','e_rpmag','ipmag','e_ipmag','zpmag','e_zpmag'])
t=Table.read('viz_SDSS_DR16_V_154_sdss16.ecsv'); print([c for c in t.colnames if 'bs' in c or 'MJD' in c or 'Date' in c or 'pm' in c.lower()][:20])
print('PS1'); show('viz_PS1_II_349_ps1.ecsv','RAJ2000','DEJ2000',lambda r: Time(r['Epoch'],format='mjd').decimalyear,['objID','Qual','Ng','gmag','e_gmag','rmag','e_rmag','imag','e_imag','zmag','e_zmag','ymag','e_ymag','gKmag','rKmag','iKmag'])
print('2MASS'); show('viz_2MASS_II_246_out.ecsv','RAJ2000','DEJ2000',lambda r: Time(r['JD'],format='jd').decimalyear,['2MASS','Jmag','e_Jmag','Hmag','e_Hmag','Kmag','e_Kmag','Qflg','Rflg','Bflg','Cflg'])
print('AllWISE'); show('viz_AllWISE_II_328_allwise.ecsv','RAJ2000','DEJ2000',lambda r: 2010.5,['AllWISE','W1mag','e_W1mag','W2mag','e_W2mag','W3mag','e_W3mag','W4mag','e_W4mag','ccf','ex','nb','snr1','snr2'])
print('CatWISE'); show('viz_CatWISE2020_II_365_catwise.ecsv','RA_ICRS','DE_ICRS',lambda r: 2015.4,['Name','W1mproPM','e_W1mproPM','W2mproPM','e_W2mproPM','pmRA','e_pmRA','pmDE','e_pmDE','snrW1pm','snrW2pm'])
t=Table.read('viz_CatWISE2020_II_365_catwise.ecsv'); print([c for c in t.colnames][60:])
print('unWISE'); show('viz_unWISE_II_363_unwise.ecsv','RAJ2000','DEJ2000',lambda r: 2015.0,['objID','FW1','e_FW1','FW2','e_FW2','q_W1','q_W2','fFW1','fFW2','FlagsW1','FlagsW2','Prim'])
