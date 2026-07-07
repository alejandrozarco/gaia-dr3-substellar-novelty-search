import requests, io, csv, math
from astroquery.jplhorizons import Horizons
TAP="https://datalab.noirlab.edu/tap/sync"
def q(adql,timeout=120):
    r=requests.post(TAP,data={'request':'doQuery','lang':'ADQL','format':'csv','query':adql},timeout=timeout)
    return r.status_code,r.text
# 56837 candidate 133188_12384 and 57781 candidate 135758_19814 : pull meas by id
for oid in ['133188_12384','135758_19814']:
    adql=f"SELECT m.objectid,m.ra,m.dec,m.mjd,m.mag_auto,m.filter,m.fwhm,m.class_star,m.exposure FROM nsc_dr2.meas m WHERE m.objectid='{oid}'"
    sc,txt=q(adql)
    print(f"=== {oid} ===")
    if sc==200 and not txt.startswith('<?xml'):
        for r in csv.DictReader(io.StringIO(txt)):
            print(f"  mjd={float(r['mjd']):.5f} ra={r['ra']} dec={r['dec']} mag={r['mag_auto']} {r['filter']} exp={r['exposure']}")
    else: print("  err",sc)
