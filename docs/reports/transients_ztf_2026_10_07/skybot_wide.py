"""SkyBoT re-query (radius 0.3 deg, I41) for objects whose 15-arcsec cone returned empty/SIGBUS (skybot.csv HOLE), 2026-10-01.
A valid wide reply lists the nearest known object; nearest > 15 arcsec = no known asteroid at the transient. Output: skybot_wide.csv"""
import requests, time, pandas as pd, numpy as np
k = pd.read_csv("skybot.csv"); S = pd.read_csv("screen1.csv").set_index("oid"); rows = []
for o in k[k.n_known.astype(str) == "HOLE"].oid:
    r = S.loc[o]; res = dict(oid=o, status="HOLE")
    for a in range(3):
        try:
            x = requests.get("https://ssp.imcce.fr/webservices/skybot/api/conesearch.php", params={"-ep": r["first"] + 2400000.5, "-ra": r.ra, "-dec": r.dec, "-rd": 0.3, "-mime": "text", "-output": "basic", "-loc": "I41", "-filter": "0", "-objFilter": "111", "-refsys": "EQJ2000", "-from": "hobby"}, timeout=180)
            if "# Flag: 1" in x.text:
                L = [l.split("|") for l in x.text.splitlines() if l and not l.startswith("#")]
                d = sorted((float(f[7]), f[1].strip(), f[5].strip()) for f in L); res = dict(oid=o, status="ok", n=len(L), nearest_as=d[0][0], nearest=f"{d[0][1]} V{d[0][2]}"); break
            if x.ok and x.text.strip() == "": res = dict(oid=o, status="empty-0.3deg"); break
        except Exception: pass
        time.sleep(10)
    rows.append(res); print(res, flush=True)
pd.DataFrame(rows).to_csv("skybot_wide.csv", index=False)
