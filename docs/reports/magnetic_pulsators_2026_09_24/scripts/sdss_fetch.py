# Find (SpecObjAll, DR17) and download SDSS/BOSS lite spectra near given coordinates. Returns list of (plate,mjd,fiber,run2d,snMedian,path)
import requests, io, os, pandas as pd
SAS = 'https://data.sdss.org/sas/dr17'
def find(ra, dec, r_deg=0.0006):
    q = (f"SELECT plate, mjd, fiberid, run2d, snMedian, class, subclass, ra, dec, survey FROM SpecObjAll WHERE ra BETWEEN {ra - r_deg} AND {ra + r_deg} "
         f"AND dec BETWEEN {dec - r_deg} AND {dec + r_deg}")
    r = requests.get('https://skyserver.sdss.org/dr17/SkyServerWS/SearchTools/SqlSearch', params=dict(cmd=q, format='csv'), timeout=120)
    if r.status_code != 200: raise RuntimeError('HOLE SpecObjAll HTTP %d' % r.status_code)
    t = r.text.split('\n', 1)[1]
    return pd.read_csv(io.StringIO(t)) if t.strip() else pd.DataFrame()
def get(plate, mjd, fiber, run2d, outdir='/tmp/fanout/magpuls/spec'):
    fn = f'spec-{int(plate):04d}-{int(mjd)}-{int(fiber):04d}.fits'; p = os.path.join(outdir, fn)
    if os.path.exists(p) and os.path.getsize(p) > 10000: return p
    sub = 'sdss' if str(run2d) in ('26', '103', '104') else 'eboss'
    u = f'{SAS}/{sub}/spectro/redux/{run2d}/spectra/lite/{int(plate):04d}/{fn}'
    r = requests.get(u, timeout=120)
    if r.status_code != 200: return None
    open(p, 'wb').write(r.content); return p
