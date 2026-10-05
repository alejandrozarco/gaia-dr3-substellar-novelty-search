import pandas as pd, numpy as np, matplotlib, sys, os; matplotlib.use('Agg'); import matplotlib.pyplot as plt
t=pd.read_csv('gates.csv'); t=t[t.survive].reset_index(drop=True)
def lc(n):
    d=pd.read_csv(f'../glc/{n}.csv',skiprows=1); d.columns=['date','jd','mag']; d['mag']=pd.to_numeric(d.mag,errors='coerce'); return d.dropna()
per=30
for k in range(0,len(t),per):
    s=t.iloc[k:k+per]; fig,ax=plt.subplots(6,5,figsize=(20,15)); ax=ax.ravel()
    for a,r in zip(ax,s.itertuples()):
        d=lc(r.Name); a.plot(d.jd-2450000,d.mag,'k.',ms=3)
        f=f'ztf/{r.Name}.csv'
        if os.path.exists(f):
            z=pd.read_csv(f); z=z[(z.catflags==0)]
            for b,c in (('zg','g'),('zr','r')):
                x=z[z.filtercode==b]; a.plot(x.mjd+0.5-50000,x.mag,'.',color=c,ms=1.5,alpha=0.5)
        a.invert_yaxis(); w=f' W12={r._49:.2f}' if False else ''
        a.set_title(f'{k+list(s.Name).index(r.Name)} {r.Name} G={r.Gmag:.1f} bprp={r.BPmag-r.RPmag:.1f} b={r.b:.0f} W12={r[t.columns.get_loc("W1-W2")+1]:.2f}',fontsize=8)
        a.tick_params(labelsize=6)
    for a in ax[len(s):]: a.axis('off')
    plt.tight_layout(); plt.savefig(f'grids/grid_{k//per}.png',dpi=55); plt.close()
print(len(t))
