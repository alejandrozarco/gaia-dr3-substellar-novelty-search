# Slow TNS public cone search (10") with long pauses to respect rate limits; HTTP 429 -> wait and retry (max 4 tries).
import requests, time, io, pandas as pd, json
m = pd.read_csv("master.csv")
ids = [2002597083798483200, 1977447164064222976, 6703736482047069696, 6403339013297801216, 5362131777028219904, 5568642355890359168,
       4679467096349698048, 1969629915562515072, 4784897896243243392, 5664935458242923392, 5931744839753122944]
res = json.load(open("tns_key.json"))
for g in ids:
    if isinstance(res.get(str(g)), list): continue
    r = m[m.gaia_dr3_source_id == g].iloc[0]
    url = f"https://www.wis-tns.org/search?ra={r.ra_g:.6f}&decl={r.dec_g:.6f}&radius=10&coords_unit=arcsec&format=csv"
    for k in range(4):
        q = requests.get(url, headers={"User-Agent": "Mozilla/5.0 (research script)"}, timeout=60)
        if q.status_code == 200 and q.text.startswith('"ID"'):
            d = pd.read_csv(io.StringIO(q.text)); res[str(g)] = [(x["Name"], str(x["Obj. Type"]), x["Discovery Date (UT)"]) for _, x in d.iterrows()]; break
        res[str(g)] = f"HOLE HTTP {q.status_code}"; time.sleep(120)
    print(g, res[str(g)], flush=True); json.dump(res, open("tns_key.json", "w"), indent=1); time.sleep(45)
print("DONE")
