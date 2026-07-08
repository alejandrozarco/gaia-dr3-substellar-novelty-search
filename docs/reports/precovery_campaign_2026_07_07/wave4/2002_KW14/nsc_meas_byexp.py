import requests, io, csv, json, math
TAP="https://datalab.noirlab.edu/tap/sync"
def q(adql, timeout=600):
    r=requests.post(TAP, data={'request':'doQuery','lang':'ADQL','format':'csv','query':adql}, timeout=timeout)
    return r.status_code, r.text
RA0, DEC0 = 252.0790, -24.7890
exps=["c4d_170517_031953_ooi_Y_v1","c4d_170517_032252_ooi_Y_v1",
      "c4d_170517_032551_ooi_Y_v1","c4d_170517_032849_ooi_Y_v1"]
inlist=",".join(f"'{e}'" for e in exps)
# exposure-filtered + position box (0.02 deg ~ 72"), fast via exposure index
adql=f"""SELECT m.ra,m.dec,m.mjd,m.mag_auto,m.magerr_auto,m.filter,m.fwhm,m.class_star,m.exposure,m.objectid,m.flags
FROM nsc_dr2.meas AS m
WHERE m.exposure IN ({inlist})
AND m.ra BETWEEN {RA0-0.03} AND {RA0+0.03}
AND m.dec BETWEEN {DEC0-0.03} AND {DEC0+0.03}"""
sc,txt=q(adql)
print("status",sc,"bytes",len(txt))
if sc!=200 or txt.startswith('<'):
    print(txt[:800]); raise SystemExit
rows=list(csv.DictReader(io.StringIO(txt)))
json.dump(rows, open("nsc_meas_byexp_box.json","w"))
print("meas rows in 0.03deg box on the 4 exposures:", len(rows))
def sep(ra,dec,r0=RA0,d0=DEC0):
    dra=(ra-r0)*math.cos(math.radians(d0))*3600; dde=(dec-d0)*3600
    return math.hypot(dra,dde),dra,dde
for r in sorted(rows,key=lambda x:(x['exposure'],float(x['ra']))):
    s,dra,dde=sep(float(r['ra']),float(r['dec']))
    if s<15:
        print(f"  {r['exposure'][10:16]} mjd={float(r['mjd']):.5f} sep={s:.2f}\"(dRA{dra:+.2f},dDec{dde:+.2f}) mag={r['mag_auto']} {r['filter']} fwhm={r['fwhm']} cstar={r['class_star']} obj={r['objectid']} flags={r['flags']}")
print("--- min sep per exposure ---")
from collections import defaultdict
d=defaultdict(list)
for r in rows: d[r['exposure']].append(r)
for e in exps:
    rs=d.get(e,[])
    if rs:
        best=min(rs,key=lambda x:sep(float(x['ra']),float(x['dec']))[0])
        s,dra,dde=sep(float(best['ra']),float(best['dec']))
        print(f"  {e}: {len(rs)} src in box, nearest {s:.2f}\" mag={best['mag_auto']} obj={best['objectid']}")
    else:
        print(f"  {e}: 0 src in box (target likely off-CCD/chip-gap)")
