import os
import sys, numpy as np, matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
sys.path.insert(0,os.path.expanduser("~/claude_projects/sdssv-white-dwarfs-2026/scripts")); import sdssv
from scipy.ndimage import gaussian_filter1d
ids=sys.argv[2:]; fig,ax=plt.subplots(len(ids),2,figsize=(16,3.6*len(ids)),gridspec_kw=dict(width_ratios=[3,1]))
for i,sid in enumerate(ids):
    vs=sdssv.visits(sid); w,f,iv=sdssv.coadd(vs)[:3]; ok=(iv>0)&np.isfinite(f)
    ax[i,0].plot(w[ok],gaussian_filter1d(f[ok],2),"k",lw=.6); ax[i,0].set_title(f"{sid} coadd of {len(vs)} visits",fontsize=9); ax[i,0].set_xlim(3700,9300)
    for l in (3934.8,3969.6,4102.9,4341.7,4862.7,5877.2,5891.6,6564.6,8500.4,8544.4,8664.5,7774.2): ax[i,0].axvline(l,color="r",lw=.3)
    for k,v in enumerate(vs):
        m=(v["wave"]>6450)&(v["wave"]<6680)&(v["ivar"]>0)
        if m.sum()>20: y=v["flux"][m]/np.median(v["flux"][m]); ax[i,1].plot(v["wave"][m],gaussian_filter1d(y,1.5)+0.5*k,lw=.7,label=str(v["mjd"]))
    ax[i,1].axvline(6564.6,color="r",lw=.4); ax[i,1].legend(fontsize=6)
plt.tight_layout(); plt.savefig(sys.argv[1],dpi=70)
