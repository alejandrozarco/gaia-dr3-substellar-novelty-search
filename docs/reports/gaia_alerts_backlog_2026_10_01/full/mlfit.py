import pandas as pd, numpy as np, sys, json, warnings; warnings.filterwarnings('ignore')
from scipy.optimize import least_squares
from lcio import *
t=pd.read_csv('gates.csv').set_index('Name'); F=pd.read_csv('feat_gaia.csv').set_index('Name')
def A(tt,t0,tE,u0):
    u=np.sqrt(u0**2+((tt-t0)/tE)**2); return (u**2+2)/(u*np.sqrt(u**2+4))
def data(n):
    r=t.loc[n]; D=[]
    g=gaia(n); D.append(pd.DataFrame(dict(t=g.mjd,m=g.mag,e=np.full(len(g),max(F.loc[n].sig,0.02)),band='G')))
    z=ztf(n,r.RAdeg,r.DEdeg)
    if z is not None and len(z):
        for b in ('zg','zr'):
            x=z[z.filtercode==b]
            if len(x)>10: D.append(pd.DataFrame(dict(t=x.mjd.values,m=x.mag.values,e=np.hypot(x.magerr.values,0.02),band=b)))
    return pd.concat(D,ignore_index=True)
def fit(n):
    d=data(n); bands=list(d.band.unique()); f=F.loc[n]
    def model(p):
        t0,ltE,u0=p[:3]; out=np.empty(len(d))
        for i,b in enumerate(bands):
            m0,fs=p[3+2*i],p[4+2*i]; k=(d.band==b).values
            out[k]=m0-2.5*np.log10(fs*A(d.t.values[k],t0,10**ltE,u0)+1-fs)
        return out
    best=None
    for tE0 in (10,30,80,200):
        for u00 in (0.05,0.3,0.8):
            p0=[f.t_peak,np.log10(tE0),u00]; lo=[f.t_peak-300,-0.3,1e-4]; hi=[f.t_peak+300,3.3,3]
            for b in bands:
                mb=np.median(d.m[d.band==b]); p0+= [mb,0.9]; lo+=[mb-1,0.02]; hi+=[mb+1,1.0]
            try:
                s=least_squares(lambda p:(model(p)-d.m.values)/d.e.values,p0,bounds=(lo,hi),loss='soft_l1',f_scale=3)
                if best is None or s.cost<best.cost: best=s
            except Exception as e: pass
    p=best.x; res=(d.m.values-model(p)); chi=res/d.e.values
    t0,tE,u0=p[0],10**p[1],p[2]
    inev=np.abs(d.t-t0)<2*tE
    out=dict(Name=n,bands='+'.join(bands),N=len(d),t0=round(t0,1),tE=round(tE,1),u0=round(u0,3),
        chi2r=round(np.sum(chi**2)/(len(d)-len(p)),2),rms_in=round(np.std(res[inev]),3),rms_out=round(np.std(res[~inev]),3),
        n_in={b:int(((d.band==b)&inev).sum()) for b in bands},n_out_5sig=int((np.abs(chi[~inev])>5).sum()))
    for i,b in enumerate(bands): out[f'm0_{b}']=round(p[3+2*i],2); out[f'fs_{b}']=round(p[4+2*i],2)
    out['Amax']=round(A(np.array([t0]),t0,tE,u0)[0],2)
    return out,d,model(p),p,bands
if __name__=='__main__':
    rows=[]
    for n in sys.argv[1:]:
        try: o,*_=fit(n); rows.append(o); print(json.dumps(o),flush=True)
        except Exception as e: print(n,'ERR',e)
    pd.DataFrame(rows).to_csv('mlfit.csv',index=False)
