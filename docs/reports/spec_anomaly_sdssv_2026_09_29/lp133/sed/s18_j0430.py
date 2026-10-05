"""LP 133-754 (Gaia DR3 1609392862209121664): J-PLUS DR3 J0430 CH G-band test.
Photometry: J-PLUS DR3 MagABDualPointSources (aperture-corrected 3" and 6" AB), CEFCA TAP.
Controls: GF21 WDs (Pwd>0.75, G<19.5, BP-RP 0.45-0.65) with J-PLUS DR3 matches."""
import warnings; warnings.filterwarnings('ignore')
import numpy as np, pickle, json
from astropy.table import Table
from scipy.optimize import minimize
F=['r','g','i','z','u','J0378','J0395','J0410','J0430','J0515','J0660','J0861']
FN={'r':'rSDSS','g':'gSDSS','i':'iSDSS','z':'zSDSS','u':'uJAVA'}
I={f:k for k,f in enumerate(F)}
curves={}
for f in F:
    d=np.loadtxt(f'filters/JPLUS.{FN.get(f,f)}.dat'); curves[f]=d
def pivot(d): l,T=d[:,0],d[:,1]; return np.sqrt(np.trapezoid(T*l,l)/np.trapezoid(T/l,l))
LP={f:pivot(curves[f]) for f in F}
print('pivots',{f:round(LP[f]) for f in F})
lam=np.arange(900.,30000.,1.0)
def synth_ab(flam,f):   # flam on grid lam (erg/s/cm2/A), photon-counting AB mag
    l,T=curves[f][:,0],curves[f][:,1]; Ti=np.interp(lam,l,T,left=0,right=0)
    fnu_mean=np.trapezoid(flam*Ti*lam,lam)/np.trapezoid(Ti*2.99792458e18/lam,lam)
    return -2.5*np.log10(fnu_mean)-48.6
def bb(T): 
    x=1.438777e8/(lam*T); return 1/lam**5/np.expm1(np.clip(x,1e-8,700))
BBT=np.arange(4000,12001,50); BBM={f:np.array([synth_ab(bb(T),f) for T in BBT]) for f in ['J0410','J0430','J0515','r','i','J0861','z']}
def koester(teff,logg):
    grid=[6250,6500,6750,7000,7250]
    t0=max(g for g in grid if g<=teff); t1=min(g for g in grid if g>teff)
    def load(t,g):
        d=np.loadtxt(f'koester/da_{t}_{g:.2f}.txt'); return np.interp(lam,d[:,0],d[:,1])
    wt=(teff-t0)/(t1-t0); wg=(logg-9.0)/0.25
    s=lambda g:(1-wt)*load(t0,g)+wt*load(t1,g)
    return (1-wg)*s(9.0)+wg*s(9.25)
# ---- CH profile prediction
def ch_profile(depth=0.55):
    p=np.ones_like(lam)
    a=(lam>=4250)&(lam<=4309); p[a]=1-depth*(lam[a]-4250)/(4309-4250)
    b=(lam>4309)&(lam<=4316); p[b]=(1-depth)+depth*(lam[b]-4309)/(4316-4309)
    return p
mod=koester(6718,9.15)
EW=np.trapezoid(1-ch_profile(),lam)
pred={f:synth_ab(mod*ch_profile(),f)-synth_ab(mod,f) for f in ['J0410','J0430','J0515','g']}
print('CH profile EW = %.1f A; predicted mag deficit:'%EW,{k:round(v,4) for k,v in pred.items()})
wI=(LP['J0515']-LP['J0430'])/(LP['J0515']-LP['J0410'])
pred_interp=pred['J0430']-(wI*pred['J0410']+(1-wI)*pred['J0515'])
# Hgamma/Hdelta effect of DA model on interp metric (model without CH)
mod_interp=synth_ab(mod,'J0430')-(wI*synth_ab(mod,'J0410')+(1-wI)*synth_ab(mod,'J0515'))
bbm=bb(6718); bb_interp=synth_ab(bbm,'J0430')-(wI*synth_ab(bbm,'J0410')+(1-wI)*synth_ab(bbm,'J0515'))
print('interp weight on J0410 %.3f; metric-(a) predicted CH signal %.4f; DA6718/9.15 model intrinsic metric %.4f; BB6718 intrinsic %.4f'%(wI,pred_interp,mod_interp,bb_interp))
# ---- measurement functions
FIT=['J0410','J0515','r','i','J0861','z']
def metrics(m,e):
    a=m[I['J0430']]-(wI*m[I['J0410']]+(1-wI)*m[I['J0515']])
    ea=np.sqrt(e[I['J0430']]**2+(wI*e[I['J0410']])**2+((1-wI)*e[I['J0515']])**2)
    # BB fit to FIT bands (free T, offset), residual at J0430
    mm=np.array([m[I[f]] for f in FIT]); ee=np.array([max(e[I[f]],0.02) for f in FIT])
    best=(1e99,None,None)
    for k,T in enumerate(BBT):
        mb=np.array([BBM[f][k] for f in FIT]); w=1/ee**2; off=np.sum(w*(mm-mb))/np.sum(w); c2=np.sum(w*(mm-mb-off)**2)
        if c2<best[0]: best=(c2,k,off)
    c2,k,off=best
    b=m[I['J0430']]-(BBM['J0430'][k]+off)
    return a,ea,b,BBT[k],c2
