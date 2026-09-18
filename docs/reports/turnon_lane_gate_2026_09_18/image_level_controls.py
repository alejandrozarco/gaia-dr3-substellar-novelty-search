import numpy as np, csv, math, subprocess, io
from astropy.io import fits
from astropy.wcs import WCS
RA,DEC=118.285310,0.593230
def load(fn):
    h=fits.open(fn)
    for hdu in h:
        if hdu.data is not None and hdu.data.ndim==2: return hdu.data.astype(float),WCS(hdu.header)
def apphot(data,w,ra,dec,r_ap,r_in,r_out):
    x,y=w.all_world2pix(ra,dec,0); x,y=float(x),float(y)
    scale=3600*np.sqrt(abs(np.linalg.det(w.pixel_scale_matrix)))
    ny,nx=data.shape
    if not (r_out/scale<x<nx-r_out/scale and r_out/scale<y<ny-r_out/scale): return None,None
    yy,xx=np.mgrid[0:ny,0:nx]; rr=np.sqrt((xx-x)**2+(yy-y)**2)*scale
    ap=rr<=r_ap; ann=(rr>=r_in)&(rr<=r_out); g=np.isfinite(data)
    if (ap&g).sum()<3 or (ann&g).sum()<20: return None,None
    bg=np.median(data[ann&g]); flux=np.sum(data[ap&g]-bg); n=(ap&g).sum()
    sd=np.std(data[ann&g]); nb=(ann&g).sum()
    return flux, sd*math.sqrt(n+n*n/nb)

o=subprocess.run(["curl","-sL","--max-time","120",
 "https://catalogs.mast.stsci.edu/api/v0.1/panstarrs/dr2/mean.csv?ra=118.285310&dec=0.593230&radius=0.022"
 "&nDetections.gte=10&columns=raMean,decMean,rMeanPSFMag"],capture_output=True,text=True).stdout
cat=[]
for r in csv.DictReader(io.StringIO(o)):
    try: rm=float(r['rMeanPSFMag']); ra=float(r['raMean']); dec=float(r['decMean'])
    except: continue
    s=3600*math.hypot((ra-RA)*math.cos(math.radians(DEC)),dec-DEC)
    cat.append((ra,dec,rm,s))
zp_refs=[c for c in cat if 17.5<=c[2]<=20.2 and c[3]>8]
ps1,wp=load('/tmp/ps1_r_big.fits'); ztf,wz=load('/tmp/ztf_ref_big.fits')
def zeropoint(data,w,rap,rin,rout):
    z=[]
    for ra,dec,rm,s in zp_refs:
        f,n=apphot(data,w,ra,dec,rap,rin,rout)
        if f and f>0: z.append(rm+2.5*math.log10(f))
    return float(np.median(z)),float(np.std(z))
zp_p,sd_p=zeropoint(ps1,wp,1.5,5.0,9.0); zp_z,sd_z=zeropoint(ztf,wz,3.0,7.0,13.0)

print("CONTROL: constant field sources measured identically in BOTH images")
print(f"{'PS1 cat r':>10} {'PS1 img':>9} {'ZTF img':>9} {'delta':>8}   (delta should be ~0)")
deltas=[]
# faint controls, matched to the target's brightness range
for ra,dec,rm,s in sorted(cat,key=lambda c:c[3]):
    if not (20.5<=rm<=22.5): continue
    if s<8: continue
    fp,np_=apphot(ps1,wp,ra,dec,1.5,5.0,9.0)
    fz,nz=apphot(ztf,wz,ra,dec,3.0,7.0,13.0)
    if not fp or not fz or fp<=0 or fz<=0: continue
    mp=zp_p-2.5*math.log10(fp); mz=zp_z-2.5*math.log10(fz)
    d=mp-mz; deltas.append(d)
    print(f"{rm:10.2f} {mp:9.2f} {mz:9.2f} {d:+8.2f}")
    if len(deltas)>=12: break
if deltas:
    print(f"\ncontrol delta: median={np.median(deltas):+.3f}  std={np.std(deltas):.3f}  n={len(deltas)}")
    print(f"TARGET  delta: +2.673 +- 0.500")
    z=(2.673-np.median(deltas))/np.std(deltas) if np.std(deltas)>0 else float('nan')
    print(f"  -> target is {z:.1f} sigma from the control distribution")
