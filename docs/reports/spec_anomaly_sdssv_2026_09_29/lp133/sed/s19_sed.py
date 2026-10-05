"""Full SED of LP 133-754 = Gaia DR3 1609392862209121664 vs Koester DA 6718 K / log g 9.15 (SVO koester2 grid, bilinear interp).
All magnitudes AB. Model scaled to PS1 g,r,i,z. Outputs: sed_photometry.csv, sed_residuals.json, lp133_sed.png"""
import warnings; warnings.filterwarnings('ignore')
import numpy as np, json
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
lam=np.arange(900.,60000.,1.0)
def load(t,g):
    d=np.loadtxt(f'koester/da_{t}_{g:.2f}.txt'); return np.interp(lam,d[:,0],d[:,1],right=np.nan)
def koester(teff,logg):
    grid=[6250,6500,6750,7000,7250]; t0=max(x for x in grid if x<=teff); t1=min(x for x in grid if x>teff)
    wt=(teff-t0)/(t1-t0); wg=(logg-9.0)/0.25
    s=lambda g:(1-wt)*load(t0,g)+wt*load(t1,g)
    f=(1-wg)*s(9.0)+wg*s(9.25)
    bb=1/lam**5/np.expm1(1.438777e8/(lam*teff)); k=np.searchsorted(lam,29000)
    f[lam>29000]=bb[lam>29000]*f[k]/bb[k]; return f
def bbf(T): return 1/lam**5/np.expm1(np.clip(1.438777e8/(lam*T),1e-8,700))
def curve(fn):
    d=np.loadtxt(fn); l,T=d[:,0],d[:,1]; return np.interp(lam,l,T,left=0,right=0)
def synth(flam,T): return -2.5*np.log10(np.trapezoid(flam*T*lam,lam)/np.trapezoid(T*2.99792458e18/lam,lam))-48.6
def piv(T): return np.sqrt(np.trapezoid(T*lam,lam)/np.trapezoid(T/lam,lam))
JP={'u':'uJAVA','g':'gSDSS','r':'rSDSS','i':'iSDSS','z':'zSDSS'}
# (label, filterfile, mag_AB, err, kind, source/aperture, epoch, sep_arcsec)
P=[
('GALEX FUV','GALEX_GALEX.FUV',23.4,None,'limit','MAST GALEX GR6/7 GII tile GI3_079027_NGC5485 (1680 s); not detected; ~3-4 sigma field limit',2008.27,None),
('GALEX NUV','GALEX_GALEX.NUV',21.661,0.153,'det','MAST GALEX GR6/7 GII, pipeline mag (NUV_MAG)',2008.27,2.76),
('SDSS u','SLOAN_SDSS.u',20.171-0.04,0.041,'det','SDSS DR16 PSF (u_AB=u-0.04)',2003.19,0.10),
('SDSS g','SLOAN_SDSS.g',19.524,0.021,'det','SDSS DR16 PSF',2003.19,0.10),
('SDSS r','SLOAN_SDSS.r',19.239,0.017,'det','SDSS DR16 PSF',2003.19,0.10),
('SDSS i','SLOAN_SDSS.i',19.197,0.021,'det','SDSS DR16 PSF',2003.19,0.10),
('SDSS z','SLOAN_SDSS.z',19.302+0.02,0.057,'det','SDSS DR16 PSF (z_AB=z+0.02)',2003.19,0.10),
('PS1 g','PAN-STARRS_PS1.g',19.452,0.010,'det','PS1 DR1 mean PSF',2012.72,0.43),
('PS1 r','PAN-STARRS_PS1.r',19.229,0.008,'det','PS1 DR1 mean PSF',2012.72,0.43),
('PS1 i','PAN-STARRS_PS1.i',19.216,0.008,'det','PS1 DR1 mean PSF',2012.72,0.43),
('PS1 z','PAN-STARRS_PS1.z',19.239,0.011,'det','PS1 DR1 mean PSF',2012.72,0.43),
('PS1 y','PAN-STARRS_PS1.y',19.215,0.069,'det','PS1 DR1 mean PSF',2012.72,0.43),
('LS g (BASS)','BOK_BASS.g',22.5-2.5*np.log10(16.339),1.0857/(16.339*np.sqrt(222.558)),'det','LS DR9/DR10-north Tractor PSF (flux_g)',2015.5,0.01),
('LS r (BASS)','BOK_BASS.r',22.5-2.5*np.log10(21.149),1.0857/(21.149*np.sqrt(79.474)),'det','LS DR9/DR10-north Tractor PSF',2015.5,0.01),
('LS z (MzLS)','KPNO_MzLS.z',22.5-2.5*np.log10(19.63),1.0857/(19.63*np.sqrt(62.949)),'det','LS DR9/DR10-north Tractor PSF',2015.5,0.01),
]
jm=dict(r=(19.261,0.007),g=(19.478,0.013),i=(19.273,0.068),z=(19.284,0.051),u=(19.972,0.115),J0378=(19.799,0.102),J0395=(19.969,0.06),J0410=(19.835,0.073),J0430=(19.798,0.095),J0515=(19.363,0.064),J0660=(19.376,0.072),J0861=(19.291,0.106))
for b in ['u','J0378','J0395','J0410','J0430','g','J0515','r','J0660','i','J0861','z']:
    P.append((f'J-PLUS {b}',f'JPLUS.{JP.get(b,b)}',jm[b][0],jm[b][1],'det','J-PLUS DR3 MagABDualPointSources MAG_APER_COR_3_0 (tile 95126, 2017-05-02)',2017.33,0.02))
