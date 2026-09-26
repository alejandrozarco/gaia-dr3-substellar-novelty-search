# Batch ATLAS forced photometry for Gaia DR3 sources (positions propagated to 2020.5). Usage: python atlas_batch.py id1 id2 ...
# Submits all tasks, then polls; writes atlas_<id>.txt. Token read from ~/.config/atlas/token (never printed).
import os, sys, time, io, requests, numpy as np, pandas as pd
BASE = "https://fallingstar-data.com/forcedphot"; H = {"Authorization": "Token " + open(os.path.expanduser("~/.config/atlas/token")).read().strip(), "Accept": "application/json"}
ids = [i for i in sys.argv[1:] if not os.path.exists(f"atlas_{i}.txt")]
q = "SELECT source_id, ra, dec, pmra, pmdec FROM gaiadr3.gaia_source WHERE source_id IN (" + ",".join(ids) + ")"
g = pd.read_csv(io.StringIO(requests.post("https://gea.esac.esa.int/tap-server/tap/sync", data=dict(REQUEST="doQuery", LANG="ADQL", FORMAT="csv", QUERY=q), timeout=300).text), dtype={"source_id": str}).set_index("source_id")
urls = {}
for i in ids:
    r = g.loc[i]; dt = 4.5; pmra = 0 if np.isnan(r.pmra) else r.pmra; pmde = 0 if np.isnan(r.pmdec) else r.pmdec
    ra = r.ra + pmra * dt / 3.6e6 / np.cos(np.radians(r.dec)); de = r.dec + pmde * dt / 3.6e6
    for k in range(10):
        x = requests.post(f"{BASE}/queue/", headers=H, data={"ra": ra, "dec": de, "mjd_min": 57000.0, "send_email": False}, timeout=60)
        if x.status_code == 201: urls[i] = x.json()["url"]; print("queued", i, flush=True); break
        print("queue refused", i, x.status_code, flush=True); time.sleep(60)
    time.sleep(3)
while urls:
    for i, url in list(urls.items()):
        try: j = requests.get(url, headers=H, timeout=60).json()
        except Exception as e: print("poll error", i, str(e)[:80], flush=True); continue
        if j.get("finishtimestamp"):
            txt = requests.get(j["result_url"], headers=H, timeout=120).text if j.get("result_url") else ""
            requests.delete(url, headers=H, timeout=60); open(f"atlas_{i}.txt", "w").write(txt); print("done", i, len(txt.splitlines()), "lines", flush=True); del urls[i]
    time.sleep(20)
print("ALL DONE", flush=True)
