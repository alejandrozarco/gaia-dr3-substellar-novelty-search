import requests, io, csv, json, math, time
TAP="https://datalab.noirlab.edu/tap/sync"
def q(adql, timeout=600):
    r=requests.post(TAP, data={'request':'doQuery','lang':'ADQL','format':'csv','query':adql}, timeout=timeout)
    return r.status_code, r.text
RA0, DEC0 = 252.0790, -24.7890
# tighter cone 25", retry up to 3x
adql=f"""SELECT m.ra,m.dec,m.mjd,m.mag_auto,m.magerr_auto,m.filter,m.fwhm,m.class_star,m.exposure,m.objectid
FROM nsc_dr2.meas AS m
WHERE 't'=q3c_radial_query(m.ra,m.dec,{RA0},{DEC0},{25/3600.0})"""
rows=None
for att in range(3):
    sc,txt=q(adql)
    print(f"attempt {att} meas cone status {sc} bytes {len(txt)}")
    if sc==200 and not txt.startswith('<'):
        rows=list(csv.DictReader(io.StringIO(txt))); break
    time.sleep(3)
if rows is None:
    print("meas cone failed all attempts"); raise SystemExit
json.dump(rows, open("nsc_meas_cone25.json","w"))
print("total meas rows within 25\" (all epochs):", len(rows))
def sep_as(ra,dec,r0=RA0,d0=DEC0):
    dra=(ra-r0)*math.cos(math.radians(d0))*3600; dde=(dec-d0)*3600
    return math.hypot(dra,dde),dra,dde
# night detections
night=[r for r in rows if 57890.10<float(r['mjd'])<57890.20]
print("=== meas on target night MJD 57890 ===", len(night))
for r in sorted(night,key=lambda x:float(x['mjd'])):
    s,dra,dde=sep_as(float(r['ra']),float(r['dec']))
    print(f"  mjd={float(r['mjd']):.5f} sep={s:.2f}\"(dRA{dra:+.2f},dDec{dde:+.2f}) mag={r['mag_auto']} {r['filter']} fwhm={r['fwhm']} cstar={r['class_star']} exp={r['exposure']} obj={r['objectid']}")
# how many distinct objects & their mean positions (for stationarity)
from collections import Counter
oc=Counter(r['objectid'] for r in rows)
print("distinct objectids within 25\":", len(oc))
# nearest few by mean over all epochs
print("=== nearest sources (mean over their meas) ===")
byid={}
for r in rows:
    byid.setdefault(r['objectid'],[]).append(r)
means=[]
for oid,rs in byid.items():
    mra=sum(float(x['ra']) for x in rs)/len(rs); mde=sum(float(x['dec']) for x in rs)/len(rs)
    s,_,_=sep_as(mra,mde)
    means.append((s,oid,len(rs),mra,mde))
for s,oid,n,mra,mde in sorted(means)[:8]:
    mjds=[float(x['mjd']) for x in byid[oid]]
    print(f"  sep={s:.2f}\" obj={oid} ndet={n} mjdrange={min(mjds):.1f}-{max(mjds):.1f} filts={set(x['filter'] for x in byid[oid])}")
