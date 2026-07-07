import requests, json, sys

# NOIRLab Astro Data Lab TAP sync, anonymous. NSC DR2.
TAP = "https://datalab.noirlab.edu/tap/sync"

def tap_query(adql):
    r = requests.post(TAP, data={
        'request':'doQuery','lang':'ADQL','format':'json',
        'query':adql}, timeout=120)
    r.raise_for_status()
    return r.json()

# 2015-07-15 mega-night: predicted RA~229.7965, Dec~-21.0922, MJD 57218.03-57218.06
# Error ellipse: SMAA 12.99", SMIA 2.56", theta -15 deg. Search a generous box +/- 20" RA, +/-6" Dec.
# NSC DR2 object table (mean positions) = static sources. meas table = per-epoch detections.
# We want the MEAS (per-exposure) detections to find a MOVER not in the mean-object table.

# Cone in NSC DR2 meas around predicted position, generous 30" radius, on the exposures of that night.
ra0, dec0 = 229.7965, -21.0922
rad = 30.0/3600.0

adql_meas = f"""
SELECT m.ra, m.dec, m.mjd, m.mag_auto, m.filter, m.fwhm, m.class_star, m.objectid, m.exposure
FROM nsc_dr2.meas AS m
WHERE 't'=q3c_radial_query(m.ra, m.dec, {ra0}, {dec0}, {rad})
  AND m.mjd BETWEEN 57217.9 AND 57218.2
"""
print("=== NSC DR2 meas cone @ 2015-07-15 night, 30arcsec ===")
try:
    res = tap_query(adql_meas)
    print(json.dumps(res, indent=1)[:4000])
    with open('nsc_meas_20150715.json','w') as f: json.dump(res,f)
except Exception as e:
    print("ERR:", e)
