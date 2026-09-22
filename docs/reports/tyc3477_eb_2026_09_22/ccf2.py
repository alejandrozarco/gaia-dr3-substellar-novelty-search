import warnings,math; warnings.filterwarnings("ignore")
import numpy as np
exec(open("ccf.py").read().split("# 1) primary velocity")[0])      # reuse loaders/helpers + target arrays
vp=float(np.load("vp.npy")[0])
def fit_primary(data,vsini):
    Fb=rot(Fw,Ff,vsini); Fm=shifted(Fw,Fb,vp,tw); ok=np.isfinite(Fm)&np.isfinite(data)
    # per-chip linear continuum tweak + line-depth scale
    Rm=np.full_like(data,np.nan); aa=[]
    for lo,hi in ((15100,15820),(15820,16450),(16450,17000)):
        m=ok&(tw>=lo)&(tw<hi)
        X=np.vstack([np.ones(m.sum()),(tw[m]-tw[m].mean())/500,-(1-Fm[m])]).T
        c,*_=np.linalg.lstsq(X,data[m],rcond=None); Rm[m]=data[m]-X@c+1; aa.append(c[2])
    return Rm,float(np.mean(aa))
best=None
for vsini in (0,5,10,15,20,25,30,40,50):
    Rr,a=fit_primary(tf,vsini); rms=np.nanstd(Rr)
    print(f"primary broadening vsini={vsini:2d}: residual rms {rms:.4f}  line-depth scale a={a:.3f}")
    if best is None or rms<best[0]: best=(rms,vsini,a,Rr)
rms,vb,ab,R=best
print(f"\nBEST: vsini_primary = {vb} km/s, residual rms {rms:.4f} (noise {np.median(te):.4f}), line-depth scale a = {ab:.3f} -> implied third light ~{(1-ab)*100:.0f}%")
Kb50=rot(Kw,Kf,50)
def search(Rr):
    c=ccf(Rr,tw,Kw,Kb50,vs); s=np.std(c[np.abs(vs-vp)>60]); return c,s
c,s=search(R)
far=np.abs(vs-vp)>60
print("residual CCF (K template, vsini 50) - highest peaks away from the primary:")
pk=[]; 
for j in np.argsort(np.where(far,c,-9))[::-1]:
    if all(abs(vs[j]-q)>40 for q in pk): pk.append(vs[j]); print(f"   {vs[j]-vp:+5.0f} km/s rel. primary: {c[j]/s:4.1f} sigma")
    if len(pk)>=4: break
# INJECTION INTO THE REAL SPECTRUM, full pipeline rerun
print("\nINJECTION into the REAL target spectrum (full pipeline incl. primary refit):")
for frac in (0.05,0.08,0.12):
    for dv_sys in (-30,0,30):
        v1,v2=vp+dv_sys-128,vp+dv_sys+128
        inj=(1-2*frac)*tf+frac*shifted(Kw,Kb50,v1,tw)+frac*shifted(Kw,Kb50,v2,tw)
        Ri,_=fit_primary(inj,vb); ci,si=search(Ri)
        j1,j2=np.argmin(abs(vs-v1)),np.argmin(abs(vs-v2))
        s1=ci[max(0,j1-8):j1+9].max()/si; s2=ci[max(0,j2-8):j2+9].max()/si
        print(f"   each K dwarf {frac*100:4.1f}% of H-band light, pair systemic {dv_sys:+d}: recovered {s1:4.1f} / {s2:4.1f} sigma")
