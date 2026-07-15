import requests, os, json, sys
tok = open(os.path.expanduser('~/.config/atlas/token')).read().strip()
BASE = 'https://fallingstar-data.com/forcedphot'
r = requests.post(f'{BASE}/queue/', headers={'Authorization': f'Token {tok}'},
                  data={'ra': 326.82833, 'dec': -13.4747, 'mjd_min': 50000., 'send_email': False})
print(r.status_code)
if r.status_code == 201:
    url = r.json()['url']
    open('/tmp/rubin_pilot/forensics/170587115976392822/atlas_task_url.txt','w').write(url)
    print('task queued:', url)
else:
    print(r.text[:500])
