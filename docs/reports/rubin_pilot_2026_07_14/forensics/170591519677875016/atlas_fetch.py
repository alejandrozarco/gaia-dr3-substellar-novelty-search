import os, requests
tok = open(os.path.expanduser("~/.config/atlas/token")).read().strip()
H = {"Authorization": f"Token {tok}"}
r = requests.get("https://fallingstar-data.com/forcedphot/static/results/job4539055.txt", headers=H)
print("status:", r.status_code, "bytes:", len(r.content))
open("/tmp/rubin_pilot/forensics/170591519677875016/atlas_fp_raw.txt","wb").write(r.content)