P+= [
('UHS J','UKIRT_WFCAM.J',18.668+0.938,0.084,'det','UHS DR1/DR3 jAperMag3 (Vega+0.938)',2014.57,0.05),
('UHS K','UKIRT_WFCAM.K',18.1+1.900,None,'limit','UHS DR3: not detected in K frame (2019.47); nominal survey 5sig depth K~18.1 Vega, NOT measured',2019.47,None),
('2MASS J','2MASS_2MASS.J',16.8+0.894,None,'limit','2MASS PSC: no source; all-sky limit J~16.8 Vega (uninformative)',1999.12,None),
('LS W1 (DR9)','WISE_WISE.W1',22.5-2.5*np.log10(3.247),1.0857/(3.247*np.sqrt(5.379)),'det','LS DR9-north forced unWISE (Tractor, AB); fracflux_w1=5.1 (heavily blended)',2015.5,0.01),
('LS W2 (DR9)','WISE_WISE.W2',22.5-2.5*np.log10(1.911),1.0857/(1.911*np.sqrt(1.469)),'det','LS DR9-north forced unWISE (AB); fracflux_w2=7.2',2015.5,0.01),
('LS W1 (DR11)','WISE_WISE.W1',22.5-2.5*np.log10(4.421),1.0857/(4.421*np.sqrt(8.735)),'det','LS DR11-north forced unWISE (AB); fracflux_w1=3.5',2016.0,0.00),
('LS W2 (DR11)','WISE_WISE.W2',22.5-2.5*np.log10(3.579),1.0857/(3.579*np.sqrt(1.794)),'det','LS DR11-north forced unWISE (AB); fracflux_w2=3.8',2016.0,0.00),
('CatWISE W1 (blend)','WISE_WISE.W1',17.462+2.699,0.055,'blend','CatWISE2020 W1mproPM; 3.46" from WD -> blend with REX neighbour 4-5"',2015.4,3.46),
('unWISE W1 (blend)','WISE_WISE.W1',22.5-2.5*np.log10(96.504)+2.699,1.0857*5.468/96.504,'blend','unWISE (Schlafly+2019) FW1 Vega nmgy; 3.61" offset -> blend',2015.0,3.61),
]
mod=koester(6718,9.15); bb=bbf(6718)
rows=[];fitm=[];fitk=[];fitb=[]
for lab,ff,m,e,kind,src,ep,sep in P:
    T=curve(f'filters/{ff}.dat'); lp=piv(T); mk=synth(mod,T); mb=synth(bb,T)
    rows.append(dict(band=lab,pivot_A=round(lp),mag_AB=round(m,3),err=None if e is None else round(e,3),kind=kind,source=src,epoch=ep,sep_arcsec=sep,_mk=mk,_mb=mb))
    if lab.startswith('PS1') and lab!='PS1 y': fitm.append(m); fitk.append(mk); fitb.append(mb)
