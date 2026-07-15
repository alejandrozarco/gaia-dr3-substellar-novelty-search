#!/usr/bin/env python
"""Submit ZTF forced photometry (ZFPS) request. Credentials never printed."""
import os, requests

RA, DEC = 313.22651, -14.84044
EMAIL = "alexander@ch.tudelft.nl"  # registered ZFPS account email (per prior repo script)
# Full ZTF history: survey start 2018-03-17 (JD 2458194.5) to today 2026-07-14 (JD 2461235.5)
JDSTART, JDEND = 2458194.5, 2461235.5

with open(os.path.expanduser("~/.config/ztf_zfps/userpass")) as f:
    userpass = f.read().strip()

resp = requests.get(
    "https://ztfweb.ipac.caltech.edu/cgi-bin/requestForcedPhotometry.cgi",
    params={
        "ra": RA, "dec": DEC,
        "jdstart": JDSTART, "jdend": JDEND,
        "email": EMAIL, "userpass": userpass,
    },
    auth=("ztffps", "dontgocrazy!"),
    timeout=120,
)
print("HTTP", resp.status_code)
body = resp.text
# scrub any echo of credentials before printing
body = body.replace(userpass, "***")
print(body[:2000])
