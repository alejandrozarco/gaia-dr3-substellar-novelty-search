"""Poll the existing ATLAS task (atlas_task_url.txt) for C1 every 5 min for up to 48 h; save atlas_c1.txt; delete the task when done."""
import os, time, requests
H = os.path.dirname(os.path.abspath(__file__)); url = open(os.path.join(H, "atlas_task_url.txt")).read().strip()
tok = open(os.path.expanduser("~/.config/atlas/token")).read().strip(); A = {"Authorization": f"Token {tok}", "Accept": "application/json"}
for i in range(576):
    try: j = requests.get(url, headers=A, timeout=120).json()
    except Exception as e: print(time.strftime("%H:%M:%S"), "poll error", type(e).__name__, flush=True); time.sleep(300); continue
    if j.get("finishtimestamp"):
        if j.get("result_url"):
            open(os.path.join(H, "atlas_c1.txt"), "w").write(requests.get(j["result_url"], headers=A, timeout=300).text); print("saved", flush=True)
        else: print("finished without result:", j.get("error_msg"), flush=True)
        requests.delete(url, headers=A, timeout=60); break
    print(time.strftime("%H:%M:%S"), "queue position", j.get("queuepos"), "started", bool(j.get("starttimestamp")), flush=True); time.sleep(300)
