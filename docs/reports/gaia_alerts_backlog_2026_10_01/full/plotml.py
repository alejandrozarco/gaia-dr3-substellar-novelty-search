import pandas as pd, numpy as np, matplotlib, sys; matplotlib.use('Agg'); import matplotlib.pyplot as plt
from mlfit import fit, A, t
C={'G':'k','zg':'tab:green','zr':'tab:red'}
def plot(n,out):
    o,d,mod,p,bands=fit(n); r=t.loc[n]
    fig,(a1,a2)=plt.subplots(1,2,figsize=(12,4.2),gridspec_kw=dict(width_ratios=[1.3,1]))
    for a in (a1,a2):
        for i,b in enumerate(bands):
            k=d.band==b; a.plot(d.t[k],d.m[k],'o' if b=='G' else '.',color=C[b],ms=3 if b=='G' else 2.5,alpha=0.8 if b=='G' else 0.5,label={'G':'Gaia G','zg':'ZTF g','zr':'ZTF r'}[b])
            tt=np.linspace(d.t.min(),d.t.max(),4000) if a is a1 else np.linspace(o['t0']-4*o['tE'],o['t0']+4*o['tE'],2000)
            m0,fs=p[3+2*i],p[4+2*i]; a.plot(tt,m0-2.5*np.log10(fs*A(tt,o['t0'],o['tE'],o['u0'])+1-fs),'-',color=C[b],lw=0.8)
        a.invert_yaxis(); a.set_xlabel('MJD'); a.set_ylabel('mag')
    a2.set_xlim(o['t0']-4*o['tE'],o['t0']+4*o['tE']); a1.legend(fontsize=7)
    fig.suptitle(f"{n}  Gaia DR3 {r.Source}  l={r.l:.1f} b={r.b:.1f}  PSPL: t0={o['t0']} tE={o['tE']} d u0={o['u0']} chi2r={o['chi2r']}",fontsize=9)
    plt.tight_layout(); plt.savefig(out,dpi=80); plt.close(); return o
if __name__=='__main__':
    for n in sys.argv[1:]: plot(n,f'lc/{n}_ml.png')
