#!/usr/bin/env python
"""Submit ZTF forced photometry (ZFPS) request at the candidate position (dec > -31 so in footprint)."""
import os, sys
import requests

RA, DEC = 332.39126, -14.8699
raw = open(os.path.expanduser("~/.config/ztf_zfps/userpass")).read().strip()
# file may hold "user:pass", "user pass", or just the shared password
if ":" in raw:
    user, pw = raw.split(":", 1)
elif " " in raw:
    user, pw = raw.split(None, 1)
else:
    user, pw = "alexander.keur@gmail.com", raw

# JD range: full ZTF history (survey start 2018-03 ~ JD 2458194) to now
params = {
    "ra": RA,
    "dec": DEC,
    "jdstart": 2458194.5,
    "jdend": 2461235.5,  # 2026-07-14
    "email": "alexander@ch.tudelft.nl",  # registered ZFPS account email (case-sensitive)
    "userpass": pw,
}
r = requests.get(
    "https://ztfweb.ipac.caltech.edu/cgi-bin/requestForcedPhotometry.cgi",
    params=params,
    auth=("ztffps", "dontgocrazy!"),  # public documented HTTP basic auth for ZFPS endpoint
    timeout=120,
)
print("HTTP", r.status_code)
body = r.text
# never print credentials; scrub anything resembling them
print(body.replace(pw, "<redacted>")[:1000])
sys.exit(0 if r.status_code == 200 else 1)
