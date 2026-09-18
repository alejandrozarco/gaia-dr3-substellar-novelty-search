import numpy as np, csv, math, subprocess, io
from astropy.io import fits
from astropy.wcs import WCS
RA,DEC=118.285310,0.593230

def load(fn):
    h=fits.open(fn)
    for hdu in h:
        if hdu.data is not None and hdu.data.ndim==2: return hdu.data.astype(float),WCS(hdu.header)
    raise SystemExit(fn)

def apphot(data,w,ra,dec,r_ap,r_in,r_out):
    x,y=w.all_world2pix(ra,dec,0); x,y=float(x),float(y)
    scale=3600*np.sqrt(abs(np.linalg.det(w.pixel_scale_matrix)))
    ny,nx=data.shape
    if not (r_out/scale < x < nx-r_out/scale and r_out/scale < y < ny-r_out/scale): return None,None,scale
    yy,xx=np.mgrid[0:ny,0:nx]; rr=np.sqrt((xx-x)**2+(yy-y)**2)*scale
    ap=rr<=r_ap; ann=(rr>=r_in)&(rr<=r_out); g=np.isfinite(data)
    if (ap&g).sum()<3 or (ann&g).sum()<20: return None,None,scale
    bg=np.median(data[ann&g])
    flux=np.sum(data[ap&g]-bg); n=(ap&g).sum()
    # noise: per-pixel scatter in annulus, scaled by sqrt(n), plus background-mean uncertainty
    sd=np.std(data[ann&g]); nb=(ann&g).sum()
    noise=sd*math.sqrt(n + n*n/nb)
    return flux,noise,scale

o=subprocess.run(["curl","-sL","--max-time","120",
 "https://catalogs.mast.stsci.edu/api/v0.1/panstarrs/dr2/mean.csv?ra=118.285310&dec=0.593230&radius=0.022"
 "&nDetections.gte=10&columns=raMean,decMean,rMeanPSFMag"],capture_output=True,text=True).stdout
refs=[]
for r in csv.DictReader(io.StringIO(o)):
    try: rm=float(r['rMeanPSFMag']); ra=float(r['raMean']); dec=float(r['decMean'])
    except: continue
    if not (17.5<=rm<=20.2): continue
    s=3600*math.hypot((ra-RA)*math.cos(math.radians(DEC)),dec-DEC)
    if s<8: continue
    refs.append((ra,dec,rm,s))
refs.sort(key=lambda t:t[3])
print(f"reference stars: {len(refs)} (PS1 r 17.5-20.2, >8\" from target)\n")

out={}
for label,fn,rap,rin,rout in (("PS1 r stack  (2010-2014 PRE )","/tmp/ps1_r_big.fits",1.5,5.0,9.0),
                              ("ZTF ref zr   (2018      POST)","/tmp/ztf_ref_big.fits",3.0,7.0,13.0)):
    data,w=load(fn)
    tf,tn,scale=apphot(data,w,RA,DEC,rap,rin,rout)
    zps=[]
    for ra,dec,rm,s in refs:
        f,n,_=apphot(data,w,ra,dec,rap,rin,rout)
        if f and f>0: zps.append(rm+2.5*math.log10(f))
    zp=float(np.median(zps)); sd=float(np.std(zps))
    tmag=zp-2.5*math.log10(tf) if (tf and tf>0) else None
    err=1.0857*tn/tf if (tf and tf>0) else None
    print(f"=== {label} ===   aperture r={rap}\"  pixscale={scale:.2f}\"")
    print(f"  target flux = {tf:9.1f} +- {tn:7.1f}   ({tf/tn:5.1f} sigma)")
    print(f"  zeropoint   = {zp:.3f} +- {sd:.3f}  (n={len(zps)} stars)")
    print(f"  TARGET MAG  = {tmag:.3f} +- {math.sqrt(err**2+sd**2):.3f}\n" if tmag else "  not detected\n")
    out[label]=(tmag,math.sqrt(err**2+sd**2) if tmag else None,tf/tn)

ks=list(out)
if all(out[k][0] for k in ks):
    m1,e1,s1=out[ks[0]]; m2,e2,s2=out[ks[1]]
    d=m1-m2; de=math.sqrt(e1**2+e2**2)
    print("="*64)
    print("IMAGE-LEVEL DIFFERENTIAL MEASUREMENT (same reference stars, both images)")
    print(f"  PRE  (PS1 stack 2010-2014): r = {m1:.3f} +- {e1:.3f}   ({s1:.1f} sigma detection)")
    print(f"  POST (ZTF ref    2018)    : r = {m2:.3f} +- {e2:.3f}   ({s2:.1f} sigma detection)")
    print(f"  BRIGHTENING = {d:+.3f} +- {de:.3f} mag   ({d/de:.1f} sigma)")
    print(f"\n  catalogue comparison: PS1 r = 21.84 +- 0.18 ; ZTF zr = 20.13")
    print(f"  catalogue brightening = {21.84-20.13:+.2f} mag")
