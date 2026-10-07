import pyvo, sys, numpy as np, time
from astropy.table import Table
s=sys.argv[1]; chunk=int(sys.argv[2]) if len(sys.argv)>2 else 50000
ids=np.loadtxt(f'lists/s{s}.csv',delimiter=',',usecols=0,dtype=np.int64,skiprows=1)
svc=pyvo.dal.TAPService('https://tapvizier.cds.unistra.fr/TAPVizieR/tap')
import os
for i in range(0,len(ids),chunk):
    out=f'lists/tic_s{s}_{i//chunk:03d}.fits'
    if os.path.exists(out): continue
    t=Table({'tic':ids[i:i+chunk]})
    q='SELECT t.TIC, t.Tmag, t.Teff, t."Dist", t.Rad, t.Mass, t.logg, t.GAIA, t.RAJ2000, t.DEJ2000, t.Rcont, t.LClass, t.Plx FROM "IV/39/tic82" AS t JOIN TAP_UPLOAD.u AS u ON t.TIC=u.tic WHERE t.Tmag<=11.5'
    t0=time.time()
    r=svc.run_async(q,uploads={'u':t},maxrec=1000000).to_table()
    r.write(out)
    print(i,len(r),round(time.time()-t0,1),flush=True)
