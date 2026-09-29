"""Daily check whether the Rubin public alert stream is flowing again.
Queries the latest alert time at Fink-LSST (tags endpoint, three tags) and ALeRCE-LSST (list_objects ordered by lastmjd).
A failed query is reported as FAILED, never as 'dark'. The stream is LIVE when any broker's latest alert is < 3 days old.
Appends one line to rubin_stream_status.log and, on the first LIVE result after a dark period, posts a macOS notification.
Usage: python rubin_stream_check.py   (RUBINWATCH_TEST=1 fires a labelled test notification only)"""
import os, time, json, subprocess, requests
H = os.path.dirname(os.path.abspath(__file__)); LOG = os.path.join(H, "rubin_stream_status.log"); STATE = os.path.join(H, ".last_state")
now_mjd = time.time() / 86400 + 40587
def fink():
    best = None
    for tag in ("in_tns", "extragalactic_new_candidate", "hostless_candidate"):
        r = requests.post("https://api.lsst.fink-portal.org/api/v1/tags", json={"tag": tag, "n": 5, "output-format": "json"}, timeout=90)
        r.raise_for_status(); d = r.json()
        for a in d:
            m = a.get("r:midpointMjdTai")
            if m is not None: best = max(best or 0, float(m))
    return best
def alerce():
    r = requests.get("https://api-lsst.alerce.online/object_api/list_objects", params=dict(page_size=5, order_by="lastmjd", order_mode="DESC", survey="lsst"), timeout=90)
    r.raise_for_status(); it = r.json().get("items", [])
    return max(float(i["lastmjd"]) for i in it) if it else None
res = {}
for name, fn in (("fink", fink), ("alerce", alerce)):
    try:
        v = fn(); res[name] = None if v is None else round(now_mjd - v, 2)
    except Exception as e:
        res[name] = f"FAILED {type(e).__name__}"
ages = [v for v in res.values() if isinstance(v, float)]
state = "LIVE" if any(a < 3 for a in ages) else ("DARK" if ages else "UNKNOWN")
line = f"{time.strftime('%Y-%m-%d %H:%M UTC', time.gmtime())}  now MJD {now_mjd:.2f}  latest-alert age (d): {json.dumps(res)}  -> {state}"
open(LOG, "a").write(line + "\n"); print(line)
prev = open(STATE).read().strip() if os.path.exists(STATE) else ""
if os.environ.get("RUBINWATCH_TEST"):  # exercises the alarm branch without touching the state file
    r = subprocess.run(["osascript", "-e", 'display notification "TEST only: the Rubin watch alarm works" with title "Rubin watch (test)"'], check=False); print("test notification exit code", r.returncode); raise SystemExit
if state == "LIVE" and prev != "LIVE":
    subprocess.run(["osascript", "-e", 'display notification "Rubin alert stream is flowing again (see rubin_stream_status.log)" with title "Rubin watch"'], check=False)
if state in ("LIVE", "DARK"): open(STATE, "w").write(state)
