# SIMBAD identifiers + bibcodes (with titles) for each target, via TAP. Failed queries are recorded as HOLE.
import json, time, requests, sys
targets = [l.split()[0] for l in open(sys.argv[1]) if l.strip() and not l.startswith("#")]
out = {}
def tap(adql):
    for k in range(3):
        try:
            r = requests.post("https://simbad.cds.unistra.fr/simbad/sim-tap/sync", data=dict(REQUEST="doQuery", LANG="ADQL", FORMAT="json", QUERY=adql), timeout=90)
            if r.status_code == 200: return r.json()["data"]
            err = f"HTTP {r.status_code}: {r.text[:200]}"
        except Exception as e: err = str(e)
        time.sleep(3)
    print("HOLE", err); return None
for g in targets:
    ids = tap(f"SELECT i2.id FROM ident AS i1 JOIN ident AS i2 ON i1.oidref = i2.oidref WHERE i1.id = 'Gaia DR3 {g}'")
    refs = tap(f"SELECT b.bibcode, b.title FROM ident AS i1 JOIN has_ref AS h ON h.oidref = i1.oidref JOIN ref AS b ON b.oidbib = h.oidbibref WHERE i1.id = 'Gaia DR3 {g}'")
    out[g] = dict(ids=None if ids is None else sorted(x[0] for x in ids), refs=None if refs is None else sorted([x[0], x[1]] for x in refs))
    print(g, "ids", None if ids is None else len(ids), "refs", None if refs is None else len(refs), flush=True)
    time.sleep(0.5)
json.dump(out, open(sys.argv[2], "w"), indent=1)
