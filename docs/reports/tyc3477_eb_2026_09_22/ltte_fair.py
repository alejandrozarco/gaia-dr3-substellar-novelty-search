import math, numpy as np
T=np.array([1750.6,2665.6,3388.1,3420.5]); O=np.array([-198.4,74.2,-22.6,-69.9]); S=np.array([20.6,11.0,7.8,11.0])
Po,eo,Tp,om=597.36,0.404,476.55,math.radians(7.8)
def kep(M,e):
    E=M.copy()
    for _ in range(60): E=E-(E-e*np.sin(E)-M)/(1-e*np.cos(E))
    return E
def shape(tt,tp,w):
    M=np.mod(2*np.pi*(tt-tp)/Po,2*np.pi); E=kep(M,eo)
    nu=2*np.arctan2(math.sqrt(1+eo)*np.sin(E/2),math.sqrt(1-eo)*np.cos(E/2))
    return (1-eo**2)/(1+eo*np.cos(nu))*np.sin(nu+w)+eo*np.sin(w)
def chi(tp,w):          # 3 free params (offset, slope, amplitude) - same as the Gaia fit
    X=np.vstack([np.ones_like(T),T-T.mean(),shape(T,tp,w)]).T/S[:,None]
    c,*_=np.linalg.lstsq(X,O/S,rcond=None); r=O/S-X@c; return float(r@r)
cg=chi(Tp,om)
tps=np.linspace(Tp,Tp+Po,1440,endpoint=False)
c=np.array([chi(tp,om) for tp in tps])
print(f"Gaia phase: chi2 = {cg:.2f}   (P, e, omega fixed at Gaia; only the orbital PHASE scanned)")
print(f"fraction of all phases that fit as well or better: {np.mean(c<=cg+1e-9):.3f}")
print(f"chi2 across phases: min {c.min():.2f}  median {np.median(c):.1f}  90th pct {np.percentile(c,90):.1f}")
print(f"best phase is {((tps[np.argmin(c)]-Tp+Po/2)%Po-Po/2):+.0f} d from Gaia's periastron time")
