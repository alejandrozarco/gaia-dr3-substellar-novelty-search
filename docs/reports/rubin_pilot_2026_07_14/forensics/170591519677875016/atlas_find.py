import os, requests
tok = open(os.path.expanduser("~/.config/atlas/token")).read().strip()
H = {"Authorization": f"Token {tok}", "Accept": "application/json"}
r = requests.get("https://fallingstar-data.com/forcedphot/queue/", headers=H)
print("status:", r.status_code)
j = r.json()
res = j["results"] if isinstance(j, dict) and "results" in j else j
for t in res[:5]:
    print(t.get("url"), "ra=", t.get("ra"), "dec=", t.get("dec"), "finish:", t.get("finishtimestamp"), "result:", t.get("result_url"))
# save the newest matching our coords
for t in res:
    if abs(t.get("ra",0)-306.74802)<1e-3 and abs(t.get("dec",0)+11.81856)<1e-3:
        open("/tmp/rubin_pilot/forensics/170591519677875016/atlas_task_url.txt","w").write(t["url"])
        print("SAVED", t["url"])
        break
