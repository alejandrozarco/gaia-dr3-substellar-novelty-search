import requests, io, csv, json
TAP = "https://datalab.noirlab.edu/tap/sync"
def q(adql, timeout=280):
    r = requests.post(TAP, data={'request':'doQuery','lang':'ADQL','format':'csv','query':adql}, timeout=timeout)
    return r.status_code, r.text

ids = ['133189_17045','133703_14601','133189_15021','136273_22941']
for oid in ids:
    adql=f"""SELECT m.objectid, m.ra, m.dec, m.mjd, m.mag_auto, m.magerr_auto, m.filter, m.fwhm, m.class_star, m.exposure
FROM nsc_dr2.meas AS m WHERE m.objectid = '{oid}'"""
    sc,txt=q(adql)
    print(f"=== objectid {oid} ===  HTTP {sc}")
    if sc==200 and not txt.startswith('<?xml'):
        rows=list(csv.DictReader(io.StringIO(txt)))
        for r in sorted(rows,key=lambda x:float(x['mjd'])):
            print(f"  mjd={float(r['mjd']):.6f} ra={float(r['ra']):.7f} dec={float(r['dec']):.7f} mag={r['mag_auto']}±{r['magerr_auto']} {r['filter']} fwhm={r['fwhm']} cstar={r['class_star']} exp={r['exposure']}")
        json.dump(rows, open(f'meas_{oid}.json','w'))
    else:
        print(txt[:300])
    print()
