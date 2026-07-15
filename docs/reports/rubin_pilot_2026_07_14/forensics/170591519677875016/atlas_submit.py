import os, sys, requests, json
RA, DEC = 306.74802, -11.81856
tok = open(os.path.expanduser("~/.config/atlas/token")).read().strip()
BASE = "https://fallingstar-data.com/forcedphot"
r = requests.post(f"{BASE}/queue/", headers={"Authorization": f"Token {tok}"},
                  data={"ra": RA, "dec": DEC, "mjd_min": 50000., "send_email": False})
print("status:", r.status_code)
if r.status_code == 201:
    url = r.json()["url"]
    open("/tmp/rubin_pilot/forensics/170591519677875016/atlas_task_url.txt","w").write(url)
    print("task queued:", url)
else:
    print(r.text[:500])
