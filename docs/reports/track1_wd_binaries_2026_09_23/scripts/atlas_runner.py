"""Resumable ATLAS forced-photometry runner for the southern track-1 pool.
State in atlas_state.json: per target -> task url / status. Keeps up to MAXQ tasks queued; collects finished ones;
tasks older than 6 h without finishing are recorded as HOLE_TIMEOUT (not nulls). Token never printed."""
import json, os, time, requests, math
exec(open("atlas_screen.py").read().split("todo = [o for o in south")[0])   # reuse pool, queue(), analyse()
STATE = "atlas_state.json"; MAXQ = 8
st = json.load(open(STATE)) if os.path.exists(STATE) else {}
# adopt tasks already sitting in the ATLAS queue (match by position)
r = requests.get(f"{BASE}/queue/", headers=H, timeout=60); existing = r.json().get("results", []) if r.status_code == 200 else []
for t in existing:
    for o in south:
        if o["sid"] not in st and abs(t["ra"] - o["ra"]) < 1e-5 and abs(t["dec"] - o["dec"]) < 1e-5:
            st[o["sid"]] = dict(url=t["url"], queued=time.time(), status="QUEUED")
json.dump(st, open(STATE, "w"))
res = {o["sid"]: o for o in json.load(open("atlas_screen.json"))} if os.path.exists("atlas_screen.json") else {}
bysid = {o["sid"]: o for o in south}
while True:
    active = [s for s, v in st.items() if v["status"] == "QUEUED"]
    for s in active:
        v = st[s]; rr = requests.get(v["url"], headers=H, timeout=60)
        if rr.status_code != 200: continue
        j = rr.json()
        if j.get("finishtimestamp"):
            o = bysid[s]
            if j.get("result_url"):
                txt = requests.get(j["result_url"], headers=H, timeout=120).text; o["atlas"] = "OK" if txt.strip() else "NO_DATA"
                if txt.strip():
                    try: analyse(o, txt)
                    except Exception as e: o["atlas"] = f"ERROR {type(e).__name__}"
            else: o["atlas"] = "NO_DATA"
            requests.delete(v["url"], headers=H, timeout=60); v["status"] = "DONE"; res[s] = o
            if o.get("verdict", "none") != "none":
                print(f"  {o['verdict']:15s} {s} {o['name']} G={o['G']:.2f} M_G={o['MG']:.2f} dRidge={o['d_ridge']:+.2f} eRASS1={o['in_erass1']} | " +
                      " ".join(f"{k}: P={b['P']} d ({b['P']*24:.3f} h) pow {b['power']}/{b['alias']} amp {b['amp']}" for k, b in o["bands"].items()), flush=True)
        elif time.time() - v["queued"] > 6 * 3600:
            v["status"] = "HOLE_TIMEOUT"; bysid[s]["atlas"] = "HOLE_TIMEOUT"; res[s] = bysid[s]
    todo = [o for o in south if o["sid"] not in st]
    while todo and sum(1 for v in st.values() if v["status"] == "QUEUED") < MAXQ:
        o = todo.pop(0); u = queue(o)
        st[o["sid"]] = dict(url=u, queued=time.time(), status="QUEUED" if u else "HOLE_QUEUE")
        if not u: o["atlas"] = "HOLE_QUEUE"; res[o["sid"]] = o
    json.dump(st, open(STATE, "w")); json.dump(list(res.values()), open("atlas_screen.json", "w"), default=str)
    n_done = sum(1 for v in st.values() if v["status"] != "QUEUED")
    print(f"{time.strftime('%H:%M:%S')} done {n_done}/{len(south)}, queued {sum(1 for v in st.values() if v['status']=='QUEUED')}", flush=True)
    if n_done >= len(south): break
    time.sleep(120)
print("ATLAS_RUNNER_DONE", sum(o.get("verdict") == "COHERENT_2BAND" for o in res.values()), "two-band,",
      sum(o.get("verdict") == "COHERENT_1BAND" for o in res.values()), "one-band", flush=True)
