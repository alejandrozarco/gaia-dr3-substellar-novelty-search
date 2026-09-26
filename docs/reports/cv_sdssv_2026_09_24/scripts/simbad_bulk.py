# SIMBAD TAP bulk lookup by 'Gaia DR3 <id>' identifier: main_id, otype, all other_types, nbref. Failed chunks -> HOLE.
import pandas as pd, requests, time, json
sw = pd.read_csv("sw_cv_x2.csv")
ids = [str(int(x)) for x in sw.gaia_dr3_source_id if x > 0]
res = {}; holes = []
def tap(q):
    for k in range(3):
        try:
            r = requests.post("https://simbad.cds.unistra.fr/simbad/sim-tap/sync", data=dict(REQUEST="doQuery", LANG="ADQL", FORMAT="json", QUERY=q), timeout=180)
            if r.status_code == 200: return r.json()
            err = f"HTTP {r.status_code} {r.text[:200]}"
        except Exception as e: err = str(e)
        time.sleep(5)
    print("HOLE", err); return None
for i in range(0, len(ids), 150):
    ch = ids[i:i + 150]
    q = ("SELECT i1.id, b.main_id, b.otype, b.nbref, b.sp_type FROM ident AS i1 JOIN basic AS b ON b.oid = i1.oidref WHERE i1.id IN (" +
         ",".join(f"'Gaia DR3 {g}'" for g in ch) + ")")
    j = tap(q)
    if j is None: holes += ch; continue
    for row in j["data"]:
        res[row[0].replace("Gaia DR3 ", "")] = dict(main_id=row[1], otype=row[2], nbref=row[3], sp_type=row[4], all_otypes=[])
    q2 = ("SELECT i1.id, o.otype FROM ident AS i1 JOIN otypes AS o ON o.oidref = i1.oidref WHERE i1.id IN (" + ",".join(f"'Gaia DR3 {g}'" for g in ch) + ")")
    j2 = tap(q2)
    if j2 is None: holes += [f"otypes:{g}" for g in ch]
    else:
        for row in j2["data"]:
            k = row[0].replace("Gaia DR3 ", "")
            if k in res: res[k]["all_otypes"].append(row[1])
    print(i, len(j["data"]), flush=True); time.sleep(1)
json.dump(dict(found=res, holes=holes, n_queried=len(ids)), open("simbad_bulk.json", "w"), indent=1)
print("found", len(res), "of", len(ids), "holes", len(holes))
from collections import Counter
print(Counter(v["otype"] for v in res.values()).most_common(30))
