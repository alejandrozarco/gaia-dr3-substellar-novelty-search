#!/usr/bin/env python
"""Retry: LS DR10 tractor + NSC DR2 via Data Lab sync TAP (raw HTTP), PS1 via csv."""
import io, json, requests
import numpy as np
import pandas as pd
from astropy.coordinates import SkyCoord

RA, DEC = 332.39126, -14.8699
co = SkyCoord(RA, DEC, unit="deg")
out = {}

def sep(ra, dec):
    return co.separation(SkyCoord(np.asarray(ra, float), np.asarray(dec, float), unit="deg")).arcsec

def dl_query(q):
    r = requests.get("https://datalab.noirlab.edu/tap/sync",
                     params={"REQUEST": "doQuery", "LANG": "ADQL", "FORMAT": "csv", "QUERY": q},
                     timeout=180)
    r.raise_for_status()
    if r.text.startswith("<"):
        raise RuntimeError(r.text[:300])
    return pd.read_csv(io.StringIO(r.text))

R = 30.0 / 3600.0
try:
    t = dl_query(f"""SELECT ra, dec, type, mag_g, mag_r, mag_i, mag_z, mag_w1, shape_r
        FROM ls_dr10.tractor WHERE q3c_radial_query(ra, dec, {RA}, {DEC}, {R})""")
    t["sep_as"] = sep(t.ra, t.dec) if len(t) else []
    out["ls_dr10"] = t.sort_values("sep_as").to_dict("records")
except Exception as e:
    out["ls_dr10"] = f"ERROR: {e}"

try:
    t = dl_query(f"""SELECT id, ra, dec, ndet, gmag, rmag, imag, zmag, grms, rrms, irms, zrms, deltamjd
        FROM nsc_dr2.object WHERE q3c_radial_query(ra, dec, {RA}, {DEC}, {R})""")
    t["sep_as"] = sep(t.ra, t.dec) if len(t) else []
    out["nsc_dr2_object"] = t.sort_values("sep_as").to_dict("records")
except Exception as e:
    out["nsc_dr2_object"] = f"ERROR: {e}"

try:
    t = dl_query(f"""SELECT objectid, mjd, filter, mag_auto, magerr_auto, ra, dec
        FROM nsc_dr2.meas WHERE q3c_radial_query(ra, dec, {RA}, {DEC}, {3.0/3600.})""")
    out["nsc_dr2_meas_3as"] = t.sort_values("mjd").to_dict("records")
except Exception as e:
    out["nsc_dr2_meas_3as"] = f"ERROR: {e}"

# PS1 DR2 mean via csv
try:
    r = requests.get("https://catalogs.mast.stsci.edu/api/v0.1/panstarrs/dr2/mean.csv",
                     params={"ra": RA, "dec": DEC, "radius": R,
                             "columns": "[objName,raMean,decMean,nDetections,gMeanPSFMag,rMeanPSFMag,iMeanPSFMag,zMeanPSFMag,yMeanPSFMag]",
                             "pagesize": 50}, timeout=120)
    t = pd.read_csv(io.StringIO(r.text))
    t["sep_as"] = sep(t.raMean, t.decMean) if len(t) else []
    out["ps1_dr2_mean"] = t.sort_values("sep_as").to_dict("records")
except Exception as e:
    out["ps1_dr2_mean"] = f"ERROR: {e} :: {r.text[:200] if 'r' in dir() else ''}"

json.dump(out, open("/tmp/rubin_pilot/forensics/170635519425249637/catalogs2.json", "w"),
          default=str, indent=1)
for k, v in out.items():
    if isinstance(v, str):
        print(k, "->", v[:300])
    else:
        print(f"== {k}: {len(v)} rows")
        for row in v[:6]:
            print("  ", json.dumps(row, default=str)[:320])
