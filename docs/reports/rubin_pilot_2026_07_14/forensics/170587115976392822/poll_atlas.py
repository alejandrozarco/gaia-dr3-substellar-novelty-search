#!/usr/bin/env python
"""Poll ATLAS FP task until done (max ~25 min), then download result to atlas_fp.txt."""
import os
import time, requests, sys

OUT = '/tmp/rubin_pilot/forensics/170587115976392822'
tok = open(os.path.expanduser('~/.config/atlas/token')).read().strip()
H = {'Authorization': f'Token {tok}', 'Accept': 'application/json'}
task_url = open(f'{OUT}/atlas_task_url.txt').read().strip()

deadline = time.time() + 25*60
while time.time() < deadline:
    try:
        j = requests.get(task_url, headers=H, timeout=60).json()
    except Exception as e:
        print('poll err', repr(e)[:100]); time.sleep(30); continue
    if j.get('finishtimestamp'):
        ru = j['result_url']
        txt = requests.get(ru, headers={'Authorization': f'Token {tok}'}, timeout=120).text
        open(f'{OUT}/atlas_fp.txt', 'w').write(txt)
        print('DONE rows=', len(txt.splitlines()) - 1)
        sys.exit(0)
    print('waiting; queuepos =', j.get('queuepos'), 'started =', j.get('starttimestamp'))
    time.sleep(45)
print('TIMEOUT still queued')
sys.exit(2)
