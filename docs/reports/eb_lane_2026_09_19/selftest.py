"""Self-recovery test: the fixed pipeline MUST recover our own filed discovery.
ZTF18abxnwmb = 2MASS J22342534+0806596, P=3.727023 d, depth 0.216 mag, duty 5.7%."""
import csv, numpy as np, subprocess, io
from astropy.timeseries import BoxLeastSquares
url=("https://irsa.ipac.caltech.edu/cgi-bin/ZTF/nph_light_curves?"
     "POS=CIRCLE%20338.605525%208.116548%200.00042&BAD_CATFLAGS_MASK=32768&FORMAT=CSV")
rows=[r for r in csv.DictReader(io.StringIO(subprocess.run(["curl","-sL","--max-time","150",url],
      capture_output=True,text=True).stdout))
      if r['catflags']=='0' and r['filtercode']=='zr' and abs(float(r['sharp']))<0.5
      and float(r['chi'])<3 and float(r['mag'])<float(r['limitmag'])-0.3]
mjd=np.array([float(r['mjd']) for r in rows]); mag=np.array([float(r['mag']) for r in rows])
err=np.array([float(r['magerr']) for r in rows]); o=np.argsort(mjd)
mjd,mag,err=mjd[o],mag[o],err[o]
base=float(np.median(mag))
flux=10.0**(-0.4*(mag-base)); ferr=flux*err*(np.log(10)/2.5)
print(f"ZTF18abxnwmb: {len(mjd)} clean zr epochs, baseline {base:.3f}")
grid=np.exp(np.linspace(np.log(0.2),np.log(20),12000))
durs=np.array([0.012,0.025,0.05,0.09])
for lab,y,dy in (("FLUX (fixed)",flux,ferr),("MAGNITUDE (old, buggy)",mag,err)):
    r=BoxLeastSquares(mjd,y,dy=dy).power(grid,durs,objective="snr")
    i=int(np.argmax(r.power)); P=float(r.period[i])
    known=3.727023
    hit = min(abs(P-known)/known, abs(P-2*known)/(2*known), abs(P-known/2)/(known/2))
    print(f"  {lab:24s} best P={P:.6f} d  snr={float(r.power[i]):.1f}  "
          f"-> {'RECOVERED' if hit<0.01 else 'MISSED'} (known {known}, closest match {hit*100:.2f}%)")
