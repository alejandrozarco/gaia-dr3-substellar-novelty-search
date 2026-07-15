import requests, os, json
tok = open(os.path.expanduser('~/.config/atlas/token')).read().strip()
h = {'Authorization': f'Token {tok}', 'Accept': 'application/json'}
r = requests.get('https://fallingstar-data.com/forcedphot/queue/', headers=h)
j = r.json()
for t in j['results'][:5]:
    print(t['url'], t['ra'], t['dec'], t.get('starttimestamp'), t.get('finishtimestamp'))
# newest task matching our coords
for t in j['results']:
    if abs(t['ra']-326.82833)<1e-3 and abs(t['dec']+13.4747)<1e-3:
        open('/tmp/rubin_pilot/forensics/170587115976392822/atlas_task_url.txt','w').write(t['url'])
        print('SAVED', t['url']); break
