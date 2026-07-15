import os, requests
pw = open(os.path.expanduser("~/.config/ztf_zfps/userpass")).read().strip()
r = requests.get("https://ztfweb.ipac.caltech.edu/cgi-bin/requestForcedPhotometry.cgi",
    auth=("ztffps", "dontgocrazy!"),
    params={"ra": 313.22651, "dec": -14.84044,
            "jdstart": 2458194.5, "jdend": 2461236.5,
            "email": "alexander@ch.tudelft.nl", "userpass": pw}, timeout=120)
txt = r.text.replace(pw, "***")
import re
print("status:", r.status_code)
m = re.findall(r"(?i)(success|error|exceed|invalid|thank)[^<]*", txt)
print(m if m else txt[:600])
