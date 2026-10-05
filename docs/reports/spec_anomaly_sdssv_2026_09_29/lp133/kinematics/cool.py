import numpy as np
def load(f):
    L=open(f).read().splitlines()
    rows=[l.split() for l in L[2:63] if l.strip() and l.split()[0][0].isdigit()]
    a=np.array([[float(x) for x in r] for r in rows]); return a
A={m:load(f'Table_Mass_{m}') for m in ['1.2','1.3']}
for m,a in A.items():
    s=(a[:,0]>=5500)&(a[:,0]<=8000); print(m,[(t,round(g,3),round(ag/1e9,3),mg) for t,g,ag,mg in zip(a[s,0],a[s,1],a[s,-1],a[s,37])])
def age_at(a,T): return 10**np.interp(np.log10(T),np.log10(a[:,0][::-1]),np.log10(a[:,-1][::-1]))
def lg_at(a,T): return np.interp(np.log10(T),np.log10(a[:,0][::-1]),a[:,1][::-1])
def mg_at(a,T): return np.interp(np.log10(T),np.log10(a[:,0][::-1]),a[:,37][::-1])
rng=np.random.default_rng(3); n=20000
T=rng.normal(6718,63,n); M=rng.normal(1.256,0.006,n)
a12=age_at(A['1.2'],T); a13=age_at(A['1.3'],T)
w=(M-1.2)/0.1; age=10**((1-w)*np.log10(a12)+w*np.log10(a13))/1e9
print('cooling age (Montreal thick-H, Bedard+2020 CO-core) Gyr: %.3f [%.3f,%.3f]'%tuple(np.percentile(age,[50,16,84])))
print('logg check at 6718K: 1.2->%.3f 1.3->%.3f'%(lg_at(A['1.2'],6718),lg_at(A['1.3'],6718)))
print('M_G(G3) model at 6718: 1.2->%.2f 1.3->%.2f'%(mg_at(A['1.2'],6718),mg_at(A['1.3'],6718)))
