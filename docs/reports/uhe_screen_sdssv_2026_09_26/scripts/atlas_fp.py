"""ATLAS forced photometry (fallingstar-data.com) for a list of positions; token read from ~/.config/atlas/token (never printed)."""
import os, sys, time, requests, pandas as pd
U = os.path.dirname(os.path.abspath(__file__)); tok = open(os.path.expanduser("~/.config/atlas/token")).read().strip()
H = {"Authorization": f"Token {tok}", "Accept": "application/json"}; BASE = "https://fallingstar-data.com/forcedphot"
T = [l.split() for l in open(sys.argv[1]) if l.strip()]
jobs = {}
for name, ra, dec in T:
    if os.path.exists(f"{U}/atlas/{name}.txt"): continue
    for k in range(5):
        r = requests.post(f"{BASE}/queue/", headers=H, data=dict(ra=ra, dec=dec, mjd_min=57000, send_email=False), timeout=120)
        if r.status_code == 201: jobs[name] = r.json()["url"]; print(name, "queued", flush=True); break
        if r.status_code == 429: time.sleep(60); continue
        print(name, "queue status", r.status_code, flush=True); time.sleep(20)
while jobs:
    time.sleep(30)
    for name, url in list(jobs.items()):
        r = requests.get(url, headers=H, timeout=120)
        if r.status_code != 200: continue
        j = r.json()
        if j.get("finishtimestamp"):
            if j.get("result_url"):
                t = requests.get(j["result_url"], headers=H, timeout=300).text; open(f"{U}/atlas/{name}.txt", "w").write(t); print(name, "done", len(t.splitlines()), flush=True)
            else:
                print(name, "finished without result", j.get("error_msg"), flush=True)
            requests.delete(url, headers=H, timeout=60); del jobs[name]
