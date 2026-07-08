import requests, io, csv, json
TAP="https://datalab.noirlab.edu/tap/sync"
def q(adql, timeout=300, fmt='csv'):
    r=requests.post(TAP, data={'request':'doQuery','lang':'ADQL','format':fmt,'query':adql}, timeout=timeout)
    return r.status_code, r.text
RA0, DEC0 = 252.0790, -24.7890
# object cone 300" to confirm coverage
for rad in [300, 120]:
    sc,txt=q(f"SELECT count(*) as n FROM nsc_dr2.object AS o WHERE 't'=q3c_radial_query(o.ra,o.dec,{RA0},{DEC0},{rad/3600.0})")
    print(f"object count within {rad}\":", txt.strip().replace('\n','|'), "status",sc)
# exposure table: is c4d_170517 in NSC DR2? search exposures near field on that mjd
sc,txt=q(f"""SELECT e.exposure,e.ra,e.dec,e.mjd,e.filter,e.exptime,e.instrument
FROM nsc_dr2.exposure AS e
WHERE 't'=q3c_radial_query(e.ra,e.dec,{RA0},{DEC0},{1.2}) AND e.mjd BETWEEN 57889 AND 57892""")
print("=== NSC exposures near field, MJD 57889-57892 ===", "status",sc)
print(txt[:1500])
