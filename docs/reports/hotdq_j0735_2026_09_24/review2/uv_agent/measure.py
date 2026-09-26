import numpy as np, sys
sys.path.insert(0,'.')
from load import *
from scipy.optimize import curve_fit
c=2.99792458e5
EXP={'FP3(eiq)':load("lfac0zeiq_x1d.fits"),'FP4(eoq)':load("lfac0zeoq_x1d.fits"),'SUM':load("lfac0z010_x1dsum.fits")}
def seg_for(l): return 'FUVB' if l<1275 else 'FUVA'
def get(X,l,lo,hi,nb=2):
    d=X[seg_for(l)]; W,F,E,fr=binspec(d['w'],d['f'],d['e'],d['q'],nb); s=(W>lo)&(W<hi)&(fr>0.99)&(E>0)
    return W[s],F[s],E[s]
def gfit(X,l0,half=0.6,cw=(0.35,0.9),vguess=0,sig0=0.06,nb=2):
    """Gaussian absorption + linear continuum fit around l0*(1+vguess/c); continuum from annulus cw (A) on both sides."""
    lc=l0*(1+vguess/c)
    W,F,E=get(X,l0,lc-cw[1],lc+cw[1],nb)
    if len(W)<10: return None
    def m(w,a,b,d,mu,s): return (a+b*(w-lc))*(1-d*np.exp(-0.5*((w-mu)/s)**2))
    p0=[np.median(F),0,0.4,lc,sig0]
    try:
        p,cv=curve_fit(m,W,F,p0=p0,sigma=E,absolute_sigma=True,bounds=([0,-np.inf,-0.5,lc-0.4,0.015],[np.inf,np.inf,1.0,lc+0.4,0.6]),maxfev=20000)
    except Exception as e: return None
    ew=p[2]*p[4]*np.sqrt(2*np.pi); 
    J=np.array([p[4]*np.sqrt(2*np.pi), p[2]*np.sqrt(2*np.pi)]); C=cv[np.ix_([2,4],[2,4])]; eew=np.sqrt(J@C@J)
    v=(p[3]/l0-1)*c; ev=np.sqrt(cv[3,3])/l0*c
    chi=np.sum(((F-m(W,*p))/E)**2)/(len(W)-5)
    return dict(ew=ew,eew=eew,v=v,ev=ev,fwhm_kms=2.355*p[4]/l0*c,chi=chi)
def boxew(X,l0,v,half,cont,nb=1):
    """box EW over l0(1+v/c)+-half, linear continuum from windows cont=[(a,b),(c,d)] in A offsets"""
    lc=l0*(1+v/c); d=X[seg_for(l0)]; w,f,e,q=d['w'],d['f'],d['e'],d['q']
    ok=(q>0)&(e>0)
    cs=np.concatenate([np.where(ok&(w>lc+a)&(w<lc+b))[0] for a,b in cont])
    pp=np.polyfit(w[cs],f[cs],1); cont_f=np.polyval(pp,w)
    s=ok&(np.abs(w-lc)<half); dw=np.gradient(w)
    ew=np.sum((1-f[s]/cont_f[s])*dw[s]); eew=np.sqrt(np.sum((e[s]/cont_f[s]*dw[s])**2))
    return ew,eew
