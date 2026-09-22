import warnings; warnings.filterwarnings("ignore")
import numpy as np, json, subprocess, urllib.parse, lightkurve as lk
from astropy.coordinates import SkyCoord
from astropy.timeseries import LombScargle
RA,DEC=223.46949,49.94663; P=0.33880
q=(f"SELECT source_id,ra,dec,phot_g_mean_mag,DISTANCE(POINT('ICRS',ra,dec),POINT('ICRS',{RA},{DEC}))*3600 AS sep "
   f"FROM gaiadr3.gaia_source WHERE 1=CONTAINS(POINT('ICRS',ra,dec),CIRCLE('ICRS',{RA},{DEC},240./3600.)) AND phot_g_mean_mag<15 ORDER BY sep")
u="https://gea.esac.esa.int/tap-server/tap/sync?REQUEST=doQuery&LANG=ADQL&FORMAT=json&QUERY="+urllib.parse.quote(q)
g=json.loads(subprocess.run(["curl","-sL","--max-time","90",u],capture_output=True,text=True).stdout)["data"]
print("Stars G<15 within 4 arcmin (could leak through TESS PSF wings):")
for sid,ra,dec,G,sep in g: print(f"   sep {sep:6.1f}in  G={G:6.2f}  {sid}")
c=SkyCoord(RA,DEC,unit="deg")
tpf=lk.search_tesscut(c,sector=76)[0].download(cutout_size=11)
fl=tpf.flux.value; t=tpf.time.value; ok=np.isfinite(fl).all(axis=(1,2))&np.isfinite(t)
fl,t=fl[ok],t[ok]
xw,yw=[float(v) for v in tpf.wcs.world_to_pixel(c)]
ny,nx=fl.shape[1:]; amp=np.zeros((ny,nx)); pw=np.zeros((ny,nx))
for j in range(ny):
    for i in range(nx):
        f=fl[:,j,i]; f=f/np.nanmedian(f)
        ls=LombScargle(t,f); mdl=ls.model(np.linspace(t[0],t[0]+P,100),1/P)
        amp[j,i]=(mdl.max()-mdl.min())/2*np.nanmedian(fl[:,j,i])   # ABSOLUTE e/s amplitude
        pw[j,i]=ls.power(1/P)
jj,ii=np.unravel_index(np.argmax(amp),amp.shape)
print(f"\nTESS S76 pixel map (11x11), target WCS pixel = ({xw:.2f},{yw:.2f})")
print(f"   pixel with the LARGEST absolute 0.3388-d amplitude: ({ii},{jj})  -> offset from target {np.hypot(ii-xw,jj-yw):.2f} px = {np.hypot(ii-xw,jj-yw)*21:.0f}in")
# amplitude-weighted centroid of the signal vs flux-weighted centroid of the star
w=np.clip(amp,0,None); yy,xx=np.mgrid[0:ny,0:nx]
cs=( (w*xx).sum()/w.sum(), (w*yy).sum()/w.sum() )
img=np.nanmedian(fl,axis=0); iw=np.clip(img-np.nanmedian(img),0,None)
ci=( (iw*xx).sum()/iw.sum(), (iw*yy).sum()/iw.sum() )
print(f"   signal-amplitude centroid ({cs[0]:.2f},{cs[1]:.2f})  vs  stellar-flux centroid ({ci[0]:.2f},{ci[1]:.2f})  -> separation {np.hypot(cs[0]-ci[0],cs[1]-ci[1])*21:.1f}in")
print("   absolute amplitude map (e/s), rows top=high y:")
for j in range(ny-1,-1,-1): print("     "+" ".join(f"{amp[j,i]:6.1f}" for i in range(nx)))
