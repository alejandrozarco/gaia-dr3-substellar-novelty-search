"""Strips of the stored coadd regions (each divided by its median) for ranked 'weird' spectra, with the nearest neighbour in grey."""
import sys, numpy as np, pandas as pd, matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
from scipy.ndimage import gaussian_filter1d
REG=[("3880",3880,4000),("4780",4780,4940),("4990",4990,5200),("5820",5820,5940),("6400",6400,6750),("7740",7740,7810),("8250",8250,8950)]
GRID=10**np.arange(np.log10(3850),np.log10(9250),6e-5)
w=pd.read_csv("weird.csv",dtype={"sdss_id":str,"nearest":str}); lo,hi=int(sys.argv[2]),int(sys.argv[3]); rows=w.iloc[lo:hi]
fig,ax=plt.subplots(len(rows),len(REG),figsize=(20,1.25*len(rows)),gridspec_kw=dict(width_ratios=[r[2]-r[1] for r in REG]))
def load(s):
    d=np.load(f"/tmp/hotdq/lane_gasdisc/store/{s[-2:]}/{s}.npz"); return d
for i,(_,r) in enumerate(rows.iterrows()):
    d=load(r.sdss_id); dn=load(r.nearest)
    for j,(k,a,b) in enumerate(REG):
        x=GRID[(GRID>a)&(GRID<b)]; ax_=ax[i,j]
        for dd,col,lw in ((dn,"0.6",0.6),(d,"k",0.7)):
            f,iv=dd[f"f_{k}"],dd[f"iv_{k}"]; ok=(iv>0)&np.isfinite(f)
            if ok.sum()>5: y=f/np.median(f[ok]); ax_.plot(x[ok],gaussian_filter1d(y[ok],1),color=col,lw=lw)
        ax_.set_yticks([]); ax_.tick_params(labelsize=5)
        if j==0: ax_.set_ylabel(f"#{lo+i} {r.sdss_id}\n{r.cls} U={r.uniqueness:.0f}",fontsize=6)
plt.tight_layout(); plt.savefig(sys.argv[1],dpi=55)
