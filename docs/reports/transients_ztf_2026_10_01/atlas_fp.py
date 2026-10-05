"""ATLAS forced photometry (fallingstar-data.com) for candidates, recent window (mjd_min 61200; ZTF alert history covers recurrence), one job at a time
(queue, poll every 15 s, fetch, then delete the task), 2026-10-01. Output: atlas/<oid>.txt. Usage: python atlas_fp.py oid:ra:dec [...]"""
import os, sys, time, requests
tok = open(os.path.expanduser("~/.config/atlas/token")).read().strip(); H = {"Authorization": f"Token {tok}", "Accept": "application/json"}
B = "https://fallingstar-data.com/forcedphot"
for a in sys.argv[1:]:
    o, ra, de = a.split(":")
    if os.path.exists(f"atlas/{o}.txt"): continue
    while True:
        r = requests.post(f"{B}/queue/", headers=H, data=dict(ra=ra, dec=de, mjd_min=61200, send_email=False), timeout=60)
        if r.status_code == 201: url = r.json()["url"]; break
        if r.status_code == 429: print("throttled", r.text[:100], flush=True); time.sleep(60); continue
        print(o, "queue failed", r.status_code, r.text[:200], flush=True); url = None; break
    if not url: continue
    while True:
        time.sleep(15); t = requests.get(url, headers=H, timeout=60).json()
        if t.get("finishtimestamp"):
            if t.get("result_url"):
                d = requests.get(t["result_url"], headers=H, timeout=120).text; open(f"atlas/{o}.txt", "w").write(d); print(o, "rows", d.count("\n"), flush=True)
            else: print(o, "HOLE (no result):", t.get("error_msg"), flush=True)
            requests.delete(url, headers=H, timeout=60); break
print("ATLAS-DONE")
