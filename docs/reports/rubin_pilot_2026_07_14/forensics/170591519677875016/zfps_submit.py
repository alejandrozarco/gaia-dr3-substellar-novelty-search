import os, requests
pw = open(os.path.expanduser("~/.config/ztf_zfps/userpass")).read().strip()
email = "alexander@ch.tudelft.nl"
RA, DEC = 306.74802, -11.81856
r = requests.get("https://ztfweb.ipac.caltech.edu/cgi-bin/requestForcedPhotometry.cgi",
    auth=("ztffps", "dontgocrazy!"),
    params={"ra": RA, "dec": DEC, "jdstart": 2458194.5, "jdend": 2461235.5,
            "email": email, "userpass": pw})
print("status:", r.status_code)
import re
txt = r.text.replace(pw, "***")
print(re.sub(r"<[^>]+>", " ", txt)[:800])
