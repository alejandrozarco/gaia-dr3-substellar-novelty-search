import pandas as pd, numpy as np, warnings; warnings.filterwarnings('ignore')
from scipy.optimize import least_squares
from astropy.timeseries import LombScargle
t=pd.read_csv('gates.csv'); t=t[t.survive].reset_index(drop=True)
def lc(n):
    d=pd.read_csv(f'../glc/{n}.csv',skiprows=1); d.columns=['date','jd','mag']; d['mag']=pd.to_numeric(d.mag,errors='coerce'); d=d.dropna()
    d['t']=d.jd-2400000.5; return d.sort_values('t')
def groups(tt,gap):
    if len(tt)==0: return []
    g=[[tt[0]]]
    for x in tt[1:]:
        if x-g[-1][-1]>gap: g.append([x])
        else: g[-1].append(x)
    return g
def pac(p,tt):
    m0,t0,tE,u0,fs=p; u=np.sqrt(u0**2+((tt-t0)/tE)**2); A=(u**2+2)/(u*np.sqrt(u**2+4))
    return m0-2.5*np.log10(fs*A+1-fs)
rows=[]
for r in t.itertuples():
    d=lc(r.Name); m=d.mag.values; tt=d.t.values
    base=np.median(m); mad=1.4826*np.median(np.abs(m-base)); sig=max(mad,0.03)
    thr=max(0.4,5*sig)
    br=tt[m<base-thr]; fa=tt[m>base+thr]
    bg=groups(br,60); fg=groups(fa,60)
    ipk=np.argmin(m); tpk=tt[ipk]; amp=base-m[ipk]
    # Paczynski fit
    best=None
    for tE0 in (5,15,40,100):
        for fs0 in (1.0,0.5):
            for u00 in (0.1,0.5):
                p0=[base,tpk,tE0,u00,fs0]
                try:
                    f=least_squares(lambda p:(pac(p,tt)-m)/np.hypot(sig,0.02),p0,bounds=([base-1,tpk-200,0.5,1e-3,0.05],[base+1,tpk+200,1000,3,1.0]))
                    if best is None or f.cost<best.cost: best=f
                except Exception: pass
    res=m-pac(best.x,tt); rms=np.std(res); nout=np.sum(np.abs(res)>max(0.3,4*sig))
    # flat-model rms
    # outside-event behaviour: points far from peak (>3 tE and >60 d)
    far=np.abs(tt-best.x[1])>max(3*best.x[2],60)
    far_rms=1.4826*np.median(np.abs(m[far]-np.median(m[far]))) if far.sum()>5 else np.nan
    far_bright=np.sum(m[far]<base-thr)
    nev=np.sum(np.abs(tt-best.x[1])<best.x[2])
    # LS on full Gaia LC
    try:
        ls=LombScargle(tt,m); fr,pw=ls.autopower(minimum_frequency=1/1500,maximum_frequency=1/20,samples_per_peak=10)
        P=1/fr[np.argmax(pw)]; fap=ls.false_alarm_probability(pw.max())
    except Exception: P,fap=np.nan,np.nan
    k=len(m)//3; trend=np.median(m[-k:])-np.median(m[:k])
    rows.append(dict(Name=r.Name,npt=len(m),base=round(base,2),sig=round(sig,3),peak=round(m[ipk],2),amp=round(amp,2),faint=round(m.max(),2),
        t_peak=round(tpk,1),n_bright_ep=len(bg),n_bright_pts=len(br),n_fade_ep=len(fg),n_fade_pts=len(fa),
        ml_t0=round(best.x[1],1),ml_tE=round(best.x[2],1),ml_u0=round(best.x[3],3),ml_fs=round(best.x[4],2),ml_rms=round(rms,3),ml_nout=int(nout),ml_nev=int(nev),
        far_rms=round(far_rms,3),far_bright=int(far_bright),P_ls=round(P,1),fap_ls=fap,trend=round(trend,2),
        last_t=round(tt.max(),1),first_t=round(tt.min(),1)))
F=pd.DataFrame(rows); F.to_csv('feat_gaia.csv',index=False)
pd.set_option('display.width',250); pd.set_option('display.max_rows',200)
print(F.drop(columns=['first_t','fap_ls']).to_string())
