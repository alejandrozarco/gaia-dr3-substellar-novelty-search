import requests, io, csv, json, math
TAP="https://datalab.noirlab.edu/tap/sync"
def q(adql,timeout=300):
    r=requests.post(TAP,data={'request':'doQuery','lang':'ADQL','format':'csv','query':adql},timeout=timeout)
    return r.status_code,r.text
RA0,DEC0=252.0790,-24.7890
ids=["139366_91157","139366_77340","139366_77339","139366_91164","139366_91157"]
ids=list(dict.fromkeys(ids))
inl=",".join(f"'{i}'" for i in ids)
sc,txt=q(f"""SELECT o.id,o.ra,o.dec,o.mag_auto,o.filter,o.ndet,o.deltamjd,o.class_star,o.rmsvar,o.deltamjd
FROM nsc_dr2.object o WHERE o.id IN ({inl})""")
print("=== object records (stationarity via ndet/deltamjd) ===",sc)
print(txt)
# depth on exp 032849 and 032551: faintest & count
for e in ["c4d_170517_032849_ooi_Y_v1","c4d_170517_032551_ooi_Y_v1"]:
    sc,txt=q(f"""SELECT count(*) n, max(mag_auto) faint, min(mag_auto) bright, avg(fwhm) afwhm
    FROM nsc_dr2.meas WHERE exposure='{e}'""")
    print(f"=== depth {e[10:16]} ===", txt.strip().replace(chr(10),' | '))
# per-exposure: how many sources within 60" of predicted (is target region populated?)
for e in ["c4d_170517_032849_ooi_Y_v1","c4d_170517_032551_ooi_Y_v1","c4d_170517_032252_ooi_Y_v1","c4d_170517_031953_ooi_Y_v1"]:
    sc,txt=q(f"""SELECT ra,dec,mag_auto FROM nsc_dr2.meas
    WHERE exposure='{e}' AND ra BETWEEN {RA0-0.02} AND {RA0+0.02} AND dec BETWEEN {DEC0-0.02} AND {DEC0+0.02}""")
    rows=list(csv.DictReader(io.StringIO(txt))) if sc==200 else []
    def sep(r):
        dra=(float(r['ra'])-RA0)*math.cos(math.radians(DEC0))*3600;dde=(float(r['dec'])-DEC0)*3600
        return math.hypot(dra,dde)
    seps=sorted(sep(r) for r in rows)
    print(f"{e[10:16]}: {len(rows)} src within 72\" box; nearest 5 seps:", [round(s,1) for s in seps[:5]])
