#!/usr/bin/env python
"""Archival catalog stack at RA 332.39126, Dec -14.8699 (Rubin diaObject 170635519425249637)."""
import warnings, json
warnings.filterwarnings("ignore")
import numpy as np

RA, DEC = 332.39126, -14.8699
R_AS = 30.0  # search radius arcsec
out = {}

from astropy.coordinates import SkyCoord
import astropy.units as u
co = SkyCoord(RA, DEC, unit="deg")


def sep(ra, dec):
    return co.separation(SkyCoord(np.asarray(ra, float), np.asarray(dec, float), unit="deg")).arcsec


# --- Data Lab TAP: Legacy Survey DR10 tractor + NSC DR2 ---
from astroquery.utils.tap.core import TapPlus
dl = TapPlus(url="https://datalab.noirlab.edu/tap", verbose=False)

q_ls = f"""SELECT ra, dec, type, flux_g, flux_r, flux_i, flux_z, flux_w1, flux_w2,
mag_g, mag_r, mag_i, mag_z
FROM ls_dr10.tractor
WHERE q3c_radial_query(ra, dec, {RA}, {DEC}, {R_AS/3600.})"""
try:
    t = dl.launch_job(q_ls).get_results().to_pandas()
    t["sep_as"] = sep(t["ra"], t["dec"]) if len(t) else []
    out["ls_dr10"] = t.sort_values("sep_as").to_dict("records") if len(t) else []
except Exception as e:
    out["ls_dr10"] = f"ERROR: {e}"

q_nsc = f"""SELECT id, ra, dec, ndet, nphot, gmag, rmag, imag, zmag, vmag,
rms(rmag) as dummy FROM nsc_dr2.object WHERE 1=0"""
q_nsc = f"""SELECT id, ra, dec, ndet, nphot, gmag, rmag, imag, zmag,
grms, rrms, irms, zrms, deltamjd, mjd
FROM nsc_dr2.object
WHERE q3c_radial_query(ra, dec, {RA}, {DEC}, {R_AS/3600.})"""
try:
    t = dl.launch_job(q_nsc).get_results().to_pandas()
    t["sep_as"] = sep(t["ra"], t["dec"]) if len(t) else []
    out["nsc_dr2_object"] = t.sort_values("sep_as").to_dict("records") if len(t) else []
except Exception as e:
    out["nsc_dr2_object"] = f"ERROR: {e}"

# per-measurement epochs for anything within 3" (precursor check), mjd-keyed
q_nscm = f"""SELECT m.objectid, m.mjd, m.filter, m.mag_auto, m.magerr_auto, m.ra, m.dec
FROM nsc_dr2.meas m
WHERE q3c_radial_query(m.ra, m.dec, {RA}, {DEC}, {3.0/3600.})"""
try:
    t = dl.launch_job(q_nscm).get_results().to_pandas()
    out["nsc_dr2_meas_3as"] = t.sort_values("mjd").to_dict("records") if len(t) else []
except Exception as e:
    out["nsc_dr2_meas_3as"] = f"ERROR: {e}"

# --- PS1 DR2 mean (MAST) ---
import requests
try:
    r = requests.get(
        "https://catalogs.mast.stsci.edu/api/v0.1/panstarrs/dr2/mean.json",
        params={"ra": RA, "dec": DEC, "radius": R_AS / 3600.0,
                "columns": "objName,raMean,decMean,nDetections,gMeanPSFMag,rMeanPSFMag,iMeanPSFMag,zMeanPSFMag,yMeanPSFMag,iMeanPSFMagStd",
                "pagesize": 50},
        timeout=90)
    rows = r.json()["data"] if r.status_code == 200 else []
    for row in rows:
        row["sep_as"] = float(sep([row["raMean"]], [row["decMean"]])[0])
    out["ps1_dr2_mean"] = sorted(rows, key=lambda x: x["sep_as"])
except Exception as e:
    out["ps1_dr2_mean"] = f"ERROR: {e}"

# --- Gaia DR3 ---
try:
    from astroquery.gaia import Gaia
    Gaia.ROW_LIMIT = 50
    j = Gaia.launch_job(f"""SELECT source_id, ra, dec, parallax, parallax_error, pmra, pmdec,
        phot_g_mean_mag, phot_bp_mean_mag, phot_rp_mean_mag, phot_variable_flag, ruwe
        FROM gaiadr3.gaia_source
        WHERE 1=CONTAINS(POINT('ICRS', ra, dec), CIRCLE('ICRS', {RA}, {DEC}, {R_AS/3600.}))""")
    t = j.get_results().to_pandas()
    t["sep_as"] = sep(t["ra"], t["dec"]) if len(t) else []
    out["gaia_dr3"] = t.sort_values("sep_as").to_dict("records") if len(t) else []
except Exception as e:
    out["gaia_dr3"] = f"ERROR: {e}"

# --- CatWISE2020 + unWISE via VizieR ---
try:
    from astroquery.vizier import Vizier
    v = Vizier(row_limit=50)
    res = v.query_region(co, radius=R_AS * u.arcsec, catalog=["II/365/catwise", "II/363/unwise"])
    for tab in res:
        name = tab.meta.get("ID", "vizier")
        t = tab.to_pandas()
        racol = [c for c in t.columns if c.lower() in ("ra_icrs", "raj2000", "ra")][0]
        decol = [c for c in t.columns if c.lower() in ("de_icrs", "dej2000", "dec", "de")][0]
        t["sep_as"] = sep(t[racol], t[decol])
        out[name] = t.sort_values("sep_as").head(10).to_dict("records")
except Exception as e:
    out["wise"] = f"ERROR: {e}"

json.dump(out, open("/tmp/rubin_pilot/forensics/170635519425249637/catalogs.json", "w"),
          default=str, indent=1)

# summary print
for k, v in out.items():
    if isinstance(v, str):
        print(k, "->", v[:200])
    else:
        print(f"{k}: {len(v)} rows; nearest:",
              json.dumps(v[0], default=str)[:400] if v else "none")
