#!/usr/bin/env python
"""Submit ATLAS forced photometry request for the Rubin hostless candidate."""
import os, sys, json
import requests

RA, DEC = 332.39126, -14.8699
BASE = "https://fallingstar-data.com/forcedphot"

with open(os.path.expanduser("~/.config/atlas/token")) as f:
    token = f.read().strip()
headers = {"Authorization": f"Token {token}", "Accept": "application/json"}

# Full history: MJD 50000 onward
resp = requests.post(
    f"{BASE}/queue/",
    headers=headers,
    data={"ra": RA, "dec": DEC, "mjd_min": 57000.0, "send_email": False},
    timeout=60,
)
print("status:", resp.status_code)
if resp.status_code == 201:
    task_url = resp.json()["url"]
    with open("/tmp/rubin_pilot/forensics/170635519425249637/atlas_task_url.txt", "w") as f:
        f.write(task_url + "\n")
    print("task queued OK (url saved to atlas_task_url.txt)")
elif resp.status_code == 429:
    print("throttled:", resp.json())
else:
    print("error body (truncated):", resp.text[:500])
    sys.exit(1)
