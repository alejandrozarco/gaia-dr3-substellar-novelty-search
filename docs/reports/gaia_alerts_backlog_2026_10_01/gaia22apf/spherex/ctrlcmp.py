"""Compare SPHEREx fluxes of control stars with 2MASS/WISE/IRAC: synthetic band averages (tophat over band, median of per-frame fluxes)"""
import numpy as np, pickle, sys
from astropy.table import Table
from astropy.coordinates import SkyCoord
bands={'J':(1.11,1.39,1.235,1594.,'Jmag'),'H':(1.50,1.80,1.662,1024.,'Hmag'),'Ks':(2.00,2.31,2.159,666.7,'Kmag'),
       'W1':(2.80,3.90,3.353,309.54,'W1mag'),'W2':(4.00,5.0,4.603,171.79,'W2mag')}
def sxband(R,lo,hi,var='base'):
    w=np.array([x[var]['wave'] for x in R]); f=np.array([x[var]['flux'][0] for x in R])
    m=(w>=lo)&(w<hi)&np.isfinite(f)
    if m.sum()<2: return np.nan,np.nan,0
    return np.median(f[m]),1.2533*np.std(f[m])/np.sqrt(m.sum()),m.sum()
def run(pkl,ra,dec,tm,aw):
    R=[x for x in pickle.load(open(pkl,'rb')) if x and 'err' not in x]
    c=SkyCoord(ra,dec,unit='deg')
    t2=tm[np.argmin(SkyCoord(tm['RAJ2000'],tm['DEJ2000'],unit='deg').separation(c).arcsec)]
    sa=SkyCoord(aw['RAJ2000'],aw['DEJ2000'],unit='deg').separation(c).arcsec; ia=np.argmin(sa)
    out=[]
    for b,(lo,hi,lc,zp,col) in bands.items():
        if b.startswith('W'):
            if sa[ia]>2.5: continue
            mag=float(aw[col][ia])
        else: mag=float(t2[col])
        ref=zp*1e6*10**(-0.4*mag)
        s,e,n=sxband(R,lo,hi)
        out.append((b,mag,ref,s,e,n,s/ref))
    return out
if __name__=='__main__':
    tm=Table.read('field_tmass.ecsv'); aw=Table.read('field_allwise.ecsv')
    for lab in ['s16','fs27','fs28','fs31']:
        sc=Table.read(f'fieldctrl/scene_{lab}.ecsv')
        print(lab)
        for row in run(f'fieldctrl/phot_{lab}.pkl',sc['ra'][0],sc['dec'][0],tm,aw):
            print('  %-3s mag=%6.3f ref=%8.0f uJy  SPHEREx=%8.0f +-%5.0f (n=%3d)  ratio=%.3f'%row)
