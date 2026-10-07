# Joint S90(20s)+S99(2min) fit (shared tc,T14,tau; separate depth/baseline) with cycle bootstrap,
# and noise-replay forecast for 1 and 5 (S90 + 4 new) 20-s sectors.
# Target TIC 450781262 (WDJ111803.09-544218.04), P=0.093889794 d, T0 BJD_TDB 2460684.83515
import numpy as np, json, sys
sys.path.insert(0,'rn')
from rednoise import load, model, files, fit
from scipy.optimize import least_squares
rng=np.random.default_rng(7)
NB=int(sys.argv[1]) if len(sys.argv)>1 else 300
t1,ph1,y1,c1=load(files['S90_20s'][0]); t2,ph2,y2,c2=load(files['S99_2min'][0])
def jm(p,ph1,ph2):
    tc,T14,tau,d1,b1,q1,d2,b2,q2=p
    return np.concatenate([model([d1,tc,T14,tau,b1,q1],ph1,20.,7),model([d2,tc,T14,tau,b2,q2],ph2,120.,15)])
LB=[-200,100,0.5,0,0.9,-0.1,0,0.9,-0.1]; UB=[200,1200,500,0.06,1.1,0.1,0.06,1.1,0.1]
def jfit(ph1,y1,ph2,y2,p0):
    # weight each set by its own rms
    s1,s2=np.std(y1[np.abs(ph1)>400]),np.std(y2[np.abs(ph2)>400])
    w=np.concatenate([np.full(len(y1),1/s1),np.full(len(y2),1/s2)])
    r=least_squares(lambda p:(jm(p,ph1,ph2)-np.concatenate([y1,y2]))*w,p0,bounds=(LB,UB),x_scale=[5,20,20,1e-3,1e-3,1e-3,1e-3,1e-3,1e-3])
    return r.x
p0=[0,400,80,0.009,1,0,0.018,1,0]
pj=jfit(ph1,y1,ph2,y2,p0)
u1,u2=np.unique(c1),np.unique(c2); i1={c:np.where(c1==c)[0] for c in u1}; i2={c:np.where(c2==c)[0] for c in u2}
bs=[]
for k in range(NB):
    s1=np.concatenate([i1[c] for c in rng.choice(u1,len(u1))]); s2=np.concatenate([i2[c] for c in rng.choice(u2,len(u2))])
    bs.append(jfit(ph1[s1],y1[s1],ph2[s2],y2[s2],pj))
bs=np.array(bs)
pc=lambda a:[float(x) for x in np.percentile(a,[16,50,84])]
res={'joint_best':dict(tc=pj[0],T14=pj[1],tau=pj[2]),'joint_boot':dict(tc=pc(bs[:,0]),T14=pc(bs[:,1]),tau=pc(bs[:,2]))}
print(json.dumps(res),flush=True)
# noise replay: S90 20-s best model + time-ordered residuals shifted cyclically
p,e,r=fit(ph1,y1,20.,7,[0.01,0,430,80,1.0,0.0])
o=np.argsort(t1); rs=r[o]
for tau_true in [70.,100.]:
    ptrue=p.copy(); ptrue[3]=tau_true
    # keep T23 = T14-2tau fixed at the fitted value so the eclipse core is unchanged
    ptrue[2]=p[2]-2*p[3]+2*tau_true
    mtrue=model(ptrue,ph1,20.,7)
    for nsec in [1,5]:
        taus=[];T14s=[];tcs=[]
        for k in range(NB//2):
            shifts=rng.integers(200,len(rs)-200,nsec)
            Y=np.concatenate([ (lambda yk:(yk.__setitem__(o,mtrue[o]+np.roll(rs,s)) or yk))(np.empty_like(y1)) for s in shifts])
            PH=np.tile(ph1,nsec)
            q=fit(PH,Y,20.,7,ptrue)[0]; taus.append(q[3]); T14s.append(q[2]); tcs.append(q[1])
        res[f'replay_tau{int(tau_true)}_n{nsec}']=dict(tau=pc(taus),T14=pc(T14s),tc=pc(tcs),tau_std=float(np.std(taus)),T14_std=float(np.std(T14s)),tc_std=float(np.std(tcs)))
        print(f'tau_true {tau_true} nsec {nsec}',json.dumps(res[f'replay_tau{int(tau_true)}_n{nsec}']),flush=True)
json.dump(res,open('rn/forecast_results.json','w'),indent=1,default=float)
