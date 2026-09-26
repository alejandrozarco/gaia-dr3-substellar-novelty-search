import numpy as np, sys
sys.path.insert(0,'.')
from load import *
from scipy.optimize import curve_fit
c=2.99792458e5
EXP={'FP3':load("lfac0zeiq_x1d.fits"),'FP4':load("lfac0zeoq_x1d.fits"),'SUM':load("lfac0z010_x1dsum.fits")}
def seg_for(l): return 'FUVB' if l<1275 else 'FUVA'
def fitline(X,l0,v0=0,cin=0.3,cout=0.8,smax=0.15,nb=3,dv=0.25,cont=None):
    lc=l0*(1+v0/c); d=X[seg_for(l0)]; W,F,E,fr=binspec(d['w'],d['f'],d['e'],d['q'],nb)
    g=(fr>0.99)&(E>0)
    if cont is None: cont=[(-cout,-cin),(cin,cout)]
    cs=g&np.any([(W>lc+a)&(W<lc+b) for a,b in cont],axis=0)
    if cs.sum()<4: return None
    pp=np.polyfit(W[cs]-lc,F[cs],1,w=1/E[cs])
    s=g&(W>lc+min(a for a,b in cont))&(W<lc+max(b for a,b in cont))
    W,F,E=W[s],F[s],E[s]; C=np.polyval(pp,W-lc); y=F/C; ey=E/C
    def m(w,dd,mu,sg): return 1-dd*np.exp(-0.5*((w-mu)/sg)**2)
    best=None
    for mu0 in np.linspace(lc-dv*0.8,lc+dv*0.8,9):
        try:
            p,cv=curve_fit(m,W,y,p0=[0.3,mu0,0.05],sigma=ey,absolute_sigma=True,bounds=([-1.5,lc-dv,0.015],[1.2,lc+dv,smax]),maxfev=5000)
            chi=np.sum(((y-m(W,*p))/ey)**2)
            if best is None or chi<best[2]: best=(p,cv,chi)
        except Exception: pass
    if best is None: return None
    p,cv,chi=best
    ew=p[0]*p[2]*np.sqrt(2*np.pi); J=np.array([p[2],p[0]])*np.sqrt(2*np.pi); eew=np.sqrt(J@cv[np.ix_([0,2],[0,2])]@J)
    # box EW over +-2.5 sigma or +-0.15 A
    return dict(ew=ew,eew=eew,v=(p[1]/l0-1)*c,ev=np.sqrt(cv[1,1])/l0*c,fwhm=2.355*p[2]/l0*c,depth=p[0],chi=chi/(len(W)-3),n=len(W))
def boxew(X,l0,v,half,cont):
    lc=l0*(1+v/c); d=X[seg_for(l0)]; w,f,e,q=d['w'],d['f'],d['e'],d['q']
    ok=(q>0)&(e>0)
    cs=ok&np.any([(w>lc+a)&(w<lc+b) for a,b in cont],axis=0)
    pp=np.polyfit(w[cs],f[cs],1); cf=np.polyval(pp,w)
    s=ok&(np.abs(w-lc)<half); dw=np.gradient(w)
    return np.sum((1-f[s]/cf[s])*dw[s]), np.sqrt(np.sum((e[s]/cf[s]*dw[s])**2)), s.sum()
