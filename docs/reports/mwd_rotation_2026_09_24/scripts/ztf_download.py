# Download ZTF DR24 light curves (IRSA API, COLLECTION=ztf_dr24, g,r,i) within 5" of each star (target + blends) -> ztf/<sid>.csv
import json, time, requests, os, sys, csv, io
T = json.load(open("data/targets.json")) + json.load(open("data/controls.json"))
log = open("logs/ztf_download.log", "a")
for rec in T:
    sid = rec["source_id"]; ra = float(rec["ra"]); dec = float(rec["dec"])
    if dec < -31: print(sid, "dec %.1f: outside ZTF sky, skipped" % dec); continue
    if sid == "1980205739970324224": print(sid, "J2159: existing analysis, not redone"); continue
    fn = f"ztf/{sid}.csv"
    if os.path.exists(fn) and os.path.getsize(fn) > 200: print(sid, "exists"); continue
    url = (f"https://irsa.ipac.caltech.edu/cgi-bin/ZTF/nph_light_curves?POS=CIRCLE%20{ra:.6f}%20{dec:.6f}%200.0014"
           "&BANDNAME=g,r,i&FORMAT=csv&COLLECTION=ztf_dr24")
    for attempt in range(3):
        try:
            r = requests.get(url, timeout=300)
        except Exception as e:
            print(sid, "EXC", e); time.sleep(10); continue
        if r.status_code == 200 and r.text.startswith("oid,"): break
        print(sid, "HTTP", r.status_code, r.text[:200].replace("\n", " ")); time.sleep(15)
    else:
        print(sid, "HOLE: download failed"); log.write(f"{sid} HOLE\n"); continue
    open(fn, "w").write(r.text)
    R = list(csv.DictReader(io.StringIO(r.text)))
    from collections import Counter
    c = Counter((x["oid"], x["filtercode"]) for x in R)
    msg = f"{sid} rows {len(R)} oids {len(c)} " + " ".join(f"{k[1]}:{v}" for k, v in sorted(c.items(), key=lambda z: -z[1])[:8])
    print(msg); log.write(msg + "\n"); log.flush()
    time.sleep(3)
