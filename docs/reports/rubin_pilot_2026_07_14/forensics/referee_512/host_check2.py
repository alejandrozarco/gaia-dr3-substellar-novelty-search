#!/usr/bin/env python
"""Referee: independent LS DR10 host check via legacysurvey.org viewer catalog API (NERSC)."""
import urllib.request, json, math

RA, DEC = 313.2265057, -14.8404352
half = 10.0 / 3600.0
url = ("https://www.legacysurvey.org/viewer/cat.json?"
       f"ralo={RA-half/math.cos(math.radians(DEC))}&rahi={RA+half/math.cos(math.radians(DEC))}"
       f"&declo={DEC-half}&dechi={DEC+half}&layer=ls-dr10")
req = urllib.request.Request(url, headers={"User-Agent": "referee-check/1.0"})
with urllib.request.urlopen(req, timeout=120) as r:
    cat = json.loads(r.read().decode())

rds = cat.get("rd", [])
print(f"n sources in ±10\" box: {len(rds)}")
for k in cat:
    pass
keys = [k for k in cat.keys() if k != "rd"]
print("fields:", keys)
for idx, (ra2, dec2) in enumerate(rds):
    dra = (ra2 - RA) * math.cos(math.radians(DEC)) * 3600
    ddec = (dec2 - DEC) * 3600
    sep = math.hypot(dra, ddec)
    info = {k: (cat[k][idx] if isinstance(cat[k], list) and len(cat[k]) == len(rds) else None) for k in keys}
    print(f"--- src {idx}: sep={sep:.3f}\" ra={ra2:.6f} dec={dec2:.6f}")
    print("   ", {k: v for k, v in info.items() if v is not None})
