# Gate the good eRASS:3 matches (pany>0.5) of Culpan candidates + knownhsd against SIMBAD cone (10") and catalogue xMatch.
# Each catalogue is probed with a known object first; an empty probe = HOLE.
import numpy as np, time, pyvo
from astropy.table import Table, vstack, unique
from astroquery.xmatch import XMatch
import astropy.units as u
g=Table.read('s04_good154_simbad.ecsv'); g=unique(g,keys='GaiaEDR3')
k=Table.read('s03_knownhsd_x_dr2mg.ecsv'); k=k[k['pany']>0.5]
c=Table({'GaiaEDR3':np.r_[np.array(g['GaiaEDR3']),np.array(k['GaiaEDR3'])],'ra':np.r_[np.array(g['RA_ICRS']),np.array(k['RA_ICRS'])],'dec':np.r_[np.array(g['DE_ICRS']),np.array(k['DE_ICRS'])],
  'src':['culpan_cand']*len(g)+['culpan_known']*len(k)})
c=unique(c,keys='GaiaEDR3'); print('objects',len(c))
# probes: AM Her (VSX, RK, Downes), RR Pic (Wang&Takata cvs?), 4U1626-67 (4XMM), HD49798
probe=Table({'GaiaEDR3':[0,1,2],'ra':[274.05542,98.9003,248.0695],'dec':[49.86836,-62.6401,-67.4612],'src':['probe_AMHer','probe_RRPic','probe_4U1626']})
cc=vstack([c,probe])
cats={'VSX':('vizier:B/vsx/vsx',10),'RK_cb':('vizier:B/cb/cbdata',10),'RK_lmxb':('vizier:B/cb/lmxbdata',10),'RK_pcb':('vizier:B/cb/pcbdata',10),'Downes':('vizier:V/123A/cv',10),
 'WangTakata_cvs':('vizier:J/A+A/698/A321/cvs',10),'WangTakata_cand':('vizier:J/A+A/698/A321/cand',10),'Rodriguez25_300':('vizier:J/PASP/137/A4201/cv_300',10),'Rodriguez25_1000':('vizier:J/PASP/137/A4201/cv_1000',10),
 '4XMM_DR13':('vizier:IX/69/xmm4d13s',10),'2RXS':('vizier:J/A+A/588/A103/cat2rxs',30),'GaiaVclass':('vizier:I/358/vclassre',3),'eRASS1_main':('vizier:J/A+A/682/A34/erass1-m',15)}
res={}
for lab,(cat,rad) in cats.items():
    for kk in range(3):
        try:
            r=XMatch.query(cat1=cc,cat2=cat,max_distance=rad*u.arcsec,colRA1='ra',colDec1='dec'); break
        except Exception as e:
            print(lab,'retry',str(e)[:100]); time.sleep(10); r=None
    if r is None: print(lab,'HOLE'); continue
    r.write(f's05_x_{lab}.ecsv',overwrite=True)
    pr=set(r['src'][np.char.startswith(np.array(r['src'],dtype=str),'probe')])
    print(f'{lab:18s} rows {len(r):4d} objs {len(set(r["GaiaEDR3"])-{0,1,2}):4d} probes hit: {sorted(pr)}',flush=True)
    res[lab]=r
c.write('s05_objects.ecsv',overwrite=True)
