import numpy as np
def load(fn):
    a=np.genfromtxt(fn,delimiter=',',skip_header=2)
    return a
def idx(lam,f):
    b=(lam>=4285)&(lam<=4316); c=((lam>=4235)&(lam<=4262))|((lam>=4322)&(lam<=4332))
    return 1-f[b].mean()/np.median(f[c]), b.sum(), c.sum()
def boot(lam,f,n=3000,seed=2):
    rng=np.random.default_rng(seed)
    b=(lam>=4285)&(lam<=4316); c=((lam>=4235)&(lam<=4262))|((lam>=4322)&(lam<=4332))
    return np.std([1-rng.choice(f[b],b.sum()).mean()/np.median(rng.choice(f[c],c.sum())) for _ in range(n)])
k=load('mwdd_J1407_Kilic.txt'); lam,fnu=k[:,0],k[:,1]
print('Kilic step',np.median(np.diff(lam)))
flam=fnu/lam**2
for nm,f in [('fnu',fnu),('flam',flam)]:
    for sh in [0,1.2]:
        print('Kilic',nm,'shift',sh,idx(lam+sh,f),'boot sd %.3f'%boot(lam+sh,f))
# local S/N
c=((lam>=4235)&(lam<=4262))|((lam>=4322)&(lam<=4332)); print('Kilic continuum S/N per px ~',np.median(fnu[c])/np.std(fnu[c]))
d=load('mwdd_J1407_DESI_2022-06-08_040013.txt'); lam2,f2,s2=d[:,0],d[:,1],d[:,2]
g=d[:,3]==1 if d.shape[1]>3 else np.ones(len(d),bool)
print('DESI flags unique',np.unique(d[:,3]))
print('DESI',idx(lam2,f2),'boot sd %.3f'%boot(lam2,f2))
x=load('mwdd_J1407_XP.txt'); print('XP near 4300',x[(x[:,0]>4150)&(x[:,0]<4450)])
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
fig,ax=plt.subplots(2,1,figsize=(9,6))
for a,(L,F,t) in zip(ax,[(lam,fnu,'Kilic+2025 MMT/BCS via MWDD (f_nu)'),(lam2,f2,'DESI DR1 via MWDD (f_lam)')]):
    m=(L>4100)&(L<4500); a.step(L[m],F[m],where='mid',lw=.7)
    a.axvspan(4285,4316,color='r',alpha=.2); a.axvspan(4235,4262,color='g',alpha=.2); a.axvspan(4322,4332,color='g',alpha=.2); a.set_title(t)
plt.tight_layout(); plt.savefig('mwdd_J1407_Gband_Kilic_DESI.png',dpi=110)
