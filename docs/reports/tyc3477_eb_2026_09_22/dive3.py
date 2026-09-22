import warnings,pickle,math; warnings.filterwarnings("ignore")
import numpy as np
from scipy.optimize import minimize_scalar
P,T0=pickle.load(open("eph.pkl","rb"))
d=pickle.load(open("tess_spoc.pkl","rb"))
Pf=lambda x: np.asarray(getattr(x,"unmasked",x),dtype=float)
secs={}
for sec,v in d.items():
    t,f,e=Pf(v[0]),Pf(v[1]),Pf(v[2]); ok=np.isfinite(t)&np.isfinite(f)&np.isfinite(e); secs[sec]=(t[ok],f[ok],e[ok])
# sharpest template: 200-s sectors only
tt=np.concatenate([secs[s][0] for s in (76,77)]); ff=np.concatenate([secs[s][1] for s in (76,77)])
ph=((tt-T0)/P)%1.0; nb=600; cen=(np.arange(nb)+0.5)/nb
tmpl=np.array([np.median(ff[(ph>=k/nb)&(ph<(k+1)/nb)]) for k in range(nb)])
def tmpl_at(x,cad_d):
    if cad_d<=250/86400: return np.interp(x%1.0,cen,tmpl,period=1.0)
    w=cad_d/P; offs=np.linspace(-w/2,w/2,15)          # boxcar-integrate the template over the exposure
    return np.mean([np.interp((x+o)%1.0,cen,tmpl,period=1.0) for o in offs],axis=0)
print(f"ephemeris P={P:.6f} T0=BTJD {T0:.5f}; template from the 200-s sectors, integrated to each sector's cadence\n")
print(f"{'sector':>6} {'cad':>5}  {'O-C primary (s)':>18}  {'O-C secondary (s)':>18}   difference")
rows=[]
for sec in sorted(secs):
    t,f,e=secs[sec]; cad=np.median(np.diff(t))
    out=[]
    for c0 in (0.0,0.5):
        x=((t-T0)/P); dx=((x-c0+0.5)%1)-0.5; m=np.abs(dx)<0.12
        tm,fm,em=t[m],f[m],e[m]
        def chi(dt):
            mod=tmpl_at((tm-dt-T0)/P,cad); k=np.median(fm)/np.median(mod)   # local normalisation
            return np.sum(((fm-k*mod)/em)**2)
        g=np.linspace(-0.012,0.012,481); cc=[chi(v) for v in g]; g0=g[int(np.argmin(cc))]
        r=minimize_scalar(chi,bounds=(g0-6e-4,g0+6e-4),method="bounded"); c0v=r.fun; red=c0v/max(1,m.sum()-2)
        s=2e-6; lo=r.x
        while chi(lo)-c0v<red and s<0.01: lo-=s; s*=1.3
        s=2e-6; hi=r.x
        while chi(hi)-c0v<red and s<0.01: hi+=s; s*=1.3
        out.append((r.x*86400,(hi-lo)/2*86400))
    (op,ep),(os_,es)=out; diff=op-os_; sd=math.hypot(ep,es)
    rows.append((np.mean(t),op,ep,os_,es))
    print(f"{sec:6d} {cad*86400:5.0f}  {op:+9.1f} +/- {ep:5.1f}   {os_:+9.1f} +/- {es:5.1f}   {diff:+7.1f} +/- {sd:5.1f} ({abs(diff)/sd:.1f} sig)")
R=np.array(rows)
w=1/(R[:,2]**2+R[:,4]**2)
print("\nLTTE / geometric shifts move BOTH eclipses together; starspots usually move them in OPPOSITE directions.")
corr=np.corrcoef(R[:,1],R[:,3])[0,1]
print(f"correlation of primary vs secondary O-C across sectors: r = {corr:+.2f}")
avg=(R[:,1]/R[:,2]**2+R[:,3]/R[:,4]**2)/(1/R[:,2]**2+1/R[:,4]**2)
print("mean (primary+secondary) O-C per sector - the part a light-travel-time effect would produce:")
for r,a in zip(R,avg): print(f"   BTJD {r[0]:8.1f}   {a:+8.1f} s")
pickle.dump(R,open("etv_ps.pkl","wb"))
