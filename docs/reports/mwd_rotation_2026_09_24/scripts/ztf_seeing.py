# Per-epoch seeing (FWHM), moon illumination and sky excess for a star's ZTF epochs from IRSA ztf.ztf_current_meta_sci (public TAP)
import sys, json, csv, io, requests, time
sys.path.insert(0, 'scripts'); import rotlib as RL
sid = sys.argv[1]
META = {r["source_id"]: r for r in json.load(open("data/targets.json")) + json.load(open("data/controls.json"))}
rec = META[sid]; rows, by = RL.read_oids(f"ztf/{sid}.csv"); ot = RL.oid_table(by, rec); tset = set(o["oid"] for o in ot if o["sep"] < 1.5)
R = [r for r in rows if r["oid"] in tset and int(r["catflags"]) == 0]
keys = sorted(set((int(r["expid"]), int(r["field"]), int(r["ccdid"], 16) if r["ccdid"].startswith("0x") else int(r["ccdid"]), int(r["qid"], 16) if r["qid"].startswith("0x") else int(r["qid"])) for r in R))
print(sid, "epochs", len(keys))
out = {}
for i in range(0, len(keys), 150):
    chunk = keys[i:i + 150]
    ex = ",".join(str(k[0]) for k in chunk)
    q = (f"SELECT expid, field, ccdid, qid, seeing, moonillf, moonesb, maglimit, airmass FROM ztf.ztf_current_meta_sci "
         f"WHERE expid IN ({ex}) AND ccdid = {chunk[0][2]} AND qid = {chunk[0][3]}") if len(set((k[2], k[3]) for k in chunk)) == 1 else \
        (f"SELECT expid, field, ccdid, qid, seeing, moonillf, moonesb, maglimit, airmass FROM ztf.ztf_current_meta_sci WHERE expid IN ({ex})")
    t0 = time.time()
    r = requests.post("https://irsa.ipac.caltech.edu/TAP/sync", data=dict(LANG="ADQL", FORMAT="csv", QUERY=q), timeout=900)
    if r.status_code != 200: print("HOLE HTTP", r.status_code, r.text[:200]); continue
    L = list(csv.DictReader(io.StringIO(r.text)))
    for x in L:
        out[f"{x['expid']}_{x['ccdid']}_{x['qid']}"] = x
    print(f"chunk {i}: {len(L)} rows in {time.time()-t0:.0f}s", flush=True)
json.dump(out, open(f"data/seeing_{sid}.json", "w"))
print("total matched", len(out))