out={}
tgt=Table.read('jplus_target_raw.ecsv')  # dualobj raw (not used for mags)
T3=dict(m=np.array([19.261,19.478,19.273,19.284,19.972,19.799,19.969,19.835,19.798,19.363,19.376,19.291]),e=np.array([0.007,0.013,0.068,0.051,0.115,0.102,0.06,0.073,0.095,0.064,0.072,0.106]))
T6=dict(m=np.array([19.269,19.5,19.319,19.167,20.115,19.79,19.978,19.761,20.07,19.343,19.518,19.236]),e=np.array([0.01,0.017,0.119,0.075,0.205,0.159,0.082,0.107,0.194,0.097,0.129,0.173]))
rows=pickle.load(open('jplus_ctrl_rows.pkl','rb'))
pool=Table.read('gf21_ctrl_infoot.ecsv'); G={int(r['GaiaEDR3']):float(r['Gmag']) for r in pool}; BR={int(r['GaiaEDR3']):float(r['BPmag']-r['RPmag']) for r in pool}
res={}
for ap,Tt,mk,ek in [('3arcsec',T3,'m3','e3'),('6arcsec',T6,'m6','e6')]:
    ta,tea,tb,tT,tc2=metrics(Tt['m'],Tt['e'])
    # Koester-model residual for target
    km={f:synth_ab(mod,f) for f in F}
    fitb=[f for f in F if f not in ('J0430','g','J0660')]
    w=np.array([1/max(Tt['e'][I[f]],0.02)**2 for f in fitb]); d=np.array([Tt['m'][I[f]]-km[f] for f in fitb])
    off=np.sum(w*d)/np.sum(w); kres={f:round(float(Tt['m'][I[f]]-km[f]-off),3) for f in F}
    C=[]
    for x in rows:
        if x['sep']>1.5: continue
        m,e=x[mk],x[ek]
        need=[I[f] for f in ['J0410','J0430','J0515']+FIT]
        if np.any(~np.isfinite(m[need]))|np.any(m[need]>50)|np.any(e[need]<=0)|np.any(e[need]>1): continue
        if np.any(x['flags'][need]!=0) or np.any(x['mask_flags'][need]!=0): continue
        a,ea,b,T,c2=metrics(m,e)
        C.append((x['gid'],G[x['gid']],BR[x['gid']],a,ea,b,T,e[I['J0430']]))
    C=np.array(C)
    def rob(v): med=np.median(v); return med,1.4826*np.median(abs(v-med)),np.std(v)
    sel_all=np.ones(len(C),bool); sel_mag=(C[:,1]>=18.9)&(C[:,1]<=19.5)
    # nearest-50 in (G, BP-RP)
    dd=np.hypot((C[:,1]-19.234)/0.3,(C[:,2]-0.538)/0.05); near=np.argsort(dd)[:50]; sel_n=np.zeros(len(C),bool); sel_n[near]=True
    r={'target':dict(interp_delta=round(ta,3),interp_err=round(tea,3),bbres=round(tb,3),bbT=int(tT),koester_resid=kres,koester_offset=round(off,3))}
    for nm,sel in [('all',sel_all),('G18.9-19.5',sel_mag),('nearest50',sel_n)]:
        a=C[sel,3]; ea=C[sel,4]; b=C[sel,5]; z=a/ea
        ma,sa,stda=rob(a); mb,sb,stdb=rob(b); mz,sz,_=rob(z)
        r[nm]=dict(n=int(sel.sum()),interp_med=round(ma,3),interp_madsig=round(sa,3),interp_std=round(stda,3),
                   interp_median_err=round(float(np.median(ea)),3),
                   target_interp_sigma=round((ta-ma)/sa,2),target_interp_rank_frac=round(float(np.mean(a>=ta)),3),
                   z_med=round(mz,2),z_madsig=round(sz,2),target_z_dev=round((ta/tea-mz)/sz,2),
                   bb_med=round(mb,3),bb_madsig=round(sb,3),target_bb_sigma=round((tb-mb)/sb,2),target_bb_rank_frac=round(float(np.mean(b>=tb)),3))
    res[ap]=r
    np.savetxt(f'j0430_controls_{ap}.csv',C,delimiter=',',header='gaia_edr3,G,BP_RP,interp_delta_J0430,err,bb_resid_J0430,bbT,e_J0430',fmt='%.5g')
res['prediction']=dict(EW_A=round(EW,1),J0430_deficit_mag=round(pred['J0430'],4),J0410=round(pred['J0410'],4),J0515=round(pred['J0515'],4),g=round(pred['g'],4),metric_a_signal=round(pred_interp,4),DA_model_intrinsic_metric_a=round(mod_interp,4),BB_intrinsic_metric_a=round(bb_interp,4))
print(json.dumps(res,indent=1))
json.dump(res,open('j0430_result.json','w'),indent=1)
