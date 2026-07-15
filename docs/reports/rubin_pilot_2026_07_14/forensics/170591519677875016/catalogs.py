#!/usr/bin/env python
"""Archival catalog forensics around Rubin diaObject 170591519677875016.
All cones 30 arcsec unless noted; results dumped as CSV/JSON in outdir."""
import json, os, sys, io
import requests
import numpy as np
import pandas as pd
from astropy.coordinates import SkyCoord
import astropy.units as u

RA, DEC = 306.74802, -11.81856
OUT = "/tmp/rubin_pilot/forensics/170591519677875016"
c = SkyCoord(RA * u.deg, DEC * u.deg)
gal = c.galactic
print(f"Galactic l={gal.l.deg:.4f} b={gal.b.deg:.4f}")
ecl = c.barycentricmeanecliptic
print(f"Ecliptic lon={ecl.lon.deg:.4f} lat={ecl.lat.deg:.4f}")

def datalab_tap(adql, name):
    try:
        r = requests.get("https://datalab.noirlab.edu/tap/sync",
                         params={"REQUEST": "doQuery", "LANG": "ADQL",
                                 "FORMAT": "csv", "QUERY": adql}, timeout=180)
        r.raise_for_status()
        df = pd.read_csv(io.StringIO(r.text))
        df.to_csv(f"{OUT}/{name}.csv", index=False)
        print(f"[{name}] {len(df)} rows")
        return df
    except Exception as e:
        print(f"[{name}] FAILED: {e}")
        return None

# --- NSC DR2 objects within 30" ---
nsc = datalab_tap(f"""
SELECT id, ra, dec, gmag,rmag,imag,zmag, ndet, deltamjd, mjd, class_star,
  rrms, irms, variable10 ,
  q3c_dist(ra,dec,{RA},{DEC})*3600.0 AS sep_as
FROM nsc_dr2.object
WHERE q3c_radial_query(ra,dec,{RA},{DEC},30.0/3600.0)
ORDER BY sep_as
""", "nsc_dr2_object_30as")

# --- LS DR10 tractor within 30" ---
ls = datalab_tap(f"""
SELECT ls_id, ra, dec, type, mag_g,mag_r,mag_i,mag_z, mag_w1,mag_w2,
  flux_g, flux_r, flux_i, flux_z, snr_g,snr_r,snr_i,snr_z,
  q3c_dist(ra,dec,{RA},{DEC})*3600.0 AS sep_as
FROM ls_dr10.tractor
WHERE q3c_radial_query(ra,dec,{RA},{DEC},30.0/3600.0)
ORDER BY sep_as
""", "ls_dr10_tractor_30as")

# --- Gaia DR3 within 30" (via Data Lab mirror) ---
gaia = datalab_tap(f"""
SELECT source_id, ra, dec, parallax, parallax_error, pmra, pmdec,
  phot_g_mean_mag, phot_bp_mean_mag, phot_rp_mean_mag, ruwe,
  phot_variable_flag,
  q3c_dist(ra,dec,{RA},{DEC})*3600.0 AS sep_as
FROM gaia_dr3.gaia_source
WHERE q3c_radial_query(ra,dec,{RA},{DEC},30.0/3600.0)
ORDER BY sep_as
""", "gaia_dr3_30as")

# --- unWISE DR1 + CatWISE2020 via Data Lab ---
catwise = datalab_tap(f"""
SELECT source_name, ra, dec, w1mpro, w2mpro, w1sigmpro, w2sigmpro,
  q3c_dist(ra,dec,{RA},{DEC})*3600.0 AS sep_as
FROM catwise2020.main
WHERE q3c_radial_query(ra,dec,{RA},{DEC},30.0/3600.0)
ORDER BY sep_as
""", "catwise2020_30as")

unwise = datalab_tap(f"""
SELECT unwise_objid, ra, dec, flux_w1, flux_w2,
  q3c_dist(ra,dec,{RA},{DEC})*3600.0 AS sep_as
FROM unwise_dr1.object
WHERE q3c_radial_query(ra,dec,{RA},{DEC},30.0/3600.0)
ORDER BY sep_as
""", "unwise_dr1_30as")

# --- PS1 DR2 mean objects within 30" via MAST catalogs API ---
try:
    r = requests.get(
        "https://catalogs.mast.stsci.edu/api/v0.1/panstarrs/dr2/mean.csv",
        params={"ra": RA, "dec": DEC, "radius": 30.0 / 3600.0,
                "nDetections.gte": 1, "pagesize": 500,
                "columns": "objID,raMean,decMean,nDetections,gMeanPSFMag,rMeanPSFMag,iMeanPSFMag,zMeanPSFMag,yMeanPSFMag,iMeanPSFMagErr,epochMean"},
        timeout=180)
    r.raise_for_status()
    ps1 = pd.read_csv(io.StringIO(r.text))
    if len(ps1):
        pc = SkyCoord(ps1.raMean.values * u.deg, ps1.decMean.values * u.deg)
        ps1["sep_as"] = c.separation(pc).arcsec
        ps1 = ps1.sort_values("sep_as")
    ps1.to_csv(f"{OUT}/ps1_dr2_mean_30as.csv", index=False)
    print(f"[ps1_dr2_mean] {len(ps1)} rows")
except Exception as e:
    print(f"[ps1_dr2_mean] FAILED: {e}")

print("done")
