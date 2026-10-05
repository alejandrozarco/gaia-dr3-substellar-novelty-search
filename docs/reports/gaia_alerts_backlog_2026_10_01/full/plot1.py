import pandas as pd, numpy as np, matplotlib, sys; matplotlib.use('Agg'); import matplotlib.pyplot as plt
from lcio import *
t=pd.read_csv('gates.csv').set_index('Name')
def plot(n,out,title_extra=''):
    r=t.loc[n]; fig,(a1,a2)=plt.subplots(2,1,figsize=(9,6),sharex=True,gridspec_kw=dict(height_ratios=[3,2]))
    g=gaia(n); a1.plot(g.mjd,g.mag,'ko',ms=3,label='Gaia G (alert LC)')
    z=ztf(n,r.RAdeg,r.DEdeg)
    if z is not None:
        for b,c in (('zg','tab:green'),('zr','tab:red'),('zi','tab:brown')):
            x=z[z.filtercode==b]
            if len(x): a1.errorbar(x.mjd,x.mag,x.magerr,fmt='.',color=c,ms=2,elinewidth=0.4,alpha=0.6,label=f'ZTF {b[1]}')
    a1.invert_yaxis(); a1.set_ylabel('mag'); a1.legend(fontsize=7)
    a=atlas(n)
    if a is not None:
        for f,c in (('o','orange'),('c','tab:cyan')):
            x=a[a.F==f]; a2.errorbar(x.MJD,x.uJy,x.duJy,fmt='.',color=c,ms=2,elinewidth=0.4,alpha=0.7,label=f'ATLAS {f} (nightly, diff flux)')
        a2.legend(fontsize=7); a2.axhline(0,color='k',lw=0.5)
    a2.set_ylabel('uJy'); a2.set_xlabel('MJD')
    a1.set_title(f'{n}  Gaia DR3 {r.Source}  G={r.Gmag:.2f} BP-RP={r.BPmag-r.RPmag:.2f}  l={r.l:.1f} b={r.b:.1f}  W1-W2={r["W1-W2"]:.2f} {title_extra}',fontsize=8)
    plt.tight_layout(); plt.savefig(out,dpi=70); plt.close()
if __name__=='__main__':
    for n in sys.argv[1:]: plot(n,f'lc/{n}.png')
