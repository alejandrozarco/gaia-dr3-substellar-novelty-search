import numpy as np, pickle, sys, matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
from astropy.table import Table
T=Table.read(sys.argv[1]); title=sys.argv[2]; outpng=sys.argv[3]
nbf=sys.argv[1].replace('.ecsv','_nbsed.pkl')
def binspec(w,f,e,Rb):
    lo=0.74; edges=[lo]
    while edges[-1]<5.05: edges.append(edges[-1]*(1+1/Rb(edges[-1])))
    edges=np.array(edges); out=[]
    for a,b in zip(edges[:-1],edges[1:]):
        m=(w>=a)&(w<b)
        if m.sum()==0: continue
        ww=1/e[m]**2; fm=np.sum(f[m]*ww)/ww.sum(); em=1/np.sqrt(ww.sum())
        if m.sum()>=3:  # empirical scatter
            em=max(em,1.2533*1.4826*np.median(np.abs(f[m]-np.median(f[m])))/np.sqrt(m.sum()))
        out.append((np.mean(w[m]),fm,em,m.sum()))
    return np.array(out)
Rb=lambda l: 40 if l<3.82 else 110
G=(T['qc']==1)&(T['clip']==0)
fig,ax=plt.subplots(2,1,figsize=(11,10))
cols=['tab:blue','tab:green','tab:red']; labs=['2025-04/05 (MJD 60794-60849)','2025-10 (MJD 60958-60982)','2026-05/06 (MJD 61175-61215)']
B={}
for e in range(3):
    m=G&(T['epoch']==e)
    if m.sum()==0: continue
    ax[0].errorbar(T['wave'][m],T['flux'][m],T['eflux_tot'][m],fmt='.',color=cols[e],alpha=0.25,ms=3)
    b=binspec(np.array(T['wave'][m]),np.array(T['flux'][m]),np.array(T['eflux_tot'][m]),Rb); B[e]=b
    ax[0].errorbar(b[:,0],b[:,1],b[:,2],fmt='o-',color=cols[e],ms=4,label=labs[e]+f' (n={m.sum()})')
ax[0].set_ylabel('flux density (uJy)'); ax[0].set_title(title); ax[0].legend(fontsize=8); ax[0].set_ylim(bottom=-200)
for l in [1.4,1.9,2.29,3.05,4.27,4.67,4.05]: ax[0].axvline(l,color='gray',lw=0.5,ls=':')
try:
    nb=pickle.load(open(nbf,'rb'))
    ax[1].errorbar(nb['bc'],nb['bm'],nb['be'],fmt='o',color='k',label='6.1" neighbour: SPHEREx stage-1 binned medians (all epochs)')
    ax[1].plot([2.16,3.55,4.49],[461,272.6,198.1],'r*',ms=14,label='neighbour prior: UGPS K (2006), IRAC 3.6/4.5 (SEIP)')
    ax[1].legend(fontsize=8); ax[1].set_ylabel('uJy')
except Exception as ex: print(ex)
ax[1].set_xlabel('wavelength (um)')
plt.tight_layout(); plt.savefig(outpng,dpi=80)
pickle.dump(B,open(sys.argv[1].replace('.ecsv','_binned.pkl'),'wb'))
for e,b in B.items():
    print('epoch',e)
    for row in b: print('  %.3f %7.0f %5.0f %2d'%tuple(row))
