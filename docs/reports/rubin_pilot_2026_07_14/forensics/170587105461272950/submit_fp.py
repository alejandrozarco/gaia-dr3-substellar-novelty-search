#!/usr/bin/env python
"""Submit ATLAS forced-photometry and ZTF ZFPS jobs for the Rubin hostless candidate.
Target: diaObjectId 170587105461272950, RA=334.24962, Dec=-18.20795.
Credentials are read from files; values are NEVER printed.
"""
import json, os, sys, time
import requests

RA, DEC = 334.24962, -18.20795
OUT = "/tmp/rubin_pilot/forensics/170587105461272950"

def read_secret(path):
    with open(os.path.expanduser(path)) as f:
        return f.read().strip()

results = {}

# ---------- ATLAS forced photometry ----------
try:
    atlas_token = read_secret("~/.config/atlas/token")
    r = requests.post(
        "https://fallingstar-data.com/forcedphot/queue/",
        headers={"Authorization": f"Token {atlas_token}", "Accept": "application/json"},
        data={"ra": RA, "dec": DEC, "mjd_min": 57000.0, "send_email": False},
        timeout=60,
    )
    if r.status_code == 201:
        task_url = r.json()["url"]
        with open(f"{OUT}/atlas_task_url.txt", "w") as f:
            f.write(task_url + "\n")
        results["atlas"] = {"status": "queued", "task_url": task_url}
    else:
        results["atlas"] = {"status": f"HTTP {r.status_code}", "body": r.text[:500]}
except Exception as e:
    results["atlas"] = {"status": "error", "err": repr(e)}

# ---------- ZTF forced photometry service (ZFPS) ----------
# dec = -18.2 > -31 => in ZTF footprint. Full history JD 2458194.5 (2018-03-17) to now.
try:
    up = read_secret("~/.config/ztf_zfps/userpass")
    # file format could be "user:pass" or two lines
    if ":" in up:
        zuser, zpass = up.split(":", 1)
    else:
        parts = up.split()
        zuser, zpass = parts[0], parts[1]
    jd_now = 2461235.5 + 1  # today + margin
    r = requests.get(
        "https://ztfweb.ipac.caltech.edu/cgi-bin/requestForcedPhotometry.cgi",
        params={
            "ra": RA, "dec": DEC,
            "jdstart": 2458194.5, "jdend": jd_now,
            "email": zuser, "userpass": zpass,
        },
        auth=("ztffps", "dontgocrazy!"),
        timeout=120,
    )
    ok = r.status_code == 200 and ("successfully" in r.text.lower() or "submitted" in r.text.lower())
    results["zfps"] = {"status": "submitted" if ok else f"HTTP {r.status_code}",
                       "snippet": r.text[:300].replace(zuser, "<user>").replace(zpass, "<pass>")}
except Exception as e:
    results["zfps"] = {"status": "error", "err": repr(e)}

print(json.dumps(results, indent=2))
