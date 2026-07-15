#!/usr/bin/env python
"""Submit ATLAS forced photometry task for target position. Token never printed."""
import json, os, sys, requests

RA, DEC = 313.22651, -14.84044
BASEURL = "https://fallingstar-data.com/forcedphot"

with open(os.path.expanduser("~/.config/atlas/token")) as f:
    token = f.read().strip()
headers = {"Authorization": f"Token {token}", "Accept": "application/json"}

resp = requests.post(
    f"{BASEURL}/queue/",
    headers=headers,
    data={"ra": RA, "dec": DEC, "mjd_min": 57000.0, "send_email": False},
    timeout=60,
)
print("HTTP", resp.status_code)
if resp.status_code == 201:
    task_url = resp.json()["url"]
    with open("/tmp/rubin_pilot/forensics/170591507978387512/atlas_task_url.txt", "w") as f:
        f.write(task_url + "\n")
    print("task queued:", task_url)
else:
    print(resp.text[:500])
    sys.exit(1)