offk=np.mean(np.array(fitm)-np.array(fitk)); offb=np.mean(np.array(fitm)-np.array(fitb))
for r in rows:
    r['model_DA']=round(r['_mk']+offk,3); r['model_BB']=round(r['_mb']+offb,3)
    r['resid_DA']=round(r['mag_AB']-r['model_DA'],3); r['resid_BB']=round(r['mag_AB']-r['model_BB'],3)
    r['sig_DA']=None if r['err'] is None else round(r['resid_DA']/max(r['err'],0.01),2)
import csv
with open('sed_photometry.csv','w',newline='') as fh:
    w=csv.DictWriter(fh,fieldnames=[k for k in rows[0] if not k.startswith('_')]); w.writeheader()
    for r in rows: w.writerow({k:v for k,v in r.items() if not k.startswith('_')})
for r in rows: print(f"{r['band']:20s} {r['pivot_A']:6d} {r['mag_AB']:7.3f} {str(r['err']):6s} {r['kind']:6s} DA {r['model_DA']:7.3f} res {r['resid_DA']:+.3f} ({r['sig_DA']})  BB res {r['resid_BB']:+.3f}")
# PS1 fit check chi2
print('PS1-griz rms about DA model: %.3f'%np.std(np.array(fitm)-np.array(fitk)-offk), ' about BB: %.3f'%np.std(np.array(fitm)-np.array(fitb)-offb))
# figure
fig,ax=plt.subplots(2,1,figsize=(9,7),sharex=True,gridspec_kw=dict(height_ratios=[3,1.3]))
fnu=lambda m:3631e6*10**(-0.4*m)  # microJy
fl_mod=mod*10**(-0.4*offk); fnu_mod=fl_mod*lam**2/2.99792458e18*1e29
ax[0].plot(lam/1e4,fnu_mod,color='0.6',lw=0.7,label='Koester DA 6718 K, log g 9.15 (scaled to PS1 griz)')
fnu_bb=bb*10**(-0.4*offb)*lam**2/2.99792458e18*1e29; ax[0].plot(lam/1e4,fnu_bb,color='C3',lw=0.7,ls='--',label='Blackbody 6718 K')
cols={'GALEX':'C4','SDSS':'C0','PS1':'C1','LS ':'C2','J-PLUS':'k','UHS':'C5','2MASS':'C7','LS W':'C2','CatWISE':'C8','unWISE':'C9'}
for r in rows:
    c=[v for k,v in cols.items() if r['band'].startswith(k)][0]; x=r['pivot_A']/1e4; y=fnu(r['mag_AB'])
    if r['kind']=='limit': ax[0].errorbar(x,y,yerr=0.3*y,uplims=True,fmt='v',color=c,ms=5)
    else:
        mk='o' if r['kind']=='det' else 'x'
        ax[0].errorbar(x,y,yerr=None if r['err'] is None else y*r['err']/1.0857,fmt=mk,color=c,ms=4,label=None)
        if r['err'] is not None and r['kind']=='det': ax[1].errorbar(x,r['resid_DA'],yerr=r['err'],fmt=mk,color=c,ms=4)
ax[0].set_xscale('log'); ax[0].set_yscale('log'); ax[0].set_ylim(0.3,200); ax[0].set_ylabel(r'$F_\nu$ ($\mu$Jy)')
for k,v in [('GALEX','C4'),('SDSS','C0'),('PS1','C1'),('LS DR9/11 (grz, forced W1/W2)','C2'),('J-PLUS DR3 3"','k'),('UHS J','C5'),('CatWISE/unWISE (blend)','C8')]: ax[0].plot([],[],'o',color=v,label=k)
ax[0].legend(fontsize=7,ncol=2); ax[0].set_title('LP 133-754 = Gaia DR3 1609392862209121664: SED')
ax[0].axvspan(0.425,0.4316,color='orange',alpha=0.3)
ax[1].axhline(0,color='0.5'); ax[1].set_ylim(1.2,-1.2); ax[1].set_ylabel('obs - DA model (mag)'); ax[1].set_xlabel(r'$\lambda$ ($\mu$m)')
ax[1].set_xlim(0.13,5.5)
plt.tight_layout(); plt.savefig('lp133_sed.png',dpi=130)
json.dump(dict(offset_DA=offk,offset_BB=offb,rows=[{k:v for k,v in r.items() if not k.startswith('_')} for r in rows]),open('sed_residuals.json','w'),indent=1,default=float)
