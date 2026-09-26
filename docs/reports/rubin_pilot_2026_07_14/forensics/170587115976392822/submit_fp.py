#!/usr/bin/env python
"""Submit ATLAS forced photometry + ZTF ZFPS requests for the Rubin target.
Credentials are read from files and NEVER printed."""
import os
import json, sys, time
import requests

RA, DEC = 326.82833, -13.4747
OUT = '/tmp/rubin_pilot/forensics/170587115976392822'

atlas_token = open(os.path.expanduser('~/.config/atlas/token')).read().strip()
zfps_userpass = open(os.path.expanduser('~/.config/ztf_zfps/userpass')).read().strip()
EMAIL = os.environ["CONTACT_EMAIL"]

# ---- ATLAS ----
r = requests.post('https://fallingstar-data.com/forcedphot/queue/',
                  headers={'Authorization': f'Token {atlas_token}'},
                  data={'ra': RA, 'dec': DEC, 'mjd_min': 57000., 'send_email': False},
                  timeout=60)
print('ATLAS submit status:', r.status_code)
if r.status_code == 201:
    task_url = r.json()['url']
    open(f'{OUT}/atlas_task_url.txt', 'w').write(task_url + '\n')
    print('ATLAS task url saved (id):', task_url.rstrip('/').split('/')[-1])
else:
    print('ATLAS submit failed body (truncated):', r.text[:300])

# ---- ZFPS ----
# JD range: ZTF survey start (2018-03-17 ~ 2458194.5) to now
import datetime
jdend = 2440587.5 + time.time()/86400.0
params = {'ra': RA, 'dec': DEC, 'jdstart': 2458194.5, 'jdend': round(jdend,5),
          'email': EMAIL, 'userpass': zfps_userpass}
r2 = requests.get('https://ztfweb.ipac.caltech.edu/cgi-bin/requestForcedPhotometry.cgi',
                  params=params, auth=('ztffps', 'dontgocrazy!'), timeout=120)
print('ZFPS submit status:', r2.status_code)
body = r2.text
# scrub any echo of credentials before printing
safe = body.replace(zfps_userpass, '***')
print('ZFPS response (truncated):', safe[:500])
