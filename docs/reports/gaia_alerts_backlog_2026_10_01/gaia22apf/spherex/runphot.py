import numpy as np, glob, sys, os, pickle, multiprocessing as mp
import sxphot as S
from astropy.table import Table
from astropy.coordinates import SkyCoord
cutdir=sys.argv[1]; srcfile=sys.argv[2]; out=sys.argv[3]; anchor=sys.argv[4] if len(sys.argv)>4 else ''
t=Table.read(srcfile)
c0=SkyCoord(t['ra'][0],t['dec'][0],unit='deg'); r=SkyCoord(t['ra'],t['dec'],unit='deg').separation(c0).arcsec
K=np.array(t['K'],float)
VAR={'base':dict(sel=(r<1)|((K<15.0)&(r<60))|((K<16.0)&(r<15)),rfit=6.0,eps=0.03),
     'deep':dict(sel=(r<1)|((K<16.0)&(r<60))|((K<17.0)&(r<15)),rfit=6.0,eps=0.03),
     'r4':dict(sel=(r<1)|((K<15.0)&(r<60))|((K<16.0)&(r<15)),rfit=4.0,eps=0.03),
     'noeps':dict(sel=(r<1)|((K<15.0)&(r<60))|((K<16.0)&(r<15)),rfit=6.0,eps=0.0)}
ra=np.array(t['ra']); dec=np.array(t['dec'])
if anchor=='auto':
    cand=np.where((K>10.0)&(K<12.5)&(r>8)&(r<35))[0]
    ia=int(cand[np.argmin(K[cand])]) if len(cand) else None
    print('anchor',None if ia is None else (t['name'][ia],K[ia],r[ia]))
else:
    ia=list(t['name']).index(anchor) if anchor else None
def one(fn):
    try:
        fr=S.load(fn); res={'fn':os.path.basename(fn)}
        free_base=np.where(VAR['base']['sel'])[0]
        if ia is not None:
            sh=S.solve_shift(fr,ra,dec,ia,free_base,rfit=3.0,eps=0.03)
        else: sh=(0.0,0.0,np.nan)
        res['shift']=sh
        for k,v in VAR.items():
            P=S.prepare(fr,ra,dec,itarget=0,rfit=v['rfit'])
            if P is None: return None
            o=S.fit(P,shift=sh[:2],free=np.where(v['sel'])[0],eps=v['eps'])
            o.pop('resid'); o.pop('data')
            res[k]=o
        return res
    except Exception as e:
        return {'fn':fn,'err':repr(e)}
if __name__=='__main__':
    fs=sorted(glob.glob(cutdir+'/*.npz'))
    with mp.Pool(3) as p: R=p.map(one,fs,chunksize=4)
    pickle.dump(R,open(out,'wb'))
    print(len(R),sum(1 for x in R if x is None),sum(1 for x in R if x and 'err' in x))
    for x in R:
        if x and 'err' in x: print(x['err'])
