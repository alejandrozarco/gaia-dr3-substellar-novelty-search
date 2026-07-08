import requests, io, csv, json
TAP="https://datalab.noirlab.edu/tap/sync"
def q(a,timeout=400):
    r=requests.post(TAP,data={'request':'doQuery','lang':'ADQL','format':'csv','query':a},timeout=timeout); return r.status_code,r.text
exps=["c4d_170517_031953_ooi_Y_v1","c4d_170517_032252_ooi_Y_v1","c4d_170517_032551_ooi_Y_v1","c4d_170517_032849_ooi_Y_v1"]
# central overlap region covered by all 4 dithers
CRA,CDEC,H=251.10,-24.60,0.06
inl=",".join(f"'{e}'" for e in exps)
sc,txt=q(f"""SELECT m.ra,m.dec,m.mjd,m.mag_auto,m.filter,m.exposure,m.objectid,m.fwhm,m.class_star
FROM nsc_dr2.meas m WHERE m.exposure IN ({inl})
AND m.ra BETWEEN {CRA-H} AND {CRA+H} AND m.dec BETWEEN {CDEC-H} AND {CDEC+H}""")
print("meas pull status",sc,"bytes",len(txt))
rows=list(csv.DictReader(io.StringIO(txt)))
# map to bycatch detection dicts
dets=[]
from collections import Counter
for r in rows:
    dets.append(dict(mjd=float(r['mjd']),ra=float(r['ra']),dec=float(r['dec']),
                     mag=float(r['mag_auto']),filter=r['filter'],exposure=r['exposure'],
                     id=r['objectid'],group_id=r['objectid'],obscode='W84'))
json.dump(dets, open("bycatch_dets.json","w"))
print("detections in overlap box (4 exposures):", len(dets))
print("per-exposure:", Counter(d['exposure'][10:16] for d in dets))
# static: NSC object mean catalog in the region
sc2,txt2=q(f"""SELECT id,ra,dec,ndet FROM nsc_dr2.object
WHERE ra BETWEEN {CRA-H} AND {CRA+H} AND dec BETWEEN {CDEC-H} AND {CDEC+H}""")
srows=list(csv.DictReader(io.StringIO(txt2))) if sc2==200 else []
static=[dict(ra=float(s['ra']),dec=float(s['dec']),id=s['id'],ndet=int(s['ndet'])) for s in srows]
json.dump(static, open("bycatch_static.json","w"))
print("NSC mean-object static sources in region:", len(static))
