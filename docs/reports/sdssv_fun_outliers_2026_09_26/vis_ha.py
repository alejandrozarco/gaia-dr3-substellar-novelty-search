"""Per-visit H-alpha region (stored, 6400-6750 A) for a list of sdss_ids: one panel per star, visits offset."""
import sys, numpy as np, matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
from scipy.ndimage import gaussian_filter1d
GRID=10**np.arange(np.log10(3850),np.log10(9250),6e-5); W=GRID[(GRID>6400)&(GRID<6750)]
ids=sys.argv[2:]; n=len(ids); fig,ax=plt.subplots((n+3)//4,4,figsize=(16,3.2*((n+3)//4)))
for a,sid in zip(ax.flat,ids):
    d=np.load(f"/tmp/hotdq/lane_gasdisc/store/{sid[-2:]}/{sid}.npz")
    for j in range(d["vf_6400"].shape[0]):
        f,iv=d["vf_6400"][j],d["viv_6400"][j]; ok=(iv>0)&np.isfinite(f)
        if ok.sum()<50: continue
        y=f/np.median(f[ok]); a.plot(W[ok],gaussian_filter1d(y[ok],1.5)+0.6*j,lw=.7); a.text(6405,1.2+0.6*j,f"{int(d['mjd'][j])} S/N {d['vsnr'][j]:.0f}",fontsize=6)
    for l in (6564.6,6680.0): a.axvline(l,color="r",lw=.4)
    a.set_title(sid,fontsize=8)
plt.tight_layout(); plt.savefig(sys.argv[1],dpi=65)
