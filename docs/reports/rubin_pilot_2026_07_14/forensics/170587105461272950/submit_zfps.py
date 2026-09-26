#!/usr/bin/env python
import os, requests, json
RA, DEC = 334.24962, -18.20795
zpass = open(os.path.expanduser("~/.config/ztf_zfps/userpass")).read().strip()
r = requests.get(
    "https://ztfweb.ipac.caltech.edu/cgi-bin/requestForcedPhotometry.cgi",
    params={"ra": RA, "dec": DEC, "jdstart": 2458194.5, "jdend": 2461236.5,
            "email": os.environ["CONTACT_EMAIL"], "userpass": zpass},
    auth=("ztffps", "dontgocrazy!"), timeout=120)
txt = r.text.replace(zpass, "<pass>")
print(json.dumps({"http": r.status_code, "snippet": txt[:600]}))
