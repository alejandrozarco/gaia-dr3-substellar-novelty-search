"""Daily watch of our TNS objects (2026-09-30). For each object in OBJECTS, the public TNS object page is fetched and reduced to
(1) the classification type, (2) the text of the 'Classification Reports' and 'Comments' sections, (3) the number of AT reports
(table rows). A change against tns_watch_state.json triggers a macOS notification and a line in
tns_watch.log. A failed fetch is logged as HOLE and never counts as a change (state is kept). The first run records the baseline.
Usage: python tns_watch.py   (TNSWATCH_TEST=1 posts a labelled test notification only)."""
import os, re, json, time, hashlib, subprocess, requests
H = os.path.dirname(os.path.abspath(__file__)); ST = os.path.join(H, "tns_watch_state.json"); LOG = os.path.join(H, "tns_watch.log")
OBJECTS = ["2026adjg", "2026adjh", "2026adji", "2026adjj", "2026adjk", "2026adjl", "2026admn", "2026admo", "2026admp", "2026admq", "2026admr"]
def note(msg, title="TNS watch"):
    subprocess.run(["osascript", "-e", f'display notification "{msg}" with title "{title}"'], check=False)
if os.environ.get("TNSWATCH_TEST"): note("TEST only: the TNS watch alarm works", "TNS watch (test)"); raise SystemExit
def summary(name):
    for a in range(3):
        try:
            r = requests.get(f"https://www.wis-tns.org/object/{name}", headers={"User-Agent": "Mozilla/5.0 (literature check)"}, timeout=90)
            if r.status_code == 200 and "Classification Reports" in r.text: break
        except Exception: pass
        time.sleep(30 * (a + 1))
    else: return None
    t = [x.strip() for x in re.sub(r"<[^>]+>", "\n", r.text).splitlines() if x.strip()]
    typ = t[t.index("Type") + 1] if "Type" in t else "?"
    i = t.index("Classification Reports"); j = next((k for k in range(i, len(t)) if t[k].startswith("Copyright")), len(t))
    tail = " | ".join(t[i:j]); n_at = r.text.count("Time received") and len(re.findall(r"<tr[^>]*class=\"[^\"]*row-(?:odd|even)", r.text))
    return dict(type=typ, tail_hash=hashlib.sha1(tail.encode()).hexdigest(), tail=tail[:600], n_rows=n_at)
old = {k: v for k, v in (json.load(open(ST)) if os.path.exists(ST) else {}).items() if not k.startswith("_")}; new = dict(json.load(open(ST))) if os.path.exists(ST) else {}; changes = []; holes = 0; stamp =time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime())
for n in OBJECTS:
    s = summary(n)
    if s is None: open(LOG, "a").write(f"{stamp} {n} HOLE (fetch failed)\n"); holes += 1; continue
    if n in old and (old[n]["type"] != s["type"] or old[n]["tail_hash"] != s["tail_hash"] or old[n]["n_rows"] != s["n_rows"]):
        changes.append(n); open(LOG, "a").write(f"{stamp} {n} CHANGED type {old[n]['type']} -> {s['type']}; rows {old[n]['n_rows']} -> {s['n_rows']}; {s['tail']}\n")
    elif n not in old: open(LOG, "a").write(f"{stamp} {n} baseline type {s['type']}, rows {s['n_rows']}\n")
    new[n] = s; time.sleep(15)
json.dump(new, open(ST, "w"), indent=1); open(LOG, "a").write(f"{stamp} checked {len(OBJECTS)}; changes: {', '.join(changes) or 'none'}\n")
if changes: note(f"Change on {', '.join(changes)} (see tns_watch.log)")
if holes == len(OBJECTS): note("All TNS fetches failed - the TNS watch is blind today", "TNS watch HOLE")
# --- VSX moderation watch (added 2026-09-30): our pending VSX new-star submissions appear in the public VSX catalogue (API cone
# 10 arcsec) once approved. The control AM Her must be returned, else the check is a HOLE. A new entry at a position triggers a
# notification (a slot for the next submission is then free: VSX refuses new submissions while 3 await review).
VSX_PENDING = {"Gaia DR3 5182404743053707904 (ZTF24abfojgu)": (49.256321, -4.365732), "TYC 3477-27-1": (223.469489, 49.946629),
               "2MASS J22342534+0806596": (338.605525, 8.116548)}
def vsx_names(ra, de, rad=10):
    r = requests.get("https://www.aavso.org/vsx/index.php", params=dict(view="api.list", ra=ra, dec=de, radius=rad / 3600, format="json"), timeout=90).json()
    it = r.get("VSXObjects", {}).get("VSXObject", []) if isinstance(r.get("VSXObjects"), dict) else []; it = it if isinstance(it, list) else [it]
    return sorted(x.get("Name") for x in it)
try:
    ok = "AM Her" in vsx_names(274.05458, 49.86778)
except Exception: ok = False
vs = json.load(open(ST)); vold = vs.get("_vsx", {}); vnew = dict(vold); vchg = []
if not ok: open(LOG, "a").write(f"{stamp} VSX HOLE (control AM Her not returned)\n"); note("VSX check failed: control not returned (API blocked?) - the VSX watch is blind today", "VSX watch HOLE")
else:
    for n, (ra, de) in VSX_PENDING.items():
        try: names = vsx_names(ra, de)
        except Exception: open(LOG, "a").write(f"{stamp} VSX {n} HOLE\n"); continue
        if n in vold and names != vold[n]: vchg.append(n); open(LOG, "a").write(f"{stamp} VSX {n} CHANGED {vold[n]} -> {names}\n")
        elif n not in vold: open(LOG, "a").write(f"{stamp} VSX {n} baseline {names}\n")
        vnew[n] = names
    vs["_vsx"] = vnew; json.dump(vs, open(ST, "w"), indent=1); open(LOG, "a").write(f"{stamp} VSX checked {len(VSX_PENDING)} (control ok); changes: {', '.join(vchg) or 'none'}\n")
    if vchg: note(f"VSX entry appeared for {', '.join(vchg)} - moderation done, a submission slot may be free", "VSX watch")
