import pandas as pd, numpy as np, matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
from lcio import *
t=pd.read_csv('gates.csv'); t=t[t.survive].reset_index(drop=True); F=pd.read_csv('feat_gaia.csv').set_index('Name')
per=12
for k in range(0,len(t),per):
    s=t.iloc[k:k+per]; fig,ax=plt.subplots(4,3,figsize=(18,13)); ax=ax.ravel()
    for i,(a,r) in enumerate(zip(ax,s.itertuples())):
        g=gaia(r.Name); a.plot(g.mjd,g.mag,'ko',ms=2.5,zorder=5)
        z=ztf(r.Name,r.RAdeg,r.DEdeg)
        if z is not None:
            for b,c in (('zg','tab:green'),('zr','tab:red')):
                x=z[z.filtercode==b]; a.plot(x.mjd,x.mag,'.',color=c,ms=2,alpha=0.5)
        a.invert_yaxis(); a.tick_params(labelsize=7)
        f=F.loc[r.Name]
        a.set_title(f'{k+i} {r.Name} G={r.Gmag:.1f} BR={r.BPmag-r.RPmag:.1f} b={r.b:.1f} W12={r._asdict().get("_70",np.nan) if False else r[t.columns.get_loc("W1-W2")+1]:.2f} tE={f.ml_tE} u0={f.ml_u0} rms={f.ml_rms}/{f.sig}',fontsize=8)
    for a in ax[len(s):]: a.axis('off')
    plt.tight_layout(); plt.savefig(f'grids/g2_{k//per:02d}.png',dpi=60); plt.close()
