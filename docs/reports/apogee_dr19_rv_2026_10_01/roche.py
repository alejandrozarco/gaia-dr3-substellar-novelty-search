import numpy as np
G=6.674e-11; Ms=1.989e30; Rs=6.957e8
def rl(q): q3=q**(1/3); return 0.49*q3**2/(0.6*q3**2+np.log(1+q3))
def solve(K,M1,R1):
    """min M2 (sin i=1) given K>=K, primary Roche-lobe limit on P. Returns (M2_min, P_roche_d)."""
    if not (np.isfinite(K) and np.isfinite(M1) and np.isfinite(R1)) or K<=0: return np.nan,np.nan
    lo,hi=1e-4,1e3
    def gfun(M2):
        a=R1*Rs/rl(M1/M2); P=2*np.pi*np.sqrt(a**3/(G*(M1+M2)*Ms)); f=P*(K*1e3)**3/(2*np.pi*G)/Ms
        return M2**3/(M1+M2)**2-f, P/86400
    for _ in range(80):
        m=np.sqrt(lo*hi)
        if gfun(m)[0]>0: hi=m
        else: lo=m
    return hi, gfun(hi)[1]
