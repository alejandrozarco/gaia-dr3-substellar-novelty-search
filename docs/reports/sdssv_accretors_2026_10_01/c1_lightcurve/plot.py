import os
import numpy as np, pandas as pd, matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt, sys
from astropy.timeseries import LombScargle
W='.'
d=pd.read_csv(f'{W}/c1_lc_clean_full.csv')
fig=plt.figure(figsize=(11,13)); gs=fig.add_gridspec(4,2,height_ratios=[2.6,1.6,1.8,1.5])
a0=fig.add_subplot(gs[0,:]); a1=fig.add_subplot(gs[1,:]); a2=fig.add_subplot(gs[2,0]); a3=fig.add_subplot(gs[2,1]); a4=fig.add_subplot(gs[3,:])
col={'zg':'tab:green','zr':'tab:red'}
for f in ['zg','zr']:
    s=d[d['filter']==f]
    a0.errorbar(s.mjd,s.C1_flux,s.C1_err,fmt='.',ms=3,lw=0.3,color=col[f],alpha=0.6,label=f'C1 ZTF {f[1]} (N={len(s)})')
    a1.plot(s.mjd,s['ring180_f']+500,'.',ms=2,color=col[f],alpha=0.5)
    a1.plot(s.mjd,s['blank1_f'],'.',ms=2,color=col[f],alpha=0.5)
    a1.plot(s.mjd,s['ctl_star_G18.30_f']-500,'.',ms=2,color=col[f],alpha=0.5)
a0.axhline(0,color='k',lw=0.5); a0.axhline(91,color='b',ls=':',lw=0.8,label='Gaia G=18.90 flux level (~91 uJy)')
a0.set_ylim(-450,700); a0.set_ylabel('difference flux vs 2018 reference (uJy)'); a0.legend(fontsize=8,loc='upper left',ncol=3)
a0.set_title('C1 = Gaia DR3 2101985070870393856: forced PSF photometry on ZTF difference images\n(joint fit with KIC 6773282 at 2.56" + PSF-derivative terms; errors scaled by KIC-ring controls)',fontsize=9)
for t,lab in [(58675,'2019-07'),(59461,'2021-08')]: a0.annotate(lab,(t,600),ha='center',fontsize=8,color='m')
a1.set_ylim(-900,900); a1.set_ylabel('uJy'); a1.set_xlabel('MJD')
a1.set_title('controls: +500 = ring point mirrored through KIC (same 2.56" separation); 0 = blank sky; -500 = constant star G=18.30',fontsize=9)
for ax,(lo,hi),ttl in [(a2,(59435,59490),'2021-08 episode'),(a3,(58664,58690),'2019-07 episode')]:
    w=d[(d.mjd>lo)&(d.mjd<hi)]
    for f in ['zg','zr']:
        s=w[w['filter']==f]; ax.errorbar(s.mjd,s.C1_flux,s.C1_err,fmt='o',ms=3,lw=0.6,color=col[f],label=f'C1 {f[1]}')
    for az,m in [(90,'x'),(180,'+'),(270,'1')]:
        ax.plot(w.mjd,w[f'ring{az}_f'],m,ms=4,color='gray',alpha=0.7,label=f'ring {az} deg' if az==90 else None)
    ax.axhline(0,color='k',lw=0.5); ax.set_title(ttl+' (grey = ring controls)',fontsize=9); ax.set_xlabel('MJD'); ax.set_ylabel('uJy'); ax.set_ylim(-500,700)
a2.legend(fontsize=7)
EXCL=[58674,58675,58676,58677,58912,59314,59316,59319,59454,59458,59460,59462,59464,59466]
q=[]
for f in ['zg','zr']:
    s=d[(d['filter']==f)&~np.floor(d.mjd).astype(int).isin(EXCL)].copy(); yy=s.C1_flux-s.base; r=1.4826*np.median(np.abs(yy-np.median(yy))); s=s[np.abs(yy)<5*r].copy(); s['y']=s.C1_flux-s.base; q.append(s)
q=pd.concat(q)
fr,pw=LombScargle(q.mjd,q.y,q.C1_err).autopower(minimum_frequency=0.1,maximum_frequency=50,samples_per_peak=5,method='fast')
a4.plot(fr,pw,lw=0.4,color='k'); a4.set_xlabel('frequency (cycles/day)'); a4.set_ylabel('LS power')
if len(sys.argv)>1: a4.axhline(float(sys.argv[1]),color='r',ls='--',lw=0.8,label='1% FAP (shuffle)'); a4.legend(fontsize=8)
a4.set_title('Lomb-Scargle of C1 (g+r, per-filter-season median removed, episode nights excluded, 5-sigma clipped)',fontsize=9)
plt.tight_layout(); plt.savefig(f'{W}/c1_ztf_forced_diffphot.png',dpi=80)
