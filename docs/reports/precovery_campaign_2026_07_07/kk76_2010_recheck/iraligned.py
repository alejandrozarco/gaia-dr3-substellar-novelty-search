import warnings,sys,math,pickle; warnings.filterwarnings("ignore"); sys.path.insert(0,"/tmp")
import numpy as np
cats,tm,pv,_=pickle.load(open("irmove.pkl","rb"))
de0=-22.873; cd=math.cos(math.radians(de0))
def nnoff(a,b,snr=40):
    A=a[a[:,2]>snr]; out=[]
    for r in A:
        dx=(b[:,0]-r[0])*cd*3600; dy=(b[:,1]-r[1])*3600; j=np.argmin(np.hypot(dx,dy))
        if np.hypot(dx[j],dy[j])<0.6: out.append((dx[j],dy[j]))
    o=np.array(out); return np.median(o,axis=0), np.median(np.abs(o-np.median(o,axis=0)),axis=0)*1.4826, len(o)
al=[cats[0]]
for k in (1,2,3):
    off,sc,n=nnoff(cats[0],cats[k])
    print(f"IR frame {k} vs frame 0: star offset ({off[0]:+.3f},{off[1]:+.3f})in  scatter ({sc[0]:.3f},{sc[1]:.3f})  from {n} stars")
    c=cats[k].copy(); c[:,0]-=off[0]/3600/cd; c[:,1]-=off[1]/3600; al.append(c)
print("predicted KK76 displacement (incl. HST parallax):",[f"({a:+.3f},{b:+.3f})" for a,b in pv])
def at(c,ra,de,tol):
    d=np.hypot((c[:,0]-ra)*cd*3600,(c[:,1]-de)*3600); j=np.argmin(d); return (j,d[j]) if d[j]<tol else (None,d[j])
movers=[]
for ra,de,s in al[0]:
    trk=[]; stat=0; ok=True
    for k in (1,2,3):
        j,dd=at(al[k],ra+pv[k][0]/3600/cd,de+pv[k][1]/3600,0.05)
        js,ds=at(al[k],ra,de,0.03)
        if j is None: ok=False; break
        if js is not None and ds<dd: stat+=1
        trk.append(dd)
    if ok and stat==0 and math.hypot(*pv[3])>0.1: movers.append((ra,de,s,trk))
print(f"\nstar-aligned IR sources following KK76's predicted track (0.05in tolerance) and NOT static: {len(movers)}")
for m in movers[:10]: print(f"   RA {m[0]:.6f} Dec {m[1]:+.6f}  S/N {m[2]:.0f}  track residuals {['%.3f'%x for x in m[3]]}in")
# honest sensitivity: how many STATIC stars would pass the same test by chance? (null check)
print(f"(null check: {sum(1 for r in al[0] if at(al[3],r[0],r[1],0.03)[0] is not None)} of {len(al[0])} frame-0 sources are static to 0.03in in frame 3)")
