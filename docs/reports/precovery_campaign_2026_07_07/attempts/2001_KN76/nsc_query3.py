import requests
TAP = "https://datalab.noirlab.edu/tap/sync"
def q(adql, fmt='csv', timeout=300):
    r = requests.post(TAP, data={'request':'doQuery','lang':'ADQL','format':fmt,'query':adql}, timeout=timeout)
    return r.status_code, r.text

ra0, dec0 = 229.7965, -21.0922
rad = 30.0/3600.0
# meas is partitioned; q3c_radial_query on meas should hit the spatial index.
# Try with q3c_join style / smaller radius and no extra predicates first.
adql = f"""SELECT m.ra, m.dec, m.mjd, m.mag_auto, m.filter, m.fwhm, m.class_star, m.exposure
FROM nsc_dr2.meas AS m
WHERE q3c_radial_query(m.ra, m.dec, {ra0}, {dec0}, {rad})"""
sc, txt = q(adql)
print("HTTP", sc)
lines = txt.splitlines()
print("rows:", len(lines)-1)
print("\n".join(lines[:40]))
