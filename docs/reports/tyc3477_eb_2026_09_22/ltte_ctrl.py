import warnings,math; warnings.filterwarnings("ignore")
import numpy as np
from scipy.optimize import least_squares
T=np.array([1750.6,2665.6,3388.1,3420.5]); O=np.array([-198.4,74.2,-22.6,-69.9]); S=np.array([20.6,11.0,7.8,11.0])
Po,eo,Tp,om=597.36,0.404,476.55,math.radians(7.8)
def kep(M,e):
    E=M.copy()
    for _ in range(60): E=E-(E-e*np.sin(E)-M)/(1-e*np.cos(E))
    return E
def shape(tt,P,e,tp,w):
    M=np.mod(2*np.pi*(tt-tp)/P,2*np.pi); E=kep(M,e)
    nu=2*np.arctan2(math.sqrt(1+e)*np.sin(E/2),math.sqrt(1-e)*np.cos(E/2))
    return (1-e**2)/(1+e*np.cos(nu))*np.sin(nu+w)+e*np.sin(w)
def chi(P,e,tp,w):
    X=np.vstack([np.ones_like(T),T-T.mean(),shape(T,P,e,tp,w)]).T/S[:,None]
    c,res,rk,_=np.linalg.lstsq(X,O/S,rcond=None); r=O/S-X@c; return float(r@r)
cg=chi(Po,eo,Tp,om)
print(f"Gaia's own (P, e, T_peri, omega): chi2 = {cg:.2f}")
# control A: keep Gaia's P and e, scan the orbital PHASE (T_peri) and omega over their full ranges
tps=np.linspace(Tp,Tp+Po,720,endpoint=False); ws=np.linspace(0,2*np.pi,72,endpoint=False)
A=np.array([[chi(Po,eo,tp,w) for w in ws] for tp in tps]); best=A.min(axis=1)
frac=np.mean(best<=cg)
print(f"control A (random orbital phase, omega free): fraction of phases fitting as well as Gaia's: {frac:.3f}  (median chi2 {np.median(best):.1f})")
print(f"   best-fitting T_peri offset from Gaia: {((tps[np.argmin(best)]-Tp+Po/2)%Po-Po/2):+.0f} d  (of a {Po:.0f}-d cycle)")
# control B: random outer PERIOD 300-1500 d (e, phase, omega free) - how special is 597 d?
rng=np.random.default_rng(3); Ps=np.exp(rng.uniform(np.log(300),np.log(1500),400)); Bc=[]
for P in Ps:
    c=min(chi(P,e,tp,w) for e in (0.0,0.2,0.4,0.6) for tp in np.linspace(0,P,24,endpoint=False) for w in np.linspace(0,2*np.pi,12,endpoint=False))
    Bc.append(c)
Bc=np.array(Bc)
print(f"control B (random P_out, all shape params free): fraction fitting as well as Gaia's FIXED orbit: {np.mean(Bc<=cg):.3f}")
print("   NOTE: control B is generous to the null (4 free shape params vs 0) - a low fraction here is strong evidence.")
