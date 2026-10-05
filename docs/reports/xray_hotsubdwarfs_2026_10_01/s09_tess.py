"""TESS FFI period scan for gate survivors. TESScut 11x11; 3x3 aperture minus median of pixels outside the central 5x5; same pixels give a background LC.
Per orbit quadratic detrend, 5-sigma clip. Lomb-Scargle 0.1-40 c/d per sector (latest sectors first, up to NMAX) and combined. SPOC 2-min/20-s PDCSAP used too when present.
Output: tess/<gaia>.json + png."""
import sys, os, json, numpy as np, warnings; warnings.filterwarnings("ignore")
from astropy.io import fits; from astropy.wcs import WCS; from astropy.coordinates import SkyCoord; from astropy.timeseries import LombScargle
from astroquery.mast import Tesscut
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
from astropy.table import Table
NMAX=4
FR=np.linspace(0.1,40,200000)
def clean(t,y):
    o=np.zeros_like(y)*np.nan; br=np.r_[0,np.where(np.diff(t)>0.5)[0]+1,len(t)]
    for a,b in zip(br[:-1],br[1:]):
        if b-a>50: p=np.polyfit(t[a:b]-t[a],y[a:b],2); o[a:b]=y[a:b]-np.polyval(p,t[a:b]-t[a])
    ok=np.isfinite(o); s=1.4826*np.nanmedian(np.abs(o[ok]-np.nanmedian(o[ok]))); return ok&(np.abs(o)<5*s),o
def run(gid,ra,dec):
    c=SkyCoord(ra,dec,unit='deg'); res=dict(gid=gid,sectors=[])
    try: secs=sorted([int(s) for s in Tesscut.get_sectors(coordinates=c)['sector']])[::-1][:NMAX]
    except Exception as ex: res['error']=f'get_sectors {ex}'; return res
    res['n_sectors_available']=len(secs)
    T,Y,B=[],[],[]
    for sec in secs:
        p=f'tess/cache_{gid}_s{sec}.fits'
        try:
            if not os.path.exists(p): Tesscut.get_cutouts(coordinates=c,size=11,sector=sec)[0].writeto(p,overwrite=True)
        except Exception as ex: res['sectors'].append(dict(sector=sec,error=str(ex)[:80])); continue
        h=fits.open(p); d=h[1].data; x,y=WCS(h[2].header).world_to_pixel(c); xi,yi=int(round(float(x))),int(round(float(y)))
        q=(d['QUALITY']==0)&np.isfinite(d['TIME']); fl=d['FLUX'][q]; t=d['TIME'][q]+2457000.0
        yy,xx=np.mgrid[0:fl.shape[1],0:fl.shape[2]]; ap=(np.abs(xx-xi)<=1)&(np.abs(yy-yi)<=1); ring=(np.abs(xx-xi)>2)|(np.abs(yy-yi)>2)
        bk=np.nanmedian(fl[:,ring],axis=1); lc=np.nansum(fl[:,ap],axis=1)-bk*ap.sum(); med=np.nanmedian(lc)
        if not np.isfinite(med) or med<=0: bk=np.nanpercentile(fl[:,ring],10,axis=1); lc=np.nansum(fl[:,ap],axis=1)-bk*ap.sum(); med=np.nanmedian(lc)
        if not np.isfinite(med) or med<=0: res['sectors'].append(dict(sector=sec,error='nonpositive flux')); continue
        ok1,yv=clean(t,lc/med-1); ok2,bv=clean(t,bk*ap.sum()/med); ok=ok1&ok2&np.isfinite(yv)&np.isfinite(bv)
        t,yv,bv=t[ok],yv[ok],bv[ok]
        if len(t)<200: continue
        cad=np.median(np.diff(t))*86400; fmax=min(40,0.5/np.median(np.diff(t))*0.95); F=FR[FR<fmax]
        ls=LombScargle(t,yv); pw=ls.power(F); k=np.argmax(pw); pb=LombScargle(t,bv).power(F)
        A=np.hypot(*np.linalg.lstsq(np.vstack([np.sin(2*np.pi*F[k]*t),np.cos(2*np.pi*F[k]*t),np.ones_like(t)]).T,yv,rcond=None)[0][:2])
        kb=np.argmin(np.abs(F-F[k]))
        res['sectors'].append(dict(sector=sec,cad_s=round(cad),n=len(t),f_peak=round(F[k],5),P_peak_h=round(24/F[k],4),fap=float(f"{ls.false_alarm_probability(pw[k],minimum_frequency=0.1,maximum_frequency=fmax):.2g}"),
            pow=round(pw[k],4),bkg_pow_same_f=round(float(pb[max(kb-20,0):kb+20].max()),4),amp_pct=round(100*A,3),med_flux=round(float(med),1),rms_pct=round(100*np.std(yv),2)))
        T.append(t);Y.append(yv);B.append(bv)
    if T:
        t,y,b=map(np.concatenate,(T,Y,B)); fmax=min(40,0.5/np.median(np.diff(t))*0.95); F=FR[FR<fmax]
        ls=LombScargle(t,y); pw=ls.power(F); k=np.argmax(pw); pb=LombScargle(t,b).power(F)
        top=np.argsort(pw)[::-1]; peaks=[]
        for j in top:
            if all(abs(F[j]-F[m])>0.05 for m in peaks): peaks.append(j)
            if len(peaks)==4: break
        res['all']=dict(n=len(t),peaks=[(round(F[j],5),round(24/F[j],4),round(pw[j],4)) for j in peaks],fap=float(f"{ls.false_alarm_probability(pw[k],minimum_frequency=0.1,maximum_frequency=fmax):.2g}"),bkg_peak_f=round(F[np.argmax(pb)],4),bkg_peak_pow=round(pb.max(),4))
        fa=F[k]
        fig,ax=plt.subplots(1,2,figsize=(12,3.5)); ax[0].plot(F,pw,'k',lw=.5); ax[0].plot(F,-pb,'r',lw=.5); ax[0].set_xscale('log'); ax[0].set_xlabel('c/d')
        ph=(t*fa)%1; bn=np.linspace(0,1,26); mb=[np.median(y[(ph>=a)&(ph<b2)]) for a,b2 in zip(bn[:-1],bn[1:])]
        ax[1].plot(ph,y,',',color='0.7'); ax[1].plot((bn[:-1]+bn[1:])/2,mb,'ko'); ax[1].set_ylim(np.percentile(y,1),np.percentile(y,99)); ax[1].set_xlabel(f'phase f={fa:.5f} c/d')
        fig.suptitle(f'Gaia DR3 {gid} TESS FFI'); plt.tight_layout(); plt.savefig(f'tess/{gid}.png',dpi=80); plt.close()
    return res
if __name__=='__main__':
    M=Table.read('s07_props.ecsv'); S=M[~M['known_cv'].astype(bool)]
    for r in S:
        gid=int(r['GaiaEDR3'])
        if str(r['otype'])=='PN' or gid==5580229559184884224 or 'GW Vir' in str(r['simbad']): continue
        if os.path.exists(f'tess/{gid}.json'): continue
        try: res=run(gid,float(r['ra_1'] if 'ra_1' in M.colnames else r['ra']),float(r['dec_1'] if 'dec_1' in M.colnames else r['dec']))
        except Exception as ex: res=dict(gid=gid,error=str(ex)[:200])
        json.dump(res,open(f'tess/{gid}.json','w'),indent=1); print(gid,json.dumps(res.get('all',res.get('error','none'))),flush=True)
