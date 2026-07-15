#!/usr/bin/env python
"""Submit ZTF forced photometry request (dec=-18.2 > -31 so in ZTF footprint)."""
import os, requests, sys

RA, DEC = 334.24962, -18.20795
with open(os.path.expanduser("~/.config/ztf_zfps/userpass")) as f:
    pw = f.read().strip()  # ZFPS userpass code
user = "alexander@ch.tudelft.nl"  # registered ZFPS email (case-sensitive per IPAC)

url = "https://ztfweb.ipac.caltech.edu/cgi-bin/requestForcedPhotometry.cgi"
# Full ZTF history: JD 2458194.5 (2018-03-17 survey start) to now
params = {
    "ra": RA, "dec": DEC,
    "jdstart": 2458194.5, "jdend": 2461236.5,
    "email": user, "userpass": pw,
}
r = requests.get(url, params=params, auth=("ztffps", "dontgocrazy!"), timeout=120)
print("status:", r.status_code)
# don't print full text (may echo credentials); check markers
t = r.text
ok = ("Successfully submitted" in t) or ("success" in t.lower())
print("submit_ok_marker:", ok)
if not ok:
    # print sanitized snippet
    import re
    s = re.sub(r"(email|userpass)=[^&\s\"']+", r"\1=REDACTED", t)
    print(s[:800])
