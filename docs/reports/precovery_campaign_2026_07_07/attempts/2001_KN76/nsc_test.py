import requests, io, csv, time
TAP = "https://datalab.noirlab.edu/tap/sync"
def q(adql, timeout=280):
    t0=time.time()
    r = requests.post(TAP, data={'request':'doQuery','lang':'ADQL','format':'csv','query':adql}, timeout=timeout)
    return r.status_code, r.text, time.time()-t0

# Test 1: object table cone (mean catalog) - should be fast
ra0,dec0=229.7965,-21.0922
adql_obj=f"""SELECT o.ra, o.dec, o.gmag, o.rmag, o.imag, o.ndet, o.class_star, o.deltamjd, o.id
FROM nsc_dr2.object AS o
WHERE 't'=q3c_radial_query(o.ra, o.dec, {ra0}, {dec0}, {30.0/3600.0})"""
sc,txt,dt=q(adql_obj)
print(f"OBJECT cone: HTTP {sc} in {dt:.1f}s")
if sc==200 and not txt.startswith('<?xml'):
    rows=list(csv.DictReader(io.StringIO(txt)))
    print(f"  {len(rows)} mean objects within 30\"")
    for r in rows[:30]:
        print(f"    ra={float(r['ra']):.6f} dec={float(r['dec']):.6f} g={r['gmag']} r={r['rmag']} i={r['imag']} ndet={r['ndet']} cstar={r['class_star']} dmjd={r['deltamjd']}")
else:
    print(txt[:400])
