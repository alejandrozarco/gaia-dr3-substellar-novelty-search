# Minimal SIMBAD TAP helper (POST sync, JSON). Returns (cols, rows) or raises on failure -> caller records HOLE.
import requests, time
URL = "https://simbad.cds.unistra.fr/simbad/sim-tap/sync"
def tap(adql, maxrec=200000, tries=3, timeout=300):
    err = None
    for k in range(tries):
        try:
            r = requests.post(URL, data=dict(REQUEST="doQuery", LANG="ADQL", FORMAT="json", QUERY=adql, MAXREC=maxrec), timeout=timeout)
            if r.status_code == 200:
                j = r.json(); return [c["name"] for c in j["metadata"]], j["data"]
            err = f"HTTP {r.status_code}: {r.text[:300]}"
        except Exception as e:
            err = repr(e)
        time.sleep(5)
    raise RuntimeError("SIMBAD TAP HOLE: " + str(err))
