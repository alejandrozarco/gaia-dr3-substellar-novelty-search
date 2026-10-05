import os
import numpy as np, pandas as pd
from astropy.timeseries import LombScargle
W='.'
raw=pd.read_csv(f'{W}/forced_lc_raw.csv')
def rs(x): x=np.asarray(x); x=x[np.isfinite(x)]; return 1.4826*np.median(np.abs(x-np.median(x)))
print('status counts:\n',raw.status.value_counts().to_string())
print('ok by filter:\n',raw[raw.status=='ok'].groupby(['filter','field']).size().to_string())
d=raw[raw.status=='ok'].copy()
n0=len(d)
q=(d.infobits==0)&np.isfinite(d.C1o2_f)&(d.seeing<4.0)&(d.maglimit>19.5)&(np.abs(d.blank1_f)<5*d.blank1_e)&(d['filter'].isin(['zg','zr']))&(d.C1o2_chi<500)
print(f'ok={n0}  after cuts (infobits=0, seeing<4", maglimit>19.5, finite, blank1 sane, g/r, fit chi2nu<500 [masked-block artefacts])={q.sum()}')
d=d[q].copy()
M='C1o2'; CTL=['mirrorKICo2','rot90KICo2','rot270KICo2']
# normalised control residuals with chi-scaled errors
for c in [M]+CTL:
    d[c+'_es']=d[c+'_e']*np.sqrt(np.clip(d[c+'_chi'],1,None))
for c in CTL+['blank1','blank2','blank3','ctl_star_G18.30','ctl_star_G18.69','ctl_star_G18.68','mirrorB2']:
    e=d[c+'_es'] if c+'_es' in d else d[c+'_e']
    for f in ['zg','zr']:
        s=d['filter']==f
        print(f'{c:18s} {f} median {np.median(d.loc[s,c+"_f"]):7.1f} robstd {rs(d.loc[s,c+"_f"]):6.1f} uJy; robstd(f/err) {rs(d.loc[s,c+"_f"]/e[s]):5.2f}')
# per-epoch empirical floor: robust std of the 3 KIC-ring controls, per filter -> combine with chi-scaled error
d['C1_flux']=d[M+'_f']
for f in ['zg','zr']:
    s=d['filter']==f
    floor=rs(np.concatenate([d.loc[s,c+'_f'] for c in CTL]))
    # scale chi-scaled errors so control pulls have unit robust std
    pulls=np.concatenate([d.loc[s,c+'_f']/d.loc[s,c+'_es'] for c in CTL]); k=rs(pulls)
    d.loc[s,'C1_err']=d.loc[s,M+'_es']*k
    print(f'{f}: KIC-ring control floor {floor:.1f} uJy; error scale k={k:.2f}; median C1 err {np.median(d.loc[s,"C1_err"]):.1f}; C1 median {np.median(d.loc[s,"C1_flux"]):.1f} robstd {rs(d.loc[s,"C1_flux"]):.1f}')
d['ctl_max_pull']=np.max(np.abs(np.array([d[c+'_f']/(d[c+'_es']) for c in CTL])),axis=0)
d['mjd']=d.jd-2400000.5
d.to_csv(f'{W}/c1_lc_clean_full.csv',index=False)

# ---------------- outbursts ----------------
FQ=100.0  # uJy: quiescent anchor from Gaia G=18.90 (AB-ish; G zero point differs, order-of-magnitude anchor)
thr=FQ*(10**0.2-1)   # +0.5 mag above an F=100 uJy baseline -> +58 uJy
print(f'\nOutburst criterion: diff flux > 5 sigma AND > {thr:.0f} uJy (0.5 mag above F_q={FQ:.0f} uJy), controls quiet (max |pull|<3)')
d['season']=np.floor(2018+(d.jd-2458119.5)/365.25).astype(int)
d['base']=d.groupby(['filter','season']).C1_flux.transform('median')
d['sig']=(d.C1_flux-d.base)/d.C1_err
d['dflux']=d.C1_flux-d.base
cand=d[(d.sig>5)&(d.dflux>thr)]
print(f'raw >5sig & >thr: {len(cand)}; with quiet controls: {(cand.ctl_max_pull<3).sum()}')
# negative-tail comparison (same criteria mirrored) as false-positive rate estimate
neg=d[(d.sig<-5)&(d.dflux<-thr)]
print(f'mirror test: < -5sig & < -thr: {len(neg)}; with quiet controls {(neg.ctl_max_pull<3).sum()}')
for c in CTL:
    pc=d[c+'_f']/(d[c+'_es']*1.0)
