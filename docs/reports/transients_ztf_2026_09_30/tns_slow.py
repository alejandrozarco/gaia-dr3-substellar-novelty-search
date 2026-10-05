"""Slow TNS cone (10 arcsec) for every candidate in vetted.csv: one request per 20 s, 5-min pause on HTTP 429.
Writes tns_results.csv (oid, tns) incrementally; resumable. 'HOLE' = no valid answer after 6 tries."""
import pandas as pd, requests, time, io, os
V = pd.read_csv("tns_queue.csv").sort_values("pri", kind="stable"); done = set(pd.read_csv("tns_results.csv").oid) if os.path.exists("tns_results.csv") else set()
for r in V.itertuples():
    if r.oid in done: continue
    res = "HOLE"
    for a in range(6):
        try:
            q = requests.get("https://www.wis-tns.org/search", params=dict(ra=r.meanra, decl=r.meandec, radius=10, coords_unit="arcsec", format="csv"), headers={"User-Agent": "Mozilla/5.0 (literature check)"}, timeout=60)
            if q.status_code == 429: time.sleep(300); continue
            if q.ok and q.text.startswith('"ID"'):
                d = pd.read_csv(io.StringIO(q.text)); res = "; ".join(f"{x.Name} {x['Obj. Type']}" for _, x in d.iterrows()) or "none"; break
        except Exception: time.sleep(30)
    pd.DataFrame([dict(oid=r.oid, tns=res)]).to_csv("tns_results.csv", mode="a", header=not os.path.exists("tns_results.csv"), index=False)
    print(r.oid, res, flush=True); time.sleep(20)
print("ALL-DONE", flush=True)
