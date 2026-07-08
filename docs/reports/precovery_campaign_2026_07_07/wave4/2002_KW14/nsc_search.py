import requests, io, csv, json, math
TAP="https://datalab.noirlab.edu/tap/sync"
def q(adql, timeout=300):
    r=requests.post(TAP, data={'request':'doQuery','lang':'ADQL','format':'csv','query':adql}, timeout=timeout)
    return r.status_code, r.text
RA0, DEC0 = 252.0790, -24.7890
# 1) cone meas 40"
adql=f"""SELECT m.ra,m.dec,m.mjd,m.mag_auto,m.magerr_auto,m.filter,m.fwhm,m.class_star,m.exposure,m.objectid
FROM nsc_dr2.meas AS m
WHERE 't'=q3c_radial_query(m.ra,m.dec,{RA0},{DEC0},{40/3600.0})"""
sc,txt=q(adql)
print("meas cone status",sc, "bytes",len(txt))
rows=list(csv.DictReader(io.StringIO(txt))) if sc==200 and not txt.startswith('<') else []
json.dump(rows, open("nsc_meas_cone40.json","w"))
print("total meas rows in 40\":", len(rows))
# night detections
night=[r for r in rows if 57890.10 < float(r['mjd']) < 57890.20]
print("meas on target night (MJD 57890.10-0.20):", len(night))
def sep_as(ra,dec):
    dra=(ra-RA0)*math.cos(math.radians(DEC0))*3600
    dde=(dec-DEC0)*3600
    return math.hypot(dra,dde), dra, dde
for r in sorted(night,key=lambda x:float(x['mjd'])):
    s,dra,dde=sep_as(float(r['ra']),float(r['dec']))
    print(f"  mjd={float(r['mjd']):.5f} sep={s:.2f}\" (dRA{dra:+.2f},dDec{dde:+.2f}) mag={r['mag_auto']} {r['filter']} fwhm={r['fwhm']} cstar={r['class_star']} exp={r['exposure']} obj={r['objectid']}")
# 2) object (mean) catalog in region for bycatch static + stationarity
adql2=f"""SELECT o.id,o.ra,o.dec,o.mag_auto,o.filter,o.ndet,o.deltamjd,o.class_star
FROM nsc_dr2.object AS o
WHERE 't'=q3c_radial_query(o.ra,o.dec,{RA0},{DEC0},{60/3600.0})"""
sc2,txt2=q(adql2)
print("object cone status",sc2)
orows=list(csv.DictReader(io.StringIO(txt2))) if sc2==200 and not txt2.startswith('<') else []
json.dump(orows, open("nsc_object_cone60.json","w"))
print("mean objects within 60\":", len(orows))
