import warnings,math; warnings.filterwarnings("ignore")
import numpy as np, runpy
ns=runpy.run_path("appear.py",run_name="notmain") if False else None
exec(open("appear.py").read().split("dis=E1")[0])        # reuse catalogues E1/E2 and helpers
def nn(a,b):
    out=[]
    for r in a:
        dx=(b[:,0]-r[0])*cd*3600; dy=(b[:,1]-r[1])*3600; j=np.argmin(np.hypot(dx,dy)); out.append((dx[j],dy[j],r[2],b[j][2]))
    return np.array(out)
v=nn(E1,E2)
bright=v[(v[:,2]>40)&(v[:,3]>40)]
print(f"epoch1->epoch2 nearest-neighbour offsets for {len(bright)} bright two-filter stars (S/N>40 both):")
for r in bright[:12]: print(f"   ({r[0]:+.3f},{r[1]:+.3f})in")
med=np.median(bright[:,:2],axis=0); mad=np.median(np.abs(bright[:,:2]-med),axis=0)*1.4826
print(f"\nMEDIAN systematic offset epoch1->epoch2: ({med[0]:+.3f}, {med[1]:+.3f}) arcsec   robust scatter ({mad[0]:.3f},{mad[1]:.3f})")
print(f"compare predicted KK76 motion over the same hour:  (+0.872, -0.011) arcsec")
# apply offset: which epoch-1 sources have NO epoch-2 counterpart after correction, and vice versa?
E2c=E2.copy(); E2c[:,0]-=med[0]/3600/cd; E2c[:,1]-=med[1]/3600
dis=E1[~match(E1,E2c,0.10)]; app=E2c[~match(E2c,E1,0.10)]
print(f"\nAFTER removing the offset: disappearing {len(dis)}, appearing {len(app)}")
for r in dis: print(f"   gone    RA {r[0]:.6f} Dec {r[1]:+.6f} S/N {r[2]:.0f}")
for r in app: print(f"   new     RA {r[0]+med[0]/3600/cd:.6f} Dec {r[1]+med[1]/3600:+.6f} S/N {r[2]:.0f}  (epoch-2 frame coords)")
