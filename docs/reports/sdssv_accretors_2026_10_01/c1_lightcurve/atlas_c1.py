"""ATLAS forced photometry at C1 (Gaia DR3 2101985070870393856), full history; submit, poll, save atlas_c1.txt."""
import os, time, requests
H = os.path.dirname(os.path.abspath(__file__)); RA, DEC = 290.51650, 42.25905
tok = open(os.path.expanduser("~/.config/atlas/token")).read().strip(); A = {"Authorization": f"Token {tok}", "Accept": "application/json"}
B = "https://fallingstar-data.com/forcedphot"
r = requests.post(f"{B}/queue/", headers=A, data={"ra": RA, "dec": DEC, "mjd_min": 57000., "send_email": False}, timeout=120)
print("submit", r.status_code, flush=True); url = r.json()["url"]; open(os.path.join(H, "atlas_task_url.txt"), "w").write(url)
for i in range(240):
    j = requests.get(url, headers=A, timeout=120).json()
    if j.get("finishtimestamp"):
        if j.get("result_url"):
            open(os.path.join(H, "atlas_c1.txt"), "w").write(requests.get(j["result_url"], headers=A, timeout=300).text); print("saved", flush=True)
        else: print("finished without result:", j.get("error_msg"), flush=True)
        requests.delete(url, headers=A, timeout=60); break
    print(time.strftime("%H:%M:%S"), "queue position", j.get("queuepos"), "started", bool(j.get("starttimestamp")), flush=True); time.sleep(120)
