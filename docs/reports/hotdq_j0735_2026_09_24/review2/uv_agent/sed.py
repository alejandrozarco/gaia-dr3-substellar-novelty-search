import numpy as np, sys
sys.path.insert(0,'.')
from load import *
from scipy.optimize import minimize_scalar, minimize
h=6.62607e-27; k=1.380649e-16; cl=2.99792458e10
def Blam(lamA,T):  # erg/s/cm2/A/sr
    l=lamA*1e-8; return 2*h*cl**2/l**5/(np.exp(h*cl/(l*k*T))-1)*1e-8
def ab2flam(m,lamA): fnu=10**(-0.4*(m+48.6)); return fnu*cl/(lamA*1e-8)**2*1e-8
# photometry (AB); lam = pivot/effective
P=[('GALEX FUV',1535,15.952,0.018,'uv'),('GALEX NUV',2301,15.637,0.010,'uv'),
   ('SM u',3493,15.811,0.03,'opt'),('SM v',3835,16.109,0.03,'opt'),('SM g',5075,16.476,0.02,'opt'),('SM r',6138,16.766,0.02,'opt'),('SM i',7767,17.156,0.03,'opt'),('SM z',9145,17.460,0.05,'opt'),
   ('XP u',3595,15.833,0.03,'xp'),('XP g',4640,16.360,0.01,'xp'),('XP r',6122,16.818,0.01,'xp'),('XP i',7440,17.123,0.02,'xp'),('XP z',8897,17.465,0.03,'xp'),
   ('VHS J(AB)',12520,17.225+0.937,0.06,'ir'),('VHS Ks(AB)',21470,17.420+1.839,0.33,'ir')]
plx=10.376e-3; d_pc=1/plx; d_cm=d_pc*3.0857e18
lam=np.array([p[1] for p in P]); fl=np.array([ab2flam(p[2],p[1]) for p in P]); efl=fl*np.array([p[3] for p in P])*0.921+0.03*fl
def fit(sel):
    best=None
    for T in np.arange(8000,80001,250):
        b=Blam(lam[sel],T); w=1/efl[sel]**2; th=np.sum(w*fl[sel]*b)/np.sum(w*b*b)
        chi=np.sum(w*(fl[sel]-th*b)**2)
        if best is None or chi<best[2]: best=(T,th,chi)
    return best
if __name__=="__main__":
    grp=np.array([p[4] for p in P])
    for nm,sel in [('XP ugriz',grp=='xp'),('SkyMapper uvgriz',grp=='opt'),('SM+XP+VHS',np.isin(grp,['opt','xp','ir'])),('SM griz only',np.isin([p[0] for p in P],['SM g','SM r','SM i','SM z'])),('XP griz',np.isin([p[0] for p in P],['XP g','XP r','XP i','XP z']))]:
        T,th,chi=fit(sel); R=np.sqrt(th/np.pi)*d_cm/6.957e10
        pred_uv=[(p[0],p[2], -2.5*np.log10(th*Blam(p[1],T)*(p[1]*1e-8)**2/cl*1e8)-48.6) for p in P if p[4]=='uv']
        print(f"{nm:18s}: T_bb={T:6.0f} K  R={R*109.1:.4f} R_earth ({R:.5f} Rsun) chi2={chi:.1f}/{sel.sum()-2}  predicted FUV {pred_uv[0][2]:.2f} (obs {pred_uv[0][1]:.2f}), NUV {pred_uv[1][2]:.2f} (obs {pred_uv[1][1]:.2f})")
    # blackbody FUV-NUV vs T
    for T in [10000,12000,13000,14000,15000,16000,18000,20000,24000,28000,35000]:
        m=[-2.5*np.log10(Blam(l,T)*(l*1e-8)**2/cl*1e8) for l in (1535,2301)]
        print(f"  BB T={T}: FUV-NUV={m[0]-m[1]:+.2f}")
    # all-in fit including UV
    T,th,chi=fit(np.ones(len(P),bool)); print("all incl UV:",T,chi)
