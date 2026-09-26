#!/usr/bin/env python
"""Recover ATLAS task URL from queue list (task already created, 201), then submit ZFPS."""
import os
import time, requests

RA, DEC = 326.82833, -13.4747
OUT = '/tmp/rubin_pilot/forensics/170587115976392822'
atlas_token = open(os.path.expanduser('~/.config/atlas/token')).read().strip()
zfps_userpass = open(os.path.expanduser('~/.config/ztf_zfps/userpass')).read().strip()
EMAIL = os.environ["CONTACT_EMAIL"]
H = {'Authorization': f'Token {atlas_token}', 'Accept': 'application/json'}

# find the most recent task at our coordinates
r = requests.get('https://fallingstar-data.com/forcedphot/queue/', headers=H, timeout=60)
print('ATLAS queue list status:', r.status_code)
tasks = r.json()['results']
mine = [t for t in tasks if abs(t.get('ra', 1e9) - RA) < 1e-3 and abs(t.get('dec', 1e9) - DEC) < 1e-3]
print('matching tasks:', len(mine))
if mine:
    t = sorted(mine, key=lambda x: x['timestamp'])[-1]
    open(f'{OUT}/atlas_task_url.txt', 'w').write(t['url'] + '\n')
    print('ATLAS task id:', t['url'].rstrip('/').split('/')[-1], 'finishtimestamp:', t.get('finishtimestamp'))

# ---- ZFPS ----
jdend = 2440587.5 + time.time()/86400.0
params = {'ra': RA, 'dec': DEC, 'jdstart': 2458194.5, 'jdend': round(jdend, 5),
          'email': EMAIL, 'userpass': zfps_userpass}
r2 = requests.get('https://ztfweb.ipac.caltech.edu/cgi-bin/requestForcedPhotometry.cgi',
                  params=params, auth=('ztffps', 'dontgocrazy!'), timeout=180)
safe = r2.text.replace(zfps_userpass, '***')
print('ZFPS submit status:', r2.status_code)
print('ZFPS response (truncated):', safe[:600])
