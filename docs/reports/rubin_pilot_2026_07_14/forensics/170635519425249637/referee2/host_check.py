#!/usr/bin/env python
"""Referee: independent host check. Live PS1 DR2 stack cone, live Legacy DR10 TAP cone,
i-band-only coverage claim, and separations computed myself."""
import requests, numpy as np, json

RA, DEC = 332.391259, -14.869900

def sep_as(ra1, dec1, ra2, dec2):
    dra = (np.asarray(ra2) - ra1) * np.cos(np.radians(dec1)) * 3600
    ddec = (np.asarray(dec2) - dec1) * 3600
    return np.hypot(dra, ddec)

# --- PS1 DR2 stack, live MAST ---
u = "https://catalogs.mast.stsci.edu/api/v0.1/panstarrs/dr2/stack.json"
r = requests.get(u, params=dict(ra=RA, dec=DEC, radius=5/3600.,
    columns="objID,objName,raStack,decStack,gPSFMag,gPSFMagErr,rPSFMag,rPSFMagErr,iPSFMag,iPSFMagErr,zPSFMag,zPSFMagErr,yPSFMag,yPSFMagErr,primaryDetection,nDetections"), timeout=60)
print("PS1 stack HTTP", r.status_code)
d = r.json()["data"]
print("PS1 stack rows within 5\":", len(d))
for row in d:
    m = dict(zip([c["name"] for c in r.json()["info"]], row)) if "info" in r.json() else None
# simpler: get column names
cols = [c["name"] for c in r.json()["info"]]
for row in d:
    m = dict(zip(cols, row))
    s = sep_as(RA, DEC, m["raStack"], m["decStack"])
    print(f"  {m['objName']} objID={m['objID']} sep={float(s):.2f}\" prim={m['primaryDetection']} nDet={m['nDetections']}")
    print(f"    g={m['gPSFMag']}+-{m['gPSFMagErr']} r={m['rPSFMag']}+-{m['rPSFMagErr']} i={m['iPSFMag']}+-{m['iPSFMagErr']} z={m['zPSFMag']}+-{m['zPSFMagErr']} y={m['yPSFMag']}+-{m['yPSFMagErr']}")

# --- Legacy Survey DR10 via Data Lab TAP (anonymous) ---
q = f"""SELECT ra,dec,type,flux_g,flux_r,flux_i,flux_z,nobs_g,nobs_r,nobs_i,nobs_z,
q3c_dist(ra,dec,{RA},{DEC})*3600 as sep_as FROM ls_dr10.tractor
WHERE q3c_radial_query(ra,dec,{RA},{DEC},30.0/3600) ORDER BY sep_as"""
r2 = requests.get("https://datalab.noirlab.edu/tap/sync",
                  params=dict(REQUEST="doQuery", LANG="ADQL", FORMAT="csv", QUERY=q), timeout=120)
print("\nLS DR10 TAP HTTP", r2.status_code)
print(r2.text[:2000])
