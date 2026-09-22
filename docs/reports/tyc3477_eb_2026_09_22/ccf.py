import warnings,math; warnings.filterwarnings("ignore")
import numpy as np
from astropy.io import fits
from scipy.ndimage import percentile_filter, gaussian_filter1d
C=299792.458
def norm(w,f,good,win=301):
    ff=np.where(good,f,np.nan); med=np.nanmedian(ff); ff=np.where(np.isfinite(ff),ff,med)
    cont=percentile_filter(ff,90,size=win,mode="nearest"); cont=gaussian_filter1d(cont,win/4)
    return f/cont
# ---- target visit (observed frame) ----
h=fits.open("target_apVisit.fits"); F=h[1].data; E=h[2].data; M=h[3].data; W=h[4].data
tw,tf,te=[],[],[]
for c in range(3):
    good=(M[c]&(1|2|4|8|16|32|64|4096))==0      # BADPIX|CRPIX|SATPIX|UNFIXABLE|BADDARK|BADFLAT|BADERR|SIG_SKYLINE
    good&=np.isfinite(F[c])&(F[c]>0)
    n=norm(W[c],F[c],good); ok=good&np.isfinite(n)&(n>0.2)&(n<1.3)
    tw.append(W[c][ok]); tf.append(n[ok]); te.append((E[c]/F[c]*n)[ok])
tw=np.concatenate(tw); tf=np.concatenate(tf); te=np.concatenate(te); o=np.argsort(tw); tw,tf,te=tw[o],tf[o],te[o]
print(f"target: {len(tw)} good pixels {tw.min():.0f}-{tw.max():.0f} A, median S/N {np.median(1/te):.0f}")
def apstar(fn,row=0):
    hh=fits.open(fn); d=hh[1].data; d=d[row] if d.ndim==2 else d
    w=10**(hh[1].header["CRVAL1"]+hh[1].header["CDELT1"]*np.arange(hh[1].header["NAXIS1"]))
    good=np.isfinite(d)&(d>0); n=norm(w,d,good); ok=good&np.isfinite(n)&(n>0.2)&(n<1.3)
    return w[ok],n[ok]
Fw,Ff=apstar("tmpl_F.fits"); Kw,Kf=apstar("tmpl_K.fits"); Kbw,Kbf=apstar("tmpl_Kb.fits")
def shifted(w,f,v,grid):
    return np.interp(grid,w*(1+v/C),f,left=np.nan,right=np.nan)
def rot(w,f,vsini):   # rotational broadening in velocity space (log-lambda uniform grid assumed ~)
    if vsini<=0: return f
    dv=np.median(np.diff(np.log(w)))*C; n=int(vsini/dv)+1; x=np.arange(-n,n+1)*dv/vsini
    k=np.where(np.abs(x)<1,np.sqrt(1-x**2),0); k/=k.sum(); return np.convolve(f-1,k,mode="same")+1
def ccf(data,tw_,tmw,tmf,vs):
    out=[]
    x=1-data
    for v in vs:
        y=1-shifted(tmw,tmf,v,tw_); ok=np.isfinite(x)&np.isfinite(y)
        xx=x[ok]-x[ok].mean(); yy=y[ok]-y[ok].mean(); out.append((xx@yy)/math.sqrt((xx@xx)*(yy@yy)))
    return np.array(out)
vs=np.arange(-400,401,2.0)
# 1) primary velocity (observed frame) from the F template
cF=ccf(tf,tw,Fw,Ff,vs); vp=vs[np.argmax(cF)]
# refine
vv=np.arange(vp-6,vp+6,0.25); cc=ccf(tf,tw,Fw,Ff,vv); vp=vv[np.argmax(cc)]
print(f"primary (F template) velocity, observed frame: {vp:+.2f} km/s   CCF peak {cc.max():.3f}")
# 2) subtract the scaled F model at vp: target ~ 1 - a*(1-F)
Fm=shifted(Fw,Ff,vp,tw); ok=np.isfinite(Fm)
a=np.sum((1-tf[ok])*(1-Fm[ok]))/np.sum((1-Fm[ok])**2)
R=np.full_like(tf,np.nan); R[ok]=tf[ok]-(1-a*(1-Fm[ok]))+1     # residual, re-centred on 1
print(f"F-template line-depth scale a = {a:.3f}  (a<1 means the target's lines are DILUTED - third light ~{(1-a)*100:.0f}% if the template matches)")
print(f"residual rms {np.nanstd(R):.4f}  vs target noise {np.median(te):.4f}")
# 3) CCF of the residual with a rotationally broadened K template
rows=[]
for lab,(kw,kf) in (("K main (4356K)",(Kw,Kf)),("K check (4426K)",(Kbw,Kbf))):
    for vsini in (0,50):
        kfb=rot(kw,kf,vsini); c=ccf(R,tw,kw,kfb,vs)
        rows.append((lab,vsini,c))
        noise=np.std(c[np.abs(vs-vp)>250]) if np.any(np.abs(vs-vp)>250) else np.std(c)
        pk=np.argsort(c)[::-1]; peaks=[]
        for j in pk:
            if all(abs(vs[j]-q)>40 for q,_ in peaks): peaks.append((vs[j],c[j]))
            if len(peaks)>=4: break
        print(f"{lab:16s} vsini={vsini:2d}: top residual-CCF peaks (v_rel to primary, height/noise): "+
              "  ".join(f"{v-vp:+.0f}km/s ({h/np.std(c):.1f})" for v,h in peaks))
np.save("ccf_rows.npy",np.array([r[2] for r in rows])); np.save("vs.npy",vs); np.save("vp.npy",np.array([vp]))
# 4) POSITIVE CONTROL: inject two broadened K stars at vp-160 and vp+100 (each 6.5% of light) into the F TEMPLATE itself
Fg=shifted(Fw,Ff,vp,tw); Kinj=rot(Kw,Kf,50)
inj=(1-0.13)*Fg+0.065*shifted(Kw,Kinj,vp-160,tw)+0.065*shifted(Kw,Kinj,vp+100,tw)
inj=inj+np.random.default_rng(1).normal(0,np.median(te),inj.size)
Fm2=shifted(Fw,Ff,vp,tw); ok2=np.isfinite(Fm2)&np.isfinite(inj)
a2=np.sum((1-inj[ok2])*(1-Fm2[ok2]))/np.sum((1-Fm2[ok2])**2)
R2=np.full_like(inj,np.nan); R2[ok2]=inj[ok2]-(1-a2*(1-Fm2[ok2]))+1
c2=ccf(R2,tw,Kw,rot(Kw,Kf,50),vs)
for vt in (-160,100):
    j=np.argmin(abs(vs-(vp+vt))); print(f"POSITIVE CONTROL: injected K dwarf at {vt:+d} km/s -> residual-CCF there {c2[j]/np.std(c2):.1f} sigma (peak within 20 km/s: {c2[max(0,j-10):j+11].max()/np.std(c2):.1f})")
np.save("ccf_inj.npy",c2)
