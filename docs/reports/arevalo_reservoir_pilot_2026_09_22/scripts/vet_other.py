"""SIMBAD (TAP, 6"), ALeRCE ZTF objects (3") + classifier labels, ADS full text on every designation.
A failed query prints HOLE; an empty successful query prints 0."""
import json, os, subprocess, urllib.parse, csv, io, time
A = "/private/tmp/claude-501/-Users-USER-claude-projects/5bae4473-7497-4a6b-8bf6-3ecc9abd4295/scratchpad/arev"
V = {k.strip(): v for k, v in json.load(open(f"{A}/vet_cone.json")).items()}
TOK = open(os.path.expanduser("~/.config/ads/token")).read().strip()
def get(url, hdr=None, t=90):
    cmd = ["curl", "-sL", "--max-time", str(t), "-w", "\n%{http_code}"]
    for h in (hdr or []): cmd += ["-H", h]
    p = subprocess.run(cmd + [url], capture_output=True, text=True)
    body, _, code = p.stdout.rpartition("\n")
    return body, code
out = {}
for sid in ("AREV_747_000417_zg_c05_q1", "AREV_1918_000493_zg_c16_q4", "AREV_990_000495_zg_c14_q3",
            "AREV_2445_000482_zg_c04_q4", "AREV_3471_000536_zg_c13_q2"):
    r = V[sid]; ra, dec = r["ra"], r["dec"]; rec = {}
    # names from the cone rows
    names = set()
    for t in r["tables"]:
        row = t["row"]
        if t["table"] == "I/355/gaiadr3": names.add("Gaia DR3 " + row.get("Source", "")); rec["dr3"] = row.get("Source")
        if t["table"] == "I/345/gaia2": names.add("Gaia DR2 " + row.get("Source", ""))
        if t["table"] == "II/246/out": names.add("2MASS J" + row.get("2MASS", ""))
        if t["table"] == "II/328/allwise": names.add("WISEA " + row.get("AllWISE", "").replace("J", "J", 1))
    # SIMBAD TAP
    q = ("SELECT main_id, otype, ra, dec FROM basic WHERE CONTAINS(POINT('ICRS',ra,dec),"
         f"CIRCLE('ICRS',{ra},{dec},{6/3600}))=1")
    body, code = get("https://simbad.cds.unistra.fr/simbad/sim-tap/sync?request=doQuery&lang=adql&format=csv&query=" + urllib.parse.quote(q))
    if code == "200" and body.startswith("main_id"):
        rows = list(csv.DictReader(io.StringIO(body))); rec["simbad"] = [(x["main_id"], x["otype"]) for x in rows]
        for x in rows: names.add(x["main_id"])
    else:
        rec["simbad"] = f"HOLE http={code} {body[:80]!r}"
    # ALeRCE
    body, code = get(f"https://api.alerce.online/ztf/v1/objects?ra={ra}&dec={dec}&radius=3&page_size=20")
    if code == "200":
        items = json.loads(body).get("items", []); rec["alerce"] = []
        for it in items:
            oid = it["oid"]; names.add(oid)
            b2, c2 = get(f"https://api.alerce.online/ztf/v1/objects/{oid}/probabilities")
            labs = []
            if c2 == "200":
                for pr in json.loads(b2):
                    if pr.get("ranking") == 1: labs.append(f"{pr['classifier_name']}:{pr['class_name']}({pr['probability']:.2f})")
            else: labs = [f"HOLE http={c2}"]
            rec["alerce"].append(dict(oid=oid, ndet=it.get("ndet"), labels=labs))
    else:
        rec["alerce"] = f"HOLE http={code}"
    # ADS full text, every designation
    rec["ads"] = {}
    for n in sorted(names):
        if not n or n.endswith(" "): continue
        qq = f'full:"{n}"'
        body, code = get("https://api.adsabs.harvard.edu/v1/search/query?" + urllib.parse.urlencode({"q": qq, "fl": "bibcode,title", "rows": 10}),
                         hdr=[f"Authorization: Bearer {TOK}"])
        if code == "200":
            d = json.loads(body)["response"]; rec["ads"][n] = [(x["bibcode"], (x.get("title") or [""])[0][:70]) for x in d["docs"]] if d["numFound"] else 0
        else:
            rec["ads"][n] = f"HOLE http={code}"
        time.sleep(0.4)
    out[sid] = rec
    print(f"### {sid}  DR3 {rec.get('dr3')}", flush=True)
    print(f"  SIMBAD 6\": {rec['simbad']}", flush=True)
    print(f"  ALeRCE 3\": {rec['alerce']}", flush=True)
    for n, v in rec["ads"].items(): print(f"  ADS {n}: {v}", flush=True)
json.dump(out, open(f"{A}/vet_other.json", "w"), indent=1)
