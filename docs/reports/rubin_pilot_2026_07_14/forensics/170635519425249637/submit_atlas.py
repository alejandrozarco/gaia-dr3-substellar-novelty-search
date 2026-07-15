#!/usr/bin/env python
"""Submit ATLAS forced photometry job at the Rubin candidate position. Full history."""
import os, sys, json, time
import requests

RA, DEC = 332.39126, -14.8699
tok = open(os.path.expanduser("~/.config/atlas/token")).read().strip()
BASE = "https://fallingstar-data.com/forcedphot"

r = requests.post(
    f"{BASE}/queue/",
    headers={"Authorization": f"Token {tok}", "Accept": "application/json"},
    data={"ra": RA, "dec": DEC, "mjd_min": 57000.0, "send_email": False},
    timeout=60,
)
print("HTTP", r.status_code)
if r.status_code == 201:
    task_url = r.json()["url"]
    with open("/tmp/rubin_pilot/forensics/170635519425249637/atlas_task_url.txt", "w") as f:
        f.write(task_url + "\n")
    print("task queued:", task_url)
else:
    print(r.text[:500])
    sys.exit(1)
