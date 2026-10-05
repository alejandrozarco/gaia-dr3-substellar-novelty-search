import pandas as pd, os, time, urllib.request, sys
from concurrent.futures import ThreadPoolExecutor
from astropy.io import fits
W='.'
d=pd.read_csv(f'{W}/sci_meta.tbl')
CEN='center=290.5165,42.25905&size=140arcsec&gzip=false'
def urls(r):
    s=str(r.filefracday)
    b=f'https://irsa.ipac.caltech.edu/ibe/data/ztf/products/sci/{s[:4]}/{s[4:8]}/{s[8:]}/ztf_{s}_{r.field:06d}_{r.filtercode}_c{r.ccdid:02d}_{r.imgtypecode}_q{r.qid}_'
    tag=f'{s}_{r.field}_{r.filtercode}_c{r.ccdid:02d}_q{r.qid}'
    return tag,[(b+'scimrefdiffimg.fits.fz?'+CEN,f'{W}/cut/{tag}_diff.fits'),
                (b+'diffimgpsf.fits',f'{W}/cut/{tag}_psf.fits'),
                (b+'sciimg.fits?'+CEN,f'{W}/cut/{tag}_sci.fits')]
def ok(fn):
    try:
        with fits.open(fn) as h:
            for x in h:
                if x.data is not None and x.data.size>0: return True
    except Exception: return False
    return False
def get(u,fn):
    if os.path.exists(fn) and ok(fn): return 'cached'
    last=''
    for a in range(4):
        try:
            with urllib.request.urlopen(u,timeout=120) as resp:
                data=resp.read()
            open(fn,'wb').write(data)
            if ok(fn): return 'ok'
            last=f'invalid({len(data)}B)'
        except Exception as e:
            last=str(e)[:100]
            if '404' in last: break
        time.sleep(1+2*a)
    if os.path.exists(fn) and not ok(fn): os.remove(fn)
    return 'FAIL '+last
def job(i):
    r=d.iloc[i]; tag,L=urls(r)
    return tag,[get(u,f) for u,f in L]
log=open(f'{W}/download_log.txt','w')
with ThreadPoolExecutor(14) as ex:
    for n,(tag,st) in enumerate(ex.map(job,range(len(d)))):
        log.write(f'{tag} {st}\n'); log.flush()
        if n%100==0: print(n,tag,st,flush=True)
print('done')
