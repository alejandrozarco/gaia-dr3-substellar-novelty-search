#!/usr/bin/env python
"""Submit ZTF forced photometry (ZFPS) request. dec=-14.87 > -31 so in ZTF footprint."""
import os, sys
import requests

RA, DEC = 332.39126, -14.8699

with open(os.path.expanduser("~/.config/ztf_zfps/userpass")) as f:
    line = f.read().strip()
# expected format: user:pass or "user pass" or two lines
if ":" in line:
    user, pw = line.split(":", 1)
elif "\n" in line:
    parts = line.split("\n")
    user, pw = parts[0].strip(), parts[1].strip()
else:
    user, pw = line.split(None, 1)

url = "https://ztfweb.ipac.caltech.edu/cgi-bin/requestForcedPhotometry.cgi"
params = {
    "ra": str(RA),
    "dec": str(DEC),
    "jdstart": "2458194.5",   # ZTF survey start ~2018-03-17
    "jdend": "2461235.5",     # 2026-07-14
    "email": user,
    "userpass": pw,
}
r = requests.get(url, params=params, auth=("ztffps", "dontgocrazy!"), timeout=120)
print("status:", r.status_code)
ok = r.status_code == 200
print("body contains 'success/Thank':", ("Thank" in r.text) or ("success" in r.text.lower()))
print(r.text[:300].replace(user, "<user>").replace(pw, "<pass>"))
sys.exit(0 if ok else 1)
