#!/usr/bin/env python
"""Archival catalog cone searches around the transient position."""
import json, io, sys
import requests
import pandas as pd
import numpy as np

RA, DEC = 313.22651, -14.84044
D = "/tmp/rubin_pilot/forensics/170591507978387512"
out = {}

def sep_arcsec(ra, dec):
    return np.hypot((np.asarray(ra) - RA) * np.cos(np.radians(DEC)), np.asarray(dec) - DEC) * 3600.0

# ---------- Gaia DR3 (ESA TAP sync), 15" ----------
adql = f"""SELECT source_id, ra, dec, parallax, parallax_error, pmra, pmdec,
phot_g_mean_mag, phot_bp_mean_mag, phot_rp_mean_mag, phot_variable_flag, ruwe,
DISTANCE(POINT('ICRS', ra, dec), POINT('ICRS', {RA}, {DEC}))*3600 AS sep_as
FROM gaiadr3.gaia_source
WHERE 1=CONTAINS(POINT('ICRS', ra, dec), CIRCLE('ICRS', {RA}, {DEC}, 15.0/3600))
ORDER BY sep_as"""
r = requests.post("https://gea.esac.esa.int/tap-server/tap/sync",
                  data={"REQUEST": "doQuery", "LANG": "ADQL", "FORMAT": "csv", "QUERY": adql}, timeout=120)
gaia = pd.read_csv(io.StringIO(r.text))
print("=== Gaia DR3 within 15\" ==="); print(gaia.to_string(index=False) if len(gaia) else "EMPTY")
gaia.to_csv(f"{D}/cat_gaia_dr3.csv", index=False)

# ---------- Datalab TAP: LS DR10 tractor + NSC DR2 object, 15" ----------
def datalab(q, name):
    r = requests.get("https://datalab.noirlab.edu/tap/sync",
                     params={"REQUEST": "doQuery", "LANG": "ADQL", "FORMAT": "csv", "QUERY": q}, timeout=180)
    if r.status_code != 200 or r.text.startswith("<"):
        print(f"{name}: HTTP {r.status_code} err {r.text[:300]}"); return pd.DataFrame()
    df = pd.read_csv(io.StringIO(r.text))
    return df

q_ls = f"""SELECT ls_id, ra, dec, type, mag_g, mag_r, mag_i, mag_z, mag_w1, mag_w2,
flux_g, flux_r, flux_z, psfsize_r, ebv,
q3c_dist(ra, dec, {RA}, {DEC})*3600 AS sep_as
FROM ls_dr10.tractor
WHERE q3c_radial_query(ra, dec, {RA}, {DEC}, 15.0/3600) ORDER BY sep_as"""
ls = datalab(q_ls, "LS DR10")
print("\n=== Legacy Survey DR10 tractor within 15\" ==="); print(ls.to_string(index=False) if len(ls) else "EMPTY")
ls.to_csv(f"{D}/cat_lsdr10.csv", index=False)

q_nsc = f"""SELECT id, ra, dec, gmag, rmag, imag, zmag, umag, vrmag,
grms, rrms, irms, zrms, ndet, nphot, deltamjd, mjd,
q3c_dist(ra, dec, {RA}, {DEC})*3600 AS sep_as
FROM nsc_dr2.object
WHERE q3c_radial_query(ra, dec, {RA}, {DEC}, 15.0/3600) ORDER BY sep_as"""
nsc = datalab(q_nsc, "NSC DR2")
print("\n=== NOIRLab Source Catalog DR2 within 15\" ==="); print(nsc.to_string(index=False) if len(nsc) else "EMPTY")
nsc.to_csv(f"{D}/cat_nsc_dr2.csv", index=False)

# ---------- PS1 DR2 mean objects, 15" ----------
r = requests.get("https://catalogs.mast.stsci.edu/api/v0.1/panstarrs/dr2/mean.csv",
                 params={"ra": RA, "dec": DEC, "radius": 15.0/3600,
                         "columns": "[objID,raMean,decMean,nDetections,gMeanPSFMag,rMeanPSFMag,iMeanPSFMag,zMeanPSFMag,yMeanPSFMag,iMeanPSFMagErr,qualityFlag,objInfoFlag]"},
                 timeout=120)
try:
    ps1 = pd.read_csv(io.StringIO(r.text))
except Exception:
    ps1 = pd.DataFrame(); print("PS1 raw:", r.text[:300])
if len(ps1):
    ps1["sep_as"] = sep_arcsec(ps1["raMean"], ps1["decMean"])
    ps1 = ps1.sort_values("sep_as")
print("\n=== PS1 DR2 mean within 15\" ==="); print(ps1.to_string(index=False) if len(ps1) else "EMPTY")
ps1.to_csv(f"{D}/cat_ps1_dr2.csv", index=False)

# ---------- CatWISE2020 + unWISE via VizieR TAP, 15" ----------
def vizier(table, cols, name):
    q = f"""SELECT {cols}, DISTANCE(POINT('ICRS', RAJ2000, DEJ2000), POINT('ICRS', {RA}, {DEC}))*3600 AS sep_as
FROM "{table}" WHERE 1=CONTAINS(POINT('ICRS', RAJ2000, DEJ2000), CIRCLE('ICRS', {RA}, {DEC}, 15.0/3600))"""
    r = requests.get("https://tapvizier.cds.unistra.fr/TAPVizieR/tap/sync",
                     params={"REQUEST": "doQuery", "LANG": "ADQL", "FORMAT": "csv", "QUERY": q}, timeout=120)
    if r.status_code != 200:
        print(f"{name}: HTTP {r.status_code}", r.text[:200]); return pd.DataFrame()
    try:
        return pd.read_csv(io.StringIO(r.text))
    except Exception:
        print(f"{name} raw:", r.text[:300]); return pd.DataFrame()

cw = vizier("II/365/catwise", "Name, RAJ2000, DEJ2000, W1mproPM, W2mproPM, e_W1mproPM, e_W2mproPM", "CatWISE2020")
print("\n=== CatWISE2020 within 15\" ==="); print(cw.to_string(index=False) if len(cw) else "EMPTY")
cw.to_csv(f"{D}/cat_catwise.csv", index=False)

uw = vizier("II/363/unwise", "objID, RAJ2000, DEJ2000, FW1, FW2, e_FW1, e_FW2", "unWISE")
print("\n=== unWISE within 15\" ==="); print(uw.to_string(index=False) if len(uw) else "EMPTY")
uw.to_csv(f"{D}/cat_unwise.csv", index=False)
