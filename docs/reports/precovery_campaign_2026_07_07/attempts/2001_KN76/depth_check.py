import requests, io, csv, math, json, time
from astroquery.jplhorizons import Horizons
TAP="https://datalab.noirlab.edu/tap/sync"
def q(adql,timeout=280):
    r=requests.post(TAP,data={'request':'doQuery','lang':'ADQL','format':'csv','query':adql},timeout=timeout)
    return r.status_code,r.text

# What is the faint limit of detected sources on the 2015-05 nights vs the 2015-07-15 night?
# Query exposure table for the exposures on those nights near the field, get depth95/nsources.
# NSC DR2 exposure table: nsc_dr2.exposure has ra,dec,mjd,filter,exptime,depth95,fwhm
def exposures(ra0,dec0,rad_as,mjd_lo,mjd_hi):
    adql=f"""SELECT e.exposure,e.ra,e.dec,e.mjd,e.filter,e.exptime,e.depth95,e.fwhm,e.nmeas
FROM nsc_dr2.exposure AS e
WHERE 't'=q3c_radial_query(e.ra,e.dec,{ra0},{dec0},{rad_as/3600.0}) AND e.mjd BETWEEN {mjd_lo} AND {mjd_hi}"""
    sc,txt=q(adql)
    if sc!=200 or txt.startswith('<?xml'): 
        print("   exposure query err",sc,txt[:200]); return None
    return list(csv.DictReader(io.StringIO(txt)))

# 2015-05 run field center ~ (230.68,-21.34); 2015-07-15 ~ (229.80,-21.09); DECam FOV ~1.1deg so 1 deg cone
print("=== 2015-05 run exposures (57162-57167) near field ===")
ex=exposures(230.68,-21.34,3600, 57162,57167)
if ex:
    for r in sorted(ex,key=lambda x:float(x['mjd'])):
        print(f"  {r['exposure']} mjd={float(r['mjd']):.4f} {r['filter']} exp={r['exptime']}s depth95={r['depth95']} fwhm={r['fwhm']} nmeas={r['nmeas']}")
print("\n=== 2015-07-15 mega-night exposures (57218) near field ===")
ex=exposures(229.80,-21.09,3600, 57217.9,57218.2)
if ex:
    for r in sorted(ex,key=lambda x:float(x['mjd']))[:20]:
        print(f"  {r['exposure']} mjd={float(r['mjd']):.4f} {r['filter']} exp={r['exptime']}s depth95={r['depth95']} fwhm={r['fwhm']} nmeas={r['nmeas']}")
print("\n=== 2013-03-11 exposures (56362) ===")
ex=exposures(228.80,-20.83,3600, 56362,56363)
if ex:
    for r in sorted(ex,key=lambda x:float(x['mjd'])):
        print(f"  {r['exposure']} mjd={float(r['mjd']):.4f} {r['filter']} exp={r['exptime']}s depth95={r['depth95']} fwhm={r['fwhm']} nmeas={r['nmeas']}")
