#!/usr/bin/env python
"""Referee: independent re-pull of Fink/LSST photometry for diaObject 170591507978387512,
MJD-keyed asserts against the claimed photometry_jd_keyed.csv rows."""
import json, math, sys
import requests
import pandas as pd
import numpy as np

DIA = "170591507978387512"
BASE = "https://api.lsst.fink-portal.org"

r_obj = requests.post(f"{BASE}/api/v1/objects",
                      json={"diaObjectId": DIA, "output-format": "json"}, timeout=60)
print("objects status:", r_obj.status_code)
obj = r_obj.json()
with open("/tmp/rubin_pilot/forensics/referee_512b/fink_obj.json", "w") as f:
    json.dump(obj, f, indent=1)

r_src = requests.post(f"{BASE}/api/v1/sources",
                      json={"diaObjectId": DIA, "output-format": "json"}, timeout=60)
print("sources status:", r_src.status_code)
src = r_src.json()
with open("/tmp/rubin_pilot/forensics/referee_512b/fink_sources.json", "w") as f:
    json.dump(src, f, indent=1)

df = pd.DataFrame(src)
print("n sources:", len(df))
print("columns:", sorted(df.columns.tolist()))
sys.stdout.flush()

# figure out flux columns
cols = [c for c in df.columns if 'Flux' in c or 'flux' in c]
print("flux-ish cols:", cols)
keep = [c for c in ['diaSourceId','midpointMjdTai','band','psfFlux','psfFluxErr',
                    'scienceFlux','scienceFluxErr','snr','reliability','ra','dec',
                    'visit','detector','pixelFlags'] if c in df.columns]
print(df[keep].to_string())
