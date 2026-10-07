# Conservative forecast: cycle-bootstrap errors on synthetic S90-noise-replay stacks of 1 and 5 x 20-s sectors.
# Target TIC 450781262, P=0.093889794 d, T0 BJD_TDB 2460684.83515
import numpy as np, json, sys
sys.path.insert(0,'rn')
from rednoise import load, model, files, fit
rng=np.random.default_rng(11)
NB=int(sys.argv[1]) if len(sys.argv)>1 else 150
t1,ph1,y1,c1=load(files['S90_20s'][0])
p,e,r=fit(ph1,y1,20.,7,[0.01,0,430,80,1.0,0.0]); o=np.argsort(t1); rs=r[o]
out={}
for tau_true in [70.,100.]:
    pt=p.copy(); pt[3]=tau_true; pt[2]=p[2]-2*p[3]+2*tau_true
    mt=model(pt,ph1,20.,7)
    for nsec in [1,5]:
        Ys=[];PH=[];CY=[]
        for j,s in enumerate(rng.integers(200,len(rs)-200,nsec)):
            yk=np.empty_like(y1); yk[o]=mt[o]+np.roll(rs,s); Ys.append(yk); PH.append(ph1); CY.append(c1+j*10**6)
        Y=np.concatenate(Ys); PHc=np.concatenate(PH); CYc=np.concatenate(CY)
        q0=fit(PHc,Y,20.,7,pt)[0]
        uc=np.unique(CYc); idx={c:np.where(CYc==c)[0] for c in uc}; bs=[]
        for i in range(NB):
            sel=np.concatenate([idx[c] for c in rng.choice(uc,len(uc))]); bs.append(fit(PHc[sel],Y[sel],20.,7,q0)[0])
        bs=np.array(bs); pc=lambda a:[float(x) for x in np.percentile(a,[16,50,84])]
        out[f'tau{int(tau_true)}_n{nsec}']=dict(fit_tau=float(q0[3]),tau=pc(bs[:,3]),T14=pc(bs[:,2]),tc=pc(bs[:,1]))
        print(f'tau{int(tau_true)}_n{nsec}',json.dumps(out[f'tau{int(tau_true)}_n{nsec}']),flush=True)
json.dump(out,open('rn/forecast_boot_results.json','w'),indent=1)
