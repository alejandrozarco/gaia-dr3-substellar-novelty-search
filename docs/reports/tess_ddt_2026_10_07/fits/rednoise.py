# Red-noise-aware trapezoid fit of the WDJ1118-5442 eclipse in TESS S90 (20 s, 2 min) and S99 (2 min).
# Target: TIC 450781262 / Gaia DR3 5346312514819760896, P=0.093889794 d, T0 BJD_TDB 2460684.83515 (ATLAS mid-exposure corrected)
import numpy as np, glob, sys, json
from astropy.io import fits
from scipy.optimize import least_squares
rng=np.random.default_rng(42)
P=0.093889794; T0=2460684.83515-2457000.0; Ps=P*86400
W=1200.0
def load(f):
    d=fits.open(f)[1].data; t=d['TIME']; y=d['SAP_FLUX']; q=d['QUALITY']
    m=np.isfinite(t)&np.isfinite(y)&(q==0); t,y=np.asarray(t[m],float),np.asarray(y[m],float)
    yy=y.copy()
    for i0 in np.arange(t.min(),t.max(),0.25):
        s=(t>=i0)&(t<i0+0.25)
        if s.sum()>10: yy[s]=y[s]/np.median(y[s])
    cyc=np.round((t-T0)/P).astype(int)
    ph=(t-T0-cyc*P)*86400.0
    w=np.abs(ph)<W
    return t[w],ph[w],yy[w],cyc[w]
def model(p,ph,exp,ns):
    dep,tc,T14,tau,c,q=p
    out=np.zeros_like(ph)
    for k in np.linspace(-0.5,0.5,ns)*(ns>1):
        xx=np.abs(ph+k*exp-tc)
        out+=np.clip((T14/2-xx)/max(tau,1e-3),0,1)
    return c+q*(ph/1000.)**2-dep*out/ns
LB=[0,-200,100,0.5,0.9,-0.1]; UB=[0.06,200,1200,500,1.1,0.1]
def fit(ph,y,exp,ns,p0):
    r=least_squares(lambda p:model(p,ph,exp,ns)-y,p0,bounds=(LB,UB),x_scale=[1e-3,5,20,20,1e-3,1e-3])
    res=r.fun; J=r.jac
    cov=np.linalg.pinv(J.T@J)*np.sum(res**2)/(len(y)-6)
    return r.x,np.sqrt(np.diag(cov)),res
def beta(t,res,cad):
    # time-averaging beta over bin widths 60-600 s, in time order, within contiguous chunks
    o=np.argsort(t); r=res[o]; s1=np.std(r); bs=[]
    for wsec in [60,120,180,240,300,420,600]:
        n=max(1,int(round(wsec/cad)))
        if n<2: continue
        M=len(r)//n; rb=r[:M*n].reshape(M,n).mean(1)
        bs.append(np.std(rb)/(s1/np.sqrt(n)*np.sqrt(M/(M-1.))))
    return np.array(bs)
files={'S90_20s':(glob.glob('lc_450781262/mastDownload/TESS/*a_fast/*.fits')[0],20.,7),
       'S90_2min':(glob.glob('lc_450781262/mastDownload/TESS/*s0090*-s/*.fits')[0],120.,15),
       'S99_2min':(glob.glob('lc_450781262/mastDownload/TESS/*s0099*-s/*.fits')[0],120.,15)}
if __name__=='__main__':
    NB=int(sys.argv[1]) if len(sys.argv)>1 else 300
    out={}
    names=['depth','tc_s','T14_s','tau_s','c','q']
    for key,(f,exp,ns) in files.items():
        t,ph,y,cyc=load(f)
        p0=[0.01,0,430,80,1.0,0.0]
        p,e,res=fit(ph,y,exp,ns,p0)
        b=beta(t,res,exp)
        mod=model(p,ph,exp,ns)
        # prayer bead: cyclic shift of time-ordered residuals
        o=np.argsort(t); rs=res[o]; pb=[]
        for k in np.linspace(0,len(rs),NB,endpoint=False).astype(int)[1:]:
            yk=np.empty_like(y); yk[o]=mod[o]+np.roll(rs,k)
            pb.append(fit(ph,yk,exp,ns,p)[0])
        pb=np.array(pb)
        # cycle bootstrap (resample whole eclipse windows)
        uc=np.unique(cyc); idx={c:np.where(cyc==c)[0] for c in uc}; bs=[]
        for i in range(NB):
            sel=np.concatenate([idx[c] for c in rng.choice(uc,len(uc))])
            bs.append(fit(ph[sel],y[sel],exp,ns,p)[0])
        bs=np.array(bs)
        def pct(a): return [float(x) for x in np.percentile(a,[16,50,84])]
        out[key]=dict(N=int(len(y)),ncyc=int(len(uc)),rms=float(np.std(res)),best=dict(zip(names,map(float,p))),white_err=dict(zip(names,map(float,e))),
                     beta=[float(x) for x in b],beta_med=float(np.median(b)),
                     prayer={n:pct(pb[:,i]) for i,n in enumerate(names[:4])},
                     cycboot={n:pct(bs[:,i]) for i,n in enumerate(names[:4])},
                     cycboot_tau_lt40=float(np.mean(bs[:,3]<40)))
        print(key,json.dumps(out[key],indent=None),flush=True)
        np.save(f'rn/{key}_boot.npy',bs); np.save(f'rn/{key}_pb.npy',pb)
    json.dump(out,open('rn/rednoise_results.json','w'),indent=1)
