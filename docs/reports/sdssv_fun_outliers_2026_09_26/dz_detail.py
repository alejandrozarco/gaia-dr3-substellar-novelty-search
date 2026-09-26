import os
import sys, numpy as np, matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
sys.path.insert(0,os.path.expanduser("~/claude_projects/sdssv-white-dwarfs-2026/scripts")); import sdssv
from scipy.ndimage import gaussian_filter1d
ids=sys.argv[2:]; fig,ax=plt.subplots(len(ids),4,figsize=(18,3.2*len(ids)),gridspec_kw=dict(width_ratios=[3,1,1,1]),squeeze=False)
for i,sid in enumerate(ids):
    vs=sdssv.visits(sid); w,f,iv=sdssv.coadd([v for v in vs if v["in_stack"]] or vs)[:3]; ok=(iv>0)&np.isfinite(f)
    ax[i,0].plot(w[ok],gaussian_filter1d(f[ok],1.5),"k",lw=.6); ax[i,0].set_xlim(3700,9300); ax[i,0].set_title(f"{sid} ({len(vs)} visits)",fontsize=9)
    for j,(lo,hi,ls,nm) in enumerate(((5860,5930,[5891.6,5897.6],"Na D"),(6680,6740,[6709.6],"Li 6708"),(7640,7720,[7667.0,7701.1],"K 7665/7699"))):
        m=ok&(w>lo)&(w<hi); ax[i,j+1].plot(w[m],gaussian_filter1d(f[m]/np.median(f[m]),1),"k",lw=.8)
        for l in ls: ax[i,j+1].axvline(l,color="r",lw=.5)
        ax[i,j+1].set_title(nm,fontsize=8)
    for l in (3934.8,3969.6,5891.6,6709.6,7667.0,7701.1,8544.4,4227.9,5174): ax[i,0].axvline(l,color="r",lw=.3)
plt.tight_layout(); plt.savefig(sys.argv[1],dpi=70)