print(cand.sort_values('mjd')[['mjd','filter','C1_flux','C1_err','sig','ctl_max_pull','C1o2_chi','seeing','dip_y']].round(2).to_string())
d.to_csv(f'{W}/c1_lc_clean_full.csv',index=False)
# nightly clustering of positive excursions
cq=cand[cand.ctl_max_pull<3].copy(); cq['night']=np.floor(cq.mjd).astype(int)
print('candidate nights:',sorted(set(cq.night)))
# for each candidate night: all epochs within +-3 d
for n in sorted(set(cq.night)):
    w=d[(d.mjd>n-3)&(d.mjd<n+4)]
    print(f'--- night {n}: epochs within -3..+4 d:')
    print(w[['mjd','filter','C1_flux','C1_err','sig','ctl_max_pull']].round(2).to_string())

print('\nper-epoch pulls vs per-filter-season median: N>+3:',(d.sig>3).sum(),' N<-3:',(d.sig<-3).sum(),' N>+4:',(d.sig>4).sum(),' N<-4:',(d.sig<-4).sum(),' of',len(d))
# nightly weighted means, C1 and the 3 KIC-ring controls
d['night']=np.floor(d.mjd).astype(int)
def nightly(col,ecol):
    g=d.groupby(['night','filter'])
    return g.apply(lambda s: pd.Series(dict(n=len(s),f=np.average(s[col]-s.base*(col=='C1_flux'),weights=s[ecol]**-2),e=np.sum(s[ecol]**-2)**-0.5)),include_groups=False)
nm=nightly('C1_flux','C1_err'); nm['sig']=nm.f/nm.e
print('nights x filter:',len(nm),' nightly C1 >+4 sig:',(nm.sig>4).sum(),' <-4:',(nm.sig<-4).sum(), ' >+3:',(nm.sig>3).sum(),' <-3:',(nm.sig<-3).sum())
for c in CTL:
    d[c+'_E']=d[c+'_es']*np.median(d.C1_err/d.C1o2_es)
    nc=nightly(c+'_f',c+'_E'); nc['sig']=(nc.f-np.median(nc.f))/nc.e
    print(f'  control {c}: nightly >+4: {(nc.sig>4).sum()}  <-4: {(nc.sig<-4).sum()}  >+3: {(nc.sig>3).sum()} <-3: {(nc.sig<-3).sum()}')
print(nm.sort_values('sig',ascending=False).head(10).round(1).to_string())
print('\ncorrelations of C1 flux (minus season median) with seeing / dip_y / mirror:')
for c in ['seeing','dip_y','mirrorKICo2_f','rot90KICo2_f','rot270KICo2_f','KIC_f']:
    print(f'  {c}: spearman r = {pd.Series(d.dflux).corr(d[c],method="spearman"):.3f}')
d.to_csv(f'{W}/c1_lc_clean_full.csv',index=False)

out=d[['mjd','filter','field','C1_flux','C1_err','base','sig',M+'_chi','KIC_f','dip_x','dip_y']+[f'ring{a}_f' for a in [90,120,150,180,210,240,270]]+['blank1_f','ctl_star_G18.30_f','seeing','maglimit','magzp','tag']].rename(columns={M+'_chi':'fit_chi2nu','KIC_f':'KIC_diff_flux','base':'season_median','sig':'pull_vs_season_median'})
hdr="# C1 = Gaia DR3 2101985070870393856 (RA 290.516500 Dec +42.259050). ZTF scimrefdiffimg forced PSF photometry (own code), fluxes in uJy (AB, MAGZP), relative to the 2018 reference image.\n# Joint fit: PSF at C1 + PSF at KIC 6773282 (Gaia DR3 2101985070870394368, 2.56 arcsec) + 1st/2nd PSF derivatives at KIC + constant. C1_err = formal*sqrt(chi2nu)*k (k from KIC-ring controls).\n# ringNNN_f = same-separation control points around KIC (azimuth from the C1 direction); blank1_f = blank sky; ctl_star_G18.30_f = constant star.\n"
open(f'{W}/c1_ztf_forced_diffphot.csv','w').write(hdr+out.to_csv(index=False,float_format='%.3f'))
