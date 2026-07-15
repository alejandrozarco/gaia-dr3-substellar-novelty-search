import os, requests, sys
tok = open(os.path.expanduser("~/.config/atlas/token")).read().strip()
url = open("/tmp/rubin_pilot/forensics/170591507978387512/atlas_task_url.txt").read().strip()
r = requests.get(url, headers={"Authorization": f"Token {tok}", "Accept": "application/json"}, timeout=60)
j = r.json()
print("finishtimestamp:", j.get("finishtimestamp"))
print("result_url:", j.get("result_url"))
print("queue pos / started:", j.get("queuepos"), j.get("starttimestamp"))
if j.get("result_url"):
    rr = requests.get(j["result_url"], headers={"Authorization": f"Token {tok}"}, timeout=120)
    open("/tmp/rubin_pilot/forensics/170591507978387512/atlas_fp_raw.txt","w").write(rr.text)
    print("saved", len(rr.text), "bytes")
