import os, sys, requests, json
tok = open(os.path.expanduser("~/.config/atlas/token")).read().strip()
BASE = "https://fallingstar-data.com/forcedphot"
hdr = {"Authorization": f"Token {tok}", "Accept": "application/json"}
r = requests.post(f"{BASE}/queue/", headers=hdr, data={
    "ra": 313.22651, "dec": -14.84044, "mjd_min": 57000.0, "send_email": False, "use_reduced": False})
print("status", r.status_code)
if r.status_code == 201:
    url = r.json()["url"]
    open("/tmp/rubin_pilot/forensics/170591507978387512/atlas_task_url.txt","w").write(url)
    print("task queued:", url)
else:
    print(r.text[:500])
