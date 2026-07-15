#!/usr/bin/env python
import requests, os, time, json, sys
D = "/tmp/rubin_pilot/forensics/170587105461272950"
tok = open(os.path.expanduser("~/.config/atlas/token")).read().strip()
url = open(f"{D}/atlas_task_url.txt").read().strip()
H = {"Authorization": f"Token {tok}", "Accept": "application/json"}
for i in range(40):
    try:
        r = requests.get(url, headers=H, timeout=60)
        j = r.json()
        print(time.strftime("%H:%M:%S"), "queuepos", j.get("queuepos"), "started", j.get("starttimestamp"),
              "finished", j.get("finishtimestamp"), flush=True)
        if j.get("error_msg"):
            print("ERROR:", j["error_msg"]); sys.exit(2)
        if j.get("result_url"):
            rr = requests.get(j["result_url"], headers={"Authorization": f"Token {tok}"}, timeout=300)
            open(f"{D}/atlas_fp.txt", "w").write(rr.text)
            print("SAVED atlas_fp.txt", len(rr.text), "bytes")
            sys.exit(0)
    except Exception as e:
        print("poll err:", repr(e), flush=True)
    time.sleep(60)
print("TIMEOUT after 40 polls")
sys.exit(1)
