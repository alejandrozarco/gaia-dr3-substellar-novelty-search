# Submit ATLAS forced-photometry jobs for gate survivors (token read from file, never printed). Probe: HD 49798 position is not needed; a known CV (RR Pic) is added as positive control.
import os, json, time, requests, numpy as np
from astropy.table import Table
tok=open(os.path.expanduser('~/.config/atlas/token')).read().strip()
H={'Authorization':f'Token {tok}','Accept':'application/json'}
M=Table.read('s07_props.ecsv'); S=M[~M['known_cv'].astype(bool)]
skip={5580229559184884224}  # G=7 star
S=[r for r in S if str(r['otype'])!='PN' and int(r['GaiaEDR3']) not in skip and 'GW Vir' not in str(r['simbad'])]
jobs=[(int(r['GaiaEDR3']),float(r['ra_1'] if 'ra_1' in M.colnames else r['ra']),float(r['dec_1'] if 'dec_1' in M.colnames else r['dec'])) for r in S]
jobs.append((5477422099543150592,98.9003,-62.6401))  # RR Pic control
out={}
if os.path.exists('atlas/tasks.json'): out=json.load(open('atlas/tasks.json'))
for gid,ra,de in jobs:
    if str(gid) in out: continue
    for k in range(5):
        r=requests.post('https://fallingstar-data.com/forcedphot/queue/',headers=H,data={'ra':ra,'dec':de,'mjd_min':57000.,'send_email':False},timeout=60)
        if r.status_code==201: out[str(gid)]=r.json()['url']; break
        elif r.status_code==429:
            time.sleep(int(r.json().get('detail','x 10 ').split()[-2]) if 'seconds' in r.text else 15)
        else: print(gid,'status',r.status_code,r.text[:150]); time.sleep(10)
    json.dump(out,open('atlas/tasks.json','w'),indent=1)
print('submitted',len(out),'of',len(jobs))
