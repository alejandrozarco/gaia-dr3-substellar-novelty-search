"""Stage 2: fix the 6.1" neighbour to a smooth SED from stage-1 fits, refit target; QC; per-epoch spectra."""
import numpy as np, pickle, glob, os, sys, multiprocessing as mp
import sxphot as S
from astropy.table import Table
from astropy.coordinates import SkyCoord
from scipy.interpolate import UnivariateSpline
cutdir, srcfile, stage1, out, nbname, anchor = sys.argv[1:7]
t=Table.read(srcfile); names=list(t['name'])
ra=np.array(t['ra']); dec=np.array(t['dec']); K=np.array(t['K'],float)
c0=SkyCoord(ra[0],dec[0],unit='deg'); r=SkyCoord(ra,dec,unit='deg').separation(c0).arcsec
sel=(r<1)|((K<15.0)&(r<60))|((K<16.0)&(r<15))
inb=names.index(nbname) if nbname!='none' else None
R1={x['fn']:x for x in pickle.load(open(stage1,'rb')) if x and 'err' not in x}
nbsed=None
if inb is not None:
    w=np.array([x['base']['wave'] for x in R1.values()]); f=np.array([x['base']['flux'][inb] for x in R1.values()])
    ok=np.isfinite(f); w,f=w[ok],f[ok]
    # binned medians in log-wavelength then smoothing spline
    edges=np.exp(np.linspace(np.log(0.74),np.log(5.02),46)); bc=[];bm=[];be=[]
    for a,b in zip(edges[:-1],edges[1:]):
        m=(w>=a)&(w<b)
        if m.sum()>=3: bc.append(np.median(w[m])); bm.append(np.median(f[m])); be.append(1.25*np.median(np.abs(f[m]-np.median(f[m])))/np.sqrt(m.sum())+1)
    bc,bm,be=map(np.array,(bc,bm,be))
    sp=UnivariateSpline(np.log(bc),bm,w=1/be,k=3,s=len(bc))
    nbsed=(bc,bm,be,sp)
    pickle.dump(dict(bc=bc,bm=bm,be=be),open(out.replace('.pkl','_nbsed.pkl'),'wb'))
free=np.where(sel)[0]
if inb is not None: free=free[free!=inb]
def one(fn):
    b=os.path.basename(fn)
    if b not in R1: return None
    x1=R1[b]; fr=S.load(fn)
    P=S.prepare(fr,ra,dec,itarget=0,rfit=6.0)
    if P is None: return None
    fixed={}
    if inb is not None:
        fnb=max(float(nbsed[3](np.log(x1['base']['wave']))),0.0)/x1['base']['fcorr']  # back to QR2 scale for subtraction
        fixed={inb:fnb}
    o=S.fit(P,shift=x1['shift'][:2],free=free,fixed=fixed,eps=0.03)
    o.pop('resid'); o.pop('data'); o['fn']=b; o['nbfixed']=fixed.get(inb,np.nan)*x1['base']['fcorr'] if inb is not None else np.nan
    o['stage1']=x1['base']['flux'][0]; o['stage1_deep']=x1['deep']['flux'][0]; o['stage1_r4']=x1['r4']['flux'][0]
    return o
if __name__=='__main__':
    fs=sorted(glob.glob(cutdir+'/*.npz'))
    with mp.Pool(3) as p: R=[x for x in p.map(one,fs,chunksize=4) if x]
    rows=[]
    for o in R:
        rows.append(dict(fn=o['fn'],mjd=o['mjd'],det=o['det'],wave=o['wave'],band=o['band'],flux=o['flux'][0],eflux=o['eflux'][0],
            chi2r=o['chi2r'],fq=o['fq'],flags_near=o['flags_near'],nmask_near=o['nmask_near'],fcorr=o['fcorr'],nbfixed=o['nbfixed'],
            stage1=o['stage1'],stage1_deep=o['stage1_deep'],stage1_r4=o['stage1_r4'],zodi=o['zodi'],xt=o['xt'],yt=o['yt']))
    T=Table(rows)
    # errors: scale by sqrt(chi2r) where >1 and add 3% systematic (Expl. Suppl. eq 19)
    T['eflux_tot']=np.sqrt((T['eflux']*np.sqrt(np.clip(T['chi2r'],1,None)))**2+(0.03*T['flux'])**2)
    # QC: masked pixels within 2.5 px, bad flags (TRANSIENT/OVERFLOW/SUR_ERROR/NONFUNC/PERSIST) within 2.5 px, fq>3
    bad=(1<<0)|(1<<1)|(1<<2)|(1<<6)|(1<<17)
    T['qc']=((T['nmask_near']==0)&((T['flags_near']&bad)==0)&(T['fq']<3)).astype(int)
    T['epoch']=np.digitize(T['mjd'],[60900,61100])
    # robust outlier rejection per epoch against a running median in log-wavelength (window 0.04 dex)
    T['clip']=0
    for e in range(3):
        m=np.where((T['epoch']==e)&(T['qc']==1))[0]
        lw=np.log10(T['wave'][m])
        for i,j in enumerate(m):
            nb=m[np.abs(lw-lw[i])<0.04]
            if len(nb)<4: continue
            med=np.median(T['flux'][nb]); mad=1.4826*np.median(np.abs(T['flux'][nb]-med))
            if abs(T['flux'][j]-med)>5*max(mad,T['eflux_tot'][j]): T['clip'][j]=1
    T.sort('wave'); T.write(out.replace('.pkl','.ecsv'),overwrite=True)
    pickle.dump(R,open(out,'wb'))
    print(len(T),'qc ok',T['qc'].sum(),'clipped',T['clip'].sum())
