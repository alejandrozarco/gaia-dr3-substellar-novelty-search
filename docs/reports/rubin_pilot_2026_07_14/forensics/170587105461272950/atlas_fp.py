#!/usr/bin/env python
"""Queue ATLAS forced photometry at target position, poll until done, save full history."""
import os, sys, time, io
import requests
import pandas as pd

RA, DEC = 334.24962, -18.20795
OUTDIR = "/tmp/rubin_pilot/forensics/170587105461272950"
BASE = "https://fallingstar-data.com/forcedphot"

with open(os.path.expanduser("~/.config/atlas/token")) as f:
    token = f.read().strip()
headers = {"Authorization": f"Token {token}", "Accept": "application/json"}

# Queue task: full history from MJD 57000 (2015) to now
task_url = None
for attempt in range(10):
    r = requests.post(f"{BASE}/queue/", headers=headers,
                      data={"ra": RA, "dec": DEC, "mjd_min": 57000, "send_email": False})
    if r.status_code == 201:
        task_url = r.json()["url"]
        print(f"queued: {task_url}")
        break
    elif r.status_code == 429:
        wait = 30
        msg = r.json()
        print(f"throttled: {msg}", file=sys.stderr)
        time.sleep(wait)
    else:
        print(f"queue error {r.status_code}: {r.text[:500]}", file=sys.stderr)
        sys.exit(2)
if task_url is None:
    sys.exit(3)

result_url = None
t0 = time.time()
while time.time() - t0 < 3300:
    r = requests.get(task_url, headers=headers)
    if r.status_code != 200:
        print(f"poll error {r.status_code}", file=sys.stderr); time.sleep(20); continue
    j = r.json()
    if j.get("finishtimestamp"):
        result_url = j.get("result_url")
        print(f"finished, result_url present: {result_url is not None}")
        break
    print(f"waiting... starttimestamp={j.get('starttimestamp')}")
    time.sleep(20)

if not result_url:
    print("TIMEOUT or no result_url", file=sys.stderr)
    sys.exit(4)

r = requests.get(result_url, headers=headers)
txt = r.text
with open(f"{OUTDIR}/atlas_fp_raw.txt", "w") as f:
    f.write(txt)
df = pd.read_csv(io.StringIO(txt.replace("###", "")), delim_whitespace=True)
df.to_csv(f"{OUTDIR}/atlas_fp.csv", index=False)
print(f"rows={len(df)} mjd_range={df['MJD'].min():.2f}..{df['MJD'].max():.2f}")
print("DONE")
