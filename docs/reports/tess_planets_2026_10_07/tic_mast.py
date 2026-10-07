import sys, os, numpy as np, time
from astroquery.mast import Catalogs
s=sys.argv[1]; ch=2000
ids=np.loadtxt(f'lists/s{s}.csv',delimiter=',',usecols=0,dtype=np.int64,skiprows=1)
os.makedirs(f'lists/tic{s}',exist_ok=True)
cols=['ID','Tmag','Teff','d','rad','mass','logg','GAIA','ra','dec','contratio','lumclass','plx','Vmag','Kmag','gaiabp','gaiarp','GAIAmag']
for i in range(0,len(ids),ch):
    out=f'lists/tic{s}/c{i//ch:04d}.csv'
    if os.path.exists(out): continue
    for k in range(4):
        try:
            r=Catalogs.query_criteria(catalog='Tic', ID=[int(x) for x in ids[i:i+ch]]); break
        except Exception as e:
            print('retry',i,e,flush=True); time.sleep(10)
    r=r[r['Tmag']<=11.5][cols]
    r.write(out,format='csv',overwrite=True)
    print(time.strftime('%H:%M:%S'),i,len(r),flush=True)
open(f'lists/tic{s}/DONE','w').write('ok')
