import requests, sys
TAP = "https://datalab.noirlab.edu/tap/sync"
ra0, dec0 = 229.7965, -21.0922
rad = 30.0/3600.0
adql = f"""SELECT m.ra, m.dec, m.mjd, m.mag_auto, m.filter, m.fwhm, m.class_star, m.objectid, m.exposure
FROM nsc_dr2.meas AS m
WHERE 't'=q3c_radial_query(m.ra, m.dec, {ra0}, {dec0}, {rad})
  AND m.mjd BETWEEN 57217.9 AND 57218.2"""
r = requests.post(TAP, data={'request':'doQuery','lang':'ADQL','format':'csv','query':adql}, timeout=180)
print("HTTP", r.status_code)
print(r.text[:3000])
