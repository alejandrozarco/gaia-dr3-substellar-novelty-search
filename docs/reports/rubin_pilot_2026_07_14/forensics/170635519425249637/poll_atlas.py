#!/usr/bin/env python
import os, requests, time, sys

tok = open(os.path.expanduser("~/.config/atlas/token")).read().strip()
url = open("/tmp/rubin_pilot/forensics/170635519425249637/atlas_task_url.txt").read().strip()
deadline = time.time() + 40 * 60
while time.time() < deadline:
    try:
        r = requests.get(url, headers={"Authorization": f"Token {tok}", "Accept": "application/json"}, timeout=60)
        d = r.json()
        if d.get("error_msg"):
            print("ATLAS error:", d["error_msg"]); sys.exit(2)
        if d.get("result_url"):
            rr = requests.get(d["result_url"], headers={"Authorization": f"Token {tok}"}, timeout=300)
            open("/tmp/rubin_pilot/forensics/170635519425249637/atlas_fp.txt", "w").write(rr.text)
            print("saved atlas_fp.txt", len(rr.text), "bytes")
            sys.exit(0)
    except Exception as e:
        print("poll err", e)
    time.sleep(45)
print("timed out after 40 min")
sys.exit(1)
