import requests, io, csv, sys
TAP = "https://datalab.noirlab.edu/tap/sync"
def q(adql, timeout=300):
    r = requests.post(TAP, data={'request':'doQuery','lang':'ADQL','format':'csv','query':adql}, timeout=timeout)
    return r.status_code, r.text

def cone_meas(ra0, dec0, rad_as, label):
    rad = rad_as/3600.0
    adql = f"""SELECT m.ra, m.dec, m.mjd, m.mag_auto, m.magerr_auto, m.filter, m.fwhm, m.class_star, m.exposure, m.objectid
FROM nsc_dr2.meas AS m
WHERE 't'=q3c_radial_query(m.ra, m.dec, {ra0}, {dec0}, {rad})"""
    sc, txt = q(adql)
    if sc!=200 or txt.startswith('<?xml'):
        print(f"[{label}] HTTP {sc} ERROR"); print(txt[:500]); return None
    rows = list(csv.DictReader(io.StringIO(txt)))
    print(f"[{label}] cone {rad_as}\" @ ({ra0},{dec0}): {len(rows)} meas rows")
    return rows

# 2015-07-15 mega-night
rows = cone_meas(229.7965, -21.0922, 30.0, "2015-07-15")
if rows:
    import json
    json.dump(rows, open('nsc_meas_20150715.json','w'))
    # night detections
    night = [r for r in rows if 57217.9 < float(r['mjd']) < 57218.2]
    print(f"  -> {len(night)} detections on the night MJD 57217.9-57218.2")
    for r in sorted(night, key=lambda x: float(x['mjd'])):
        print(f"    mjd={float(r['mjd']):.5f} ra={float(r['ra']):.6f} dec={float(r['dec']):.6f} mag={r['mag_auto']} filt={r['filter']} fwhm={r['fwhm']} cstar={r['class_star']} obj={r['objectid']}")
