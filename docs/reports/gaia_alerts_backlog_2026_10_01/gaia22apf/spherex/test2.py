import numpy as np, glob, sxphot as S, matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
from astropy.table import Table
from astropy.coordinates import SkyCoord
from astropy.wcs import WCS
t=Table.read('scene_sources.ecsv')
c0=SkyCoord(305.66064,39.19732,unit='deg'); r=SkyCoord(t['ra'],t['dec'],unit='deg').separation(c0).arcsec
sel=(r<1)|((t['K']<15.0)&(r<60))|((t['K']<16.0)&(r<15))
src=t[sel]
fs=sorted(glob.glob('cut/*.npz'))
dets=[S.load(f)['hdr']['DETECTOR'] for f in fs]
picks=[fs[[i for i,d in enumerate(dets) if d==k][0]] for k in [1,2,3,4,5,6]]
fig,ax=plt.subplots(6,4,figsize=(13,19))
for row,fn in enumerate(picks):
    fr=S.load(fn); o=S.fit_frame(fr,src)
    om=1
    w=WCS(fr['hdr']); xs,ys=w.all_world2pix(t['ra'],t['dec'],0); xs-=fr['x0']; ys-=fr['y0']
    xt,yt=o['xt']-fr['x0'],o['yt']-fr['y0']
    data=(fr['im']-fr['zo']); res=o['resid']
    sl=(slice(int(yt)-9,int(yt)+10),slice(int(xt)-9,int(xt)+10))
    ext=[sl[1].start-0.5,sl[1].stop-0.5,sl[0].start-0.5,sl[0].stop-0.5]
    v=np.nanpercentile(data[sl],[5,99.5])
    ax[row,0].imshow(data[sl],origin='lower',vmin=v[0],vmax=v[1],extent=ext); ax[row,0].set_title(f"D{o['det']} {o['wave']:.2f}um chi2r {o['chi2r']:.1f}")
    ax[row,1].imshow(np.arcsinh(data[sl]/np.nanstd(data[sl])*5),origin='lower',extent=ext)
    rr=res[sl]; s=np.nanpercentile(np.abs(rr[rr!=0]),95) if (rr!=0).any() else 1
    ax[row,2].imshow(rr,origin='lower',vmin=-s,vmax=s,cmap='RdBu',extent=ext); ax[row,2].set_title('resid uJy')
    for a in ax[row,:3]:
        a.plot(xs,ys,'r+',ms=5); a.plot(xt,yt,'wx',ms=8); a.set_xlim(ext[:2]); a.set_ylim(ext[2:])
        m=(np.asarray(src['name'])); 
    ax[row,3].imshow((fr['fl'][sl]&S.MASK)>0,origin='lower',extent=ext); ax[row,3].set_title('masked')
plt.tight_layout(); plt.savefig('diag_resid.png',dpi=70)
