import numpy as np, warnings; warnings.filterwarnings('ignore')
from astropy.timeseries import LombScargle
from scipy.optimize import least_squares
res={}
for s in [64,99,100,101]:
    t,y,tc=np.load(f'ap_s{s}.npy'); T=t.max()-t.min()
    c1=np.polyfit(t,tc,1)[0]  # d/d
    row=[]
    for f0 in [203.41,206.76,228.57,225.22]:
        fr=np.arange(f0-0.06,f0+0.06,0.0001); p=LombScargle(t,y).power(fr); f=fr[p.argmax()]
        # nonlinear LSQ for f with 2-freq model in the same frame side
        def mod(par,tt): return par[1]*np.sin(2*np.pi*par[0]*tt+par[2])
        tm=t-t.mean()
        r=least_squares(lambda par: y-np.mean(y)-mod(par,tm),[f,0.45,0.0])
        J=r.jac; cov=np.linalg.inv(J.T@J)*np.sum(r.fun**2)/(len(y)-3); ef=np.sqrt(cov[0,0])
        row.append((r.x[0],ef,abs(r.x[1])))
    res[s]=(row,c1)
    print(f'S{s} T={T:.1f}d dTIMECORR/dt={c1*86400:.2f} s/d  '+'  '.join(f'{f:.4f}+-{e:.4f}(A{a:.2f})' for f,e,a in row)+f'   sum203+228={row[0][0]+row[2][0]:.4f} pred 432(1-c1)={432*(1-c1):.4f}')
names=['203.4(sub)','206.76(sub)','228.57(super)','225.22(super)']
for i,n in enumerate(names):
    f=np.array([res[s][0][i][0] for s in res]); e=np.array([res[s][0][i][1] for s in res]); w=1/e**2; m=(f*w).sum()/w.sum(); chi=((f-m)**2*w).sum()
    print(f'{n}: weighted mean {m:.4f}; chi2 for constant frequency over S64,S99,S100,S101 = {chi:.1f} (dof 3); range {f.max()-f.min():.4f}')
